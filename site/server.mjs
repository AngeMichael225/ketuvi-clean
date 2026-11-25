import { createServer } from 'node:http';
import { readFile, stat, mkdir, open } from 'node:fs/promises';
import { resolve, relative, isAbsolute, join, extname, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { randomUUID } from 'node:crypto';
import { createMailDelivery, RECIPIENT } from './mail.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const MIME = { '.html':'text/html; charset=utf-8', '.css':'text/css; charset=utf-8', '.js':'text/javascript; charset=utf-8', '.xml':'application/xml; charset=utf-8', '.json':'application/json; charset=utf-8', '.svg':'image/svg+xml', '.png':'image/png', '.webp':'image/webp', '.jpg':'image/jpeg', '.otf':'font/otf', '.ttf':'font/ttf', '.ico':'image/x-icon', '.txt':'text/plain; charset=utf-8' };
class RequestError extends Error {
  constructor(status, message, field) {
    super(message);
    this.status = status;
    this.field = field;
  }
}
function json(res, status, value) { res.writeHead(status, { 'Content-Type':'application/json; charset=utf-8', 'Cache-Control':'no-store' }); res.end(JSON.stringify(value)); }
function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = []; let bytes = 0, tooLarge = false;
    req.on('data', chunk => { bytes += chunk.length; if (bytes > 16384) { tooLarge = true; chunks.length = 0; } else if (!tooLarge) chunks.push(chunk); });
    req.on('end', () => tooLarge ? reject(new RequestError(413, 'Votre message est trop long. Limitez-le à 4 000 caractères.')) : resolve(Buffer.concat(chunks).toString('utf8')));
    req.on('error', reject);
  });
}
function validate(body) {
  if (!body || typeof body !== 'object' || Array.isArray(body)) throw new RequestError(400, 'Vérifiez les renseignements de votre demande.');
  const value = {};
  for (const [key, max] of Object.entries({ name:100, email:254, phone:40, message:4000, service:40, location:160, availability:160 })) {
    value[key] = typeof body[key] === 'string' ? body[key].trim() : '';
    if (value[key].length > max) throw new RequestError(400, `Limitez ce champ à ${max} caractères.`, key);
  }
  if (!['quote','application'].includes(body.kind) || body.website) throw new RequestError(400, 'Vérifiez les renseignements de votre demande.');
  if (value.name.length < 2) throw new RequestError(400, 'Entrez un nom d’au moins deux caractères.', 'name');
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.email)) throw new RequestError(400, 'Entrez une adresse courriel complète, par exemple nom@exemple.ca.', 'email');
  if (body.kind === 'application' && value.message.length < 10) throw new RequestError(400, 'Ajoutez quelques précisions pour atteindre dix caractères.', 'message');
  if (body.consent !== true) throw new RequestError(400, 'Acceptez le traitement des renseignements pour envoyer votre demande.', 'consent');
  const knownService = ['commercial','residential','occasional','general'].includes(value.service);
  if (!knownService && (body.kind === 'quote' || value.service)) throw new RequestError(400, 'Choisissez un service dans la liste.', 'service');
  return { kind:body.kind, ...value, consent:true };
}

