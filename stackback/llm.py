import os
from typing import Optional
from .parser import ParsedError

EXPLAIN_PROMPT = """You are a helpful Python debugging assistant. A developer ran their Python script and got this error:

Error Type: {error_type}
Message: {message}
File: {filename} (line {line_number})

Full traceback:
```
{traceback}
```

Please:
1. Explain what caused this error in 2-3 sentences (plain English, no jargon)
2. Suggest a concrete fix with a code example

Be concise and practical."""

FIX_PROMPT = """Python error: {error_type}: {message}
Traceback:
{traceback}

Provide ONLY the fixed code snippet (no explanation, just the corrected code)."""

MOCK_EXPLANATIONS = {
    "TypeError": "A TypeError occurs when an operation is applied to an object of inappropriate type. For example, trying to use a string where an integer is expected. Check the variable types at the line shown in the traceback.",
    "ValueError": "A ValueError occurs when a function receives an argument of the correct type but an inappropriate value. Check the input being passed to the function.",
    "FileNotFoundError": "The file or directory you're trying to open doesn't exist at the specified path. Check if the path is correct and the file exists.",
    "ImportError": "Python can't find the module you're trying to import. Make sure it's installed (pip install <module>) and the name is correct.",
    "AttributeError": "You're trying to access an attribute or method that doesn't exist on this object. Check the object type and available methods.",
    "KeyError": "You're trying to access a dictionary key that doesn't exist. Check if the key is present before accessing it, or use .get() with a default.",
    "IndexError": "You're trying to access a list index that's out of range. The list is shorter than expected. Check the list length before indexing.",
    "NameError": "You're using a variable name that hasn't been defined yet. Check for typos or make sure the variable is defined before use.",
}

class LLMExplainer:
    def __init__(self, api_key: Optional[str] = None, provider: str = "openai"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
        self.provider = provider
        self._client = None
    
    def _get_client(self):
        if self._client:
            return self._client
        if self.provider == "openai" and self.api_key:
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
                return self._client
            except ImportError:
                pass
        return None
    
    def explain(self, error: ParsedError) -> str:
        """Returns plain-English explanation. Falls back to built-in explanations."""
        client = self._get_client()
        if client:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": EXPLAIN_PROMPT.format(
                        error_type=error.error_type,
                        message=error.message,
                        filename=error.filename or "unknown",
                        line_number=error.line_number or "unknown",
                        traceback=error.traceback[:2000]
                    )}],
                    max_tokens=300
                )
                return response.choices[0].message.content
            except Exception:
                pass
        
        # Fallback: built-in explanations
        for key, explanation in MOCK_EXPLANATIONS.items():
            if key in error.error_type:
                return explanation
        return f"A {error.error_type} occurred: {error.message}. Check the traceback above for the exact location."
    
    def suggest_fix(self, error: ParsedError) -> str:
        """Returns a fix suggestion."""
        client = self._get_client()
        if client:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": FIX_PROMPT.format(
                        error_type=error.error_type,
                        message=error.message,
                        traceback=error.traceback[:1500]
                    )}],
                    max_tokens=200
                )
                return response.choices[0].message.content
            except Exception:
                pass
        return f"# Fix for {error.error_type}\n# Check: {error.message}"