"""PDF resume text extraction for Phase 2."""

from io import BytesIO

from pypdf import PdfReader


def extract_resume_text(pdf_bytes: bytes) -> str:
    """Extract selectable text from a PDF resume without storing the file."""
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
    except Exception as error:
        raise ValueError("The uploaded file could not be read as a PDF.") from error

    if reader.is_encrypted:
        raise ValueError("Encrypted PDF resumes are not supported.")

    text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    if not text:
        raise ValueError("No selectable text was found in this PDF resume.")

    return text
