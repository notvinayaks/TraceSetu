# Product foundation verification — 26 September 2026

Product branch: `product/live-foundation`. Main still preserves the published MVP. Code milestone: `384ae2ba4bd9929871b5dc6891a852f3ef285d3b`.

## Implemented and verified

- Versioned Alembic schema, frozen original baseline, explicit legacy adoption, schema-mismatch rejection and preservation of case records. Original evidence tables cannot be downgraded away.
- Serialised schema upgrades on SQLite and PostgreSQL; controlled rollback/reapply of the worker-heartbeat revision.
- Separate worker command, persistent process heartbeat, stale-worker readiness and PostgreSQL `SKIP LOCKED` claims. Twelve concurrent claims returned twelve distinct jobs in the PostgreSQL check.
- Tenant-restricted administrator operational status; public readiness returns only a ready/not-ready result. The UI uses the existing restrained table/panel design.
- Generated request IDs and allowlisted structured operational events with route templates; SQL parameter rendering disabled. External proxy/runtime logs still need deployment governance.
- A bounded live-validation runner that uses authenticated case/job APIs, retains failures/raw responses/signed bundles, matches exact supplied transfer references and verifies replay. Synthetic/imported modes are refused. Empty responses and missing access are distinct from verified transfer samples.

## Test evidence

| Environment/check | Result |
|---|---|
| Local Windows / SQLite full suite | 128 passed, 2 PostgreSQL-only tests skipped; one upstream test-client deprecation warning. |
| GitHub Ubuntu / SQLite | 128 passed, 2 skipped; Ruff passed. |
| GitHub Ubuntu / PostgreSQL 16 full suite | 130 passed, including tenant/case permission regressions, migration preservation/rollback and concurrent claims. |
| Frontend | TypeScript/Vite passed locally and in CI. |
| Browser | Main training/challenge/bundle/replay/mobile workflow passed. New admin health panel/refresh passed on desktop and mobile. Zero page errors/overflow; desktop screenshot visually inspected. |
| Separate API and worker | Main browser workflow passed with the API's embedded worker disabled and a standalone worker sharing the isolated database. Zero page errors/mobile overflow. |
| Dependency consistency | `pip check` passed. |
| Publication | Source-only audited branch; no private data/credentials or submission media. |

Verified CI: https://github.com/notvinayaks/TraceSetu/actions/runs/36225606185. Local tests/screenshots are retained under ignored `tmp/`; they are not private data published to GitHub.

## Actual public-data check

The public Esplora endpoint timed out during sample selection. It was not silently replaced or described as successful. A separate test explicitly selected BlockCypher and the public historical address `13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94`, with the time window 3 August 2017 UTC, one hop and six configured requests. The separately fetched reference response contained two transactions and three outputs. The application acquired the real data, matched all three exact output references, and verified its signed evidence bundle and deterministic replay. No receiving VASP identity was established.

The selection and application responses came from the same provider. This verifies transport, parsing, amount consistency and evidence replay; it is not independent consensus or attribution ground truth. Full-chain, ownership and independent-ground-truth validation stay false in the manifest. The completed private manifest is `.local/product-live-validation-002/manifest.json`; the original response is `tmp/product-blockcypher-selection.json`. Neither is committed to GitHub.

The access-result extension was exercised through the real application for the other five chains. Ethereum, BNB Chain and Polygon reported `unavailable` / `not_configured` with zero attempted provider calls because Etherscan credentials are absent. Separate public Tron and Solana access probes each retained one successful response under a one-request cap and reported `live_no_transfers`; their chosen burn/system-program addresses were neutral access probes, not suspected wallets or transfer-validation examples. Manifests: `.local/product-live-access-001/manifest.json` and `.local/product-public-access-001/manifest.json`. These outcomes verify that the runner records positive, empty and unavailable states without inventing operational coverage.

## Remaining scope

The user asked to wind down, publish the current foundation and stop on 26 September 2026. Further full-product work is paused pending a new request; the MVP remains on `main`, and foundation changes remain on `product/live-foundation`.

Docker Desktop's engine could not be started here; PostgreSQL checks instead ran against an isolated CI service. A local container/TLS deployment, backup/restore drills, agency SSO/MFA, production key and storage governance, external retained audit, shared provider quotas/fairness, broad public/live-chain coverage, independent evaluation and official SAHYOG connectivity remain open. Passing these engineering tests is not full-product completion or production acceptance.
