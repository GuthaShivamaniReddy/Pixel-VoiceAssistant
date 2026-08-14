import httpx
import pytest

from pixel.knowledge.fetch import fetch_approved_html


def test_fetch_rejects_arbitrary_urls() -> None:
    with pytest.raises(ValueError):
        fetch_approved_html("https://evil.example/page")


def test_fetch_uses_canonical_allowlisted_url() -> None:
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(str(request.url))
        return httpx.Response(
            200,
            text="<html><body><h1>About</h1><p>Cyber Florida</p></body></html>",
        )

    client = httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=False)
    html = fetch_approved_html("https://cyberflorida.org/about/", client=client)
    assert "Cyber Florida" in html
    assert seen == ["https://cyberflorida.org/about/"]
