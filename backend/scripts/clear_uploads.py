from pathlib import Path
import shutil


BACKEND_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = BACKEND_DIR / "uploads"
PROCESSED_DIR = BACKEND_DIR / "processed"
CHROMA_DB_DIR = BACKEND_DIR / "chroma_db"


def clear_uploaded_pdfs() -> int:
    if not UPLOAD_DIR.exists():
        return 0

    deleted_count = 0
    for pdf_path in UPLOAD_DIR.glob("*.pdf"):
        pdf_path.unlink()
        deleted_count += 1

    return deleted_count


def clear_processed_json() -> int:
    if not PROCESSED_DIR.exists():
        return 0

    deleted_count = 0
    for json_path in PROCESSED_DIR.glob("*.json"):
        json_path.unlink()
        deleted_count += 1

    return deleted_count


def clear_chroma_db() -> bool:
    if not CHROMA_DB_DIR.exists():
        return False

    shutil.rmtree(CHROMA_DB_DIR)
    return True


if __name__ == "__main__":
    deleted_pdfs = clear_uploaded_pdfs()
    deleted_json = clear_processed_json()
    deleted_chroma = clear_chroma_db()

    print(f"Deleted {deleted_pdfs} uploaded PDF file(s).")
    print(f"Deleted {deleted_json} processed JSON file(s).")
    print(f"Deleted Chroma DB: {deleted_chroma}.")
