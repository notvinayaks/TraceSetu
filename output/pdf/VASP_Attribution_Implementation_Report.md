# Automated VASP Attribution

Research and implementation report | 24 September 2026 | v1.0

# 01 | Executive decision

## What should be built

Build an independent, API-first blockchain investigation platform for the Ministry of Home Affairs / Indian Cyber Crime Coordination Centre (I4C) problem supplied by the user. The platform accepts an address and investigation scope, reconstructs verifiable transaction paths, identifies the first supported custodial service on each path, and prepares evidence and a reviewed request-routing recommendation. SAHYOG is an integration destination, not a prerequisite for the independent analysis engine.

The recommended design combines public or contracted blockchain history with licensed attribution intelligence and an agency-maintained VASP directory. An open-data installation remains useful, but cannot honestly promise the same coverage of private exchange deposit addresses. A fully functional release must expose those differences rather than silently substituting fabricated labels.

## The product promise

Given a supported network, address, time window and optional originating transaction, return the nearest observed VASP candidates, their receiving addresses, complete supporting paths, evidence provenance, uncertainty, amount-allocation assumptions, and a verified route for the responsible investigator. Return an explicit unresolved or partial result when evidence is insufficient. Never convert a vendor risk score into proof of ownership or criminality.

| Decision | Recommended position |
| --- | --- |
| Delivery scope | Full case workflow, all six requested chains, reporting, monitoring, security, operations and integration contracts. |
| Attribution | Evidence-first rules and calibrated ranking; human review for consequential routing. |
| Technology | React/TypeScript, FastAPI/Python, PostgreSQL, Temporal, object storage, and a rebuildable Neo4j projection. |
| Deployment | Portable containers; independently operated SIH installation and an agency deployment profile. |
| Data strategy | Competitive commercial-provider evaluation plus independently verified chain facts. |
| Production claim | Granted only after data, accuracy, security, recovery and official integration gates pass. |

## What this report establishes

This is a researched implementation specification, not an assertion that software has already been built. Public documentation supports the feasibility of its components. No paid intelligence account, SAHYOG API credential, production benchmark, or exchange-confirmed evaluation corpus was supplied. The exact original SIH listing and problem ID were not independently supplied or verified; the user-provided statement is the requirements baseline.

> The durable value is not a graph that always names an exchange. It is a reproducible explanation of what the evidence supports, what remains unknown, and what an authorised investigator can do next.

# 02 | Research findings and evidence boundaries

## Verified findings that change the design

MHA's 23 July 2025 parliamentary response reports 35 VASPs onboarded to SAHYOG at that date. Its description, and the public portal, concern notices to intermediaries. These sources establish participation and institutional context; they do not document the cryptocurrency disclosure/freezing API required by this proposal. No public integration contract was located in this review. [S01, S02]

Public blockchain APIs expose transaction facts, while commercial products separately advertise address screening, entity intelligence and tracing. Product coverage is endpoint-specific: a chain supported for screening is not necessarily supported for historical tracing or label export. Etherscan's documented address-metadata endpoint requires Pro Plus and is limited to two calls per second, despite different general API tier limits. [S20, S21, S25-S30]

Official protocol documents provide verifiable links for selected cross-chain transfers. CCTP messages and Wormhole VAAs can support protocol-specific matching; they do not establish a universal bridge or mixer deanonymisation service. [S18, S19]

## Evidence status used throughout

| Status | Meaning in this report |
| --- | --- |
| Documented | Official documentation or a primary publication supports the stated capability. |
| Vendor claim | Supplier describes a capability; independent quality and contractual access remain untested. |
| Proposed | An engineering choice, target or acceptance rule recommended here. |
| External dependency | Requires access, procurement, an official agreement, legal decision or ground truth. |
| Unknown | Public evidence is insufficient; the implementation must preserve this state. |

## Checks performed and their limits

Official documentation and research papers were inspected on 24 September 2026. A web retrieval returned Etherscan's public chain-list JSON. Direct local HTTPS requests to Blockstream's tip-height endpoint, Etherscan's chain list and TronGrid's latest-block endpoint failed with TLS connection errors at approximately 14:10 UTC. This does not establish provider downtime; it means this environment did not complete those direct checks. No credentialed API or end-to-end application test was executed.

The FIU downloads index confirms an updated VDA guideline dated 8 January 2026; direct PDF retrieval was unsuccessful in the research tool. Legal interpretation is therefore not based on a claimed complete reading of that PDF. The source register records retrieval limitations. Marketing latency, accuracy and coverage figures are not adopted as our benchmark results. [S04, S22]

# 03 | Requirements and the full release boundary

## Traceability from the supplied problem statement

| Requirement | Implementation deliverable | Proof required before release |
| --- | --- | --- |
| Automatic wallet analysis | Validated intake, asynchronous run, normalised events and reproducible snapshot. | Real address and transaction cases; explicit unsupported-network errors. |
| Nearest VASP discovery | Bounded temporal traversal and independently evidenced candidate list. | Known first-service and no-service cases, with depth and completeness checks. |
| Bitcoin, Ethereum, Tron, BNB, Solana, Polygon | Six certified adapters, with native and supported token coverage. | Per-chain history, pagination, finality and decoder acceptance suites. |
| Clusters and wallet roles | Versioned entity assertions, deposit/hot-wallet role evidence and reversible clusters. | Known deposit, omnibus and misleading sweep cases. |
| Mixers, bridges and swaps | Service detection; certified cross-chain decoders; visible uncertainty boundaries. | Verified protocol links and deliberately unresolved ambiguous paths. |
| Confidence and risk | Separate attribution evidence grades, calibrated probabilities where validated, and risk reasons. | Held-out evaluation, calibration and abstention analysis. |
| LEA reports and routing | Evidence bundle, signed manifest, legal-entity directory and approval workflow. | Reproducible exports and authorised integration acceptance. |
| Case dashboard and alerts | Graph, timeline, case assignments, watchlists and actionable change alerts. | Role-specific user journeys and alert deduplication tests. |
| Scale and resilience | Bounded workloads, provider quotas, durable jobs, backups and recovery. | Load, outage, replay and restore exercises. |

## Complete product versus universal coverage

Full delivery includes the entire investigative workflow and operational controls. It does not mean that every private ledger, privacy system, token implementation or bridge can be traced. The release must publish a machine-readable capability matrix and list unresolved paths. Additional EVM networks such as Base, Arbitrum and Optimism can be enabled only after their own endpoint and finality certification; shared address syntax is not sufficient.

Three installation profiles use the same code: independent research/SIH, licensed operational investigation, and agency-integrated deployment. They differ in credentials, data entitlements and permitted actions. Fixture replay has a permanent simulation label and never silently replaces live results.

> Completion means every required capability is implemented, tested and honestly bounded. Official SAHYOG connectivity remains an external release gate, even when the independent platform is complete.

# 04 | How the system works from intake to action

## The investigator's workflow

1. Create or import a case with agency, purpose, access controls and an external reference. Add one or more suspect addresses, an explicit chain, a date range and, when available, the incident transaction or Bitcoin output.
2. Validate address format and network. For an ambiguous EVM address, ask the investigator to select networks or run separately authorised network discovery. Do not guess Ethereum from a 0x prefix.
3. Start a trace. The system records the query scope, provider capabilities, software versions, block checkpoints and cost/depth limits before fetching data.
4. Retrieve and preserve transaction evidence, normalise transfers, enrich supported addresses with source-qualified labels, and follow time-consistent value movements.
5. Present ranked receiving-service candidates, their first deposit boundary, the actual event path and the unresolved branches. Distinguish the smallest hop count from the strongest evidence or largest value route.
6. The investigator reviews facts, hypotheses, missing data, jurisdiction and destination legal entity. A separate authorised reviewer approves any outgoing lawful request.
7. Generate the evidence bundle and dispatch through the approved SAHYOG interface when available. Track transport receipt, case acceptance, VASP response and reported asset action as different states.
8. Continue monitoring relevant addresses and labels. New deposits, reorgs, label corrections and meaningful risk changes produce an auditable case update.

## A useful answer when no VASP is found

The platform returns the chain and time range searched, deepest frontier reached, unresolved services, observed balances, provider failures, discarded spam/dust rules, and a recommended next investigation step. It does not state that an address is unhosted merely because no label was returned.

## What actually causes asset action

The platform assembles and routes evidence. An authorised recipient determines account ownership, disclosure, preservation, freezing or release under the applicable process. A historical deposit does not prove a current custodial balance. Centralised stablecoin issuers may have separate legal and technical mechanisms; these are distinct recipients and must not be represented as a universal blockchain freeze button. [S38, S39]

# 05 | Define "nearest" precisely

## Four questions that must stay separate

| Question | Answer produced |
| --- | --- |
| Is the submitted address already attributed? | A source-qualified ownership or control assertion for that address, possibly disputed. |
| Did it send directly to a service? | A one-hop observed transfer into an evidenced service address. |
| What is the nearest downstream service? | The first qualifying custodial boundary on each time-valid outgoing path. |
| Which recipient can act on this case? | The verified legal entity and request channel, subject to asset, jurisdiction and authority. |

Define a qualifying candidate as a VASP or custodial service with an evidenced link to the receiving address at the relevant time. Record wallet role separately: customer deposit address, hot wallet, omnibus wallet, custody contract, or role unknown. A hot-wallet label alone does not prove that the address is a currently supported customer deposit route.

For a run scope S, let P(S) be the admissible paths supported by the collected evidence. For each candidate entity v, compute h(v) as the minimum number of economic movement steps from the seed to the first evidenced entry into v. A Bitcoin transaction spend, an account transfer, a decoded swap and a matched bridge transition have explicit step types. Preserve the raw event count as well; these different metrics are never presented interchangeably.

The default nearest view orders qualified candidates by h(v), then evidence quality and relevant amount. A separate actionable view may prioritise stronger evidence, fresher deposits or a verified recipient. The UI explains the difference. An attributed seed is h=0; a direct deposit is h=1. In an unhosted-wallet-to-intermediary-to-exchange route, the exchange is downstream at h=2, not a direct recipient from the original wallet.

## Scope of the claim

Use the wording "nearest observed qualifying VASP within this run's scope." Assert shortest-within-scope only when all admissible lower-depth frontiers are exhausted. If a provider omits history, a branch is pruned or a budget is reached, set nearest_proven=false. There is no claim of a globally nearest exchange across unknown data.

Do not jump from an exchange deposit to unrelated withdrawals in the same exchange cluster. That crosses an off-chain accounting boundary without a customer ledger.

# 06 | Identifiers, taxonomy and input semantics

## Chain-qualified identity is mandatory

Represent accounts with a CAIP-10-compatible chain-qualified identifier, while retaining original input, decoded bytes and a safe display representation. Separate mainnet from testnet. EVM network identifiers include Ethereum 1, BNB Smart Chain 56 and Polygon PoS 137; the chain registry verifies configured RPC endpoints rather than trusting their names. [S40, S22]

Asset identity is chain plus native-asset identifier or token contract/mint, not the symbol. Two assets called USDT can be unrelated; native and bridged representations require explicit mapping evidence. Store integer base-unit quantities, token decimals with source/version, and display amounts as decimal strings. Never use floating point for evidence amounts.

| Object | Required distinction |
| --- | --- |
| Bitcoin | Script/output identity, txid and vout; an address is an encoding of selected script types. |
| EVM | Account versus token contract; external transaction versus log versus execution trace. |
| Tron | Base58Check and hex forms decode to one chain-qualified account; preserve the supplied form. |
| Solana | Wallet authority, token account, mint, program and program-derived account are separate roles. |
| Custodial service | Brand, blockchain cluster, operating legal entity and customer account are distinct. |
| Protocol | DEX pool, router, bridge, mixer and swap operator are not automatically equivalent legal categories. |

## Two analysis modes

Address exploration examines outgoing relationships in a specified window. It cannot assume that every historical transfer relates to the offence. Incident-flow tracing starts from identified transactions, UTXOs or token-transfer events and tracks feasible continuations from those seeds. Reports name the mode prominently.

The input contract supports direction, assets, starting events, time boundaries, maximum depth, query budget, finality policy and observation date. Upstream analysis is available for contextual source-of-funds research, but does not substitute for outgoing nearest-deposit discovery.

The service taxonomy supports multiple assertions with effective dates. FATF's VASP framework is a legal and functional classification; a protocol label alone does not settle whether a particular operator is a VASP in a jurisdiction. [S03]

# 07 | Worked example: the exact output to expect

## Illustrative fixture, not a real investigation

The following synthetic addresses and exchanges explain behaviour only. They must never be loaded as real attribution intelligence or shown without a fixture label.

[DIAGRAM:trace]

Assume the incident identifies a 10,000-unit token transfer into wallet S. S later sends 6,000 units to A and 3,000 to deposit address D1. A forwards 5,800 to D2. D1 is evidenced as an Exchange Alpha deposit address; D2 is evidenced as an Exchange Beta deposit address. S also sends 500 to an unresolved service U. The remaining 500 stays at S in this simplified same-token example; gas is paid separately.

