# Source release verification — 26 September 2026

This source-only package was checked in a fresh, isolated installation. Application and test source files match the existing working prototype; publication changes are limited to packaging and portable documentation.

| Check | Result |
|---|---|
| Python dependency installation | Passed in a newly created virtual environment using `requirements.lock` and the official PyPI index. |
| Python dependency consistency | `pip check`: no broken requirements. |
| Backend regression | **116 passed**, one upstream Starlette test-client deprecation warning. |
| Ruff | `ruff check backend tests scripts/verify_evidence.py`: passed. |
| Frontend dependency installation | `pnpm install --frozen-lockfile`: passed. |
| Frontend production build | TypeScript and Vite build passed. |
| Fresh startup | New local database and random bootstrap accounts created; health endpoint returned TraceSetu / independent installation / SAHYOG not connected. |
| Existing browser smoke workflow | Passed sign-in, training-case creation, durable analysis, custody result, request-budget planning, source challenge, bundle download and integrity/replay verification, coverage page and mobile viewport. No page errors or horizontal mobile overflow. |
| Upload contents | Application, schemas, tests, launch/verification scripts, lockfiles and technical documentation only. Private runtime data and generated submission artifacts excluded. |

Local verification used Windows, Python 3.12.14, Node.js 24.19.0 and pnpm 11.25.0. CI is separately configured for Python 3.12, Node.js 24 and pnpm 11.19.0; its actual run status is visible in the repository's Actions tab.

The browser check used the clean installation on port 8790 with that origin explicitly allowed in its process configuration; the checked-in default remains port 8787. Its only temporary script change was the test URL. The original running installation and cases were not modified.

The first Python installation attempt encountered a DNS failure on the machine's configured package index; retrying against official PyPI succeeded. The initial browser attempt was correctly rejected because the alternate test origin had not yet been allowed. Both were test-environment issues, not changes to application behavior.

This release check did not rerun live blockchain acquisition, all optional browser workflows, Docker/PostgreSQL deployment or an independent attribution benchmark. It does not establish production readiness, new live-chain coverage, SAHYOG delivery or asset freezing. See [status and limits](status.md).
