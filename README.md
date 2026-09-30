# TraceSetu

**Latest project package — 30 September 2026:** `product/live-foundation` contains the verified application foundation plus the completed research, reference experiment, guides and SIH deliverables. The published MVP remains on `main`. Full-product development is paused; publication does not claim completion. Read [operations](docs/OPERATIONS.md) before upgrading an existing database and [the build plan](docs/PRODUCT_BUILD.md) for the remaining acceptance gates. Public/free APIs remain the access constraint.

## Start with the latest work

- [Eight-page forensic-method paper](output/pdf/TraceSetu_Forensic_Method_Research_Paper.pdf) and [editable source](research/method-review-20260929/TraceSetu_Forensic_Method_Research_Paper.md).
- [Revised six-slide PPT](output/submission/TraceSetu_ANANTHA_SIH2026_Research_Revision.pptx), preserving the supplied design.
- [Synthetic reference experiment](research/method-review-20260929/reference/README.md): 64 passing functional/adversarial tests; no measured live attribution accuracy or app integration.
- [Simple visual guide](output/pdf/TraceSetu_Simple_Visual_Guide.pdf), [detailed team guide](output/pdf/TraceSetu_Problem_and_Solution_Explained.pdf), and [original research/implementation report](output/pdf/VASP_Attribution_Research_and_Implementation_Report.pdf).
- [Complete project handover / skill](skills/custody-atlas-sih/SKILL.md), [implementation checklist](IMPLEMENTATION_CHECKLIST.md), and [publication scope](docs/PUBLICATION_20260930.md).

The proposed extension uses sourced service wallets to generate deposit-address hypotheses, then searches transfers in chronological order to the first supported custody boundary. A perfectly imitating customer remains indistinguishable from service control; independent deposit evidence is still required. Older deliverables are retained as history; [the output index](output/README.md) identifies current files.

**Follow the funds. Find the receiving service.**

TraceSetu is a local investigation workbench for the SIH problem of attributing an unknown cryptocurrency wallet to the nearest supported Virtual Asset Service Provider (VASP), such as an exchange or custodian. It follows recorded transfers, shows the first evidenced receiving service on each path, exposes missing information, and prepares a request package for independent review.

**Status: functioning SIH prototype.** It is not connected to SAHYOG, does not identify customers from wallet addresses, and cannot freeze funds. A request export is explicitly marked `NOT_SENT` / `NOT_CONNECTED`. See the [capability and limits register](docs/status.md).

This branch contains the application, synthetic training fixtures, tests, research, setup documentation and selected project presentation/document files. It includes no private cases, credentials, provider responses, recordings or standalone narration files. A fresh installation starts with an empty case register; training cases are created inside the app.

## What works

- Case management, investigator/reviewer/admin accounts, case permissions and independent approvals.
- Bounded chronological tracing that stops at the first supported custodian on each branch, with an interactive graph and inspectable evidence.
- A nearestness certificate that describes the search scope and gaps that could change the answer.
- Source-family challenges that recompute the result without overwriting the original evidence.
- A request-budget planner and explicit query execution, durable request reservations, recovery and partial-result reporting.
- Read-only adapters for Bitcoin, Ethereum, BNB Chain, Polygon, Tron and Solana. Provider keys and access plans may be required; parser coverage is not a claim of complete live coverage.
- Reviewed service labels, risk assertions, watched-wallet case alerts, and a scoped Ethereum/Polygon CCTP V2 USDC bridge exercise.
- PDF/JSON/CSV reports, signed evidence ZIPs, offline verification and deterministic replay.
- Reviewed recipients and request packages, signed service-response import and independently reviewed feedback.
- A built-in **How it works** guide, available before and after sign-in.

Live mode never falls back to synthetic data. A missing label means unknown, not safe or proven self-custody. The training scenarios are explicitly invented and require no paid intelligence API.

## Run locally

Prerequisites: **Python 3.12**, **Node.js 24**, and **pnpm 11.19.0**. These match the included CI recipe. Keep the dependency lockfiles. If pnpm is absent, install it with `npm install --global pnpm@11.19.0`.

### Windows PowerShell

Run these commands inside the repository folder:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.lock
Set-Location frontend
pnpm install --frozen-lockfile
pnpm build
Set-Location ..
powershell -ExecutionPolicy Bypass -File scripts/start.ps1
```

### Linux / macOS

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
cd frontend
pnpm install --frozen-lockfile
pnpm build
cd ..
sh scripts/start.sh
```

Open **http://127.0.0.1:8787/**. On first startup the app creates the accounts `investigator`, `reviewer` and `admin`, with fresh random passwords in **`.local/bootstrap-credentials.txt`**. Read this file locally to sign in. There is no universal password. Password changes are available in the account screen and revoke existing sessions.

The default server is local-only. Keep `.local/` private: it contains the database, credentials, evidence and signing material. The application creates it automatically; do not copy another installation's private files into a clone.

## Try the prototype

Sign in as **investigator**, then select **Open training case**. Follow the [training workflow](docs/DEMO.md) to inspect custody candidates, challenge a source, execute a budgeted training expansion, verify evidence and prepare a separately reviewed request. Use another browser session for the **reviewer** account.

Select **Review a bridge case** for the separate synthetic CCTP proof-review exercise. Every training case and recipient must stay marked as training. Public-data cases from the original development machine are not bundled with the source.

