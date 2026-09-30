# TraceSetu: a concrete method for finding the first receiving VASP

Research review, proposed method and synthetic reference experiment

29 September 2026 | Team ANANTHA | Plain-language technical paper

## 1. What problem are we actually solving?

An officer has a cryptocurrency address connected to a complaint. The officer needs to find the company that received a relevant transfer, so a lawful request can be addressed to the correct organisation. A **VASP** is a business providing services involving virtual assets, such as an exchange or a custodial wallet provider. Bitcoin is an asset and network; it is not an exchange.

The exact supplied problem is **Automated Attribution of Unknown Cryptocurrency Wallets to Nearest Virtual Asset Service Providers (VASPs) through Blockchain Intelligence APIs**. The supplied SIH context identifies the Ministry of Home Affairs and I4C as the intended problem owners.

Public blockchains usually expose transfers between addresses. They do not automatically expose the company controlling each address or the customer behind an exchange account. An exchange may give a customer a deposit address and later collect the deposited tokens into a shared hot wallet. Finding the hot wallet is not necessarily finding the first point where the exchange already controlled the assets.

**Why label lookup is insufficient:** following arrows until a labelled exchange appears is a useful baseline, but it does not explain how an unlabelled deposit address is discovered. A graph dashboard alone does not solve that gap.

## The proposed answer

Combine **seeded deposit-address discovery** with **time-respecting first-custody tracing**. Start with sourced evidence about a small set of service wallets. Look for specific operational patterns that suggest additional deposit addresses. Keep those suggestions separate from observed transfers. Then search the transfer history in the right order, returning the first supported custodian on each branch and exposing any nearer unresolved candidate.

The service name still comes from external identity evidence. Patterns can extend a known service's candidate address set; they cannot invent the legal identity of an entirely unknown operator. An ambiguous result remains unknown or unconfirmed.

## What this paper actually establishes

TraceSetu already has a working investigation workflow and bounded tracing. This review adds a precisely specified research proposal and an isolated executable experiment. The experiment demonstrates rule behaviour on fictional records; it does not establish real-world attribution accuracy. The new detector is not integrated into the running MVP. No official SAHYOG connection, customer disclosure or asset freeze has occurred.

<!-- pagebreak -->

## 2. One example: why finding a hot wallet is not enough

Every address and service in this example is fictional. Suppose reported address **S** sends a token to **D**. D later forwards that token to **H**. A sourced assertion identifies H as a hot wallet of Exchange Alpha. Separate evidence identifies **G** as Alpha's gas-funding wallet. Gas is the native asset needed to pay a transaction fee on an account-based chain.

<!-- diagram:example -->

An exact-label search finds H, two recorded transfers from S. But if Alpha also controls D, custody began one transfer earlier. The hard question is therefore: **is D Alpha's deposit infrastructure, or is D an ordinary customer sending money to Alpha?** One payment to H cannot answer that.

The proposed account-based rule looks for repeated, fully observed cycles: D receives a token, G provides transaction-fee funds, and D sends the received token units to H. This is motivated by published work on deposit-address heuristics and a service-specific gas/sweep pattern. [1, 2] A sweep means collecting assets from a deposit address into another wallet.

Even a complete match remains a hypothesis. An ordinary customer with gas assistance could behave identically. Independent confirmation or stronger control evidence is needed before treating D as established Alpha custody. If D has a conflicting label or incomplete history, the result must state the gap rather than silently substitute H as the nearest deposit address.

## Keep two kinds of evidence separate

**Transfer graph:** addresses or Bitcoin outputs are nodes; observed transfers are directed edges. Each event retains its chain, asset, exact integer amount, transaction identifier, ledger order, success status and source record. This graph describes movement.

**Service-control evidence graph:** separate assertions connect addresses to named services and roles. Each assertion records its source, supporting events, validity period, when it became available, and any contradiction. An inferred link also retains its rule and version. This graph describes claims about control; it is not automatically proven ownership.

Seed inputs can include source-cited public tag collections and reviewed service confirmations. Public TagPacks are one possible starting point. [8] A public explorer label is a lead to review, not an authenticated statement from the service. No named-service database is conjured from transaction history.

