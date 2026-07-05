from reachkit.normalization.text import compact_text, truncate_text


def test_compact_text_normalizes_whitespace():
    assert compact_text(" Alpha\n\n beta\t gamma ") == "Alpha beta gamma"


def test_compact_text_applies_max_chars_with_marker():
    assert compact_text("abcdefghij", max_chars=8) == "abcde..."


def test_truncate_text_leaves_short_text_unchanged():
    assert truncate_text("short", 10) == "short"
