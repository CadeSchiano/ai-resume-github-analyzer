from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.developer_report_service import generate_developer_report
from app.services.report_service import generate_report
from app.services.resume_service import extract_resume_text

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)


@router.get("/{username}")
def analyze(username: str):

    report = generate_report(username)

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="GitHub user not found"
        )

    return report


@router.post("/{username}/resume")
async def analyze_developer(
    username: str,
    resume: UploadFile = File(...),
    target_role: str | None = Form(None),
):
    """Analyze one PDF resume with the user's public GitHub evidence."""
    pdf_bytes = await resume.read()
    if not pdf_bytes.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="Upload a valid PDF resume.")

    try:
        resume_text = extract_resume_text(pdf_bytes)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    try:
        report = generate_developer_report(username, resume_text, target_role)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if report is None:
        raise HTTPException(status_code=404, detail="GitHub user not found")

    return report
