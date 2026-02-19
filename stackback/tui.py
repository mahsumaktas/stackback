from typing import Optional
from .parser import ParsedError

def show_error_header(error: ParsedError) -> None:
    """Display the error header."""
    location = ""
    if error.filename and error.line_number:
        location = f"  ({error.filename}:{error.line_number})"
    print(f"\n✗ {error.error_type}: {error.message}{location}\n")

def show_menu() -> str:
    """Show interactive menu and return choice."""
    print("What would you like to do?")
    print("  [1] Explain — what went wrong and why")
    print("  [2] Fix — get a code fix suggestion")
    print("  [3] Stack Overflow — search for solutions")
    print("  [4] Skip — continue without action")
    print()
    
    while True:
        try:
            choice = input("Choice [1-4]: ").strip()
            if choice in ('1', '2', '3', '4', 'q', 'skip'):
                return choice
            print("Please enter 1, 2, 3, or 4")
        except (EOFError, KeyboardInterrupt):
            return '4'

def run_interactive(error: ParsedError, explainer=None) -> str:
    """Run interactive TUI flow. Returns action taken."""
    show_error_header(error)
    choice = show_menu()
    
    if choice == '1':
        if explainer:
            print("\nExplanation:\n")
            print(explainer.explain(error))
        else:
            print(f"\n{error.error_type}: {error.message}")
        return 'explain'
    elif choice == '2':
        if explainer:
            print("\nSuggested fix:\n")
            print(explainer.suggest_fix(error))
        else:
            print(f"\n# Check line {error.line_number} in {error.filename}")
        return 'fix'
    elif choice == '3':
        import urllib.parse
        query = urllib.parse.quote(f"{error.error_type} {error.message[:80]}")
        url = f"https://stackoverflow.com/search?q={query}&tagged=python"
        print(f"\nStack Overflow search:\n{url}")
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            pass
        return 'stackoverflow'
    else:
        return 'skip'