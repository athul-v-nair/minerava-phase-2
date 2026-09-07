# Minerva — Interactive Diagrams

These are **standalone HTML** files generated with `archify` (`tt-a1i/archify`). Open them directly in a browser — no server needed. They support pan/zoom, theme switch, focus, and export.

*   `minerva-architecture.html` — System architecture (`docs/diagrams/minerva-architecture.json` → validated `showcase`, 0 errors, 9/9 checks). Views: `Review hot path` / `Control path` / `Security`.
*   `minerva-review-sequence.html` — MR review sequence (`docs/diagrams/minerva-review-sequence.json` → validated `showcase`, 0 errors, 9/9 checks). Views: `Trigger + guard` / `Fetch & reason` / `Post & audit`.

Regenerate:

```bash
node "C:\Users\Gokul\.agents\skills\archify\bin\archify.mjs" validate architecture docs/diagrams/minerva-architecture.json --quality showcase --json
node "C:\Users\Gokul\.agents\skills\archify\bin\archify.mjs" deliver architecture docs/diagrams/minerva-architecture.json docs/diagrams/minerva-architecture.html --quality showcase --json

node "C:\Users\Gokul\.agents\skills\archify\bin\archify.mjs" validate sequence docs/diagrams/minerva-review-sequence.json --quality showcase --json
node "C:\Users\Gokul\.agents\skills\archify\bin\archify.mjs" deliver sequence docs/diagrams/minerva-review-sequence.json docs/diagrams/minerva-review-sequence.html --quality showcase --json
```
