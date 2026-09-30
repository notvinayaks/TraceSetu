# TraceSetu — final submission and live-case handover

Current edition: 25 September 2026. This section supersedes older branding and recording holds. The user chose **TraceSetu** and explicitly requested continuation of the PPT correction, actual public-case test, native 4K film (maximum 2:45), matching narration and comprehensive handover. Recording is authorized. External disclosure messages and freezes are not.

## Identity, purpose and limits

TraceSetu joins English **trace** with Sanskrit **setu**, bridge. Say “Trace SAY-too.” Tagline: **Follow the funds. Find the receiving service.** Former names were Vittanvaya and Custody Atlas. No trademark clearance or global uniqueness is claimed.

The current interface, browser title, API product identity, generated reports, help guide, working documentation and final slide deck use TraceSetu. The stable `custody-atlas-sih` skill path, `ATLAS_` settings, session/schema identifiers and older signed bundles preserve compatibility and provenance. Archived filenames containing former names describe historical artifacts, not the current product. Do not modify signed evidence simply to change branding.

The immediate product is the polished local SIH MVP, not the deferred production platform. End users are cybercrime investigators, separately authorized reviewers and local administrators. It helps an officer inspect the first supported custodial boundary per chronological path and the evidence needed before routing an action. It neither identifies beneficial owners from wallet addresses nor guarantees a nearest real exchange.

The practical differentiator is the combination of **first-custody stopping, an inspectable nearestness certificate, source challenges, a budgeted next-query planner and reviewed service feedback**. These have fixture acceptance tests and clear conditions; no world-first, independent accuracy superiority, proven recovery or measured operational speedup is claimed. Multi-chain graphs, case management and reports alone are not novel.

## Slide decision and changes

Final deck: `output/submission/TraceSetu_ANANTHA_SIH2026_SUBMISSION.pptx`.

The second supplied workflow was clearer, but required corrections. The first included an important independent request-review stage. The final deck combines the clearer layout with that review requirement, removes the redundant workflow and contains six slides. The supplied SIH visual style, team ANANTHA, Team ID 170835 and PS ID 26182 are retained as user-supplied metadata, not official endorsement.

- Slide 1: TraceSetu identity and user-supplied submission details.
- Slide 2: reported wallet → acquisition and evidence → bounded custody analysis → independently reviewed action, export and feedback. Candidate wallets are not automatically called deposit wallets. Source roles and validity intervals matter.
- Slide 3: actual stack, chronological/outpoint tracing, categorical evidence grades and explicit CCTP limits. Public prototype/repository URLs have editable placeholders; no public URLs were supplied and localhost is not a public deployment.
- Slide 4: current MVP, 116 backend tests and explicitly synthetic custody screenshot; future deployment and official-integration gates stay separate.
- Slide 5: public context and intended benefits. The ₹1,646 crore figure is the ED's 15 February 2025 BitConnect release. The 35 VASPs figure is a dated 23 July 2025 MHA parliamentary answer, not a present-day total. TraceSetu has no measured recovery amount. Competitor capabilities are not presented as absent merely to manufacture novelty.
- Slide 6: research sources, current role/limits and the previously missing ED reference.

Actual stack: React, TypeScript, Vite, Cytoscape.js, Lucide; Python, FastAPI, Uvicorn, Pydantic, HTTPX; SQLAlchemy, SQLite WAL and a local worker; local SHA-256-addressed evidence objects; ReportLab and cryptography/Ed25519. No LLM attribution engine, running Neo4j, Temporal, production PostgreSQL cluster or deployed SAHYOG connection is implied. Six adapters exist; Bitcoin has a bounded live sample. Broad live checks of the other chains are pending. CCTP V2 USDC Ethereum–Polygon verification is synthetically tested; live proof validation remains pending.

## Real public case and evidence

Case: **WannaCry ransomware, public historical Bitcoin study**. CERT-In's published alert, page 4, displays `13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94`. The source establishes why this starting address is relevant; it is not proof of downstream ownership, an active police case, or a verified VASP label.

