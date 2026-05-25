import json

from fastapi.testclient import TestClient

from app.api import papers
from app.main import app


def test_upload_paper_saves_pdf_and_processed_json(tmp_path, monkeypatch) -> None:
    upload_dir = tmp_path / "uploads"
    processed_dir = tmp_path / "processed"
    stored_chunks = []
    stored_embeddings = []

    monkeypatch.setattr(papers.settings, "upload_dir", str(upload_dir))
    monkeypatch.setattr(papers.settings, "processed_dir", str(processed_dir))
    monkeypatch.setattr(
        papers,
        "extract_text_from_pdf",
        lambda pdf_path: [
            {
                "page_number": 1,
                "text": "Abstract\nThis   is abstract.\n\n1\nIntroduction\nIntro text.",
            },
            {
                "page_number": 2,
                "text": "Methodology\nMethod text.\nResults\nResult text.\nConclusion\nDone.",
            },
        ],
    )
    monkeypatch.setattr(
        papers,
        "embed_texts",
        lambda texts: [[float(index)] for index, _ in enumerate(texts, start=1)],
    )
    monkeypatch.setattr(
        papers,
        "store_chunks",
        lambda chunks, embeddings: (
            stored_chunks.extend(chunks),
            stored_embeddings.extend(embeddings),
        ),
    )

    client = TestClient(app)
    response = client.post(
        "/api/papers/upload",
        files={"file": ("paper.pdf", b"%PDF-1.4 fake pdf bytes", "application/pdf")},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["paper_id"] == "paper-1"
    assert data["filename"] == "paper-1.pdf"
    assert data["original_filename"] == "paper.pdf"
    assert data["sections"] == {
        "abstract": "This is abstract.",
        "introduction": "Intro text.",
        "methodology": "Method text.",
        "results": "Result text.",
        "conclusion": "Done.",
        "figures": [],
        "tables": [],
    }
    assert data["chunks"][0] == {
        "chunk_id": "paper-1_chunk_001",
        "paper_id": "paper-1",
        "section": "abstract",
        "text": "This is abstract.",
        "page": 1,
    }
    assert stored_chunks == data["chunks"]
    assert stored_embeddings == [[1.0], [2.0], [3.0], [4.0], [5.0]]

    assert (upload_dir / "paper-1.pdf").read_bytes() == b"%PDF-1.4 fake pdf bytes"

    processed_data = json.loads((processed_dir / "paper-1.json").read_text())
    assert processed_data == {
        "paper_id": "paper-1",
        "filename": "paper-1.pdf",
        "original_filename": "paper.pdf",
        "sections": data["sections"],
        "chunks": data["chunks"],
    }


def test_generate_paper_id_uses_next_available_number(tmp_path) -> None:
    upload_dir = tmp_path / "uploads"
    processed_dir = tmp_path / "processed"
    upload_dir.mkdir()
    processed_dir.mkdir()
    (upload_dir / "paper-1.pdf").write_bytes(b"pdf")
    (processed_dir / "paper-2.json").write_text("{}", encoding="utf-8")

    assert papers.generate_paper_id(upload_dir, processed_dir) == "paper-3"


def test_upload_paper_rejects_non_pdf() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/papers/upload",
        files={"file": ("paper.txt", b"not a pdf", "text/plain")},
    )

    assert response.status_code == 400


def test_list_papers_returns_processed_json_files(tmp_path, monkeypatch) -> None:
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()
    monkeypatch.setattr(papers.settings, "processed_dir", str(processed_dir))

    processed_file = processed_dir / "paper.json"
    processed_file.write_text(
        json.dumps(
            {
                "filename": "paper.pdf",
                "sections": {
                    "abstract": "Abstract text.",
                    "introduction": "",
                    "methodology": "",
                    "results": "",
                    "conclusion": "",
                    "figures": [],
                    "tables": [],
                },
            }
        ),
        encoding="utf-8",
    )

    client = TestClient(app)
    response = client.get("/api/papers")

    assert response.status_code == 200
    assert response.json() == {
        "papers": [
            {
                "filename": "paper.pdf",
                "sections": {
                    "abstract": "Abstract text.",
                    "introduction": "",
                    "methodology": "",
                    "results": "",
                    "conclusion": "",
                    "figures": [],
                    "tables": [],
                },
            }
        ]
    }


def test_get_paper_analysis_returns_structured_analysis(tmp_path, monkeypatch) -> None:
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()
    monkeypatch.setattr(papers.settings, "processed_dir", str(processed_dir))

    (processed_dir / "paper-1.json").write_text(
        json.dumps(
            {
                "paper_id": "paper-1",
                "filename": "paper-1.pdf",
                "original_filename": "script_switching.pdf",
                "sections": {
                    "abstract": "This study investigates script-switching robustness.",
                    "introduction": "The problem is that models fail on Arabizi.",
                    "methodology": "The study uses a controlled experiment.",
                    "results": "The results confirm a large performance drop.",
                    "conclusion": "Future work should explore better training.",
                },
            }
        ),
        encoding="utf-8",
    )

    client = TestClient(app)
    response = client.get("/api/papers/paper-1/analysis")

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Script Switching"
    assert data["problem"] == "The problem is that models fail on Arabizi."
    assert data["objective"] == "This study investigates script-switching robustness."
    assert data["method"] == "The study uses a controlled experiment."
    assert data["results"] == ["The results confirm a large performance drop."]
    assert data["future_work"] == ["Future work should explore better training."]


def test_get_paper_analysis_returns_404_for_missing_paper(tmp_path, monkeypatch) -> None:
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()
    monkeypatch.setattr(papers.settings, "processed_dir", str(processed_dir))

    client = TestClient(app)
    response = client.get("/api/papers/missing/analysis")

    assert response.status_code == 404
