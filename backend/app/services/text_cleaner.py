import re


_PAGE_NUMBER_PATTERN = re.compile(r"^\s*(?:page\s*)?\d+\s*$", re.IGNORECASE)
_DUPLICATE_SPACE_PATTERN = re.compile(r"[ \t]{2,}")
_BROKEN_WORD_PATTERN = re.compile(r"(\w)-\s*\n\s*(\w)")
_SENTENCE_END_PATTERN = re.compile(r"[.!?:;]$")
_LIKELY_HEADING_PATTERN = re.compile(
    r"^\s*(?:\d+(?:\.\d+)*\.?\s+)?[A-Z][A-Za-z ]{2,}\s*$"
)


def clean_text(text: str) -> str:
    text = _remove_page_numbers(text)
    text = _fix_broken_lines(text)
    text = _remove_empty_lines(text)
    text = _remove_duplicate_spaces(text)
    return text.strip()


def _remove_page_numbers(text: str) -> str:
    lines = text.splitlines()
    return "\n".join(line for line in lines if not _PAGE_NUMBER_PATTERN.match(line))


def _fix_broken_lines(text: str) -> str:
    text = _BROKEN_WORD_PATTERN.sub(r"\1\2", text)
    lines = text.splitlines()
    fixed_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            fixed_lines.append("")
            continue

        if not fixed_lines or not fixed_lines[-1]:
            fixed_lines.append(stripped)
            continue

        previous = fixed_lines[-1]
        if (
            _SENTENCE_END_PATTERN.search(previous)
            or _is_likely_heading(previous)
            or _is_likely_heading(stripped)
        ):
            fixed_lines.append(stripped)
        else:
            fixed_lines[-1] = f"{previous} {stripped}"

    return "\n".join(fixed_lines)


def _remove_empty_lines(text: str) -> str:
    lines = (line.strip() for line in text.splitlines())
    return "\n".join(line for line in lines if line)


def _remove_duplicate_spaces(text: str) -> str:
    return _DUPLICATE_SPACE_PATTERN.sub(" ", text)


def _is_likely_heading(line: str) -> bool:
    return bool(_LIKELY_HEADING_PATTERN.match(line)) and len(line.split()) <= 4
