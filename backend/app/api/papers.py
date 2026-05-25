import json
import shutil
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import settings
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.section_detector import detect_sections
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


@router.post("/upload")
def upload_paper(file: UploadFile = File(...)) -> dict[str, object]:
    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    upload_dir = ensure_directory(settings.upload_dir)
    processed_dir = ensure_directory(settings.processed_dir)

    filename = Path(file.filename).name
    pdf_path = upload_dir / filename
    processed_path = processed_dir / f"{pdf_path.stem}.json"

    with pdf_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    pages = extract_text_from_pdf(pdf_path)
    raw_text = "\n".join(page["text"] for page in pages)
    cleaned_text = clean_text(raw_text)
    sections = detect_sections(cleaned_text)

    processed_data = {
        "filename": filename,
        "sections": sections,
    }

    processed_path.write_text(
        json.dumps(processed_data, indent=2),
        encoding="utf-8",
    )

    return {
        "filename": filename,
        "pdf_path": str(pdf_path),
        "processed_path": str(processed_path),
        "sections": sections,
    }
