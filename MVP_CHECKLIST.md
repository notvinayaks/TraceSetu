# SIH MVP — release checklist

## GitHub source release — 26 September 2026

- [x] Publish the complete prototype source, tests and portable setup to [private notvinayaks/TraceSetu](https://github.com/notvinayaks/TraceSetu), excluding private runtime data and submission media/scripts.
- [x] Verify fresh dependency installs, 116 backend tests, Ruff, TypeScript/Vite and the main browser workflow with zero page errors or mobile overflow.
- [x] Confirm remote commit equality and successful backend/frontend GitHub Actions jobs: [run 36221054101](https://github.com/notvinayaks/TraceSetu/actions/runs/36221054101).

The Git-managed copy is `output/repository/TraceSetu`; it is separate from the original running workspace. See `docs/GITHUB_RELEASE.md` before synchronising future changes. Existing MVP and future-production counts are unchanged.

The user revised the immediate deliverable to a working MVP on 25 September 2026 (India time). Production infrastructure and institutional onboarding are deferred. The original [full-product checklist](IMPLEMENTATION_CHECKLIST.md) remains available as a future backlog.

**12 of 12 scoped MVP release checks verified.** Counts represent the local release checks below, not completion of every production requirement or real-world attribution accuracy. The app is running at http://127.0.0.1:8787/.

- [x] **M01** Sign-in, investigator/reviewer roles, case membership and isolation. API regression tests.
- [x] **M02** End-to-end training investigation: wallet → chronological graph → first evidenced custody candidates → visible gaps. Engine/API tests and existing browser checks.
- [x] **M03** Explainable USP: bounded nearestness certificate and source-family challenge, with original evidence preserved. Engine/API/browser checks.
- [x] **M04** Six-chain acquisition adapters and strict evidence imports, with explicit unavailable/partial states. Parser and failure-path tests; live provider certification is excluded from this MVP claim.
- [x] **M05** Source-backed service roles, categorical evidence grades and risk tags; unknown stays unassessed. No fabricated ownership or probability.
- [x] **M06** Bounded Ethereum/Polygon CCTP V2 proof review and cross-chain graph demonstration. Synthetic protocol/API/browser checks; other protocols remain unresolved.
- [x] **M07** Investigation PDF and signed evidence bundle with independent hash/signature/replay verification. Regression and visual checks.
- [x] **M08** Verified-recipient proposal, separate reviewer, payload-bound request review and NOT_SENT export; signed service-response feedback and withdrawals. API/browser checks. Official SAHYOG dispatch is an external dependency.
- [x] **M09** Wallet watches and local case change alerts. Scheduler/closed-case/duplicate tests.
- [x] **M10** Query execution API, durable per-job budget across retries, parent preservation and conflict holds. 18 targeted tests and 107-test full regression passed.
- [x] **M11** Updated query action passes real browser execution, mobile overflow, PDF inspection and bundle replay; investigator/reviewer/bridge workflows also passed again against the final build. Evidence: four `tmp/browser/*results.json` files, screenshots and two rendered query-report pages. Zero browser page errors.
- [x] **M12** Deliver requirement mapping, concise USP/demo guide, accurate status register and working local app URL. Evidence: `SIH_MVP_GUIDE.md`, `docs/status.md`, `README.md` and the running localhost application. Full production backlog is explicitly deferred.

**Required honesty at the demo:** training data is synthetic; six adapters are implemented; one live Bitcoin sample/refresh and evidence replay are verified, while broader live coverage and ownership validation remain outstanding; numerical confidence calibration, general cluster inference, arbitrary swaps/bridges and production scaling are deferred; official SAHYOG is not connected. No real disclosure request has been sent and no funds have been frozen.

See [SIH MVP guide and requirement mapping](SIH_MVP_GUIDE.md) for the presentation script and exact scope.

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