Never turn every payment into a control link. Never identify two people merely because they paid the same deposit address. Never connect an exchange's unrelated withdrawal to a previous customer deposit as if its private ledger were public.

<!-- pagebreak -->

## 3. A concrete account-based detection rule

The reference implements a deliberately narrow rule for a plain token on one chain. It is inspired by the literature, not an exact reproduction of either paper. Native-asset tracing, rebasing tokens, transfer taxes, shared relayers and complex smart-account execution need separate handling. The thresholds below are demonstration choices, not published accuracy guarantees.

1. **Supply identity anchors.** H must have a sourced hot-wallet role and G a sourced service gas-feeder role for the same named service. Record chain, address, source family, event-time validity and when the evidence became known. A transfer from an arbitrary donor does not satisfy this condition.
2. **Check the observation window.** Require explicitly attested complete native/token history, relevant receipts and boundary balances. The reference starts with zero token and native balances. It trusts the completeness attestation supplied to it; a real collector must justify it. A single API page is not proof of completeness.
3. **Find complete cycles in ledger order.** A positive token receipt is followed by a service-gas top-up, then a direct sweep from D to H before the next receipt. The outgoing token units must exactly equal that cycle's incoming units. The receipt must identify D as the transaction sender and fee payer.
4. **Check accounting and contradictions.** Gas credits must cover the recorded fees; closing balances must reconcile. Conflicting service anchors, unexplained outflows, unsupported execution or missing records cause abstention: an explicit decision not to answer.
5. **Require repetition, then emit a hypothesis.** The toy policy requires three cycles and at least 100 integer token units per receipt. Neither is calibrated. The output remains an unconfirmed deposit candidate, with supporting references and no ownership probability.
6. **Bind the result to its evidence.** The reference checks the event/anchor snapshot, asset, window, cutoff and source-exclusion configuration before reuse. Changes to coverage, balances or rule policy also require rerunning detection; these are not covered by its reuse hash. Never promote a candidate into a trusted seed just because it passed the rule.

## Why this is a plausible lead, and why it is not proof

Repeated collection into known infrastructure plus service-specific fee support gives more operational context than a single payment. Victor describes exchange-seeded deposit heuristics and their false-positive risks. Brechlin and colleagues describe gas funding and token collection in one exchange case study. [1, 2] These findings justify testing the combined hypothesis; they do not validate our thresholds or generalise it to every VASP.

The reference rejects native outflows, including residual-gas returns, so it does not reproduce the entire Evonax sequence. Its strict conditions deliberately reduce coverage. It is also retrospective: identifying D at its first receipt may use later cycles observed before the analysis cutoff. This is not proof of immediate identification when the first payment happens.

<!-- pagebreak -->

## 4. Graph theory: the search has to respect time

Define nearest as **the fewest recorded transfer steps to a first supported custodial boundary, within the acquired evidence and declared limits**. It does not mean closest geographically, fastest arrival or guaranteed recovery. Return a frontier of first boundaries across branches; there may be several services rather than one universal answer.

A static graph can connect S to B using a payment at 12:00 and B to an exchange using a withdrawal at 11:00. That path is invalid for forward tracing. Temporal-graph research distinguishes several path objectives; our minimum-hop objective is a specific adaptation, not a claim to have invented temporal search. [4]

Each search state must include the chain-qualified location, asset, arrival ledger position, time and remaining budget. Reaching the same address later is a different state: its service role or available outgoing transfers may have changed. A permanent address-only visited flag can discard valid paths.

<!-- algorithm -->

In an explicit time-expanded graph, waiting edges can have cost 0 and transfer edges cost 1; 0-1 breadth-first search is one possible minimum-hop implementation. The reference instead uses event-aware bounded search. Search cost depends on the number of acquired events and surviving states; no real-world speed advantage is measured here.

Chronological connectivity is not proof that the victim's exact units funded every later transfer. Account balances may mix unrelated deposits. Even Bitcoin inputs can have several outputs without uniquely determining which input funded which output. Any allocation method must be named separately; different taint-allocation rules can yield different answers. [10]

