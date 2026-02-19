import os
from unittest.mock import patch
from stackback.llm import LLMExplainer
from stackback.parser import ParsedError

# Ensure no real API calls are made during tests
os.environ["OPENAI_API_KEY"] = "sk-fake-key-for-testing"

def test_mock_explain_type_error():
    """Test that the fallback explanation is used when no API key is provided."""
    explainer = LLMExplainer(api_key=None)  # No API key
    error = ParsedError(
        error_type="TypeError",
        message="unsupported operand type(s)",
        filename="app.py",
        line_number=10,
        traceback="Traceback...",
    )
    explanation = explainer.explain(error)
    assert "TypeError" in explanation
    assert "operation is applied to an object of inappropriate type" in explanation

def test_mock_explain_unknown_error():
    """Test fallback for an error type not in the mock explanations."""
    explainer = LLMExplainer(api_key=None)
    error = ParsedError(
        error_type="CustomUnseenError",
        message="Something very specific went wrong",
        filename="lib.py",
        line_number=50,
        traceback="Traceback...",
    )
    explanation = explainer.explain(error)
    assert "CustomUnseenError" in explanation
    assert "Something very specific went wrong" in explanation

def test_suggest_fix_returns_string():
    """Test that suggest_fix returns a string, even with a fake key."""
    # This will fail the API call and return the fallback string
    explainer = LLMExplainer(api_key="sk-fake-key")
    error = ParsedError(
        error_type="ValueError",
        message="invalid literal",
        filename="parser.py",
        line_number=25,
        traceback="Traceback...",
    )
    with patch("openai.OpenAI") as mock_openai:
        # Prevent actual API call
        mock_openai.return_value.chat.completions.create.side_effect = Exception("API call failed")
        
        fix_suggestion = explainer.suggest_fix(error)
        assert isinstance(fix_suggestion, str)
        assert "# Fix for ValueError" in fix_suggestion
        assert "# Check: invalid literal" in fix_suggestion

def test_llm_initialization_with_env_var():
    """Test that the explainer can be initialized with an environment variable."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-env-var-key"}):
        explainer = LLMExplainer()
        assert explainer.api_key == "sk-env-var-key"

def test_no_api_key_provided():
    """Test that the explainer works without any API key."""
    with patch.dict(os.environ, clear=True):
        explainer = LLMExplainer(api_key=None)
        assert explainer.api_key is None
        error = ParsedError("NameError", "name 'x' is not defined", "test.py", 1, "...")
        explanation = explainer.explain(error)
        assert "NameError" in explanation
        assert "variable name that hasn't been defined" in explanation
