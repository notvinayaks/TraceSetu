# Prototype capability and limits register

Scope: the working local SIH prototype as packaged on 26 September 2026. Full production infrastructure remains future work. This source repository does not include the original machine's private case database or its generated reports.

| Capability | Current evidence / limit |
|---|---|
| Wallet intake and case dashboard | Authenticated APIs, roles, case permissions and local worker are implemented; official SAHYOG intake is not connected. |
| Nearest receiving VASP | Deterministic first-custody traversal, service/role assertions, conflicting/unknown states and snapshot-bounded nearestness certificate. Real ownership requires reliable labels; no beneficial-owner identification. |
| Six-chain acquisition | Bitcoin, Ethereum, BNB Chain, Polygon, Tron and Solana adapters and parser tests. Bounded live Bitcoin acquisition was checked during development; broad live multi-chain/ownership validation remains pending. |
| Clusters, hot/deposit wallets, mixers | Sourced assertion categories are supported. No automatic ownership clustering or inferred mixer deposit-to-withdrawal mapping. |
| Bridges / swaps | Scoped CCTP V2 native-USDC Ethereum/Polygon proof validation and synthetic review workflow. Live CCTP and general bridges/swaps are not validated or implemented universally. |
| Confidence / risk | Categorical evidence grades, source-linked risk tags, conflicts and unassessed states. No calibrated accuracy percentages or automatic criminality claims. |
| Differentiation | Bounded first custody, inspectable nearestness, source challenge, budgeted next query and reviewed service feedback are implemented. Comparative time/cost/accuracy advantages have not been measured. |
| Reports | PDF, JSON, CSV, signed evidence bundles and replay. Integrity is not a legal admissibility guarantee. |
| Request routing | Reviewed recipient, two-person payload review and local export. Official SAHYOG delivery, VASP onboarding, real notices and asset freezes are not connected. |
| Alerts | Local watched-wallet case updates and sourced risk indicators. General laundering-typology detection and external notifications are future work. |
| Scale / deployment | Single-node local validation, bounded workloads and per-job durable request budgets. PostgreSQL/Docker recipes exist; distributed quotas, production concurrency, backups, security accreditation and high-volume benchmarks remain open. |

The backend test suite covers explicitly synthetic algorithm, provider/parser, execution, permissions, protocol and evidence workflows. It is not an independent real-world attribution benchmark. Fresh-install and publication checks are recorded in [release verification](RELEASE_VERIFICATION.md).

External dependencies include licensed identity data where required, provider entitlements, independently verified recipient identities, agency authentication/MFA and official SAHYOG contracts/access. The prototype does not simulate these as successful operational connections.
