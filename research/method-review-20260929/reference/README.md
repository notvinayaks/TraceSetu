# TraceSetu: isolated account-based deposit-candidate reference

**Status: proposed research reference, 29 September 2026.** This is a separate
standard-library Python experiment. It does not change or integrate with the
running TraceSetu MVP. It is not an exact reproduction of a published paper,
an ownership classifier, a Bitcoin algorithm, or a real-world accuracy study.
All addresses, services, identity anchors and transactions here are fictional.

## The question this experiment addresses

A known exchange hot wallet may be two transfers away from the reported
address. The intermediate address might already be a customer deposit address
controlled by that service. Looking only for existing company labels can miss
that earlier possible custody boundary.

This reference asks whether a **very narrow observed operating pattern** can
flag the intermediate address for further investigation. It never treats that
pattern as proof of ownership. A customer repeatedly paying an exchange is a
counterexample to simply grouping all senders to an exchange together.

## Two graphs/concepts kept separate

1. **Transfer observations:** chain-qualified sender, recipient, asset, exact
   integer amount, ledger order, time and transaction/receipt references.
2. **Service assertions:** externally supplied source-qualified evidence that a
   particular address had the role of hot wallet or service gas feeder for a
   named service during a stated interval. Assertions also have a learned-at
   time, source family and optional withdrawal time.

An outgoing transfer to a hot wallet does not create a service-control edge.
The proposal emits a separate unconfirmed candidate supported by references to
both kinds of input. It does not propagate candidates as new trusted anchors.

## Exact proposed conditions

The detector considers one account address, one chain and one plain token in a
bounded observation window. Its inputs must establish the following:

1. Full-window history of native transfers, token transfers and relevant
   transaction receipts, plus boundary balances, is explicitly attested. A
   token-transfer page alone is insufficient. The reference trusts this input
   attestation; it does not independently prove provider completeness.
2. The window ends no later than the evaluation cutoff. Opening token and
   native balances are exactly zero. There are no unexplained other assets or
   outflows. The token's plain, nonrebasing, non-fee transfer semantics must be
   established as an input, not guessed from its symbol.
3. Each qualifying cycle has one successful positive token incoming, then one
   native gas top-up, then one same-chain, same-token outgoing sweep **before
   the next incoming**. The outgoing token units equal the incoming units
   exactly. There is no percentage tolerance.
4. The sweep is a direct token-transfer transaction sent by the examined
   account. A receipt establishes that the same account pays a positive native
   fee. Relayer, allowance-spender, account-abstraction and complex contract
   execution cases are outside this reference.
5. The top-up sender has an explicit, source-qualified **service gas-feeder**
   role. An ordinary donor or shared relayer is not sufficient. Its asserted
   service must match the sweep recipient's source-qualified **hot-wallet**
   service. Neither role is inferred from this pattern.
6. Each anchor must match the exact chain/address, apply at the event time,
   have been learned no later than the evaluation cutoff, remain unwithdrawn
   for the reanalysis, and survive any source-family exclusion. Conflicting
   service assignments cause abstention.
7. Observed feeder credits must cover actual sweep receipt fees, and the
   resulting native and token balances must reconcile to closing balances.
   This supports consistency, not proof of intent or who holds a private key.
8. At least **three** complete cycles are required in this toy policy. Three
   is an arbitrary demonstration threshold, not a research-calibrated cutoff
   or a confidence percentage. Repeated evidence from one source is not
   independent corroboration.

The reference also uses a synthetic minimum of 100 integer token units. This
is not an economic dust definition or a suitable threshold for real assets.
A smaller positive incoming causes abstention rather than being silently
deleted to manufacture a clean pattern. Zero-value and reverted incoming
events do not count as deposits. Failed or zero-value outgoing executions
cause abstention because additional gas/accounting effects need handling.

If a condition cannot be checked from supplied observations, the result is
`abstain` with a reason. A passing result is always `heuristic_candidate` with
`ownership_proven: false`, `independent_confirmation_required: true` and no
calibrated probability. Full isolation deliberately sacrifices coverage.

## The reference search comparison

The fictional pattern is:

```text
Reported address --> candidate address --> known hot wallet
                             ^
                             |
                   known service gas feeder
```

`known_labels_only` performs bounded, forward-in-time transfer-path search and
finds the known hot-wallet assertion at two hops. It preserves the unlabelled
predecessor and explicitly does **not** prove that the hot wallet is nearest.

`candidate_frontier` uses the independently computed candidate assessment:

- With the full toy pattern, it stops at the intermediate address after one
  hop and reports an **unconfirmed possible custody boundary**.
- If that assessed boundary lacks coverage, loses a required source or has
  conflicting evidence, it stops as unresolved. It does not skip the gap and
  call the farther hot wallet the nearest deposit service.
- A hot-wallet or deposit-address service assertion is a stop. A hot-wallet
  assertion alone does not establish that the address accepts customer
  deposits. A gas-feeder-only assertion also stops the search, explicitly as
  `unresolved_service_controlled_non_deposit_role`; its role does not establish
  customer deposit acceptance. The search never links a service's later pooled
  withdrawals as this customer's continued funds.
