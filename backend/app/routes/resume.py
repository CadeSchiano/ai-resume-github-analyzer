from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.security import enforce_request_rate_limit
from app.services.resume_report_service import generate_resume_report
from app.services.resume_service import extract_resume_text, validate_resume_pdf


router = APIRouter(
    prefix="/resume",
    tags=["Resume"],
    dependencies=[Depends(enforce_request_rate_limit)],
)


async def _extract_uploaded_resume_text(resume: UploadFile) -> str:
    pdf_bytes = await resume.read()
    try:
        validate_resume_pdf(pdf_bytes)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

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
