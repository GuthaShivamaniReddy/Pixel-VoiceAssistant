"""Reject user-controlled names that could traverse storage paths."""

from __future__ import annotations

from pathlib import PurePosixPath, PureWindowsPath


def safe_basename(name: str, *, max_length: int = 200) -> str:
    raw = (name or "").strip()
    if not raw or len(raw) > max_length:
        raise ValueError("invalid_filename")
    if any(item in raw for item in ("/", "\\", "\x00", "\n", "\r")):
        raise ValueError("invalid_filename")
    if ".." in raw:
        raise ValueError("invalid_filename")
    posix = PurePosixPath(raw).name
    windows = PureWindowsPath(raw).name
    if posix != raw or windows != raw or raw in {".", ".."}:
        raise ValueError("invalid_filename")
    return raw