Source PDF SHA-256: `dc8c96c2dd908fbfa9cf40e561d9c8c598f1c4b1d5639c55a6c6bcb5b47d3389`. A preserved copy is `output/submission/live-case/CERT-In_WannaCry_Alert.pdf`. Page 4 was visually checked. The investigation period is 3 August 2017 UTC, one hop. A live query means data is fetched now about historical transactions, not that the incident is current or that a continuous blockchain stream exists.

Actual successful acquisition returned these two transactions and three outputs:

| Transaction | Output | Receiving address | Exact satoshis | BTC |
|---|---:|---|---:|---:|
| `a028bb2d4c795cb8a8fd2f03285934fba8747fa84296fb7711dcda179b21cc4c` | 0 | `1ARirZgU4q61sSjVK2iB8BEYC5w2B8ZnE9` | 10287428 | 0.10287428 |
| Same transaction | 1 | `1H68h8qsVkMUgY8khcdFpbHV22cCnC74dk` | 956285137 | 9.56285137 |
| `8def6458a46234ab0e040602e7852ff5cf58650f3f1102803b1d4bca4cc293a1` | 0 | `1M1CfXLynR6vqbjwTqSiiLRVDQZEXHHJbb` | 1005800019 | 10.05800019 |

**Zero supported VASP candidates were found.** Coverage and hop limits remain visible. The tool does not manufacture a label, an attribution probability or an apparently successful freeze. Its risk classifier has no imported ransomware assertion in this case; the public-source association appears in the investigator's case notes. Unknown risk remains unassessed. Amounts are observed outputs, not recoverable balances or proven incident allocation.

Evidence location: `output/submission/live-case/`. `verification.json` records the latest checked job, scope and counts. `analysis.json`, `snapshot.json`, `TraceSetu_WannaCry_Report.pdf` and `TraceSetu_WannaCry_Evidence.zip` preserve the reviewed run. The original `run.json` preserves initial setup provenance; a later filmed query can have a different job ID. Never confuse inherited transfers in a child analysis with freshly fetched responses; acquisition metrics state their scope.

## Explicit Bitcoin provider alternative and regression evidence

Public Esplora endpoints experienced timeouts from this installation. A selectable BlockCypher adapter was added in `backend/vasp_app/blockcypher.py`; `ATLAS_BITCOIN_PROVIDER=blockcypher` chooses it explicitly. Default configuration remains Esplora. No paywall, authentication, rate-limit or licensing control was bypassed, and no silent fallback was added.

The adapter uses the documented full-address endpoint, 50-row block-height pagination and `txlimit=1000` so large input sets are not silently truncated. It checks confirmations locally, exact integer satoshis, timestamps, address identity, double-spend status and full input/output lengths. It retains input outpoints and ledger position. Unsupported multi-address scripts create partial coverage, not invented links. Budget/rate/response-size limits, raw hashing, checkpoints and cache accounting use the existing acquisition engine.

A live check found that combining `confirmations=1` with `before` repeatedly returned the first page. Omitting that optional server filter while retaining local confirmation checks advanced the cursor. A regression assertion covers the parameter combination. A stalled cursor still fails closed and retains checkpointed events. If the provider omits its history-completion signal, the adapter retains returned transactions but marks coverage partial; absence of a flag is never evidence of complete history. Fresh queries also encountered public-provider read timeouts; these are recorded as incomplete acquisition. Local timeout was increased to 60 seconds for the demo, not masked as success.

The full backend suite passed **116 tests** (historical 107 plus 9 BlockCypher contract cases), recorded in `tmp/tracesetu-backend-junit.xml`. After the pagination-parameter and missing-completion-signal adjustments, all nine provider tests passed, including the added missing-signal regression. The report/bundle/replay/tamper workflow test also passed after replacing a missing-hop report value with “not established.” TypeScript/Vite production build passed following the rename and the follow-up-query scroll correction. Starting a selected-query execution now returns the viewport to the running-job status, avoiding an off-screen progress panel when the prior result disappears. Tests are correctness checks, not accuracy or real-world ownership benchmarks.

