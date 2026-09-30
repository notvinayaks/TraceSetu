const { createRequire } = require('node:module');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const { chromium } = createRequire(path.join(root, 'frontend/package.json'))('playwright');

(async () => {
  const output = path.join(root, 'output/ui-review');
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const errors = [], checks = [];
    page.on('pageerror', e => { errors.push(e.message); fs.writeFileSync(path.join(output, 'page-errors.json'), JSON.stringify(errors)); });
    const shot = name => page.screenshot({ path: path.join(output, name + '.png'), fullPage: true });
    const noOverflow = async () => assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'Horizontal page overflow');
    await page.goto('http://127.0.0.1:8787', { waitUntil: 'networkidle' });
    await shot('01-sign-in');
    const credentials = fs.readFileSync(path.join(root, '.local/bootstrap-credentials.txt'), 'utf8');
    await page.getByLabel('Username', { exact: true }).fill('investigator');
    await page.getByLabel('Password', { exact: true }).fill(credentials.match(/^investigator: (.+)$/m)[1].trim());
    await page.getByRole('button', { name: 'Sign in', exact: true }).click();
    await page.getByRole('heading', { name: 'Investigations', exact: true }).waitFor();
    await page.locator('.case-row').first().waitFor();
    const initial = await page.locator('.case-row').first().getAttribute('data-case-id');
    assert(await page.locator('.case-row').count() <= 8);
    await page.getByRole('button', { name: 'Next', exact: true }).click();
    assert.notEqual(await page.locator('.case-row').first().getAttribute('data-case-id'), initial);
    await page.getByRole('button', { name: 'Previous', exact: true }).click();
    assert.equal(await page.locator('.case-row').first().getAttribute('data-case-id'), initial);
    await page.getByRole('button', { name: 'Closed', exact: true }).click();
    for (const status of await page.locator('.case-row .tag').allTextContents()) assert.equal(status, 'Closed');
    await page.getByRole('button', { name: /^All cases/ }).click();
    await page.getByLabel('Search cases').fill('not-a-real-case-reference-xyz');
    await page.getByRole('heading', { name: 'No matching investigations' }).waitFor();
    await page.getByLabel('Search cases').fill('');
    checks.push('case pagination, status filtering and search');
    await page.getByRole('button', { name: 'New investigation', exact: true }).click();
    await page.getByRole('dialog').waitFor();
    assert.equal(await page.evaluate(() => document.activeElement.name), 'title');
    for (let n = 0; n < 20; n++) {
      await page.keyboard.press('Tab');
      assert(await page.evaluate(() => !!document.activeElement.closest('[role="dialog"]')));
    }
    await page.keyboard.press('Escape');
    await page.getByRole('dialog').waitFor({ state: 'hidden' });
    assert.equal(await page.evaluate(() => document.activeElement.textContent.trim()), 'New investigation');
    checks.push('modal initial focus, keyboard trap, Escape and focus restoration');
    await shot('02-investigations');
    await page.getByLabel('Search cases').fill('Custody frontier');
    await page.locator('.case-row').first().click();
    await page.getByRole('button', { name: 'Inspect evidence', exact: true }).first().waitFor();
    await page.locator('.graph-canvas canvas').first().waitFor();
    await noOverflow();
    await shot('03-custody-workspace');
    await page.getByRole('button', { name: 'Inspect evidence', exact: true }).first().click();
    const inspector = page.getByRole('region', { name: 'Evidence inspector' });
    await inspector.waitFor();
    assert(await page.evaluate(() => document.activeElement.getAttribute('aria-label') === 'Evidence inspector'));
    await shot('04-evidence-inspector');
    await page.keyboard.press('Escape');
    await inspector.waitFor({ state: 'hidden' });
    checks.push('evidence drawer and keyboard dismissal');
    await page.setViewportSize({ width: 390, height: 844 });
    await noOverflow();
    await shot('05-mobile-case');
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.getByRole('button', { name: 'Investigations', exact: true }).click();
    const live = JSON.parse(fs.readFileSync(path.join(root, 'tmp/live-bitcoin/results.json')));
    await page.getByLabel('Search cases').fill('LIVE-BTC');
    await page.locator(`[data-case-id="${live.case_id}"]`).click();
    await page.getByText('Live data acquired', { exact: true }).waitFor();
    const submitted = page.waitForResponse(r => r.url().includes('/analyses') && r.request().method() === 'POST');
    await page.getByRole('button', { name: 'Refresh live data', exact: true }).click();
    const response = await submitted;
    assert(response.ok());
    const newJob = await response.json();
    assert.notEqual(newJob.id, live.job_id);
    assert.equal(response.request().postDataJSON().mode, 'live');
    await page.getByText('Live data acquired', { exact: true }).waitFor({ timeout: 90000 });
    const detail = await (await page.request.get(`http://127.0.0.1:8787/api/analyses/${newJob.id}`)).json();
    assert.equal(detail.request.mode, 'live');
    assert(detail.result.acquisition_metrics.successful_http_responses > 0);
    assert(detail.result.analysis.graph.events.length > 0);
    assert.equal(detail.result.analysis.candidates.length, 0, 'Public transaction history must not invent an ownership label');
    for (const event of detail.result.analysis.graph.events) assert(!event.id.includes('fixture:'));
    const raw = detail.result.raw_evidence[0];
    const rawResponse = await page.request.get(`http://127.0.0.1:8787/api/analyses/${newJob.id}/evidence/${raw.sha256}`);
    assert(rawResponse.ok());
    assert.equal(crypto.createHash('sha256').update(await rawResponse.body()).digest('hex'), raw.sha256);
    const snapshotResponse = await page.request.get(`http://127.0.0.1:8787/api/analyses/${newJob.id}/snapshot`);
    const snapshot = await snapshotResponse.json();
    fs.writeFileSync(path.join(output, 'live-snapshot.json'), JSON.stringify(snapshot, null, 2));
    await page.evaluate(() => scrollTo(0,0));
    await shot('06-live-bitcoin');
    await page.getByRole('button', { name: 'Evidence', exact: true }).click();
    await shot('07-live-transfer-evidence');
    const downloadEvent = page.waitForEvent('download');
    await page.getByRole('link', { name: 'Signed evidence bundle' }).click();
    const bundle = path.join(output, 'Live_Bitcoin_Evidence.zip');
    await (await downloadEvent).saveAs(bundle);
    await page.getByRole('button', { name: 'Verify evidence', exact: true }).click();
    await page.getByLabel('Evidence ZIP (maximum 10 MB)').setInputFiles(bundle);
    await page.getByRole('button', { name: 'Verify bundle', exact: true }).click();
    await page.getByText('Integrity valid · replay matched', { exact: true }).waitFor();
    await shot('08-live-bundle-verified');
    checks.push('real Bitcoin browser refresh, new immutable run, raw evidence SHA-256, unknown attribution, signed bundle replay');
    await page.setViewportSize({ width: 390, height: 844 });
    await noOverflow();
    for (const view of ['VASP directory', 'Data & coverage']) {
      await page.getByRole('button', { name: view, exact: true }).click();
      await noOverflow();
    }
    await page.getByRole('button', { name: 'Investigations', exact: true }).click();
    await page.getByLabel('Search cases').fill('');
    await noOverflow();
    await shot('09-mobile-register');
    checks.push('390px mobile case, register, verification, directory and coverage');
    assert.deepEqual(errors, []);
    const result = { passed: true, checked_at: new Date().toISOString(), checks, pageErrors: errors, live: {
      case_id: live.case_id, job_id: newJob.id, mode: detail.request.mode, status: detail.status,
      events: detail.result.analysis.graph.events.length, candidates: detail.result.analysis.candidates.length,
      metrics: detail.result.acquisition_metrics, raw_evidence: detail.result.raw_evidence,
      scope: 'Fresh public Bitcoin acquisition and processing; no VASP ownership assertion or broad six-chain validation.',
    }};
    fs.writeFileSync(path.join(output, 'results.json'), JSON.stringify(result, null, 2));
    console.log(JSON.stringify(result));
  } catch (error) {
    const page = browser.contexts()[0]?.pages()[0];
    if (page) {
      await page.screenshot({ path: path.join(output, 'failure.png'), fullPage: true });
      console.log((await page.locator('body').innerText()).slice(0, 2800));
    }
    throw error;
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
