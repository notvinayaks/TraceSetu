"""Explicitly fictional observations and asserted roles; no real labels."""

from dataclasses import replace

from method import Anchor, Coverage, Event, detect_candidate

CHAIN = "synthetic:account-chain-A"
OTHER_CHAIN = "synthetic:account-chain-B"
TOKEN = "synthetic:plain-token"
NATIVE = "synthetic:native"
SERVICE = "SYNTHETIC_SERVICE_ALPHA"
ADDRESS = "SYNTHETIC_DEPOSIT_CANDIDATE"
HOT = "SYNTHETIC_HOT_WALLET"
FEEDER = "SYNTHETIC_GAS_FEEDER"
SUSPECT = "SYNTHETIC_REPORTED_ADDRESS"
WINDOW = (0, 40)


def fixture():
    anchors = [
        Anchor("hot-role", CHAIN, HOT, SERVICE, "hot_wallet", -10, 100, -1,
               "synthetic:hot-role-source", "fixture://explicit-hot-role"),
        Anchor("gas-role", CHAIN, FEEDER, SERVICE, "gas_feeder", -10, 100, -1,
               "synthetic:gas-role-source", "fixture://explicit-gas-feeder-role"),
    ]
    events = []
    for cycle in range(1, 4):
        at = cycle * 10
        sender = SUSPECT if cycle == 1 else f"SYNTHETIC_SENDER_{cycle}"
        events += [
            Event(f"deposit-{cycle}", f"tx-deposit-{cycle}", CHAIN, TOKEN,
                  sender, ADDRESS, 1000 * cycle, at, at),
            Event(f"gas-{cycle}", f"tx-gas-{cycle}", CHAIN, NATIVE,
                  FEEDER, ADDRESS, 100, at + 1, at + 1),
            Event(f"sweep-{cycle}", f"tx-sweep-{cycle}", CHAIN, TOKEN,
                  ADDRESS, HOT, 1000 * cycle, at + 2, at + 2,
                  tx_sender=ADDRESS, gas_payer=ADDRESS, fee_units=10,
                  receipt_ref=f"fixture://receipt-{cycle}", execution_kind="direct_token_transfer"),
        ]
    coverage = Coverage(CHAIN, ADDRESS, *WINDOW, True, True, True,
                        {TOKEN: 0, NATIVE: 0}, {TOKEN: 0, NATIVE: 270},
                        "fixture://complete-history-and-boundary-balances")
    return events, anchors, coverage


def detect(events=None, anchors=None, coverage=None, **kwargs):
    base_events, base_anchors, base_coverage = fixture()
    defaults = dict(chain=CHAIN, address=ADDRESS, token=TOKEN, native=NATIVE,
                    window=WINDOW, as_of=40)
    defaults.update(kwargs)
    return detect_candidate(base_events if events is None else events,
                            base_anchors if anchors is None else anchors,
                            base_coverage if coverage is None else coverage, **defaults)


def mutate_event(events, event_id, **changes):
    return [replace(e, **changes) if e.event_id == event_id else e for e in events]
