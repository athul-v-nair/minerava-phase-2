# Minerva — Vertical Slice Spec

> **How to use:** Each slice is a *vertical* increment: `DB migration + API + UI` so the frontend can manually verify the backend immediately.  
> **Source of truth:** This file + `specs/slice-*.md` (when split). **Tickets:** Create Linear issues per slice and link back to the slice section.  
> **Skills:** `ponytail` (YAGNI), `impeccable`, `verification-before-completion`. Run `/code-review` at end of each slice before push.

## Slice 0 — Scaffolding & Local Runtime

**Goal:** `git clone → docker-compose up → open dashboard → see health` in < 5 min.

*   **DB:** Empty `data/minerva.db` (WAL, FKs on), `alembic` init, `alembic upgrade head` on api boot. No tables yet.
*   **API:** `FastAPI` app with `GET /health` → `{"status":"ok", "version": "..."}` + OpenAPI at `/docs` + CORS for `web`. `pytest` + `ruff` wired.
*   **Web:** Vite React skeleton, React Router, TanStack Query, `shadcn/ui` init, page `/health` that fetches `GET /health` and shows status. Empty states + skeleton.
*   **Infra:** `docker-compose.yml` (`api` + `web` + `gitlab` service stub), `.env.example`, `Makefile` (`make up/down/logs`), `.gitignore` (`data/`, `.venv/`).
*   **Docs:** `README.md` with setup steps, `opencode --serve` note.

**Acceptance:**

*   `docker-compose up` starts api+web+gitlab; `curl localhost:8000/health` → 200.
*   `http://localhost:5173/health` shows live api status (no mocks).
*   `pytest` + `ruff check` pass in CI stub.

**Tickets:** `MIN-0a` Alembic+SQLite, `MIN-0b` FastAPI health, `MIN-0c` Vite shell, `MIN-0d` docker-compose+docs.

---

## Slice 1 — Auth & Organizations

**Goal:** Register/login and see your org in the UI.

*   **DB:** `organizations(id, name UNIQUE, created_at)`, `users(id, email UNIQUE, password_hash, org_id FK nullable, role ENUM[org_admin,member], created_at)`. Alembic migration.
*   **API:**
    *   `POST /auth/register {email, password, orgName?}` → creates user + (if `orgName` given) org + membership as `org_admin`; else `org_id=NULL`.
    *   `POST /auth/login {email,password}` → `{access_token, refresh_token, user}` (JWT, HS256, 15m/7d).
    *   `GET /me`, `GET /orgs/me`, `PATCH /orgs/{id}` (admin only).
    *   Password: `bcrypt`, ≥12 chars, never logged.
*   **Web:**
    *   `/login`, `/register` (form + zod), auth guard, `GET /me` hydration, `/org` page showing org name + member list (read-only for now).
*   **Guardrail:** All subsequent routes require `Bearer` token; tests assert 401 without it.

**Acceptance:**

*   Register → login → `GET /me` returns org; UI shows org name.
*   Wrong password → 401 with no stack trace.
*   `users` row has `password_hash` not plaintext.

---

## Slice 2 — VCS Connections & Repo Enablement

**Goal:** Connect your self-hosted GitLab via PAT and enable repos for Minerva.

*   **DB:** `vcs_connections(id, user_id FK, provider ENUM[gitlab,github], base_url, encrypted_pat BLOB, display_name, is_active, created_at)`, `repositories(id, vcs_connection_id FK, external_id, name, url, is_enabled, last_synced_at, UNIQUE(vcs_connection_id, external_id))`, `repository_assignments(user_id, repository_id)` (composite PK). Crypto helper `api/app/core/crypto.py` (`Fernet`, key from `MINERVA_ENCRYPTION_KEY`).
*   **API:**
    *   `POST /vcs-connections {provider, base_url, pat, display_name}` → encrypts PAT, tests connection via adapter (`listRepos` probe), stores. `GET /vcs-connections`, `DELETE /vcs-connections/{id}`.
    *   `POST /vcs-connections/{id}/sync` → calls `VCSAdapter.listRepos()` → upserts `repositories`, sets `last_synced_at`.
    *   `GET /repositories?connectionId=`, `PATCH /repositories/{id} {is_enabled}`, `POST /repositories/{id}/assignments {user_ids}` (admin only), `GET /repositories/{id}`.
    *   `VCSAdapter` interface in `api/app/vcs/base.py` + `GitLabAdapter` impl (stubbed `listRepos`/`getMR`/`getDiff`/`postComment` via REST). `github` stub that raises `NotImplemented`.
*   **Web:**
    *   `/vcs` — list connections, `Add GitLab` dialog (base_url + PAT + Test button), sync status.
    *   `/repos` — table per connection, `Enable` toggle, `Assigned users` multi-select, `Sync` button, empty state.
*   **Security:** PAT never returned by API; `encrypted_pat` column is `BLOB`; integration test asserts DB value ≠ plaintext.

**Acceptance:**

*   Add GitLab PAT → row in `vcs_connections` is encrypted (inspect `data/minerva.db`).
*   `Sync` pulls real repo list from docker GitLab and shows in UI.
*   Toggling `Enable` persists and is reflected on reload.

---

## Slice 3 — Webhooks, Idempotency & Never-Loop

**Goal:** GitLab MR webhooks trigger the platform without loops or duplicates.

