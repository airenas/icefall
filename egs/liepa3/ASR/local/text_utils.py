"""Small text utilities extracted from prepare_corpus.py for easier testing.
"""
import unicodedata
from typing import Tuple

allowed_lt = set("ąčęėįšųūž")


def remove_accent(c: str) -> str:
    # Preserve ASCII characters, whitespace, and explicitly allowed Lithuanian letters
    if c.isspace() or c.isascii() or c in allowed_lt:
        return c
    # Normalize to NFKD form then remove combining marks (category 'Mn')
    nkfd = unicodedata.normalize("NFKD", c)
    base_chars = [ch for ch in nkfd if unicodedata.category(ch) != "Mn"]
    return "".join(base_chars)


def clean_text(param: str) -> Tuple[str, bool]:
    """Clean the input text.

    - replace punctuations with spaces
    - collapse whitespace
    - casefold to lowercase
    - attempt to normalize accents (via NFKD)
    - verify characters are ascii, whitespace, or allowed_lt

    Returns (cleaned_text, ok)
    """
    # remove punctuations
    res = "".join(c if c.isalnum() or c.isspace() else " " for c in param)
    # remove double spaces
    res = " ".join(res.split()).casefold()
    res = "".join([remove_accent(c) for c in res])
    for c in res:
        if c.isspace() or (c.isalpha() and (c.isascii() or c in allowed_lt)):
            continue
        return "", False
    return res, True

