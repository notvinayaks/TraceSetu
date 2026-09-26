"""Explicitly selected read-only Bitcoin provider; never an automatic fallback.

Full-address pagination follows the documented exclusive block-height cursor.
Observed outputs retain their entire input set: no input/output fund allocation.
"""

from datetime import datetime

from .config import settings
from .domain import Coverage, Transfer


def acquire_bitcoin(acquisition, address):
    from .providers import ProviderError

    events, evidence, seen = [], [], set()
    before, pages = None, 0
    omitted_scripts = False
    pagination_uncertain = False
    while True:
        acquisition.checkpoint(events, "bitcoin", address, pages, evidence, str(before or "first-page"))
        # Apply confirmation checks locally. Combining the provider's optional
        # confirmations filter with before returned the first page repeatedly
        # in the independently captured public-address check on 25 Sep 2026.
        params = {"limit": 50, "txlimit": 1000}
        if before is not None:
            params["before"] = before
        data, h = acquisition.fetch(
            "BlockCypher", settings.blockcypher_api_url.rstrip("/") + f"/addrs/{address}/full", params=params
        )
        evidence.append(h)
        pages += 1
        if (
            not isinstance(data, dict)
            or data.get("address") != address
            or not isinstance(data.get("txs"), list)
        ):
            raise ProviderError("BlockCypher: invalid or mismatched address response")
        rows = data["txs"]
        heights = []
        for tx in rows:
            height = tx.get("block_height", -1)
            if height < 0 or tx.get("confirmations", 0) < 1:
                continue
            heights.append(height)
            if tx.get("double_spend"):
                raise ProviderError("BlockCypher: provider reports a double-spend conflict")
            try:
                dt = datetime.fromisoformat(tx["confirmed"].replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    raise ValueError("timezone absent")
                stamp = int(dt.timestamp())
            except (ValueError, KeyError, TypeError) as exc:
                raise ProviderError("BlockCypher: invalid confirmation timestamp") from exc
            if not acquisition.spec.start <= stamp <= acquisition.spec.end:
                continue
            inputs, outputs = tx.get("inputs", []), tx.get("outputs", [])
            if tx.get("vin_sz") != len(inputs) or tx.get("vout_sz") != len(outputs):
                raise ProviderError("BlockCypher: truncated transaction input/output arrays")
            senders = list(dict.fromkeys(a for i in inputs for a in i.get("addresses", [])))
            if address not in senders:
                continue
            if any(
                len(i.get("addresses", [])) != 1 or not i.get("prev_hash") or i.get("output_index", -1) < 0
                for i in inputs
            ):
                omitted_scripts = True
                continue
            for n, out in enumerate(outputs):
                if len(out.get("addresses", [])) != 1:
                    omitted_scripts = True
                    continue
                amount = out.get("value")
                if type(amount) is not int or amount < 0:
                    raise ProviderError("BlockCypher: output value is not exact non-negative satoshis")
                event_id = f"bitcoin:{tx['hash']}:vout:{n}"
                if event_id in seen:
                    continue
                seen.add(event_id)
                index = tx.get("block_index")
                events.append(
                    Transfer(
                        id=event_id,
                        chain="bitcoin",
                        txid=tx["hash"],
                        senders=senders,
                        recipient=out["addresses"][0],
                        asset="bitcoin:native",
                        amount=str(amount),
                        decimals=8,
                        timestamp=stamp,
                        kind="utxo",
                        finality="confirmed",
                        evidence=[h],
                        output_index=n,
                        input_outpoints=[f"{i['prev_hash']}:{i['output_index']}" for i in inputs],
                        position=[height, index, n] if type(index) is int and index >= 0 else None,
                    )
                )
        # Read to the provider's explicit history end. Timestamp order alone cannot
        # safely truncate height pagination because block timestamps can decrease.
        # An omitted flag is not affirmative evidence of complete history.
        # Real responses may omit it even when n_tx exceeds returned rows.
        if "hasMore" not in data:
            pagination_uncertain = True
            break
        if data["hasMore"] is False:
            break
        if not heights or (before is not None and min(heights) >= before):
            raise ProviderError("BlockCypher: history cursor did not advance")
        before = min(heights)
    return events, Coverage(
        chain="bitcoin",
        address=address,
        status="partial" if omitted_scripts or pagination_uncertain else "complete",
        pages=pages,
        evidence=evidence,
        reason=(
            (
                "BlockCypher omitted the history-completion signal; returned transfers retained. "
                if pagination_uncertain
                else "BlockCypher confirmed address history paginated to provider end. "
            )
            + "Non-single-address scripts excluded; no pinned head or independent consensus verification. "
            "UTXO links indicate possible exposure, not allocation or common ownership."
            + (" Some transaction scripts could not be represented." if omitted_scripts else "")
        ),
    )
