# Capability and verification register

**Publication update — 30 September 2026:** completed research, the isolated reference experiment, handover and selected project deliverables are included on `product/live-foundation`; see [publication scope](PUBLICATION_20260930.md). The full-product build remains paused. Local-only paths below describe historical evidence and are not all distributed in the clone.

Updated 29 September 2026 (India time). The user stopped the full-product build after the verified foundation publication; the current request is cryptocurrency-forensics research, a design-preserving PPT revision and a simple technical paper. The working SIH MVP is preserved. Public/free APIs remain the access constraint. See `IMPLEMENTATION_CHECKLIST.md` and `docs/PRODUCT_BUILD.md`. This file records evidence, not a production-readiness claim.

**Research method review:** `research/method-review-20260929/` specifies seeded deposit-candidate discovery plus time-respecting first-custody tracing. A separate standard-library Python reference passed **64 synthetic functional/adversarial tests**, independently rerun after temporal-state and stale-assessment fixes. The rule is deliberately narrow, retrospective, uses externally supplied identity anchors/coverage and cannot distinguish a perfectly imitating customer from service control. Its event/anchor hash does not bind coverage/balance assertions or policy parameters; those changes require rerunning detection. It is not integrated into the running MVP and no real-world attribution precision is measured. The eight-page paper, references, fictional diagram, evaluation plan and revised six-slide PPT explicitly separate proposed inference from existing functionality. Broader Bitcoin clustering, live inference and independent evaluation remain open.