## Bitcoin needs a different inference layer

Bitcoin uses **UTXOs**, individual transaction outputs that later transactions spend. Preserve those exact outpoint links for movement. Common-input, change-address and peel-chain heuristics may suggest common control, but collaborative transactions and ambiguous change can break those assumptions. Meiklejohn and colleagues illustrate seed-based attribution and dangerous over-merging; Kappos and colleagues investigate guarded peel-chain continuation. [6, 3]

The proposed Bitcoin extension retains each inferred link and its assumptions, checks wallet features, and refuses ambiguous expansion. Excluding recognised CoinJoin patterns does not prove single ownership. This Bitcoin clustering extension is not implemented in the new reference. The existing app's Bitcoin parser and outpoint traversal are separate capabilities.

<!-- pagebreak -->

## 5. What was built, and what the experiment shows

The isolated reference contains a strict token-pattern detector, sourced-anchor filtering, bounded temporal search, fictional fixtures, regression tests and reproducible JSON results. It performs zero external API calls and uses no real customer data. It is independent of the running app and its case database.

**Verified reference result: 64 synthetic tests passed; zero failures or errors.** The tests cover accounting, receipt evidence, source conflicts/exclusion, missing coverage, time order, chain separation, time-varying revisits, stale assessments and deliberate imitation. Passing these tests verifies the specified behaviours; it is not an attribution-accuracy percentage.

| Fictional scenario | Recorded outcome |
| --- | --- |
| Known labels only | Reaches the hot-wallet assertion at two hops; does not establish the nearest actual service. |
| Full strict pattern | Stops at the one-hop unconfirmed deposit candidate. Ownership remains unproven. |
| Missing coverage or required source | Keeps an unresolved boundary; does not substitute a farther hot wallet as a certain answer. |
| Same pattern, customer controls D | Indistinguishable from the service-controlled case. Still only a hypothesis. |
| Changed evidence or later revisit | Invalidates stale assessments; preserves distinct chronological arrival states. |

The two-hop comparison measures transfer connectivity only. A path using a later sweep must not be presented as amount-preserving tracing of the first deposit. The candidate detector's isolated-cycle checks do not turn general graph paths into monetary allocation proofs.

## Existing application versus new research

**Existing MVP:** case workspace, sourced labels, bounded chronological tracing, custody stops, source challenge, query budgeting, review controls and signed evidence export/replay. Stack: Python/FastAPI/Pydantic, SQLAlchemy with SQLite WAL, React/TypeScript/Vite and Cytoscape. ReportLab creates reports; SHA-256 and Ed25519 support evidence integrity. The separate product foundation adds migration/worker/PostgreSQL checks; it is not a completed production deployment.

Recorded release verification includes 116 MVP backend tests and browser checks. A bounded real Bitcoin acquisition returned two transactions and three outputs, but established no VASP. Six implemented parsers do not demonstrate six-chain live attribution. No new live attribution claim is made in this review.

**Research-only now:** automated deposit inference, broader Bitcoin clustering and comparative accuracy evaluation. No ownership ML model or LLM is implemented. The reference can be reproduced with `python research/method-review-20260929/reference/run_experiment.py`. Its README, exact inputs and machine-readable results accompany this paper in the project.

<!-- pagebreak -->

## 6. How to find out whether this actually works

We need independently confirmed deposit roles and difficult ordinary-customer examples. The labels used to create a prediction cannot also be its only alleged ground truth. Ghost Clusters demonstrates why service records and address roles matter when evaluating attribution coverage. [5]

**Freeze the evidence at a historical cutoff.** Only transactions and labels available by that cutoff may be used. Hide the tested deposit labels, retain permitted hot/gas seeds, and keep threshold development separate from the final test. Split by time and wallet family; report known-service expansion and genuinely unseen-service performance separately. The latter cannot produce a name without an external identity anchor.

**Compare four baselines under the same case scope and budget:** exact address lookup; temporal search to exact labels; sweep-only deposit inference; and the proposed sweep-plus-service-operation evidence. Also remove the gas evidence, chronology constraint and conflict checks in controlled ablations to see what each contributes.

