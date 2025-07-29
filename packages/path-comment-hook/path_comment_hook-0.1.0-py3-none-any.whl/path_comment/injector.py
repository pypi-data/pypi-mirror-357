# src/path_comment/injector.py
"""Path comment injection logic.

Ensure every source file starts with a comment that contains its path
relative to the project root.  Operates in two modes:  • check → just
verify, no edits  • fix   → rewrite the file in-place if needed
"""

from __future__ import annotations

from enum import Enum, auto
from pathlib import Path, PurePosixPath

from identify.identify import tags_from_path

from .detectors import comment_prefix
from .file_handler import FileHandler, FileHandlingError


class Result(Enum):
    """Result states for path comment processing."""

    OK = auto()  # header already present
    CHANGED = auto()  # header inserted / fixed
    SKIPPED = auto()  # binary or unsupported
    REMOVED = auto()  # header was removed (for delete operations)


def _has_shebang(first_line: str) -> bool:
    return first_line.startswith("#!")  # e.g. "#!/usr/bin/env bash"


def _is_path_comment(line: str, file_path: Path, project_root: Path) -> bool:
    """Check if a line looks like a path comment for this file."""
    prefix = comment_prefix(file_path)
    if prefix is None:
        return False

    line = line.strip()
    if not line.startswith(prefix):
        return False

    # Extract the comment content after the prefix
    comment_part = line[len(prefix) :].strip()

    # Check if it looks like a file path (contains forward slashes or is a simple filename)
    return "/" in comment_part or (
        bool(comment_part) and " " not in comment_part and "." in comment_part
    )


def delete_header(
    file_path: Path,
    project_root: Path,
    mode: str = "fix",  # "check" | "fix"
) -> Result:
    """Remove path comment header from file_path if it exists.

    Returns a Result enum; in "check" mode we never modify files. Uses
    FileHandler for safe operations with encoding detection and atomic
    writes.
    """
    # Normalize paths
    project_root = project_root.resolve()
    if not file_path.is_absolute():
        file_path = (project_root / file_path).resolve()

    # Binary? bail early
    if "binary" in tags_from_path(str(file_path)):
        return Result.SKIPPED

    prefix = comment_prefix(file_path)
    if prefix is None:
        return Result.SKIPPED

    # Use FileHandler for safe file operations
    try:
        handler = FileHandler(file_path)
        file_info = handler.read()
    except FileHandlingError as e:
        if e.__cause__ and isinstance(e.__cause__, PermissionError):
            raise
        return Result.SKIPPED

    lines = file_info.content.splitlines(keepends=True)
    if not lines:
        return Result.OK  # Empty file, nothing to remove

    first_line = lines[0]
    header_removed = False
    new_lines = lines.copy()

    # Handle files that start with a shebang; header would be after it
    if _has_shebang(first_line):
        if len(lines) > 1 and _is_path_comment(lines[1], file_path, project_root):
            # Remove the header line after shebang
            if mode == "check":
                return Result.REMOVED
            new_lines.pop(1)
            header_removed = True
    else:
        # Check if first line is a path comment
        if _is_path_comment(first_line, file_path, project_root):
            if mode == "check":
                return Result.REMOVED
            new_lines.pop(0)
            # Also remove the blank line that typically follows if it exists
            if new_lines and new_lines[0].strip() == "":
                new_lines.pop(0)
            header_removed = True

    if not header_removed:
        return Result.OK

    if mode == "check":
        return Result.REMOVED

    # Write the modified content
    try:
        new_content = "".join(new_lines)
        handler.write(new_content, file_info.line_ending)
        return Result.REMOVED
    except FileHandlingError as e:
        if e.__cause__ and isinstance(e.__cause__, PermissionError):
            raise
        return Result.SKIPPED


def ensure_header(
    file_path: Path,
    project_root: Path,
    mode: str = "fix",  # "check" | "fix"
) -> Result:
    """Ensure *file_path* contains the correct header.

    Returns a Result enum; in "check" mode we never modify files. Uses
    the new FileHandler for safe operations with CRLF preservation,
    encoding detection, and atomic writes.
    """
    # ------------------------------------------------------------------ #
    # Normalize paths:                                                    #
    #  • pre-commit passes *relative* paths; tests pass absolute paths.   #
    #  • We resolve both file_path and project_root so                   #
    #    `file_path.relative_to(project_root)` is always valid.          #
    # ------------------------------------------------------------------ #
    project_root = project_root.resolve()
    if not file_path.is_absolute():
        file_path = (project_root / file_path).resolve()

    # Binary?  bail early
    if "binary" in tags_from_path(str(file_path)):
        return Result.SKIPPED

    prefix = comment_prefix(file_path)
    if prefix is None:
        return Result.SKIPPED

    rel = PurePosixPath(file_path.relative_to(project_root))
    expected_line = f"{prefix} {rel}\n"

    # Use the new FileHandler for safe file operations
    try:
        handler = FileHandler(file_path)
        file_info = handler.read()
    except FileHandlingError as e:
        # Check the underlying cause of the FileHandlingError
        if e.__cause__ and isinstance(e.__cause__, PermissionError):
            # Re-raise permission errors so they get counted as errors
            raise
        # For other file handling issues, skip the file
        return Result.SKIPPED

    lines = file_info.content.splitlines(keepends=True)
    if not lines:
        # Empty file - add the header
        if mode == "check":
            return Result.CHANGED
        try:
            handler.write(expected_line, file_info.line_ending)
            return Result.CHANGED
        except FileHandlingError:
            return Result.SKIPPED

    first_line = lines[0]

    # Handle files that start with a shebang; header must go *after* it
    if _has_shebang(first_line):
        header_pos = 1
        if len(lines) > 1:
            present_header = lines[1]
            needs_change = present_header != expected_line
        else:
            # File only has shebang, need to add header
            needs_change = True
    else:
        header_pos = 0
        needs_change = first_line != expected_line

    if not needs_change:
        return Result.OK
    if mode == "check":
        return Result.CHANGED

    # --- rewrite with safe file handling and line ending preservation ---
    try:
        new_lines = lines.copy()

        if header_pos == 1:  # Insert after shebang
            if len(new_lines) > 1 and _is_path_comment(new_lines[1], file_path, project_root):
                new_lines[1] = expected_line  # Replace existing header
            else:
                new_lines.insert(1, expected_line)  # Insert header after shebang
        else:  # Insert at beginning
            # Prepend header, keep original first line, and add blank line
            original_first = new_lines[0]
            new_lines[0] = expected_line
            # Ensure a blank line after header for readability
            blank = file_info.line_ending.value
            new_lines.insert(1, blank)
            new_lines.insert(2, original_first)

        new_content = "".join(new_lines)
        handler.write(new_content, file_info.line_ending)
        return Result.CHANGED

    except FileHandlingError as e:
        # Check the underlying cause of the FileHandlingError
        if e.__cause__ and isinstance(e.__cause__, PermissionError):
            # Re-raise permission errors so they get counted as errors
            raise
        # If write fails for other reasons, return SKIPPED to avoid breaking the workflow
        return Result.SKIPPED
