from pathlib import Path

from app.services import pdf_extractor


class FakePage:
    def __init__(self, text: str | None) -> None:
        self.text = text

    def extract_text(self) -> str | None:
        return self.text


class FakeReader:
    def __init__(self, pdf_source: Path) -> None:
        self.pdf_source = pdf_source
        self.pages = [
            FakePage("First page text"),
            FakePage(None),
            FakePage("Third page text"),
        ]


def test_extract_text_from_pdf_returns_text_with_page_numbers(monkeypatch) -> None:
    monkeypatch.setattr(pdf_extractor, "PdfReader", FakeReader)

    pages = pdf_extractor.extract_text_from_pdf(Path("paper.pdf"))

    assert pages == [
        {"page_number": 1, "text": "First page text"},
        {"page_number": 2, "text": ""},
        {"page_number": 3, "text": "Third page text"},
    ]
