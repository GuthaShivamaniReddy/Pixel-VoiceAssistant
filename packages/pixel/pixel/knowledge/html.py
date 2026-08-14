"""HTML importer for approved Cyber Florida pages. Stdlib only."""

from __future__ import annotations

from html.parser import HTMLParser

_SKIP_TAGS = frozenset({"script", "style", "noscript", "svg", "iframe", "form"})
_SKIP_BLOCKS = frozenset({"nav", "footer"})


class _HtmlExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self._in_title = False
        self._skip = 0
        self._heading_level = 0
        self.blocks: list[tuple[str, str]] = []
        self._buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        name = tag.lower()
        classes = " ".join(value or "" for key, value in attrs if key == "class").lower()
        ids = " ".join(value or "" for key, value in attrs if key == "id").lower()
        noisy = any(
            hint in classes or hint in ids
            for hint in ("cookie", "menu", "nav-main", "site-footer", "banner")
        )
        if self._skip:
            self._skip += 1
            return
        if name in _SKIP_TAGS or name in _SKIP_BLOCKS or noisy:
            self._skip = 1
            return
        if name == "title":
            self._in_title = True
            return
        if name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._flush("p")
            self._heading_level = int(name[1])
            return
        if name in {"p", "li", "div", "section", "article", "br"}:
            if name in {"p", "li", "br"}:
                self._flush("p")

    def handle_endtag(self, tag: str) -> None:
        name = tag.lower()
        if self._skip:
            self._skip -= 1
            return
        if name == "title":
            self._in_title = False
            return
        if name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._flush(name)
            self._heading_level = 0
            return
        if name in {"p", "li"}:
            self._flush("p")

    def handle_data(self, data: str) -> None:
        if self._skip:
            return
        text = data.strip()
        if not text:
            return
        if self._in_title:
            self.title = f"{self.title} {text}".strip()
            return
        self._buf.append(text)

    def _flush(self, kind: str) -> None:
        text = " ".join(self._buf).strip()
        self._buf.clear()
        if not text:
            return
        if kind.startswith("h"):
            self.blocks.append((kind, text))
        else:
            self.blocks.append(("p", text))


def extract_html(html: str) -> tuple[str, list[tuple[str, str]]]:
    parser = _HtmlExtractor()
    parser.feed(html)
    parser.close()
    parser._flush("p")
    title = parser.title.strip()
    blocks = [(kind, text) for kind, text in parser.blocks if text]
    if not blocks:
        raise ValueError("HTML contained no indexable content")
    return title, blocks
