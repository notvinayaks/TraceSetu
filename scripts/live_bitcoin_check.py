"""Bounded live smoke check using a public, recent Bitcoin transaction.

Creates an explicitly neutral demonstration case; never labels ownership or risk.
No synthetic inputs are passed to the analysis. Requires a running local app.
"""
import asyncio
import hashlib
import json
from pathlib import Path
import re
import time
import uuid
import httpx

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'tmp/live-bitcoin'

async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient(timeout=20) as chain:
        base = 'https://mempool.space/api'
        head = await chain.get(base + '/blocks/tip/hash')
        head.raise_for_status()
        blockhash = head.text.strip()
        response = await chain.get(base + '/block/' + blockhash + '/txs')
        response.raise_for_status()
        OUT.joinpath('public-block-transactions.json').write_bytes(response.content)
        # Choose a simple publicly observed transaction for a readable graph.
        transactions = [t for t in response.json() if (t['vin'][0].get('prevout') or {}).get('scriptpubkey_address')]
        tx = min(transactions, key=lambda t: len(t['vin']) + len(t['vout']))
        address = tx['vin'][0]['prevout']['scriptpubkey_address']
    credentials = (ROOT / '.local/bootstrap-credentials.txt').read_text()
    password = re.search(r'^investigator: (.+)$', credentials, re.M)[1].strip()
    async with httpx.AsyncClient(base_url='http://127.0.0.1:8787/api', timeout=30) as app:
        login = await app.post('/auth/login', json={'username': 'investigator', 'password': password})
        login.raise_for_status()
        app.headers['X-CSRF-Token'] = login.json()['csrf']
        case = await app.post('/cases', json={
            'title': 'Bitcoin · live public-data demonstration',
            'reference': 'LIVE-BTC-' + time.strftime('%Y%m%d-%H%M%S'),
            'description': 'Neutral public-chain demonstration selected from a recent block. No suspicion, criminality or wallet ownership is asserted. Live acquisition uses a bounded time window and one custody hop.',
            'members': [],
        })
        case.raise_for_status()
        case_id = case.json()['id']
        spec = {'chain': 'bitcoin', 'address': address,
                'start': tx['status']['block_time']-86400, 'end': int(time.time()),
                'max_hops': 1, 'max_requests': 3}
        request = await app.post('/cases/' + case_id + '/analyses',
            json={'mode': 'live', 'spec': spec}, headers={'Idempotency-Key': str(uuid.uuid4())})
        request.raise_for_status()
        job = request.json()
        OUT.joinpath('run.json').write_text(json.dumps({'case_id': case_id, 'job_id': job['id'], 'spec': spec}, indent=2))
        print('Live job submitted; waiting for acquisition.', flush=True)
        deadline = time.monotonic() + 150
        while time.monotonic() < deadline:
            r = await app.get('/analyses/' + job['id'])
            r.raise_for_status()
            job = r.json()
            if job['status'] not in ['QUEUED', 'RUNNING']:
                break
            await asyncio.sleep(2)
        OUT.joinpath('analysis.json').write_text(json.dumps(job, indent=2))
        snapshot_response = await app.get('/analyses/' + job['id'] + '/snapshot')
        snapshot_response.raise_for_status()
        snapshot = snapshot_response.json()
        OUT.joinpath('snapshot.json').write_text(json.dumps(snapshot, indent=2))
        analysis = (job.get('result') or {}).get('analysis') or {}
        events = analysis.get('graph', {}).get('events', [])
        raw = (job.get('result') or {}).get('raw_evidence', [])
        matching = [e for e in events if e['txid'] == tx['txid']]
        exact = all(e['amount'] == str(tx['vout'][e['output_index']]['value']) for e in matching)
        summary = {
            'checked_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'source': base, 'selection_block_hash': blockhash,
            'selection_response_sha256': hashlib.sha256(response.content).hexdigest(),
            'case_id': case_id, 'job_id': job['id'], 'address': address,
            'status': job['status'], 'mode': job['request']['mode'],
            'event_count': len(events), 'raw_evidence_count': len(raw),
            'observed_transaction_found': bool(matching), 'exact_satoshi_amounts_match': bool(matching) and exact,
            'candidate_count': len(analysis.get('candidates', [])),
            'acquisition_metrics': (job.get('result') or {}).get('acquisition_metrics'),
            'coverage': snapshot.get('coverage'),
            'passed': job['request']['mode'] == 'live' and len(raw) > 0 and bool(matching) and exact,
            'scope': 'One live public Bitcoin acquisition; provider-based transfer verification, not independent consensus or VASP identity validation.',
        }
        OUT.joinpath('results.json').write_text(json.dumps(summary, indent=2))
        print(json.dumps(summary, indent=2))
        if not summary['passed']:
            raise SystemExit(1)

asyncio.run(main())