## Recording and presenter's claims

Capture: `scripts/record_live_walkthrough.cjs`; rendering: `scripts/render_live_walkthrough.py`. The final file is `output/submission/TraceSetu_Live_Case_4K.mp4`, with actual 3840×2160 Edge frames, an enlarged cursor, click ripples, smooth click-centred zooms and eight timed chapters totaling 160 seconds. The separate narration is `output/submission/TraceSetu_Narration_Script.md`. A silent file is intentional; the user requested a script to speak alongside it. Delivery completion is recorded only after the final encoded file passes decode, playback and visual verification.

The recording demonstrates real acquisition, observed trace, evidence rows, the no-attribution result, certificate, budgeted follow-up, signed export/replay and the conditions for request preparation. Provider waiting time is condensed; it is not a performance benchmark. The recorded case does not demonstrate a live cross-chain route, actual service response, paid intelligence or an externally sent notice. The deck's synthetic custody example is a separate labelled test, never evidence for this ransomware case.

## Additional verified primary references

- [CERT-In WannaCry alert](https://www.csk.gov.in/documents/WannacryWannaCryptRansomware_CRITICAL_ALERT_CERT-In.pdf): public ransomware source and the seed address on page 4; no downstream VASP attribution.
- [MyCERT WannaCry advisory](https://mycert.org.my/portal/advisories?id=fb834148-452a-44d2-858b-7f5c64611d22&page=84&per-page=10): historical technical incident context.
- [BlockCypher full-address API](https://www.blockcypher.com/dev/bitcoin/#address-full-endpoint): provider pagination and transaction-array contract; not a wallet ownership database.
- [Esplora API](https://github.com/Blockstream/esplora/blob/master/API.md): original Bitcoin adapter contract; network reachability can vary.
- [ED BitConnect release, 15 February 2025](https://enforcementdirectorate.gov.in/sites/default/files/latestnews/Press%20Release-Search-%20Bitconnect-15.02.2025.pdf): supports the dated seizure context in the deck, not TraceSetu's impact.
- [ED annual report 2024–25](https://www.enforcementdirectorate.gov.in/media/5y2bfhhj/annual_report_24-25.pdf): supporting official context.
- [MHA Rajya Sabha Q.399, 23 July 2025](https://www.mha.gov.in/MHA1/Par2017/pdfs/par2025-pdfs/RS23072025/399.pdf): dated SAHYOG onboarding context, not evidence of access for this prototype.
- [Chainalysis Reactor](https://www.chainalysis.com/product/reactor/): public competitor features; no unsupported exclusivity claim.

The original exact problem statement, 30 requirement mappings, full 41-section research report, all original research references, the complete intended production solution and deferred backlog remain in the complete skill. Current external gates still include official SAHYOG access, licensed/verified labels, independent field evaluation, approved service recipients and production security/scale validation.

## Exact final slide text for a future presentation agent

The following is extracted from the final editable deck, in object order. Layout coordinates, logos and formatting stay in the PPTX. It is the current submission wording, not the full intended production scope.

### Submission slide 1

TRACESETU
SMART INDIA HACKATHON 2026
Blockchain investigation with evidence at every step
Problem Statement ID: 26182
Problem Statement Title
Automated Attribution of Unknown Cryptocurrency Wallets to Nearest Virtual Asset Service Providers (VASPs) through Blockchain Intelligence APIs
Theme: Blockchain & Cybersecurity
PS Category: Software
Team ID: 170835
Team Name: ANANTHA

### Submission slide 2

IDEA & SOLUTION
TraceSetu helps officers trace a reported wallet to supported receiving services and inspect the evidence before action.
Every result shows its sources,
search limits and unresolved gaps.
FIRST CUSTODY
Stop each branch at the first
supported exchange or custodian.
NEARESTNESS CERTIFICATE
Show which gaps can hide
a nearer receiving service.
SOURCE CHALLENGE
Remove a disputed source and
recompute without losing history.
BUDGETED ACQUISITION
Prioritise nearer missing evidence.
Reserve API calls before dispatch.
REVIEWED FEEDBACK
Review an authenticated service
reply before promoting its claim.
SYSTEM WORKFLOW: WALLET TO REVIEWED ACTION
CASE INPUTS
ACQUISITION AND EVIDENCE SNAPSHOT
CASE SCOPE
Wallet + blockchain
Time and asset window
Case ID + query limits
1  ACQUIRE
Bitcoin: Esplora / BlockCypher
EVM: Etherscan V2
TronGrid / Solana RPC
2  VALIDATE & ORDER
Exact units + ledger order
Bitcoin outpoint links
Status / time / content hash
3  ENRICH EVIDENCE
Source-backed service labels
Role + period of validity
CCTP proof where supported
Worker: reserve calls, cache replies, save checkpoints.
CHAIN ADAPTERS
Bitcoin
Ethereum / BNB Chain
Polygon
Tron / Solana
Bitcoin sample verified.
Other chains: live checks
and access pending.
CUSTODY ATTRIBUTION ENGINE
4  FIND FIRST CUSTODY
Chronological paths
First custody per branch
Keep unresolved gaps
5  CHECK EVIDENCE
Nearestness within snapshot
Remove source + recompute
Source grade + separate risk
6  RETURN RESULTS
VASP candidates + wallets
Paths + evidence gaps
Next query to run
HUMAN REVIEW, EXPORT AND FEEDBACK
7  REVIEW ACTION
Verify recipient + request
Independent review
8  EXPORT & VERIFY
PDF + signed ZIP
Request JSON: NOT_SENT
9  REVIEW FEEDBACK
Import scoped signed reply
Review before using its labels
CASE STORAGE
SQLite WAL / SQLAlchemy
Evidence hashes + audit log
Official SAHYOG access pending. Request export does not send a notice.
TRACESETU
2
ANANTHA
@SIH Idea submission - Template

### Submission slide 3

Implementation flow
How attribution works
Technology stack
Wallet + chain + time window
Acquire, validate and normalise
Transfer
paths
Service
assertions
Bridge
proofs
Chronological first-custody search
Candidates + certificate + gaps
1
Causal transaction paths
Order by ledger position. Bitcoin continuation
must spend the preceding outpoint.
2
Source-qualified service labels
Bind entity, chain, wallet role and validity
interval to inspectable source evidence.
3
First-custody termination
Keep the first custodian on every branch.
Do not infer unrelated exchange withdrawals.
4
Scoped nearestness
A shallower unresolved branch limits the
answer within the acquired graph.
5
Confidence and risk separation
Categorical evidence grades, not probabilities.
Risk reasons remain separate from attribution.
6
Scoped cross-chain verification
CCTP V2 USDC: Ethereum–Polygon only.
Synthetic tests passed; live proof pending.
PROTOTYPE:  [paste public URL]
TECHNICAL APPROACH
3
INTERFACE & GRAPH
React
TypeScript
Vite
Cytoscape.js
Lucide
API & VALIDATION
Python
FastAPI
Uvicorn
Pydantic
HTTPX
STORAGE & EVIDENCE
SQLite WAL
SQLAlchemy
ReportLab
cryptography
Ethereum tools
TESTING & BUILD
pytest
Playwright
Ruff
Prettier
pnpm
LOCAL RUNTIME
EVIDENCE STANDARDS
Node.js
Ed25519
SHA-256
Python worker + SQLite
REPOSITORY:  [paste repository URL]
ANANTHA
@SIH Idea submission - Template

### Submission slide 4

FEASIBILITY ANALYSIS
CURRENT PROTOTYPE
VIABILITY & CONTROLS
Actual prototype / labelled synthetic custody exercise
Risk
Control
Stale labels
Source challenge and independent review
History / quota gaps
Explicit stops, checkpoints and a hard cap
Official integration
Pending: approved SAHYOG contract
Agency operations
Future: agency identity and security validation
Staged adoption
1  Agency pilot
Verified labels, approved recipients and
independent first-service evaluation.
2  Validated scale-up
Agency identity, storage and orchestration
after security, load and restore testing.
FEASIBILITY AND VIABILITY
4
TECHNICAL FEASIBILITY
Working local MVP
React / FastAPI case workspace.
Causal tracing, PDF reports and replay.
Six chain adapter parsers implemented.
116 backend tests passed.
Live data alone does not establish ownership.
OPERATIONAL VIABILITY
Review remains with officers
Investigators inspect paths and sources.
An independent reviewer approves requests.
SAHYOG delivery needs approved access.
Pilot requires licensed labels, known recipients
and independent first-VASP ground truth.
COST & DEPLOYMENT
Open-source core, explicit costs
API quotas and licensed labels drive cost.
Cache responses and cap each acquisition.
Current: SQLite and local files.
Agency deployment remains future work.
Security, scale and restore validation required.
ANANTHA
@SIH Idea submission - Template

### Submission slide 5

WHY THIS PROBLEM MATTERS
Public context and the prototype’s contribution
₹1,646 cr
Crypto seized in a fraud case [9]
ED reported a ₹1,646 crore crypto seizure
in the BitConnect fraud investigation.
Official release, 15 February 2025.
First custody
A bounded decision for officers
Show the first supported receiving service
on each path, with sources and gaps.
Unknown wallets remain unknown.
35 VASPs
Onboarded on SAHYOG [6]
Official parliamentary reply, 23 July 2025.
A service network for agency coordination.
Access and integration still need approval.
HOW TRACESETU CAN SUPPORT INVESTIGATORS
Less tracing effort
Automate the path to a
supported receiving VASP.
Support asset action
Prepare evidence for lawful
disclosure or freezing requests.
Expose uncertainty
Surface gaps and disputed
labels before recipient approval.
Verifiable handoff
Share signed case evidence
with deterministic replay.
EXISTING APPROACHES AND TRACESETU’S CONTRIBUTION
Dimension
Explorer + SAHYOG workflow
Chainalysis Reactor [8]
TraceSetu MVP
Tracing
Officer follows transfers
Automated graph / entity tracing
First custody on each supported path
Evidence
Manual case assembly
Entity intelligence and reports
Source challenge + evidence certificate
Handoff
Officer selects recipient
Case investigation tooling
Reviewed export; SAHYOG API proposed
Intended benefits require operational evaluation. TraceSetu has no validated recovery amount or official SAHYOG connection.
IMPACT AND BENEFITS
5
ANANTHA
@SIH Idea submission - Template

### Submission slide 6

Technology / research
Research insight
Role in TraceSetu
Paper / primary reference
[1] Bitcoin service
attribution
Shared-control heuristics connect
address activity with service evidence.
Design basis for sourced assertions.
Ownership remains evidence-dependent.
Meiklejohn et al., IMC 2013
A Fistful of Bitcoins
doi.org/10.1145/2504730.2504747
[2] Ethereum address
clustering
Deposit-address patterns are
specific to account-based chains.
Guides chain-specific label caution.
MVP does not implement this clustering.
Victor, Financial Cryptography 2020
Address Clustering Heuristics for Ethereum
Paper: fc20.ifca.ai/preproceedings/31.pdf
[3] Blockchain graph
analysis
BlockSci describes specialised
transaction data structures and analysis.
Performance reference for future
scaling and baseline evaluation.
Kalodner et al., USENIX Security 2020
BlockSci: Design and applications
Paper: usenix.org/system/files/sec20-kalodner.pdf
[4] Cross-chain
protocol evidence
CCTP links a USDC burn and mint
through a message and attestation.
Scoped V2 Ethereum–Polygon verifier.
Synthetic proof tests in the MVP.
Circle, CCTP documentation
Messages, attestations and protocol flow
developers.circle.com/cctp
[5] Signed, replayable
evidence
Ed25519 authenticates signed bytes.
Hashes detect changed artifacts.
Signed manifest + deterministic replay.
Integrity does not establish ownership.
Josefsson & Liusvaara, RFC 8032 (2017)
Edwards-Curve Digital Signature Algorithm
rfc-editor.org/rfc/rfc8032
PRIMARY SOURCES AND IMPLEMENTATION REFERENCES
[6] MHA / SAHYOG, Q.399 (2025)
[7] Esplora API
[8] Chainalysis Reactor
RESEARCH  AND REFERENCES
6
[9] ED: BitConnect seizure, 15 February 2025
ANANTHA
@SIH Idea submission - Template

## Final live-case verification record

```json
{
  "case_id": "cas_59ba98ec804c452c875fe72d4b07ac53",
  "reference": "PUBLIC-WANNACRY-20260925-192816",
  "job_id": "job_b45be3fd2f6a4bf49992e6eadb0f2083",
  "recorded_parent_job_id": "job_48e35ef47d304dd3bde6099ff7cbfb0e",
  "spec": {
    "chain": "bitcoin",
    "address": "13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94",
    "start": 1501718400,
    "end": 1501804740,
    "max_hops": 1,
    "max_states": 2000,
    "max_requests": 2,
    "asset": null,
    "minimum_amount": "0"
  },
  "source_url": "https://www.csk.gov.in/documents/WannacryWannaCryptRansomware_CRITICAL_ALERT_CERT-In.pdf",
  "source_pdf_sha256": "dc8c96c2dd908fbfa9cf40e561d9c8c598f1c4b1d5639c55a6c6bcb5b47d3389",
  "status": "COMPLETED_WITH_GAPS",
  "event_count": 3,
  "candidate_count": 0,
  "metrics": {
    "attempted_http_requests": 1,
    "successful_http_responses": 1,
    "within_job_cache_hits": 0,
    "request_cap": 4,
    "billing_units": "UNKNOWN",
    "scope": "Durable request reservations across this execution's recovery attempts; a crash may consume an undispatched slot. Parent evidence is not counted as new acquisition.",
    "request_count_kind": "reserved_attempt_slots"
  },
  "passed": true
}
```

Independent bundle verification:

```json
{
  "integrity": "valid",
  "replay": "matched",
  "signer_sha256": "e6db48586af15965abd7a79df9fcb10f2b48743d6c0c8780d929f8ca9be42c22",
  "identity_trusted": false,
  "mode": "live",
  "files": 14
}
```

## Verified final delivery

- Final deck: `output/submission/TraceSetu_ANANTHA_SIH2026_SUBMISSION.pptx`, six slides; native PowerPoint rendering and text/integrity checks passed. SHA-256: `a37d8f1cefdf64ca7f58919792626e788f15fe967b643bf257c9acf6d38e040c`.
- Final video: `output/submission/TraceSetu_Live_Case_4K.mp4`, **160 seconds**, **3840×2160**, **25 fps**, H.264, **45,279,390 bytes**, silent with a 334-word synchronized narration script. It has eight chapters, a visible cursor, click ripples and 15 smooth click zooms.
- Video SHA-256: `27b377669f15506df1c43333c607df8840b21e59e8c075c8f405aa9b44181671`. Full decode passed. Edge playback advanced without media errors and seeking to 150 seconds passed. Final chapter views were inspected, including the corrected visible processing state.
- Final filmed query: `job_b45be3fd2f6a4bf49992e6eadb0f2083`; parent `job_48e35ef47d304dd3bde6099ff7cbfb0e`. One successful fresh HTTP response under a four-request execution cap; three observed outputs, zero supported custody candidates. The evidence bundle contains 14 checked files and independently replays successfully. Local signer identity remains untrusted unless separately verified.
- Handover: `output/TraceSetu_COMPLETE_SKILL.md`, identical to the canonical and installed `custody-atlas-sih/SKILL.md`. The stable discovery alias is intentional. Current UI, report and help branding are TraceSetu; historical originals remain archived.
- Main app health returned `status=ok`, `product=TraceSetu`, `sahyog=not connected`. The app stays available at `http://127.0.0.1:8787/`.

All requested local submission artifacts are complete. Public prototype/repository URLs remain editable placeholders because no public URLs were supplied. Production infrastructure, official access and independent real-world VASP-attribution evaluation remain deferred/external requirements, not completed submission work.
