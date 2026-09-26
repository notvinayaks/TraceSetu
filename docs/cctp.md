# CCTP V2 correlation and review

Implemented scope as of 24 September 2026: native USDC between Ethereum (Circle domain 0) and Polygon (domain 7), using the original TokenMessengerV2 and MessageTransmitterV2 contracts in the pinned registry `circle-cctp-evm-2026-09-24`. Other chains, CCTP V1, TokenMessengerWithFees, other bridge protocols and opaque swaps remain unresolved. This is a protocol-specific addition to the full-product plan, not a claim of universal cross-chain tracing.

## What establishes the link

The verifier requires a successful source receipt, matching source block, source `MessageSent`, complete attested message, attester public-key evidence, successful destination receipt, matching destination block, matching `MessageReceived`, and exactly one corresponding native-USDC mint. It binds transaction hashes, block hashes, transaction indexes, log indexes and timestamps. Removed logs, duplicate receipt positions, malformed ABI encoding, invalid signatures, expired messages, unsupported contracts and ambiguous matches fail closed.

CCTP V2 assigns its nonce off-chain. The attested message is matched to the source bytes after clearing only the protocol-populated nonce, executed finality, executed fee and expiration fields. Two identical eligible source messages are ambiguous; the verifier does not choose by amount or position in the API response. Destination matching uses the nonce, source domain, sender, complete body and executed finality, with any nonzero destination-caller restriction checked. The accepted mint must occur before that `MessageReceived` and after any preceding `MessageReceived` in the same receipt.

Signatures use Keccak-256 and secp256k1 recovery, canonical low-S values and ordered distinct recovered signers present in the supplied CCTP V2 key evidence. The tool does **not** invent a quorum from the number of public keys. Under the receipt/provider trust assumption, the successful destination contract execution establishes that its configured threshold was accepted. Supported executed-finality values are 1000 and 2000; a supported message must meet the requested threshold policy. These values are protocol fields, not an independent consensus proof.

Amounts remain integers. The proof records burned amount, fee and net minted amount separately. Both supported assets have six decimals. A bridge edge carries the net mint and counts as one protocol-correlated hop. The outgoing path on the destination chain starts at the actual mint timestamp and position, not the source burn time. Time ordering that appears reversed across the two acquired block timestamps is unresolved. The engine still reports possible per-path exposure with lower bound zero; it does not assign customer funds or add overlapping paths.

## Trust and limitations

- A supplied public key authenticates a signature relative to that key, not the claim that the key belongs to Circle. Imported packages start as hypotheses; an independent reviewer must establish receipt and key provenance before use. A positive synthetic test does not authenticate a live provider.
- Receipt/block agreement is a provider-consistency check. There is no receipts-trie proof, light-client validation, independent node quorum, historical code-hash registry or continuous reorganisation reconciliation in this implementation.
- The live adapter fetches current Circle public keys from the fixed HTTPS endpoint. Historical key rotation can make old valid messages unresolved; the adapter does not guess missing historic keys. Current contract addresses are pinned, not scraped into an automatically trusted registry.
- Receipt acceptance and the registered messenger supply the protocol-semantic assumption. An upgraded or compromised contract/provider is outside this verifier's independent assurance. Hook bytes are retained but not interpreted as an onward transfer or swap.
- A protocol link establishes neither a VASP identity nor a beneficial owner. Destination custody still requires a separate sourced assertion and stops traversal at the first evidenced custody boundary.
- Proof packages for the same source-domain nonce cannot silently compete. Duplicate packages in a snapshot are unresolved. A case allows one pending or approved package per message and evidence purpose; review and withdrawal are versioned.

## Read-only acquisition

Set `ATLAS_CCTP_ENABLED=true` and configure an Etherscan API key with the required endpoint/chain entitlement. It is disabled by default. Configuration is not proof of connectivity or live validation.

1. The ordinary ERC20 index identifies a candidate source transaction; its receipt and block are reconciled first.
2. A supported `MessageSent` triggers GET `https://iris-api.circle.com/v2/messages/{sourceDomain}?transactionHash=...` and GET `https://iris-api.circle.com/v2/publicKeys`.
3. An optional `forwardTxHash` is only a lookup hint. Otherwise the adapter asks Etherscan `getLogs` for the registered destination transmitter, `MessageReceived` topic and exact nonce, with an AND operator and an ambiguity bound. The destination receipt and block are then fetched and verified in either case.
4. A passing package is preserved inside the immutable snapshot and its raw HTTP responses are hash-bound in the evidence bundle. The destination wallet is queued for ordinary history acquisition, subject to the same depth and request bounds.

