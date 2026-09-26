# Scoped service feedback and corrections

This is TraceSetu's own interchange format, not a published SAHYOG or VASP standard. Production use requires the receiving service to agree to this format and independent verification of its signing-key identity. No real response or provider onboarding has been validated.

## Signing and import

The directory entry must contain a Base64-encoded, raw 32-byte Ed25519 public key, verified by a separate reviewer. The exact key is included in the reviewed request body. A later key rotation cannot silently authenticate a response to an older request.

The service signs the UTF-8 bytes produced by `vasp_app.store.canonical(payload)`: JSON sorted recursively by object key, no insignificant whitespace, Unicode unescaped, NaN forbidden. Use strings for exact large numbers. Interoperating signers must reproduce those exact bytes; do not assume every language's default JSON serialiser is equivalent. This implementation is not a claim of RFC 8785 compliance. The signature is Base64 of the raw Ed25519 signature.

Example unsigned payload, with explicit synthetic placeholders:

```json
{
  "schema": "atlas.service-response.v1",
  "request_id": "REQUEST_ID_FROM_REVIEWED_EXPORT",
  "request_sha256": "BODY_SHA256_FROM_REVIEWED_EXPORT",
  "attestation": {
    "chain": "ethereum",
    "address": "EXACT_REQUESTED_ADDRESS",
    "entity": "EXACT_REQUESTED_ENTITY",
    "category": "exchange",
    "role": "deposit",
    "valid_from": 1750000000,
    "valid_to": 1750001000
  }
}
```

Import through the case's Requests screen or `POST /api/cases/{case_id}/feedback`, with `request_id`, `payload`, and `signature`. Only an approved request in that case is accepted. Scope mismatches, invalid signatures, changed request hashes, unsupported structured schemas, reversed intervals and replayed payloads fail explicitly. Signed free-form findings may be stored and reviewed but cannot create an attribution label. The structured attestation deliberately does not accept beneficial-owner data, risk claims or inferred cluster members.

## Independent review and promotion

A different authorised reviewer approves the feedback in Evidence. Approval rechecks the stored envelope, signature, request binding and current recipient verification. A valid structured attestation creates one reviewed, case-scoped assertion for precisely that wallet/entity/role/time interval. Multiple entries using one signing key share a provenance family, so challenges can remove their shared dependency together. A signature establishes control of the reviewed key, not the truth of the claim.

Training recipients, responses and promoted assertions stay in training mode. They are excluded from operational acquisitions. Case data is never promoted into a cross-agency public cache.

Choose **Reassess recorded evidence** to create a new analysis using the existing transaction snapshot and currently approved case assertions. No blockchain provider is called. The previous analysis is preserved. The new bundle includes the signed response envelope, original available acquisition artifacts and audit records. Reassessment does not establish that historic transactions remain canonical today.

## Withdrawals and affected findings

An investigator proposes withdrawal of a currently approved assertion, including a reason and supporting evidence. A separate reviewer approves or rejects it. Version checks reject stale or concurrent decisions. Approval marks the assertion withdrawn, records affected analyses and creates an in-case alert. It does not erase the assertion or old snapshots.

Affected analyses show an evidence-change notice. New requests, approvals and new report/request/bundle exports from those results are blocked until reassessment. Historical analysis JSON and snapshot download remain available for audit. Existing exported files cannot be recalled; their recipients must be handled through the agency's authorised process. A withdrawal affecting one supporting source conservatively requires reassessment even if another source still supports the same candidate.

Reassessment removes the withdrawn assertion, merges approved case assertions and creates a superseding result. Remaining independent labels may still support the same candidate. Further history might be needed when a formerly stopped custody boundary opens. Correction does not automatically assert that the wallet belongs to a different entity.

## Remaining gates

Automatic authenticated correction formats, cross-case reuse with data-use permissions, provider key rotation/onboarding, revocation distribution to previously exported bundles, and live-provider interoperability remain unimplemented or unvalidated. The current tests exercise explicit synthetic attestations and their failure cases.