| Candidate | Supported observation | Correct interpretation |
| --- | --- | --- |
| Alpha / D1 | S to D1, 3,000 units, one hop. | Nearest observed VASP; direct recipient from S. |
| Beta / D2 | S to A to D2, 5,800 units, two hops. | Another first-VASP route, with an intervening wallet. |
| U | S to U, 500 units; service unresolved. | Unresolved branch; do not assign an exchange. |

If the known deposit D1 subsequently sweeps to Alpha's hot wallet, keep that event as supporting service-role evidence. Do not count the sweep as a second independent deposit or search Alpha's other withdrawals for the suspect's next move.

## Why the amount claim needs its own reasoning

If A already held unrelated funds, the 5,800-unit outgoing transfer is an observed amount, not automatically 5,800 incident units. The report shows feasible amount bounds or a named allocation scenario. Likewise, S's receipt of 10,000 incident units must be accompanied by balance/history completeness before all later outflows are assigned to that seed.

An investigator sees Alpha first in the nearest view, Beta as a separate route, and U as unresolved. An operational-priority view could rank Beta higher for another reason, but must retain the displayed distances and explain the ordering. No beneficial owner or currently frozen balance is inferred from this fixture.

# 08 | The tracing algorithm

## Temporal, bounded, evidence-preserving search

Use a breadth-first frontier by economic hop count, enriched with incident-lot and protocol state. At each level, fetch all required pages within authorised scope, validate canonical transactions, and batch label lookups. Index event order by chain position; use protocol causal links for cross-chain steps. A visited-address set alone is incorrect because the same account can be reached with different times, assets and amount constraints.

```text
validate_scope_and_capabilities(request)
snapshot = create_run(checkpoints, versions, limits)
frontier = seed_states(request)
while frontier and budget_remaining:
    layer = pop_lowest_hop_states(frontier)
    events, coverage = fetch_validate_normalise(layer)
    preserve_raw_evidence_and_coverage(events, coverage)
    for state in layer:
        for step in admissible_continuations(state, events):
            next_state = advance_time_asset_and_amount(state, step)
            assertions = resolve_labels(step.recipient, step.time)
            if qualifies_as_first_custodial_boundary(assertions):
                record_candidate(next_state, assertions)
            elif is_unresolvable_boundary(step):
                record_unresolved_frontier(next_state)
            else:
                enqueue_if_not_dominated(next_state)
finalise_candidates_paths_and_completeness(snapshot)
```

State includes account/output, asset, causal position, hop count, incident-lot constraints, used evidence IDs and uncertainty class. Dominance pruning is permitted only when one state cannot yield a better valid result than another under the selected query. Record the rule and excluded frontier so pruning is reviewable.

## Bounds that prevent runaway work

Proposed defaults: 90-day incident window, 6 economic hops, 10,000 expanded account states, 100,000 events and a provider-credit ceiling per run. These are configurable engineering limits, not claims about laundering depth. An extension is a new versioned run. Materiality thresholds, fan-out caps and unsupported decoders produce explicit partial status and excluded amounts where measurable.

Finish the current depth when proving nearest candidates; discovering one labelled address is not a reason to discard other branches. Store predecessor references as a path DAG rather than duplicating every path. Worst-case expansion remains exponential in branching depth, so pagination, caching and limits are part of correctness, not merely performance optimisations.

# 09 | Follow value without inventing provenance

## Transfers and attributable funds are different quantities

Every edge has an observed on-chain amount. Incident attribution is a separate model over those edges. In an account model, tokens of the same asset are fungible inside a balance; in Bitcoin, input UTXOs are consumed by transactions, but the protocol does not assign particular input satoshis to specific outputs. A visible path therefore establishes possible movement, not always a unique allocation. [S08, S10]

Maintain incident lots with conservation constraints. At each account/transaction boundary, incident allocation cannot exceed the incoming incident capacity, available balance, or observed outgoing amount. Account for fees, burns, mints, token-transfer taxes, retained balances and verified transformations. Never sum all edge amounts along a route as the amount of loss.

For a simple complete-history account holding 100 incident units and 900 other units before a 200-unit outflow, the incident contribution can range from 0 to 100. A proportional allocation of 20 is only one scenario. If that outflow instead equals the full 1,000-unit balance with no intervening events or same-asset fees, the model constrains the incident contribution to 100. These examples assume the initial balances and all intervening same-asset events are known.

## Implementable amount analysis

Use a time-expanded flow model for selected candidate subgraphs. Calculate minimum and maximum feasible incident flow to each target subject to capacity and conservation constraints. When histories or initial balances are incomplete, widen the bounds and flag the missing constraints; do not report a mathematically precise lower bound from an incomplete ledger.

Optional FIFO, LIFO and proportional allocation views are explicitly named analytical scenarios. They do not alter raw evidence or masquerade as ownership facts. Keep scenarios separate, and label endpoints whose bounds overlap: independently maximised upper bounds across targets are not necessarily jointly achievable and must not be added together.

## Swaps and valuation

For a verified swap, record input and output assets, actual amounts, fees, recipient and transaction context. Preserve native quantities across asset changes; use a separately sourced, timestamped price only for indicative value comparisons. An unavailable price is unknown, not zero. Stablecoin symbols do not justify assuming a fixed exchange rate.

The release test corpus must include splits, merges, loops, replenished balances, partial spends, swap slippage and multiple incident seeds sharing an account. No new funds may be created by attribution arithmetic.

# 10 | Labels, clusters and deposit evidence

## Assertions, not an overwritable label field

Store each attribution assertion with source, chain, address/cluster, entity identifier, role, observed time, valid-time interval if known, retrieval time, method, source record hash, licence constraints and reviewer state. Historical validity that the source does not provide remains unknown. New labels can inform an old investigation, but the report must disclose that they were learned later.

| Evidence class | Use | Important limitation |
| --- | --- | --- |
| Authorised VASP confirmation | Strong deposit/control evidence for the stated address and interval. | Must authenticate the response and its scope; no universal customer identity claim. |
| Licensed intelligence assertion | Candidate entity and role evidence with supplier provenance. | Vendor confidence and independent calibration are different things. |
| Official service publication | Corroborates a stated service address or contract. | A reserve/hot address need not accept customer deposits. |
| Explorer/public label | Useful lead and supporting context, subject to permitted reuse. | Coverage, source independence and update history may be unclear. |
| Behavioural heuristic | A candidate relationship for review. | A sweep or repeated transfer does not establish ownership by itself. |

## Conservative clustering rules

For Bitcoin, common-input and change heuristics are optional, independently versioned hypotheses. CoinJoin and collaborative-spend patterns can invalidate common-input ownership assumptions; suppress or downgrade clustering in those cases. The published clustering research supports careful validation, not universal certainty. [S32]

For account chains, shared gas funding, repeated sweep patterns, deposit forwarding and transaction timing may generate proposals. Do not union every sender to a known exchange, collapse all users of a router, or infer common control from the same token contract. A contract labelled as an exchange interface may route value to several independent recipients.

Cluster membership edges are distinct from movement edges. A merge must be reversible, attributable and bounded against explosive growth. An inferred cluster can support a candidate, but cannot replace the actual deposit path or shorten its raw transfer history.

## Conflict and correction

Preserve contradictory assertions and identify correlated sources. Three sites repeating one label are one provenance family, not three independent confirmations. Reviewer overrides require a reason, evidence and expiry. Corrections append a new version, invalidate affected candidate scores, and alert authorised case owners without rewriting previously issued reports.

# 11 | Confidence scoring and honest abstention

## Four dimensions are displayed independently

Attribution confidence concerns service/control identity. Path confidence concerns the validity of a proposed movement connection. Coverage describes what history and event types were actually collected. Risk describes exposure or behaviour under a stated policy. Combining them into one unexplained number hides the main investigative uncertainties.

At launch, use evidence grades: confirmed within stated scope, corroborated, probable lead, weak lead, conflicting and unresolved. The word confirmed is reserved for an authenticated confirmation or equivalent accepted ground truth with its exact scope. The system may also show a transparent ranking score, labelled a ranking score rather than a probability.

## Path to a calibrated probability

Use a small interpretable model after enough independently labelled examples exist. Features can include source quality, independent corroboration, address-role specificity, freshness, conflict flags, cluster method and chain. Fit and calibrate on training/validation data split by entity and time; reserve a locked test set. Suitable starting methods are logistic regression followed, where justified by sample size, by isotonic or sigmoid calibration. Complex graph neural networks are not an initial dependency.

Show calibration curves, Brier score, precision and abstention by chain, source and wallet role. A percentage is released only for slices with adequate support and acceptable calibration. Record model version, training cutoff and calibration population with every prediction. Unsupported slices retain evidence grades.

## Why multiplying scores is unsafe

A supplier's score, a heuristic score and a path score are not necessarily probabilities, and their errors are often correlated. Do not multiply them or present an average as statistical certainty. As a conservative display rule, an unresolved or heuristic-only link prevents the whole route from being called verified. Quantitative route confidence requires validation on route-level outcomes.

## Proposed release targets, not measured performance

For the high-confidence actionable tier, target at least 98% observed entity precision and a 95% Wilson lower confidence bound of at least 95% on the independent acceptance set. Report coverage and abstention alongside precision, so the team cannot satisfy the target by answering only trivial examples. No probability or threshold alone approves a freezing request.

Thresholds are policy-controlled, versioned and change-reviewed. A drift alert can automatically lower a provider's trust tier and require review; it must not silently substitute another entity.

# 12 | Risk and laundering typologies

## Explainable signals instead of guilt scores

Risk outputs support prioritisation. An address receiving a malicious dust transfer, using a bridge, or interacting with a DeFi protocol is not proof of wrongdoing. Distinguish direct designation, indirect exposure, behavioural patterns and investigator-supplied allegations. A vendor category stays attributed to that vendor.

| Signal family | Implementable evidence | Required guardrail |
| --- | --- | --- |
| Sanctions/designations | Exact chain-qualified matches to dated authoritative lists. | Preserve additions/removals and applicable jurisdiction; absence is not clearance. |
| Ransomware, darknet, fraud | Licensed threat labels and case-confirmed intelligence. | Source date, entity scope and confidence required. |
| Rapid pass-through | Receipt followed by relevant outgoing value within a policy window. | Account for exchange operations, payments and unrelated prior balance. |
| Fan-in / fan-out | Time-bounded counts, amounts and concentration measures. | Exclude technical routers and known service aggregation where appropriate. |
| Peel-like movement | Repeated spend/retained-output patterns. | Keep change inference separate; do not classify all such wallets as criminal. |
| Chain or asset hopping | Verified swap and bridge events on a route. | Legitimate use is common; identify behaviour without claiming intent. |
| Mixer interaction | Validated contract/service interaction. | No deterministic exit attribution without further evidence. |

OFAC's sanctions-list service supplies downloadable list data, useful as one labelled source. It is not a complete criminal-address registry and does not determine Indian legal authority. Relevant domestic and UN sources require their own approved ingestion and scope rules. [S37]

## Rule implementation

Each risk rule has a version, inputs, lookback period, aggregation basis, materiality threshold, known benign explanations and severity. Return the evidence IDs and reason text that fired. Where an exposure percentage is used, define its denominator: eligible observed inflow or outflow in a named asset/window, with completeness status.

Policy severity and evidence confidence are separate. A highly serious but weakly supported threat should trigger review, not be upgraded to certain ownership. Dedupe exposure to the same underlying incident across loops and intermediary hops.

Alerts are generated for material new evidence, a confirmed deposit into a candidate VASP, a changed authoritative designation, a reorg or a label correction. Rate-limit, group by case and support acknowledgment. Periodic jobs with unchanged evidence remain quiet.

# 13 | Bitcoin adapter and attribution limits

## Data acquisition and normalisation

Use Bitcoin Core with an address/output indexer when operating owned infrastructure, or a contracted indexed provider. A normal node RPC interface should not be assumed to supply complete arbitrary-address history. Esplora documents address transactions and outspend lookups that are useful for a read-only indexed adapter. Verify commercial-use, rate and retention terms before depending on a public instance. [S09]

Represent transactions as input/output structures with txid, input outpoints, output index, script, satoshi value, block hash/height and status. The canonical event key for an output includes chain, txid and vout. Retain scripts that do not map cleanly to a supported display address. The spend relation is outpoint-to-spending-transaction; fabricated direct input-address-to-output-address edges must not imply exact allocation. [S08]

## Traversal behaviour

Begin from the incident output when known. Find its spend, reconstruct all relevant inputs and outputs, separate fees and continue plausible output branches. If the user only supplies an address, scope to selected received outputs and make the selection visible. A change-output guess is a hypothesis; preserve alternative branches if ownership cannot be validated.

