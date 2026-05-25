from pathlib import Path
from typing import BinaryIO, TypedDict

try:
    from pypdf import PdfReader
except ModuleNotFoundError:
    PdfReader = None


class ExtractedPage(TypedDict):
    page_number: int
    text: str


PdfSource = str | Path | BinaryIO


def extract_text_from_pdf(pdf_source: PdfSource) -> list[ExtractedPage]:
    """Read a PDF and return extracted text for each page."""
    if PdfReader is None:
        raise RuntimeError("pypdf is required to extract text from PDF files.")

    reader = PdfReader(pdf_source)
    pages: list[ExtractedPage] = []

    for index, page in enumerate(reader.pages, start=1):
        pages.append(
            {
                "page_number": index,
                "text": page.extract_text() or "",
            }
        )

    return pages
