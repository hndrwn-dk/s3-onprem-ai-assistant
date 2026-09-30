# tests/test_text_formatter.py

from text_formatter import smart_format_text


def test_smart_format_short():
    assert smart_format_text("hello world") == "hello world"


def test_smart_format_trims():
    text = "word " * 200
    result = smart_format_text(text, max_length=40)
    assert len(result) <= 43
    assert result.endswith("...")
