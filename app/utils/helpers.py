"""
General-purpose utility functions.
"""

import re
import time
import unicodedata
from pathlib import Path


def clean_text(text: str) -> str:
    """Normalize whitespace and strip control characters from text."""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def truncate_text(text: str, max_chars: int = 2000, suffix: str = "...") -> str:
    """Truncate text to max_chars, appending suffix if truncated."""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - len(suffix)] + suffix


def format_duration(seconds: float) -> str:
    """Convert seconds to a human-readable duration string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}m {secs}s"


def sanitize_filename(name: str) -> str:
    """Strip characters unsafe for filenames."""
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    name = re.sub(r"\s+", "_", name.strip())
    return name[:100]  # cap length


def read_file_text(path: str | Path) -> str:
    """Read a text file, returning empty string on error."""
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception:
        return ""


def timer() -> callable:
    """Return a callable that reports elapsed seconds since creation."""
    start = time.perf_counter()
    return lambda: time.perf_counter() - start
