import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile, rm, utimes } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, dirname, resolve } from 'node:path';
import { createServer } from 'node:http';
import { randomUUID } from 'node:crypto';
import { createSiteServer } from '../server.mjs';
import { createMailDelivery } from '../mail.mjs';

async function fixture(t, brokenStorage = false, mailDelivery = null) {
  const temp = await mkdtemp(join(tmpdir(), 'ketuvi-test-'));
  const root = join(temp, 'public'), dataDir = join(temp, 'private');
  await mkdir(root);
  await writeFile(join(root, 'index.html'), '<h1>KetuviClean</h1>');
  if (brokenStorage) await writeFile(dataDir, 'not a directory');
  const server = createSiteServer({ root, dataDir, mailDelivery });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  t.after(async () => {
    await new Promise(resolve => server.close(resolve));
    assert.equal(dirname(resolve(temp)), resolve(tmpdir()));
    await rm(temp, { recursive: true, force: true });
  });
  return { url: `http://127.0.0.1:${server.address().port}`, root, dataDir };
}
const valid = { kind: 'quote', name: 'Test Intégration', email: 'test@example.com', phone: '', service: 'commercial', message: 'Un entretien pour un espace professionnel.', consent: true };
const post = (url, body, headers = {}) => fetch(url + '/api/requests', { method: 'POST', headers: { 'Content-Type': 'application/json', ...headers }, body: JSON.stringify(body) });

test('revalidates static files, returns their size for HEAD, and serves same-size revisions', async t => {
  const { url, root } = await fixture(t);
  const first = await fetch(url);
  assert.equal(first.status, 200);
  const initial = await first.text();
  const tag = first.headers.get('etag');
  assert.match(tag, /^W\/"[^"]+"$/);
  assert.equal(first.headers.get('cache-control'), 'no-cache');
  const head = await fetch(url, {method:'HEAD'});
  assert.equal(head.headers.get('etag'), tag);
  assert.equal(Number(head.headers.get('content-length')), Buffer.byteLength(initial));
  assert.equal(await head.text(), '');
  const cached = await fetch(url, {headers:{'If-None-Match':'"other", ' + tag}});
  assert.equal(cached.status, 304);
  assert.equal(await cached.text(), '');
  const revision = initial.replace('KetuviClean', 'KetuviClair');
  const path = join(root, 'index.html');
  await writeFile(path, revision);
  const timestamp = new Date(Date.now() + 2000);
  await utimes(path, timestamp, timestamp);
  const updated = await fetch(url, {headers:{'If-None-Match':tag}});
  assert.equal(updated.status, 200);
  assert.notEqual(updated.headers.get('etag'), tag);
  assert.equal(await updated.text(), revision);
  const health = await fetch(url + '/api/health', {headers:{'If-None-Match':'*'}});
  assert.equal(health.status, 200);
  assert.equal(health.headers.get('cache-control'), 'no-store');
  assert.equal(health.headers.get('etag'), null);
});

test('drops a stale key handover date from contact navigation and keeps moving dates', async t => {
  const { url, root } = await fixture(t);
  await mkdir(join(root, 'contact'));
  await writeFile(join(root, 'contact', 'index.html'), '<section id="demande"></section>');

  const stale = await fetch(url + '/contact/?service=occasional&motif=surface-ciblee&date_cles=2027-01-11#demande', { redirect: 'manual' });
  assert.equal(stale.status, 307);
  assert.equal(stale.headers.get('location'), '/contact/?service=occasional&motif=surface-ciblee');
  const otherService = await fetch(url + '/contact?service=commercial&motif=demenagement&espace=bureaux&espace=sols-passages&date_cles=2027-01-11', { method: 'HEAD', redirect: 'manual' });
  assert.equal(otherService.status, 307);
  assert.equal(otherService.headers.get('location'), '/contact/?service=commercial&motif=demenagement&espace=bureaux&espace=sols-passages');

  for (const date of ['', '2027-01-11']) {
    const moving = await fetch(url + '/contact/?service=occasional&motif=demenagement&date_cles=' + date, { redirect: 'manual' });
    assert.equal(moving.status, 200);
  }
});

