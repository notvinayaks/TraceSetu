# Next-query execution — implemented contract and limits

Implemented in `execution.py`, the worker, authenticated API and dashboard. Planning is still advisory until the investigator explicitly executes it. The 18 execution tests and full 107-test regression passed; the release checklist records browser/visual acceptance. Live provider execution has not been validated from this installation.

## Required behavior

An investigator explicitly executes the selected history actions from an immutable plan belonging to a completed analysis in the same case. Bind the plan record version, content hash, parent analysis hash, snapshot hash, exact time/asset/traversal specification and original request budget. Reject changed/stale evidence, closed cases, wrong tenant/case, changed plan records, unrecognised policy versions and duplicate idempotency keys with different input. Review-only actions must not become guessed provider calls.

Use a new durable job and superseding snapshot/result. Never rewrite the parent. Preserve the plan artifact, parent evidence, new raw responses, actual HTTP usage and any unfinished scopes in the bundle. Configured provider availability is not verified entitlement. Estimates remain estimates even after an execution is launched; final accounting uses actual reserved HTTP attempts.

## Recovery and quota design

Reserve each HTTP attempt in a transactional checkpoint **before** sending it, fenced to the job's current lease/attempt. The hard budget spans recovery attempts. Losing a worker after reservation may spend a slot without producing evidence; it must never reset the quota or turn a lost response into a successful one.

Persist cache-key hashes -> raw-response artifact hashes, successful-response metadata, used attempts and cache-hit counts. Do not persist credential-bearing URLs, bodies or parameters in checkpoint metadata. On recovery, verify and parse the content-addressed cached responses and repeat deterministic parsing without paying again for already preserved responses. Fence every checkpoint write against current job ownership; a stale worker must not publish a result or regain spend authority.

Reuse the existing provider parsers, partial-result checkpoints and bounded HTTP transport. Preserve earlier successful evidence when a later scope fails. Selected actions share the total budget; do not promise that the estimated allocation completes every selected scope. Broader cross-job quotas and tenant fairness remain G07, not a hidden claim of this checkpoint.

## Tested evidence merge rules

- Identical event IDs with identical protocol fields can combine provenance references.
- Contradictory protocol fields for an existing event ID must produce an explicit reconciliation gap; never choose a version silently or leave an evidenced actionable path through the conflict.
- A partial acquisition cannot establish that a historical transaction disappeared. Preserve its historical provenance and incomplete coverage; do not call the scope current or complete.
- If a fully acquired scope no longer includes a prior outgoing event, preserve the prior snapshot and explain the exclusion from the superseding result. Absence alone does not establish why it disappeared. Full canonical reorganisation reconciliation remains D09.
- Reviewed assertions/proofs and withdrawal holds must be applied consistently. Do not resurrect a withdrawn protocol message or cross an evidenced custodial boundary while gathering a selected frontier.
- The originating incident window, seed and asset stay fixed. The parent result is a separate immutable record, not an editable canvas.

## UI and acceptance tests

Display selected scopes, hard request cap, estimated requests, configuration limitations and the parent result before execution. Show queued/running/recovered/cancelled/partial outcomes and real usage afterward. Keep training execution explicitly synthetic with no HTTP calls, never as a fallback for a failed live job.

Test read-only HTTP execution with explicit mock transports, forced crash/retry boundaries, stale leases, exhausted budgets, partial pages, contradictory events, withdrawn evidence, closed/cross-tenant cases, idempotency, historical snapshot preservation and bundle replay. Exercise the actual browser action and result inspection. Live execution remains an external validation gate until genuine permitted provider responses are retained.

The execution implementation, 18 targeted tests, 107-test regression and browser/report acceptance checks passed. C10 is checked for the stated per-job scope; live validation and cross-job quotas remain separate gates.

## Concrete API and snapshot contract

`POST /api/analyses/{parent}/query-plan` returns an immutable plan plus record ID, version and SHA-256. `POST /api/analyses/{parent}/query-plans/{record}/execute` accepts `{version, plan_sha256}` and an `Idempotency-Key`. It returns a new queued job. One plan can fund one job; retrying the same key returns that job. A new acquisition requires a new plan. Reviewer-only users cannot execute provider queries.

Engine 0.5.0 / snapshot 1.2 adds persistent `reconciliation_gaps`. Conflicting normalized observations are saved as evidence artifacts; held event IDs are excluded even if a subsequent acquisition repeats them. There is no automatic conflict-clear operation. General canonical reorganisation review remains D09. Missing observations in a newly complete scope are excluded with a partial/canonicality-review warning, not labelled an established reorganisation.

Recovery repeats parsing over saved raw responses. It is not a provider cursor continuation or a pinned-head guarantee. Recovered complete scopes are downgraded to partial where head consistency has not been established. A conflicting bridge-proof identity fails closed. New known custody/mixer scopes are skipped. Training execution uses a separately labelled invented expansion and never substitutes for live failure.

The signed bundle retains plan, execution summary, parent snapshot/analysis and new response artifacts. `reserved_request_slots` counts durable reservations; it may exceed actually dispatched requests after a crash. Provider billing remains unknown. Current quotas are shared across scopes and retries **within one job**; cross-job fairness/quotas remain G07.
