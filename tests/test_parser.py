"""Tests for the error parser."""
from stackback.parser import parse_output, ParsedError


def test_parse_python_typeerror():
    output = '''Traceback (most recent call last):
  File "app.py", line 42, in <module>
    data[idx]
TypeError: list indices must be integers, not str'''
    result = parse_output(output)
    assert result is not None
    assert result.error_type == "TypeError"
    assert "integers" in result.message
    assert result.file == "app.py"
    assert result.line == 42


def test_parse_no_error():
    assert parse_output("Hello, world!") is None


def test_parse_nameerror():
    output = 'NameError: name "foo" is not defined'
    result = parse_output(output)
    assert result is not None
    assert result.error_type == "NameError"
