# TraceSetu prototype contributor instructions

Read README.md, docs/status.md, skills/custody-atlas-sih/SKILL.md and the relevant contract documentation before modifying the app. On 30 September 2026 the user authorised publishing completed TraceSetu work, including research and selected project deliverables. The full-product build remains paused after the 26 September wind-down. Preserve the verified MVP on main and the foundation/research on product/live-foundation. Public/free APIs only. Operational capabilities require measured evidence; external access/acceptance gates must remain explicit.

- Preserve the evidence distinction between observed transfers, provider assertions, reviewed labels, hypotheses, synthetic fixtures and missing coverage.
- Live mode must never silently use synthetic data. Unknown does not mean low risk or self-custody.
- Stop each branch at its first evidenced custodian. Never link an exchange deposit to an unrelated withdrawal through an assumed private ledger.
- Keep exact amounts, chronological ordering, source hashes, immutable parent evidence and explicit partial coverage.
- Do not invent VASP ownership, confidence percentages, successful API calls, SAHYOG connectivity, notices or freezes.
- Keep independent review, tenant/case permissions and payload binding. Sending external requests requires explicit user authorisation; the current application exports only.
- Never commit .env files, credentials, signing keys, case databases, provider responses, private generated evidence, recordings or standalone narration. The explicitly allowlisted project PPT/PDF/Word deliverables and self-contained handover are authorised; do not broadly unignore output directories.
- The 64-test deposit-inference reference is separate from the app, synthetic and not independently evaluated for accuracy. Keep its heuristic outcomes distinct from ownership proof. Preserve chronological arrival states and evidence-snapshot binding.
- Maintain IMPLEMENTATION_CHECKLIST.md after verified milestones; run scripts/update_checklist.py. Counts are unweighted tasks, not readiness percentages.
- Preserve ATLAS_ settings and atlas.* schema identifiers for evidence compatibility unless a migration is explicitly designed.
- Verify backend changes with pytest and Ruff; verify interface changes with the TypeScript/Vite build and relevant browser checks. Record exact test scope and unverified dependencies in docs/status.md or docs/RELEASE_VERIFICATION.md.
- Do not claim measured superiority, government endorsement, production readiness or full problem-statement compliance without evidence.
