# Differentiation specification: from an exchange guess to a reviewable action

Updated 25 September 2026 (India time). This is a product/design decision record, not a claim of worldwide uniqueness. The status table distinguishes implemented mechanisms from proposed extensions. The user has deferred the full production build in favor of a working SIH MVP; the 50-page main report remains the future target architecture.

## Product position

For an investigator who starts with an unknown wallet, deliver a ranked first-custody result, an inspectable explanation of the evidence and missing information, the cheapest useful next investigation step, and a reviewed request packet to the verified service entity. The proposed advantage is the combination of decision quality, cost control and reproducibility in the MHA/I4C workflow.

The operational objective is time to a **correct, review-ready receiving-service determination**, subject to an acceptable false-routing rate and known data coverage. Do not optimise for the percentage of queries that return a confident-looking exchange name.

## What the competition already has

| Offering reviewed | Publicly described capability | Consequence for our positioning |
| --- | --- | --- |
| [Chainalysis Reactor](https://www.chainalysis.com/product/reactor/) and [Rapid](https://www.chainalysis.com/product/rapid/) | Entity tracing, graph analysis, triage and packaging intelligence for investigative/legal workflows. | A graph plus an AI summary plus a PDF is not a defensible innovation claim. |
| [TRM Triage](https://www.trmlabs.com/blockchain-intelligence-platform/triage) | Frontline crypto-artifact triage and actionable investigative guidance. | Ease of use and triage alone are insufficient differentiation. |
| [Elliptic Investigator](https://www.elliptic.co/products/investigator/) | Automatic graph generation, entity attribution and one-click cross-chain tracing. | Multi-chain tracing is baseline functionality, not our unique selling point. |
| [GraphSense](https://graphsense.org/) | Open-source analytics, algorithmic transparency and data sovereignty. | Open source, self-hosting and explainability are not unique by themselves. |
| [Iknaio platform](https://iknaio.com/platform/) | Pathfinder, CaseConnect and QuickLock are described as investigation, collaboration and action tooling. | Case linking and action assistance also have prior examples. |

These are supplier descriptions, not hands-on comparisons. Absence of a feature from a public page does not establish that a competitor lacks it. No exhaustive patent, procurement or product evaluation has been performed.

## D1. Bounded first-custody frontier with a nearestness certificate

**Investigator problem:** a platform may return a distant famous exchange while a closer receiving service, a branch, or a missing page is overlooked.

**Implementation:** build a time-respecting frontier that stops each path at its first sufficiently supported custody boundary. Return all qualifying minimum-distance candidates, alternate later paths, unresolved branches and the evidence snapshot. Keep the nearest view separate from an operational-priority view.

**Certificate fields:** seed and scope, ledger checkpoints, normalised movement-event hashes, attribution assertion versions, permissible hop definition, exhausted depths, pruning rules, pagination/decoder gaps, candidate paths and the deterministic algorithm/configuration version.

**Two different claims:** `nearest_known_target_in_snapshot_proven` concerns a deterministic search over the collected, qualified graph. `nearest_real_vasp_proven` concerns reality outside that graph and normally remains false when intermediary custody is unknown. Complete pagination does not imply complete identity labels. An unlabeled intermediary can still be a VASP.

**Acceptance:** an independent offline verifier reproduces the shortest qualified targets in the snapshot; a truncated lower-depth frontier invalidates the corresponding completeness claim; a known closer service cannot be bypassed to reach a famous farther exchange. Adding a newly verified intermediate service correctly changes the first boundary.

## D2. Challenge the answer before an investigator acts

**Investigator problem:** an apparently strong result may depend entirely on one stale label, one inferred cluster or one ambiguous bridge edge.

**Implementation:** run controlled sensitivity checks over the frozen evidence: remove each critical assertion/provenance family, reject heuristic-only edges, change a disputed cluster membership and compare candidates, distances, route validity and amount bounds. Display the smallest known evidence dependencies that make the recommendation change.

**Important limit:** this is evidence sensitivity, not a probability of truth. If removing an assertion opens a previously stopped service frontier for which history was never fetched, return `requires_expansion`; do not pretend the alternative search was complete. Shared upstream label sources are removed together when their dependence is known.

**Acceptance:** a candidate supported only by one assertion loses its supported identity when that assertion is removed. Independent corroboration is visible. The interface explains what changed without inventing a new owner. A disputed mixer link never becomes a verified path solely because it preserves the preferred answer.

## D3. Spend API credits where they can change the decision

**Investigator problem:** blind expansion burns a large query budget on high-fan-out wallets without resolving the actionable receiving service.

**Implementation:** queue unresolved subjects and assign a transparent priority using lower hop distance, whether the question can change the first-custody answer, stale/conflicting identity evidence, incident relevance, endpoint availability and incremental credit cost. Batch compatible label calls and share permitted public-chain cache entries. Reserve a portion of budget for completing shallow frontiers.

Use a versioned deterministic policy first. Do not call its score an expected-information-gain probability before that claim has been validated. The UI shows the next query and a reason such as "classifying this one-hop intermediary could supersede the current three-hop candidate."

**Acceptance:** benchmark against chronological breadth-first expansion, a fixed-depth baseline and cost-matched alternatives on the same authorised datasets. Compare useful-answer rate, missed first services, precision, spend and latency. Proposed release gate: no material precision degradation, and a statistically reported cost or time advantage on the held-out workload. No efficiency percentage is claimed before measurement.

## D4. Turn authenticated VASP responses into reusable evidence

**Investigator problem:** an agency repeatedly asks the same service to resolve a deposit address, while old responses remain unstructured in case attachments.

**Implementation:** accept the service response as an immutable artifact, validate its authorised channel/signature, capture the precise address/control/role/time scope and require review before publishing a new service assertion. Associate legal-entity and recipient versions. Re-evaluate dependent cases after confirmation or correction, subject to agency permissions and data-use rights.

**Trust rule:** a signature proves control of a key; it does not identify a VASP unless that key's binding was independently verified. A PDF on official-looking letterhead is not automatically authenticated. KYC and customer-account data stay restricted; approved reusable service-level facts are separated from private case data.

**Acceptance:** forged/untrusted responses are quarantined. A valid scoped confirmation upgrades only its permitted subject/interval. A correction retracts affected findings and generates a superseding report. Cross-agency information cannot leak through the cache or feedback channel.

## D5. A portable evidence package that survives provider changes

**Investigator problem:** a graph screenshot is hard to reproduce when a subscription ends or labels change.

**Implementation:** export original artifacts where permitted, normalised facts, a minimal selected graph, assertion versions, assumptions, coverage, software/configuration versions and a signed manifest. Provide an offline integrity and replay verifier. The report distinguishes source authenticity, integrity and attribution truth.

**Acceptance:** replay reproduces material findings; modified files fail hash verification; missing licensed artifacts are disclosed rather than fabricated. The verifier does not certify judicial admissibility or convert a supplier assertion into a fact.

## Practical, lawful engineering shortcuts

1. **Use existing parsers and indexing infrastructure where appropriate.** Evaluate GraphSense components and per-dataset TagPack licences rather than rebuilding every ingestion primitive. Its open-source status does not make every external dataset unrestricted, nor prove six-chain coverage.
2. **Buy intelligence selectively.** Fetch verifiable chain history first, query labels in batches at decision-relevant frontiers, cache only within contract terms and refresh when evidence freshness matters. Measure actual billing units; batching requests may not reduce per-address charges.
3. **Reuse verified service facts, not guessed identities.** Agency-reviewed confirmations and corrected assertions can improve future coverage without exposing customer records.
4. **Make uncertainty productive.** A result can explain the missing dependency and propose an authorised next step instead of manufacturing a service name.
5. **Use provider-specific fallback honestly.** An unavailable API produces a resumable partial result. It never becomes an invisible synthetic response or an unauthorised scraped substitute.

## What we will not pitch as innovation

Generic AI summaries; a decorative blockchain dashboard; unsupported "99% accuracy"; magic mixer deanonymisation; a universal freeze button; identifying beneficial owners from public wallet syntax; simulated SAHYOG receipts presented as live integration; or renamed standard graph algorithms.

## Demonstration designed to reveal failures

Use visibly labelled synthetic cases for adversarial algorithm demonstrations and separate independently reviewed real-chain cases for factual evidence validation. Show: a closer VASP hidden by a stale label; a two-source conflict; a completed versus truncated shallow frontier; an ambiguous bridge; a mixed-funds amount bound; a controlled credit budget; an authenticated confirmation and a forged reply; and a tampered evidence file.

The demonstration should allow a reviewer to change an input or remove an assertion and observe the result change. A fixed video or handpicked graph alone does not pass.

## Status and next engineering gates

| Capability | Current status | Proof needed |
| --- | --- | --- |
| Competitive differentiation specification | Researched and recorded | Continue reviewing new evidence; never claim exhaustive uniqueness. |
| First-custody certificate | Implemented; synthetic regression and replay tests pass | Independent labelled evaluation and real provider coverage. |
| Assumption challenge | Implemented; newly opened frontier and browser checks pass | Wider adversarial and real-world evaluation. |
| Query planner | Cost-aware advisory allocation plus explicit selected-plan execution, immutable parent preservation, durable per-job budgets/cache across recovery and conflict holds; API/browser checks pass | Live execution validation, cross-job quotas, cost-matched held-out benchmark and ablation. No measured efficiency improvement claim yet. |
| Confirmation feedback | Key/request-bound signed import, scoped promotion, reviewed withdrawal, stale-result guards and reassessment implemented; synthetic API tests pass | Real provider trust onboarding, automatic signed correction formats, permissioned cross-case propagation and distributed revocation. |
| Evidence export/replay | PDF/CSV/JSON/raw evidence, Ed25519 ZIP and offline verifier implemented | Licensed artifact policy, trusted agency signing and external immutable retention. |
| Full six-chain operational product | Independent application works on explicit training evidence; adapters implemented; CCTP V2 Ethereum/Polygon protocol proof, review and replay work on synthetic cases | Live data validation, additional bridge/swap protocols, security, scale and official integration gates remain. |

No competition-win guarantee or claim that nobody else implements these mechanisms is made. The defensible claim will be the capability set we can demonstrate and the measured benefit it delivers.