| Case | Required handling |
| --- | --- |
| Unspent incident output | Report no observed onward movement at the checkpoint; optionally watch it. |
| Transaction with many inputs/outputs | Preserve the transaction boundary and amount ambiguity. |
| CoinJoin / collaborative transaction | Suspend ownership merging and display unresolved provenance unless independent evidence supports more. |
| Exchange deposit followed by sweep | Stop candidate tracing at the first service entry; use sweep as role evidence only. |
| Mempool replacement or reorg | Mark provisional findings superseded; rebuild affected confirmed paths. |

Use a proposed default of six confirmations for the operational finality policy, adjustable to agency risk appetite. This is a confirmation threshold, not mathematical irreversibility or a universal exchange crediting rule. Immediate triage may display fewer confirmations with a prominent provisional status.

Bitcoin acceptance cases must cover P2PKH, P2SH, SegWit and Taproot outputs, batched exchange payments, change ambiguity, partial provider history, double-spend replacements and disconnected blocks. Lightning payments and other off-chain accounting are outside deterministic on-chain tracing unless separately evidenced.

# 14 | Ethereum, BNB Chain and Polygon adapters

## Share code, certify each network

Use one EVM decoding library with separate network configurations and capability tests. Fetch transactions, receipts, block headers, token events and execution traces where available. Ethereum JSON-RPC provides receipts/logs; internal execution needs additional trace support or a verified indexed data product. Geth's built-in tracers document call-level inspection. [S10, S11]

Normalise native transfers, supported ERC-20 transfers, relevant NFT transfers, contract creation and verified swap/bridge actions. Record transaction index, log index or trace path, emitter contract, success state and evidence pointer. A reverted transaction does not create successful transfer edges. Account for its fee separately. Validate token identity; an arbitrary contract can emit misleading-looking events. [S41]

| Network | Additional responsibility |
| --- | --- |
| Ethereum | Use supported safe/finalized checkpoints and record trace-history availability. |
| BNB Smart Chain | Validate BSC-specific RPC/finality support; do not inherit Ethereum timings. |
| Polygon PoS | Validate milestone/finality behaviour and canonical token/bridge mappings. |

BNB documents API and finality differences from Ethereum. Polygon documents a distinction between probabilistic and deterministic finality. Implement against the deployed chain version and provider response; hard-coded historical block-time assumptions are unsuitable for release. [S16, S17]

## Avoid the common false graph

The transaction's top-level recipient may be a router, proxy or entry point, not the ultimate asset recipient. Decode validated logs and execution context. Distinguish wrapping/unwrapping, fees and mint/burn events from transfers. A delegate call does not independently transfer the associated apparent value. Account-abstraction bundlers and gas sponsors are not automatically beneficial owners.

An address can exist on several EVM networks with different histories. Contracts at the same bytes need not have the same code or operator. Maintain per-chain labels unless the source explicitly supports broader attribution.

For historical queries, public RPC logs alone do not replace a full address-history index. Bound block ranges, paginate indexed endpoints, and reconcile overlap windows. Native internal transfers, tokens and external transactions each carry separate coverage flags. Alchemy's history and webhook products have different documented support, so adapter certification must operate at method level. [S23]

# 15 | Tron adapter

## Include native TRX and token transfers

TronGrid exposes indexed account and TRC-20 history with cursor-style fingerprint pagination and confirmed/unconfirmed controls. Tron documentation distinguishes these indexed history services from ordinary self-hosted node APIs; operating a node alone does not provide the same arbitrary-address history interface. [S12, S13]

Decode Base58Check and hex address forms into a single chain-qualified identity. Retrieve native transfers, supported token transfers, receipts/events and relevant internal transactions. Preserve contract address, integer value, transaction hash, event position, block reference, result and data provenance. Verify the intended token contract rather than trusting a USDT symbol in provider metadata.

## Pagination and finality contract

Freeze the query's time range and other filters while following a fingerprint. Save every cursor/checkpoint with the run. Deduplicate across pages and use an overlap reconciliation window for late indexing. A repeated cursor, unexpectedly truncated page sequence or inaccessible historical range results in partial coverage, not an empty history conclusion.

Use confirmed/solidified observations for final reports under the configured policy. Permit provisional display separately. Verify both transaction execution success and the relevant value event. Fees and resource consumption are represented separately from incident token movement.

| Test condition | Expected result |
| --- | --- |
| More than one page of TRC-20 history | Every in-scope transfer collected once with original filters preserved. |
| Hex and Base58 input of the same account | Same canonical account and no duplicate entity. |
| Failed contract execution | No successful transfer edge from an attempted operation. |
| Malicious token with familiar symbol | Distinct asset, warning, no substitution for the genuine token. |
| Deposit address later swept | First service entry remains the deposit; sweep evidence does not reveal a customer. |
| Provider fingerprint/rate-limit error | Resumable job with visible partial state and retry budget. |

## Operational dependency

Run a credentialed throughput and archival-history evaluation before selecting TronGrid or a commercial alternative. API keys, per-account quotas, supported internal-transfer endpoints and commercial reuse terms belong in the provider contract. These were not validated with credentials during this research.

The Tron adapter is a required full-release component, not a chain icon backed by EVM data. If a dependency is unavailable, the UI must report Tron unsupported or temporarily degraded rather than return fixture intelligence.

# 16 | Solana adapter

## Account semantics determine correctness

Solana's signature-history method returns transactions referencing an account. Fetch full transaction metadata, then resolve static and loaded account keys, outer instructions, inner instructions, token balances and failure state. A mentioned account is not necessarily a sender, recipient or owner. The official JSON structures document versioned lookups and inner instructions. [S14, S15]

Treat wallet authority, associated or other token account, token mint, program and program-derived account as different objects. Attribute token balances to the relevant owner at the event time where evidence supports that relation. Current ownership is not sufficient to reconstruct the full history of a closed or reassigned token account.

## Normalised event rules

Store signature, slot, block reference where available, transaction position when retrievable, instruction index, inner-instruction index, mint and base-unit amount. Record the maximum supported transaction version and decoder version. Use actual instruction/event context and balance reconciliation to avoid double-counting the same transfer from both parsed instructions and token deltas.

Decode supported SPL Token and Token-2022 actions; explicitly flag extensions whose transfer semantics are not yet supported. Handle wrapped SOL, account creation/closure, rent effects, program fees and multi-instruction swaps separately. If a transaction failed, it cannot be treated as a successful token movement, even if logs describe attempted instructions.

## Data-provider decision

Use an archival RPC/indexing service for complete case windows, plus independent RPC checks of selected evidence. Helius describes parsed-event products that can reduce decoding effort, but program coverage and semantic correctness still need acceptance tests. A parsed provider response is a source artifact, not a replacement for canonical transaction metadata. [S24]

| Difficult case | Required response |
| --- | --- |
| Closed token account missing from current owner list | Recover historical accounts from indexed events or declare a history gap. |
| Router transaction with several recipients | Decode actual asset flows, not the fee payer alone. |
| Null transaction or unavailable old slot | Preserve signature and missing-history reason; try an authorised fallback. |
| Confirmed versus finalized observation | Display provisional state and refresh before final evidence export. |

Certification includes versioned transactions, lookup tables, inner transfers, token accounts, failed transactions and pagination across archival boundaries. Lamports and token quantities remain integers throughout.

# 17 | Cross-chain tracing and uncertainty boundaries

## Certify protocol families, not the phrase "cross-chain"

The first full release should include certified CCTP and Wormhole transfer decoders on supported source/destination pairs, plus the same-chain swaps needed by its benchmark cases. Maintain a protocol registry containing network, deployment address, code/version, valid block interval, asset mappings and decoding tests. An unsupported bridge still appears as a classified boundary with an unresolved continuation.

For CCTP, inspect the source burn/message, message domain fields and nonce, and the destination receipt/mint. Verify the relevant message/attestation and destination execution; retain version-specific rules and finality thresholds. Do not infer a completed transfer from a source burn alone. [S18]

For Wormhole, bind the source event, emitter chain/address, sequence and VAA to an observed successful destination redemption under the correct transfer protocol. A signed message alone is not proof that assets reached a beneficiary. The VAA documentation also warns about reorg effects on identifiers before finality. [S19]

| Link type | May enter verified path? | What the system records |
| --- | --- | --- |
| Matched protocol message and destination execution | Yes, subject to finality and decoder certification. | Both transactions, payload, asset mapping and evidence hashes. |
| Authorised provider's documented linkage | As provider-derived evidence; independent check where possible. | Source, method, confidence, scope and reproduction limits. |
| Amount/time similarity | No; investigative hypothesis only. | Candidate alternatives and why they are ambiguous. |
| Custodial swap or exchange internal ledger | Only with authorised records sufficient to link the movement. | Ledger evidence and custody boundary. |
| Mixer/cryptographic privacy boundary | Normally unresolved without additional admissible evidence. | Entry, service evidence and missing linkage. |

## Economic accounting

Model bridging as one economic transition with multiple raw protocol events. Do not count lock/burn, message relay and mint/release as independent suspect payments. Account for fees, rounding, recipient changes and native versus wrapped assets. A cross-chain clock comparison cannot replace a message's causal relationship.

Retries, pending attestations, delayed redemption and protocol upgrades must be recoverable states. A failed or refunded transfer updates the route rather than fabricating success. Cross-chain support is a versioned chain-pair and protocol matrix visible in the UI and report.

# 18 | Coverage, finality and reorganisation handling

## Completeness is an output

Each adapter returns a coverage manifest: requested and observed ranges, provider history horizon, event types supported, pages/cursors exhausted, missing blocks, decoder errors, latest indexed height, chain tip, finality checkpoint and observation time. A successful HTTP response is not proof of complete history.

```text
coverage = {
  "requested_range": "explicit UTC/block bounds",
  "event_types": {"native": "complete", "internal": "partial"},
  "pagination_exhausted": true,
  "missing_ranges": [],
  "finality_checkpoint": "chain-specific identifier",
  "pruned_frontiers": 0,
  "nearest_proven": false,
  "overall": "partial"
}
```

This is a proposed internal schema. Completeness can be true for a specific provider contract and bounded scope while attribution coverage remains unknown. No percentage of all exchange labels is inferred from the number of API calls that succeeded.

## A canonical chain, with preserved observations

Ingest provisional observations and maintain block parent links. On a detected reorg, mark affected evidence non-canonical, recompute paths, invalidate cached results and issue a correction event to impacted cases. Preserve the original observation and old report as superseded evidence rather than deleting its existence.

| Network family | Finality approach proposed for release |
| --- | --- |
| Bitcoin | Configurable confirmation policy; store block ancestry and remaining reorg risk. |
| Ethereum | Supported safe/finalized checkpoint semantics, with provider compatibility tests. |
| BNB / Polygon | Chain-specific finality mechanisms and responses, not inherited time constants. |
| Tron | Confirmed/solidified view according to the certified adapter. |
| Solana | Confirmed for provisional triage; finalized policy for final reports. |

For supported chains, source-event order follows ledger/execution position. Two transfers sharing a timestamp are not interchangeable. An atomic swap can have several correlated events in one transaction; only validated decoding determines their relation.

## Three separate reasons for a partial result

Data partial: a provider or index omits history. Search partial: depth, time, fan-out or cost limits prevented exploration. Attribution partial: observed transfers are complete but service identity or custody is unknown. Reports retain all three states and the next step needed to improve each.

# 19 | Provider landscape and procurement choice

## Recommended approach: a measured bake-off

Evaluate at least two attribution suppliers on the same independently labelled cases before selecting a primary. Maintain a second adapter for resilience and targeted corroboration, subject to licence terms. A large advertised chain count is not evidence of deposit-label quality on the six required chains.

| Supplier / source | Documented or advertised capability | Required verification |
| --- | --- | --- |
| TRM BLOCKINT API | API-oriented address behaviour, entity/risk intelligence and transaction history. [S27] | Exact chain/asset endpoints, labels, path export, role evidence and contractual quotas. |
| Chainalysis | Address Screening API; Reactor investigative tracing product. [S25, S26] | Do not assume a screening subscription exposes Reactor graphs or all proprietary labels. |
| Elliptic | Documented wallet/transaction analysis API and signed alert workflows. [S28, S29] | Entity-level output, historical trace access, chains, commercial rights and evidence export. |
| Arkham | Intel API announcements describe labels and fund flows; update feed supports changes/deletions. [S30, S31] | Contracted coverage, provenance, licence/redistribution rights and support commitments. |
| Etherscan | Indexed EVM data and paid address metadata. [S20-S22] | Product-specific tier, endpoint throttles, completeness and permitted reuse. |
| RPC/indexers | Chain facts, receipts, logs, outspends and decoded transactions. [S09-S15, S23, S24] | Archival depth, internal events, pagination and canonicality. |

## Selection rubric: proposed weights

Score independently measured entity/deposit precision at 30%, coverage of relevant six-chain cases at 20%, evidence/provenance/export at 15%, legal/security/data rights at 15%, throughput/reliability at 10%, and total effective cost at 10%. Mandatory failures override a weighted score: unusable chain coverage, prohibited evidence retention, unacceptable case disclosure, or absent commercial entitlement.

