from pixel.knowledge.chunking import chunk_blocks
from pixel.knowledge.html import extract_html
from pixel.knowledge.normalize import content_hash, normalize_text


def test_html_drops_nav_and_keeps_headings() -> None:
    html = """
    <html><head><title>About</title></head>
    <body>
      <nav>Home About cookie settings</nav>
      <h1>About Cyber Florida</h1>
      <p>Florida Center for Cybersecurity.</p>
      <footer>copyright</footer>
    </body></html>
    """
    title, blocks = extract_html(html)
    kinds = [kind for kind, _ in blocks]
    text = " ".join(body for _, body in blocks)
    assert title == "About"
    assert "h1" in kinds
    assert "Florida Center for Cybersecurity" in text
    assert "cookie settings" not in text
    assert "copyright" not in text


def test_empty_html_is_a_parse_failure() -> None:
    try:
        extract_html("<html><body><nav>menu</nav></body></html>")
    except ValueError as exc:
        assert "no indexable content" in str(exc)
    else:
        raise AssertionError("expected parse failure")


def test_normalize_does_not_rewrite_facts() -> None:
    raw = "Cyber  Florida\n\n\nis the Florida Center for Cybersecurity."
    assert "Florida Center for Cybersecurity" in normalize_text(raw)
    assert content_hash(raw) == content_hash(normalize_text(raw))


def test_chunking_preserves_heading_order_and_stable_ids() -> None:
    blocks = [
        ("h1", "FirstLine"),
        ("p", "Public-sector cybersecurity training."),
        ("h2", "Beginners"),
        ("p", "Beginner-friendly paths are listed here."),
    ]
    first = chunk_blocks(blocks, source_id="cf-firstline", title="FirstLine")
    second = chunk_blocks(blocks, source_id="cf-firstline", title="FirstLine")
    assert first[0]["heading_path"]
    assert [item["chunk_id"] for item in first] == [item["chunk_id"] for item in second]
    assert [item["ordinal"] for item in first] == list(range(len(first)))
    joined = " ".join(str(item["content"]) for item in first)
    assert "Public-sector cybersecurity training" in joined
    assert "Beginner-friendly" in joined


def test_chunk_size_limit_splits_long_sections() -> None:
    blocks = [("h1", "Long"), ("p", "word " * 400), ("p", "tail " * 400)]
    chunks = chunk_blocks(blocks, source_id="cf-home", title="Long")
    assert len(chunks) >= 2
    assert all(len(str(item["content"])) <= 1300 for item in chunks)
