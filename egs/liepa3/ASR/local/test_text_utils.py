import pytest

from text_utils import clean_text, remove_accent, allowed_lt


def test_remove_accent_keeps_ascii_and_allowed():
    assert remove_accent('a') == 'a'
    assert remove_accent(' ') == ' '
    for c in allowed_lt:
        assert remove_accent(c) == c


def test_remove_accent_normalizes_other_letters():
    # 'é' should be normalized to 'e' plus combining accent in NFKD,
    # but function returns the NFKD result which may include combining mark.
    out = remove_accent('é')
    assert out == 'e'


def test_clean_text_basic():
    s, ok = clean_text("Hello, WORLD!")
    assert ok
    assert s == "hello world"

def test_clean_text_lt():
    s, ok = clean_text("ČĘĖĮŠŲŪŽ ąčęėįšųūž olia")
    assert ok
    assert s == "čęėįšųūž ąčęėįšųūž olia"

def test_clean_text_punctuation_and_spaces():
    s, ok = clean_text("This\t is---a test!!!")
    assert ok
    assert s == "this is a test"


def test_clean_text_disallowed_char():
    s, ok = clean_text("hello 2")
    assert not ok
    assert s == ""

