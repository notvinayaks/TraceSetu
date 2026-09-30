# TraceSetu — interface review and live-data demonstration

**Current steering (25 September):** the user explicitly requested the real public-case recording, then approved TraceSetu and asked to continue. That authorization supersedes earlier UI-approval holds below. Current delivery and live-case facts are in `docs/TRACESETU_SUBMISSION.md`; older measurements below remain historical evidence.

Historical interface milestone, 25 September 2026. At this stage the user asked for UI confirmation before recording. The later explicit request to record a real public case and approval of TraceSetu superseded that hold. This section preserves the UI verification evidence; section 21 of the complete skill and docs/TRACESETU_SUBMISSION.md govern current delivery.

## What changed

- Replaced the dark sidebar, dark graph, oversized statistics cards and decorative treatments with a restrained investigation desk: off-white surfaces, navy controls, fine borders, a serif wordmark and a light transaction graph.
- Put a concise supported-service answer above the graph. Separate path counts, unresolved branches, source-backed risk signals and scoped nearestness remain available; unknown risk is explicitly unassessed.
- Added working case status filters, search and eight-row pagination. Existing cases are preserved.
- Open wallet and transfer evidence in a side drawer. Technical JSON sits behind disclosures. Case notes collapse to keep the work area readable.
- Added modal focus management, Tab containment, Escape dismissal, focus restoration, visible keyboard focus, current-navigation semantics and notification expiry. Mobile navigation keeps its labels; desktop and 390-pixel mobile views were checked.
- Added a live-acquisition strip with the actual source, recorded retrieval timestamp, observed transfer count and **Refresh live data**. Refresh starts a new immutable live analysis under the existing request/hop bounds and keeps the prior result.
- Corrected a Bitcoin graph bug: spreading transfer data after a transaction-node ID replaced that ID, leaving UTXO edges connected to nonexistent nodes. The node now retains its transaction identity. This surfaced while opening actual public Bitcoin data, not the account-based training graph.

The backend API, attribution rules, evidence contracts, independent-review controls and credentials were not changed for this revision. No production infrastructure was added.

## What actually worked with real data

The public sample is a neutral transaction selected from a recent Bitcoin block, not an allegation about its wallets. A bounded live job in **Bitcoin · live public-data demonstration** fetched confirmed address history through the configured mempool.space Esplora API. Its observed transaction and integer satoshi amounts matched the provider's separately fetched block response. The browser then ran **Refresh live data** successfully, checked a raw response's SHA-256 and exported/replayed a signed live evidence bundle.

- Final browser run: `2026-09-25T06:56:21.267Z`.
- Case: `cas_6f95076b051a4a08893424da110e77f9`.
- Final checked job: `job_b25b935508394e7f85d11b26c0faa579`.
- Result: `COMPLETED_WITH_GAPS`, one observed transfer, one successful HTTP request, zero cache hits, zero custody candidates.
- Observed transfer: **0.00085536 BTC / 85,536 satoshis**. It is an observed transaction output, not a proven allocation of incident funds.
- The hop-bound frontier and missing ownership assertions remain visible. **No service identified yet** is the correct result for this evidence. A public transaction API is not an ownership directory.
- Evidence: `output/ui-review/results.json`, `live-snapshot.json`, `Live_Bitcoin_Evidence.zip`, `06-live-bitcoin.png`, `07-live-transfer-evidence.png`, `08-live-bundle-verified.png`; initial direct-job record in `tmp/live-bitcoin/results.json` and `analysis.json`.

This establishes a successful live Bitcoin sample and an on-demand refresh workflow. It does **not** establish streaming coverage, full Bitcoin completeness, independently validated ownership, six-chain certification, live cross-chain attribution or production readiness. The amount comparison used responses from the same provider and is an implementation consistency check, not independent consensus verification.

