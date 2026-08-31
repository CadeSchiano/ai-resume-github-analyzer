from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.resume_report_service import generate_resume_report
from app.services.resume_service import extract_resume_text


router = APIRouter(
    prefix="/resume",
    tags=["Resume"],
)


async def _extract_uploaded_resume_text(resume: UploadFile) -> str:
    pdf_bytes = await resume.read()
    if not pdf_bytes.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="Upload a valid PDF resume.")

    try:
        return extract_resume_text(pdf_bytes)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/extract")
async def extract_resume(resume: UploadFile = File(...)):
    """Extract text from a PDF resume. The file is processed in memory only."""
    text = await _extract_uploaded_resume_text(resume)

    return {"text": text}


@router.post("/analyze")
async def analyze_resume(resume: UploadFile = File(...)):
    """Analyze a PDF resume with deterministic parsing and scoring."""
    text = await _extract_uploaded_resume_text(resume)

    return generate_resume_report(text)
