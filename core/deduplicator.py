class UrlDeduplicator:
    def __init__(self):
        self._seen: set[str] = set()

    def seen(self, url: str) -> bool:
        return url in self._seen

    def add(self, url: str) -> None:
        self._seen.add(url)

    def add_if_new(self, url: str) -> bool:
        if url in self._seen:
            return False
        self._seen.add(url)
        return True