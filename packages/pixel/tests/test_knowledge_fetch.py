import httpx
import pytest

from pixel.knowledge.fetch import fetch_approved_html


def test_fetch_rejects_ssrf_and_unsafe_schemes() -> None:
    for url in (
        "https://127.0.0.1/",
        "https://localhost/admin",
        "file:///etc/passwd",
        "javascript:alert(1)",
        "https://169.254.169.254/latest/meta-data/",
    ):
        with pytest.raises(ValueError):
            fetch_approved_html(url)


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