All HTTP calls share the job's request ceiling, pacing, response-size limit and timeout. Failures leave explicit limitations. Earlier reconciled source transfers survive a later bridge failure or exhausted budget. No submission, mint, burn, relay, signing or wallet-transaction endpoint is called. No failed response is replaced by a fixture. Coverage remains partial, including on otherwise successful correlation.

Live validation of this adapter is **pending**. Parser, signature, transport, workflow and replay tests use explicit synthetic evidence. Do not label the adapter operational until independently checked live source/destination examples, key provenance and entitlement are documented.

## Imported proof workflow

The JSON contract is `docs/bridge-proof.schema.json`; snapshots containing proofs use schema `1.1`, or `1.2` when reconciliation holds are present. Empty proof/hold extensions are omitted so historical `1.0` canonical snapshots retain their hashes.

1. An investigator opens a case and uses **Evidence > Import bridge proof**. The API is `POST /api/cases/{case_id}/bridges` with `{proof, mode, rationale}`. Mode is `operational` or `training`. Explicitly synthetic packages cannot be submitted as operational evidence.
2. The API validates the complete protocol package before storing a pending record and content hash. Validation success is not approval. A second authorised user reviews the exact record version at `POST /api/records/{id}/review`.
3. **Reassess recorded evidence** freezes a new snapshot and analysis; the prior result is preserved. It makes no new HTTP calls and may expose missing destination history. A fresh live acquisition can use reviewed case proofs when gathering downstream history.
4. **Assumptions** can remove the bridge's provenance family and replay the graph. This can remove a custody path without changing its separate service label.
5. `POST /api/evidence/{id}/withdrawal`, followed by independent review, marks affected analyses stale. New request/report/bundle exports are blocked until reassessment. Historical snapshots remain accessible. Reassessment excludes withdrawn proofs and marks the source scope incomplete. Reappearance of the same protocol message in newly acquired data does not clear a reviewed withdrawal; a new independent approval is required.

Bundles preserve raw responses, snapshot proof payloads, exact analysis and report/CSV fields for source/destination transactions and burn/fee/mint amounts. Bridge traversal was introduced in engine `0.4.0`; current engine `0.5.0` additionally honors reconciliation holds. The verifier retains frozen `0.3.0` and `0.4.0` engines for historical bundle replay. Old engines reject reconciliation-hold snapshots. Compatibility is version-specific, not an assertion that all past/future formats replay.

## Reproducible training exercise

Choose **Review a bridge case** on the Investigations screen. This uses invented receipts, a publicly known local test signing key and the fictional Example Cross-chain Exchange. Initially there is no custody path. In Evidence, propose the training proof; approve it from the separate reviewer account; reassess. The path becomes Ethereum seed -> Polygon mint recipient -> fictional exchange. Inspect the delivery, challenge `synthetic-cctp-v2`, export and replay the bundle, then withdraw the proof and reassess. Every result/export remains synthetic. Never use these addresses or labels as intelligence about real owners.

`tests/test_cctp.py` covers both directions, zero/nonzero fee, reorganisation mismatch, wrong nonce/body/emitter/mint, invalid signature/key, duplicate and malformed evidence, expiration, arrival causality, review gates, challenge, withdrawal and replay. HTTP transport tests cover both destination lookup routes, continuation to the destination and budget interruption without losing earlier evidence. `scripts/browser_bridge_check.cjs` exercises the investigator/reviewer screens and export workflow.

## Primary references

Consulted 24 September 2026. Implementation is original; these references define protocol fields and provider contracts.

- [Circle CCTP technical reference](https://developers.circle.com/cctp/references/technical-guide)
- [Circle CCTP contract addresses](https://developers.circle.com/cctp/references/contract-addresses)
- [Circle native USDC contract addresses](https://developers.circle.com/stablecoins/usdc-contract-addresses)
- [Circle message and attestation endpoint](https://developers.circle.com/api-reference/cctp/all/get-messages-v2)
- [Circle public-key endpoint](https://developers.circle.com/api-reference/cctp/all/get-public-keys-v2)
- [Circle attestation verification](https://developers.circle.com/cctp/references/attestation-verification)
- [Circle MessageTransmitterV2 source](https://github.com/circlefin/evm-cctp-contracts/blob/master/src/v2/MessageTransmitterV2.sol)
- [Circle MessageV2 wire layout](https://github.com/circlefin/evm-cctp-contracts/blob/master/src/messages/v2/MessageV2.sol)
- [Circle TokenMessengerV2 source](https://github.com/circlefin/evm-cctp-contracts/blob/master/src/v2/TokenMessengerV2.sol)
- [Etherscan log lookup](https://docs.etherscan.io/api-reference/endpoint/getlogs)
