import re


_CITATION_PATTERN = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")


def extract_citations(text: str) -> list[str]:
    citations: list[str] = []

    for match in _CITATION_PATTERN.finditer(text):
        for citation in match.group(1).split(","):
            normalized = citation.strip()
            if normalized and normalized not in citations:
                citations.append(normalized)

    return citations
