from dataclasses import dataclass
from typing import Optional


@dataclass
class HttpResponse:
    url: str
    status: Optional[int] = None
    headers: Optional[dict[str, str]] = None
    body: Optional[bytes] = None
    elapsed: Optional[float] = None
    error: Optional[str] = None


@dataclass
class DiscoveredUrl:
    url: str
    source: str
    category: str
    is_scan_candidate: bool
    in_scope: bool
    reason: Optional[str] = None


@dataclass
class CacheHint:
    vendor: str                  # cloudflare, cloudfront, akamai, generic_x_cache, unknown...
    status: str                  # hit, miss, unknown
    evidence: str                # hangi header/value yüzünden bu kararı verdik