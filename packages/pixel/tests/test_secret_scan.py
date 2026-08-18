from pathlib import Path
from shutil import which
from subprocess import run  # noqa: S404

from pixel.security.scan import scan_path

ROOT = Path(__file__).resolve().parents[3]


def test_repository_has_no_live_secret_markers() -> None:
    hits = scan_path(ROOT)
    assert hits == []


def test_git_history_has_no_private_key_or_live_openai_markers() -> None:
    git = which("git")
    assert git is not None
    # Require key material, not docs/tests that mention the prefixes.
    patterns = (
        r"sk-(live|proj)-[A-Za-z0-9_-]{16,}",
        r"-----BEGIN [A-Z][A-Z ]{0,40}PRIVATE KEY-----",
    )
    for pattern in patterns:
        result = run(  # noqa: S603
            [git, "log", "-G", pattern, "--all", "--pretty=format:%H", "--max-count=5"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == ""