Public sanctions feeds and carefully reviewed public labels remain supplemental evidence. Do not scrape a paid dashboard or assume visible explorer labels can be redistributed freely. Do not reproduce proprietary datasets beyond contracted rights.

No vendor is selected or quoted in this report. Public pages establish product availability and advertised capabilities; credentials, actual result schemas, prices and independent performance remain procurement tasks. The architecture avoids dependence on an undocumented vendor endpoint.

# 20 | Provider contracts and adapter interface

## A common interface with visible differences

```text
capabilities() -> chains, assets, history, event_types, limits
fetch_history(subject, range, cursor) -> events, cursor, coverage
fetch_transaction(chain, txid) -> raw_evidence, canonical_status
lookup_attribution(subjects, as_of) -> assertions, provenance
lookup_risk(subjects, policy) -> source_findings
resolve_cross_chain(event) -> links, status, evidence
health_and_quota() -> freshness, availability, remaining_budget
```

These are our adapter interfaces, not claimed public methods of any named supplier. Optional methods may return unsupported with a reason. Vendors are never forced into a misleading lowest-common-denominator response that loses uncertainty.

## Every contract must answer

| Area | Questions to resolve before operational use |
| --- | --- |
| Coverage | Which exact chains, assets, event classes and historical dates are available per endpoint? |
| Attribution | Does the response identify entity, cluster, wallet role, effective date and evidence method? |
| Delivery | Pagination guarantees, bulk limits, retry policy, change/deletion feeds and schema deprecation notice? |
| Rights | Can raw responses be stored, hashed, retained after expiry, cited in court and shared with an authorised recipient? |
| Privacy | Query retention, subprocessors, training use, hosting/transfer locations and tenant separation? |
| Service | Availability commitment, support escalation, historical backfill and disaster behaviour? |
| Commercial | Per-call/credit/token/address costs, rescreening terms, burst ceilings, minimums and overages? |

## Resilience and quota enforcement

Use a central token bucket per provider and endpoint, with agency/run budgets and a bounded retry policy. Respect Retry-After and use exponential backoff with jitter for retryable failures. Avoid retrying invalid requests or revoked credentials indefinitely. Cache with chain, subject, scope, source, version and freshness; do not let one agency's private labels leak through shared caches.

Validate schemas and error payloads even when HTTP status is 200. A provider can signal no records, a quota error or unsupported data inside the response body. Distinguish all three. Redact keys in URLs, logs, traces and exports.

Use capability probes and synthetic contract fixtures in CI, then controlled authenticated canaries in the deployed environment. Provider disagreement creates a reviewable conflict. Fallback must preserve source identity and cannot silently strengthen the confidence claim.

# 21 | System architecture and trust boundaries

[DIAGRAM:architecture]

## Components and ownership

The investigator web client calls a case API through an authenticated gateway. The API enforces agency/case permissions, validates scope and starts a durable trace workflow. Workers acquire evidence, decode events, resolve labels, run traversal and generate reports. A separate integration service handles approved SAHYOG requests and receipts.

PostgreSQL is the authoritative store for cases, jobs, canonical events, assertion versions, approvals and audit references. Immutable source artifacts and generated evidence bundles live in encrypted object storage with retention controls. Neo4j is a derived graph projection for case exploration and traversal acceleration, rebuildable from authoritative records.

Provider calls pass through an egress gateway that allowlists destinations, applies quotas and redacts secrets. External providers receive only necessary blockchain subjects and authorised query parameters. Case narratives, victim details and legal documents stay inside the application unless an approved workflow explicitly needs to disclose them.

## Transactional boundaries

Persist authoritative events and an outbox record in one PostgreSQL transaction. Projection workers consume the outbox idempotently. The UI reads a graph only at a declared projection checkpoint; if it lags, show that state. A successful case update cannot be lost because a secondary graph database was temporarily unavailable.

Keep request approval and dispatch separate from general tracing workers. Integration credentials are unavailable to graph/decoder jobs. The dispatch service requires the approved report hash, immutable recipient version and case authorisation. It cannot send a newly changed draft using an old approval.

## Deployment shape

Start with a modular backend and independently scalable worker processes, not dozens of microservices. Separate chain adapters, attribution, analytics and integration through stable module contracts. The same containerised services support local development and a production cluster; the production profile adds high availability, secrets management, controlled egress and recovery procedures.

Agency deployment may use approved infrastructure in India. The exact cloud/on-premises selection, data export policy and accreditation process are decisions for the receiving organisation, not facts implied by the SIH problem statement.

# 22 | Technology stack and decision rationale

| Layer | Recommended technology | Why it belongs here |
| --- | --- | --- |
| Investigator UI | React + TypeScript + Vite; accessible component library. | Interactive case workspace without an unnecessary public SEO/server-rendering layer. |
| Graph / charts | Cytoscape.js and a maintained chart library. | Typed graph interactions, filtering, selection and printable views. [S36] |
| API | FastAPI, Pydantic, SQLAlchemy and Alembic. | Validated Python services and generated OpenAPI contracts. [S35] |
| Durable jobs | Temporal Python workers. | Resumable long-running fetch, review and retry workflows; activities remain idempotent. [S34] |
| Authoritative database | PostgreSQL with partitioning and row-level security. | Transactional cases/events, tenancy and audit relationships. [S33] |
| Graph projection | Neo4j; edition matched to resilience needs. | Queryable property graph; never the sole evidence store. [S42] |
| Evidence | S3-compatible encrypted storage with validated retention/legal-hold support. | Raw artifacts and immutable report versions. [S43] |
| Identity | Keycloak/OIDC or agency SSO, MFA and service identities. | Federation, least privilege and auditable sessions. |
| Observability | OpenTelemetry, Prometheus, Grafana and structured logs. | Correlate jobs, provider faults, latency and resource use without logging secrets. |
| Delivery / tests | Containers, CI, Terraform/Helm for production; pytest, property tests, Playwright and load tools. | Reproducibility, integration verification and operational deployment. |

## Explicit choices and trade-offs

Use Python for the first six adapters and orchestration; add a Go/Rust decoder only if profiling demonstrates a bottleneck. Avoid introducing a separate ML service until a validated scoring model requires it. LLMs are optional drafting aids over authorised evidence, not the entity-attribution engine or a source of transaction facts.

PostgreSQL-backed bounded adjacency search remains a fallback if the graph projection is unavailable. Neo4j Community is appropriate for a single-instance development setup; its enterprise high-availability capabilities must not be assumed to exist in a free deployment. Budget and certify the chosen edition, or benchmark the PostgreSQL alternative for the required workload. [S42]

Kafka and ClickHouse are scaling options for sustained bulk ingestion/analytics, not initial prerequisites. Introduce them only against measured throughput/storage thresholds and with an owned operations plan. Pin supported runtime, database and dependency versions with lockfiles and container digests at implementation kickoff; this report does not invent untested compatibility claims.

# 23 | Authoritative data model

| Entity | Essential fields and invariants |
| --- | --- |
| Agency / user / grant | Tenant ID, role, case permission, purpose and expiry; deny by default. |
| Case / subject | Case reference, classification, chain-qualified address, incident seed, time range and source. |
| Trace run | Immutable input, checkpoints, limits, capability snapshot, code/model/config versions and status. |
| Block / transaction | Chain, hash, parent/height or slot, canonicality, execution state and evidence pointer. |
| Transfer / action | Stable event key, asset, source/recipient, integer amount, order, type and raw provenance. |
| UTXO / spend | Chain, txid, vout, script, value and observed spend/canonical version. |
| Entity / assertion | Vendor/legal identity mapping, address role, source, valid/retrieved time, licence and status. |
| Cluster membership | Member, cluster, method, evidence, confidence/grade and reversible version. |
| Bridge link | Source/destination event IDs, protocol/version, message identity, validation state and amount mapping. |
| Candidate / path | First-service boundary, predecessor DAG, hop metrics, amount bounds and evidence/coverage state. |
| Evidence / report | Object reference, hash, media type, capture metadata, manifest version and signatures. |
| Recipient / request | Legal entity version, verified channel, approval, payload hash, idempotency key and receipts. |
| Watch / audit | Authorised scope, checkpoint, alert state; append-only actor/action/result records. |

## Keys and storage rules

Canonical event uniqueness is chain plus transaction plus the native event locator: vout, log index, trace path or instruction position. Provider observations have separate IDs, so a reorg or contradictory response can be retained without corrupting the canonical record. Amounts use exact numeric storage and decimal-string JSON transport.

Partition high-volume events by chain and block/time range. Index (chain, sender, asset, event_order), the equivalent recipient index, transaction IDs and assertion subject/time. Do not physically copy an entire chain into every case: case evidence selects immutable artifacts from shared public-chain facts, while private case annotations remain tenant-bound.

Keep valid time separate from system observation time. Unknown source validity remains null and does not default to "always true." A re-run pins a new evidence snapshot; an older report retains its original inputs.

An outbox and deterministic ingestion keys support at-least-once delivery without duplicated canonical events. Projection lag, report generation and signed export all refer to explicit run/version IDs. Retention/deletion jobs respect legal holds and separate raw public data from restricted case records.

# 24 | API contracts developers can implement

## Our public application API, not an official SAHYOG schema

| Endpoint | Contract and important behaviour |
| --- | --- |
| POST /v1/cases | Creates a tenant-scoped case; external reference unique within an integration namespace. |
| POST /v1/cases/{id}/subjects | Validates chain/address/seed; preserves original input. |
| POST /v1/cases/{id}/traces | Returns 202 with run ID; requires Idempotency-Key and bounded scope. |
| GET /v1/traces/{id} | Status, stage, budget, coverage, errors and result version. |
| GET /v1/traces/{id}/graph | Bounded cursor-paginated graph with projection checkpoint. |
| GET /v1/traces/{id}/candidates | Paths, first-service boundary, evidence grades, amount model and unresolved branches. |
| POST /v1/traces/{id}/reports | Generates immutable PDF/JSON/CSV evidence package asynchronously. |
| POST /v1/requests | Creates a request draft bound to case, recipient version and report hash. |
| POST /v1/requests/{id}/approve | Reviewer authorisation; later edits revoke the approval. |
| POST /v1/requests/{id}/dispatch | Dispatches approved payload; privilege and integration mode enforced. |
| POST /v1/cases/{id}/watches | Creates a budgeted authorised monitor with expiry. |
| GET /v1/capabilities | Actual certified chain/provider/protocol support and freshness. |

```json
{
  "chain_id": "eip155:1",
  "address": "<validated chain address>",
  "mode": "incident_flow",
  "seed_event_ids": ["<evidence-linked event>"],
  "from": "2026-09-01T00:00:00Z",
  "to": "2026-09-24T00:00:00Z",
  "max_hops": 6,
  "finality_policy": "final_report",
  "max_provider_credits": 2000
}
```

The example is an illustrative request shape, not executable credentials or a fabricated real address. All timestamps are explicit UTC. Response quantities are strings, and source evidence IDs resolve only within authorised access.

## Compatibility and security

Generate a versioned OpenAPI document, typed TypeScript client and contract fixtures. Use consistent typed errors for invalid address, unsupported scope, exhausted budget, stale result, provider outage, provider access restrictions and denied access. Apply object-level checks to every case/run/report/attachment, including exported links and event streams. A user-supplied callback URL is not permitted to become unrestricted outbound network access.

# 25 | Durable jobs, retries and monitoring

## Trace lifecycle

```text
RECEIVED -> VALIDATED -> QUEUED -> FETCHING -> NORMALISING
         -> ENRICHING -> TRACING -> SCORING -> REVIEW_READY
         -> REPORTING -> COMPLETED
Branches: PARTIAL | WAITING_PROVIDER | CANCELLED | FAILED
```

Each stage writes progress and its checkpoint. A run can complete with a partial analytical result; an operational exception is a separate failed state. Never label an empty API response caused by an outage as "no VASP found." Cancellation stops new calls, preserves collected evidence and produces a clear cancelled snapshot.

Temporal workflows coordinate stage transitions, timeouts and recovery. Activities can execute more than once, so ingestion, report publication and notifications use deterministic idempotency keys. Durable execution does not make an external side effect exactly once by itself. [S34]

## Workload controls

Partition queues by chain and workload class: interactive triage, deep traces, bulk import, label refresh and watch reconciliation. Reserve capacity for active investigators and urgent authorised cases; prevent one large batch from exhausting all provider quota. Apply limits to the caller, agency, case and supplier endpoint.

Use a circuit breaker for a failing provider, retain the resumable cursor, and expose the next retry/expiry. A fallback provider contributes new source evidence and may change completeness. Credentials revoked or contracts expired produce configuration incidents rather than endless retry storms.

## Watch behaviour

Prefer signed provider webhooks when available; reconcile by polling canonical history so missed events are recoverable. Verify signature/timestamp, deduplicate event IDs, reject replay and enqueue work before acknowledging delivery. Elliptic documents signed webhook integration and retries, which the adapter must test rather than merely assume. [S29]

