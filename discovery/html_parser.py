from selectolax.parser import HTMLParser


def parse_html(html: bytes) -> HTMLParser | None:

    if not html:
        return None

    try:
        return HTMLParser(html)
    except Exception:
        return None