# Implementation decisions and deployment boundaries

## ADR 001 - Transactional application database and a local durable worker

The independent installation uses FastAPI, SQLAlchemy 2, a transactional database queue, content-addressed local objects, and React/TypeScript/Cytoscape. SQLite WAL is the tested development database. A PostgreSQL driver and configurable URL are included; PostgreSQL concurrency and recovery have not yet been validated in this environment.

The research report's target architecture includes Temporal, a derived graph store, object storage and scalable deployment. These are not claimed to exist in this installation. The bounded engine traverses acquired snapshots in Python. This keeps a small installation executable without misrepresenting a graph database or a workflow cluster as running. Migration to production infrastructure remains an explicit engineering and validation gate, not an invisible implementation detail.

## ADR 002 - Explicit evidence categories instead of invented probabilities

Provider, reviewed and hypothesis are source grades. No calibrated attribution probability is available. The engine reports contradictions, unresolved frontiers and identity coverage separately. Risk is `unassessed` when there are no sourced tags. A mixer label is an exposure assertion, not proof of laundering or a deterministic link through a mixing pool.

## ADR 003 - Snapshot reproduction

Each result binds to a canonical JSON snapshot and trace specification. A bundle contains the result, snapshot, raw acquisition responses where available, case metadata, audit excerpt, PDF and CSV. Ed25519 authenticates the manifest relative to the installation key. The independent verifier checks membership, hashes, signature and analysis replay. It never executes source code inside a bundle. Key identity requires a trusted out-of-band fingerprint; local database audit history is not external immutable retention.

## ADR 004 - Safe stopping boundaries

Custodial candidates stop further expansion on that path, including conflicts and hypotheses. Challenges that remove a boundary can expose unacquired branches and return `requires_expansion`. The implementation never connects an exchange deposit to an unrelated withdrawal. Cross-chain links require the implemented protocol verifier: CCTP V2 native USDC between Ethereum and Polygon binds the source message, signed attestation, destination acceptance and exact mint. Imported proofs also require independent review. Destination traversal begins at mint time/position. Unimplemented protocols remain unresolved. No Wormhole verification, mixer deanonymisation, CoinJoin clustering, beneficial-owner identification or universal freeze control is claimed. See `docs/cctp.md` for provider/key/contract trust assumptions and pending live validation.

## ADR 005 - Operator-reviewed routing

Recipient entries begin pending. A different reviewer must approve the source, delivery channel and any signing key. Requests bind to the exact analysis, candidate, recipient snapshot, legal basis and scope. Exports require approval bound to a payload hash and current recipient verification. Every export says `NOT_SENT` and `NOT_CONNECTED`. Signed service responses must bind to the request ID and request hash; their signatures are checked against the reviewed recipient key, and their contents remain pending review.

Structured responses can promote an exact wallet/entity/role/interval assertion after independent review. Training assertions stay separate. Reviewed withdrawals preserve old snapshots, flag affected analyses and require reassessment before new operational/report exports. Details and unsupported correction workflows are in `service-feedback.md`.

## ADR 007 - Measured acquisition versus advisory estimates

The deterministic attribution result retains its simple unresolved-frontier queue for replay compatibility. The separate `frontier-budget-1.1` planner records an auditable plan bound to the parent job, analysis hash and chosen HTTP-request budget. It protects shallow depth, then sorts by distinct observed paths per estimated call. Estimates use endpoint floors and observed pagination, never invented exchange probabilities or prices. Planning makes no provider calls. Explicit execution now creates a superseding job with immutable input binding, durable per-job request reservations/cache across recovery and persistent event-conflict holds. Reserved slots can include a request lost before dispatch; provider billing units remain unknown. Learned cost models, cross-job quotas and a held-out efficiency benchmark remain future work. See `query-execution-design.md`.

## ADR 006 - Public data does not imply public identity

Blockchain adapters acquire transactions. They cannot infer service ownership without labels. Etherscan requires credentials for these endpoints; its plan availability is provider-controlled. Tron and Solana parsers expose partial coverage explicitly. Bitcoin UTXO outputs preserve the input set and outpoints; the graph never pretends exact input-to-output allocation. All native amounts remain integer strings.
