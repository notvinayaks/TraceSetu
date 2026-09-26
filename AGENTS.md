# TraceSetu prototype contributor instructions

Read README.md, docs/status.md and the relevant contract documentation before modifying the app. This repository contains the functioning SIH MVP; full production expansion is deferred unless explicitly requested.

- Preserve the evidence distinction between observed transfers, provider assertions, reviewed labels, hypotheses, synthetic fixtures and missing coverage.
- Live mode must never silently use synthetic data. Unknown does not mean low risk or self-custody.
- Stop each branch at its first evidenced custodian. Never link an exchange deposit to an unrelated withdrawal through an assumed private ledger.
- Keep exact amounts, chronological ordering, source hashes, immutable parent evidence and explicit partial coverage.
- Do not invent VASP ownership, confidence percentages, successful API calls, SAHYOG connectivity, notices or freezes.
- Keep independent review, tenant/case permissions and payload binding. Sending external requests requires explicit user authorisation; the current application exports only.
- Never commit .env files, credentials, signing keys, case databases, provider responses, generated evidence or submission media.
- Preserve ATLAS_ settings and atlas.* schema identifiers for evidence compatibility unless a migration is explicitly designed.
- Verify backend changes with pytest and Ruff; verify interface changes with the TypeScript/Vite build and relevant browser checks. Record exact test scope and unverified dependencies in docs/status.md or docs/RELEASE_VERIFICATION.md.
- Do not claim measured superiority, government endorsement, production readiness or full problem-statement compliance without evidence.
