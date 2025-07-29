# src/path_comment/welcome.py

"""Welcome message for path-comment-hook installation."""

from rich.console import Console

WELCOME_BANNER = r"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         PATH COMMENT HOOK v0.1.0                             ║
║                                                                               ║
║    Add file path comments to source files for better navigation              ║
║    and code organization                                                      ║
║                                                                               ║
║    Repository: https://github.com/Shorzinator/path-comment-hook               ║
║    Documentation: https://shorzinator.github.io/path-comment-hook            ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""


def display_welcome() -> None:
    """Display welcome message with banner and next steps."""
    console = Console()

    # Display banner
    console.print(WELCOME_BANNER, style="cyan")

    # Next steps
    console.print("\nNext Steps:", style="bold green")
    console.print("1. Run: path-comment --help", style="dim")
    console.print("2. Try: path-comment your_file.py", style="dim")
    console.print("3. Set up pre-commit hooks for automation", style="dim")
    console.print("4. Configure custom settings in pyproject.toml", style="dim")

    console.print("\nDocumentation:", style="bold blue")
    console.print("https://shorzinator.github.io/path-comment-hook", style="dim")

    console.print(
        ("Happy coding!", "bold magenta"),
    )


if __name__ == "__main__":
    display_welcome()
