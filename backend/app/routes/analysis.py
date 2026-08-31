from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.security import enforce_request_rate_limit
from app.services.ai_explanation_service import generate_ai_explanation
from app.services.developer_report_service import generate_developer_report
from app.services.report_service import generate_report
from app.services.resume_service import extract_resume_text, validate_resume_pdf

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
    dependencies=[Depends(enforce_request_rate_limit)],
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
    include_ai_explanation: bool = Form(False),
):
    """Analyze one PDF resume with the user's public GitHub evidence."""
    pdf_bytes = await resume.read()
    try:
        validate_resume_pdf(pdf_bytes)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

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

    if include_ai_explanation:
        try:
            report["ai_explanation"] = generate_ai_explanation(report)
        except ValueError as error:
            raise HTTPException(status_code=503, detail=str(error)) from error

    return report
