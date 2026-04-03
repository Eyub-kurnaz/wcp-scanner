from urllib.parse import urlparse


LOCAL_HOSTS = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
}


SUSPICIOUS_MARKERS = (
    "${", "}", "[[", "]]", "[", "]", "(", ")", "*"
)


ASSET_EXTENSIONS = (
    ".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg",
    ".webp", ".ico", ".woff", ".woff2", ".ttf", ".eot",
    ".mp4", ".webm", ".mp3", ".ogg", ".pdf", ".map"
)


AUTH_KEYWORDS = (
    "login", "signin", "sign-in", "logout", "register",
    "auth", "oauth", "token", "session", "account"
)


API_KEYWORDS = (
    "/api/", "/graphql", "/v1/", "/v2/", "/v3/",
)


MARKETING_KEYWORDS = (
    "newsletter", "signup", "sign-up", "subscribe",
    "campaign", "cloud.email", "marketing", "email"
)


ENV_KEYWORDS = (
    "dev", "stage", "staging", "test", "qa", "int", "preprod"
)


def is_http_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def is_same_scope(base_url: str, target_url: str, include_subdomains: bool = True) -> bool:
    try:
        base = urlparse(base_url)
        target = urlparse(target_url)

        base_host = base.hostname.lower() if base.hostname else ""
        target_host = target.hostname.lower() if target.hostname else ""

        if not base_host or not target_host:
            return False

        if target_host == base_host:
            return True

        if include_subdomains and target_host.endswith("." + base_host):
            return True

        return False

    except Exception:
        return False


def is_discoverable_url(url: str) -> bool:
    if not is_http_url(url):
        return False

    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()

        if not host:
            return False

        return True
    except Exception:
        return False


def _has_suspicious_parts(url: str) -> bool:
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        path = parsed.path or ""

        if any(marker in host for marker in SUSPICIOUS_MARKERS):
            return True

        if any(marker in path for marker in SUSPICIOUS_MARKERS):
            return True

        if host in LOCAL_HOSTS:
            return True

        if host.startswith("localhost.") or ".localhost." in host:
            return True

        if "." not in host and host not in LOCAL_HOSTS:
            return True

        if path in ("/a", "/f", "/n", "/x"):
            return True

        return False

    except Exception:
        return True


def is_scan_candidate(url: str, base_url: str) -> bool:
    """
    Şimdilik saldırı adayını dar tutuyoruz:
    - HTTP/HTTPS olmalı
    - suspicious olmamalı
    - scope içinde olmalı
    """
    if not is_http_url(url):
        return False

    if _has_suspicious_parts(url):
        return False

    if not is_same_scope(base_url, url, include_subdomains=True):
        return False

    return True


def categorize_url(url: str) -> str:
    """
    URL'yi kaba ama faydalı bir heuristic ile etiketler.
    Bu sınıflandırma simdilik yüksek dogrulukta değil.
    """
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        path = (parsed.path or "").lower()
        full = f"{host}{path}"

        # asset
        if path.endswith(ASSET_EXTENSIONS):
            return "asset"

        if any(token in host for token in ("cdn.", "static.", "assets.")):
            return "asset"

        # auth
        if any(keyword in full for keyword in AUTH_KEYWORDS):
            return "auth"

        # api
        if host.startswith("api.") or any(keyword in path for keyword in API_KEYWORDS):
            return "api"

        # marketing
        if any(keyword in full for keyword in MARKETING_KEYWORDS):
            return "marketing"

        # environment / test
        host_parts = host.split(".")
        if any(part in ENV_KEYWORDS for part in host_parts):
            return "environment"

        if any(keyword in full for keyword in ENV_KEYWORDS):
            return "environment"

        # page
        if path == "" or path == "/" or "." not in path.split("/")[-1]:
            return "page"

        return "unknown"

    except Exception:
        return "unknown"