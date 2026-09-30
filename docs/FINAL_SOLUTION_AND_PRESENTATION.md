# TraceSetu: complete solution and SIH presentation brief

Edition: 25 September 2026. This is the consolidated **intended final product**, followed by its current implementation boundary. The complete original 41-section research report remains embedded in the single project skill; this document does not replace or shorten that report. Do not describe the proposed deployment below as already running.

## Identity and central promise

**Name:** TraceSetu. **Sanskrit-derived styling:** Trace + Setu / सेतु. **Pronunciation guide:** Trace SAY-too. **Tagline:** Follow the funds. Find the receiving service.

The user selected **TraceSetu** on 25 September 2026: English *trace* plus Sanskrit *setu* (bridge). It represents the bridge from a transaction trail to supported investigative action. No trademark availability or global uniqueness is claimed. Former names were Vittanvaya and Custody Atlas. The earlier etymology used [vitta](https://www.sanskrit-lexicon.uni-koeln.de/scans/MWScan/MWScanpdf/mw0965-vitta.pdf) and [anvaya](https://www.sanskrit-lexicon.uni-koeln.de/scans/MW72Scan/MW72Scanpdf/pg_0047.pdf); those links are historical naming research, not the derivation of TraceSetu. VittaSutra was rejected after finding [an existing project](https://devpost.com/software/vittasutra). Current app, deck and deliverables use TraceSetu; signed historical evidence, internal schemas, ATLAS_ configuration keys and the stable custody-atlas-sih skill identifier preserve compatibility.

**One sentence:** TraceSetu turns an unknown wallet into a bounded, evidence-backed map of the first reachable custodial services, explains what could change that answer, and prepares the correct reviewed next action.

**Beneficiaries:** investigators and supervisors handling cybercrime cases; technical analysts who need reproducibility; agency administrators managing data access; legal/request teams selecting the correct entity and channel. The user supplied MHA / I4C, CIS Division, SIH Software / Blockchain & Cybersecurity context. No official affiliation, approval, problem ID or exclusive government deployment is asserted.

## The complete end-to-end product we intend to deliver

1. **Authorised intake.** SAHYOG, another authorised case system or the standalone investigator workspace submits a case reference, chain-qualified wallet, relevant time window, optional incident transaction, investigation purpose and query budget. Identity, role and case access are checked before work begins. Address validation and seed semantics prevent mixing an address-wide neighbourhood search with tracing a specific incident payment.
2. **Capability and cost preflight.** The engine snapshots the installed provider capabilities, licensed label scope, finality policy and available budget. It states what can be fetched on this chain, which token/history/trace endpoints are supported, and which attribution sources are missing. Unknown coverage remains visible.
3. **Evidence acquisition.** Durable workers query permitted public or contracted chain APIs, archive responses with source/time/hash metadata, reconcile pagination and receipts and checkpoint work. Shared public-chain evidence may be cached; private case annotations never enter another tenant's case. Provider errors, quota limits and partial history appear in the output.
4. **Canonical multichain normalisation.** Convert observations into chain-qualified events without rounding native units. Preserve Bitcoin outpoints, EVM transaction/log/trace positions, Tron event identity, and Solana instruction/account semantics. Exclude failed or non-final events from confirmed conclusions. Reorganisations append corrected observations and invalidate affected conclusions; they do not silently rewrite old reports.
5. **Attribution resolution.** Keep independent assertions for address ownership, deposit/hot-wallet role, cluster membership and service/legal entity mapping. Each assertion carries provenance, scope, validity, licensing and review state. A sweep pattern can suggest a cluster but cannot establish ownership by itself. Conflicts remain reviewable; an unknown label is not a self-custody classification.
6. **First-custody frontier.** Search each branch in causal transaction order within explicit depth, time, graph-size and request limits. Stop each branch at its first supported custodial service. Do not follow an exchange's later withdrawals as if they were the same customer's funds. Preserve equal-depth alternatives, unresolved branches and the scope of the nearestness claim. An exchange, custodian, mixer, bridge or swap service is classified according to evidence, not a name guessed from activity.
7. **Supported cross-chain continuation.** Use protocol-specific proof verification to relate source and destination events. Preserve bridge fees, asset mappings and source/destination event order. A matching amount and time is a hypothesis, not a certified link. Stop at unknown bridges, mixers or ambiguous swap services and record the missing proof needed to continue. Add protocols through independent certification suites, not a universal bridge checkbox.
8. **Amount and risk interpretation.** Display observed transfer amounts separately from conservative incident-attributable bounds. Never sum overlapping path upper bounds into a recovered balance. Keep attribution strength, history completeness, fund continuity and risk reasons distinct. Explainable indicators may flag obfuscation, rapid dispersal or exposure to a sourced high-risk entity. An indicator is an investigative lead, not a finding of guilt. Calibrated probability scores require a suitable independent labelled corpus; until then use explicit evidence grades and abstention.
9. **Decision-oriented workspace.** Show the custody frontier, graph, supporting paths, evidence drawer, coverage gaps and request destination. The investigator can challenge a source or assumption and see which conclusions disappear. The planner ranks the next permitted evidence requests under a budget, protects unresolved nearer branches and records why a query was selected. Execute only the reviewed selected scopes in a new version of the analysis.
10. **Evidence and reporting.** Generate a human-readable report, structured case export, transfer table and signed manifest of raw artifacts, snapshot and analysis versions. A separate verifier checks file integrity and deterministic replay. A signature proves integrity relative to the signer; it does not prove a label is true, the signer is an exchange or a court will admit the report.
11. **Correctly routed, reviewed action.** Resolve the evidenced service to an agency-maintained legal entity and verified delivery channel. Build a minimal disclosure or asset-preservation/freezing request package with legal basis, scope, hashes and immutable recipient version. A separate authorised reviewer approves the exact payload. The official integration adapter sends only when credentials, institutional approval and API contracts exist. Record acknowledgements, retries and service response status. Blockchain analysis itself cannot freeze funds.
12. **Governed feedback.** Authenticated, request-bound service responses may support narrowly scoped new assertions after independent review. Preserve signature/key provenance, case and time restrictions, contradictory responses and withdrawals. A valid digital signature without a trusted identity binding is insufficient. Corrections create new analysis versions and invalidate stale requests where necessary.
13. **Monitoring and alerts.** Authorised watches rescan defined subjects from durable checkpoints, deduplicate alerts and indicate why a newly observed custody event or risk signal matters. The full product will support reliable scheduling, delivery policies and operational escalation. It will not silently imply continuous monitoring after a local process has stopped.
14. **Operational closure.** The case records actions taken, service receipts, limitations and reviewer decisions. Retention/deletion respects legal holds and agency policy. Administrators observe provider failures, queue health, budget use, restore readiness and access-control violations without putting sensitive case contents into logs.

## Complete system architecture and technology choices

```text
Authorised SAHYOG / external intake             Investigator + reviewer dashboard
                 \                              /
                Authenticated API, tenant/case policy, validated scope
                                      |
                       Case / job / evidence orchestration
                                      |
                 Budgeted acquisition and attribution workers
                 /                    |                    \
       Chain history APIs      Licensed intelligence     Reviewed agency labels
                 \                    |                    /
                Canonical events + versioned assertions + coverage
                                      |
          Temporal custody-frontier search + certified bridge decoders
                                      |
       Candidates / limits / source challenge / next-query recommendations
                         /                          \
          Reproducible signed reports        Request drafting and review
                                                      |
                                      Official integration outbox / receipts
                                                      |
                                      Verified VASP / SAHYOG destination
```

**Current executable profile:** React, TypeScript, Vite, Cytoscape, Lucide; Python, FastAPI, Pydantic and SQLAlchemy; SQLite WAL; local content-addressed evidence; in-process durable-job runner with persisted state; ReportLab and Ed25519-signed ZIP evidence. The skill contains exact inspected versions and contracts. This is a functioning independent local application, not a hosted agency production environment.

**Full deployment profile, proposed:** retain the React/FastAPI domain layer; move authoritative records to PostgreSQL with validated migrations and tenant isolation; use Temporal for durable asynchronous activities; store evidence in encrypted S3-compatible storage with validated retention and legal-hold support; use a rebuildable Neo4j graph projection if benchmarking justifies it. A transactional outbox keeps projection and dispatch consistent with authoritative state. Add agency OIDC/SSO, MFA, workload identities, managed secrets and independent signing-key custody. Instrument using OpenTelemetry, Prometheus/Grafana and redacted structured logs. Containerise deployment; validate backup restoration, failover, patching and alert ownership. Kafka/ClickHouse are optional scale-driven additions, not dependencies already present.

**Separation of trust:** chain providers provide observations; intelligence vendors provide assertions; the agency directory supplies reviewed legal-entity/channel mappings; reviewers authorise consequential action. Acquisition workers do not hold dispatch credentials. An LLM is not the source of transaction facts or ownership claims. An optional drafting assistant could explain already authorised evidence in future, with references and human review.

**Authoritative data:** tenant/user/grant, case/subject, run/checkpoint/budget, block/transaction/event, UTXO/spend, source artifact, assertion/version, cluster membership, bridge link, candidate/path, coverage, plan/execution, report/manifest, recipient/version, request/approval/receipt, watch/alert, audit. Record valid time separately from retrieval time. Native amounts travel as integer/decimal strings. A derived graph can be rebuilt; original evidence cannot be reconstructed merely from a graph screenshot.

**Scaling behaviour:** limit work per case, paginate and checkpoint acquisitions, cache permitted public observations, share immutable artifacts by content hash, partition large event stores, apply per-provider quotas and fair scheduling across tenants, and separate heavy report jobs from intake. Measure throughput before increasing infrastructure. No current benchmark establishes high-volume production readiness.

## Six-chain and service coverage: intended versus built

| Area | Full product commitment | Verified local MVP boundary |
|---|---|---|
| Bitcoin | Certified UTXO history, spend and attribution coverage; explicit CoinJoin/change uncertainty | Read-only Esplora adapter and parser/engine tests; one bounded live Bitcoin sample, browser refresh, raw hash and signed replay verified. Full-chain/ownership certification outstanding |
| Ethereum / BNB Chain / Polygon | Independently certified account, token, receipt and supported internal-trace coverage on each network | Etherscan-family read-only adapters and reconciliation tests; no claimed complete live history |
| Tron | Certified native/TRC20 event history, finality and pagination | TronGrid adapter and tests; live acquisition unvalidated |
| Solana | Certified signature/instruction/token-account ownership interpretation and supported program decoders | RPC adapter and parser tests; incomplete/unsupported instruction cases remain explicit |
| Other chains | Add adapter, capability manifest, decoder/finality tests and evaluation before claiming support | Not presently certified or promised as universal coverage |
| Exchanges / custodians / deposit and hot wallets | Licensed or independently confirmed assertions and reversible entity/role/cluster management | Assertion types and governed review; examples are synthetic; no broad ownership database |
| Mixers / tumblers | Sourced service detection and clear uncertainty stop; no promised deanonymisation | Tagged stops and ambiguity handling; no universal detector |
| DeFi bridges / cross-chain swaps | Protocol-certified event linkage with fee and asset accounting; unresolved boundary otherwise | CCTP V2 USDC Ethereum–Polygon proof pipeline exercised synthetically; not general swap tracing |
| High-risk ecosystems / typologies | Licensed/official source ingestion, explainable rules, triaged alerts and independent quality checks | Risk/coverage presentation and local watches; no broad ransomware/darknet/terrorism intelligence feed |
| SAHYOG / VASP action | Official authenticated intake, reviewed routing, dispatch, receipts and escalation | Standalone case API and reviewed exports; NOT_CONNECTED / NOT_SENT |

## What differentiates the solution

The defensible positioning is **decision-grade custody attribution under uncertainty and budget**, demonstrated through five connected mechanisms. It is not a claim that no existing vendor has comparable functionality.

1. **Bounded custody frontier with an inspectable nearestness certificate.** The output tells an investigator which first custodial boundaries are supported and where incomplete nearer branches could change the answer. Acceptance: preserve equal-depth candidates; stop at the first custody boundary; a missing nearer branch prevents a global-nearest claim.
2. **Challenge the evidence, not just view a graph.** Disable a supporting source as a counterfactual and show which paths survive. Acceptance: removing the sole assertion removes its candidate; independent surviving evidence remains visible; the original analysis is retained.
3. **Spend the next query where it can resolve uncertainty.** Use request budgets, endpoint costs, cache and durable reservations to choose and execute selected evidence queries. Acceptance: no duplicate execution, no overspend across retries, no undisclosed fallback, preserve parent evidence. The training expansion deliberately uses zero provider HTTP calls; it is not a measured live API savings claim.
4. **Evidence that another reviewer can replay.** Export raw references, snapshot, result, versioned contracts and signed manifest; verify integrity and deterministic replay separately from factual truth. Acceptance: tampering fails verification and the unchanged bundle reproduces the supported result.
5. **Reviewed feedback improves future work without erasing provenance.** Request-bound service confirmation can become an assertion only after identity, signature, scope and review checks. Acceptance: wrong signer/scope/request, conflicting evidence or a withdrawn assertion cannot silently establish ownership.

**Why this may be efficient:** bounded search avoids unrestricted graph expansion; stopping at custody avoids meaningless exchange-ledger traversal; cache prevents repeat permitted acquisitions; budget selection prioritises unresolved nearer branches; immutable reuse avoids repeating the entire investigation after each addition. These are implemented or proposed mechanisms, not quantified superiority. Evaluate against depth-first/manual/breadth-first baselines on the same permitted corpus; report accuracy with coverage, abstention, cost and investigator time.

**Practical cost-saving choices:** start independently of SAHYOG access; use allowed public chain APIs and verified user imports; reserve paid labels for the unknown assertions they actually resolve; test deterministic edge cases offline; use open-source software where its licence and operational features fit. Do not bypass API restrictions or relabel synthetic data as a clever live workaround.

## Explicit outputs for an investigator

An answer should include case/run IDs, seed and time range, acquisition limits, provider/source status, candidate entity and wallet role, receiving chain/address, chronological supporting transfers, first-custody hop position, relevant bridge proof, observed amounts and separate attribution bounds, source conflicts, coverage gaps, risk reasons, nearestness scope, next suggested queries, reviewer notes and export hashes. If evidence is missing, return a useful unresolved result with the missing source or query, not an exchange guessed to make the demo look complete.

Example: an invented suspect sends to an intermediary, which sends to a synthetically labelled deposit address. The system shows Example Exchange Alpha at the first supported custody boundary. Challenging its sole source makes that attribution unresolved. A separate unresolved branch can justify another budgeted query. These fixture results demonstrate the workflow, not ownership of a real exchange address.

## Validation and complete-product release gates

The local MVP baseline has 107 passing backend tests and four passing browser workflows, recorded before the branding/video change. Rebranding is a presentation change; record its own build/browser/report checks. These counts establish tested cases, not general-world accuracy. The twelve local MVP checklist checks and the 95-task full-product backlog have different scopes.

Before calling the full product operational, complete: credentialed six-chain end-to-end checks; licensed entity coverage and redistribution rights; official SAHYOG schema/auth/sandbox/access; reviewed jurisdiction-specific request policy and recipient directory; independent ground truth and held-out evaluation; calibrated confidence only if justified; security assessment and agency identity integration; PostgreSQL migrations and tenant-isolation tests; realistic load/latency/cost tests; restore/failover/retention/reorganisation drills; trained operational ownership and incident response. Avoid invented completion dates, staffing commitments, monetary estimates or accuracy/recovery percentages. The original report contains a historical indicative 24–32-week plan, not a current delivery promise.

## PPT instructions for another AI

Use this section and the current-state sections of SKILL.md to explain the solution. Use the embedded original report for detailed design and citations. Do not turn the historical future-tense architecture into a description of the current demo. Do not invent team members, college, problem ID, government logos, partnerships, market size, customer adoption, benchmark charts or live API results. If the SIH template is provided later, obey its slide count and required fields instead of this optional outline.

**Narrative:** unknown wallet → delay finding the responsible custodian → evidence-backed custody frontier → show limits and challenge → query within a budget → reviewed correct destination → reproducible evidence → scalable proposed integration. The unique emphasis is deciding what an investigator can responsibly do next.

| Suggested slide | Concrete content and visual | Claim status |
|---|---|---|
| 1. Problem and solution | TraceSetu, tagline, exact PS title, user-supplied MHA/I4C context; wallet-to-custody line | Problem supplied; product independent |
| 2. The operational gap | Address ≠ owner ≠ VASP entity ≠ authorised freeze; multi-hop delay | Research-backed reasoning, no invented statistics |
| 3. Complete proposed workflow | The 14-step workflow condensed into intake → evidence → frontier → review → action → feedback | Target design; label integration proposed |
| 4. Differentiation | Five mechanisms above with one concrete acceptance test each | Mechanisms built locally; superiority unmeasured |
| 5. Working MVP | Actual renamed app screenshot/clip: graph, source challenge, query execution, replay | Synthetic training demonstration, visibly labelled |
| 6. Architecture and chain coverage | Actual stack next to proposed production profile; six-chain capability table | Distinguish adapter implementation from live certification |
| 7. Evidence and safeguards | Raw artifacts → manifest → replay; independent review; no false freeze claim | Tested local controls, external identity/access outstanding |
| 8. Feasibility and validation | 107-test baseline; browser workflows; dependency gates; cost-control mechanisms | Test evidence only; no accuracy percentage |
| 9. Impact and next steps | Measure time to supported custodian, correct recipient rate, abstention, provider spend; requested access/evaluation | Intended benefits and measurement plan, not measured outcomes |

**Visual language:** deep navy #132733, teal #087e70, warm amber #E8B469, light neutral #F5F7F9. Use one simple flow per slide; clear source/assumption/unknown badges; actual application screenshots without private credentials. Reserve amber for incomplete coverage and synthetic/proposed caveats. Avoid decorative circuit imagery that takes space from the actual workflow.

**Speaker answers:**

- “Does it identify every wallet?” No. It returns supported candidates or an explicit unresolved result within stated coverage.
- “Can you freeze assets?” The system prepares and routes reviewed requests when official integration exists; the competent service/authority acts. The demo sends nothing.
- “Why not just buy a tracing tool?” This project explores an evidence-first, provider-neutral custody-to-action workflow with source challenge, query budgets and reproducible review; procurement and comparative evaluation remain necessary.
- “Is it connected to SAHYOG?” Not this installation. The connector contract and credentials are an external gate; no official API was invented.
- “Is six-chain support live?” Six read-only adapters are implemented and tested with controlled responses. A bounded public Bitcoin sample and browser refresh worked with real data. Other wallet adapters and broader completeness/attribution certification remain outstanding.
- “What is genuinely working now?” Local authenticated cases, bounded analysis, graph/evidence review, source challenge, budgeted training expansion, governed CCTP proof exercise, signed report bundles/replay and reviewed request/feedback controls.
- “Why no percentage confidence?” Calibrated probabilities require independent ground truth. Honest evidence grades are preferable to unvalidated certainty.

## Text equivalents of the two original research-report figures

The embedded historical report preserves its original `[DIAGRAM:trace]` and `[DIAGRAM:architecture]` insertion markers. These are the complete information content of those vector figures, recorded from `research/build_report.py`, so another AI does not need the PDF to recover the diagrams.

**Historical synthetic token example (gas excluded):** wallet S is the incident seed. S → wallet A (intermediary): 6,000 token units; A → Exchange Beta deposit D2: 5,800 units, two hops from S. S → Exchange Alpha deposit D1: 3,000 units, one hop. S → Service U: 500 units on a dashed unresolved branch. S retains 500; A retains 200. No customer identity is inferred. This 10,000-unit research example is distinct from the current app's native-asset and CCTP fixtures; never describe it as a real transaction or substitute its amounts into the recorded demo.

**Historical proposed architecture figure:** Investigator workspace (case / graph / evidence) → Gateway + case API (identity / permissions) → SAHYOG boundary (approved requests only). Gateway → Durable workflows + workers (fetch / decode / attribute / trace). Workers → Provider gateway (quotas / scoped egress) → External sources (chain facts / intelligence). Workers → PostgreSQL (authoritative records). Workers → Evidence objects (raw bytes / signed manifests). PostgreSQL → Neo4j projection (rebuildable case graph). Figure notes: private case data stays inside the application trust boundary; provider assertions are evidence inputs; dispatch requires separate approval. All infrastructure in this figure is the proposed full deployment, not the current SQLite installation.

## Handover rule

Keep the complete target design, current MVP and external gates together. Preserve all exact requirements and source links in SKILL.md. The video is a concise demonstration and cannot replace the complete specification. A new model must inspect current code before changing it, keep the existing local data and historical evidence compatible, and update the skill/checklists after verified changes.
