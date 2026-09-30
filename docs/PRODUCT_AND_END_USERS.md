# TraceSetu — problem, end users and solution brief for a new agent

**Current steering (25 September):** the user explicitly requested the real public-case recording, then approved TraceSetu and asked to continue. That authorization supersedes earlier UI-approval holds below. Current delivery and live-case facts are in `docs/TRACESETU_SUBMISSION.md`; older measurements below remain historical evidence.

This brief is part of the self-contained project skill. It records the intended users and product reasoning, not the results of user interviews or an institutional procurement agreement. Read it together with the exact supplied problem statement, the 30-row requirement matrix and the implementation evidence embedded in that skill.

## The problem we are solving

An authorised investigator may have a cryptocurrency address linked to a reported incident but not know which exchange or custodial provider can respond to a lawful information request. The address may be unhosted, unlabelled or separated from a service by intermediate transfers. Searching a blockchain manually can be slow and can produce a misleading destination if the investigator follows an exchange's unrelated withdrawals.

The useful question is: **which receiving service is first supported by the available evidence on each relevant path, and what remains unknown before an investigator can act?** It is not enough to draw a graph or identify a famous exchange somewhere downstream. The result needs source evidence, correct chronology, stated scope, a verified legal recipient and a reviewed action package.

The user supplied the SIH context: **Ministry of Home Affairs; Indian Cyber Crime Coordination Centre (I4C), CIS Division; Software; Blockchain & Cybersecurity**. The exact official problem ID and listing URL were not verified. This context does not establish endorsement, a government deployment, a customer contract or government-exclusive licensing.

## End users and the outcome each needs

| User / stakeholder | What they bring or need | How the current MVP supports them | Boundary to preserve |
|---|---|---|---|
| Investigating officer / LEA investigator | Case reference, reported wallet, correct chain, investigation window; a defensible next step | Creates a case, runs an analysis, inspects the graph/evidence/gaps, proposes evidence and prepares a request | A finding is bounded intelligence, not proof of beneficial ownership, criminality or recovery |
| Technical blockchain analyst | Source inspection, exact amounts, chain semantics, disputed labels and incomplete branches | Transfer/UTXO inspection, raw evidence, source-family challenge, nearestness certificate, query planning/execution and replay | “Analyst” is a job function; the app currently has investigator/reviewer/admin roles, not a separate analyst account type |
| Independent reviewer / supervisor | Assurance that evidence, recipient and requested scope have been checked | Reviews exact evidence/recipient/request versions; self-approval is rejected; withdrawn support triggers stale-result safeguards | The reviewer must be a different authorised user with the required case access; approval is not automatic legal authority |
| Authorised legal / disclosure coordination staff | Correct service/legal entity, current contact, reviewed legal basis and minimal scope | Recipient evidence, matching, expiry, request review and export are available through the existing roles | No dedicated legal-role UI or live SAHYOG delivery is implemented. Jurisdiction and legal authority require the authorised process |
| Agency administrator / operator | Controlled accounts, case access and a working local installation | Admin account management, local bootstrap, role/case checks and documented configuration | Agency SSO/MFA, external key governance, large-scale operation and production retention are future work; do not claim all are managed in the UI |
| VASP compliance / law-enforcement response team | A properly routed, evidence-bound request; a way to return a trustworthy scoped response | The local request/Ed25519 response model and independently reviewed response promotion are demonstrated with training data | VASPs are external counterparties, not onboarded customers or users of a finished VASP portal; no real response integration is claimed |
| Victim / complainant | A more effective authorised investigation | Indirect intended beneficiary of the investigator workflow | There is no citizen complaint or victim recovery portal in this MVP, and no promise of freezing or recovery |
| I4C / agency integration and security teams | Reliable contracts, access controls, auditability and deployment assurance | API contracts, evidence model and complete target architecture are documented | Official SAHYOG access, institutional acceptance, security accreditation and operational evaluation remain external gates |
| SIH judges / demonstration audience | Understand the problem, see the working mechanisms and assess honest scope | The polished UI, public “How it works” guide, labelled training exercises and recorded live Bitcoin evidence support explanation | A judge viewing a prototype is not a production user; a compelling demo does not prove deployment readiness |

