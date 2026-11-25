import { randomUUID } from 'node:crypto';
import { link, mkdir, open, readFile, rename, unlink } from 'node:fs/promises';
import { join } from 'node:path';

export const RECIPIENT = 'info@ketuvi.com';
const serviceNames = { commercial: 'Entretien commercial', residential: 'Entretien résidentiel', occasional: 'Travaux ponctuels', general: 'À discuter' };
const day = 24 * 60 * 60 * 1000;

function deliveryError(status, message) {
  return Object.assign(new Error(message), { status });
}

function emailBody(record, from) {
  const { kind, service, availability, name, email, phone, location, message } = record.request;
  const title = kind === 'quote' ? 'Demande de soumission' : 'Candidature spontanée';
  const context = kind === 'quote' ? 'Service : ' + serviceNames[service] : 'Disponibilités : ' + (availability || 'Non précisées');
  return {
    from,
    to: [RECIPIENT],
    reply_to: email,
    subject: title + ' — ' + record.id,
    text: [title, 'Référence : ' + record.id, '', 'Nom : ' + name, 'Courriel : ' + email,
      'Téléphone : ' + (phone || 'Non précisé'), 'Ville : ' + (location || 'Non précisée'),
      context, '', message].join('\n')
  };
}

// Write a complete file before making it visible, including to another process.
async function storeRecord(path, record, create) {
  const temporary = path + '.' + randomUUID() + '.tmp';
  const file = await open(temporary, 'wx', 0o600);
  try {
    try {
      await file.writeFile(JSON.stringify(record));
      await file.sync();
    } finally {
      await file.close();
    }
    if (create) await link(temporary, path);
    else await rename(temporary, path);
  } finally {
    await unlink(temporary).catch(error => { if (error.code !== 'ENOENT') throw error; });
  }
}

async function pendingRecord(path, value) {
  try {
    return JSON.parse(await readFile(path, 'utf8'));
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
  }
  const record = { id: 'KTV-' + randomUUID().slice(0, 8).toUpperCase(), createdAt: new Date().toISOString(), recipient: RECIPIENT, request: value };
  try {
    await storeRecord(path, record, true);
    return record;
  } catch (error) {
    if (error.code !== 'EEXIST') throw error;
    return JSON.parse(await readFile(path, 'utf8'));
  }
}

export function createMailDelivery({ apiKey, from }, fetchImpl = fetch) {
  if (!apiKey && !from) return null;
  if (!apiKey || !from) throw new Error('Pour activer le courriel, définissez KETUVI_RESEND_API_KEY et KETUVI_MAIL_FROM ensemble.');
  const active = new Map();

  async function deliver(dataDir, key, value, payload) {
    const directory = join(dataDir, 'mail');
    await mkdir(directory, { recursive: true, mode: 0o700 });
    const path = join(directory, key + '.json');
    const record = await pendingRecord(path, value);
    if (JSON.stringify(record.request) !== payload) {
      throw deliveryError(409, 'Cette référence correspond à une autre demande.');
    }
    if (record.emailId) return record.id;
    if (Date.now() - Date.parse(record.createdAt) >= day) {
      throw deliveryError(409, 'Écrivez à ' + RECIPIENT + ' avec la référence ' + record.id + ' pour vérifier votre demande.');
    }
    // Resend remembers an idempotency key for 24 hours, including if our response was lost.
    let emailId;
    try {
      const response = await fetchImpl('https://api.resend.com/emails', {
        method: 'POST',
        headers: { Authorization: 'Bearer ' + apiKey, 'Content-Type': 'application/json', 'Idempotency-Key': 'ketuvi/' + key },
        body: JSON.stringify(emailBody(record, from)),
        redirect: 'error',
        signal: AbortSignal.timeout(8000)
      });
      if (response.ok) emailId = (await response.json()).id;
    } catch {
      // A timeout is ambiguous. Keep the pending request and let the client retry with its original key.
    }
    if (typeof emailId !== 'string' || !emailId.trim()) {
      throw deliveryError(503, 'La messagerie n’a pas confirmé l’envoi. Réessayez avec les mêmes renseignements.');
    }
    await storeRecord(path, { ...record, emailId, acceptedAt: new Date().toISOString() }, false);
    return record.id;
  }

  return async (dataDir, value, clientKey) => {
    const key = (clientKey ?? randomUUID()).toLowerCase();
    if (!/^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/.test(key)) {
      throw deliveryError(400, 'La référence de votre demande est invalide.');
    }
    const payload = JSON.stringify(value);
    const existing = active.get(key);
    if (existing) {
      if (existing.payload !== payload) throw deliveryError(409, 'Cette référence correspond à une autre demande.');
      return existing.result;
    }
    const result = deliver(dataDir, key, value, payload);
    active.set(key, { payload, result });
    try { return await result; }
    finally { active.delete(key); }
  };
}
