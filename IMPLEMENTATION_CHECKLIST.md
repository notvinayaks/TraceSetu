# Custody Atlas — full-product backlog

## Replacement presentation — 3 October 2026

- [x] Rebuild the six-slide submission in the original `(10)` template with a reference-inspired problem/solution layout, editable methods flow, concrete experiment comparison, actual labelled prototype screenshot and primary-source links. Recheck source claims, rerun the 64 synthetic reference tests and inspect the native PowerPoint/PDF output. Deliverables: `docs/SIH_SUBMISSION_20261003.md`.

Documentation only; no new production capability or live attribution is claimed. Named engineering counts are unchanged.

## Final template submission and public publication — 30 September 2026

- [x] Publish completed project work publicly on `product/live-foundation` while preserving the MVP on `main`. Evidence: anonymous repository access and four successful hosted checks at commit `eb5b899c48a5b5c69322f4fa6546a643a10af595`, run `36720225633`.
- [x] Rebuild the six-slide idea presentation in the exact supplied `(10)` template, include an authentic labelled prototype screenshot, verified-method references, public repository/demo links and separate implemented/research status. Evidence: `docs/SIH_SUBMISSION_20260930.md` and the final PowerPoint/PDF package checks.
- [x] Provide copy-ready idea title, description and abstract, and update the complete project handover. Evidence: `output/submission/TraceSetu_Idea_Description_Abstract.txt` and `skills/custody-atlas-sih/SKILL.md`.

Documentation/publication only. The named engineering counts remain unchanged. No SIH portal upload, new live attribution result, application integration or full-product completion is claimed.

## Research-method review — 29 September 2026

- [x] Review primary cryptocurrency-forensics papers, specify seeded deposit-candidate inference plus temporal first-custody search, and explain its evidence/identifiability limits. Evidence: `research/method-review-20260929/TraceSetu_Forensic_Method_Research_Paper.md` and the eight-page reviewed PDF in `output/pdf/`.
- [x] Build and independently review an isolated synthetic reference experiment. **64 functional/adversarial tests passed**, including later address revisits, stale event/anchor snapshot rejection and gas-feeder-only unresolved stops. Evidence: `research/method-review-20260929/reference/results.json`. No measured real-world accuracy or application integration.
- [x] Revise the user-selected six-slide PPT while retaining its original geometry, themes, fonts, images and native tables; inspect all six native PowerPoint renders. Evidence: `output/submission/TraceSetu_ANANTHA_SIH2026_Research_Revision.pptx`, `tmp/method-review-20260929/design-preservation.json` and `final-validation.json`.

This documentation/reference milestone does not complete a named production-backlog item. The full-product build remains paused; no app/UI changes or new GitHub push were made for this review. Independent service/deposit truth, calibrated evaluation, production integration and official SAHYOG remain open.

## Detailed team guide — 28 September 2026

- [x] Replace the dense introduction with a three-page visual explanation using one fictional example, transfer diagram, decision flowchart and reviewed-action workflow. Evidence: `output/pdf/TraceSetu_Simple_Visual_Guide.pdf`; all pages visually inspected, no clipped text or arrows crossing text in the final version. Documentation only; named engineering counts unchanged.

- [x] Explain the problem, intended complete solution, implemented features, USP, technical terms, live-data evidence and remaining limits in a detailed plain-language document. Evidence: `output/pdf/TraceSetu_Problem_and_Solution_Explained.pdf`, 12 visually reviewed pages; `tmp/team-guide-20260928/qa.json` verifies all 231 source text blocks and 12 bookmarks. Documentation only; full-product work remains stopped and the named engineering counts are unchanged.

## GitHub source release — 26 September 2026