A watch stores its last canonical checkpoint, label versions, risk-policy version, budget, permitted recipients and expiry. Notifications contain the minimum necessary case reference, with sensitive details behind authenticated access. Alert only on meaningful changes: a new relevant transfer/deposit, risk evidence change, label correction, or invalidated path.

When a label changes, find affected cases through assertion dependencies and generate a superseding result. Reports are not silently rewritten. A watch on an unchanged address must not incur unbounded rescreening expense or produce daily noise.

# 26 | SAHYOG integration without invented access

## What is known and what must be obtained

The public SAHYOG material confirms the portal and describes notice workflows; it does not furnish the specific application contract needed here. Implement a versioned boundary that can be adapted after I4C provides the permitted request types, identity model, message schema, security requirements and test environment. [S01, S02]

| Integration mode | What works | Claim permitted |
| --- | --- | --- |
| Standalone | Case intake, tracing, evidence, directory and downloadable request draft. | Independent investigation platform. |
| Contract simulator | Proposed inbound case event, callbacks, acknowledgments, failures and duplicate handling. | Tested proposed integration contract; simulation clearly labelled. |
| Official sandbox | Authenticated exchange against the supplied agency sandbox and approved schema. | Sandbox integration tested for named workflows. |
| Production | Approved credentials, recipients, legal process and operations acceptance. | Live integration for the explicitly authorised scope. |

## Proposed exchange flow

SAHYOG or an authorised connector submits an external case reference, chain-qualified subjects, scope and purpose. Our gateway authenticates the sender, maps tenant/case permissions and acknowledges intake. An asynchronous callback or polling endpoint returns a run reference and status; evidence is transferred only through an approved channel.

After review, our dispatch service sends an approved request package with an idempotency key, case reference, recipient identifier, report/manifest hashes and lawful request type. The adapter verifies the receipt and stores both payload versions. These fields are a proposal, not undocumented claims about SAHYOG's current schema.

## Mandatory questions for I4C

Obtain the actual API specification, onboarding rules, sandbox access, authentication method, callback verification, IP/egress requirements, attachment limits, recipient master data, receipt/status meanings, timeouts, version policy and audit/retention requirements. Confirm which requests may be submitted and who approves them. Determine whether delegated accounts or a service principal are permitted.

Use mTLS/OAuth or signed messages only as negotiated; do not claim the portal already implements them. Do not automate around CAPTCHA or treat a portal login as permission to call private interfaces. A simulator can validate our logic while this work proceeds, but cannot close the official integration gate.

# 27 | Routing to the right legal entity

## A directory is a governed dataset

An exchange brand may span multiple legal entities, products, jurisdictions and custodial arrangements. The directory maps a canonical service entity to verified legal names, jurisdictions, supported request categories, official portal/channel, accepted identification fields, disclosure requirements, languages, escalation policy and last verification date. It contains no guessed officer email addresses.

Sources include authenticated agency master data, confirmed VASP legal-response material and reviewed official service documentation. Any contact/channel change requires dual review and an audit record. Expired or conflicting recipient records block automated dispatch while preserving a draft for manual resolution.

## Request state machine

```text
DRAFT -> EVIDENCE_READY -> LEGAL_REVIEW -> APPROVED
      -> DISPATCHING -> TRANSPORT_ACK -> RECIPIENT_ACCEPTED
      -> RESPONSE_RECEIVED -> ACTION_REPORTED -> CLOSED
Branches: REJECTED | NEEDS_INFORMATION | DELIVERY_UNKNOWN
          EXPIRED | CANCELLED | CORRECTED
```

Transport acknowledgement is not recipient acceptance, and acceptance is not a confirmed freeze. Record the response source, affected asset/amount, timestamps, scope and case reference. "Funds frozen" appears only after verified recipient evidence states it; the platform never manufactures that outcome from a sent request.

## Prevent duplicate or misdirected action

Bind approval to the exact payload hash, recipient version and evidence report. Changes require a fresh approval. If dispatch times out after possibly reaching the recipient, enter DELIVERY_UNKNOWN and reconcile by idempotency key/status query. Retry blindly only where the receiving contract guarantees deduplication; otherwise use controlled manual reconciliation.

Route separate requests for preservation, disclosure and asset action according to the agency's legal templates. The system must distinguish the subject wallet from an identified customer account and request the records necessary to resolve that relationship. Off-chain KYC, login and account-ledger data are supplied only through authorised processes, not scraped or inferred from a blockchain graph.

An issuer request for a supported stablecoin is a separate path with its own verified recipient and authority requirements. Native BTC or ETH cannot be frozen by this application. Historical fund exposure, available on-chain balance and a service's presently controllable customer balance are different values. [S38, S39]

# 28 | Investigator dashboard and interaction design

## The workspace must make evidence review easy

| Screen | What the investigator can do |
| --- | --- |
| Case queue | Search assigned cases, filter urgency/status, see provider degradation and unresolved reviews. |
| Intake | Add addresses/transactions, resolve chain ambiguity, choose incident mode and authorised scope. |
| Case overview | Review subjects, candidate services, earliest actionable deposit, coverage gaps and latest changes. |
| Graph explorer | Expand bounded branches, inspect every event, compare alternatives and collapse service clusters. |
| Timeline and ledger | Sort actual event order, filter assets, export exact amounts and open source evidence. |
| Candidate review | Compare nearest distance, entity evidence, wallet role, amount bounds and verified recipient. |
| Evidence/report | Preview findings, hypotheses, methods, limitations, attachments and report versions. |
| Requests | Draft, review, approve, track receipts and reconcile uncertain delivery. |
| Watchlist/admin | Manage authorised monitors, budgets, provider capabilities and directory verification. |

## Graph conventions

Use shapes and text labels as well as colour. Solid edges represent observed movements or verified protocol links; dashed edges are hypotheses. Cluster membership is visually different from money movement. Label chain, asset, amount, event time and confirmation state on demand, with a detailed inspection panel for provenance.

The default graph shows a bounded, relevant subgraph rather than trying to draw millions of nodes. Server-side filters, incremental expansion and saved views preserve responsiveness. Every hidden branch is still counted in the coverage summary; visual simplification must not change analytical results.

## Explicit uncertainty in the interface

Always display run mode, scope, as-of checkpoint, completeness and evidence grade next to candidate results. "No label returned" is not "self-custody confirmed." A historical transfer to a service is not "balance available to freeze." Display a provider conflict as conflicting assertions, not whichever response arrived last.

Support keyboard navigation, high contrast, accessible tables, UTC/IST time display with timezone labels, and printable graph legends. English is the initial operational language; keep terminology and translation resources structured for Hindi and other required agency languages.

The interface must not require users to connect a cryptocurrency wallet or provide private keys. This platform reads evidence and manages investigations; it does not need signing authority over suspect funds.

# 29 | Investigation-ready reports and evidence custody

## Every report answers the same questions

Include case/reference and access classification; scope and investigator; seed addresses/events; collection sources and timestamps; chain checkpoints; ranked service candidates; first-deposit paths; raw event identifiers; native amounts and allocation assumptions; attribution evidence and conflicts; unresolved branches; risk reasons; verified recipient recommendation; review history; and explicit limitations.

Deliver a human-readable PDF and a machine-readable evidence bundle containing JSON findings, CSV transfer tables, source-response artifacts where licence permits, decoder/config versions, and a manifest. The PDF graph is an aid; it is not a substitute for transaction records.

## Evidence acquisition and integrity

For each artifact, preserve acquisition time, source URL/API operation with secrets removed, request parameters, response status, provider record/version, raw bytes, SHA-256 hash and collection agent version. Store block/transaction references so an independent reviewer can check supported facts again. If an upstream source changes or is unavailable later, retained original bytes remain attributable.

Create a canonical manifest listing artifact hashes, sizes and roles. Hash the report separately, then sign a manifest that references it; avoid an impossible self-referential report hash. Protect signing keys in a KMS/HSM or approved equivalent. Hashes detect modification; they do not prove that a source attribution was true.

Use object retention/legal-hold controls appropriate to the deployment, with encrypted backups and access logs. S3 Object Lock is one documented WORM mechanism; any compatible implementation must have its actual retention and privilege behaviour tested. Do not place sensitive evidence or its linkable identifiers on a public blockchain. [S43]

## Reproducibility and correction

Replaying the frozen evidence through the pinned decoder/rules must reproduce normalised facts and material findings. Include an offline manifest verifier. Re-fetching a live provider later is a new observation, not guaranteed byte-identical evidence.

Electronic-evidence submission may require statutory certificates and other conditions. The Bharatiya Sakshya Adhiniyam contains an electronic-record framework and certificate schedule; the product can assemble metadata for authorised completion, but cannot certify admissibility automatically. Counsel and competent signatories approve the appropriate form and process. [S05]

Redacted reports are new signed versions with a redaction log. A later correction preserves the original, cites what changed and notifies authorised recipients according to the agency's procedure.

# 30 | Security and misuse resistance

## Protect sensitive investigative relationships

Use agency SSO/OIDC, MFA, short-lived sessions and distinct service identities. Combine role-based permissions with agency, case assignment, purpose and classification checks. Database row-level security adds defence in depth; application roles must not be owners or bypass-RLS roles. Privileged maintenance access is separate, logged and time-bound. [S33]

| Threat | Required control and verification |
| --- | --- |
| Cross-agency access / ID enumeration | Object-level authorisation on every API, graph query, export and event stream; negative isolation tests. |
| Provider/SSRF compromise | Allowlisted egress, safe redirects, bounded responses, schema validation and no arbitrary callback fetching. |
| Credential exposure | Managed secrets, rotation, scoped keys and redaction of query strings/logs. |
| Malicious case attachment | Type/size limits, malware scan, isolated parsing and safe previews. |
| Label/data poisoning | Source provenance, reversible assertions, conflict handling and reviewer separation. |
| Resource exhaustion | Depth/node/page/credit limits, concurrency quotas and fair scheduling. |
| Fraudulent request dispatch | Separate reviewer privilege, recipient verification and payload-bound approval. |
| Supply-chain attack | Pinned builds, SBOM, vulnerability checks, signed artifacts and controlled releases. |

OWASP's API risks include object-level authorisation, resource consumption, SSRF and unsafe consumption of external APIs. These directly shape the test plan rather than serving as a compliance badge. [S44]

## Data minimisation and audit

Encrypt data in transit and at rest with managed keys and separation of duties. Do not include victim names, case narratives or legal attachments in blockchain-provider queries. Even an address query can reveal investigative interest; procurement must define supplier logging, retention and permitted use.

Log who accessed a case, exported evidence, changed an assertion, approved a recipient or dispatched a request. Hash chaining can improve tamper detection, but must be complemented by restricted administration and immutable external log retention. Audit-log availability is an operational dependency.

The research/SIH profile uses public facts and explicitly synthetic cases. The operational profile requires verified organisational users. Automated scoring never infers a private person's identity or criminal status solely from a wallet graph. If an optional language model drafts a narrative, treat evidence text as untrusted input and require citation-bound human review.

# 31 | Legal, policy and deployment governance

## Design obligations to settle before production

This section identifies requirements for review; it does not substitute for legal advice or assert that any particular authority has approved the system. The user identified MHA/I4C as the problem owner but supplied no deployment mandate, credentials, budget or statutory instrument.

| Topic | Verified source/context | Engineering consequence |
| --- | --- | --- |
| VASP scope | FATF guidance provides a functional framework and notes later standards updates. [S03] | Version taxonomy; legal classification is jurisdiction-specific and reviewable. |
| Indian VDA reporting regime | FIU's official index lists January 2026 updated guidelines and registration circulars. [S04] | Obtain current text and counsel's obligations matrix; registration is not proof of wallet ownership. |
| Electronic evidence | BSA electronic-record provisions and schedule. [S05] | Capture acquisition/system metadata and support authorised certificates. |
| Personal data | MeitY publishes DPDP Rules 2025, corrigendum and an enforcement timeline. [S06] | Map applicable provisions and commencement dates to actual deployment; do not assume blanket exemptions. |
| Cyber incidents/logging | CERT-In's 2022 directions and official FAQ index. [S07] | Review applicable incident reporting, clock/log controls and retention in India. |
| Cross-border action | Destination entity, local process and agency authority vary. | Use verified channels and legal templates; no universal freeze power. |

CERT-In's published directions include six-hour reporting for specified incidents and rolling 180-day ICT logs in India for covered organisations. Operational counsel must verify applicability and current requirements; this does not establish a single universal retention period for all investigation evidence. [S07]

## Information governance decisions

Approve a data inventory, purpose/access policy, retention schedule, legal-hold rules, breach process, supplier agreements and cross-border disclosure rules. Differentiate public chain facts, proprietary labels, victim/case data, VASP responses and authentication logs. Each has different access, retention and contractual constraints.

Do not assume government deployment automatically permits any data processing or overseas provider query. Determine the actual operating entity and applicable exemptions/obligations. Keep production data out of development fixtures and evaluation sharing unless authorised and minimised.