**Product foundation verification:** versioned Alembic migrations, exact legacy-schema adoption, separate-worker entry point, PostgreSQL row claims, worker heartbeats, readiness, allowlisted operational request logs, tenant-restricted admin queue status and an admin health panel are implemented. Local suite: **128 passed / 2 PostgreSQL tests skipped**; hosted PostgreSQL full suite: **130 passed**. Backend/frontend/PostgreSQL [CI jobs all passed](https://github.com/notvinayaks/TraceSetu/actions/runs/36225606185). The main browser workflow and new health panel passed with zero page errors/mobile overflow. The live runner verified one real bounded BlockCypher Bitcoin sample with three exact output references and signed replay; Esplora selection timed out and is not reported as successful. The references are from the same provider, not independent attribution truth. Current details: `docs/PRODUCT_FOUNDATION_VERIFICATION.md`. Historical rows below retain their earlier baseline context; their former deferral is superseded by the resumed scope.

| Capability | Implementation | Verification / limitation |
|---|---|---|
| Research and implementation report | Completed; 50-page PDF and 44-source register | Rendered and inspected; original research stage complete |
| Independent web application | FastAPI API, React UI, local durable store | Frontend build passed; Playwright/Edge workflow passed |
| Authentication / case permissions | Scrypt passwords, random bootstrap secrets, HttpOnly sessions, CSRF, role and tenant/case checks | Positive and negative API tests; agency SSO/MFA not implemented |
| Case management | Case creation, members, status, version conflicts, activity log | API tests and browser case creation |
| Bounded custody frontier | Chronological directed paths, branch stopping, conflicting assertions, visible incomplete frontier | Synthetic regression tests; no independent real-world accuracy benchmark yet |
| Nearestness certificate | Snapshot/spec binding; separate bounded known-target and real-world claims | Missing shallow coverage and contradictory labels tested; real nearestness never presumed |
| Assumption challenge | Remove a provenance family, replay, report changed candidates and missing expansion | Engine and browser test; immutable original preserved |
| Query planning and execution | Versioned budget allocation with depth protection, explicit execution into a superseding result, immutable input binding, durable per-job request reservations/cache across retries, persistent contradictory-event holds | 18 execution tests and browser scope-review/execution/parent-preservation/report/replay checks pass. Synthetic expansion makes zero HTTP calls. Live execution and held-out cost-matched evaluation remain unvalidated; no savings claim |
| Bitcoin | Esplora confirmed address history, UTXO inputs/outpoints and outputs | Live public Bitcoin sample and browser refresh passed on 25 September 2026; exact satoshis, response hash and signed bundle replay checked. One bounded sample, not full-chain/ownership certification; no CoinJoin/change clustering |
| Ethereum / BNB / Polygon | Etherscan V2 normal/internal indexes and receipt/block-reconciled standard ERC20 logs | Decoder/adapter tests pass, including removed/reorganised/mismatched receipts; key absent. Pinned-head coverage, internal reconciliation, asset validation and live tests outstanding |
| Tron | Confirmed TronGrid native/TRC20 index | Adapter implemented; partial internal/event-order coverage; live validation outstanding |
| Solana | Finalized RPC signatures, parsed native/SPL transfer instructions, transaction-local token owners | Adapter implemented; historical token-account discovery, unsupported instruction coverage and live validation outstanding |
| Live provider failure | Explicit unavailable/partial coverage and empty attribution when unsupported | Missing-key test passes; no fixture fallback |
| Attribution data | Case-scoped source assertions with independent review | Review tests pass; commercial identity database not connected |
| Risk | Source-linked risk tags and unassessed state | Tested; numeric probability/risk calibration not implemented |
| Cross-chain | CCTP V2 native-USDC Ethereum/Polygon message, signature, receipt and mint correlation; independent import review; read-only acquisition; destination traversal from mint time | 27 targeted synthetic tests and browser review/challenge/withdrawal/replay workflow pass. Disabled-by-default live adapter is unvalidated. Other protocols/chains, independent consensus and historical code/key assurance remain gates; see `docs/cctp.md` |
| Graph | Interactive Cytoscape wallet/transfer inspection; explicit UTXO transaction nodes | Browser rendering, screenshots and interaction checked |
| Evidence export | PDF, JSON, CSV, raw responses, signed ZIP manifest | Hash/signature/replay and tamper tests pass; sample report rendered and inspected |
| Recipient directory / request review | Separate reviewer, verification expiry, exact entity match, payload-bound approval | Full API workflow passes; JSON export says NOT_SENT / NOT_CONNECTED |
| Signed service responses | Ed25519 key/request/hash binding, replay rejection, independently reviewed scoped promotion, training/operational separation | Full API workflow passes; real provider onboarding not performed |
| Corrections / reassessment | Two-person assertion/bridge-proof withdrawal, affected-analysis alerts, stale export guards and new results over preserved transfers | API/browser tests cover withdrawal, blocked request/report export, retained historical snapshots and superseding analysis; withdrawn protocol messages require new review before reuse. Cross-case propagation and external revocation distribution outstanding |
| Acquisition accounting | Standard jobs record HTTP attempts/cache hits; query executions record durable reserved request slots, preserved responses and cache hits across recovery, hash-bound in bundles | Lost slots can include requests never dispatched. Budget is shared within a job; cross-job quotas remain deferred. Billing units remain unknown |
| Wallet watches | Durable local scheduling, per-run budget, in-case change alerts | Scheduling, duplicate prevention, change alert and closed-case tests pass; multi-process scheduling remains a deployment gate |
| Worker recovery | Transactional claim, renewable lease, attempt fencing, bounded recovery, cancellation | Claim/lease regression passes; multi-worker deployment and recovery validation outstanding |
| Evidence verifier | UI and offline CLI, size/path/membership/hash/signature/replay checks; engine 0.5.0 and frozen 0.3.0/0.4.0 replay | Regression tests, browser verification and a preserved 0.4.0 bridge bundle replay pass; identity requires trusted key fingerprint |
| Production infrastructure | Configurable PostgreSQL connection; tested local SQLite WAL | PostgreSQL, external object retention, Temporal/graph services, deployment/backup/load gates outstanding |
| Official SAHYOG | No authenticated contract/access available | Not connected; no message sent and no asset frozen |

## Recorded checks

- Final MVP browser regression on 25 September 2026 (India time): **all four workflows passed**, zero page errors. Files: `tmp/browser/results.json`, `review-results.json`, `bridge-results.json`, `query-results.json`. Investigator, reviewer and bridge checks were rerun after the final query/mobile build.

- Latest full regression: **107 passed**, one existing Starlette/httpx TestClient deprecation warning; `tmp/backend-check.txt`, `tmp/backend-junit.xml`. Targeted execution suite: **18 passed** (`tmp/execution-junit.xml`). Covers immutable-plan binding, duplicate execution, roles/cases, recovery caches, lost reservations, budget exhaustion, partial HTTP acquisition, event conflicts, evidence preservation and reassessment.
- `scripts/browser_query_check.cjs`: scope review, explicit synthetic execution, parent preservation, superseding result, PDF export, signed-bundle replay and mobile overflow passed. Zero page errors. Evidence: `tmp/browser/query-results.json`, `query-review.png`, `query-result.png`, `query-mobile.png`, `query-report.pdf`, `query-evidence.zip`. The two report pages were rendered with Poppler and visually inspected. Mobile graph overflow found by this check was fixed before acceptance.
- Latest TypeScript/Vite build passed; Python lint passed. The following older checks describe earlier milestones and are retained for provenance.

- `python -m pytest tests -q`: **89 passed**, one Starlette TestClient deprecation warning, on 24 September 2026. The warning does not establish a test failure. Coverage includes all six adapter parsers, CCTP protocol/signature/receipt validation and destination chronology, review/withdrawal/replay, receipt/block consistency, removed-log rejection, missing-receipt abstention, partial-page retention, outpoint continuity, imports, watch scheduling, scoped signed feedback, advisory planning and workflow isolation. Run output and JUnit evidence: `tmp/backend-check.txt`, `tmp/backend-junit.xml`. Subsequent targeted CCTP run: **27 passed**, including fresh-run withdrawal hold, new independent approval and synthetic-purpose rejection; `tmp/cctp-check.txt`, `tmp/cctp-junit.xml`.
- TypeScript compilation passed after import corrections.
- Vite 6.4.3 build passed. The graph component is loaded on demand, with a separate graph dependency chunk. TypeScript and Python lint checks pass.
- `scripts/browser_check.cjs`: sign-in, training case, durable analysis, custody result, assumption challenge, bundle download, bundle verification, coverage screen, and mobile case viewport passed. Zero page errors; no mobile horizontal overflow. Saved evidence: `tmp/browser/results.json` and PNGs.
- `scripts/browser_review_check.cjs`: separate investigator/reviewer sessions completed recipient proposal/approval, payload review, not-sent export, signed scoped response, independent promotion, reassessment, reviewed withdrawal, affected-analysis notice and superseding reassessment. Zero page errors. Saved evidence: `tmp/browser/review-results.json`.
- `scripts/browser_bridge_check.cjs`: unreviewed synthetic bridge abstention, independent proof review, cross-chain graph/amount inspection, PDF export, provenance challenge, signed-bundle replay, withdrawal/stale-report guard and superseding analysis passed. Zero page errors and no mobile overflow. `tmp/browser/bridge-results.json`, `bridge-investigation.png`, `bridge-evidence.zip` and `bridge-report.pdf`. The two-page sample PDF was rendered with Poppler and visually inspected; it is synthetic evidence, not a real case report.
- Container and CI recipes are supplied. Docker Desktop did not finish starting within the bounded startup attempt; neither a container deployment, PostgreSQL validation nor a CI service run is claimed.
- Earlier public endpoint attempts timed out. On 25 September 2026 a later public Bitcoin analysis and browser refresh succeeded through mempool.space, with exact-output/hash/bundle checks. Tron/Solana block/slot probes succeeded but do not certify their wallet adapters. No credentialed provider validation was performed. See `docs/UI_REDESIGN_AND_LIVE_DEMO.md`.

## What may be claimed now

The independent case/evidence/review workflow is implemented and demonstrably works on explicit synthetic evidence. The engine preserves uncertainty and supports reproducible challenges. The six chain acquisition adapters exist, with visible coverage limitations.

Do not claim complete real-world attribution, validated multi-chain coverage, official government integration, production scale, calibrated accuracy, real freezing, or world-first novelty. Those remaining gates belong to the deferred production backlog. The requirement map explicitly identifies partial support and unimplemented general clustering/swaps rather than presenting every problem-statement item as fully solved.

## TraceSetu branding and final handover/video milestone

25 September 2026: renamed the app, API presentation and new reports to TraceSetu; preserved historical evidence and compatibility identifiers. Added the complete target solution and PPT guidance to the self-contained skill. Delivered a verified 2:40 native 4K walkthrough, visible cursor, 14 click zooms and timed narration script. Build/lint, report-bundle test, browser/mobile workflow and actual nine-chapter capture passed. Video decoded fully and passed browser playback/seek; PDF pages visually inspected. See `docs/VIDEO_DELIVERY.md` and `output/demo/video-verification.json`. Production backlog scope/counts remain unchanged.

## UI revision and live Bitcoin milestone — historical UI review milestone

25 September 2026: the investigation desk now uses a restrained light layout, clearer result summary, case filters/search/pagination, evidence drawer and keyboard/mobile improvements. Existing investigator, independent-review, bridge and query browser workflows passed. The additional UI check passed with zero page errors, including real Bitcoin refresh, response SHA-256 verification and signed live-bundle replay. Source-linked risk signals and unassessed states remain visible. Fixed a UTXO transaction-node ID collision exposed by real-data rendering.

One bounded live Bitcoin sample is now demonstrated; it produced one observed transfer and no invented custody label. This does not certify all six chains or real-world VASP attribution. The 50/95 future-backlog count and original 12/12 scoped release baseline are unchanged.

- [x] Redesign implemented and built.
- [x] Desktop/mobile, keyboard and existing investigation workflows checked.
- [x] Live Bitcoin acquisition, refresh and evidence verification demonstrated.
- [x] Handover and capability limits updated.
- [x] The user subsequently requested the real-case recording and approved TraceSetu; this supersedes the earlier waiting instruction.
- [x] Authorized replacement footage captured at 3840×2160; final delivery verification is tracked in the TraceSetu submission milestone.

Details and a proposed 2:40 sequence: [UI review and live demo](UI_REDESIGN_AND_LIVE_DEMO.md). Screenshots and machine-readable evidence are in `output/ui-review/`. The older `output/demo/Vittanvaya_SIH_MVP_4K.mp4` remains a previous-UI artifact, not the new recording.


## Plain-language in-app guide milestone

- [x] Add **How it works** before sign-in, in the sidebar and on Investigations, with seven linked chapters, a labelled illustrative flow, plain result definitions, roles, next actions, limits and FAQs.
- [x] Verify the training shortcut, return to the existing case, desktop/mobile layouts and zero browser page errors. Evidence: `output/help-review/results.json` and screenshots; TypeScript/Vite passed.

See `docs/HOW_IT_WORKS.md` and `frontend/src/HowItWorks.tsx`. This is an onboarding improvement, not a new attribution or live-coverage claim. The original scoped-release/backlog counts remain unchanged. The later explicit real-case recording request supersedes the earlier UI-approval hold; see docs/TRACESETU_SUBMISSION.md.


## Consolidated single-file agent handover

- [x] Preserve the exact problem, 30 requirement rows, full original report, 44 numbered research records and supplementary links, intended final solution, actual implementation/contracts and all current UI/guide changes.
- [x] Add explicit end-user jobs, implemented-role boundaries, current versus future support, five USP mechanisms and their acceptance/measurement limits, a front-page reading map and all six recorded browser-result files.
- [x] Validate completeness, Markdown navigation/fences, 45 API routes, the 107-test historical record, source fingerprints and secret exclusion; preserve the historical approval context; the later recording request supersedes that hold.

Canonical file: `skills/custody-atlas-sih/SKILL.md`. Shareable identical file: `output/TraceSetu_COMPLETE_SKILL.md`. These are context/handover artifacts, not a database or source-repository backup. Production task counts and application behavior are unchanged.

## TraceSetu submission milestone — 25 September 2026

- [x] Rename the current app, help, API identity, generated reports, active documents and presentation to TraceSetu; preserve historical signed artifacts and stable schema identifiers.
- [x] Audit the supplied PPT against actual implementation; retain six slides, correct review/coverage/stack claims, label the custody example synthetic and provide editable link fields. Final native layout and integrity checks are recorded under `tmp/ppt-review`.
- [x] Add an explicitly selected read-only Bitcoin alternative; verify nine provider regressions and **116 passing backend tests**. Incomplete pagination remains partial.
- [x] Acquire real public WannaCry transactions, preserve exact amounts and primary-source context, execute a bounded follow-up, and verify signed live-bundle integrity and deterministic replay. No VASP label is invented.
- [x] Capture eight chapters of the real app at native 3840×2160, with zero browser page errors; provide a synchronized 334-word script.
- [x] Final 160-second 3840×2160 video passed full decode, Edge playback/seek and visual QA; 15 click zooms and a clear pointer are included.
- [x] Validate the complete handover: exact statement, full original report, all requirements, sources, 45 routes, 116-test evidence, final deck text and live recording facts; prepare identical shareable and installed copies.

Current facts, sources and limits: `docs/TRACESETU_SUBMISSION.md`. These are submission milestones; the original scoped MVP and future-production backlog counts remain separate.
