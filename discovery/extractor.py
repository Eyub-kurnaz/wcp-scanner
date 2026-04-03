from urllib.parse import urljoin, urlparse, urlunparse


def is_valid_url(raw_url: str | None) -> bool:
    """
    URL'nin gerçekten HTTP isteği olup olmayacağını kontrol eder.
    """
    if not raw_url:
        return False

    cleaned = raw_url.strip()

    # sadece kontrol için lowercase
    lowered = cleaned.lower()

    # boş veya sadece fragment (#)
    if not cleaned or cleaned.startswith("#"):
        return False

    if lowered.startswith((
        "javascript:",
        "mailto:",
        "tel:",
        "data:",
        "about:",
        "file:",
    )):
        return False

    return True


def normalize_url(url: str) -> str:
    """
    URL normalize eder:
    - scheme & host lowercase
    - default port kaldırılır
    - trailing slash normalize edilir
    - fragment (#...) kaldırılır
    """
    try:
        parsed = urlparse(url)

        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()

        # default port temizleme
        if scheme == "http" and netloc.endswith(":80"):
            netloc = netloc[:-3]
        elif scheme == "https" and netloc.endswith(":443"):
            netloc = netloc[:-4]

        path = parsed.path or "/"

        # trailing slash normalize
        if path != "/":
            path = path.rstrip("/")

        # fragment kaldır
        fragment = ""

        return urlunparse((
            scheme,
            netloc,
            path,
            parsed.params,
            parsed.query,
            fragment
        ))

    except Exception:
        return url


def extract_urls(tree, base_url: str) -> set[str]:
    """
    HTML tree içinden URL'leri çıkarır ve normalize eder.
    """
    urls = set()

    if not tree:
        return urls

    def add_url(raw_url: str | None):
        if not is_valid_url(raw_url):
            return

        try:
            full_url = urljoin(base_url, raw_url)
            normalized = normalize_url(full_url)

            if normalized:
                urls.add(normalized)

        except Exception:
            pass

    # <a href="">
    for node in tree.css("a"):
        add_url(node.attributes.get("href"))

    # <script src="">
    for node in tree.css("script"):
        add_url(node.attributes.get("src"))

    # <link href="">
    for node in tree.css("link"):
        add_url(node.attributes.get("href"))

    # <img src="">
    for node in tree.css("img"):
        add_url(node.attributes.get("src"))

    # <form action="">
    for node in tree.css("form"):
        add_url(node.attributes.get("action"))

    # <iframe src="">
    for node in tree.css("iframe"):
        add_url(node.attributes.get("src"))

    return urls