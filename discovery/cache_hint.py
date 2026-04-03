from models import CacheHint


def _normalize_header_map(headers: dict[str, str] | None) -> dict[str, str]:
    if not headers:
        return {}
    return {k.lower(): v for k, v in headers.items()}


def detect_cache_hint(headers: dict[str, str] | None) -> CacheHint:

    h = _normalize_header_map(headers)

    # Cloudflare
    if "cf-cache-status" in h:
        value = h["cf-cache-status"]
        upper = value.upper()
        if "HIT" in upper:
            return CacheHint("cloudflare", "hit", f"CF-Cache-Status: {value}")
        if "MISS" in upper:
            return CacheHint("cloudflare", "miss", f"CF-Cache-Status: {value}")
        return CacheHint("cloudflare", "unknown", f"CF-Cache-Status: {value}")

    # Google Cloud CDN
    if "cdn_cache_status" in h:
        value = h["cdn_cache_status"]
        lower = value.lower()
        if "hit" in lower:
            return CacheHint("google_cloud_cdn", "hit", f"cdn_cache_status: {value}")
        if "mis" in lower or "miss" in lower:
            return CacheHint("google_cloud_cdn", "miss", f"cdn_cache_status: {value}")
        return CacheHint("google_cloud_cdn", "unknown", f"cdn_cache_status: {value}")

    # X-Cache-Status family
    if "x-cache-status" in h:
        value = h["x-cache-status"]
        upper = value.upper()
        if "HIT" in upper:
            return CacheHint("x_cache_status_family", "hit", f"X-Cache-Status: {value}")
        if "MISS" in upper or "FRESH/MISS" in upper:
            return CacheHint("x_cache_status_family", "miss", f"X-Cache-Status: {value}")
        return CacheHint("x_cache_status_family", "unknown", f"X-Cache-Status: {value}")

    # X-Cache-Lookup family
    if "x-cache-lookup" in h:
        value = h["x-cache-lookup"]
        lower = value.lower()
        if "hit from" in lower or "cache hit" in lower:
            return CacheHint("x_cache_lookup_family", "hit", f"X-Cache-Lookup: {value}")
        if "miss from" in lower or "cache miss" in lower:
            return CacheHint("x_cache_lookup_family", "miss", f"X-Cache-Lookup: {value}")
        return CacheHint("x_cache_lookup_family", "unknown", f"X-Cache-Lookup: {value}")

    # Rack Cache
    if "x-rack-cache" in h:
        value = h["x-rack-cache"]
        lower = value.lower()
        if "hit" in lower:
            return CacheHint("rack_cache", "hit", f"X-Rack-Cache: {value}")
        if "miss" in lower or "fresh" in lower:
            return CacheHint("rack_cache", "miss", f"X-Rack-Cache: {value}")
        return CacheHint("rack_cache", "unknown", f"X-Rack-Cache: {value}")

    # CDN77
    if "x-77-cache" in h:
        value = h["x-77-cache"]
        upper = value.upper()
        if "HIT" in upper:
            return CacheHint("cdn77", "hit", f"X-77-Cache: {value}")
        if "MISS" in upper:
            return CacheHint("cdn77", "miss", f"X-77-Cache: {value}")
        return CacheHint("cdn77", "unknown", f"X-77-Cache: {value}")

    # ChinaCache
    if "x-cc-via" in h:
        value = h["x-cc-via"]
        upper = value.upper()
        if "[H," in upper or upper.startswith("H"):
            return CacheHint("chinacache", "hit", f"X-cc-via: {value}")
        if "[M," in upper or upper.startswith("M"):
            return CacheHint("chinacache", "miss", f"X-cc-via: {value}")
        return CacheHint("chinacache", "unknown", f"X-cc-via: {value}")

    # Incapsula
    if "x-info" in h:
        value = h["x-info"]
        upper = value.upper()
        if "OCNN" in upper:
            return CacheHint("incapsula", "hit", f"X-Info: {value}")
        if "PNNN" in upper:
            return CacheHint("incapsula", "miss", f"X-Info: {value}")
        return CacheHint("incapsula", "unknown", f"X-Info: {value}")

    # Akamai-ish via Server-Timing
    if "server-timing" in h:
        value = h["server-timing"]
        upper = value.upper()
        if "DESC=HIT" in upper:
            return CacheHint("akamai_like", "hit", f"Server-Timing: {value}")
        if "DESC=MISS" in upper:
            return CacheHint("akamai_like", "miss", f"Server-Timing: {value}")

    # Generic Cache header
    if "cache" in h:
        value = h["cache"]
        upper = value.upper()
        if "HIT" in upper:
            return CacheHint("cache_header_family", "hit", f"Cache: {value}")
        if "MISS" in upper:
            return CacheHint("cache_header_family", "miss", f"Cache: {value}")
        return CacheHint("cache_header_family", "unknown", f"Cache: {value}")

    # Nginx-ish
    if "cache-status" in h:
        value = h["cache-status"]
        upper = value.upper()
        if "HIT" in upper:
            return CacheHint("cache_status_family", "hit", f"Cache-Status: {value}")
        if "MISS" in upper:
            return CacheHint("cache_status_family", "miss", f"Cache-Status: {value}")
        return CacheHint("cache_status_family", "unknown", f"Cache-Status: {value}")

    if "x-proxy-cache" in h:
        value = h["x-proxy-cache"]
        upper = value.upper()
        if "HIT" in upper:
            return CacheHint("x_proxy_cache_family", "hit", f"X-Proxy-Cache: {value}")
        if "MISS" in upper:
            return CacheHint("x_proxy_cache_family", "miss", f"X-Proxy-Cache: {value}")
        return CacheHint("x_proxy_cache_family", "unknown", f"X-Proxy-Cache: {value}")

    # Generic X-Cache
    if "x-cache" in h:
        value = h["x-cache"]
        lower = value.lower()
        upper = value.upper()

        if "cloudfront" in lower:
            if "hit" in lower:
                return CacheHint("cloudfront", "hit", f"X-Cache: {value}")
            if "miss" in lower:
                return CacheHint("cloudfront", "miss", f"X-Cache: {value}")
            return CacheHint("cloudfront", "unknown", f"X-Cache: {value}")

        if "tcp_hit" in upper or "HIT TCP_IMS_HIT" in upper:
            return CacheHint("x_cache_family", "hit", f"X-Cache: {value}")

        if "tcp_miss" in upper:
            return CacheHint("x_cache_family", "miss", f"X-Cache: {value}")

        if "HIT" in upper:
            return CacheHint("x_cache_family", "hit", f"X-Cache: {value}")

        if "MISS" in upper:
            return CacheHint("x_cache_family", "miss", f"X-Cache: {value}")

        return CacheHint("x_cache_family", "unknown", f"X-Cache: {value}")

    return CacheHint("unknown", "unknown", "no known cache identification header")