*   **DB:** `reviews(id PK, repository_id FK, mr_iid, mr_url, head_sha, trigger ENUM[mr_opened,mention], model, score nullable, summary nullable, findings JSON nullable, raw_response TEXT nullable sanitized, comment_url nullable, status ENUM[pending,posted,failed], created_at, UNIQUE(repository_id, head_sha))`.
*   **API:**
    *   `POST /webhooks/gitlab` — verify `X-Gitlab-Token == GITLAB_WEBHOOK_TOKEN` (timing-safe), parse `object_kind == merge_request` (action `open`/`update`) and `note` (comment) with `@minerva`. Drop if `user.username == BOT_USERNAME`. Lookup `repository_id` via `vcs_connection.base_url + project.path`. Idempotency: `SELECT reviews WHERE repository_id+head_sha` → if exists → `200 {status:"already_reviewed"}` (no LLM call). Else insert `reviews(status=pending)` and return 200. **No LLM yet.**
    *   `GET /reviews?repositoryId=&mrIid=` (scoped to assigned repos).
*   **Web:** `/reviews` — table showing webhook receipts (pending rows), filter by repo, detail drawer with `head_sha`, `trigger`, `status`. Manual `curl` webhook test documented in `README`.
*   **Tests:** Unit: idempotency (same `head_sha` twice → second is no-op). Integration: bot comment ignored. E2e: `curl` webhook → row in `reviews` + appears in UI.

**Acceptance:**

*   `curl` MR-opened webhook → `reviews` row `pending` + visible in `/reviews`.
*   Replaying same `head_sha` → `already_reviewed`, no duplicate row.
*   Comment authored by `BOT_USERNAME` → ignored (no row, no LLM call).

---

## Slice 4 — Review Engine (OpenAI-compatible → opencode --serve)

**Goal:** Turn a pending review into a scored comment on the MR.

*   **API:**
    *   `LLMClient` (`api/app/core/llm_client.py`) wrapping `OpenAI(base_url=LLM_BASE_URL, api_key=dummy)`. Config: `LLM_BASE_URL`, `LLM_MODEL`, `LLM_TIMEOUT=30s`, retry once.
    *   `ReviewEngine` (`api/app/services/review_engine.py`): builds prompt (`prompts/review_v1.txt` + diff from `VCSAdapter.getDiff`), calls LLM, expects strict JSON `{summary, findings:[{severity,file,line,message,suggestion}]}`, validates via `pydantic`, derives score via `scoring.py` (`critical -4, warning -2, info -0.5`, floor 0, enforced `no critical/warning → ≥8`), formats comment: `## Minerva Review — Score: X/10\n\nSummary\n\n### Critical (n)\n- file:line — message\n...`.
    *   Background task (FastAPI `BackgroundTasks` or inline for MVP): on webhook insert, fetch diff → call LLM → `postComment` via adapter → update `reviews(status=posted, score, summary, findings, raw_response_sanitized, comment_url)`. On timeout/5xx: retry once, then `status=failed`, **no comment**, log only (fail-quietly). Audit: store `model`, `raw_response` sanitized (strip PATs), `comment_url`.
    *   `POST /reviews/{id}/retry` (admin, for failed reviews).
*   **Web:** `/reviews` detail now shows score badge (color by 0-3 red, 4-6 amber, 7-10 green), summary, grouped findings with `file:line`, `comment_url` link, `raw_response` collapsed. `/reviews` list shows score column.
*   **Prompt:** Versioned `review_v1.txt`; instructs `Return ONLY JSON, no markdown`. Parser tolerates ```json fences.

**Acceptance:**

*   Open MR in docker GitLab → webhook → within 60s a comment appears on the MR with `Score: X/10` + grouped findings.
*   MR with zero critical/warning → score ≥8 (automated test).
*   LLM timeout → no comment, `reviews.status=failed`, log line, retry once only.
*   Raw diff with injected PAT is sanitized before persisting.

---

## Slice 5 — Polish, Org Scoping & BYOK Prep

**Goal:** Harden multi-tenancy and prepare for hosting.

*   **DB/API:**
    *   Tenant isolation: every `GET /repositories`, `GET /reviews`, webhook lookup filtered by `user.org_id` or `repository_assignments`; tests assert cross-org 404.
    *   Org admin flows: invite member (`POST /orgs/{id}/members {email, role}`), assign repos to users (already in Slice 2, now scoped).
    *   Instruction pipelines stub: `review_pipelines(id, org_id, name, prompt_template)` (admin CRUD, not yet wired to engine — selected via `REVIEW_PIPELINE_ID` env).
    *   BYOK providers stub: `llm_providers(id, org_id, name, base_url_encrypted, api_key_encrypted)` (admin CRUD, encrypted, not yet selected — engine still uses global `LLM_BASE_URL`).
*   **Web:**
    *   Role-aware UI: non-admin sees disabled `Enable`/`Assign` controls.
    *   `/org` — member table with role badges, invite dialog.
    *   `/reviews` — org-scoped filters, audit trail drawer.
    *   Empty states, skeletons, error toasts everywhere (`impeccable` pass).
*   **Infra:** `Alembic` migration for new tables, `GET /health` now reports `db ok, llm reachable` (best-effort).
*   **Docs:** `guardrails.md` checks enforced by tests (idempotency, never-loop, score derivation).

**Acceptance:**

*   User A (org 1) cannot `GET /reviews` for org 2's repo → 404.
*   Non-admin cannot `PATCH /repositories/{id}` → 403.
*   Admin can CRUD `review_pipelines` and `llm_providers` (stored encrypted, visible in UI).

---

## Slice 6 — Hardening & Release

*   Rate/cost caps (per-repo debounce, max reviews per hour), prompt-injection defenses (diff is data, not instruction), comprehensive e2e (GitLab MR → comment → dashboard), `ruff`/`pytest` green, `/code-review` on own PR, tag `v0.1.0`.

## Ticketing Rule

*   One Linear ticket per bullet under a slice, title = `[Slice N] <area>: <action>`, description = slice acceptance + link to this file's section. Labels: `slice-0..6`, `backend/frontend/infra`.