export function createSiteServer({ root = join(here,'public'), dataDir = join(here,'.data'), mailDelivery = null } = {}) {
  const publicRoot = resolve(root);
  const delivery = mailDelivery ? 'email' : 'local';
  return createServer(async (req, res) => {
    res.setHeader('X-Content-Type-Options','nosniff');
    res.setHeader('Referrer-Policy','strict-origin-when-cross-origin');
    res.setHeader('X-Frame-Options','SAMEORIGIN');
    try {
      const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
      if (url.pathname === '/api/health' && req.method === 'GET') return json(res,200,{ ok:true, delivery });
      if (url.pathname === '/api/requests' && req.method === 'POST') {
        const origin = req.headers.origin;
        if (req.headers['sec-fetch-site'] === 'cross-site' || (origin && new URL(origin).host !== req.headers.host)) throw new RequestError(403,'Cette demande doit être envoyée depuis le site Ketuvi.');
        if (!(req.headers['content-type'] || '').startsWith('application/json')) throw new RequestError(415,'Le format de la demande n’est pas reconnu.');
        let body; try { body = JSON.parse(await readBody(req)); } catch (error) { if (error.status) throw error; throw new RequestError(400,'Le message reçu n’est pas valide.'); }
        const value = validate(body);
        if (body.expectedDelivery !== undefined && body.expectedDelivery !== delivery) throw new RequestError(409,'Le mode d’envoi a changé. Actualisez la page avant de réessayer.');
        if (mailDelivery) {
          const id = await mailDelivery(dataDir, value, req.headers['idempotency-key']);
          return json(res,201,{ ok:true, receipt:id, delivery:'email' });
        }
        const id = 'KTV-' + randomUUID().slice(0,8).toUpperCase();
        try {
          await mkdir(dataDir,{ recursive:true });
          const file = await open(join(dataDir,'requests.ndjson'),'a',0o600);
          try { await file.write(JSON.stringify({ id, createdAt:new Date().toISOString(), recipient:RECIPIENT, ...value })+'\n'); await file.sync(); } finally { await file.close(); }
        } catch { throw new RequestError(503,'Votre demande n’a pas pu être enregistrée. Réessayez dans un instant.'); }
        return json(res,201,{ ok:true, receipt:id, delivery:'local' });
      }
      if (!['GET','HEAD'].includes(req.method)) throw new RequestError(405,'Méthode non permise.');
      if ((url.pathname === '/contact/' || url.pathname === '/contact') && url.searchParams.has('date_cles')) {
        const moving = url.searchParams.get('service') === 'occasional' && url.searchParams.get('motif') === 'demenagement';
        if (!moving) {
          url.searchParams.delete('date_cles');
          // A redirect without a fragment preserves the visitor's original #demande.
          res.writeHead(307, { Location: '/contact/' + url.search, 'Cache-Control': 'no-store' });
          return res.end();
        }
      }
      if (url.pathname.startsWith('/api/')) throw new RequestError(404,'Page introuvable.');
      let pathname; try { pathname = decodeURIComponent(url.pathname); } catch { throw new RequestError(400,'Adresse invalide.'); }
      if (pathname.includes('\\') || pathname.includes('\0') || pathname.split('/').some(p => p.startsWith('.'))) throw new RequestError(404,'Page introuvable.');
      let path = resolve(publicRoot,'.'+pathname);
      const rel = relative(publicRoot,path);
      if (rel.startsWith('..') || isAbsolute(rel)) throw new RequestError(404,'Page introuvable.');
      let metadata;
      try {
        metadata = await stat(path, { bigint:true });
        if (metadata.isDirectory()) {
          path = join(path,'index.html');
          metadata = await stat(path, { bigint:true });
        }
        if (!metadata.isFile()) throw new Error();
      } catch {
        const errorPage = join(publicRoot,'404.html');
        try {
          const content = await readFile(errorPage);
          res.writeHead(404,{ 'Content-Type':MIME['.html'], 'Content-Length':content.length });
          return res.end(req.method === 'HEAD' ? undefined : content);
        } catch { throw new RequestError(404,'Page introuvable.'); }
      }
      const opaqueTag = `"${metadata.size.toString(16)}-${metadata.mtimeNs.toString(16)}"`;
      const cacheHeaders = { 'Cache-Control':'no-cache', 'ETag':'W/' + opaqueTag };
      const candidates = (req.headers['if-none-match'] || '').split(',').map(tag => tag.trim());
      if (candidates.some(tag => tag === '*' || tag.replace(/^W\//, '') === opaqueTag)) {
        res.writeHead(304, cacheHeaders);
        return res.end();
      }
      const content = req.method === 'HEAD' ? undefined : await readFile(path);
      res.writeHead(200,{
        ...cacheHeaders,
        'Content-Type':MIME[extname(path)] || 'application/octet-stream',
        'Content-Length':content?.length ?? metadata.size.toString()
      });
      res.end(content);
    } catch (error) { if (!res.headersSent) json(res,error.status || 500,{ error:error.status ? error.message : 'Un problème est survenu. Réessayez dans un instant.', field:error.field }); else res.end(); }
  });
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const port = Number(process.env.PORT || 4173);
  const mailDelivery = createMailDelivery({ apiKey:process.env.KETUVI_RESEND_API_KEY, from:process.env.KETUVI_MAIL_FROM });
  const server = createSiteServer({ mailDelivery });
  server.listen(port,'127.0.0.1',() => console.log(`KetuviClean — http://127.0.0.1:${port}`));
  server.on('error',error => { console.error(`Le serveur n’a pas pu démarrer (${error.code}).`); process.exitCode = 1; });
}
