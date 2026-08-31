# Northstar: Developer Readiness Analyzer

Northstar turns a PDF resume and a public GitHub profile into a practical, evidence-based readiness review for early-career developers.

It does not use AI to score people. GitHub, resume, cross-evidence, and role-readiness scores are deterministic and based only on the visible evidence collected by the application. An optional AI explanation can summarize those results without changing them.

## What it analyzes

- Public GitHub repositories: source-code presence, documentation, tests, CI, technology signals, project presentation, and activity.
- PDF resumes: explicit skills, experience, projects, and concrete outcomes.
- Resume × GitHub evidence: whether a resume skill has visible support in an original public repository.
- Target-role readiness for intern, software engineering, frontend, backend, full-stack, mobile, and AI/ML paths.

Only public repositories are analyzed. Private repositories, GitHub profile data beyond the public API response, and uploaded resumes are not stored.

## Interface

The Next.js frontend collects a GitHub username, PDF resume, target role, and an optional request for an AI explanation. It presents scores separately from the supporting evidence so a missing signal is never represented as a low score.

## Stack

| Area | Technology |
| --- | --- |
| API | FastAPI, Python |
| Resume extraction | pypdf |
| GitHub evidence | GitHub REST API |
| Frontend | Next.js, React, TypeScript |
| Optional explanation | OpenAI Responses API |

## Run locally

### 1. Start the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`.

### 2. Start the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## Optional configuration

Create `backend/.env` locally. It is ignored by Git and must never be committed.

```env
# Optional but recommended for repeated GitHub analyses.
GITHUB_TOKEN=github_pat_...

# Required only when the “Add an AI explanation” option is selected.
OPENAI_API_KEY=sk-...

# Optional overrides
OPENAI_MODEL=gpt-5-mini
FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

`GITHUB_TOKEN` is not required to analyze public repositories. Without it, GitHub applies its public API rate limit. Northstar limits a single analysis to the eight most recently updated public repositories and briefly caches successful public API responses to make repeat checks reliable. If GitHub still rate-limits a request, the API returns a clear temporary error instead of showing empty GitHub scores.

## API

| Endpoint | Purpose |
| --- | --- |
| `GET /analysis/{username}` | Deterministic GitHub-only report |
| `POST /resume/extract` | Extract text from a PDF resume |
| `POST /resume/analyze` | Deterministic resume report |
| `POST /analysis/{username}/resume` | Combined resume, GitHub, cross-evidence, and role report |

The combined endpoint accepts multipart form fields:

- `resume`: required PDF file, maximum 5 MB
- `target_role`: optional supported role
- `include_ai_explanation`: optional `true`/`false`, default `false`

## Security and privacy

- Resume uploads are validated as PDFs, size-limited, processed in memory, and returned with `Cache-Control: no-store`.
- The API rate-limits analysis and resume routes per client IP.
- CORS is restricted to the configured local frontend origins; it never uses a wildcard origin.
- OpenAI requests are opt-in, send only the completed report, and use `store=False`.
- Environment files, frontend build output, and dependencies are ignored by Git.

## Verification

```bash
cd backend
python3 -m pytest -q

cd ../frontend
npm run build
npm audit --audit-level=high
```

## Current scope

This is intentionally a local, stateless analyzer. It has no accounts, database, background workers, private-repository access, or persistent resume storage.
