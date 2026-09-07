# Minerva — PR Review Agent

VCS-agnostic PR/MR review agent. Phase 1: self-hosted **GitLab** → posts `Score: X/10` + summary + `critical/warning/info` findings with `file:line`.

Stack: `FastAPI + React (Vite + shadcn) + SQLite + Alembic + opencode --serve`

## Quick Start (< 5 min)

```bash
cp .env.example .env
# edit .env: set MINERVA_ENCRYPTION_KEY, JWT_SECRET, GITLAB_WEBHOOK_TOKEN
# generate key: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

docker-compose up --build
# api: http://localhost:8000/health  -> {"status":"ok"}
# api docs: http://localhost:8000/docs
# web: http://localhost:5173/health
# gitlab: http://localhost:8929
```

Local dev without Docker:

```bash
cd api && pip install -r requirements.txt && alembic upgrade head && uvicorn app.main:app --reload
cd web && npm install && npm run dev
```

## opencode --serve (Phase-1 LLM)

Phase-1 review path uses a local OpenAI-compatible endpoint. No cloud key required.

```bash
opencode --serve --port 4000
# set LLM_BASE_URL=http://localhost:4000/v1 in .env
# or http://opencode:4000/v1 inside docker-compose
```

## Health

```bash
curl localhost:8000/health
# {"status":"ok","version":"0.1.0"}
```

Web health page at `http://localhost:5173/health` fetches live API status (no mocks).

## Testing

```bash
cd api && pytest -q
ruff check api
```

## Project Structure

```
/docs/        spec, architecture, guardrails
/api/         FastAPI app (app/main.py), Alembic, SQLite
/web/         React + Vite + shadcn/ui
data/         minerva.db (WAL, FKs on) — gitignored
```

## Guardrails

- One review per `(repository_id, head_sha)` — duplicate = `already_reviewed`
- Never-loop: ignore `BOT_USERNAME` webhooks
- Score derived: `critical -4, warning -2, info -0.5`, floor 0, `0 findings → ≥8`
- PATs encrypted with `Fernet` (`MINERVA_ENCRYPTION_KEY` from ENV)
- Diff = data (prompt-injection hardening) — not in Slice 0 yet
