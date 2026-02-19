"""stackback - AI-powered terminal error fixer."""
import typer
from rich.console import Console

app = typer.Typer(help="AI-powered terminal error fixer")
console = Console()


@app.command()
def run(
    command: list[str] = typer.Argument(..., help="Command to run"),
    provider: str = typer.Option("openai", help="LLM provider: openai, claude, gemini, ollama"),
):
    """Run a command and fix errors with AI assistance."""
    console.print(f"[dim]Running: {' '.join(command)}[/dim]")
    console.print("[yellow]stackback v0.0.1 — coming soon[/yellow]")


if __name__ == "__main__":
    app()
