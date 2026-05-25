from fastapi.testclient import TestClient

from app.api import chat
from app.main import app


def test_chat_returns_best_chunks_as_answer(monkeypatch) -> None:
    retrieved_chunks = [
        {
            "chunk_id": "paper_001_chunk_001",
            "paper_id": "paper_001",
            "section": "abstract",
            "text": "This paper solves retrieval over research PDFs.",
            "page": 1,
            "score": 0.1,
        }
    ]
    monkeypatch.setattr(
        chat,
        "retrieve_chunks",
        lambda question, paper_id: retrieved_chunks,
    )
    monkeypatch.setattr(
        chat,
        "generate_answer",
        lambda question, chunks: "This paper solves retrieval over research PDFs.",
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


def test_chat_accepts_pdf_filename_as_paper_id(monkeypatch) -> None:
    seen_paper_ids = []
    monkeypatch.setattr(
        chat,
        "retrieve_chunks",
        lambda question, paper_id: (
            seen_paper_ids.append(paper_id)
            or [
                {
                    "chunk_id": "paper_chunk_001",
                    "paper_id": paper_id,
                    "section": "abstract",
                    "text": "Paper context.",
                    "page": 1,
                    "score": 0.1,
                }
            ]
        ),
    )
    monkeypatch.setattr(chat, "generate_answer", lambda question, chunks: "Answer.")

    client = TestClient(app)
    response = client.post(
        "/api/chat",
        json={"paper_id": "paper.pdf", "question": "What is it about?"},
    )

    assert response.status_code == 200
    assert seen_paper_ids == ["paper"]


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


def test_chat_returns_service_unavailable_for_missing_dependencies(monkeypatch) -> None:
    monkeypatch.setattr(
        chat,
        "retrieve_chunks",
        lambda question, paper_id: (_ for _ in ()).throw(RuntimeError("chromadb is required")),
    )

    client = TestClient(app)
    response = client.post(
        "/api/chat",
        json={"paper_id": "paper_001", "question": "Unknown?"},
    )

    assert response.status_code == 503
    assert response.json() == {"detail": "chromadb is required"}
