# src/path_comment/config.py
"""Handle loading and validating configuration from *pyproject.toml* files.

Providing a centralized way to manage tool settings ensures that the
rest of the codebase can rely on a single, validated source of truth.
"""

from __future__ import annotations

import fnmatch
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

# Python 3.11+ has tomllib in stdlib, older versions need tomli
try:
    if sys.version_info >= (3, 11):
        import tomllib
    else:
        import tomli as tomllib
except ImportError as e:
    if sys.version_info < (3, 11):
        raise ImportError(
            "tomli is required for Python < 3.11. Install with: pip install tomli"
        ) from e
    else:
        raise


class ConfigError(Exception):
    """Raised when there's an error in configuration loading or validation."""

    pass


# Default ignore patterns - comprehensive list of files/directories to exclude
DEFAULT_IGNORE_PATTERNS = [
    # Version Control
    ".git/*",
    ".svn/*",
    ".hg/*",
    ".bzr/*",
    "_darcs/*",
    # Python
    "__pycache__/*",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".mypy_cache/*",
    ".pytest_cache/*",
    ".coverage",
    "htmlcov/*",
    ".tox/*",
    "venv/*",
    ".venv/*",
    "env/*",
    ".env/*",
    "build/*",
    "dist/*",
    "*.egg-info/*",
    ".eggs/*",
    # Node.js/JavaScript
    "node_modules/*",
    ".npm/*",
    ".yarn/*",
    "bower_components/*",
    "*.min.js",
    "*.min.css",
    ".next/*",
    ".nuxt/*",
    # Build outputs
    "target/*",  # Rust, Java
    "bin/*",
    "obj/*",  # .NET
    "out/*",
    # IDEs and Editors
    ".vscode/*",
    ".idea/*",
    "*.swp",
    "*.swo",
    "*~",
    ".DS_Store",
    "Thumbs.db",
    # Documentation
    "_build/*",
    ".doctrees/*",
    "site/*",  # MkDocs
    # Logs and temporary files
    "*.log",
    "*.tmp",
    "*.temp",
    ".cache/*",
    ".sass-cache/*",
    # Package managers
    "vendor/*",  # Go, PHP
    "Pods/*",  # iOS CocoaPods
    ".bundle/*",  # Ruby
]


@dataclass
class Config:
    """Configuration settings for path-comment-hook.

    Attributes:
        exclude_globs: List of glob patterns for files to exclude from processing.
        custom_comment_map: Mapping of file extensions to custom comment templates.
        default_mode: Default path resolution mode ('file', 'folder', or 'smart').
        use_default_ignores: Whether to include default ignore patterns.
    """

    exclude_globs: List[str] = field(default_factory=list)
    custom_comment_map: Dict[str, str] = field(default_factory=dict)
    default_mode: str = "file"
    use_default_ignores: bool = True

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.default_mode not in {"file", "folder", "smart"}:
            raise ConfigError(
                f"Invalid default_mode '{self.default_mode}'. Must be one of: file, folder, smart"
            )

    def should_exclude(self, file_path: Path, project_root: Path | None = None) -> bool:
        """Check if a file should be excluded based on ignore patterns.

        Args:
            file_path: Path to check against exclusion patterns.
            project_root: Project root for relative path calculation (optional).

        Returns:
            True if the file should be excluded, False otherwise.
        """
        # Convert to string for pattern matching
        path_str = str(file_path)

        # Also try with relative path if project_root is provided
        relative_path_str = None
        if project_root:
            try:
                relative_path = file_path.relative_to(project_root)
                relative_path_str = str(relative_path)
            except ValueError:
                # file_path is not under project_root
                pass

        # Check user-defined exclude patterns
        for pattern in self.exclude_globs:
            if fnmatch.fnmatch(path_str, pattern):
                return True
            if relative_path_str and fnmatch.fnmatch(relative_path_str, pattern):
                return True

        # Check default ignore patterns if enabled
        if self.use_default_ignores:
            for pattern in DEFAULT_IGNORE_PATTERNS:
                if fnmatch.fnmatch(path_str, pattern):
                    return True
                if relative_path_str and fnmatch.fnmatch(relative_path_str, pattern):
                    return True

        return False

    def get_comment_prefix(self, extension: str) -> str | None:
        """Get custom comment prefix for a file extension.

        Args:
            extension: File extension (including the dot, e.g., '.py').

        Returns:
            Custom comment template if configured, None otherwise.
        """
        return self.custom_comment_map.get(extension)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary representation.

        Returns:
            Dictionary containing all configuration values.
        """
        return {
            "exclude_globs": self.exclude_globs,
            "custom_comment_map": self.custom_comment_map,
            "default_mode": self.default_mode,
            "use_default_ignores": self.use_default_ignores,
            "default_ignore_patterns": DEFAULT_IGNORE_PATTERNS if self.use_default_ignores else [],
        }


def load_config(project_root: Path) -> Config:
    """Load configuration from pyproject.toml in the project root.

    Args:
        project_root: Path to the project root directory.

    Returns:
        Config object with loaded or default settings.

    Raises:
        ConfigError: If there's an error parsing the configuration file.
    """
    pyproject_path = project_root / "pyproject.toml"

    if not pyproject_path.exists():
        return Config()

    try:
        with pyproject_path.open("rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"Failed to parse pyproject.toml: {e}") from e
    except OSError as e:
        raise ConfigError(f"Failed to read pyproject.toml: {e}") from e

    tool_config = data.get("tool", {}).get("path-comment-hook", {})

    # Extract and validate configuration values
    exclude_globs = tool_config.get("exclude_globs", [])
    custom_comment_map = tool_config.get("custom_comment_map", {})
    default_mode = tool_config.get("default_mode", "file")
    use_default_ignores = tool_config.get("use_default_ignores", True)

    # Type validation
    if not isinstance(exclude_globs, list):
        raise ConfigError("exclude_globs must be a list of strings")

    if not isinstance(custom_comment_map, dict):
        raise ConfigError(
            "custom_comment_map must be a dict mapping extensions to comment templates"
        )

    if not isinstance(default_mode, str):
        raise ConfigError("default_mode must be a string")

    if not isinstance(use_default_ignores, bool):
        raise ConfigError("use_default_ignores must be a boolean")

    try:
        return Config(
            exclude_globs=exclude_globs,
            custom_comment_map=custom_comment_map,
            default_mode=default_mode,
            use_default_ignores=use_default_ignores,
        )
    except ConfigError:
        # Re-raise validation errors from Config.__post_init__
        raise


def show_config(project_root: Path) -> Dict[str, Any]:
    """Load and return configuration for display purposes.

    Args:
        project_root: Path to the project root directory.

    Returns:
        Dictionary representation of the current configuration.
    """
    config = load_config(project_root)
    return config.to_dict()