Agency-specific security testing, hosting/accreditation and procurement requirements are an external acceptance workstream. Maintain named owners and dated decisions so a missing legal or administrative decision cannot be hidden behind a successful technical demo.

# 32 | Capacity planning and performance targets

## Start from workload assumptions

Proposed planning profile: 1,000 new traces/day, 250 uncached expanded subjects/trace, four history/detail requests per subject and 20% retry/reconciliation overhead. This implies 1.2 million history/detail requests/day, about 13.9/second on average, before attribution lookups, watch traffic and bursts. Batching labels can reduce calls, but not necessarily billable address units.

At five times average peak demand, this profile needs roughly 70 history/detail requests/second across providers. It cannot be served by assuming a single free explorer key has unlimited throughput. Quotas and capabilities must be allocated per chain and endpoint. Etherscan's free tier documents selected-chain limits of three calls/second and 100,000/day; specialist metadata has its own limit. [S20, S21]

| Proposed target | Precise interpretation |
| --- | --- |
| p95 API acknowledgement under 2 s | Validation and durable enqueue; excludes completing a trace. |
| p95 bounded triage under 60 s | Cached or contracted short-history profile, under declared load; measure by chain. |
| p95 ordinary trace under 5 min | Agreed reference corpus and limits; deep jobs use a separate queue/SLO. |
| p95 case graph interactions under 1 s | Bounded visible graph, not the entire underlying ledger. |
| 99.5% pilot availability | Proposed service target with a defined measurement window and dependency policy. |
| 99.9% operational availability | Target only after HA, failover and error-budget evidence. |

These are acceptance targets, not measured results or guaranteed times for arbitrary wallets. A complete label search of a large high-activity wallet may take substantially longer or hit a budget boundary.

## Storage model

Assume 5,000 observed events/trace and 50% cross-case deduplication: about 2.5 million new events/day. At an assumed 1-3 KB per normalised event, base storage is 2.5-7.5 GB/day before indexes, replicas, raw responses, backups and reports. Measure these multipliers on fixtures and pilot data; do not size a national service from this illustrative calculation alone.

Cache public chain facts safely, batch compatible lookups, partition event stores and bound graph expansion. Measure cost and latency per successful useful result, not only per HTTP request. Reassess bulk indexing and additional analytical stores when contracted request cost or measured backlog justifies them.

# 33 | Deployment, recovery and operating the service

## Environments with the same application behaviour

Development runs the backend, frontend, PostgreSQL, Temporal, object store and graph projection through a documented container setup. CI uses disposable isolated services and clearly marked fixtures. Staging exercises real contracted providers with non-sensitive authorised examples. Production uses approved infrastructure, managed secrets, restricted egress and independently tested backups.

Prefer a small Kubernetes deployment only when the operating team can support it; an adequately hardened container/VM deployment can serve a limited installation. Production reliability comes from tested redundancy and operations, not the presence of a Kubernetes logo. Keep provider subscriptions and database operations owned by named people.

## Resilience design

Use PostgreSQL high availability with point-in-time recovery, replicated evidence storage and tested restore procedures. The graph projection is rebuildable; if it is unavailable, bounded investigation queries fall back to authoritative data or report a clear delay. Select and test the required Temporal persistence/availability topology. No approval or dispatch state depends solely on an in-memory queue.

Proposed operational targets are RPO at most 15 minutes for recoverable application data and RTO at most four hours for critical case access, to be proven in a restore exercise. Issued evidence and dispatch receipts require a stronger durability policy and must be recoverable from retained immutable artifacts and reconciled external receipts. These are design targets, not guarantees achieved by this report.

| Runbook | Trigger and response |
| --- | --- |
| Provider outage / quota exhaustion | Pause affected queues, preserve cursors, activate approved fallback, notify operations. |
| Chain reorg / decoder regression | Quarantine affected results, recompute, issue corrections and disable unsafe decoder. |
| Incorrect attribution | Retract the assertion version, identify dependent cases and notify authorised reviewers. |
| Dispatch uncertainty | Stop automatic retries; reconcile receiver status and approved payload identity. |
| Key or account compromise | Revoke/rotate credentials, preserve audit evidence and follow incident procedure. |
| Database/object restore | Restore into isolation, verify manifests/checkpoints and reconcile pending external actions. |

Monitor queue age, provider error and 429 rates, chain lag, history gaps, decoder failures, graph projection lag, assertion conflicts, report failures, dispatch states and per-case cost. Log correlation IDs without sensitive narratives or API keys. A release includes an on-call rota, escalation contacts, rollback procedure and a completed recovery drill.

# 34 | Ground truth and evaluation design

## What counts as a correct answer

Use authenticated VASP address/control confirmations where available, independently reviewed official service disclosures and authorised case outcomes. Public hot-wallet labels alone cannot validate precision for private deposit-wallet attribution. Synthetic fixtures test algorithms, not real-world entity-identification accuracy.

The proposed acceptance corpus contains at least 1,200 independently reviewed trace tasks across the six chains, with a target of 200 per chain. Stratify by direct deposits, indirect deposits, negative/no-resolved-service cases, contract routing, stale/conflicting labels and incomplete histories. Include at least 300 actionable-tier predictions overall if claiming the precision gate, with enough per-chain support to report confidence intervals. Obtain more data if a slice is underpowered.

Use entity-disjoint and time-forward splits wherever possible. Prevent the same deposit address, cluster or duplicated public incident from leaking across training and test sets. Freeze an acceptance set before tuning thresholds. Two analysts adjudicate disagreements; an unresolved ground-truth case is not forced into a convenient label.

## Metrics that must be reported together

| Metric | Meaning and denominator |
| --- | --- |
| Entity precision | Correct service identity among predictions issued at each evidence tier. |
| Recall / answer coverage | Resolved correct targets among independently solvable labelled tasks; separately report all-case answer rate. |
| First-service correctness | Correct first custodial boundary, not merely any reachable exchange. |
| Top-k recall / ranking | Whether verified candidates occur in the returned set and how they are ordered. |
| Path validity | Evidence-supported, time-valid movements and independently validated protocol transitions. |
| Amount validity | Conservation and correctness of bounds under stated assumptions. |
| Calibration / abstention | Reliability of supported probability bins and rate/reasons for withholding an answer. |
| Operational quality | p50/p95 latency, cost, coverage gaps, review time and recipient-routing errors. |

Evaluation is prospective where possible: measure baseline investigator time and assisted time on comparable cases, without assuming speedup proves correctness. Request acceptance, confirmed assets restrained and later recovery are separate outcomes with separate external dependencies.

If licensed ground truth is unavailable, publish only the fixture/path-validation results and the coverage of public labels. Do not claim a national accuracy rate, universal beneficial-owner identification, or production-grade deposit attribution from a few famous exchange wallets.

# 35 | Concrete test matrix

| Test group | Cases | Release expectation |
| --- | --- | --- |
| Identity / amounts | Wrong checksum/network, ambiguous EVM address, huge integers, token-symbol collisions. | Reject invalid scope; no chain or precision substitution. |
| Chain adapters | Pagination, overlapping pages, cursor loop, missing history, rate limit and malformed success response. | Every event once; all gaps and failures visible. |
| Temporal paths | Outgoing before incident, same-block order, return loops, chain clock skew. | No impossible causal path; bounded traversal terminates. |
| Bitcoin | Change ambiguity, CoinJoin, batching, replaced transaction, reorg. | Correct UTXO evidence and no unjustified ownership merge. |
| EVM / Tron | Failed execution, internal transfer, proxy/router, fee-on-transfer and fake token event. | Actual successful movements with decoder/coverage flags. |
| Solana | Versioned keys, inner instructions, fee payer, closed token account, Token-2022 extension. | Correct account role and no duplicate movement. |
| Bridges / swaps | Matched message, pending redemption, refund, mismatched asset, unsupported protocol. | Only certified links form verified routes. |
| Attribution | Stale/conflicting labels, correlated sources, cluster rollback, unknown deposit role. | Evidence grade changes correctly; unresolved remains unresolved. |
| Funds | Splits/merges, prior balance, multiple seeds, swaps and shared target bounds. | Conservation; no double-counting of incident amounts. |
| Workflow / dispatch | Worker crash, duplicate job, approval edit, timeout after send, callback replay. | Resume safely; reconcile ambiguity; no unauthorised duplicate dispatch. |
| Access / evidence | Cross-tenant IDs, signed-link expiry, modified artifact, redaction, hold policy. | Access denied; tampering detected; immutable versions retained. |
| Operations | Provider outage, database failover, backup restore, projection rebuild and load peak. | Declared recovery and performance gates pass. |

## Test layers

Use unit tests for decoders and domain rules; property tests for conservation, idempotency and graph invariants; recorded fixtures for regression; integration tests against real disposable databases/workers; and authorised live connector tests for current provider contracts. Playwright verifies role-specific user journeys and report/request states. Load and fault-injection tests cover the planning workload and bounded worst cases.

No test obtains certainty by reusing the same vendor output as both prediction and ground truth. Maintain an adversarial corpus that intentionally attempts false exchange attribution. A release candidate produces a test evidence pack with exact build, datasets, environment, failures and waived limitations. Security-critical isolation, evidence integrity and dispatch-approval failures cannot be waived for operational use.

# 36 | SIH demonstration and operational release profiles

## A convincing demonstration uses real, inspectable evidence

The SIH build should run locally or in a controlled hosted environment with documented setup and visible provider configuration. Demonstrate the complete journey: case intake, real public-chain history, candidate evidence, uncertainty, report export, reviewer approval and a clearly labelled integration simulator receipt. The full production plan remains the target even if SIH evaluation occurs before external access is granted.

| Demonstration scenario | What it proves |
| --- | --- |
| Verified public service address | Live collection, source inspection and correct service evidence handling. |
| Authorised indirect-deposit case | Temporal traversal and correct first-service boundary. |
| Bitcoin split / Solana token account | Chain-specific semantics rather than six copies of one EVM demo. |
| Certified bridge transfer | Both chain legs and protocol proof visible. |
| Ambiguous mixer / missing labels | Honest abstention and useful unresolved frontier. |
| Provider disconnected | Resumable partial state; no automatic substitution of fabricated success. |
| Evidence tampered in test copy | Offline verifier rejects the modified artifact. |
| Duplicate simulator delivery | Receiver deduplicates; dispatch state remains accurate. |

Real-world examples require reviewed ground truth and permitted data use. Never send a real legal notice or move cryptocurrency merely to make the demonstration look complete. Controlled testnet fixtures exercise parsers and workflow; they do not validate production exchange attribution.

## How to label readiness

Independent release: six-chain functionality and end-to-end case/report workflow pass within stated data coverage. Licensed release: contracted attribution, independent precision evaluation and operational support pass. Agency-integrated release: official SAHYOG contract and authorised request workflows pass in the required environment. Each claim names the tested scope and dependencies.

The solution's differentiation is evidence orchestration, first-service discovery, conservative fund allocation, versioned assertions and correct recipient routing. It is not a claim to out-infer all commercial intelligence providers from public address syntax.

No production-ready label is granted on the strength of a polished dashboard alone. The final acceptance checklist applies to the actual deployed build, not screenshots or a narrated mockup.

# 37 | Full implementation roadmap

## Proposed 24-32 week engineering programme

This estimate assumes an experienced team, timely provider access and available reviewers. It is not an SIH deadline prediction. Procurement, official integration and ground-truth access can extend elapsed time independently of coding progress.

| Window | Deliverables | Exit gate |
| --- | --- | --- |
| Weeks 1-2 | Requirements freeze, threat model, evidence schema, provider RFI, ground-truth protocol and repo/CI. | Data rights, scope and architecture decisions recorded; blocking access requests identified. |
| Weeks 3-6 | Case/auth API, durable workers, evidence store, Ethereum and Bitcoin paths, first report export. | Real data reproduced from frozen evidence; no fixture fallback in live mode. |
| Weeks 7-10 | Tron, BNB, Polygon and Solana adapters; per-chain history/finality certification. | Six-chain test matrix passes for declared event/asset scope. |
| Weeks 11-14 | Provider normalisation, assertion ledger, first-service algorithm, amount constraints and graph UI. | Independent candidate/path review; conflicts and abstention work. |
| Weeks 15-18 | CCTP/Wormhole decoders, risk rules, watches, directory and request approval. | Certified cross-chain cases; dedupe, corrections and dispatch isolation pass. |
| Weeks 19-22 | Calibration if justified, full acceptance corpus, performance tuning, security and recovery drills. | Accuracy targets, isolation and evidence integrity verified; deficits corrected. |
| Weeks 23-26 | Official sandbox integration if available, pilot with investigators, accessibility and training. | Named agency/pilot reviewers accept workflows and measured limitations. |
| Weeks 27-32 | Remediation, operational hardening, production integration acceptance and handover. | Full production gates pass; approved deployment and support ownership. |

## Critical path

Data entitlements and ground truth drive attribution certification. All six adapters drive the complete-chain release. Verified VASP directory and lawful workflow drive request correctness. Official API access drives SAHYOG acceptance. None can be replaced by extra frontend work.

