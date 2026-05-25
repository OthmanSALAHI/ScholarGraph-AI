import re


SectionValue = str | list[str]
SectionMap = dict[str, SectionValue]


_OUTPUT_SECTIONS = {
    "abstract",
    "introduction",
    "methodology",
    "results",
    "conclusion",
}

_HEADING_ALIASES = {
    "abstract": "abstract",
    "introduction": "introduction",
    "related work": "related_work",
    "background": "related_work",
    "method": "methodology",
    "methods": "methodology",
    "methodology": "methodology",
    "approach": "methodology",
    "proposed method": "methodology",
    "experiments": "experiments",
    "experiment": "experiments",
    "experimental setup": "experiments",
    "results": "results",
    "result": "results",
    "evaluation": "results",
    "discussion": "results",
    "conclusion": "conclusion",
    "conclusions": "conclusion",
    "references": "references",
}

_HEADING_PATTERN = re.compile(
    r"^\s*(?:\d+(?:\.\d+)*\.?\s+)?([A-Z][A-Za-z ]{2,})\s*$"
)
_FIGURE_PATTERN = re.compile(r"^\s*(fig\.?|figure)\s*\d+[:.\-\s].+", re.IGNORECASE)
_TABLE_PATTERN = re.compile(r"^\s*table\s*\d+[:.\-\s].+", re.IGNORECASE)


def detect_sections(text: str) -> SectionMap:
    sections: SectionMap = {section: "" for section in _OUTPUT_SECTIONS}
    sections["figures"] = []
    sections["tables"] = []
    current_section: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        _save_figure_or_table(sections, line)

        section = _detect_heading(line)
        if section:
            _save_section(sections, current_section, current_lines)
            current_section = section
            current_lines = []
            continue

        if current_section:
            current_lines.append(line)

    _save_section(sections, current_section, current_lines)
    return sections


def _detect_heading(line: str) -> str | None:
    match = _HEADING_PATTERN.match(line)
    if not match:
        return None

    heading = re.sub(r"\s+", " ", match.group(1).strip()).lower()
    return _HEADING_ALIASES.get(heading)


def _save_section(
    sections: SectionMap,
    section: str | None,
    lines: list[str],
) -> None:
    if section not in _OUTPUT_SECTIONS:
        return

    content = "\n".join(line.strip() for line in lines).strip()
    sections[section] = content


def _save_figure_or_table(sections: SectionMap, line: str) -> None:
    caption = line.strip()
    if not caption:
        return

    if _FIGURE_PATTERN.match(caption):
        figures = sections["figures"]
        if isinstance(figures, list):
            figures.append(caption)

    if _TABLE_PATTERN.match(caption):
        tables = sections["tables"]
        if isinstance(tables, list):
            tables.append(caption)
