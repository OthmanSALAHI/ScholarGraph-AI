from fastapi.testclient import TestClient

from app.api import chat
from app.main import app


def test_chat_returns_best_chunks_as_answer(monkeypatch) -> None:
    monkeypatch.setattr(
        chat,
        "retrieve_chunks",
        lambda question, paper_id: [
            {
                "chunk_id": "paper_001_chunk_001",
                "paper_id": paper_id,
                "section": "abstract",
                "text": "This paper solves retrieval over research PDFs.",
                "page": 1,
                "score": 0.1,
            }
        ],
    )

    client = TestClient(app)
    response = client.post(
        "/api/chat",
        json={
            "paper_id": "paper_001",
            "question": "What problem does this paper solve?",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "This paper solves retrieval over research PDFs.",
        "sources": [
            {
                "chunk_id": "paper_001_chunk_001",
                "paper_id": "paper_001",
                "section": "abstract",
                "text": "This paper solves retrieval over research PDFs.",
                "page": 1,
                "score": 0.1,
            }
        ],
    }


def test_chat_returns_empty_sources_when_no_chunks(monkeypatch) -> None:
    monkeypatch.setattr(chat, "retrieve_chunks", lambda question, paper_id: [])

    client = TestClient(app)
    response = client.post(
        "/api/chat",
        json={"paper_id": "paper_001", "question": "Unknown?"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "No relevant chunks found for this paper.",
        "sources": [],
    }
