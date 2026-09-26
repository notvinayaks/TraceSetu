# TraceSetu operator guide — product development

The full product build is in progress. The operations below are implemented engineering controls, not agency deployment accreditation. Live attribution, legal identity and institutional delivery have separate acceptance gates.

## Database upgrades

The app now uses Alembic revisions rather than silently creating an evolving schema. A new development database migrates at startup. Existing unversioned databases are refused until an operator explicitly adopts the exact original schema. Unexpected columns, indexes or tables prevent adoption; nothing is guessed or deleted.

**Before upgrading a populated installation:** stop its API and workers, take a consistent database backup and copy the evidence objects and signing key to protected backup storage, then verify restoration in a separate location. SQLite WAL databases must be backed up through SQLite's backup API (or while fully closed), not by copying only the `.sqlite3` file while writers are active. PostgreSQL needs a verified native backup. Do not put database/signing-key backups in Git.

From the root, with the appropriate private environment configured:

```powershell
.venv\Scripts\python.exe scripts/manage.py db-version
.venv\Scripts\python.exe scripts/manage.py db-upgrade --adopt-legacy
```

Use `db-upgrade` without `--adopt-legacy` for a new or already versioned database. On Linux use `.venv/bin/python`. The schema changes run under a database lock. The operational heartbeat revision can be rolled back in a controlled maintenance procedure; dropping the original investigation schema is prohibited. Database backups and schema checks do not establish a complete disaster-recovery programme.

## Separate API and workers

Set `ATLAS_WORKER_ENABLED=false` for the API process, then run a separate process against the same configured database and evidence directory:

```powershell
.venv\Scripts\python.exe scripts/manage.py worker
```

Each worker has a random process identity and a persistent heartbeat. PostgreSQL claims use locked rows with `SKIP LOCKED`; SQLite uses conditional claims. Watch scheduling uses transaction/row locks. Long-running jobs retain the existing attempt/lease fences and bounded recovery. Shared provider quotas, tenant fairness and wider load/fault tests are still separate work.

Set `ATLAS_READINESS_REQUIRES_WORKER=true` when the installation must serve analysis jobs. `/api/health` is liveness; `/api/ready` returns 503 when required components fail. A recent worker heartbeat is not evidence that every provider or job works. The admin-only `/api/operations` and **Data & coverage → Service health** show database/schema/storage/worker checks and agency-scoped queue counts.

## Production configuration gate

`ATLAS_ENVIRONMENT=production` requires `ATLAS_LOCAL_BOOTSTRAP=false`, `ATLAS_SECURE_COOKIE=true`, `ATLAS_AUTO_MIGRATE=false`, explicit allowed hosts and HTTPS origins. Apply migrations as a separate operator step before starting the API/worker. The settings check does not install TLS or configure an agency identity provider. TLS termination, SSO/MFA, production signing/storage policy, external audit and independent acceptance remain release gates.

## Operational logs

Structured request events use generated request IDs, route templates, status, duration and error category. They exclude literal query strings, bodies, cookies, addresses and client-supplied request IDs. Worker-loop failures record categories without exception URLs. SQLAlchemy parameter rendering is disabled. Protect log access and configure the reverse proxy/runtime to avoid logging raw URLs or credentials; this allowlist is not a claim that every external component is configured securely.

## Live provider validation

The runner creates explicitly neutral cases, submits real `live` jobs, saves failures and signed evidence, checks deterministic replay and compares exact supplied transaction references. It rejects synthetic/imported results and does not call a response with zero observed transfers a successful transfer test. Full-chain validation, independently established ownership and real-world accuracy remain false.

Prepare a private plan containing `schema_version: "tracesetu.live-validation-plan.v1"` and `checks`. Each check has a unique lowercase `name`, a normal `TraceSpec` in `spec` (chain, valid address, start/end epoch seconds, traversal limits and request cap), and optional `expected_transfers` (txid, recipient, asset, integer-string amount and source reference). Use authorised public samples with independently reviewed reference facts. A plan is capped at 200 configured HTTP requests across at most 12 checks; lower budgets are recommended for public endpoints.

```powershell
.venv\Scripts\python.exe scripts/validate_live.py private-plan.json --output .local/live-check-001 --bootstrap-file .local/bootstrap-credentials.txt
```

The output directory must be new. Local bootstrap login is restricted to loopback; remote login requires HTTPS and the password in `ATLAS_VALIDATION_PASSWORD`. Never put credentials in arguments, plans or Git. Optional `--trusted-fingerprint` pins a signer identity obtained through a trusted channel. Without it, bundle integrity/replay is checked but signer identity is untrusted. Exit 0 means every bounded check returned transfer evidence and passed the selected checks; exit 1 includes unavailable, empty, mismatch, failed or timed-out checks. A timeout may leave a bounded job running; inspect its recorded job ID.

All retained cases, raw responses and exported manifests are local evidence. The manifest records the selected provider, configuration state and whether an endpoint response was actually observed. Successful HTTP access is not verified data-use rights or general entitlement. The reference URL/text is operator-supplied context; its authenticity is not established merely by matching a transaction. No provider licence, full history, service ownership or SAHYOG connection is inferred from a successful run.