## Configure live acquisition

Copy `.env.example` to `.env` if you need to override defaults, then restart the app. The example contains no credentials.

| Setting | Purpose |
|---|---|
| `ATLAS_ETHERSCAN_API_KEY` | Etherscan V2 acquisition for Ethereum, BNB Chain and Polygon, subject to endpoint/plan access. |
| `ATLAS_ETHERSCAN_METADATA_ENABLED` | Optional address metadata; disabled by default and subject to the required entitlement. Metadata enters as a hypothesis. |
| `ATLAS_TRONGRID_API_KEY` | TronGrid access where required. |
| `ATLAS_SOLANA_RPC_URL` | An authorised Solana RPC endpoint; default public endpoint has provider-controlled limits. |
| `ATLAS_BITCOIN_PROVIDER` | Explicitly select `esplora` (default) or `blockcypher`; no silent fallback. |
| `ATLAS_BITCOIN_API_URL` | Esplora-compatible URL; default `https://mempool.space/api`. |
| `ATLAS_BLOCKCYPHER_API_URL` | BlockCypher Bitcoin endpoint when explicitly selected. |
| `ATLAS_CCTP_ENABLED` | Optional scoped CCTP acquisition; disabled by default, pending live validation. |

Create a case, select **Live provider acquisition**, and set a wallet, chain, time window and bounded search/request scope. Provider errors and missing coverage remain visible. Transaction history alone does not establish a VASP's identity. Sourced labels need their own evidence and review. Read the [provider contracts](docs/provider-contracts.md).

The optional `scripts/live_bitcoin_check.py` performs a bounded public Esplora smoke check against a running local installation. It creates a neutral public-data case and uses real HTTP requests. It is not an ownership test or part of offline CI.

## Stack and implementation

| Layer | Technology / location |
|---|---|
| Interface | React, TypeScript, Vite, Cytoscape; `frontend/src/` |
| API and validation | Python, FastAPI, Pydantic; `backend/vasp_app/main.py` and `domain.py` |
| Persistence | SQLAlchemy, SQLite WAL, content-addressed evidence files; `store.py` |
| Graph analysis | Deterministic bounded traversal, custody stops and challenges; `engine.py` |
| Acquisition | Read-only HTTP/RPC adapters; `providers.py`, `blockcypher.py`, `cctp.py` |
| Planning / jobs | Request budgeting, reservations, local durable worker; `planner.py`, `execution.py`, `worker.py` |
| Evidence | ReportLab PDF, SHA-256, Ed25519 signatures and replay; `reports.py` |
| Verification | Pytest, Ruff, TypeScript build, Playwright workflows |

Attribution does not use an LLM or an invented probability score. Source grades, conflicts and missing coverage are visible. The foundation's PostgreSQL test concurrency is verified in CI; an installed production deployment, Docker operation and large-scale performance remain separate acceptance gates.

## Tests

From the repository root, on Windows:

```powershell
.venv\Scripts\python.exe -m pytest tests -q
.venv\Scripts\python.exe -m ruff check backend tests scripts/verify_evidence.py
Set-Location frontend
pnpm build
```

On Linux/macOS substitute `.venv/bin/python`. Tests use temporary synthetic data, not local case records or live provider credentials. GitHub Actions is configured to run the backend checks and frontend build.

The optional browser checks need a running local app on port 8787 with its original generated bootstrap passwords. Windows uses Microsoft Edge; on other platforms install Chromium from `frontend/` using `pnpm exec playwright install chromium`. Run from the root in this order:

```sh
node scripts/browser_check.cjs
node scripts/browser_review_check.cjs
node scripts/browser_bridge_check.cjs
node scripts/browser_query_check.cjs
```

These create synthetic training cases and local screenshots under ignored `tmp/`. They do not send notices. The review check depends on the training case made by the first check.

## Verify an exported evidence bundle

```powershell
.venv\Scripts\python.exe scripts/verify_evidence.py path\to\evidence.zip
.venv\Scripts\python.exe scripts/verify_evidence.py path\to\evidence.zip --trusted-fingerprint EXPECTED_SHA256
```

Integrity and replay do not establish the signer's identity. Obtain the expected public-key fingerprint through a trusted channel. A valid signature does not prove ownership or legal admissibility. The verifier supports engine `0.5.0` and frozen `0.3.0` / `0.4.0` implementations.

## API and further documentation

The running app exposes its schema at `/api/openapi.json`. Sign-in returns a CSRF token; authenticated writes require `X-CSRF-Token`. Analysis creation also requires a unique `Idempotency-Key`. Reusing an idempotency key with different input is rejected.

- [Training workflow](docs/DEMO.md)
- [Implemented capabilities and outstanding limits](docs/status.md)
- [Architecture decisions](docs/architecture-decisions.md)
- [Provider contracts](docs/provider-contracts.md)
- [Query execution and recovery](docs/query-execution-design.md)
- [CCTP proof scope](docs/cctp.md)
- [Signed service feedback](docs/service-feedback.md)
- [Snapshot schema](docs/snapshot.schema.json) and [bridge-proof schema](docs/bridge-proof.schema.json)

Historical `ATLAS_` settings and `atlas.*` schema identifiers are retained for compatibility with evidence replay. They are not a second product.
