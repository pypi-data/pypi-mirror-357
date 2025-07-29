# src/path_comment/cli.py
# mypy: disable-error-code=unreachable
"""CLI interface for path-comment-hook.

Root CLI for the *path-comment* pre-commit hook.
Calling pattern expected by pre-commit:
    path-comment-hook  [--check/-c]  <file1> <file2> ...
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, List

import typer
from rich.console import Console
from rich.table import Table

from .__about__ import __version__
from .config import ConfigError, load_config
from .processor import print_processing_summary, process_files_parallel
from .welcome import display_welcome

if TYPE_CHECKING:
    from .config import Config

# Rich console for better output
console = Console()


# Main typer app
app = typer.Typer(
    name="path-comment-hook",
    help="Insert or verify a relative-path comment at the top of each file.",
    no_args_is_help=True,
)


# Constants for Typer parameter defaults to avoid function calls in default

# Argument/Option factory calls are evaluated at import time here, avoiding
# ruff B008 (function calls in default argument values) inside the actual
# function signatures.

# -- Files argument
FILES_ARGUMENT = typer.Argument(
    None,
    help="Files to process. If omitted, use --all to process entire project.",
)

# -- Common options
CHECK_OPTION = typer.Option(
    False,
    "--check",
    "-c",
    help="Dry-run: only verify; exit 1 if any file would change.",
)

PROJECT_ROOT_OPTION = typer.Option(
    None,
    "--project-root",
    help="Root directory used to compute the relative header path.",
)

WORKERS_OPTION = typer.Option(
    None,
    "--workers",
    help="Number of worker threads for parallel processing. Defaults to CPU count.",
)

VERBOSE_OPTION = typer.Option(
    False,
    "--verbose",
    "-v",
    help="Show detailed processing information.",
)

PROGRESS_OPTION = typer.Option(
    False,
    "--progress",
    help="Show progress bar during processing.",
)

ALL_FILES_OPTION = typer.Option(
    False,
    "--all",
    help="Process all supported files under --project-root (recursively)",
)


@app.command()
def run(
    files: List[str] = FILES_ARGUMENT,
    check: bool = CHECK_OPTION,
    project_root: Path = PROJECT_ROOT_OPTION,
    workers: int = WORKERS_OPTION,
    verbose: bool = VERBOSE_OPTION,
    show_progress: bool = PROGRESS_OPTION,
    all_files: bool = ALL_FILES_OPTION,
) -> None:
    """Process files and ensure they have the correct header."""
    # Set project_root to current working directory if not explicitly provided
    if project_root is None:
        project_root = Path.cwd()

    # Resolve project_root to handle symlinks (e.g., /var -> /private/var on macOS)
    project_root = project_root.resolve()

    # If --all specified or no files provided, discover files automatically
    if all_files or not files:
        try:
            cfg = load_config(project_root)
        except ConfigError as e:
            console.print(f"[bold red]Configuration Error:[/bold red] {e}")
            raise typer.Exit(code=1) from e

        file_paths = _discover_files(project_root, cfg)

        if not file_paths:
            console.print("[yellow]No eligible files found to process.[/yellow]")
            raise typer.Exit(code=0)
    else:
        # Convert string file arguments to Path objects
        file_paths = []
        for file_str in files:
            file_path = Path(file_str)
            # Convert relative paths to absolute paths based on current working directory
            if not file_path.is_absolute():
                file_path = Path.cwd() / file_path
            # Resolve to handle symlinks (e.g., /var -> /private/var on macOS)
            file_path = file_path.resolve()
            file_paths.append(file_path)

    # Validate provided/discovered files
    for file_path in file_paths:
        if not file_path.exists():
            console.print(f"[bold red]Error:[/bold red] File '{file_path}' does not exist.")
            raise typer.Exit(code=1)
        if not file_path.is_file():
            console.print(f"[bold red]Error:[/bold red] '{file_path}' is not a file.")
            raise typer.Exit(code=1)

    mode = "check" if check else "fix"

    # Process files in parallel
    results = process_files_parallel(
        files=file_paths,
        project_root=project_root,
        mode=mode,
        workers=workers,
        show_progress=show_progress,
    )

    # Print summary if verbose or if there were changes/errors
    has_changes = any(r.result.name == "CHANGED" for r in results)
    has_errors = any(r.error is not None for r in results)

    if verbose or has_errors:
        print_processing_summary(results, mode, show_details=verbose)
    elif has_changes and not check:
        if all_files:
            # Show concise summary for bulk operations
            changed_count = sum(1 for r in results if r.result.name == "CHANGED")
            console.print(f"Successfully updated {changed_count} files.")
        else:
            # Show individual files for specific file operations
            for result in results:
                if result.result.name == "CHANGED":
                    console.print(f"Updated {result.file_path}")
    elif has_changes and check:
        if all_files:
            # Show concise summary for bulk check operations
            changed_count = sum(1 for r in results if r.result.name == "CHANGED")
            console.print(f"Would update {changed_count} files.")
        else:
            # Show individual files for specific file check operations
            for result in results:
                if result.result.name == "CHANGED":
                    console.print(f"Would update {result.file_path}")

    # Exit with error code if in check mode and there were changes or errors
    if check and (has_changes or has_errors):
        raise typer.Exit(code=1)
    elif has_errors:
        raise typer.Exit(code=1)


@app.command("show-config")
def show_config(
    project_root: Path = PROJECT_ROOT_OPTION,
) -> None:
    """Display the current path-comment-hook configuration."""
    # Set project_root to current working directory if not explicitly provided
    if project_root is None:
        project_root = Path.cwd()

    try:
        config = load_config(project_root)
        config_dict = config.to_dict()

        console.print("\n[bold green]Path-Comment-Hook Configuration[/bold green]")
        console.print(f"[dim]Loaded from: {project_root / 'pyproject.toml'}[/dim]\n")

        # Create a nice table for display
        table = Table(
            title="Configuration Settings",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Setting", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")

        # Add configuration rows
        table.add_row("exclude_globs", str(config_dict["exclude_globs"]))
        table.add_row("use_default_ignores", str(config_dict["use_default_ignores"]))
        table.add_row(
            "default_ignore_patterns",
            f"{len(config_dict['default_ignore_patterns'])} patterns"
            if config_dict["default_ignore_patterns"]
            else "[dim]None[/dim]",
        )
        table.add_row(
            "custom_comment_map",
            str(config_dict["custom_comment_map"])
            if config_dict["custom_comment_map"]
            else "[dim]None[/dim]",
        )
        table.add_row("default_mode", config_dict["default_mode"])

        console.print(table)
        console.print()

    except ConfigError as e:
        console.print(f"[bold red]Configuration Error:[/bold red] {e}")
        raise typer.Exit(code=1) from e
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(code=1) from e


@app.command()
def delete(
    files: List[str] = FILES_ARGUMENT,
    check: bool = CHECK_OPTION,
    project_root: Path = PROJECT_ROOT_OPTION,
    workers: int = WORKERS_OPTION,
    verbose: bool = VERBOSE_OPTION,
    show_progress: bool = PROGRESS_OPTION,
    all_files: bool = ALL_FILES_OPTION,
) -> None:
    """Remove path comment headers from files."""
    # Set project_root to current working directory if not explicitly provided
    if project_root is None:
        project_root = Path.cwd()

    # Resolve project_root to handle symlinks (e.g., /var -> /private/var on macOS)
    project_root = project_root.resolve()

    # If --all specified or no files provided, discover files automatically
    if all_files or not files:
        try:
            cfg = load_config(project_root)
        except ConfigError as e:
            console.print(f"[bold red]Configuration Error:[/bold red] {e}")
            raise typer.Exit(code=1) from e

        file_paths = _discover_files(project_root, cfg)

        if not file_paths:
            console.print("[yellow]No eligible files found to process.[/yellow]")
            raise typer.Exit(code=0)
    else:
        # Convert string file arguments to Path objects
        file_paths = []
        for file_str in files:
            file_path = Path(file_str)
            # Convert relative paths to absolute paths based on current working directory
            if not file_path.is_absolute():
                file_path = Path.cwd() / file_path
            # Resolve to handle symlinks (e.g., /var -> /private/var on macOS)
            file_path = file_path.resolve()
            file_paths.append(file_path)

    # Validate provided/discovered files
    for file_path in file_paths:
        if not file_path.exists():
            console.print(f"[bold red]Error:[/bold red] File '{file_path}' does not exist.")
            raise typer.Exit(code=1)
        if not file_path.is_file():
            console.print(f"[bold red]Error:[/bold red] '{file_path}' is not a file.")
            raise typer.Exit(code=1)

    mode = "check" if check else "fix"

    # Process files in parallel with delete operation
    results = process_files_parallel(
        files=file_paths,
        project_root=project_root,
        mode=mode,
        workers=workers,
        show_progress=show_progress,
        operation="delete",
    )

    # Print summary if verbose or if there were changes/errors
    has_removals = any(r.result.name == "REMOVED" for r in results)
    has_errors = any(r.error is not None for r in results)

    if verbose or has_errors:
        print_processing_summary(results, mode, show_details=verbose)
    elif has_removals and not check:
        if all_files:
            # Show concise summary for bulk operations
            removed_count = sum(1 for r in results if r.result.name == "REMOVED")
            console.print(f"Successfully deleted hook from {removed_count} files.")
        else:
            # Show individual files for specific file operations
            for result in results:
                if result.result.name == "REMOVED":
                    console.print(f"Removed header from {result.file_path}")
    elif has_removals and check:
        if all_files:
            # Show concise summary for bulk check operations
            removed_count = sum(1 for r in results if r.result.name == "REMOVED")
            console.print(f"Would remove header from {removed_count} files.")
        else:
            # Show individual files for specific file check operations
            for result in results:
                if result.result.name == "REMOVED":
                    console.print(f"Would remove header from {result.file_path}")

    # Exit with error code if in check mode and there were changes or errors
    if check and (has_removals or has_errors):
        raise typer.Exit(code=1)
    elif has_errors:
        raise typer.Exit(code=1)


@app.command()
def welcome() -> None:
    """Display the welcome message with ASCII art and quick start guide."""
    display_welcome()


def _discover_files(project_root: Path, config: Config) -> List[Path]:
    """Recursively discover files to process under *project_root*.

    The discovery respects *exclude_globs* from the configuration and also
    consults :func:`path_comment.detectors.comment_prefix` to skip binaries or
    unsupported types.
    """
    from .detectors import comment_prefix  # local import to avoid CLI startup cost

    files: List[Path] = []
    for path in project_root.rglob("*"):
        if path.is_file() and not config.should_exclude(path, project_root):
            if comment_prefix(path) is not None:  # only supported types
                files.append(path)
    return files


def main() -> None:
    """Main entry point that handles pre-commit hook behavior."""
    args = sys.argv[1:]
    if not args:  # No arguments
        app()
        return

    # Handle --version flag
    if "--version" in args:
        console.print(f"path-comment-hook {__version__}")
        return

    # Convert -h to --help for better compatibility
    args = ["--help" if arg == "-h" else arg for arg in args]
    sys.argv[1:] = args

    # Check if a known subcommand is present
    known_commands = {
        "run",
        "show-config",
        "delete",
        "welcome",
    }  # Add any other top-level commands
    is_known_command_call = args[0] in known_commands

    # Check if it's a direct help/version call
    is_help_or_version_call = args[0] in {"--help", "-h", "--version"}

    if not is_known_command_call and not is_help_or_version_call:
        # If it's not a known command and not help/version,
        # assume it's files/options for the default 'run' command.
        # This includes cases like 'pch --all', 'pch --check file.py', etc.
        sys.argv.insert(1, "run")

    app()


# Convenience: python -m path_comment.cli
if __name__ == "__main__":
    main()
