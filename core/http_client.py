import aiohttp
import asyncio
import time

from models import HttpResponse


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "close",
}


class AsyncHttpClient:
    def __init__(self, timeout: int = 10, concurrency: int = 10):
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(concurrency)

    async def fetch(self, session, method: str, url: str, headers: dict | None = None) -> HttpResponse:
        async with self.semaphore:
            start = time.perf_counter()

            merged_headers = dict(DEFAULT_HEADERS)
            if headers:
                merged_headers.update(headers)

            try:
                async with session.request(
                    method,
                    url,
                    headers=merged_headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    allow_redirects=True,
                ) as resp:
                    body = await resp.read()
                    elapsed = time.perf_counter() - start

                    return HttpResponse(
                        url=str(resp.url),
                        status=resp.status,
                        headers=dict(resp.headers),
                        body=body,
                        elapsed=elapsed,
                    )

            except Exception as e:
                return HttpResponse(
                    url=url,
                    error=str(e),
                    elapsed=time.perf_counter() - start,
                )