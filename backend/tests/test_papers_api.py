import json

from fastapi.testclient import TestClient

from app.api import papers
from app.main import app


def test_upload_paper_saves_pdf_and_processed_json(tmp_path, monkeypatch) -> None:
    upload_dir = tmp_path / "uploads"
    processed_dir = tmp_path / "processed"

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

    client = TestClient(app)
    response = client.post(
        "/api/papers/upload",
        files={"file": ("paper.pdf", b"%PDF-1.4 fake pdf bytes", "application/pdf")},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["filename"] == "paper.pdf"
    assert data["sections"] == {
        "abstract": "This is abstract.",
        "introduction": "Intro text.",
        "methodology": "Method text.",
        "results": "Result text.",
        "conclusion": "Done.",
        "figures": [],
        "tables": [],
    }

    assert (upload_dir / "paper.pdf").read_bytes() == b"%PDF-1.4 fake pdf bytes"

    processed_data = json.loads((processed_dir / "paper.json").read_text())
    assert processed_data == {
        "filename": "paper.pdf",
        "sections": data["sections"],
    }


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
