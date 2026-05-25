from app.services.chunker import chunk_sections, chunk_text


def test_chunk_text_splits_text_by_chunk_size() -> None:
    assert chunk_text("abcdef", chunk_size=2) == ["ab", "cd", "ef"]


def test_chunk_sections_returns_structured_chunks() -> None:
    sections = {
        "abstract": "Short abstract.",
        "introduction": "",
        "methodology": "Methodology text.",
        "results": "Results text.",
    }
    section_pages = {
        "abstract": 1,
        "methodology": 5,
        "results": 8,
    }

    assert chunk_sections(sections, "paper_001", section_pages) == [
        {
            "chunk_id": "paper_001_chunk_001",
            "paper_id": "paper_001",
            "section": "abstract",
            "text": "Short abstract.",
            "page": 1,
        },
        {
            "chunk_id": "paper_001_chunk_002",
            "paper_id": "paper_001",
            "section": "methodology",
            "text": "Methodology text.",
            "page": 5,
        },
        {
            "chunk_id": "paper_001_chunk_003",
            "paper_id": "paper_001",
            "section": "results",
            "text": "Results text.",
            "page": 8,
        },
    ]


def test_chunk_sections_splits_long_sections() -> None:
    sections = {"methodology": "abcdef"}

    assert chunk_sections(sections, "paper_001", {"methodology": 5}, chunk_size=3) == [
        {
            "chunk_id": "paper_001_chunk_001",
            "paper_id": "paper_001",
            "section": "methodology",
            "text": "abc",
            "page": 5,
        },
        {
            "chunk_id": "paper_001_chunk_002",
            "paper_id": "paper_001",
            "section": "methodology",
            "text": "def",
            "page": 5,
        },
    ]