- Reports from a different source-exclusion configuration, asset, cutoff or
  observation window are stale and cannot be reused as current evidence. Each
  assessment also records a deterministic SHA-256 digest of every supplied
  event and identity anchor. The frontier recomputes this digest from its
  current inputs. Removed, added, edited or withdrawn records invalidate the
  assessment and cause an unresolved stop until it is recomputed. Input-list
  reordering alone does not change the digest. This hash detects change; it
  does not authenticate a source or prove that observations are true.
- A state's time and ledger order must both move forward. Same-looking
  addresses on different chains do not connect. Revisiting an address is
  allowed because a service role can become valid between two visits. The
  state therefore includes arrival time/order and path, rather than pruning
  solely by address. Strictly increasing event order prevents event reuse;
  explicit hop/state limits bound expansion even when address cycles exist.

This is chronological **transfer connectivity**, not proof that the exact
same units of an account balance moved along an arbitrary multi-hop path.
In the fixture, the known-label baseline may connect `deposit-1` to the later
`sweep-2` or `sweep-3` because they are chronologically reachable. It does not
allocate or conserve the amount from `deposit-1` on those paths. Those outputs
are not traced-fund attribution, balances or recovery amounts.
There is no universal nearestness certificate, no inference about off-chain
customer ledgers, and no cross-chain proof in this reference. An assessed
unresolved boundary is different from every unlabelled transit address: the
experiment receives its selected candidate assessments explicitly. Production
candidate selection and completeness are separate unimplemented questions.

The candidate assessment is **retrospective at its stated cutoff**. With the
toy cutoff at time 40, it can use all three cycles to assess an address first
reached at time 10. It does not demonstrate that a live system could identify
the address at time 10 before cycles two and three occurred. A cutoff at time
15 includes only one cycle and therefore abstains. Record cutoff semantics
separately from the event time when reporting any future evaluation.

## Adversarial limit: patterns cannot prove who controls an address

Consider a customer-controlled address that receives separate payments,
receives gas from a cooperating or donating service feeder, and repeatedly
sends the exact received token amounts to the service. Its public observations
can be identical to those of a service-controlled deposit address.

**The detector cannot distinguish those hidden realities.** The test named
`test_fully_imitated_pattern_is_indistinguishable_and_never_proves_ownership`
intentionally demonstrates that limit. A passing test here means the program
keeps the result a hypothesis; it does not mean it detected the adversary.
Gas affiliation is a supporting clue, not a signature of wallet control.
Independent service confirmation or other reliable control evidence remains
necessary before treating the address as established service custody.

This is why the source may propose the narrower claim “prioritise unlabelled
deposit-address hypotheses for review,” not “identify exchanges without
identity data” or “prove ownership from graph structure.”

## Reproduce

Requires Python 3.10 or newer. No packages, credentials, network access,
purchases, live fund transfers or real personal data are used.

From the project root:

```powershell
python research/method-review-20260929/reference/run_experiment.py
```

Or run only the functional suite:

```powershell
python -m unittest discover -s research/method-review-20260929/reference -v
```

`run_experiment.py` runs the actual tests, writes `results.json` alongside the
code, and exits unsuccessfully if tests fail. JSON includes individual test
outcomes, scenario decisions, baseline/frontier comparisons and SHA-256 hashes
of the four Python sources. The JSON metadata explicitly disclaims measured
real-world precision/recall and any conversion of unit-test success to accuracy.

## Files

| File | Purpose |
|---|---|
| `method.py` | Narrow rule, evidence filtering and bounded time-respecting search |
| `fixtures.py` | Clearly fictional records and helper constructors |
| `test_method.py` | Functional, temporal, evidence and adversarial checks |
| `run_experiment.py` | Test runner and machine-readable scenario generation |
| `results.json` | Actual reproducible run outputs; entirely synthetic |

## Evaluation required before a product claim

An independent, authorised dataset must include service-confirmed deposit
addresses and ordinary exchange customers. Split evaluation by time and
service/entity so later labels and near-duplicate addresses cannot leak into
training or threshold selection. Evaluate difficult negatives: relayers,
gas-sponsoring services, customer payment forwarding, donation/imitation,
contract-controlled accounts, shared infrastructure, incomplete histories and
provider errors. Identity sources used to predict a result cannot also serve
as its purported independent ground truth.

Report precision together with false positives, answer coverage, abstention,
time-to-answer, provider request cost and confidence intervals. Compare against
known-label-only tracing and independently reproduce suitable published
heuristics. Tune thresholds only on a separate development set. Do not report
training-fixture outcomes as an accuracy or efficiency benchmark.

The rule rejects native-coin outflows, including residual-gas returns after a
sweep. This deliberate restriction is another reason it is **not a full
reproduction of an Evonax-style consolidation/gas-return heuristic**. A paper's
complete method, required traces and evaluation would need a separate faithful
implementation before any reproduction or comparison claim.

Bitcoin requires transaction/outpoint graph methods and careful handling of
CoinJoin, PayJoin and change heuristics; none is implemented here. Broader
account-chain collection, protocol verification, production integration,
independent attribution data, risk classification and official SAHYOG access
also remain outside this experiment.