Workstreams can proceed concurrently under one integration schedule: platform/evidence; chain ingestion; attribution/analytics; frontend/reports; and security/agency integration. The roadmap defines stage exits rather than promising a fixed launch date regardless of failed tests.

A student team should re-estimate using actual availability, skills, budget and mentor access. Do not compress this production programme into a weekend or redefine a limited demonstration as the full requested solution. A working early vertical slice is an internal milestone toward the complete release, not the final scope.

# 38 | Staffing, budget model and purchasing gates

## Roles for a serious build

Plan for a technical lead, two blockchain/data engineers, two backend/workflow engineers, one frontend engineer, one QA/automation engineer and one platform/security engineer. This eight-person example needs additional scheduled investigator/domain and legal/privacy review, plus procurement and operational ownership. Roles may overlap in a smaller team, with a corresponding schedule trade-off.

## Costs are assumptions, not supplier quotations

| Cost item | How to estimate it |
| --- | --- |
| Engineering | Team-months multiplied by an explicitly chosen fully loaded rate. |
| Chain data | History/detail units, archival RPC, webhook/stream fees, quota minimums and redundancy. |
| Attribution | Billable addresses/calls, bulk access, investigators' seats, retention/export rights and support. |
| Infrastructure | Databases, workers, object storage, backups, egress, logs, KMS and recovery capacity. |
| Validation | Ground-truth curation, legal/domain review, independent security assessment and pilot support. |
| Operations | Monitoring/on-call, patching, provider changes, incident response and user training. |

For illustration only: 8 people x 7 months x INR 2 lakh per person-month = INR 112 lakh in engineering. Add a 20% engineering contingency and that component becomes INR 134.4 lakh (INR 1.344 crore). The rate is an explicit planning assumption, not a researched labour quote; it can be replaced with the team's actual cost.

For infrastructure scenario modelling, reserve an assumed INR 0.5-2 lakh/month for a controlled pilot and INR 2-8 lakh/month for a larger redundant deployment. These are budgeting placeholders, not priced bills of materials, and exclude commercial intelligence, full archival-node fleets, tax, security audits and support staffing. Benchmark and obtain region-specific quotes before committing funds.

## The budget equation

Monthly external cost equals fixed subscriptions plus history units times history-unit price, attribution units times attribution-unit price, monitoring units times monitoring price, storage/compute/egress, support and applicable tax. Include failed requests and rescreening according to each contract. Our 1,000-traces/day scenario is a workload example, not proof that a particular plan can serve it.

No total project price is defensible before commercial intelligence quotations and deployment sizing. An open-data student build can reduce cash expenditure, but narrower labels and unpaid engineering are real trade-offs. Government sponsorship, free vendor access and waived licences are not assumed.

# 39 | Risk register and decisions that change the plan

| Risk | Early indicator | Response / accountable owner |
| --- | --- | --- |
| Insufficient deposit-label coverage | Many verified chain paths end at unknown addresses. | Compare vendors, obtain authorised confirmations, publish unresolved rate; data lead. |
| False entity or cluster match | Independent reviewers dispute a high-tier candidate. | Quarantine rule/provider, revert assertions, notify impacted cases; analytics lead. |
| No SAHYOG contract/access | No official sandbox/specification by integration milestone. | Continue standalone release and simulator; keep official gate open; integration owner. |
| Provider access too expensive | Forecast credits or minimum subscription exceed budget. | Optimise scope/cache, negotiate, reprioritise volume; product/procurement owner. |
| Missing historical/internal events | Reconciliation gaps on required-chain fixtures. | Archival/indexer fallback or explicit partial support; chain lead. |
| Cross-chain overclaim | Link rests only on similar time/amount. | Downgrade to hypothesis; require protocol proof; analytics reviewer. |
| Wrong legal recipient | Brand resolves to multiple unverified entities. | Block dispatch, verify directory; legal/integration owner. |
| Case data exposure | Excessive provider query metadata or failed isolation test. | Minimise, revoke access, remediate before operational use; security owner. |
| Cost/latency blow-up | High fan-out wallets exhaust worker/API budgets. | Fair queues, bounded expansion and resumable partial results; platform lead. |
| Misleading confidence | Good aggregate precision but poor chain/role slice. | Disable percentages for unsupported slices; collect more ground truth; evaluation lead. |
| Team capacity gap | Chain or evidence work repeatedly misses exit gates. | Add experienced support or extend time; technical lead. |

## Decisions to resolve at project kickoff

Confirm the exact SIH problem ID and evaluation rules; team size and delivery calendar; permitted provider spend; target users and hosting model; expected case volume; what assets and history depth must be supported; ground-truth access; and whether I4C will provide an integration liaison. None is silently inferred from the ministry's name.

Choose the primary/secondary attribution supplier only after the benchmark and contract review. Choose Neo4j edition and operational topology after resilience/cost evaluation. Choose lawful request templates and retention policy with the receiving organisation. These decisions do not block writing the independent software contracts, fixtures, parser tests and evidence workflow.

## Limits that must remain visible

Unsupported privacy systems, unknown custody, inaccessible off-chain ledgers and missing labels are investigation boundaries. The platform can improve speed and reproducibility without promising to identify every owner, trace every mixer exit or guarantee a recoverable balance. No result currently available in this research validates such a promise.

# 40 | Build specification and the first concrete work

## Repository and ownership boundaries

```text
apps/web/                  investigator UI and typed API client
services/api/              cases, permissions, reports, request API
workers/                   Temporal workflows and activities
packages/domain/           identifiers, events, assertions, scoring
packages/adapters/         bitcoin, evm, tron, solana, intelligence
packages/protocols/        swaps and certified bridge decoders
packages/evidence/         manifests, signing, report generation
integrations/sahyog/       proposed contract, simulator, real adapter
infra/                     local compose, deployment, monitoring
tests/                     fixtures, property, contract, end-to-end
benchmarks/                labelled evaluation and load manifests
docs/                      architecture, runbooks, data rights, UAT
```

## The first ten working days

Days 1-2: finalise scope/assumptions, create architecture decision records, provider questionnaires and the threat/data-flow model. Define identifiers, raw evidence envelope, canonical transfer, assertion and coverage schemas. Create the capability registry before any chain badges are enabled.

Days 3-4: implement the case/auth skeleton, database migrations, durable workflow, raw-evidence storage and manifest hashing. Establish CI, fixture isolation and exact-amount conventions. Verify tenant isolation before case data enters the system.

Days 5-7: implement one EVM and one Bitcoin acquisition path with pinned real public examples and permitted provider access. Preserve raw responses, canonical checks and complete pagination. Add the first-service traversal and deliberately ambiguous negative fixtures.

Days 8-10: connect the graph/ledger UI, generate a reproducible evidence report, and complete the intake-to-reviewed-draft workflow. Record measured gaps and update the six-chain delivery backlog. This is an engineering integration checkpoint, not the declared final product.

## Setup and documentation contract

The future repository must provide .env.example with no secrets, a one-command container startup after prerequisites, automated migrations, health checks, a capability-status screen, fixture replay mode and an authorised live validation command. Document Windows development through WSL2 or another tested container path, as well as production Linux deployment.

No endpoint may return a manufactured exchange result when its provider is unconfigured. CI must verify that live mode fails transparently without required credentials. The final README must say which tests actually ran, which access remains external and how to reproduce every demonstrated result.

# 41 | Definition of done and handover

## Gates for calling the requested solution operational

| Gate | Required evidence |
| --- | --- |
| Functional completeness | Case creation, six certified chains, actual tracing, evidence-qualified candidates, graph, risk, reports, monitors and request workflow work together. |
| Real data | Successful authenticated/public integration tests for every configured connector, with preserved responses and capability manifest. |
| Attribution quality | Independent ground-truth evaluation, precision/coverage/abstention by slice, and no unsupported confidence percentages. |
| Path and amount integrity | Temporal correctness, bridge proofs, conservation and all critical adversarial cases pass. |
| Evidence | Reproducible report bundle, signed manifest, offline verification and correction/redaction workflow demonstrated. |
| Security | Tenant isolation, authorisation, secret handling, dispatch separation and independent assessment issues resolved. |
| Reliability | Load targets under declared workload, provider-failure recovery, restore and projection-rebuild drills pass. |
| Directory and legal workflow | Verified recipient records, approved templates, retention/authority decisions and trained reviewers. |
| SAHYOG | Official sandbox and production acceptance for the exact authorised contract; simulator alone does not pass. |
| Operational ownership | Maintained deployment, monitoring, on-call/support, licence renewals, patching and training assigned. |

## Deliverables handed over

Source repository and reproducible build; OpenAPI and integration schemas; database migrations; deployment configuration; adapter/protocol capability matrix; provider-rights register; evaluation corpus and methodology within permitted sharing; test reports; operator/investigator manuals; recovery and incident runbooks; sample evidence bundles; signing/secret ownership procedure; and the accepted limitations register.

## What is complete now

This research stage supplies the architecture, reasoning, implementation contracts, full-release backlog, test strategy, deployment plan, budget model and source register. It intentionally precedes implementation, as requested. It does not claim a running application, licensed data access, measured attribution accuracy, or SAHYOG connectivity.

The next stage is to implement this plan against actual available credentials and independently verifiable examples. Work can proceed on the standalone platform while procurement and official integration are resolved, but final readiness labels must continue to reflect the gates that have actually passed.

> A defensible complete solution returns useful intelligence quickly, preserves the evidence needed to challenge it, and knows when the correct result is still unknown.

# Sources and evidence notes

All sources accessed/reviewed 24 September 2026.

## S01: Rajya Sabha Unstarred Question 399, 23 July 2025

Ministry of Home Affairs, Government of India | Government primary source

