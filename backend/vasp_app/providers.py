"""Bounded read-only public API adapters. Provider errors never become fixture data."""

from __future__ import annotations
import time
from collections import deque
import httpx
from .config import settings
from .domain import Transfer, Snapshot, Coverage, TraceSpec, Assertion, BridgeProof
from .store import artifact, digest
from .addresses import tron_from_hex
from .evm_receipts import erc20_transfers
from .cctp import REGISTRY, TRANSMITTER, RECEIVED_TOPIC, sent_messages, parse_message, blob, verify_bridge


class ProviderError(Exception):
    pass


class BudgetExhausted(ProviderError):
    pass


class Acquisition:
    def __init__(self, spec: TraceSpec, progress=lambda **_: None):
        self.spec = spec
        self.calls = 0
        self.cache_hits = 0
        self.raw = []
        self.progress = progress
        self.last_call = 0
        self.client = httpx.Client(timeout=settings.provider_timeout, follow_redirects=False)
        self.cache = {}
        self.partial_events = []
        self.partial_scope = None
        self.evm_contexts = {}
        self.bridge_proofs = {}
        self.bridge_events = {}
        self.bridge_attempted = set()
        self.bridge_limitations = []
        self.durable_budget = None

    def close(self):
        self.client.close()

    def checkpoint(self, events, chain, address, pages, evidence, cursor):
        self.partial_events = list(events)
        self.partial_scope = Coverage(
            chain=chain,
            address=address,
            status="partial",
            reason="Acquisition interrupted before all pages/endpoints completed",
            pages=pages,
            evidence=list(evidence),
            cursor=cursor,
        )

    def fetch(self, provider, url, *, params=None, body=None, headers=None):
        # Cache only within this immutable acquisition; credentials never enter evidence metadata.
        cache_key = digest({"provider": provider, "url": url, "params": params, "body": body})
        if cache_key in self.cache:
            self.cache_hits = self.durable_budget.cache_hit() if self.durable_budget else self.cache_hits + 1
            return self.cache[cache_key]
        if self.calls >= self.spec.max_requests:
            raise BudgetExhausted("Request budget exhausted")
        time.sleep(max(0, 0.55 - (time.monotonic() - self.last_call)))
        self.calls = self.durable_budget.reserve() if self.durable_budget else self.calls + 1
        self.last_call = time.monotonic()
        self.progress(stage=f"Acquiring {provider} · request {self.calls}/{self.spec.max_requests}")
        try:
            with self.client.stream(
                "POST" if body else "GET", url, params=params, json=body, headers=headers
            ) as response:
                data = b""
                for chunk in response.iter_bytes():
                    data += chunk
                    if len(data) > 8_000_000:
                        raise ProviderError("Provider response exceeds the 8 MB evidence limit")
                if response.status_code != 200:
                    raise ProviderError(f"{provider}: HTTP {response.status_code}; acquisition incomplete")
                h = artifact(data)
                self.raw.append(
                    {
                        "sha256": h,
                        "provider": provider,
                        "retrieved_at": int(time.time()),
                        "request_number": self.calls,
                    }
                )
                import json

                try:
                    payload = json.loads(data)
                except ValueError:
                    if self.durable_budget:
                        self.durable_budget.response(None, h, self.raw[-1])
                    raise
        except (httpx.HTTPError, ValueError) as e:
            # Never expose exception URLs containing keys.
            raise ProviderError(f"{provider}: {type(e).__name__}; acquisition incomplete") from None
        self.cache[cache_key] = (payload, h)
        if self.durable_budget:
            self.durable_budget.response(cache_key, h, self.raw[-1])
        return payload, h

    def bitcoin(self, address):
        if settings.bitcoin_provider == "blockcypher":
            from .blockcypher import acquire_bitcoin

            return acquire_bitcoin(self, address)
        events = []
        cursor = ""
        pages = 0
        evidence = []
        complete = False
        while True:
            self.checkpoint(events, "bitcoin", address, pages, evidence, cursor or "first-page")
            data, h = self.fetch(
                "Esplora",
                settings.bitcoin_api_url.rstrip("/")
                + f"/address/{address}/txs/chain"
                + ("/" + cursor if cursor else ""),
            )
            evidence.append(h)
            pages += 1
            if not isinstance(data, list):
                raise ProviderError("Esplora: invalid transaction response")
            for tx in data:
                status = tx.get("status", {})
                if not status.get("confirmed"):
                    continue
                stamp = status.get("block_time", 0)
                inputs = [i for i in tx.get("vin", []) if i.get("prevout", {}).get("scriptpubkey_address")]
                senders = list(dict.fromkeys(i["prevout"]["scriptpubkey_address"] for i in inputs))
                if address not in senders or not self.spec.start <= stamp <= self.spec.end:
                    continue
                for n, out in enumerate(tx.get("vout", [])):
                    if not out.get("scriptpubkey_address"):
                        continue
                    events.append(
                        Transfer(
                            id=f"bitcoin:{tx['txid']}:vout:{n}",
                            chain="bitcoin",
                            txid=tx["txid"],
                            senders=senders,
                            recipient=out["scriptpubkey_address"],
                            asset="bitcoin:native",
                            amount=str(out["value"]),
                            decimals=8,
                            timestamp=stamp,
                            kind="utxo",
                            evidence=[h],
                            output_index=n,
                            input_outpoints=[f"{i['txid']}:{i['vout']}" for i in inputs],
                        )
                    )
            if (
                len(data) < 25
                or min((t.get("status", {}).get("block_time", self.spec.end) for t in data), default=0)
                < self.spec.start
            ):
                complete = True
                break
            cursor = data[-1]["txid"]
        return events, Coverage(
            chain="bitcoin",
            address=address,
            status="complete" if complete else "partial",
            pages=pages,
            evidence=evidence,
            reason="Confirmed address history paginated through the requested window; scripts without address representations excluded. UTXO links are possible exposure, not input-output allocation.",
        )

    def evm(self, chain, address):
        if not settings.etherscan_api_key:
            raise ProviderError("Etherscan API key is not configured")
        chain_id = {"ethereum": 1, "bnb": 56, "polygon": 137}[chain]
        events = []
        evidence = []
        pages = 0
        for action in ["txlist", "txlistinternal", "tokentx"]:
            page = 1
            while True:
                self.checkpoint(events, chain, address, pages, evidence, action + ":" + str(page))
                data, h = self.fetch(
                    "Etherscan V2",
                    "https://api.etherscan.io/v2/api",
                    params=dict(
                        chainid=chain_id,
                        module="account",
                        action=action,
                        address=address,
                        startblock=0,
                        endblock=9999999999,
                        page=page,
                        offset=100,
                        sort="desc",
                        apikey=settings.etherscan_api_key,
                    ),
                )
                evidence.append(h)
                pages += 1
                rows = data.get("result")
                if data.get("status") == "0" and data.get("message") == "No transactions found":
                    rows = []
                if not isinstance(rows, list):
                    raise ProviderError(
                        "Etherscan V2: unavailable, rate limited, or plan does not support this endpoint"
                    )
                for n, r in enumerate(rows):
                    stamp = int(r.get("timeStamp", 0))
                    value = r.get("value", "0")
                    if (
                        r.get("from", "").lower() != address
                        or not r.get("to")
                        or r.get("isError", "0") != "0"
                        or not self.spec.start <= stamp <= self.spec.end
                    ):
                        continue
                    if not value.isdigit() or int(value) == 0:
                        continue
                    if action == "tokentx":
                        self.checkpoint(events, chain, address, pages, evidence, "receipt:" + r["hash"])
                        verified = self.evm_token_receipt(chain, address, r, h)
                        known = {e.id: e for e in events}
                        for event in verified:
                            if event.id in known and known[event.id].model_dump(
                                exclude={"evidence"}
                            ) != event.model_dump(exclude={"evidence"}):
                                raise ProviderError(
                                    "Conflicting indexed metadata for the same reconciled token log"
                                )
                            if event.id not in known and self.spec.start <= event.timestamp <= self.spec.end:
                                events.append(event)
                                known[event.id] = event
                        self.checkpoint(events, chain, address, pages, evidence, "bridge:" + r["hash"])
                        if (
                            settings.cctp_enabled
                            and chain in REGISTRY
                            and r["contractAddress"].lower() == REGISTRY[chain]["usdc"]
                        ):
                            self.discover_cctp(chain, address, r["hash"])
                        for link in self.bridge_events.values():
                            if link.chain == chain and address in link.senders and link.id not in known:
                                events.append(link)
                                known[link.id] = link
                        continue
                    else:
                        suffix = (
                            "internal:" + r.get("traceId", str(n)) if action == "txlistinternal" else "native"
                        )
                    events.append(
                        Transfer(
                            id=f"{chain}:{r['hash']}:{suffix}",
                            chain=chain,
                            txid=r["hash"],
                            senders=[address],
                            recipient=r["to"].lower(),
                            asset=chain
                            + (":" + r["contractAddress"].lower() if action == "tokentx" else ":native"),
                            amount=value,
                            decimals=int(r.get("tokenDecimal", 18)) if action == "tokentx" else 18,
                            timestamp=stamp,
                            position=[int(r["blockNumber"]), int(r.get("transactionIndex", 0)), 0]
                            if action == "txlist"
                            else None,
                            finality="pending" if r.get("confirmations") == "0" else "confirmed",
                            kind={"txlist": "native", "txlistinternal": "internal", "tokentx": "token"}[
                                action
                            ],
                            evidence=[h],
                        )
                    )
                if (
                    len(rows) < 100
                    or min((int(r.get("timeStamp", 0)) for r in rows), default=0) < self.spec.start
                ):
                    break
                page += 1
        return events, Coverage(
            chain=chain,
            address=address,
            status="partial",
            pages=pages,
            evidence=evidence,
            reason="Account/internal index and receipt-reconciled standard ERC20 logs queried. Token receipts match acquired block hash, position and timestamp; this is not an independent consensus or trie proof. A contract-emitted log does not prove token legitimacy, economic value, or sender authorisation. Pinned-head pagination, internal trace reconciliation, nonstandard token and NFT coverage remain incomplete; decimals are provider metadata.",
        )

    def evm_token_receipt(self, chain, address, row, index_evidence):
        base = {
            "chainid": {"ethereum": 1, "bnb": 56, "polygon": 137}[chain],
            "module": "proxy",
            "apikey": settings.etherscan_api_key,
        }
        receipt_data, receipt_hash = self.fetch(
            "Etherscan receipt",
            "https://api.etherscan.io/v2/api",
            params={**base, "action": "eth_getTransactionReceipt", "txhash": row["hash"]},
        )
        receipt = receipt_data.get("result")
        if not isinstance(receipt, dict) or not receipt.get("blockNumber"):
            raise ProviderError("EVM token receipt unavailable; indexed token row was not substituted")
        block_data, block_hash = self.fetch(
            "Etherscan block",
            "https://api.etherscan.io/v2/api",
            params={
                **base,
                "action": "eth_getBlockByNumber",
                "tag": receipt["blockNumber"],
                "boolean": "false",
            },
        )
        try:
            result = erc20_transfers(
                chain,
                row["hash"],
                address,
                row["contractAddress"],
                int(row["tokenDecimal"]),
                receipt,
                block_data.get("result"),
                [index_evidence, receipt_hash, block_hash],
            )
            self.evm_contexts[(chain, row["hash"].lower())] = (
                receipt,
                block_data.get("result"),
                [index_evidence, receipt_hash, block_hash],
            )
            return result
        except (ValueError, KeyError, TypeError):
            raise ProviderError(
                "EVM token receipt/block reconciliation failed; indexed token row was not substituted"
            ) from None

    def discover_cctp(self, chain, address, txhash):
        """Read-only message correlation; any missing leg leaves an explicit gap."""
        scope = (chain, txhash.lower(), address)
        if scope in self.bridge_attempted:
            return
        self.bridge_attempted.add(scope)
        receipt, block, evidence = self.evm_contexts[(chain, txhash.lower())]
        try:
            source_messages = [parse_message(raw) for _, raw in sent_messages(receipt)]
            if not any(m["message_sender"] == address for m in source_messages):
                return
            iris, iris_hash = self.fetch(
                "Circle CCTP V2 messages",
                f"https://iris-api.circle.com/v2/messages/{REGISTRY[chain]['domain']}",
                params={"transactionHash": txhash},
            )
            rows = iris.get("messages")
            if not isinstance(rows, list) or not 1 <= len(rows) <= 100:
                raise ValueError("Attested messages unavailable or oversized")
            keys_data, keys_hash = self.fetch(
                "Circle CCTP V2 keys", "https://iris-api.circle.com/v2/publicKeys"
            )
            accepted = 0
            for row in rows:
                if (
                    not isinstance(row, dict)
                    or row.get("status") != "complete"
                    or row.get("cctpVersion") != 2
                ):
                    continue
                message = parse_message(blob(row.get("message")))
                if message["message_sender"] != address:
                    continue
                destination = next(
                    (
                        c
                        for c, d in REGISTRY.items()
                        if d["domain"] == message["destination_domain"] and c != chain
                    ),
                    None,
                )
                if not destination:
                    self.bridge_limitations.append(
                        "CCTP destination domain is outside the implemented Ethereum/Polygon decoder"
                    )
                    continue
                base = {"chainid": REGISTRY[destination]["chainid"], "apikey": settings.etherscan_api_key}
                dest_tx = row.get("forwardTxHash")
                lookup_hashes = []
                if not dest_tx:
                    lookup, lh = self.fetch(
                        "Etherscan CCTP destination lookup",
                        "https://api.etherscan.io/v2/api",
                        params={
                            **base,
                            "module": "logs",
                            "action": "getLogs",
                            "fromBlock": 0,
                            "toBlock": 9999999999,
                            "address": TRANSMITTER,
                            "topic0": RECEIVED_TOPIC,
                            "topic2": message["nonce"],
                            "topic0_2_opr": "and",
                            "page": 1,
                            "offset": 2,
                        },
                    )
                    lookup_hashes.append(lh)
                    logs = lookup.get("result")
                    if lookup.get("status") != "1" or not isinstance(logs, list) or len(logs) != 1:
                        raise ValueError("Destination receipt acceptance is missing or ambiguous")
                    dest_tx = logs[0]["transactionHash"]
                from .evm_receipts import data

                dest_tx = data(dest_tx, 32)
                dest_receipt, drh = self.fetch(
                    "Etherscan CCTP receipt",
                    "https://api.etherscan.io/v2/api",
                    params={
                        **base,
                        "module": "proxy",
                        "action": "eth_getTransactionReceipt",
                        "txhash": dest_tx,
                    },
                )
                dr = dest_receipt.get("result")
                if not isinstance(dr, dict) or not dr.get("blockNumber"):
                    raise ValueError("Destination receipt unavailable")
                dest_block, dbh = self.fetch(
                    "Etherscan CCTP block",
                    "https://api.etherscan.io/v2/api",
                    params={
                        **base,
                        "module": "proxy",
                        "action": "eth_getBlockByNumber",
                        "tag": dr["blockNumber"],
                        "boolean": "false",
                    },
                )
                proof = BridgeProof(
                    id="cctp_" + digest([chain, txhash.lower(), message["nonce"]])[:32],
                    source_chain=chain,
                    destination_chain=destination,
                    source_txhash=txhash,
                    destination_txhash=dest_tx,
                    nonce=message["nonce"],
                    source_receipt=receipt,
                    source_block=block,
                    destination_receipt=dr,
                    destination_block=dest_block.get("result"),
                    iris_response=iris,
                    public_keys=keys_data,
                    grade="provider",
                    evidence=evidence + [iris_hash, keys_hash, drh, dbh] + lookup_hashes,
                )
                verified = verify_bridge(proof)
                if len(self.bridge_proofs) >= 100 and proof.id not in self.bridge_proofs:
                    raise ValueError("CCTP proof bound reached")
                self.bridge_proofs[proof.id] = proof
                self.bridge_events[proof.id] = verified["event"]
                accepted += 1
            if accepted == 0:
                self.bridge_limitations.append(
                    "CCTP source observed but no supported completed destination proof was established"
                )
        except BudgetExhausted:
            self.bridge_limitations.append("CCTP correlation stopped at the shared request budget")
            raise
        except (ProviderError, ValueError, KeyError, TypeError, AttributeError):
            self.bridge_limitations.append(
                "CCTP source observed; message, signatures or destination receipt could not be established. No guessed cross-chain link was added."
            )

    def tron(self, address):
        events = []
        evidence = []
        pages = 0
        for token in [False, True]:
            cursor = None
            while True:
                self.checkpoint(
                    events,
                    "tron",
                    address,
                    pages,
                    evidence,
                    ("trc20:" if token else "native:") + (cursor or "first-page"),
                )
                params = {
                    "only_confirmed": "true",
                    "only_from": "true",
                    "limit": 200,
                    "order_by": "block_timestamp,asc",
                    "min_timestamp": self.spec.start * 1000,
                    "max_timestamp": self.spec.end * 1000,
                }
                if cursor:
                    params["fingerprint"] = cursor
                data, h = self.fetch(
                    "TronGrid",
                    "https://api.trongrid.io/v1/accounts/"
                    + address
                    + "/transactions"
                    + ("/trc20" if token else ""),
                    params=params,
                    headers={"TRON-PRO-API-KEY": settings.trongrid_api_key}
                    if settings.trongrid_api_key
                    else {},
                )
                if data.get("success") is not True or not isinstance(data.get("data"), list):
                    raise ProviderError("TronGrid: incomplete or rejected response")
                evidence.append(h)
                pages += 1
                for n, r in enumerate(data["data"]):
                    if token:
                        if r.get("type") != "Transfer" or r.get("from") != address:
                            continue
                        info = r.get("token_info", {})
                        value = r.get("value", "0")
                        recipient = r.get("to")
                        asset = "tron:" + info.get("address", "unknown")
                        txid = r["transaction_id"]
                        decimals = int(info.get("decimals", 0))
                        stamp = int(r["block_timestamp"]) // 1000
                    else:
                        if any(x.get("contractRet") != "SUCCESS" for x in r.get("ret", [])):
                            continue
                        contracts = r.get("raw_data", {}).get("contract", [])
                        if len(contracts) != 1 or contracts[0].get("type") != "TransferContract":
                            continue
                        v = contracts[0]["parameter"]["value"]
                        sender = tron_from_hex(v["owner_address"])
                        if sender != address:
                            continue
                        recipient = tron_from_hex(v["to_address"])
                        value = str(v["amount"])
                        asset = "tron:native"
                        decimals = 6
                        txid = r["txID"]
                        stamp = int(r["block_timestamp"]) // 1000
                    events.append(
                        Transfer(
                            id=f"tron:{txid}:" + ("token:" + digest(r) if token else "native"),
                            chain="tron",
                            txid=txid,
                            senders=[address],
                            recipient=recipient,
                            asset=asset,
                            amount=str(value),
                            decimals=decimals,
                            timestamp=stamp,
                            kind="token" if token else "native",
                            evidence=[h],
                        )
                    )
                cursor = (
                    data.get("meta", {}).get("fingerprint")
                    if data.get("meta", {}).get("links", {}).get("next")
                    else None
                )
                if not cursor:
                    break
        return events, Coverage(
            chain="tron",
            address=address,
            status="partial",
            pages=pages,
            evidence=evidence,
            reason="Confirmed TRX and indexed TRC20 transfers queried; internal TRX, resource transactions and event-index reconciliation are not covered.",
        )

    def solana(self, address):
        events = []
        evidence = []
        before = None
        pages = 0
        while True:
            self.checkpoint(events, "solana", address, pages, evidence, before or "first-page")
            cfg = {"commitment": "finalized", "limit": 100}
            if before:
                cfg["before"] = before
            data, h = self.fetch(
                "Solana RPC",
                settings.solana_rpc_url,
                body={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getSignaturesForAddress",
                    "params": [address, cfg],
                },
            )
            if data.get("error") or not isinstance(data.get("result"), list):
                raise ProviderError("Solana RPC: signature history unavailable")
            evidence.append(h)
            pages += 1
            rows = data["result"]
            for row in rows:
                if (
                    row.get("err") is not None
                    or not self.spec.start <= (row.get("blockTime") or 0) <= self.spec.end
                ):
                    continue
                self.checkpoint(events, "solana", address, pages, evidence, "transaction:" + row["signature"])
                tx, th = self.fetch(
                    "Solana RPC",
                    settings.solana_rpc_url,
                    body={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getTransaction",
                        "params": [
                            row["signature"],
                            {
                                "encoding": "jsonParsed",
                                "commitment": "finalized",
                                "maxSupportedTransactionVersion": 0,
                            },
                        ],
                    },
                )
                evidence.append(th)
                r = tx.get("result")
                if not r or r.get("meta", {}).get("err") is not None:
                    continue
                message = r["transaction"]["message"]
                keys = [a["pubkey"] if isinstance(a, dict) else a for a in message["accountKeys"]]
                balances = {
                    keys[b["accountIndex"]]: b
                    for b in r["meta"].get("preTokenBalances", []) + r["meta"].get("postTokenBalances", [])
                }
                instructions = [(f"outer:{n}", i) for n, i in enumerate(message["instructions"])]
                for group in r["meta"].get("innerInstructions", []) or []:
                    instructions.extend(
                        (f"inner:{group['index']}:{n}", i) for n, i in enumerate(group["instructions"])
                    )
                for index, ins in instructions:
                    parsed = ins.get("parsed", {})
                    info = parsed.get("info", {})
                    if parsed.get("type") not in ("transfer", "transferChecked"):
                        continue
                    src = info.get("source")
                    dst = info.get("destination")
                    if not src or not dst:
                        continue
                    if ins.get("program") == "system":
                        asset = "solana:native"
                        value = str(info.get("lamports", 0))
                        decimals = 9
                    elif ins.get("program") in ("spl-token", "spl-token-2022"):
                        bal = balances.get(src) or balances.get(dst)
                        if not bal:
                            continue
                        asset = "solana:" + bal["mint"]
                        value = str(info.get("amount", info.get("tokenAmount", {}).get("amount", "0")))
                        decimals = bal["uiTokenAmount"]["decimals"]
                        src = balances.get(src, {}).get("owner", src)
                        dst = balances.get(dst, {}).get("owner", dst)
                    else:
                        continue
                    if src != address:
                        continue
                    events.append(
                        Transfer(
                            id=f"solana:{row['signature']}:{index}",
                            chain="solana",
                            txid=row["signature"],
                            senders=[src],
                            recipient=dst,
                            asset=asset,
                            amount=value,
                            decimals=decimals,
                            timestamp=row["blockTime"],
                            finality="finalized",
                            kind="native" if asset.endswith(":native") else "token",
                            evidence=[th],
                        )
                    )
            if len(rows) < 100 or min((x.get("blockTime") or 0 for x in rows), default=0) < self.spec.start:
                break
            before = rows[-1]["signature"]
        return events, Coverage(
            chain="solana",
            address=address,
            status="partial",
            pages=pages,
            evidence=evidence,
            reason="Finalized parsed instructions for signatures mentioning this address. Historical/closed token-account discovery, unsupported instructions and complete intra-slot ordering remain unresolved.",
        )

    def collect(self, assertions, reviewed_bridges=()):
        spec = self.spec
        queue = deque([(spec.chain, spec.address, 0)])
        seen = set()
        events = {}
        coverage = []
        limitations = []
        assertions = list(assertions)
        for proof in reviewed_bridges:
            try:
                link = verify_bridge(proof)
                self.bridge_proofs[proof.id] = proof
                self.bridge_events[proof.id] = link["event"]
            except (ValueError, KeyError, TypeError):
                limitations.append("A previously reviewed CCTP proof failed revalidation")
        while queue:
            chain, address, depth = queue.popleft()
            if (chain, address) in seen:
                continue
            seen.add((chain, address))
            # Metadata is an optional paid capability, never inferred from a normal RPC response.
            if settings.etherscan_metadata_enabled and chain in ("ethereum", "bnb", "polygon"):
                try:
                    assertions.extend(self.evm_metadata(chain, address))
                except ProviderError as exc:
                    limitations.append(str(exc))
            custodial = {
                (a.chain, a.address)
                for a in assertions
                if a.category in ("exchange", "custodian", "mixer")
                and a.valid_from <= spec.start
                and (a.valid_to is None or a.valid_to >= spec.end)
            }
            if depth > 0 and (chain, address) in custodial:
                continue
            if depth >= spec.max_hops:
                continue
            self.partial_events = []
            self.partial_scope = None
            try:
                rows, c = (
                    self.evm(chain, address)
                    if chain in ("ethereum", "bnb", "polygon")
                    else getattr(self, chain)(address)
                )
                rows = list(rows)
                ids = {e.id for e in rows}
                for e in self.bridge_events.values():
                    if (
                        e.chain == chain
                        and address in e.senders
                        and spec.start <= e.timestamp <= spec.end
                        and e.id not in ids
                    ):
                        rows.append(e)
                        ids.add(e.id)
                coverage.append(c)
                for e in rows:
                    events[e.id] = e
                    queue.append((e.destination_chain or chain, e.recipient, depth + 1))
            except ProviderError as exc:
                if self.partial_scope and self.partial_scope.evidence:
                    coverage.append(
                        self.partial_scope.model_copy(
                            update={"reason": str(exc) + "; earlier pages retained"}
                        )
                    )
                    for e in self.partial_events:
                        events[e.id] = e
                        queue.append((e.destination_chain or chain, e.recipient, depth + 1))
                else:
                    coverage.append(
                        Coverage(chain=chain, address=address, status="unavailable", reason=str(exc))
                    )
                limitations.append(str(exc))
                if isinstance(exc, BudgetExhausted):
                    break
        if queue:
            limitations.append(
                "Acquisition stopped with an unexpanded frontier. No complete-nearestness claim is available."
            )
        return Snapshot(
            mode="live",
            origin="Read-only provider acquisition",
            collected_at=int(time.time()),
            events=list(events.values()),
            assertions=assertions,
            coverage=coverage,
            limitations=list(dict.fromkeys(limitations + self.bridge_limitations)),
            bridge_proofs=list(self.bridge_proofs.values()),
            schema_version="1.1" if self.bridge_proofs else "1.0",
            window_start=spec.start,
            window_end=spec.end,
        )

    def evm_metadata(self, chain, address):
        if not settings.etherscan_api_key:
            raise ProviderError("Etherscan metadata enabled but no key configured")
        data, h = self.fetch(
            "Etherscan metadata",
            "https://api.etherscan.io/v2/api",
            params={
                "chainid": {"ethereum": 1, "bnb": 56, "polygon": 137}[chain],
                "module": "nametag",
                "action": "getaddresstag",
                "address": address,
                "apikey": settings.etherscan_api_key,
            },
        )
        if data.get("status") != "1" or not isinstance(data.get("result"), list):
            raise ProviderError(
                "Etherscan metadata unavailable; Pro Plus entitlement and provider availability must be verified"
            )
        result = []
        for r in data["result"]:
            if r.get("address", "").lower() != address:
                continue
            tag = r.get("nametag")
            if not tag:
                continue
            slugs = {str(v).lower() for v in r.get("labels_slug", [])}
            category = "exchange" if "exchange" in slugs else "unknown"
            # Nametag is a provider label, not necessarily a legal entity or direct-deposit address.
            # Current metadata does not establish historical validity; leave it as a hypothesis for review.
            result.append(
                Assertion(
                    id="etherscan:" + chain + ":" + address + ":" + h[:12],
                    chain=chain,
                    address=address,
                    entity=tag,
                    category=category,
                    role="unknown",
                    grade="hypothesis",
                    source_family="etherscan-metadata",
                    source="Etherscan current nametag; historical validity and legal entity mapping require review",
                    evidence=[h],
                )
            )
        return result


def capabilities():
    return [
        dict(
            chain=c,
            implemented=True,
            configured=(bool(settings.etherscan_api_key) if c in ("ethereum", "bnb", "polygon") else True),
            live_validated=False,
            provider={
                "bitcoin": "BlockCypher" if settings.bitcoin_provider == "blockcypher" else "Esplora",
                "ethereum": "Etherscan V2",
                "bnb": "Etherscan V2",
                "polygon": "Etherscan V2",
                "tron": "TronGrid",
                "solana": "Solana RPC",
            }[c],
            status="Adapter implemented; live validation pending",
            coverage="Confirmed address transactions"
            if c == "bitcoin"
            else "Partial transfer coverage; see acquisition limitations",
        )
        for c in ("bitcoin", "ethereum", "tron", "bnb", "solana", "polygon")
    ]
