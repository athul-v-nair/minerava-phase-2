# Skills for developing Minerva

Install and use these agent skills while working on this project. All installs
via `npx skills add <owner/repo>` (skills.sh) — or follow the repo's own README.

## In use in this repo

| Skill | Why | Install |
|---|---|---|
| **ponytail** (dietrichgebert/ponytail) | Lazy/YAGNI-first engineering: stdlib before deps, shortest diff, delete before add. Already wired as an opencode plugin in `opencode.json`. Levels: `lite` / `full` (default) / `ultra`. | `npx skills add dietrichgebert/ponytail` (or plugin: `"plugin": ["@dietrichgebert/ponytail"]`) |
| **impeccable** (pbakaus/impeccable) | Production-grade frontend design: craft floor, contrast verification, responsive checks, anti-pattern bans. Use for every UI task in `web/`. | `npx skills add https://github.com/pbakaus/impeccable --skill impeccable` |

## Recommended for this project

### UI/UX
- **frontend-design** (anthropics/skills) — high-quality UI design reference
  (798K installs). → https://www.skills.sh/anthropics/skills/frontend-design
- **web-design-guidelines** (vercel-labs/agent-skills) — design system rules for
  product UIs. → https://www.skills.sh/vercel-labs/agent-skills/web-design-guidelines
- **design-an-interface** (mattpocock/skills) — interface design workflow.
  → https://www.skills.sh/mattpocock/skills/design-an-interface
- **shadcn** (shadcn/ui) — accessible component library setup for the dashboard.
  → https://www.skills.sh/shadcn/ui/shadcn
- **anti-ui-slop** (uizze.com) — stops generic LLM-looking UI. → https://www.skills.sh/site/uizze.com/anti-ui-slop
- **ui-ux-pro-max** (nextlevelbuilder) — full UI/UX pipeline. → https://www.skills.sh/nextlevelbuilder/ui-ux-pro-max-skill/ui-ux-pro-max

### Token efficiency / lazy code
- **caveman-compress** (juliusbrussee/caveman) — token compression skill.
  → https://www.skills.sh/juliusbrussee/caveman/caveman-compress
- Matt Pocock's skill set (aihero.dev) shipped a **63% token reduction** in
  v1.0 — worth installing whole: `npx skills add mattpocock/skills`
  → https://www.aihero.dev/skills
  - **/grill-with-docs** — grill the docs/spec against the codebase; use before
    and after implementing each phase → https://www.aihero.dev/grill-with-docs
  - **/to-spec** — turn a conversation into a spec (used for `docs/SPEC.md`)
   - **/to-tickets** — convert a spec document into actionable Linear tickets with titles, descriptions, and acceptance criteria. Use after `/to-spec` to break down features into trackable work items.
  - **/tdd** — test-driven development workflow
  - **/triage** — backlog triage for ROADMAP items
  - **/wayfinder** — planning before big refactors
   - **/archify** — Turn a codebase or system description into a polished, interactive system map. Use for architecture diagrams, component flow visualizations, and system overviews. Produces clean, clickable, user-friendly diagrams that are easier to understand than static images. Install: `npx skills add tt-a1i/archify -g`

### Code review (meta — Minerva is a reviewer)
- **code-review** (mattpocock/skills) — a code review skill; useful for reviewing
  Minerva's own PRs. → https://www.skills.sh/mattpocock/skills/code-review
- **requesting-code-review** / **receiving-code-review** (obra/superpowers) —
  review workflows. → https://www.skills.sh/obra/superpowers
- **grill-me** (mattpocock/skills) — adversarial review of your own design
  decisions before writing code (917K installs).

### Process
- **writing-plans** + **executing-plans** (obra/superpowers) — plan-driven
  execution for multi-phase work.
- **verification-before-completion** (obra/superpowers) — never claim done
  before verification (run pytest + ruff).
- **test-driven-development** (obra/superpowers) — TDD loop for the agent.
- **improve-codebase-architecture** (mattpocock/skills) — periodic architecture
  audit.

### Git
- **/git-guardrails-claude-code** — sets up a PreToolUse hook that intercepts and blocks dangerous git commands (force-push, destructive resets, risky branch ops) before execution. Use for every git workflow to prevent accidental data loss. Install:
  `npx skills add https://github.com/mattpocock/skills --skill git-guardrails-claude-code`
- **/git-commit** — writes standardized git commits following the Conventional Commits spec, with intelligent diff analysis that generates accurate, scoped messages automatically. Use whenever committing code to keep history clean and readable. Install:
  `npx skills add https://github.com/github/awesome-copilot --skill git-commit`

## Suggested phase mapping

| Phase | Skills |
|---|---|
| 1 (agent) | ponytail, /tdd, /grill-with-docs, verification-before-completion, /to-tickets, /archify, /git-guardrails-claude-code, /git-commit |
| 2 (web app) | impeccable, frontend-design, web-design-guidelines, shadcn, anti-ui-slop, /to-tickets, /archify, /git-guardrails-claude-code, /git-commit |
| 3 (CI/CD) | code-review, grill-me, improve-codebase-architecture, /git-guardrails-claude-code, /git-commit |
| 4–5 (hardening) | systematic-debugging (obra), /grill-me, caveman-compress |