| Measure | What it answers |
| --- | --- |
| Service and deposit-role precision | Among answered claims, how many identify the correct operator and role? Report both separately. |
| Answer coverage and abstention | How often does the method answer, and how often does it explicitly stop? |
| False merges and path errors | Does it join unrelated users or accept impossible/unsupported routes? |
| Nearest-boundary correctness | On completely observed bounded cases, is an earlier receiving boundary missed? |
| Calls, latency and review time | Does it save resources and investigator effort on the same tasks? |

Report sample sizes, uncertainty intervals, failures and the reasons for abstention. Test exchange customers, merchant forwarding, shared gas sponsors, exchange-to-exchange traffic, adversarial imitation, batched sweeps, CoinJoin/change ambiguity, truncated histories and chain reorganisations. Do not evaluate only clean examples that were designed to pass.

## What could differentiate TraceSetu?

The defensible hypothesis is the combination: **discover an earlier candidate, show precisely why it is suspected, preserve nearer gaps, let an analyst remove a source or inference, and spend the next API call on evidence that could change the decision**. Existing bounded custody, source challenge, query budgeting and reviewed feedback provide a place to integrate this method. Superiority must be measured against the baselines above.

Graph visualisation, clustering and compliance reports already exist. GraphSense is an example of established graph analytics and sourced tags. [8] Adding a generic graph neural network does not solve the missing identity problem: the Elliptic task studied by Weber and colleagues classifies licit/illicit transactions, not the company controlling a deposit address. [9] Learned ranking is a later option only with suitable independent labels.

<!-- pagebreak -->

## 7. How this fits the complete SIH solution

| Requirement from the supplied statement | Intended design and honest current boundary |
| --- | --- |
| Analyse a suspect wallet from SAHYOG | Validated case input and authenticated API workflow exist locally. Official SAHYOG contracts/access are still required. |
| Nearest exchange or custodial VASP | Existing bounded tracing uses supplied labels. New seeded deposit discovery is an isolated research reference awaiting independent evaluation and integration. |
| Bitcoin, Ethereum, Tron, BNB, Solana, Polygon | Six read-only adapters/parsers exist. Live access and completeness vary. Only bounded Bitcoin acquisition has the recorded nonempty live check described here. |
| Clusters, hot/deposit wallets, mixers, bridges, swaps | Preserve role-specific assertions. Broader discovery is not complete. A mixer or unsupported bridge creates a visibility limit, not an invented connection. |
| Cross-chain mapping | Require verifiable protocol/service evidence. Existing CCTP V2 native-USDC Ethereum/Polygon proof scope has synthetic validation; broad cross-chain attribution is unproven. |
| Tags, confidence, risk and alerts | Keep operator/role evidence separate from risk. Current rule grades are not calibrated probabilities; production risk feeds, calibrated scores and alert operations remain incomplete. |
| Graph, dashboard and reports | Existing case UI, movement graph and signed evidence export support review. A signature proves package integrity, not the truth of every source assertion. |
| Disclosure/freezing routing | Prepare a scoped request for a verified recipient and independent review. Local exports remain NOT_SENT; the receiving institution controls disclosure and freezing. |
| Real-time and large-volume operation | Caches, budgets and worker foundation exist. Provider quotas, indexing, independent load/security validation and agency deployment remain gates. |

Cross-ledger research shows the value of service-specific evidence; matching amount and time alone is not universal proof that two chain events belong to the same transfer. [7] Likewise, an unsupported protocol route or missing page must not become a fabricated edge.

## Practical next implementation gates

First build a reviewed, source-qualified seed register and a collector that can account for missing pages, receipts, balances, finality and rate limits. Public TagPacks may supply leads, subject to source/usage review; they are not independent truth. [8] Next obtain authorised deposit-role confirmations, reproduce baselines and evaluate the new rule. Only then integrate candidate search, challenges and feedback behind explicit evidence statuses. Separate work is needed for chain-specific rules, scale and official portal integration.

## A short explanation for judges