The initial target users are authorised investigative teams. Other permitted institutional compliance uses may be a future possibility, but the user has not selected a commercial market, price, licence or business model. Do not invent one for a PPT.

## Our solution, in one end-to-end journey

1. **Intake:** record a case, permitted users, a chain-qualified wallet and UTC time window. A future official SAHYOG caller would use an approved integration contract; today the independent case UI/API performs intake.
2. **Acquire:** fetch configured live provider history, use an imported structured snapshot, or deliberately choose a labelled training fixture. Respect request/state/hop limits; retain raw source responses and missing coverage.
3. **Normalise:** preserve exact native units, event identity, direction, chronology and available finality evidence. Bitcoin links retain transaction/input/output ambiguity; they do not invent input-to-output allocation.
4. **Associate assertions:** attach source-backed service/role/risk assertions and narrowly supported bridge proofs. Keep provider claims, investigator hypotheses, reviewed assertions and authenticated service responses distinct.
5. **Trace:** traverse chronological paths and stop at the first supported custody boundary on each branch. Do not stitch an exchange deposit to unrelated withdrawals. Unsupported mixers, bridges or swaps remain unresolved.
6. **Explain:** present candidates, paths, exact transfers, gaps and a snapshot-bound nearestness certificate. The user can inspect evidence or challenge a source and see what changes.
7. **Acquire the next useful evidence:** protect nearer unresolved branches, plan within a request budget and explicitly execute eligible scopes into a new analysis. Estimates, actual HTTP attempts and unknown vendor billing units stay separate.
8. **Review and preserve:** independently review new assertions/proofs and reassess; export a PDF or signed bundle. Verify hashes, signatures and deterministic replay while keeping source truth and signer identity separate from file integrity.
9. **Prepare action:** match the supported candidate to a current verified recipient, record the legal basis/scope, obtain another user's payload-bound approval and export. The current output remains NOT_SENT / NOT_CONNECTED.
10. **Learn and correct:** import supported signed scoped responses for review, record corrections/withdrawals, reassess stale results and retain case audit activity. Local wallet watches may create case change alerts while the installation runs.

The full intended production solution additionally needs licensed/authoritative attribution sources, agency identity and key governance, robust provider/reorganisation coverage, scalable acquisition and storage, independent evaluation, institutional deployment acceptance and authenticated SAHYOG/VASP transport. That architecture is fully preserved in the main skill and original research report. It is not the current release gate.

## The USP we can actually explain and demonstrate

**Defensible first-custody attribution with a visible path to the next evidence decision.** TraceSetu combines a bounded answer, its evidence dependencies and a budgeted next step, then carries that evidence into independently reviewed action packages.

| Mechanism | Demonstrable investigator outcome | Existing acceptance evidence | Claim not yet established |
|---|---|---|---|
| First-custody frontier | Stops at the first supported service on each branch and retains gaps or alternatives | Deterministic engine tests and labelled custody scenario | Real-world first-service accuracy/coverage across providers |
| Inspectable nearestness certificate | Shows what “nearest” means for this snapshot, and why unknown labels still matter | Bounded-target/shallow-gap tests and UI certificate | Globally nearest actual service or complete identity coverage |
| Source-family challenge | Removing a questioned label/proof reveals which conclusions depended on it | Challenge/recompute workflows preserve the original evidence | Measured reduction in investigator mistakes or time |
| Budget-aware next query | Turns uncertainty into reviewed acquisition scopes under a hard per-job budget | Planner/execution/recovery tests and synthetic execution demo | Vendor-price savings, superior throughput or held-out advantage |
| Reviewed service feedback | A properly bound response can become scoped evidence without silently replacing provenance | Synthetic signed-response, independent review and withdrawal workflows | Real VASP onboarding, trusted external keys and production interoperability |

