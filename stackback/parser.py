import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class ParsedError:
    error_type: str
    message: str
    filename: Optional[str]
    line_number: Optional[int]
    traceback: str
    language: str = "python"

def parse_python_traceback(output: str) -> Optional[ParsedError]:
    """Parse Python traceback from stderr output."""
    if 'Traceback (most recent call last):' not in output and not _has_error_line(output):
        return None
    
    # Extract error type and message from last line
    lines = output.strip().splitlines()
    error_line = None
    for line in reversed(lines):
        match = re.match(r'^(\w+(?:\.\w+)*Error|\w+Exception|SyntaxError|KeyboardInterrupt):\s*(.*)', line.strip())
        if match:
            error_line = match
            break
    
    if not error_line:
        # Try simple error without "Error" suffix
        for line in reversed(lines):
            match = re.match(r'^(\w+):\s+(.+)', line.strip())
            if match and len(match.group(1)) > 2:
                error_line = match
                break
    
    error_type = error_line.group(1) if error_line else "UnknownError"
    message = error_line.group(2) if error_line else output.split('\n')[-1]
    
    # Extract filename and line number from traceback
    filename = None
    line_number = None
    file_matches = re.findall(r'File "([^"]+)", line (\d+)', output)
    if file_matches:
        # Last occurrence = innermost frame = where error happened
        last_file, last_line = file_matches[-1]
        # Skip stdlib files
        if not ('lib/python' in last_file or 'site-packages' in last_file):
            filename = last_file
            line_number = int(last_line)
        elif file_matches:
            filename = file_matches[-1][0]
            line_number = int(file_matches[-1][1])
    
    return ParsedError(
        error_type=error_type,
        message=message,
        filename=filename,
        line_number=line_number,
        traceback=output
    )

def _has_error_line(output: str) -> bool:
    """Check if output has a Python error line."""
    return bool(re.search(r'^\w+(?:Error|Exception|Warning):', output, re.MULTILINE))

def is_error_output(output: str) -> bool:
    """Returns True if output contains a Python error/traceback."""
    return 'Traceback (most recent call last):' in output or _has_error_line(output)

def run_and_capture(command: List[str]) -> tuple[str, str, int]:
    """Run command and capture stdout, stderr, exit code."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out after 30 seconds", 1
    except FileNotFoundError:
        return "", f"Command not found: {command[0]}", 1