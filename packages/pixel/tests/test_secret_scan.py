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
    for needle in ("BEGIN PRIVATE KEY", "sk-live-", "sk-proj-"):
        result = run(  # noqa: S603
            [git, "log", "-S", needle, "--all", "--pretty=format:%H", "--max-count=5"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0
        assert result.stdout.strip() == ""
