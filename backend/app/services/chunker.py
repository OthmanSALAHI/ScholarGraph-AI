from typing import TypedDict


class Chunk(TypedDict):
    chunk_id: str
    paper_id: str
    section: str
    text: str
    page: int | None


SectionMap = dict[str, str]
SectionPages = dict[str, int]


def chunk_text(text: str, chunk_size: int = 1000) -> list[str]:
    if not text:
        return []
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


def chunk_sections(
    sections: SectionMap,
    paper_id: str,
    section_pages: SectionPages | None = None,
    chunk_size: int = 1000,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    section_pages = section_pages or {}

    for section, text in sections.items():
        section_text = text.strip()
        if not section_text:
            continue

        for text_chunk in chunk_text(section_text, chunk_size):
            chunk_number = len(chunks) + 1
            chunks.append(
                {
                    "chunk_id": f"{paper_id}_chunk_{chunk_number:03d}",
                    "paper_id": paper_id,
                    "section": section,
                    "text": text_chunk.strip(),
                    "page": section_pages.get(section),
                }
            )

    return chunks
