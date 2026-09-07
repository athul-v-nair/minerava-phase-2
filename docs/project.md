# Minerva — Project Brief

> **Status:** Pre-build | SDLC: `Spec → Tickets (Linear) → Build → /code-review → Push to GitHub`  
> **Repo:** `minerva-phase-2` (this repo) | **Date:** 2026-09-07

## 1. Vision

Minerva is a **VCS-agnostic PR/MR review agent** that posts an automated review comment with a **0–10 merge score**, a 2–3 sentence summary, and findings grouped by severity with `file:line` references.

*   Primary VCS for Phase 1: **Self-hosted GitLab** (Docker image provided).
*   Future VCS: **GitHub** (and any Git-based VCS) via a **VCS Adapter** plugin interface.
*   Local-first execution: Phase-1 review path uses **`opencode --serve`** (OpenAI-compatible, no cloud keys, no DB required).

## 2. Goals (MVP)

1.  Receive GitLab MR webhook (`MR opened`) and comment trigger (`@minerva`).
2.  Post **exactly one** review comment per `head_sha` (idempotent, never-loop).
3.  Call an **OpenAI-compatible** LLM endpoint (local `opencode --serve` now, real OpenAI/BYOK later) and derive a deterministic 0–10 score from findings.
4.  Provide a **React dashboard** to manage Organizations, Users, VCS connections, and Repo enablement — usable to manually test the backend from day one.
5.  Store secrets (PATs) **encrypted at rest** (`Fernet/AES-GCM`, key from `ENV`).

## 3. Non-Goals (MVP)

*   Auto-fixing code / pushing commits to the MR.
*   Auto-merge / blocking merge via GitLab approvals API (comment-only in MVP).
*   On-prem LLM hosting at scale, multi-model orchestration.
*   GitHub support (designed for, not built in Phase 1).

## 4. Personas & Roles

| Persona | Description | Permissions (MVP) |
|---|---|---|
| **Org Admin** | Creates org, invites members | Manage org, VCS connections, repo enablement, instruction pipelines, BYOK providers |
| **Org Member (User)** | Developer assigned to repos | Scoped to repos they are assigned to; can trigger `@minerva`, view review history for assigned repos |
| **Unassigned User** | User with no org | Personal workspace (default org auto-created) or standalone; limited to own VCS connections |

*Constraint: One user → at most one org (1:N, not M:N) for MVP.*

## 5. Core User Journeys

1.  **Onboard:** Admin registers (`email+password`) → creates Org → connects GitLab VCS (PAT encrypted) → syncs repo list → enables Minerva on selected repos → assigns users to repos.
2.  **Review:** Developer opens MR → Minerva posts review comment with score/summary/findings. Developer comments `@minerva` on same or updated MR → new review only if `head_sha` changed.
3.  **Inspect:** Any scoped user opens React dashboard → views Review history per repo/MR (score, trigger, model, comment URL, raw sanitized response).

## 6. Tech Stack (Locked)

| Layer | Choice | Notes |
|---|---|---|
| Backend | **Python + FastAPI** | OpenAPI auto-gen, async |
| Frontend | **React (Vite)** + `shadcn/ui` (per `docs/skills.md`) | `impeccable` + `anti-ui-slop` for design |
| DB | **SQLite + Alembic** | Migrations prepared for Postgres switch |
| LLM | **OpenAI-compatible client** → `opencode --serve` (Phase 1), BYOK later | `POST /v1/chat/completions` |
| VCS | Self-hosted **GitLab** (Docker) | Adapter pattern for GitHub later |
| Infra | `docker-compose` (`gitlab` + `api` + `web` + `sqlite` volume) | Local-first |

## 7. Repository Structure (Target)

```
/docs/               # project.md, architecture.md, spec.md, guardrails.md, agents.md
/specs/              # versioned slice specs (mirrors Linear tickets)
/api/                # FastAPI app
  app/
    core/            # config, security (encryption), llm_client
    vcs/             # adapter interface + gitlab/github impls
    models/          # SQLAlchemy models + Alembic
    routers/         # auth, orgs, vcs, repos, webhooks, reviews
    services/        # review_engine, scoring, webhook_handler
/web/                # React app
docker-compose.yml
alembic.ini
```

## 8. SDLC & Workflow

1.  **Specs** live in `docs/spec.md` + `specs/slice-*.md` (versioned, reviewable). **Tickets** live in **Linear** (each ticket links back to its spec slice).
2.  Build is **vertical slices** — each slice ships `DB migration + API + UI` so the frontend can manually verify the backend immediately. No `backend-first` then `frontend`.
3.  Every slice ends with **`/code-review` skill** before push. Push to GitHub only after review passes.
4.  Skills in use: `ponytail` (YAGNI, shortest diff), `impeccable`, `verification-before-completion`, `git-guardrails` (see `docs/skills.md`).

## 9. Constraints & Assumptions

*   **Local-first:** Nothing in the Phase-1 review hot path may require a cloud service or a DB. If DB/LLM is down, fail quietly (log, retry once, give up — no noisy comment).
*   **Encrypted secrets:** PATs never stored raw, never logged, never returned by API.
*   **Multi-tenancy:** SQLite file per environment; logical isolation via `org_id` FK + `repository_assignments` scoping.
*   **Idempotency:** `reviews(head_sha, repo_id)` unique constraint; duplicate webhook is a no-op.

## 10. Success Metrics (MVP)

*   MR opened → comment posted in < 60s (p95) on local `opencode` model.
*   `@minerva` re-trigger on same `head_sha` → 0 new comments (idempotent).
*   Minerva's own comment never triggers a loop (verified by integration test).
*   Score correlates with findings: 0 critical/warning → score ≥ 8 (unit-tested).
*   All PATs encrypted at rest (verified by DB inspection test).
*   Dashboard usable to enable a repo and view its review history without `curl`.

## 11. Open Questions (Resolved → Decisions)

*   Q: One user in many orgs? **A: No — one org max in MVP.**
*   Q: PAT at org or user level? **A: User level (encrypted). Org has many VCS via its users.**
*   Q: Login? **A: Email+password for MVP (OAuth later).**
*   Q: Score scale? **A: 0–10 integer, derived from findings.**
