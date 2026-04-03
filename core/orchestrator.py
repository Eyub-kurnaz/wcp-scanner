import aiohttp
from collections import deque

from core.http_client import AsyncHttpClient
from core.deduplicator import UrlDeduplicator
from discovery.html_parser import parse_html
from discovery.extractor import extract_urls, normalize_url
from discovery.js_extractor import extract_urls_from_js
from discovery.url_filter import (
    is_discoverable_url,
    is_scan_candidate,
    is_same_scope,
    categorize_url,
)
from discovery.cache_hint import detect_cache_hint
from models import DiscoveredUrl


class ScanOrchestrator:
    def __init__(self, config):
        self.config = config
        self.client = AsyncHttpClient(
            timeout=config.timeout,
            concurrency=config.concurrency,
        )
        self.deduplicator = UrlDeduplicator()

    async def run(self) -> dict:
        queue = deque()
        queue.append((self.config.target_url, 0))

        discovered_map: dict[str, DiscoveredUrl] = {}
        crawled_pages = []

        discovered_map[self.config.target_url] = DiscoveredUrl(
            url=self.config.target_url,
            source="seed",
            category=categorize_url(self.config.target_url),
            is_scan_candidate=True,
            in_scope=True,
            reason=None,
        )

        async with aiohttp.ClientSession() as session:
            while queue and len(crawled_pages) < self.config.max_pages:
                current_url, depth = queue.popleft()

                if depth > self.config.max_depth:
                    continue

                if not self.deduplicator.add_if_new(current_url):
                    continue

                result = await self.client.fetch(session, "GET", current_url)
                cache_hint = detect_cache_hint(result.headers)

                crawled_pages.append({
                    "url": current_url,
                    "status": result.status,
                    "error": result.error,
                    "elapsed": result.elapsed,
                    "cache_vendor": cache_hint.vendor,
                    "cache_status": cache_hint.status,
                    "cache_evidence": cache_hint.evidence,
                })

                if result.error:
                    continue

                content_type = (result.headers.get("Content-Type") or "").lower()

                if "text/html" not in content_type:
                    continue

                if not result.body:
                    continue

                tree = parse_html(result.body)
                urls = extract_urls(tree, result.url)

                # 1) HTML extraction
                for url in urls:
                    if not is_discoverable_url(url):
                        continue

                    in_scope = is_same_scope(
                        self.config.target_url,
                        url,
                        include_subdomains=True,
                    )

                    candidate = is_scan_candidate(url, self.config.target_url)

                    if url not in discovered_map:
                        discovered_map[url] = DiscoveredUrl(
                            url=url,
                            source="html",
                            category=categorize_url(url),
                            is_scan_candidate=candidate,
                            in_scope=in_scope,
                            reason=None if candidate else "filtered_candidate",
                        )

                # 2) JS extraction
                js_urls = [
                    url for url in urls
                    if url.lower().endswith(".js") or ".js?" in url.lower()
                ]

                for js_url in js_urls:
                    js_result = await self.client.fetch(session, "GET", js_url)

                    if js_result.error or not js_result.body:
                        continue

                    js_extracted = extract_urls_from_js(js_result.body, js_result.url)

                    for js_found_url in js_extracted:
                        normalized = normalize_url(js_found_url)

                        if not is_discoverable_url(normalized):
                            continue

                        in_scope = is_same_scope(
                            self.config.target_url,
                            normalized,
                            include_subdomains=True,
                        )

                        candidate = is_scan_candidate(normalized, self.config.target_url)

                        if normalized not in discovered_map:
                            discovered_map[normalized] = DiscoveredUrl(
                                url=normalized,
                                source="js",
                                category=categorize_url(normalized),
                                is_scan_candidate=candidate,
                                in_scope=in_scope,
                                reason=None if candidate else "filtered_candidate",
                            )

                # 3) Queue
                for url in urls:
                    if not is_scan_candidate(url, self.config.target_url):
                        continue

                    if depth + 1 <= self.config.max_depth:
                        queue.append((url, depth + 1))

        discovered_urls = sorted(discovered_map.values(), key=lambda x: x.url)
        scan_candidates = sorted(
            [x for x in discovered_urls if x.is_scan_candidate],
            key=lambda x: x.url,
        )

        return {
            "target": self.config.target_url,
            "crawled_pages": crawled_pages,
            "discovered_urls": discovered_urls,
            "scan_candidates": scan_candidates,
        }