[Rajya Sabha Unstarred Question 399, 23 July 2025](https://www.mha.gov.in/MHA1/Par2017/pdfs/par2025-pdfs/RS23072025/399.pdf)

Supports: Page 5 reports 35 VASPs onboarded to SAHYOG at that date; describes the portal's notice context.

Limit: Historical count, not a current total or an API specification.

Access: Official PDF text retrieved.

## S02: SAHYOG public portal

Ministry of Home Affairs | Government primary source

[SAHYOG public portal](https://sahyog.mha.gov.in/)

Supports: Public description and authenticated portal entry point.

Limit: No cryptocurrency disclosure/freezing integration contract exposed in the reviewed public page.

Access: Public page retrieved; no authenticated access attempted.

## S03: Updated Guidance for a Risk-Based Approach to Virtual Assets and VASPs (2021)

Financial Action Task Force | Intergovernmental guidance

[Updated Guidance for a Risk-Based Approach to Virtual Assets and VASPs (2021)](https://www.fatf-gafi.org/en/publications/Fatfrecommendations/Guidance-rba-virtual-assets-2021.html)

Supports: VASP/virtual-asset framework and attention to unhosted/P2P arrangements.

Limit: The page notes that later standards revisions are not incorporated; jurisdictional legal review is required.

Access: Official guidance page and indexed PDF excerpts reviewed.

## S04: Official downloads: VDA guidelines and registration circulars

Financial Intelligence Unit - India | Government primary source

[Official downloads: VDA guidelines and registration circulars](https://fiuindia.gov.in/files/Downloads/Downloads.html)

Supports: Lists VDA AML/CFT guidelines updated 8 January 2026 and registration circulars.

Limit: Direct retrieval of VDA08012026.pdf failed; no claim of complete substantive legal review of that document.

Access: Official index retrieved; guideline title/date confirmed.

## S05: The Bharatiya Sakshya Adhiniyam, 2023

India Code | Statutory primary source

[The Bharatiya Sakshya Adhiniyam, 2023](https://www.indiacode.nic.in/bitstream/123456789/20063/1/a2023-47.pdf)

Supports: Electronic-record provisions including section 63 and associated certificate requirements.

Limit: An evidence export is not automatically admissible; competent legal/signatory review remains necessary.

Access: Official indexed statutory text and certificate excerpts reviewed.

## S06: Digital Personal Data Protection Rules 2025 and enforcement timeline

Ministry of Electronics and Information Technology | Government primary source

[Digital Personal Data Protection Rules 2025 and enforcement timeline](https://www.meity.gov.in/documents/act-and-policies/digital-personal-data-protection-rules-2025-gDOxUjMtQWa)

Supports: Official publication index for Rules, corrigendum and enforcement timeline.

Limit: Applicability and commencement must be mapped to the actual deployment; no blanket government exemption assumed.

Access: Official indexed page reviewed.

## S07: Directions under section 70B, 28 April 2022

CERT-In | Government primary source

[Directions under section 70B, 28 April 2022](https://www.cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf)

Supports: Specified incident reporting and ICT logging requirements for covered organisations.

Limit: Review current applicability and official FAQs; investigation evidence retention is a separate policy.

Access: Official eight-page PDF text retrieved.

## S08: Developer Guide: Transactions

Bitcoin Developer Documentation | Protocol documentation

[Developer Guide: Transactions](https://developer.bitcoin.org/devguide/transactions.html)

Supports: Inputs spend previous outputs; transaction and UTXO structure.

Limit: Protocol structure does not establish beneficial ownership or unique input-to-output fund allocation.

Access: Official developer text reviewed.

## S09: Esplora HTTP API documentation

Blockstream | Maintainer documentation

[Esplora HTTP API documentation](https://github.com/Blockstream/esplora/blob/master/API.md)

Supports: Address history, transaction and output-spend interfaces for an indexed Bitcoin adapter.

Limit: Public-instance availability, commercial usage and throughput were not validated; local endpoint probe failed TLS.

Access: Maintainer API reference retrieved.

## S10: JSON-RPC API

Ethereum.org | Protocol documentation

[JSON-RPC API](https://ethereum.org/developers/docs/apis/json-rpc/)

Supports: Receipts, logs, block queries and safe/finalized selectors.

Limit: Standard RPC is not a universal arbitrary-address archival history or internal-trace service.

Access: Official documentation reviewed.

## S11: Built-in tracers

Go Ethereum | Client maintainer documentation

[Built-in tracers](https://geth.ethereum.org/docs/developers/evm-tracing/built-in-tracers)

Supports: Execution/call tracing as an additional data surface.

Limit: Node/provider configuration and historical trace access require separate verification.

Access: Official documentation retrieved.

## S12: TRC-20 transaction history

TRON Developer Hub | Protocol/provider documentation

[TRC-20 transaction history](https://developers.tron.network/es/docs/get-trc20-transaction-history)

Supports: Indexed per-account TRC-20 history, fingerprint pagination and confirmation filters.

Limit: Endpoint limits and data rights need credentialed validation; displayed locale path is the retrieved source.

Access: Official developer page reviewed.

## S13: Exchange wallet integration

TRON Developer Hub | Protocol documentation

[Exchange wallet integration](https://developers.tron.network/docs/exchangewallet-integrate-with-the-tron-network)

Supports: Distinction between native-node calls and indexed account-history services.

Limit: A self-hosted node alone is not assumed to provide indexed history; no live keyed integration tested.

Access: Official documentation retrieved.

## S14: getSignaturesForAddress

Solana | Protocol documentation

[getSignaturesForAddress](https://solana.com/docs/rpc/http/getsignaturesforaddress)

Supports: Signature history for account references and pagination/configuration fields.

Limit: Referenced account is not necessarily a value recipient; archival availability varies by provider.

Access: Official RPC reference retrieved.

## S15: RPC JSON structures

Solana | Protocol documentation

[RPC JSON structures](https://solana.com/docs/rpc/json-structures)

Supports: Loaded keys, inner instructions and transaction metadata structures.

Limit: Parsing all application semantics and token extensions still requires validated decoders.

Access: Official RPC structures reviewed.

## S16: BSC JSON-RPC endpoint and API differences

BNB Chain | Protocol documentation

[BSC JSON-RPC endpoint and API differences](https://docs.bnbchain.org/bnb-smart-chain/developers/json_rpc/json-rpc-endpoint/)

Supports: EVM compatibility with BSC-specific interfaces and finality differences.

Limit: No hard-coded historical block timing or universal Ethereum finality assumption is adopted.

Access: Official documentation reviewed.

## S17: Polygon PoS finality

Polygon | Protocol documentation

[Polygon PoS finality](https://docs.polygon.technology/pos/concepts/finality/finality)

Supports: Finality concepts and the milestone mechanism; also located in official documentation index.

Limit: The older milestones URL failed; current route and network/provider behaviour must be rechecked when implementing.

Access: Official index inspected; current finality route retrieved separately.

## S18: CCTP technical guide

Circle | Protocol maintainer documentation

[CCTP technical guide](https://developers.circle.com/cctp/references/technical-guide)

Supports: Message/attestation flow, source and destination domains, nonce and version-specific semantics.

Limit: Protocol linkage does not by itself prove destination execution or customer identity; YAML retrieval was unavailable.

Access: Official technical guide and supported-domain page reviewed.

## S19: Verified Action Approvals (VAAs)

Wormhole | Protocol maintainer documentation

[Verified Action Approvals (VAAs)](https://wormhole.com/docs/protocol/infrastructure/vaas/)

Supports: VAA identifiers, guardian signatures and finality/reorg caveats.

Limit: A signed message is not proof of successful destination asset redemption.

Access: Official protocol documentation reviewed.

## S20: Rate limits

Etherscan | Provider documentation

[Rate limits](https://docs.etherscan.io/rate-limits)

Supports: General API plan limits, including selected-chain free tier constraints.

Limit: Limits can change; endpoint-specific restrictions override the general plan table.

Access: Official documentation retrieved.

## S21: Get metadata for an address

Etherscan | Provider API reference

[Get metadata for an address](https://docs.etherscan.io/api-reference/endpoint/getaddresstag)

Supports: Address nametags/metadata, documented Pro Plus requirement and two-calls-per-second endpoint limit.

Limit: Public documentation is not an active entitlement or validation of label precision.

Access: Official endpoint reference retrieved, including access requirements.

## S22: Public V2 chain list

Etherscan | Provider data endpoint

[Public V2 chain list](https://api.etherscan.io/v2/chainlist)

Supports: Chain-specific identifiers and API metadata for configuration discovery.

Limit: A fetched chain registry does not prove successful authenticated transaction or label calls.

Access: Web retrieval returned JSON; direct local HTTPS probe failed TLS.

## S23: alchemy_getAssetTransfers

Alchemy | Provider API reference

[alchemy_getAssetTransfers](https://www.alchemy.com/docs/data/transfers-api/transfers-endpoints/alchemy-get-asset-transfers)

Supports: Indexed transfer-history interface and method-specific internal-transfer coverage.

Limit: History and webhook products differ; no assumption that all advertised networks expose every event type.

Access: Official method and feature-support documentation reviewed.

## S24: Introducing Parsed Events API and Parsed Streams

Helius | Provider product announcement

[Introducing Parsed Events API and Parsed Streams](https://www.helius.dev/blog/parsed-events-and-streams)

Supports: Availability of parsed Solana data products and historical-query descriptions.

Limit: Provider coverage claims are not independently tested; legacy API-reference URL retrieval failed.

Access: Official announcement reviewed.

## S25: Address Screening

Chainalysis | Vendor capability claim

[Address Screening](https://www.chainalysis.com/product/address-screening/)

Supports: Address risk screening and API availability.

Limit: No subscription, entity precision or export entitlement validated; screening is not assumed to expose all tracing data.

Access: Official product page reviewed.

## S26: Reactor investigations

Chainalysis | Vendor capability claim

[Reactor investigations](https://www.chainalysis.com/product/reactor/)

Supports: Investigative tracing/graph product distinct from address screening.

Limit: Marketing scale/accuracy claims are not adopted as our results or an available API contract.

Access: Official product page reviewed.

## S27: BLOCKINT API

TRM Labs | Vendor capability claim

[BLOCKINT API](https://www.trmlabs.com/blockchain-intelligence-platform/blockint-api)

Supports: API-oriented address behaviour, risk/entity intelligence and transaction history offering.

Limit: Exact response schemas, entitlements, provenance and benchmark quality require procurement/testing.

Access: Official product page retrieved.

## S28: AML API introduction

Elliptic | Provider API documentation

[AML API introduction](https://developers.elliptic.co/docs/aml-api-introduction)

Supports: Batch/single wallet and transaction analysis interfaces and key-based onboarding.

Limit: This does not establish access to every investigative graph or deposit assertion.

Access: Official developer guide reviewed.

## S29: Rescreening and alerting

Elliptic | Provider API documentation

[Rescreening and alerting](https://developers.elliptic.co/docs/rescreening-and-alerting)

Supports: Webhook alerts, signature validation guidance and retry behaviour.

Limit: Implementation must validate current signed delivery and duplication behaviour with its actual subscription.

Access: Official developer guide reviewed.

## S30: The new Arkham API, 17 February 2026

Arkham | Vendor capability claim

[The new Arkham API, 17 February 2026](https://info.arkm.com/announcements/the-new-arkham-api)

Supports: Intel API described as exposing entity labels and fund-flow data.

Limit: Access, costs, data rights and independent quality were not established.

Access: Official announcement reviewed.

## S31: API upgrade: real-time intel, 8 September 2026

Arkham | Vendor product changelog

[API upgrade: real-time intel, 8 September 2026](https://info.arkm.com/announcements/arkham-api-upgrade-real-time-intel)

Supports: New/updated/deleted intelligence feed and cursor-based update semantics.

Limit: Freshness is a supplier statement, not an independently measured SLA.

Access: Official announcement reviewed.

## S32: How to Peel a Million: Validating and Expanding Bitcoin Clusters

Kappos et al.; USENIX Security 2022 | Primary research paper

[How to Peel a Million: Validating and Expanding Bitcoin Clusters](https://www.usenix.org/system/files/sec22-kappos.pdf)

Supports: Bitcoin clustering methodology and limitations including collaborative transactions.

Limit: Published research does not validate a new implementation or provide universal ownership certainty.

Access: Original paper text retrieved.

## S33: Row security policies

PostgreSQL Global Development Group | Software maintainer documentation

[Row security policies](https://www.postgresql.org/docs/18/ddl-rowsecurity.html)

Supports: Row-level policies as a defence-in-depth mechanism.

Limit: Application permissions and privileged-role behaviour still require isolation tests.

Access: Official versioned documentation reviewed.

## S34: What is a Temporal Activity?

Temporal | Software maintainer documentation

[What is a Temporal Activity?](https://docs.temporal.io/activities)

Supports: Workflow activities, durable lifecycle and recommended idempotency.

Limit: Does not create exactly-once effects in an external recipient system.

Access: Official documentation retrieved and idempotency passage inspected.

## S35: Features

FastAPI | Software maintainer documentation

[Features](https://fastapi.tiangolo.com/features/)

Supports: API framework choice and schema-driven interface design.

Limit: Framework capabilities do not substitute for security, scalability or application acceptance tests.

Access: Official documentation retrieved.

## S36: Graph library documentation

Cytoscape.js | Software maintainer documentation

[Graph library documentation](https://js.cytoscape.org/)

Supports: Interactive graph visualisation tooling.

Limit: Visual graph layout is not attribution or proof of ownership.

Access: Official documentation retrieved.

## S37: Sanctions List Service

US Treasury, Office of Foreign Assets Control | Government primary source

[Sanctions List Service](https://ofac.treasury.gov/sanctions-list-service)

Supports: Official downloadable sanctions-list data service.

Limit: One source with a particular jurisdictional scope; not an exhaustive criminal-wallet registry.

Access: Official page retrieved.

## S38: USDC terms

Circle | Issuer legal terms

[USDC terms](https://www.circle.com/legal/usdc-terms)

Supports: Issuer-specific blocked-address and legal-order provisions.

Limit: Does not create an application-controlled freeze mechanism or settle an agency's legal authority.

Access: Official legal terms excerpts reviewed.

## S39: Legal terms and policies

Tether | Issuer legal terms

[Legal terms and policies](https://tether.to/en/legal/)

Supports: Issuer-specific legal, information-sharing and token-freezing provisions.

Limit: Current request process and jurisdiction must be confirmed; no automatic action entitlement inferred.

Access: Official legal page excerpts reviewed.

## S40: CAIP-10: Account ID specification

Chain Agnostic Improvement Proposals | Identifier specification

[CAIP-10: Account ID specification](https://standards.chainagnostic.org/CAIPs/caip-10)

Supports: Chain-qualified account identifiers.

Limit: Canonicalisation and input validation remain chain-specific implementation work.

Access: Specification retrieved through canonical redirect.

## S41: ERC-20 token standard

Ethereum Improvement Proposals | Protocol specification

[ERC-20 token standard](https://eips.ethereum.org/EIPS/eip-20)

Supports: Token interface/event semantics used by the EVM decoder design.

Limit: An arbitrary contract emitting similar events is not verified asset identity or compliant behaviour.

Access: Official specification retrieved.

## S42: Operations manual introduction and editions

Neo4j | Software maintainer documentation

[Operations manual introduction and editions](https://neo4j.com/docs/operations-manual/current/introduction/)

Supports: Property graph deployment and Community/Enterprise capability distinctions.

Limit: Enterprise clustering/HA must not be assumed in a free single-instance deployment.

Access: Official documentation retrieved; editions section inspected.

## S43: Locking objects with S3 Object Lock

Amazon Web Services | Storage provider documentation

[Locking objects with S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html)

Supports: Retention/legal hold and WORM storage mechanism.

Limit: Not a hosting recommendation or compliance certification; compatible products need their own validation.

Access: Official documentation reviewed.

## S44: API Security Top 10, 2023

OWASP | Security project guidance

[API Security Top 10, 2023](https://api-security.owasp.org/editions/2023/en/0x00-header/)

Supports: Object authorisation, resource consumption, SSRF and unsafe API-consumption threats.

Limit: An awareness framework, not a security audit or certification.

Access: Official project material reviewed.
