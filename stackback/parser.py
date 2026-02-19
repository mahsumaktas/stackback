"""Parse terminal errors and exceptions."""
import re
from dataclasses import dataclass


@dataclass
class ParsedError:
    error_type: str
    message: str
    file: str | None = None
    line: int | None = None
    raw: str = ""


def parse_output(output: str) -> ParsedError | None:
    """Extract structured error info from command output."""
    # Python exceptions
    py_match = re.search(
        r"(\w+Error|\w+Exception): (.+?)(?:\n|$)", output
    )
    if py_match:
        error_type, message = py_match.groups()
        file_match = re.search(r'File "(.+?)", line (\d+)', output)
        return ParsedError(
            error_type=error_type,
            message=message.strip(),
            file=file_match.group(1) if file_match else None,
            line=int(file_match.group(2)) if file_match else None,
            raw=output,
        )
    return None
