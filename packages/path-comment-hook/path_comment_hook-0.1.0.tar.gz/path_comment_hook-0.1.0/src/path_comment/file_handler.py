# src/path_comment/file_handler.py
"""Safe file handling with CRLF preservation, encoding detection, and atomic writes.

This module provides robust file handling capabilities that preserve
line endings, detect encodings with fallback, and ensure atomic writes
to prevent data corruption.
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import chardet
from rich.console import Console

console = Console()


class LineEnding(Enum):
    """Enumeration of line ending types."""

    LF = "\n"
    CRLF = "\r\n"


class FileHandlingError(Exception):
    """Raised when there's an error in file handling operations."""

    pass


@dataclass
class FileInfo:
    """Information about a file's content, encoding, and line endings.

    Attributes:
        content: The file's text content.
        encoding: The detected or used encoding.
        line_ending: The detected line ending type.
        original_path: The original file path.
    """

    content: str
    encoding: str
    line_ending: LineEnding
    original_path: Path


def detect_line_ending(file_path: Path) -> LineEnding:
    """Detect the line ending type used in a file.

    Args:
        file_path: Path to the file to analyze.

    Returns:
        The detected line ending type (defaults to LF if none found).

    Raises:
        FileHandlingError: If the file cannot be read.
    """
    try:
        with file_path.open("rb") as f:
            # Read first chunk to detect line endings
            chunk = f.read(8192)

        if not chunk:
            return LineEnding.LF  # Default for empty files

        # Look for CRLF first (more specific)
        if b"\r\n" in chunk:
            return LineEnding.CRLF
        elif b"\n" in chunk:
            return LineEnding.LF
        else:
            return LineEnding.LF  # Default when no line endings found

    except OSError as e:
        raise FileHandlingError(f"Failed to detect line endings in {file_path}: {e}") from e


def detect_encoding(file_path: Path) -> str:
    """Detect the encoding of a file with UTF-8 preference and chardet fallback.

    Args:
        file_path: Path to the file to analyze.

    Returns:
        The detected encoding name.

    Raises:
        FileHandlingError: If encoding cannot be detected.
    """
    try:
        with file_path.open("rb") as f:
            raw_data = f.read()

        if not raw_data:
            return "utf-8"  # Default for empty files

        # First, try UTF-8
        try:
            raw_data.decode("utf-8")
            return "utf-8"
        except UnicodeDecodeError:
            pass

        # Fallback to chardet
        try:
            result = chardet.detect(raw_data)
            if result and result["encoding"] and result["confidence"] > 0.7:
                detected_encoding: str = result["encoding"]
                console.print(
                    f"[yellow]Warning:[/yellow] Using {detected_encoding} encoding "
                    f"for {file_path} (confidence: {result['confidence']:.2f})"
                )
                return detected_encoding
            else:
                # Last resort - try latin-1 which can decode any byte sequence
                console.print(
                    f"[yellow]Warning:[/yellow] Low confidence encoding detection "
                    f"for {file_path}, using latin-1 as fallback"
                )
                return "latin-1"
        except Exception as e:
            console.print(
                f"[yellow]Warning:[/yellow] Chardet failed for {file_path}, "
                f"using latin-1 as fallback: {e}"
            )
            return "latin-1"

    except OSError as e:
        raise FileHandlingError(f"Failed to detect encoding for {file_path}: {e}") from e


class FileHandler:
    """Handles safe file operations with encoding and line ending preservation.

    This class provides methods for reading and writing files while
    preserving their original encoding and line ending characteristics.
    """

    def __init__(self, file_path: Path) -> None:
        """Initialize the file handler.

        Args:
            file_path: Path to the file to handle.
        """
        self.file_path = file_path.resolve()

    def read(self) -> FileInfo:
        """Read the file and detect its characteristics.

        Returns:
            FileInfo object with content, encoding, and line ending information.

        Raises:
            FileHandlingError: If the file cannot be read.
        """
        if not self.file_path.exists():
            raise FileHandlingError(f"Failed to read file: {self.file_path} does not exist")

        try:
            # Detect characteristics first - this also validates file access
            line_ending = detect_line_ending(self.file_path)
            encoding = detect_encoding(self.file_path)

            # Read content preserving original line endings
            with self.file_path.open("rb") as f:
                raw_data = f.read()

            # Decode with detected encoding
            content = raw_data.decode(encoding)

            return FileInfo(
                content=content,
                encoding=encoding,
                line_ending=line_ending,
                original_path=self.file_path,
            )

        except (OSError, UnicodeError) as e:
            raise FileHandlingError(f"Failed to read file {self.file_path}: {e}") from e
        except FileHandlingError:
            # Re-raise our custom errors with better context
            raise FileHandlingError(f"Failed to read file {self.file_path}") from None

    def write(self, content: str, line_ending: LineEnding) -> None:
        """Write content to the file atomically, preserving line endings.

        This method uses atomic writes (temporary file + rename) to ensure
        data integrity even if the process is interrupted.

        Args:
            content: The content to write.
            line_ending: The line ending type to use.

        Raises:
            FileHandlingError: If the file cannot be written.
        """
        try:
            # Normalize line endings in content
            normalized_content = self._normalize_line_endings(content, line_ending)

            # Create temporary file in the same directory for atomic operation
            temp_fd = None
            temp_path = None

            try:
                # Create temporary file
                temp_fd, temp_path_str = tempfile.mkstemp(
                    suffix=".tmp",
                    prefix=f".{self.file_path.name}.",
                    dir=self.file_path.parent,
                )
                temp_path = Path(temp_path_str)

                # Write to temporary file in binary mode for precise line ending control
                with os.fdopen(temp_fd, "wb") as f:
                    f.write(normalized_content.encode("utf-8"))
                    f.flush()
                    os.fsync(f.fileno())
                temp_fd = None  # Closed by context manager

                # Copy original file permissions if it exists
                if self.file_path.exists():
                    original_stat = self.file_path.stat()
                    temp_path.chmod(original_stat.st_mode)

                # Atomic rename
                if os.name == "nt":  # Windows
                    # On Windows, we need to remove the target first
                    if self.file_path.exists():
                        self.file_path.unlink()
                    temp_path.rename(self.file_path)
                else:  # Unix-like systems
                    temp_path.rename(self.file_path)

            except Exception:
                # Clean up temporary file on error
                if temp_fd is not None:
                    try:
                        os.close(temp_fd)
                    except OSError:
                        # Ignore cleanup errors to avoid masking original exception
                        console.print(
                            "[yellow]Warning:[/yellow] Failed to close temporary file descriptor"
                        )
                if temp_path and temp_path.exists():
                    try:
                        temp_path.unlink()
                    except OSError:
                        # Ignore cleanup errors to avoid masking original exception
                        console.print(
                            f"[yellow]Warning:[/yellow] Failed to remove temporary file {temp_path}"
                        )
                raise

        except OSError as e:
            raise FileHandlingError(f"Failed to write file {self.file_path}: {e}") from e

    def _normalize_line_endings(self, content: str, line_ending: LineEnding) -> str:
        """Normalize line endings in content to the specified type.

        Args:
            content: The content to normalize.
            line_ending: The target line ending type.

        Returns:
            Content with normalized line endings.
        """
        # First normalize all line endings to LF
        normalized = content.replace("\r\n", "\n").replace("\r", "\n")

        # Then convert to target line ending
        if line_ending == LineEnding.CRLF:
            return normalized.replace("\n", "\r\n")
        else:
            return normalized
