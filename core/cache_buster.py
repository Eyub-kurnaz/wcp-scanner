import secrets
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse


class CacheBuster:
    def __init__(self, param_name: str = "_cb"):
        self.param_name = param_name

    def new_value(self) -> str:
        return secrets.token_hex(6)

    def apply(self, url: str, value: str | None = None) -> str:
        """
        URL'ye cache buster query param ekler.
        Aynı test içinde aynı value farklıda farklı olmalı.
        """
        cb_value = value or self.new_value()

        parsed = urlparse(url)
        query_items = parse_qsl(parsed.query, keep_blank_values=True)

        # aynı param varsa yenisiyle değiştir
        filtered = [(k, v) for k, v in query_items if k != self.param_name]
        filtered.append((self.param_name, cb_value))

        new_query = urlencode(filtered, doseq=True)

        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment,
        ))