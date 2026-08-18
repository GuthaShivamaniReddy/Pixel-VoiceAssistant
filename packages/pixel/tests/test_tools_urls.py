from pixel.tools.urls import extract_url, validate_navigation_url


def test_approved_canonical_url_allows() -> None:
    ok, reason = validate_navigation_url("https://cyberflorida.org/firstline/")
    assert ok is True
    assert reason == "ok"


def test_unapproved_domain_denied() -> None:
    ok, _reason = validate_navigation_url("https://attacker.example/")
    assert ok is False


def test_javascript_scheme_denied() -> None:
    ok, _reason = validate_navigation_url("javascript:alert(1)")
    assert ok is False


def test_data_scheme_denied() -> None:
    ok, _reason = validate_navigation_url("data:text/html,<script>alert(1)</script>")
    assert ok is False


def test_lookalike_host_denied() -> None:
    ok, _reason = validate_navigation_url("https://cyberflorida.org.attacker.com/")
    assert ok is False
    assert validate_navigation_url("https://cyberflorida.org.attacker.example/")[0] is False


def test_http_and_file_denied() -> None:
    assert validate_navigation_url("http://cyberflorida.org/")[0] is False
    assert validate_navigation_url("file:///etc/passwd")[0] is False


def test_localhost_and_metadata_denied() -> None:
    assert validate_navigation_url("https://127.0.0.1/")[0] is False
    assert validate_navigation_url("https://localhost/")[0] is False
    assert validate_navigation_url("https://169.254.169.254/")[0] is False


def test_unregistered_path_on_approved_host_denied() -> None:
    assert validate_navigation_url("https://cyberflorida.org/not-a-registered-page")[0] is False


def test_extract_url() -> None:
    assert extract_url("Open https://attacker.example/phish") == "https://attacker.example/phish"