- [x] Prepare a complete prototype-only repository, with portable setup and no private runtime data, videos or narration. Evidence: `output/repository/TraceSetu`, 79-file staged audit in `tmp/github-package-audit.json`.
- [x] Verify a fresh installation: 116 backend tests, Ruff, dependency consistency, frontend build and main browser workflow passed. Evidence: `output/repository/TraceSetu/docs/RELEASE_VERIFICATION.md`.
- [x] Create the private repository, push `main` and compare local/remote commit hashes. Evidence: [notvinayaks/TraceSetu](https://github.com/notvinayaks/TraceSetu), initial commit `fac605d5e9d8688b561933790a571c65f6e704b3`.
- [x] Confirm both hosted GitHub Actions jobs pass on the uploaded commit. Evidence: [verified CI run](https://github.com/notvinayaks/TraceSetu/actions/runs/36221054101).

See `docs/GITHUB_RELEASE.md` for the publication folder and future synchronisation instructions. These release tasks do not change the unweighted future-product task counts or establish production readiness.

**Current scope, 26 September 2026:** the user explicitly resumed the full live product build, with public/free APIs only. This full-product checklist is active again. The earlier MVP release remains documented in [MVP_CHECKLIST.md](MVP_CHECKLIST.md); its historical completion does not satisfy this checklist. Checkboxes still require implementation and verification, and external gates cannot be simulated as complete. See [current build plan](docs/PRODUCT_BUILD.md).

<!-- progress:start -->
**52 of 95 named tasks verified. 43 remain: 31 engineering/validation tasks and 12 external acceptance gates.**

| Workstream | Verified | Remaining |
|---|---:|---:|
| A. Research and implementation design | 6/6 | 0 |
| B. Application foundation and security | 8/12 | 4 |
| C. Attribution, graph correctness and differentiation | 10/15 | 5 |
| D. Chain acquisition and data quality | 9/15 | 6 |
| E. Cross-chain protocol evidence | 5/8 | 3 |
| F. Investigation, evidence and lawful-request workflow | 9/14 | 5 |
| G. Reliability, scale, usability and handover | 5/13 | 8 |
| X. External acceptance gates — cannot be invented | 0/12 | 12 |
<!-- progress:end -->

**How to read it:** checked means the narrowly stated task has passed the linked checks. An unchecked engineering task is still mine to implement or verify. External gates need access, authoritative data or acceptance from the relevant organisation; they are never replaced by invented results. Counts are unweighted task counts, **not a percentage of effort or production readiness**. Several remaining tasks are larger than completed ones.

**Published baseline:** the 12 scoped MVP acceptance checks passed. Full-product engineering has now resumed, preserving that baseline and all remaining acceptance gates.

**Evidence:** [capability/status register](docs/status.md), [research PDF](output/pdf/VASP_Attribution_Research_and_Implementation_Report.pdf), [architecture decisions](docs/architecture-decisions.md). Latest full backend run: **107 tests passed**; targeted execution run: **18 passed**. Query execution browser workflow and report visual QA passed. These are synthetic/local checks, not live attribution accuracy.

## A. Research and implementation design

- [x] **A01** Research the problem and distinguish on-chain observations from VASP identity and beneficial ownership. Evidence: research report and 44-source register.
- [x] **A02** Produce the full architecture, stack, data/API contracts, test strategy, deployment plan and dependency analysis. Evidence: 50-page implementation report.
- [x] **A03** Research competing capabilities and define testable differentiation without claiming world-first novelty. Evidence: `research/differentiation.md`.
- [x] **A04** Define first-custody stopping rules, nearestness scope, incomplete coverage and explicit abstention. Evidence: report, engine contract and regression tests.
- [x] **A05** Document provider access/licensing assumptions and the unavailable official SAHYOG contract. Evidence: report and provider contracts.
- [x] **A06** Render and visually verify the research PDF and preserve editable source and source register. Evidence: `research/verify_report.py`, `output/pdf/`.

## B. Application foundation and security

- [x] **B01** Build the independent FastAPI/React application and reproducible local startup. Evidence: frontend build and browser sign-in/case workflow.
- [x] **B02** Implement password hashing, random local bootstrap credentials, sessions, CSRF and session revocation on password change. Evidence: security/workflow API tests.
- [x] **B03** Enforce tenant, case membership and investigator/reviewer/admin permissions. Evidence: positive and negative access tests.
- [x] **B04** Create/manage cases, references, classification, members and status with version-conflict checks. Evidence: API tests and browser workflow.
- [x] **B05** Implement durable local jobs, lease claims, recovery, attempt fencing, cancellation and idempotency. Evidence: worker/workflow tests; single-node scope only.
- [x] **B06** Preserve content-addressed artifacts, canonical JSON and integrity checks on reads. Evidence: tamper and bundle tests.
- [x] **B07** Configure host/origin restrictions and bounded request/provider response sizes; keep secrets out of acquisition metadata. Evidence: middleware/provider tests and code checks.
- [x] **B08** Add versioned database migrations and verify PostgreSQL schema upgrades, tenancy enforcement, concurrency and rollback behavior. Evidence: frozen-baseline adoption/preservation/rejection and migration concurrency/rollback tests; full PostgreSQL CI suite **130 passed**, including existing tenant/case permissions and 12 simultaneous distinct worker claims. [CI run](https://github.com/notvinayaks/TraceSetu/actions/runs/36225606185). Schema removal is prohibited; runtime deployment and disaster-recovery acceptance remain separate gates.
- [ ] **B09** Integrate agency-compatible OIDC/SSO, MFA policy and service identities; validate real IdP login/revocation boundaries.
- [ ] **B10** Add controlled secrets/signing-key lifecycle, rotation and production KMS/HSM support with validation.
- [ ] **B11** Implement externally retained audit records, retention/legal hold and governed evidence correction/redaction.
- [ ] **B12** Add production observability, health/readiness detail, redacted structured logs and actionable failure metrics.

## C. Attribution, graph correctness and differentiation

- [x] **C01** Trace chronological directed paths and stop at the first custody boundary on every branch. Evidence: engine tests; no exchange-internal ledger crossing.
- [x] **C02** Preserve exact integer amounts and chain-qualified asset/address identities. Evidence: engine and adapter tests.
- [x] **C03** Keep possible exposure bounds separate from incident-fund allocation; never sum overlapping paths as recovered funds. Evidence: engine contract/tests and reports.
- [x] **C04** Show contradictory labels, hypotheses, mixer stops and unresolved asset/protocol transitions. Evidence: adversarial engine tests.
- [x] **C05** Produce a snapshot/spec-bound nearestness certificate that separates bounded known targets from unknown real-world services. Evidence: shallow-gap tests.
- [x] **C06** Remove a provenance family and recompute the result without changing the original evidence. Evidence: engine/API/browser challenge checks.
- [x] **C07** Produce a budget-aware advisory next-query plan with depth protection and explicit cost assumptions. Evidence: planner/API/browser tests.
- [x] **C08** Record actual request attempts/cache hits separately from estimates and unknown vendor billing units. Evidence: provider accounting tests and evidence manifest.
- [x] **C09** Show sourced risk tags and an unassessed state; do not invent calibrated probabilities. Evidence: engine tests and UI.
- [x] **C10** Execute selected next-query plans with immutable input binding, acquisition recovery, a request budget shared across scopes/retries within a job, and a superseding result. Evidence: 18 execution tests, full regression and browser query/report/replay checks. Cross-job quotas remain G07.
- [ ] **C11** Add explainable laundering-typology rules and adversarial tests, with signals separated from criminal conclusions.
- [ ] **C12** Implement conservative, reversible cluster hypotheses and conflict handling, including Bitcoin change/CoinJoin ambiguity and service hot/deposit roles.
- [ ] **C13** Build the independent evaluation harness with entity/time-disjoint slices, precision/coverage/abstention, cost and investigator-time metrics.
- [ ] **C14** Calibrate confidence only if independently labelled data supports it; otherwise preserve evidence grades and measured abstention.
- [ ] **C15** Run cost-matched planner and assumption-challenge comparisons; claim differentiation benefits only after measured results.

## D. Chain acquisition and data quality

- [x] **D01** Implement bounded read-only acquisition, pacing, timeout, within-run caching, raw-response hashes and partial-result preservation. Evidence: provider tests; no fixture fallback.
- [x] **D02** Implement Bitcoin confirmed history, input sets, outputs and exact spent-outpoint continuity. Evidence: synthetic Esplora/engine tests.
- [x] **D03** Implement Ethereum normal/internal indexes and standard ERC20 receipt/block reconciliation. Evidence: synthetic parser and removed/reorganised-log tests.
- [x] **D04** Implement BNB Chain through the EVM adapter with chain-specific identity. Evidence: synthetic adapter contract; live certification remains open.
- [x] **D05** Implement Polygon through the EVM adapter with chain-specific identity. Evidence: synthetic adapter contract and CCTP exercise; live certification remains open.
- [x] **D06** Implement Tron confirmed native/TRC20 history and filter non-transfer records. Evidence: synthetic TronGrid tests.
- [x] **D07** Implement Solana finalized signatures, supported parsed native/SPL transfers and transaction-local token owners. Evidence: synthetic RPC tests.
- [x] **D08** Implement optional Etherscan metadata ingestion as hypotheses; missing key/entitlement stays explicit. Evidence: provider tests.
- [ ] **D09** Add pinned-head acquisition, canonicality/reorganisation reconciliation and superseding evidence across the supported chains.
- [ ] **D10** Reconcile EVM native/internal transfers and ordering; certify supported token semantics and reviewed asset registries.
- [ ] **D11** Complete Bitcoin script, replacement/reorganisation and pagination adversarial coverage; document unresolved allocation cases.
- [ ] **D12** Expand Tron internal/event-order coverage and verify provider finality/receipt semantics.
- [ ] **D13** Add Solana historical/closed token-account discovery and supported instruction/intra-slot ordering coverage.
- [ ] **D14** Add a production intelligence-provider adapter and entity/legal-identity mapping under its verified API/rights contract.
- [x] **D15** Provide an authorised live-validation runner and per-chain capability manifest preserving actual responses, failures and entitlement results. Evidence: `scripts/validate_live.py`, strict plan/bundle/source-mode tests and actual six-chain capability runs. Bitcoin: bounded transfer sample/replay passed; Tron/Solana: endpoint responses retained without transfer validation; Ethereum/BNB/Polygon: missing configured access, zero provider calls. No data rights, full-chain or ownership certification is inferred. Private manifests are referenced in `docs/PRODUCT_FOUNDATION_VERIFICATION.md`.

26 September D15 scope: implemented the validation tooling and recorded actual access outcomes, not successful six-chain attribution. Independent/live transfer acceptance for each chain and institutional access remain separate X02–X07/X01 gates.

## E. Cross-chain protocol evidence

- [x] **E01** Define bounded proof packages and preserve unsupported bridge transitions as unresolved. Evidence: schema 1.1 and engine tests.
- [x] **E02** Verify CCTP V2 native-USDC Ethereum/Polygon source bytes, attestation signatures, destination acceptance and exact mint. Evidence: `tests/test_cctp.py`; synthetic only.
- [x] **E03** Bind burn/fee/net amounts and destination mint time/position; reject ambiguous/duplicate/tampered packages. Evidence: targeted adversarial tests.
- [x] **E04** Implement read-only CCTP acquisition using forward-transaction hints or nonce-specific destination lookup under the shared job budget. Evidence: mocked HTTP transport tests; live validation open.
- [x] **E05** Support independent proof review, source-family challenge, withdrawal holds, reassessment, graph inspection and report/bundle replay. Evidence: API and browser bridge workflow.
- [ ] **E06** Validate historical contract/key provenance, key rotation, finality and reorganisation behavior on independently checked live CCTP examples.
- [ ] **E07** Extend certified bridge support to the other relevant chains/protocols, including a separately verified Wormhole or equivalent adapter with proof-specific tests.
- [ ] **E08** Implement supported on-chain swap/aggregator semantics and economic accounting; opaque off-chain swaps remain explicitly unresolved unless separately evidenced.

## F. Investigation, evidence and lawful-request workflow

- [x] **F01** Provide case dashboard, interactive graph, UTXO transaction nodes, transfer inspection and coverage limitations. Evidence: browser tests/screenshots.
- [x] **F02** Import strict snapshots and separate submitted hypotheses from reviewed case assertions. Evidence: import/API tests.
- [x] **F03** Produce PDF/JSON/CSV/raw-evidence bundles with signed manifests. Evidence: report visual QA and bundle tests.
- [x] **F04** Verify bundle membership, hashes, signatures and deterministic replay without executing bundled code. Evidence: tamper tests, CLI and browser; engines 0.3.0/0.4.0/0.5.0 supported.
- [x] **F05** Maintain an independently reviewed recipient directory with expiry, purpose and exact entity matching. Evidence: API/browser tests; no real contacts preloaded.
- [x] **F06** Prepare disclosure/preservation/freezing-review packages with payload-bound approval and explicit NOT_SENT / NOT_CONNECTED exports. Evidence: API/browser workflow.
- [x] **F07** Verify request/key-bound signed service responses and promote only reviewed wallet/entity/time-scoped attestations. Evidence: forgery/replay/scope tests and browser workflow.
- [x] **F08** Withdraw reviewed assertions/proofs, flag dependent analyses, block stale exports and create superseding analyses. Evidence: API/browser tests.
- [x] **F09** Schedule local wallet watches with per-run budgets and in-case change alerts. Evidence: scheduling/duplicate/closed-case tests; external notifications not implemented.
- [ ] **F10** Add governed legal-entity aliases, verified directory correction/expiry workflows and approved request-template versioning.
- [ ] **F11** Implement a clearly labelled SAHYOG contract simulator and separate dispatch boundary, with idempotent delivery/status semantics and no real-send default.
- [ ] **F12** Implement the real SAHYOG adapter only against the official authorised contract; distinguish sent, acknowledged, accepted and verified action states.
- [ ] **F13** Add signed correction/revocation formats and permissioned cross-case propagation without leaking case data.
- [ ] **F14** Add operational alert acknowledgement/escalation and authorised notification delivery, with noise/duplicate controls.

## G. Reliability, scale, usability and handover

- [x] **G01** Run local backend regression tests and record machine-readable results. Evidence: `tmp/backend-check.txt`, `tmp/backend-junit.xml`; 107 passed at last full run.
- [x] **G02** Compile TypeScript, build Vite and pass Python lint checks. Evidence: recorded local build/lint results.
- [x] **G03** Run investigator and independent-reviewer browser workflows without page errors. Evidence: three `tmp/browser/*results.json` files.
- [x] **G04** Check mobile overflow and visually inspect current graph/report output. Evidence: Playwright screenshots and Poppler render QA.
- [x] **G05** Supply startup instructions, configuration example, dependency locks, API schema and deployment/CI recipes. Evidence: README and repository files; recipe execution is a separate gate.
- [ ] **G06** Run container/Linux/PostgreSQL deployment end-to-end, including migrations, secrets, TLS and least-privilege processes. Docker startup has not succeeded in this environment.
- [ ] **G07** Implement and validate scalable durable workflows, shared quotas, tenant fairness, retry/backoff and multi-worker recovery.
- [ ] **G08** Add encrypted object storage/retention and checkpointed graph projection; validate graph rebuild and database fallback.
- [ ] **G09** Benchmark declared large-wallet and concurrent-case workloads; meet documented latency/cost/memory targets or report shortfalls.
- [ ] **G10** Demonstrate backup/restore, interrupted-job recovery, provider outages and signing-key rotation drills.
- [ ] **G11** Complete keyboard/screen-reader/accessibility checks and investigator usability testing; resolve critical issues.
- [ ] **G12** Run CI in the target service, dependency/security checks and independent penetration assessment; fix release-blocking findings.
- [ ] **G13** Deliver tested operator/investigator manuals, incident/recovery runbooks and an accepted production handover package.

## X. External acceptance gates — cannot be invented

- [ ] **X01** Obtain provider/API entitlements and data retention/redistribution rights for the deployed configuration.
- [ ] **X02** Validate Bitcoin live acquisition with independently checked real examples and retained evidence.
- [ ] **X03** Validate Ethereum live acquisition and attribution inputs with independently checked real examples.
- [ ] **X04** Validate Tron live acquisition and attribution inputs with independently checked real examples.
- [ ] **X05** Validate BNB Chain live acquisition and attribution inputs with independently checked real examples.
- [ ] **X06** Validate Solana live acquisition and attribution inputs with independently checked real examples.
- [ ] **X07** Validate Polygon live acquisition and attribution inputs with independently checked real examples.
- [ ] **X08** Obtain an independently adjudicated acceptance corpus across the six chains; preserve negative/ambiguous cases and prevent training/test leakage.
- [ ] **X09** Pass the report's attribution-quality gates with measured precision, coverage, abstention and confidence intervals; do not treat vendor labels as independent ground truth.
- [ ] **X10** Obtain verified VASP recipients, trusted service-signing identities, authorised legal templates and receiving-agency governance decisions.
- [ ] **X11** Obtain the official SAHYOG API contract/sandbox and pass authenticated integration acceptance for the authorised scope.
- [ ] **X12** Pass approved production hosting/security/retention/operational acceptance, assign support ownership and document real SAHYOG delivery/action acknowledgements where authorised.

## Update rules

1. Implement the narrowly named task, run its meaningful acceptance checks, inspect the result and record the evidence.
2. Only then change its checkbox to checked and update `docs/status.md` when a capability changes.
3. Run `python scripts/update_checklist.py` to refresh counts. This script only counts boxes; it never decides a task is complete.
4. Reopen a checked item if a regression invalidates its evidence. Keep synthetic, local, live and official acceptance distinct.
5. Do not call the production platform complete while applicable production gates remain open. The revised MVP can be handed over when its separate checklist passes. Do not ask for repeated approval for already authorised work.

## Latest completed milestone

25 September 2026 (India time): completed explicit query execution, durable per-job request reservations and response reuse, immutable parent binding, conflict holds, dashboard scope review and report/bundle output. Full suite: 107 passed; targeted execution suite: 18 passed; query browser/mobile and PDF visual checks passed. User revised delivery to an MVP; production expansion is deferred.

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

Details and a proposed 2:40 sequence: [UI review and live demo](docs/UI_REDESIGN_AND_LIVE_DEMO.md). Screenshots and machine-readable evidence are in `output/ui-review/`. The older `output/demo/Vittanvaya_SIH_MVP_4K.mp4` remains a previous-UI artifact, not the new recording.


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