Portable signed evidence/replay supports all five mechanisms. Graphs, multiple chains, case dashboards, risk labels and request packaging are useful capabilities, but are not unique by themselves. Competitor research is recorded from public sources; it is not proof that competing products lack these mechanisms. Do not claim world-first status, guaranteed novelty, superior accuracy, quantified savings or guaranteed SIH success.

## Current product, actual data and UI

- **Identity:** TraceSetu (Sanskrit-derived Trace + Setu / सेतु), formerly Vittanvaya; originally Custody Atlas. “Follow the funds. Find the receiving service.” Legacy schema IDs and ATLAS-prefixed settings remain compatible.
- **Working stack:** React/TypeScript/Cytoscape, Python/FastAPI, SQLAlchemy/SQLite WAL, a local durable worker, content-addressed local evidence and Ed25519 bundle signing. The graph algorithm is deterministic; no attribution LLM is implemented.
- **UI:** restrained light investigation desk; case search/status/pagination; first-service summary; light graph; source-linked risk panel; evidence drawer; keyboard/modal support and mobile layouts. Technical raw records remain inspectable.
- **Onboarding:** a seven-chapter **How it works** guide is available before sign-in, in the sidebar and on the case register. It includes role explanations, a working training shortcut, result definitions, follow-up actions, reporting, coverage and FAQs. Its complete displayed source is embedded in section 19.
- **Real data actually verified:** one bounded public Bitcoin sample and browser refresh, exact satoshi consistency, raw-response SHA-256 and signed live-bundle replay. The checked result was one observed transfer, no supported service candidate and COMPLETED_WITH_GAPS. A real transfer without a verified ownership label is not a failed requirement that may be repaired by inventing a label.
- **Other chains:** six adapters are implemented/parser-tested. Tron/Solana block/slot probes succeeded, but do not certify complete wallet acquisition. Ethereum/BNB/Polygon need provider credentials/entitlements; broad live and cross-chain validation remain outstanding.
- **Demo modes:** use live Bitcoin to show acquisition/provenance; visibly switch to synthetic cases for sourced custody labels, challenge, query expansion, bridge review and request/response demonstrations. The current independent installation has no official SAHYOG connection and has frozen no funds.

## Instructions that must survive every handoff

The current deliverable is a polished, functional SIH MVP; the user deferred the production build. Preserve the complete final-product vision as a future architecture, not a mandate to expand the current task. Keep all 30 problem-statement requirements mapped to their exact demonstrated subset and remaining gate.

The later user request explicitly authorized the real public-case 4K recording and approved TraceSetu. The film must remain no longer than **2:45**, with a visible cursor, click zooms and synchronized narration. Current delivery is described in `docs/TRACESETU_SUBMISSION.md`; the earlier synthetic **2:40** video is archived separately. Do not treat the superseded UI-approval hold as a reason to stop authorized work.

The baseline is **107 previously passing backend tests**, four original browser workflows, an additional UI/live-Bitcoin browser check and an additional guide check. These ran at recorded milestones; documentation updates do not rerun or recertify them. The original full-product checklist remains **50/95 verified tasks**, with **45** remaining/deferred including **12 external gates**. Later UI/guide documentation milestones are listed separately; no readiness percentage is implied.

For a new agent: orient with section 0 and this brief; read the exact problem and matrix; follow current implementation sections before historical research; use sections 18–19 for the latest UI/data/guide; use section 16 for the complete intended solution/PPT narrative. Continue from the existing repository, preserve cases and credentials, and verify relevant changes. The skill is complete recorded project context, not a copy of the private database, secret keys, every dependency or every binary artifact. Source files and actual evidence remain the executable authority.
