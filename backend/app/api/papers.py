import json
import shutil
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import settings
from app.db.vector_store import store_chunks
from app.services.chunker import chunk_sections
from app.services.embedder import embed_texts
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.research_analyzer import analyze_paper
from app.services.section_detector import detect_section_pages, detect_sections
from app.services.text_cleaner import clean_text
from app.utils.file_utils import ensure_directory

router = APIRouter()


@router.get("")
def list_papers() -> dict[str, list[dict[str, object]]]:
    processed_dir = ensure_directory(settings.processed_dir)
    papers: list[dict[str, object]] = []

    for processed_file in sorted(processed_dir.glob("*.json")):
        try:
            paper = json.loads(processed_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue

        papers.append(paper)

    return {"papers": papers}


@router.get("/{paper_id}/analysis")
def get_paper_analysis(paper_id: str) -> dict[str, object]:
    paper = load_processed_paper(paper_id)
    return analyze_paper(paper)


@router.post("/upload")
def upload_paper(file: UploadFile = File(...)) -> dict[str, object]:
    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    upload_dir = ensure_directory(settings.upload_dir)
    processed_dir = ensure_directory(settings.processed_dir)

    original_filename = Path(file.filename).name
    paper_id = generate_paper_id(upload_dir, processed_dir)
    filename = f"{paper_id}.pdf"
    pdf_path = upload_dir / filename
    processed_path = processed_dir / f"{paper_id}.json"

    with pdf_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    pages = extract_text_from_pdf(pdf_path)
    raw_text = "\n".join(page["text"] for page in pages)
    cleaned_text = clean_text(raw_text)
    sections = detect_sections(cleaned_text)
    section_pages = detect_section_pages(pages)
    chunks = chunk_sections(sections, paper_id=paper_id, section_pages=section_pages)
    embeddings = embed_texts([chunk["text"] for chunk in chunks])
    store_chunks(chunks, embeddings)

    processed_data = {
        "paper_id": paper_id,
        "filename": filename,
        "original_filename": original_filename,
        "sections": sections,
        "chunks": chunks,
    }

    processed_path.write_text(
        json.dumps(processed_data, indent=2),
        encoding="utf-8",
    )

    return {
        "paper_id": paper_id,
        "filename": filename,
        "original_filename": original_filename,
        "pdf_path": str(pdf_path),
        "processed_path": str(processed_path),
        "sections": sections,
        "chunks": chunks,
    }


def generate_paper_id(upload_dir: Path, processed_dir: Path) -> str:
    used_numbers: set[int] = set()

    for path in [*upload_dir.glob("paper-*.pdf"), *processed_dir.glob("paper-*.json")]:
        try:
            used_numbers.add(int(path.stem.removeprefix("paper-")))
        except ValueError:
            continue

    next_number = 1
    while next_number in used_numbers:
        next_number += 1

    return f"paper-{next_number}"


def load_processed_paper(paper_id: str) -> dict[str, object]:
    processed_dir = ensure_directory(settings.processed_dir)
    normalized_paper_id = Path(paper_id).stem
    processed_path = processed_dir / f"{normalized_paper_id}.json"

    if not processed_path.exists():
        raise HTTPException(status_code=404, detail="Paper not found.")

    try:
        return json.loads(processed_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail="Processed paper JSON is invalid.") from exc
