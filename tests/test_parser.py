"""Tests for the error parser."""
import pytest
from stackback.parser import parse_error, parse_output, is_error_output, ParsedError


# === Full Traceback Tests ===

def test_parse_python_typeerror():
    output = '''Traceback (most recent call last):
  File "app.py", line 42, in <module>
    data[idx]
TypeError: list indices must be integers, not str'''
    result = parse_output(output)
    assert result is not None
    assert result.error_type == "TypeError"
    assert "integers" in result.message
    # Test both new and legacy field names
    assert result.filename == "app.py"
    assert result.file == "app.py"       # legacy alias
    assert result.line_number == 42
    assert result.line == 42             # legacy alias
    assert result.language == "python"


def test_parse_python_valueerror():
    output = '''Traceback (most recent call last):
  File "converter.py", line 7, in convert
    return int(s)
ValueError: invalid literal for int() with base 10: 'abc' '''
    result = parse_error(output)
    assert result is not None
    assert result.error_type == "ValueError"
    assert "literal" in result.message
    assert result.filename == "converter.py"


def test_parse_python_importerror():
    output = '''Traceback (most recent call last):
  File "main.py", line 1, in <module>
    import numpy as np
ModuleNotFoundError: No module named 'numpy' '''
    result = parse_error(output)
    assert result is not None
    assert "ModuleNotFoundError" in result.error_type
    assert "numpy" in result.message
    assert result.filename == "main.py"


def test_parse_python_keyerror():
    output = '''Traceback (most recent call last):
  File "app.py", line 15, in <module>
    name = config["database"]["host"]
KeyError: 'host' '''
    result = parse_error(output)
    assert result is not None
    assert result.error_type == "KeyError"
    assert result.line_number == 15


def test_parse_python_attributeerror():
    output = '''Traceback (most recent call last):
  File "model.py", line 30, in predict
    return self.model.predict(X)
AttributeError: 'NoneType' object has no attribute 'predict' '''
    result = parse_error(output)
    assert result is not None
    assert result.error_type == "AttributeError"
    assert result.filename == "model.py"
    assert result.line_number == 30


def test_parse_python_nameerror():
    output = '''Traceback (most recent call last):
  File "script.py", line 3, in <module>
    print(undefined_var)
NameError: name 'undefined_var' is not defined'''
    result = parse_error(output)
    assert result is not None
    assert result.error_type == "NameError"
    assert "undefined_var" in result.message


def test_parse_syntax_error():
    output = '''  File "bad.py", line 5
    if x =  5:
         ^
SyntaxError: invalid syntax'''
    result = parse_error(output)
    assert result is not None
    assert result.error_type == "SyntaxError"
    assert result.filename == "bad.py"
    assert result.line_number == 5


def test_parse_filenotfounderror():
    output = '''Traceback (most recent call last):
  File "app.py", line 10, in load_config
    with open("config.json") as f:
FileNotFoundError: [Errno 2] No such file or directory: 'config.json' '''
    result = parse_error(output)
    assert result is not None
    assert result.error_type == "FileNotFoundError"
    assert "config.json" in result.message


def test_parse_zerodivision():
    output = '''Traceback (most recent call last):
  File "calc.py", line 8, in divide
    return a / b
ZeroDivisionError: division by zero'''
    result = parse_error(output)
    assert result is not None
    assert result.error_type == "ZeroDivisionError"
    assert result.filename == "calc.py"


def test_parse_nested_traceback():
    """Parser should extract innermost frame."""
    output = '''Traceback (most recent call last):
  File "main.py", line 20, in main
    result = process(data)
  File "processor.py", line 15, in process
    return transform(item)
  File "transform.py", line 8, in transform
    return int(item)
ValueError: invalid literal for int() with base 10: 'bad' '''
    result = parse_error(output)
    assert result is not None
    assert result.error_type == "ValueError"
    # Should use innermost frame
    assert result.filename == "transform.py"
    assert result.line_number == 8


# === No-error Tests ===

def test_parse_no_error():
    assert parse_error("Hello, world!") is None


def test_parse_empty_string():
    assert parse_error("") is None


def test_parse_none_returns_none():
    assert parse_error(None) is None


def test_parse_successful_command():
    output = "Tests passed: 42\nOK"
    assert parse_error(output) is None


# === is_error_output Tests ===

def test_is_error_output_traceback():
    output = "Traceback (most recent call last):\n  File 'x.py', line 1\nTypeError: bad type"
    assert is_error_output(output) is True


def test_is_error_output_single_line():
    assert is_error_output("ValueError: invalid value") is True


def test_is_error_output_false():
    assert is_error_output("All tests passed!") is False


def test_is_error_output_empty():
    assert is_error_output("") is False


# === ParsedError dataclass tests ===

def test_parsed_error_legacy_aliases():
    """file and line are aliases for filename and line_number."""
    err = ParsedError(
        error_type="TypeError",
        message="bad type",
        filename="app.py",
        line_number=10,
        traceback="...",
    )
    assert err.file == "app.py"
    assert err.line == 10
    assert err.raw == "..."


def test_traceback_stored():
    output = '''Traceback (most recent call last):
  File "app.py", line 1
TypeError: bad'''
    result = parse_error(output)
    assert result is not None
    assert result.traceback == output


# === LLM Mock Tests ===

def test_llm_mock_explain():
    from stackback.llm import LLMExplainer
    explainer = LLMExplainer(api_key="")  # mock mode
    error = ParsedError("TypeError", "bad type", "app.py", 1, "...", "python")
    explanation = explainer.explain(error)
    assert isinstance(explanation, str)
    assert len(explanation) > 0


def test_llm_mock_fix():
    from stackback.llm import LLMExplainer
    explainer = LLMExplainer(api_key="")
    error = ParsedError("KeyError", "key not found", "app.py", 5, "...", "python")
    fix = explainer.suggest_fix(error)
    assert isinstance(fix, str)
    assert len(fix) > 0


def test_llm_build_prompt():
    from stackback.llm import LLMExplainer
    explainer = LLMExplainer(api_key="")
    error = ParsedError("ValueError", "invalid value", "app.py", 3, "Traceback...", "python")
    prompt = explainer._build_prompt(error)
    assert "ValueError" in prompt
    assert "invalid value" in prompt
    assert "app.py" in prompt
