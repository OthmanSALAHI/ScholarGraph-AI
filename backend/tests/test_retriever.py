from app.services import retriever


def test_retrieve_chunks_embeds_question_and_formats_results(monkeypatch) -> None:
    monkeypatch.setattr(retriever, "embed_text", lambda question: [0.1, 0.2])
    monkeypatch.setattr(
        retriever,
        "search_chunks",
        lambda query_embedding, limit, paper_id: {
            "ids": [["paper_001_chunk_001"]],
            "documents": [["Relevant chunk text."]],
            "metadatas": [[{"paper_id": paper_id, "section": "abstract", "page": 1}]],
            "distances": [[0.12]],
        },
    )

    assert retriever.retrieve_chunks("What problem?", paper_id="paper_001") == [
        {
            "chunk_id": "paper_001_chunk_001",
            "text": "Relevant chunk text.",
            "paper_id": "paper_001",
            "section": "abstract",
            "page": 1,
            "score": 0.12,
        }
    ]


def test_retrieve_chunks_returns_empty_for_blank_question(monkeypatch) -> None:
    monkeypatch.setattr(retriever, "embed_text", lambda question: [])

    assert retriever.retrieve_chunks("   ", paper_id="paper_001") == []