test('persists a real quote before returning its receipt', async t => {
  const { url, dataDir } = await fixture(t);
  const response = await post(url, valid, { Origin: url });
  assert.equal(response.status, 201);
  const result = await response.json();
  assert.equal(result.delivery, 'local');
  assert.match(result.receipt, /^KTV-/);
  const saved = JSON.parse((await readFile(join(dataDir, 'requests.ndjson'), 'utf8')).trim());
  assert.equal(saved.name, valid.name);
  assert.equal(saved.id, result.receipt);
});
test('rejects an invalid email without saving a request', async t => {
  const { url } = await fixture(t);
  const response = await post(url, { ...valid, email: 'invalid' });
  assert.equal(response.status, 400);
  assert.equal((await response.json()).field, 'email');
});
test('requires a service for quotes and accepts applications without a service', async t => {
  const { url, dataDir } = await fixture(t);
  const quote = await post(url, { ...valid, service: '' });
  assert.equal(quote.status, 400);
  assert.equal((await quote.json()).field, 'service');
  const application = await post(url, { ...valid, kind: 'application', service: '', availability: 'Le matin' });
  assert.equal(application.status, 201);
  const saved = JSON.parse((await readFile(join(dataDir, 'requests.ndjson'), 'utf8')).trim());
  assert.equal(saved.kind, 'application');
  assert.equal(saved.availability, 'Le matin');
});
test('requires an explicit consent and known request kind', async t => {
  const { url } = await fixture(t);
  assert.equal((await post(url, { ...valid, consent: false })).status, 400);
  assert.equal((await post(url, { ...valid, kind: 'unknown' })).status, 400);
});
test('rejects oversized messages and foreign origins', async t => {
  const { url } = await fixture(t);
  assert.equal((await post(url, { ...valid, message: 'x'.repeat(18000) })).status, 413);
  assert.equal((await post(url, valid, { Origin: 'https://unrelated.example' })).status, 403);
});
test('keeps the private inbox and server files outside the public root', async t => {
  const { url } = await fixture(t);
  assert.equal((await fetch(url)).status, 200);
  for (const path of ['/server.mjs', '/.data/requests.ndjson', '/%2e%2e%2fprivate%2frequests.ndjson']) {
    assert.ok([403, 404].includes((await fetch(url + path)).status), path);
  }
});
test('reports a storage failure instead of a success receipt', async t => {
  const { url } = await fixture(t, true);
  const response = await post(url, valid);
  assert.equal(response.status, 503);
  assert.equal((await response.json()).receipt, undefined);
});

test('only enables mail with both provider settings', () => {
  assert.equal(createMailDelivery({}), null);
  assert.throws(() => createMailDelivery({ from: 'test@example.test' }), /KETUVI_RESEND_API_KEY/);
  assert.throws(() => createMailDelivery({ apiKey: 'test-only' }), /KETUVI_MAIL_FROM/);
});

test('waits for mail acceptance and safely retries the same request', async t => {
  const calls = [];
  let providerAvailable = false;
  const provider = createServer(async (req, res) => {
    let body = '';
    for await (const chunk of req) body += chunk;
    calls.push({ key: req.headers['idempotency-key'], body: JSON.parse(body) });
    res.writeHead(providerAvailable ? 200 : 503, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(providerAvailable ? { id: 'accepted-by-stub' } : { error: 'busy' }));
  });
  await new Promise(resolve => provider.listen(0, '127.0.0.1', resolve));
  t.after(() => new Promise(resolve => provider.close(resolve)));
  const relay = 'http://127.0.0.1:' + provider.address().port;
  const mailDelivery = createMailDelivery({ apiKey: 'test-only', from: 'sender@example.test' }, (_, options) => fetch(relay, options));
  const { url, dataDir } = await fixture(t, false, mailDelivery);
  assert.equal((await (await fetch(url + '/api/health')).json()).delivery, 'email');
  const key = randomUUID();
  const headers = { 'Idempotency-Key': key };
  const request = { ...valid, service: 'residential', message: 'Pièces choisies : Cuisine, Salle de bain.\nNettoyer les armoires.' };
  assert.equal((await post(url, { ...request, expectedDelivery: 'local' }, headers)).status, 409);
  assert.equal(calls.length, 0);
  const failed = await post(url, request, headers);
  assert.equal(failed.status, 503);
  assert.equal((await failed.json()).ok, undefined);
  const saved = () => readFile(join(dataDir, 'mail', key + '.json'), 'utf8').then(JSON.parse);
  assert.equal((await saved()).emailId, undefined);

  providerAvailable = true;
  const results = await Promise.all([post(url, request, headers), post(url, request, headers)]);
  const confirmations = await Promise.all(results.map(response => response.json()));
  assert.equal(confirmations[0].delivery, 'email');
  assert.deepEqual(confirmations[0], confirmations[1]);
  const stored = await saved();
  assert.equal(stored.id, confirmations[0].receipt);
  assert.equal(stored.emailId, 'accepted-by-stub');
  assert.equal(calls.length, 2);
  assert.deepEqual(calls[0], calls[1]);
  assert.deepEqual(calls[0].body.to, ['info@ketuvi.com']);
  assert.equal(calls[0].body.reply_to, valid.email);
  assert.match(calls[0].body.text, /Cuisine, Salle de bain/);
  assert.equal((await post(url, request, headers)).status, 201);
  assert.equal((await post(url, { ...request, name: 'Autre personne' }, headers)).status, 409);
  assert.equal(calls.length, 2);
});
