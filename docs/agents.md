# Minerva — Agent Instructions

> **Ingestion file.** Read this first. Keep context small — follow pointers, don't inline.

## What
VCS-agnostic PR review agent. Self-hosted GitLab (Phase 1) → adapter for GitHub later. Posts `Score: X/10` + summary + `critical/warning/info` with `file:line`.

## Stack
`FastAPI` + `React (Vite + shadcn)` + `SQLite + Alembic` + `opencode --serve` (OpenAI compat). `docker-compose` = `gitlab + api + web`.

## Where to look
*   `docs/project.md:1` — goals, roles (org_admin vs member), journeys
*   `docs/architecture.md:1` — components, ERD, flows, VCS Adapter, encryption
*   `docs/spec.md:1` — 7 vertical slices (DB+API+UI per slice) + tickets
*   `docs/guardrails.md:0` — plain-English + S5 prompt-injection hardening (diff=data)
*   `docs/diagrams/minerva-architecture.html:1` + `minerva-review-sequence.html:1` — interactive maps
*   `docs/skills.md:1` — skills (`ponytail`, `impeccable`, `archify`)
*   `specs/slice-*.md` — versioned slice specs (when split from `spec.md`)

## How to build
1.  Pick next slice from `docs/spec.md:1` (vertical: `migration + API + UI + test`).
2.  Create Linear ticket per bullet → link to slice.
3.  Implement shortest diff (ponytail: stdlib before deps, delete before add).
4.  `pytest` + `ruff check` must be green. Run `/code-review` on own PR. Push to GitHub only after review passes.

## Guardrails (never violate)
*   **G1 Idempotent** per `(repo, head_sha)` → duplicate = `already_reviewed`
*   **G2 Never-loop** → ignore `BOT_USERNAME` webhooks
*   **G3 Score derived** `critical -4, warning -2, info -0.5`, `0 findings → ≥8`
*   **G5 Fail-quietly** → LLM timeout retry once → `status=failed`, no PR spam
*   **S1 PATs encrypted** (`Fernet`, `MINERVA_ENCRYPTION_KEY` from ENV, never returned/logged)
*   **S5 Diff = data** → `SYSTEM > pipeline instructions > diff` in ```diff fence, schema-validated JSON, score recomputed server-side
*   **G7 Local-first** → no cloud/API key in Phase-1 hot path (`grep OPENAI_API_KEY` = 0)

## Auth
`POST /auth/register|login` → `bcrypt` + `JWT access 15m + refresh 7d (jti)` → `Bearer` on all routes. `docs/architecture.md:6`.

## Instructions tab
Org_admin CRUD at `/instructions`, per-repo override. See `docs/architecture.md:5` + `docs/guardrails.md:2 S5.1`.

## Commands
```bash
docker-compose up          # api :8000 /health, web :5173, gitlab :8929
alembic upgrade head && pytest && ruff check
node bin/archify.mjs validate <type> docs/diagrams/*.json --quality showcase
```

## Don't
*   No `backend-only` slice. No direct `CREATE TABLE` — use Alembic.
*   No `OPENAI_API_KEY` in Phase-1 review path.
*   Don't start slice N+1 until slice N is reviewed & merged.
