import re
import unicodedata

_NON_WORD = re.compile(r"[^a-z0-9\s\-]")
_WHITESPACE = re.compile(r"\s+")


def clean_text(text) -> str:
    """Lowercase, strip punctuation and collapse whitespace. Safe on None/NaN."""
    if text is None or (isinstance(text, float) and text != text):
        return ""
    text = unicodedata.normalize("NFKC", str(text)).lower()
    text = _NON_WORD.sub(" ", text)
    return _WHITESPACE.sub(" ", text).strip()