Public endpoint probes for mempool.space, Blockstream, TronGrid and Solana returned HTTP 200; the Tron/Solana checks only retrieved a current block/slot. Their full wallet adapters were not certified by those probes. An earlier synchronous Bitcoin probe timed out before subsequent acquisition succeeded, so connectivity still needs preflight before a presentation. Etherscan credentials for Ethereum/BNB/Polygon have not been supplied. Official SAHYOG remains unconnected.

Primary protocol references checked during this revision: [Esplora API specification](https://github.com/Blockstream/esplora/blob/master/API.md), [mempool API documentation](https://mempool.space/docs/api/rest). These explain the public endpoints; the local run records establish what this installation actually did.

## Verification and review checklist

- [x] TypeScript compilation and Vite production build.
- [x] Existing investigator workflow: training trace, budget plan, source challenge, signed evidence download/replay and mobile viewport.
- [x] Existing separate-reviewer workflow: recipient/request review, export, signed feedback and corrections.
- [x] Existing bridge workflow: unreviewed abstention, proof review, reassessment, burn/fee/mint inspection, source challenge, withdrawal and stale-export guard.
- [x] Existing query execution: reviewed immutable plan, bounded synthetic expansion, preserved parent, report export and bundle replay.
- [x] Additional UI browser check: pagination/search/status filters; modal focus/keyboard/Escape; evidence drawer; desktop/mobile overflow; real Bitcoin refresh, response hash and signed live bundle replay. Zero browser page errors.
- [x] Visually inspect sign-in, case register, custody/graph, evidence drawer, live-transfer evidence, live-bundle verification and mobile screenshots.
- [x] Later user direction explicitly authorized the real public-case recording.
- [x] Later authorization received; replacement footage and narration are in the TraceSetu submission workflow, whose final verification is tracked separately.

The previous full backend baseline remains 107 passing tests. It was not rerun for this frontend-only revision; the new evidence is the compiled build and browser checks. The full-product backlog remains 50/95 narrowly verified tasks, with 45 deferred/external tasks. These counts do not describe attribution accuracy or production readiness.

## Historical suggested 2:40 sequence, superseded by the live-case script

| Time | Screen/action | Explain honestly |
|---|---|---|
| 0:00–0:12 | Case register; open the public Bitcoin case | TraceSetu turns a reported wallet into a reviewable investigation. The sample is neutral public data. |
| 0:12–0:37 | Refresh live data; show timestamp, Bitcoin graph and transfer | Actual provider acquisition. Real amounts; unknown ownership remains unknown. If the provider fails, show the failure or use an explicitly dated acquired snapshot. Never relabel it as fresh. |
| 0:37–1:00 | Open the labelled custody training case; inspect first receiving service | Switch visibly to synthetic training to demonstrate ownership assertions and first-custody stopping. |
| 1:00–1:24 | Challenge a source; show changed result; inspect next-query budget | The difference is a defensible answer with visible uncertainty and a practical next evidence action. No unsupported accuracy/cost claim. |
| 1:24–1:43 | Previously independently reviewed training bridge | Ethereum → Polygon burn, fee and mint; narrowly supported CCTP proof rather than guessed cross-chain matching. |
| 1:43–2:06 | Evidence export and successful live bundle verification | Raw responses, exact amounts, hashes and deterministic replay. Verification establishes integrity, not ownership. |
| 2:06–2:30 | Independently reviewed training recipient/request | Correct-recipient matching, separate reviewer and approved payload export. NOT_SENT / NOT_CONNECTED stay visible. |
| 2:30–2:40 | Coverage and closing promise | Six implemented adapters; successful Bitcoin sample; broader live validation and official access remain explicit gates. |

Use a fresh **Open training case** for the source challenge/query section. The newest query-test case may already contain expanded evidence and the newest bridge-test case may have a withdrawn proof; select the intended reviewed demonstration case deliberately, not merely the first row. Ensure reviewers and prepared training requests are ready before recording. Do not expose login passwords in the video.
