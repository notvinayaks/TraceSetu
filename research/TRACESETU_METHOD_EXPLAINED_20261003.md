# How TraceSetu would identify the receiving service

3 October 2026. This explains the implemented tracing engine, the separate deposit-candidate experiment and the work still needed to combine them. It does not resume the stopped full-product build.

## The problem in one sentence

An officer has a cryptocurrency address from a complaint and needs to find which exchange or custodian received funds, so that an authorised request can reach the appropriate service. A VASP is a company providing services such as exchanging or holding cryptocurrency. Bitcoin is a cryptocurrency/network, not a VASP.

The public blockchain usually provides transfers between addresses. It does not provide the exchange's customer account register. Two separate questions therefore matter:

1. **Tracing:** which recorded transfers connect the reported address to a receiving address?
2. **Attribution:** what evidence connects that receiving address to a named service, and does it establish a deposit role?

A transaction graph alone cannot supply a justified company name when no external identity evidence exists. Adding an AI model or a graph database does not remove this information requirement.

## The method we can defend

**Source-linked service labels, a rule-based deposit-pattern test, and bounded chronological breadth-first search.** The first and third parts support the current app. The new deposit-pattern test is separate research code with synthetic tests. It is not yet integrated into live acquisition or the dashboard.

### 1. Where the service names come from

A service register associates `(blockchain, address)` with a service, an address role, an evidence source, a validity period and when we learned the assertion. A role can be a deposit wallet, a collection/hot wallet or a fee-funding wallet. These roles are different: a company-controlled address does not automatically accept customer deposits.

Permitted public labels with source links, published service records and independently reviewed service responses can supply assertions. For example, GraphSense Public TagPacks explicitly package address labels with their source URLs. Its WalletExplorer pack contains historical Bitcoin exchange assertions. A tag's update date does not establish when the exchange actually controlled the address. These tags would need review before use for an event-time claim. A service's proof-of-reserves address may establish a control claim without establishing a customer-deposit role.

**Current access:** the app has an optional Etherscan `getaddresstag` connector. Etherscan lists address metadata under paid metadata access, so we cannot treat it as an available free label feed. The code retains a returned current nametag as a hypothesis with an unknown role. A reviewed GraphSense import is a proposed addition, not a connector already implemented in this release. Public/free APIs give uneven transaction and label coverage. With no supporting label, the answer remains unknown.

