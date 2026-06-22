from fastapi import FastAPI

from app.routes.github import router as github_router

app = FastAPI(
    title="AI Resume GitHub Analyzer",
    version="1.0.0"
)

app.include_router(github_router)


@app.get("/")
def root():
    return {
        "message": "AI Resume GitHub Analyzer API"
    }


@app.get("/health")
def health():
    return {
        "status": "online"
    }