from app.services.text_cleaner import clean_text


def test_clean_text_removes_empty_lines_duplicate_spaces_and_page_numbers() -> None:
    raw_text = """
1

This   paper   has extra spaces.

Page 2
Another    paragraph.
"""

    assert clean_text(raw_text) == (
        "This paper has extra spaces.\n"
        "Another paragraph."
    )


def test_clean_text_fixes_broken_lines_and_hyphenated_words() -> None:
    raw_text = "This is a hyphen-\nated word\nand this line continues."

    assert clean_text(raw_text) == (
        "This is a hyphenated word and this line continues."
    )


def test_clean_text_preserves_section_headings() -> None:
    raw_text = "Abstract\nThis   is abstract.\nIntroduction\nIntro text."

    assert clean_text(raw_text) == (
        "Abstract\n"
        "This is abstract.\n"
        "Introduction\n"
        "Intro text."
    )
