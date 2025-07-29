# src/path_comment/detectors.py
"""Detector utilities for recognizing file types and managing comment prefixes.

Providing centralized logic for identifying programming languages and
their corresponding comment styles ensures consistent behavior across
the tool.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Set

from identify.identify import tags_from_path

# Map an *identify* tag → the prefix that starts a line-comment
COMMENT_PREFIXES: Dict[str, str] = {
    # python / shell-style
    "python": "#",
    "cython": "#",
    "yaml": "#",
    "toml": "#",
    "shell": "#",
    "makefile": "#",
    # c / js-style
    "javascript": "//",
    "typescript": "//",
    "json": "//",
    "c": "//",
    "cpp": "//",
}

# Files we intentionally ignore (binaries, markdown, images, etc.)
_SKIP_TAGS: Set[str] = {
    "binary",
    "archive",  # zip, tar …
    "pdf",
}


def _get_shebang_tag(path: Path) -> str | None:
    """Check if file starts with a shebang and return appropriate tag."""
    try:
        with path.open("r", encoding="utf-8") as f:
            first_line = f.readline().strip()
            if first_line.startswith("#!"):
                if "python" in first_line.lower():
                    return "python"
                if "sh" in first_line.lower():
                    return "shell"
    except (OSError, UnicodeDecodeError):
        # File cannot be read or contains invalid UTF-8 - skip shebang detection
        return None
    return None


def comment_prefix(path: Path) -> str | None:
    """Return the correct **line-comment prefix** for *path*.

    Returns None if the file should be skipped entirely.
    """
    tags = tags_from_path(str(path))
    if tags & _SKIP_TAGS:
        return None

    # First check if it's a shebang script
    if shebang_tag := _get_shebang_tag(path):
        if prefix := COMMENT_PREFIXES.get(shebang_tag):
            return prefix

    # Then check normal file tags
    for tag in tags:
        if prefix := COMMENT_PREFIXES.get(tag):
            return prefix

    return None
