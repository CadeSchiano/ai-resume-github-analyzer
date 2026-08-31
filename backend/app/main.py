from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import MAX_RESUME_REQUEST_SIZE_BYTES
from app.routes.github import router as github_router
from app.routes.analysis import router as analysis_router
from app.routes.resume import router as resume_router

app = FastAPI(
    title="AI Resume GitHub Analyzer",
    version="1.0.0"
)

app.include_router(github_router)
app.include_router(analysis_router)
app.include_router(resume_router)


@app.middleware("http")
async def add_security_headers_and_limit_upload_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if request.method == "POST" and request.url.path.startswith(("/resume", "/analysis")):
        if content_length:
            try:
                request_size = int(content_length)
            except ValueError:
                return JSONResponse(status_code=400, content={"detail": "Invalid Content-Length header."})
            if request_size > MAX_RESUME_REQUEST_SIZE_BYTES:
                return JSONResponse(status_code=413, content={"detail": "Resume upload is too large."})

    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    if request.url.path.startswith(("/resume", "/analysis")):
        response.headers["Cache-Control"] = "no-store"
    return response

@app.get("/")
def root():
    return {"message": "AI Resume GitHub Analyzer API"}

@app.get("/health")
def health():
    return {"status": "online"}
