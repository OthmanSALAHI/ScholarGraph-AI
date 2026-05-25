import re
from pathlib import Path


def extract_title(paper: dict[str, object]) -> str:
    sections = paper.get("sections", {})
    if isinstance(sections, dict):
        title = _title_from_abstract(str(sections.get("abstract", "")))
        if title:
            return title

    original_filename = str(paper.get("original_filename") or paper.get("filename") or "")
    return _title_from_filename(original_filename)


def _title_from_abstract(abstract: str) -> str:
    for line in abstract.splitlines():
        clean_line = line.strip()
        if _looks_like_title(clean_line):
            return clean_line

    return ""


def _title_from_filename(filename: str) -> str:
    stem = Path(filename).stem
    title = re.sub(r"[_-]+", " ", stem).strip()
    return title.title()


def _looks_like_title(line: str) -> bool:
    if not line or len(line) > 160:
        return False

    words = line.split()
    if len(words) < 3:
        return False

    return not line.endswith((".", ":", ";"))
