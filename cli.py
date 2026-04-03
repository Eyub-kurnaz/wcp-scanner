from urllib.parse import urlparse
import argparse

from config import ScanConfig


def normalize_target_url(url: str) -> str:

    url = url.strip()

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)

    if not parsed.netloc:
        raise ValueError("Invalid URL provided")

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only http/https URLs are supported")

    return url


def parse_args() -> ScanConfig:
    parser = argparse.ArgumentParser(description="WCP Scanner")

    parser.add_argument(
        "--url",
        required=True,
        help="Target URL to scan",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="HTTP timeout in seconds",
    )

    parser.add_argument(
        "--concurrency",
        type=int,
        default=10,
        help="Maximum concurrent requests",
    )

    parser.add_argument(
        "--max-depth",
        type=int,
        default=1,
        help="Maximum crawl depth",
    )

    parser.add_argument(
        "--max-pages",
        type=int,
        default=10,
        help="Maximum number of pages to crawl",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output report path (.json or .txt)",
    )

    args = parser.parse_args()

    target_url = normalize_target_url(args.url)

    return ScanConfig(
        target_url=target_url,
        timeout=args.timeout,
        concurrency=args.concurrency,
        max_depth=args.max_depth,
        max_pages=args.max_pages,
        output_path=args.output,
    )