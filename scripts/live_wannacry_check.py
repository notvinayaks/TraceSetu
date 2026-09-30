import asyncio,httpx,json,re,time,uuid,hashlib
from pathlib import Path
ROOT=Path.cwd();OUT=ROOT/'output/submission/live-case';OUT.mkdir(parents=True,exist_ok=True)
SEED='13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94'
SOURCE='https://www.csk.gov.in/documents/WannacryWannaCryptRansomware_CRITICAL_ALERT_CERT-In.pdf'
async def main():
 async with httpx.AsyncClient(timeout=30) as c:
  r=await c.get(SOURCE);r.raise_for_status();(OUT/'CERT-In_WannaCry_Alert.pdf').write_bytes(r.content)
  source_hash=hashlib.sha256(r.content).hexdigest()
 async with httpx.AsyncClient(base_url='http://127.0.0.1:8787/api',timeout=40) as c:
  pw=re.search(r'^investigator: (.+)$',(ROOT/'.local/bootstrap-credentials.txt').read_text(),re.M)[1].strip()
  r=await c.post('/auth/login',json={'username':'investigator','password':pw});r.raise_for_status();c.headers['X-CSRF-Token']=r.json()['csrf']
  r=await c.post('/cases',json={'title':'WannaCry | public Bitcoin investigation','reference':'PUBLIC-WANNACRY-'+time.strftime('%Y%m%d-%H%M%S'),'description':f'Public historical ransomware case study, not an active police file. CERT-In alert page 4 displays the reported address {SEED}. Source: {SOURCE}. Source PDF SHA-256: {source_hash}. We retrieve real chain history now, scoped to 3 August 2017 UTC. A known ransomware payment address does not establish ownership of downstream wallets or identify an exchange. No official affiliation, legal authority, service attribution or asset freeze is claimed.','members':[]});r.raise_for_status();case=r.json()
  spec={'chain':'bitcoin','address':SEED,'start':1501718400,'end':1501804799,'max_hops':1,'max_requests':6}
  r=await c.post('/cases/'+case['id']+'/analyses',json={'mode':'live','spec':spec},headers={'Idempotency-Key':str(uuid.uuid4())});r.raise_for_status();job=r.json()
  run={'case_id':case['id'],'reference':case['reference'],'job_id':job['id'],'spec':spec,'source_url':SOURCE,'source_pdf_sha256':source_hash}
  (OUT/'run.json').write_text(json.dumps(run,indent=2));print('Actual public-case acquisition started',job['id'],flush=True)
  for _ in range(70):
   await asyncio.sleep(2);r=await c.get('/analyses/'+job['id']);r.raise_for_status();job=r.json()
   if job['status'] not in ['QUEUED','RUNNING']:break
  (OUT/'analysis.json').write_text(json.dumps(job,indent=2))
  a=(job.get('result')or{}).get('analysis')or{};events=a.get('graph',{}).get('events',[])
  summary={**run,'status':job['status'],'event_count':len(events),'candidate_count':len(a.get('candidates',[])),'metrics':job.get('result',{}).get('acquisition_metrics'),'txids':list(dict.fromkeys(e['txid'] for e in events)),'exact_outputs':[(e['recipient'],e['amount']) for e in events],'passed':bool(events) and job['request']['mode']=='live'}
  for suffix,name in [('snapshot','snapshot.json'),('report.pdf','TraceSetu_WannaCry_Report.pdf'),('bundle.zip','TraceSetu_WannaCry_Evidence.zip')]:
   r=await c.get('/analyses/'+job['id']+'/'+suffix);r.raise_for_status();(OUT/name).write_bytes(r.content)
  (OUT/'verification.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2),flush=True)
  assert summary['passed'], 'No successful real-data capture'
asyncio.run(main())