“We separate two questions: where did the assets move, and which company may control the receiving address? We use sourced service wallets and explicit pattern rules to suggest unlabelled deposit addresses, then search transfers in time order to the first supported custody point. Inferences retain their evidence and can be challenged. Our prototype supports the investigation workflow; the new rules are tested separately on synthetic cases. Independent deposit records are the next gate before we claim real-world accuracy.”

<!-- pagebreak -->

## 8. Primary research and reading guide

The sources below motivate the design and its limits. TraceSetu does not inherit their reported performance, and this paper is not a peer-reviewed accuracy study. Research review and local experiment completed on 29 September 2026.

**[1] Friedhelm Victor (2020). Address Clustering Heuristics for Ethereum. Financial Cryptography and Data Security, pp. 617-633.** Section 5.1 and Algorithm 1: exchange-seeded deposit inference and false-positive limitations. Historical thresholds are not our calibrated rules. [Read the paper](https://fc20.ifca.ai/preproceedings/31.pdf).

**[2] Alexander Brechlin, Jochen Schäfer and Frederik Armknecht (2025). Buy Crypto, Sell Privacy: An Extended Investigation of the Cryptocurrency Exchange Evonax. International Journal of Network Management 35(1), e2325.** Section 5.1/Figure 4: service-specific token deposit, gas funding and collection. One service case does not establish a universal rule. [Publisher / DOI](https://doi.org/10.1002/nem.2325).

**[3] George Kappos et al. (2022). How to Peel a Million: Validating and Expanding Bitcoin Clusters. USENIX Security, pp. 2207-2223.** Sections 4-5 and 7: wallet features and guarded peel-chain continuation; its study's error rate is not TraceSetu accuracy. [Read the paper](https://www.usenix.org/system/files/sec22-kappos.pdf).

**[4] Huanhuan Wu et al. (2014). Path Problems in Temporal Graphs. Proceedings of the VLDB Endowment 7(9), pp. 721-732.** Sections 2-5: time-respecting paths and distinct optimisation objectives. Our transfer-hop objective is an adaptation. [Read the paper](https://www.vldb.org/pvldb/vol7/p721-wu.pdf).

**[5] Kelvin Lubbertsen, Michel van Eeten and Rolf van Wegberg (2025). Ghost Clusters: Evaluating Attribution of Illicit Services through Cryptocurrency Tracing. USENIX Security, pp. 1357-1374.** Independent service data, deposit/internal roles, flow coverage and historical attribution limits. [Read the paper](https://www.usenix.org/system/files/usenixsecurity25-lubbertsen.pdf).

**[6] Sarah Meiklejohn et al. (2013). A Fistful of Bitcoins: Characterizing Payments Among Men with No Names. ACM Internet Measurement Conference.** Sections 3-4: identity seeds plus clustering, including harmful false merges. [Read the paper](https://cseweb.ucsd.edu/~smeiklejohn/files/imc13.pdf).

**[7] Haaroon Yousaf, George Kappos and Sarah Meiklejohn (2019). Tracing Transactions Across Cryptocurrency Ledgers. USENIX Security, pp. 837-850.** Service-assisted cross-ledger linking; historical evidence access is not a current universal capability. [Read the paper](https://www.usenix.org/system/files/sec19-yousaf_0.pdf).

**[8] Bernhard Haslhofer et al. (2021). GraphSense: A General-Purpose Cryptoasset Analytics Platform.** Existing graph analytics and provenance-oriented attribution. Public tags still need source and role review. [Paper](https://arxiv.org/abs/2102.13613) and [public TagPacks](https://github.com/graphsense/graphsense-tagpacks).

**[9] Mark Weber et al. (2019). Anti-Money Laundering in Bitcoin: Experimenting with Graph Convolutional Networks for Financial Forensics.** Illicit/licit classification is distinct from named-service and deposit-role attribution. [Read the paper](https://arxiv.org/abs/1908.02591).

**[10] Ross Anderson et al. (2018). Bitcoin Redux. Workshop on the Economics of Information Security.** Sections 3.2-3.3: allocation conventions can change taint results. This is technical context, not current Indian legal authority. [Read the paper](https://www.cl.cam.ac.uk/archive/rja14/Papers/bitcoin-redux.pdf).