Sources: [GraphSense Public TagPacks](https://github.com/graphsense/graphsense-tagpacks), [historical WalletExplorer pack](https://github.com/graphsense/graphsense-tagpacks/blob/master/packs/walletexplorer.yaml), [Etherscan API plans](https://etherscan.io/apis).

### 2. How an unknown deposit address becomes a lead

Use four fictional names for a reproducible example:

```text
Reported wallet R ── tokens ──> unknown D ── token sweep ──> H
                                    ↑                     collection wallet
                                 fee funding              asserted: Service E
                                    │
                                    G
                             fee-funding wallet
                             asserted: Service E
```

H and G already have external role assertions for E. D does not. The program tests D's observed behaviour against those assertions. It is investigating whether D could be a deposit address controlled by E, rather than merely a customer who pays E.

The research reference uses a deliberately narrow test:

- One plain token and its chain's native fee asset, within a declared observation window.
- Complete history attested for that window, actual transaction receipts and exact opening/closing balances. The program checks these supplied records; it cannot itself prove the provider omitted nothing.
- Zero opening token/native balances and one token receipt at a time.
- After the receipt, G supplies the native fee asset. D then directly signs and pays for a transfer of the exact received token units to H.
- H and G have non-conflicting, date-valid role assertions for the same service. An assertion learned later cannot enter an earlier evaluation cutoff.
- Repeated complete cycles, no unexplained activity, and balances that reconcile. Relayers, rebasing/fee tokens, residual native outflows and other unsupported activity cause abstention.

The existing fixture has these exact numbers:

| Cycle | Tokens received by D | Native funding from G | Tokens sent to H | Native fee paid by D |
|---|---:|---:|---:|---:|
| 1 | 1,000 | 100 | 1,000 | 10 |
| 2 | 2,000 | 100 | 2,000 | 10 |
| 3 | 3,000 | 100 | 3,000 | 10 |

The token closing balance is `0 + 6,000 - 6,000 = 0`. The separate native closing balance is `0 + 300 - 30 = 270`. These are integer base units of two fictional assets, not token prices or real transfers. The three events in each cycle appear in receipt/funding/sweep order. The synthetic policy requires three cycles and a minimum incoming amount of 100 units; neither threshold is calibrated to field data.

The output is **“D is an unconfirmed deposit candidate for E.”** Even an exact match cannot prove ownership: a customer can reproduce every public event in the example. Further role evidence or an independently verified service confirmation is necessary. The system must never automatically reuse its own inferred candidate as a trusted seed. A retrospective match after three cycles also cannot establish that the system knew the answer at the first deposit.

The research motivation is specific. Victor (2020), section 5.1, uses forwarding to known exchange addresses to identify possible deposit addresses. Its separate customer-clustering result must not be misread as “all senders belong to the exchange.” Brechlin et al. (2025), section 5.1, describe Evonax's fee-funding/collection behaviour and use service records to confirm address roles. Our narrow rule is an adaptation, not an exact reproduction or a universal exchange detector.

Sources: [Victor, FC 2020](https://www.ifca.ai/fc20/preproceedings/31.pdf), [Brechlin et al., 2025](https://onlinelibrary.wiley.com/doi/10.1002/nem.2325).

### 3. How the search finds the first receiving service

Create a directed graph of successful transfer events, retaining chain, asset, amount, transaction identity, ledger position and source evidence. Search states contain the address, arrival event, asset and path. An address alone is not enough: arriving at the same address later can lead to different valid transfers or identity assertions.

```text
queue := [reported address at the start of the case window]
while the queue is nonempty and the search budget remains:
    take the next state in increasing transfer count
    look up service assertions valid at its arrival event
    if supported custody exists: record it and stop this branch
    if an assessed deposit candidate/gap exists: record it and stop
    otherwise append eligible outgoing transfers in ledger order
return branch stops, paths, consulted evidence and remaining gaps
```

Chronology prevents using an outgoing transfer that happened before the incoming transfer. Hop/state/API limits prevent unlimited expansion. Source conflicts and incomplete acquisition remain visible. In the example, labels alone reach H at two transfers. A passing deposit assessment surfaces D at one transfer as an unconfirmed lead. Removing G's service evidence makes D unresolved; the system must not quietly skip D and describe H as the proven nearest deposit receiver.

“Nearest” means the fewest observed transfers in the recorded search scope, with a separate first-custody stop on each branch. It does not mean geographical proximity, largest flow, or guaranteed nearest actual custody. Account-graph connectivity also does not prove that the exact same money units traversed a path. The system stops at a custodial service instead of joining the customer's deposit to an arbitrary pooled withdrawal.

The app indexes outgoing events and uses a queue. The small research reference scans its fixture for each search state; it is not a scalable whole-chain index. Production work would need indexed acquisition, bounded state expansion and measured provider/worker performance. Temporal graphs are established prior art: [Wu et al., PVLDB 2014](https://www.vldb.org/pvldb/vol7/p721-wu.pdf).

## Different chains require different evidence

Bitcoin gives explicit links from spent transaction outputs to later inputs. A transfer's output allocation does not by itself prove which input owner's money funded each output. Common-input/change/peel clustering would be a guarded future extension; joint transactions such as CoinJoin and PayJoin can invalidate a blanket shared-control assumption. [Kappos et al., USENIX 2022](https://www.usenix.org/system/files/sec22-kappos.pdf) provides relevant Bitcoin clustering research.

The token-fee pattern above cannot simply be copied across Bitcoin, Tron and Solana. The existing six read-only adapters normalise data, but equal live coverage or attribution performance has not been established. A cross-chain continuation needs a matched protocol/service proof. The implemented CCTP V2 ETH/Polygon native-USDC proof workflow has training validation only. Unsupported bridges, swaps and mixers remain gaps.

## Why an officer would use this

An explorer can show individual transfers. The proposed value is doing the bounded search reproducibly, showing the source of each service claim, recording which nearer possibilities remain unresolved, and prioritising the next evidence acquisition within a call budget. An officer can remove a disputed source and see how the answer changes without losing the earlier record. Reviewed service feedback can improve later cases while preserving provenance.

This combination is our testable contribution. Graph display, labels and case CRUD already exist elsewhere. We have not established scientific uniqueness, superior accuracy or a measured time saving.

## What is built, and what remains

| Status | Capability |
|---|---|
| Implemented in prototype/foundation | Chronological sourced-label tracing, custody stops, scope/gap certificate, source challenge, budgeted query planning, permissions/review, signed evidence export, separate workers and PostgreSQL support. |
| Separate research reference | Narrow repeated deposit/fee/sweep matcher, candidate frontier, 64 synthetic functional/adversarial checks. Not connected to the live UI. |
| Public acquisition verified in a bounded case | Two Bitcoin transactions and three outputs reproduced. No VASP established. This validates data handling, not ownership attribution. |
| Still required | Reviewed live seed registry, matcher integration, independent deposit-role evaluation, wider chain coverage, shared quotas/fairness, load/fault tests and institutional controls. |
| External gate | Approved SAHYOG access and authorised VASP cooperation. Current request packages remain NOT_SENT. |

## The evaluator's four questions

**Novelty:** test whether preserving nearer unresolved boundaries and directing the next query reduces wrong recipients or unnecessary API calls. Compare the complete workflow with label-only tracing and manual explorer work under the same budget.

**36-hour feasibility:** a bounded case-to-reviewed-export demonstration on our existing code is feasible. A complete national platform, service ground truth and independently validated six-chain attribution from scratch in 36 hours are not credible claims.

**Ministry practicality:** separate API/worker processes, durable jobs, bounded searches and evidence records provide a foundation. National use additionally needs governed labels, shared quotas, agency fairness, SSO/MFA, official integration and measured load/failure behaviour. Extra servers alone cannot solve missing identity evidence.

**Technology:** Python/FastAPI for rules and APIs; React/TypeScript/Cytoscape for review and graphs; PostgreSQL with workers for durable jobs, SQLite locally; SHA-256 and Ed25519 for export integrity. Cryptographic signatures protect records against changes, not against false source claims.

## What would demonstrate that it works

Use independently confirmed service deposits and realistic negative examples, keeping the labels used for prediction separate from the evaluation truth. Split evaluation by time and service so later labels do not leak into earlier cases. Measure correct service and deposit role, wrong attributions, missed deposits, answer coverage/abstention, API requests and investigator time. A perfectly imitated public pattern is an important negative case. Sixty-four passing synthetic checks are not 64 correct real-world attributions or an accuracy percentage.

Independent role/coverage evaluation follows the concern demonstrated by [Lubbertsen et al., Ghost Clusters, USENIX 2025](https://www.usenix.org/system/files/usenixsecurity25-lubbertsen.pdf).

## Reproducible project evidence

- App tracing: `backend/vasp_app/engine.py` and `domain.py`.
- Optional metadata connector and access limitation: `backend/vasp_app/providers.py::evm_metadata`.
- Research rules and exact fixture: `research/method-review-20260929/reference/method.py` and `fixtures.py`.
- Synthetic checks and recorded outcomes: the same directory's `test_method.py` and `results.json`.
- Deployment scope and open gates: `docs/OPERATIONS.md`, `IMPLEMENTATION_CHECKLIST.md` and the complete project handover.
- [Public code and completed research](https://github.com/notvinayaks/TraceSetu/tree/product/live-foundation).

The defensible claim is a working evidence-led tracing foundation and a reproducible, limited deposit-candidate method. Universal unknown-wallet attribution and national deployment remain unproven.
