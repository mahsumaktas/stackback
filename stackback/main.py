"""stackback - AI-powered terminal error fixer.

Usage:
    sb python app.py
    sb pytest tests/
    stackback python app.py --provider claude
"""
import subprocess
import sys
import os
from typing import Optional

import typer
from rich.console import Console

from .parser import parse_error, is_error_output
from .llm import LLMExplainer
from .tui import show_menu

app = typer.Typer(
    help="AI-powered terminal error fixer. Run any command and fix errors with AI.",
    add_completion=False,
)
console = Console()
err_console = Console(stderr=True)

VERSION = "0.0.4"


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def run(
    command: list[str] = typer.Argument(..., help="Command to run (e.g. python app.py)"),
    provider: str = typer.Option(
        "openai", "--provider", "-p",
        help="LLM provider: openai, claude, gemini, mock",
    ),
    api_key: Optional[str] = typer.Option(
        None, "--api-key", "-k",
        help="API key (or set OPENAI_API_KEY env var)",
        envvar="OPENAI_API_KEY",
    ),
    no_ai: bool = typer.Option(
        False, "--no-ai",
        help="Skip AI and just parse the error",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="Show full output even without errors",
    ),
) -> None:
    """Run a command and fix errors with AI assistance.

    Example:
        sb python app.py
        sb pytest tests/ --provider mock
    """
    if not command:
        err_console.print("[red]Error:[/red] No command provided")
        raise typer.Exit(code=1)

    console.print(f"[dim]stackback v{VERSION} | Running:[/dim] [bold]{' '.join(command)}[/bold]\n")

    # Run the command and capture output
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        err_console.print(f"[red]Error:[/red] Command not found: {command[0]}")
        raise typer.Exit(code=127)

    # Combine stdout and stderr for error detection
    combined_output = result.stderr
    if result.returncode == 0 and not combined_output:
        console.print(result.stdout)
        console.print("[green]Command completed successfully.[/green]")
        return

    # Show stdout always
    if result.stdout:
        console.print(result.stdout, end="")

    # Check for errors
    if not is_error_output(combined_output) and result.returncode == 0:
        if verbose:
            console.print(result.stderr)
        console.print("[green]No errors detected.[/green]")
        return

    # Parse the error
    error = parse_error(combined_output)

    if not error:
        # No parseable error, just show the output and exit
        if combined_output:
            console.print(combined_output, end="")
        sys.exit(result.returncode)
        return

    # Setup LLM explainer
    explainer: Optional[LLMExplainer] = None
    if not no_ai:
        key = api_key or os.environ.get("OPENAI_API_KEY", "")
        if key or provider == "mock":
            explainer = LLMExplainer(api_key=key or "", provider=provider)
        else:
            # Use mock mode for demo
            explainer = LLMExplainer(api_key="", provider="mock")

    # Show interactive menu
    try:
        action = show_menu(error, explainer, interactive=sys.stdin.isatty())
    except Exception:
        action = "skip"

    # Exit with the original return code
    if result.returncode != 0:
        raise typer.Exit(code=result.returncode)


def main() -> None:
    """Entry point for 'sb' and 'stackback' commands."""
    app()


if __name__ == "__main__":
    main()
