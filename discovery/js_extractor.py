import re
from urllib.parse import urljoin


ABSOLUTE_URL_RE = re.compile(r"""https?://[^\s"'`<>\\]+""")
RELATIVE_URL_RE = re.compile(r"""(?:"|')(/[^"'`<>\\\s]+)(?:"|')""")


def extract_urls_from_js(js_content: bytes, base_url: str) -> set[str]:
    """
    JS içeriğinden absolute ve relative URL benzeri değerleri çıkarır.
    Şimdilik execution yok, sadece regex tabanlı extraction var.
    """
    urls: set[str] = set()

    if not js_content:
        return urls

    try:
        text = js_content.decode("utf-8", errors="ignore")
    except Exception:
        return urls

    # absolute URLs
    for match in ABSOLUTE_URL_RE.findall(text):
        urls.add(match)

    # relative URLs
    for match in RELATIVE_URL_RE.findall(text):
        try:
            urls.add(urljoin(base_url, match))
        except Exception:
            pass

    return urls