import { readFile, readdir, stat } from 'node:fs/promises';
import { extname, join, relative, resolve, sep } from 'node:path';

const root = resolve('site/public');
const errors = [];
const pages = new Map();

async function collect(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) await collect(path);
    if (entry.isFile() && extname(path) === '.html') {
      const source = await readFile(path, 'utf8');
      const ids = [...source.matchAll(/\sid="([^"]+)"/g)].map(match => match[1]);
      const targets = new Set(ids);
      if (targets.size !== ids.length) errors.push(path + ': duplicate HTML id');
      if ((source.match(/<h1\b/g) || []).length !== 1) errors.push(path + ': expected one h1');
      if (!source.includes('<html lang="fr">')) errors.push(path + ': missing French language');
      pages.set(path, { source, targets });
    }
  }
}

await collect(root);
let references = 0;
const photoPlacements = new Map();
for (const [page, { source, targets }] of pages) {
  // Each <img> is one placement, including images inside gallery templates.
  // Responsive variants and portrait crops share their original's generation ID.
  for (const [, photo] of source.matchAll(/<img\b[^>]*?\ssrc="(\/assets\/photos\/[^"]+)"/g)) {
    const sidecar = join(root, photo + '.json');
    try {
      const { job_id: id, origin } = JSON.parse(await readFile(sidecar, 'utf8'));
      if (!id || !origin) throw new Error('incomplete photo provenance');
      const placement = relative(root, page) + ' (' + photo + ')';
      if (photoPlacements.has(id)) {
        errors.push('Photo reused: ' + photoPlacements.get(id) + ' and ' + placement);
      } else {
        photoPlacements.set(id, placement);
      }
    } catch {
      errors.push(page + ': missing or invalid photo provenance for ' + photo);
    }
  }
  const paths = [...source.matchAll(/\s(?:href|src)="([^"]+)"/g)].map(match => match[1]);
  for (const [tag, action] of source.matchAll(/<form\b[^>]*?\saction="([^"]+)"[^>]*>/gi)) {
    if (!/\smethod="post"/i.test(tag)) paths.push(action);
  }
  for (const [, srcset] of source.matchAll(/\ssrcset="([^"]+)"/g)) {
    for (const candidate of srcset.split(',')) paths.push(candidate.trim().split(/\s+/)[0]);
  }
  for (const [, ids] of source.matchAll(/\s(?:for|form|aria-controls|aria-labelledby|aria-describedby)="([^"]+)"/g)) {
    for (const id of ids.split(/\s+/)) {
      if (!targets.has(id)) errors.push(page + ': unknown element #' + id);
    }
  }

  const base = 'http://local.test/' + relative(root, page).split(sep).join('/');
  for (const ref of paths) {
    const url = new URL(ref.replaceAll('&amp;', '&'), base);
    if (url.origin !== 'http://local.test') continue;
    let file = ref.startsWith('#') ? page : join(root, decodeURIComponent(url.pathname));
    try {
      if ((await stat(file)).isDirectory()) file = join(file, 'index.html');
      await stat(file);
      const fragment = decodeURIComponent(url.hash.slice(1));
      if (fragment && pages.has(file) && !pages.get(file).targets.has(fragment)) {
        errors.push(page + ': missing anchor ' + ref);
      }
      references++;
    } catch {
      errors.push(page + ': missing file ' + ref);
    }
  }
}
if (errors.length) {
  console.error(errors.join('\n'));
  process.exitCode = 1;
} else {
  console.log('Verified ' + pages.size + ' HTML pages, ' + references + ' internal links, anchors and image sources, and ' + photoPlacements.size + ' unique photo placements.');
}
