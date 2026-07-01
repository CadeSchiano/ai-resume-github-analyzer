from fastapi import APIRouter, HTTPException

from app.services.report_service import generate_report

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