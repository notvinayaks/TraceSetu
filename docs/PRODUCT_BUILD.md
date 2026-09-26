# TraceSetu full product build

Resumed 26 September 2026 at the user's explicit request. Available data access: public/free APIs only. The existing working MVP remains the baseline, not the definition of product completion.

## Work order and acceptance

1. **Operational foundation (B08/B12/G06/G07/G10).** Versioned schema upgrades, separate workers, redacted operational logs, liveness/readiness, database/worker checks, backups and recovery. Validate against disposable SQLite/PostgreSQL installations; never migrate an existing investigation database without a backup.
2. **Live evidence pipeline (D09–D15).** Actual provider requests, per-chain validation manifests, response integrity, public endpoint support, chronology and canonicality limits, recoverable pagination and shared request accounting. A successful status probe is not a successful wallet trace.
3. **Attribution and the USP (C11–C15/F10/F13).** Source-backed reviewed identity inputs, explainable typology signals, reversible hypotheses, independent evaluation and measured query-planner comparisons. No calibrated score without independent labels.
4. **Operational case workflow (B09–B11/F11–F14/G08).** Identity and retention boundaries, signing-key lifecycle, reviewed dispatch interface/simulator, governed correction propagation, alert acknowledgement and storage operations. Official dispatch remains disabled until the authorised contract and real credentials are supplied.
5. **Release acceptance (G09/G11–G13/X01–X12).** Linux/container/DB tests, failure and load exercises, accessibility, operator documentation, measured performance and independently accepted deployment/integration. External gates remain open until verified.

The authoritative task ledger remains `IMPLEMENTATION_CHECKLIST.md`. Its tasks are unweighted, not a readiness percentage. Each sizeable task may have verified substeps without its parent being complete. The current prototype has 116 passing backend tests and successful local/browser/GitHub CI evidence; those checks do not establish the remaining production properties.

The five differentiators remain first custody per path, an inspectable nearestness certificate, source-family challenge, budget-aware evidence acquisition and provenance-preserving reviewed service feedback. All product extensions must preserve exact values, original evidence, reproducible decisions, permission boundaries and explicit uncertainty.

## Technical references checked for this phase

- [Alembic migration tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [PostgreSQL locking](https://www.postgresql.org/docs/current/explicit-locking.html)
- [SQLAlchemy connection-pool recovery](https://docs.sqlalchemy.org/en/20/core/pooling.html#disconnect-handling-pessimistic)
- [Compose service readiness dependencies](https://docs.docker.com/compose/how-tos/startup-order/)

These inform implementation; they are not evidence of a successful TraceSetu deployment.
