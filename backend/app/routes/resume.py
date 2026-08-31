from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.resume_service import extract_resume_text


router = APIRouter(
    prefix="/resume",
    tags=["Resume"],
)


@router.post("/extract")
async def extract_resume(resume: UploadFile = File(...)):
    """Extract text from a PDF resume. The file is processed in memory only."""
    pdf_bytes = await resume.read()
    if not pdf_bytes.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="Upload a valid PDF resume.")

    try:
        text = extract_resume_text(pdf_bytes)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {"text": text}
