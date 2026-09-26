"""Synthetic cases are explicit fixtures, never a fallback from a failed provider."""

from .domain import Snapshot


def training_snapshot():
    start = 1750000000

    def event(n, sender, recipient, amount, offset):
        return dict(
            id=f"fixture-event-{n}",
            chain="ethereum",
            txid=f"fixture-tx-{n}",
            senders=[f"fixture:{sender}"],
            recipient=f"fixture:{recipient}",
            asset="ethereum:native",
            amount=str(amount),
            decimals=18,
            timestamp=start + offset,
            position=[100 + n, 0, 0],
            finality="finalized",
            evidence=[f"fixture-source-{n}"],
        )

    return Snapshot.model_validate(
        dict(
            mode="fixture",
            origin="TraceSetu synthetic training scenario v1; no real addresses or services",
            collected_at=start + 1000,
            window_start=start,
            window_end=start + 1000,
            events=[
                event(1, "suspect", "alpha-deposit", 4 * 10**18, 10),
                event(2, "suspect", "intermediary", 6 * 10**18, 20),
                event(3, "intermediary", "beta-deposit", 5 * 10**18, 30),
                event(4, "intermediary", "mixer", 10**18, 40),
                event(5, "suspect", "unresolved", 10**15, 50),
                event(6, "alpha-deposit", "alpha-hot", 4 * 10**18, 60),
            ],
            assertions=[
                dict(
                    id="fixture-label-alpha",
                    chain="ethereum",
                    address="fixture:alpha-deposit",
                    entity="Example Exchange Alpha",
                    category="exchange",
                    role="deposit",
                    grade="reviewed",
                    source_family="fixture-directory",
                    source="Synthetic directory",
                    evidence=["fixture-directory-1"],
                ),
                dict(
                    id="fixture-label-beta",
                    chain="ethereum",
                    address="fixture:beta-deposit",
                    entity="Example Custodian Beta",
                    category="custodian",
                    role="deposit",
                    grade="provider",
                    source_family="fixture-provider",
                    source="Synthetic provider",
                    evidence=["fixture-provider-1"],
                ),
                dict(
                    id="fixture-label-mixer",
                    chain="ethereum",
                    address="fixture:mixer",
                    entity="Example Mixer",
                    category="mixer",
                    grade="provider",
                    source_family="fixture-provider",
                    source="Synthetic provider",
                    evidence=["fixture-provider-2"],
                    risk_tags=["mixer_exposure"],
                ),
            ],
            coverage=[
                dict(
                    chain="ethereum",
                    address=f"fixture:{a}",
                    status="complete",
                    reason="All events in synthetic window",
                    pages=1,
                )
                for a in ["suspect", "intermediary"]
            ]
            + [
                dict(
                    chain="ethereum",
                    address="fixture:unresolved",
                    status="partial",
                    reason="Deliberate pagination gap for training",
                    pages=1,
                )
            ],
            limitations=[
                "Entirely synthetic training data. This is not an investigation or a live provider result."
            ],
        )
    )
