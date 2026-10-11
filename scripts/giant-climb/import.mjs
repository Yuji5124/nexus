// Imports the GIANT CLIMB selection into NEXUS:
//   source (pinned, see giant-climb/catalog.mjs) → validate license → optimise with
//   glTF Transform → self-contained GLB in assets/giant-climb/<category>/ →
//   thumbnail → metadata record in data/assets.json → credits and report.
// Run `node scripts/giant-climb/fetch-sources.mjs` first, then `npm run scan`.
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { dedup, prune, weld, getBounds, unpartition } from '@gltf-transform/functions';
import draco3d from 'draco3dgltf';
import { sources, assets as catalog, excluded } from '../../giant-climb/catalog.mjs';
import { originals, generate } from './generate-originals.mjs';
import { renderThumbnails } from './thumbnails.mjs';
import { cacheDir } from './fetch-sources.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const outRoot = path.join(root, 'assets/giant-climb');
const thumbRoot = path.join(root, 'thumbnails/giant-climb');
const dataFile = path.join(root, 'data/assets.json');
const BUDGET = { triangles: 20000, bytes: 1024 * 1024 };
const prefix = { 'kenney-space-kit': 'space', 'kenney-city-builder': 'citykit', 'kenney-platformer': 'platformer', 'kenney-fps': 'fpskit', 'kenney-racing': 'racing', 'kenney-mini-arena': 'arena', 'pmndrs-market': 'kenney', 'threejs-r180': 'quaternius', 'nexus-original': 'gc' };
// Suggested metres per model unit so a ~1.4 m player reads correctly. Models are not rescaled.
const metresPerUnit = { 'kenney-space-kit': 4, 'kenney-city-builder': 12, 'kenney-platformer': 1.3, 'kenney-fps': 2, 'kenney-racing': 1.8, 'kenney-mini-arena': 2, 'pmndrs-market': 1.8, 'threejs-r180': 12, 'nexus-original': 1 };
const marketScale = { 'city-building': 8, character: 1.1 };

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'draco3d.decoder': await draco3d.createDecoderModule() });
const sha256 = data => crypto.createHash('sha256').update(data).digest('hex');
const slug = text => text.replace(/\.(glb|gltf)$/i, '').replace(/([a-z])([A-Z])/g, '$1_$2').replace(/[^a-zA-Z0-9]+/g, '_').replace(/^_|_$/g, '').toLowerCase();
const title = text => text.replace(/\.(glb|gltf)$/i, '').replace(/[_-]+/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
const round = v => Number(v.toFixed(3));

function sourcePath(entry) {
  const source = sources[entry.source];
  return path.join(cacheDir, entry.source, source.root || '', entry.file);
}
function sourceUrl(entry) {
  const s = sources[entry.source];
  const file = [s.root, entry.file].filter(Boolean).join('/').split('/').map(encodeURIComponent).join('/');
  if (s.kind === 'git' || s.kind === 'raw') return `${s.repo}/blob/${s.commit}/${s.kind === 'raw' ? 'examples/models/gltf/' : ''}${file}`;
  if (s.kind === 'npm') return `${s.sourceUrl} (${[s.root, entry.file].join('/')})`;
  return s.homepage;
}

async function checkLicense(entry) {
  const s = sources[entry.source];
  if (s.license !== 'CC0-1.0') throw new Error('non-CC0 source');
  if (entry.source === 'pmndrs-market') {
    const info = JSON.parse(await fs.readFile(path.join(path.dirname(sourcePath(entry)), 'info.json'), 'utf8'));
    if (info.creator !== 'kenney' || info.license !== 1) throw new Error(`market item not Kenney/CC0: ${JSON.stringify(info)}`);
    return info;
  }
  if (s.licenseFile) {
    const text = await fs.readFile(path.join(cacheDir, entry.source, s.licenseFile), 'utf8');
    if (!/CC0|Creative Commons Zero/i.test(text)) throw new Error('license file does not state CC0');
  }
  if (entry.source === 'threejs-r180' && !/CC0 1\.0/.test(await fs.readFile(path.join(path.dirname(sourcePath(entry)), 'README.md'), 'utf8'))) throw new Error('README does not state CC0');
  return null;
}

function stats(document) {
  let triangles = 0, vertices = 0;
  for (const mesh of document.getRoot().listMeshes()) for (const prim of mesh.listPrimitives()) {
    const count = prim.getAttribute('POSITION')?.getCount() || 0; vertices += count;
    if (prim.getMode() === 4) triangles += (prim.getIndices()?.getCount() ?? count) / 3;
  }
  const b = getBounds(document.getRoot().listScenes()[0]);
  return { triangles, vertices, min: b.min.map(round), max: b.max.map(round), size: b.max.map((v, i) => round(v - b.min[i])) };
}

const entries = [
  ...catalog,
  ...originals.map(([name, category, tags, roles, description]) => ({ source: 'nexus-original', file: `${name}.glb`, category, tags, roles, description }))
];

await generate();
await fs.rm(outRoot, { recursive: true, force: true });
await fs.rm(thumbRoot, { recursive: true, force: true });
const seen = new Map(), records = [], rejected = [];
for (const entry of entries) {
  const s = sources[entry.source];
  const base = entry.source === 'pmndrs-market' ? entry.slug : path.posix.basename(entry.file);
  const id = entry.source === 'nexus-original' ? slug(base) : `${prefix[entry.source]}_${slug(base)}`;
  try {
    const input = await fs.readFile(sourcePath(entry));
    const inputHash = sha256(input);
    if (seen.has(inputHash)) throw new Error(`duplicate of ${seen.get(inputHash)}`);
    seen.set(inputHash, id);
    await checkLicense(entry);
    const document = await io.read(sourcePath(entry));
    const before = stats(document);
    for (const ext of document.getRoot().listExtensionsUsed()) if (ext.extensionName === 'KHR_draco_mesh_compression') ext.dispose();
    const embedded = document.getRoot().listTextures().some(t => t.getURI() && !t.getURI().startsWith('data:'));
    await document.transform(dedup(), prune(), weld(), unpartition());
    document.getRoot().getAsset().generator = 'NEXUS GIANT CLIMB import (glTF Transform)';
    const after = stats(document);
    if (!after.triangles || after.size.some(v => !Number.isFinite(v)) || after.size.filter(v => v > 0).length < 2) throw new Error('empty or degenerate geometry');
    if (after.triangles > BUDGET.triangles) throw new Error(`${after.triangles} triangles exceeds budget`);
    const glb = Buffer.from(await io.writeBinary(document));
    if (glb.length > BUDGET.bytes) throw new Error(`${glb.length} bytes exceeds budget`);
    const rel = `assets/giant-climb/${entry.category}/${id}.glb`;
    await fs.mkdir(path.dirname(path.join(root, rel)), { recursive: true });
    await fs.writeFile(path.join(root, rel), glb);
    const scale = entry.source === 'pmndrs-market' ? marketScale[entry.category] ?? metresPerUnit[entry.source] : metresPerUnit[entry.source];
    const animations = document.getRoot().listAnimations().map(a => a.getName());
    const description = entry.description || `${title(base)} from ${s.name}.`;
    records.push({
      id, name: entry.name ? title(entry.name) : title(base), title: entry.name ? title(entry.name) : title(base), collection: 'giant-climb',
      category: entry.category, tags: [...new Set(['giant-climb', 'lowpoly', ...entry.tags])], gameRoles: entry.roles,
      climbable: entry.roles.some(r => ['climbable-surface', 'handhold'].includes(r)),
      description, file: rel, localPath: rel, thumbnail: `thumbnails/giant-climb/${id}.png`, format: 'GLB', type: 'model',
      license: 'CC0-1.0', licenseUrl: 'https://creativecommons.org/publicdomain/zero/1.0/', author: s.author, source: s.name,
      sourceUrl: sourceUrl(entry), sourceFile: [s.root, entry.file].filter(Boolean).join('/'), sourceRevision: s.commit || (s.version ? `${s.package}@${s.version}` : 'generated'),
      sourceSha256: inputHash, licenseEvidence: s.note,
      units: { metresPerUnit: scale, nativeSize: after.size, suggestedSizeMetres: after.size.map(v => round(v * scale)), upAxis: 'Y' },
      optimization: { tool: 'glTF Transform 4: dedup, prune, weld, unpartition' + (entry.file.endsWith('.gltf') ? ', Draco decoded, glTF→GLB' : '') + (embedded ? ', external textures embedded' : ''), sourceBytes: input.length, outputBytes: glb.length, sourceTriangles: before.triangles },
      animations, animated: animations.length > 0,
      notes: entry.notes || '', recommendedFor: ['giant-climb', 'threejs', 'lowpoly', ...entry.roles], addedAt: '2026-10-11T00:00:00.000Z'
    });
  } catch (error) { rejected.push({ id, source: entry.source, file: entry.file, reason: error.message }); }
}

console.log(`Imported ${records.length} GLBs, rejected ${rejected.length}. Rendering thumbnails…`);
await renderThumbnails(thumbRoot, records.map(r => path.join(root, r.file)));

// Merge into the NEXUS index: replace the previous giant-climb records, keep everything else.
const index = JSON.parse(await fs.readFile(dataFile, 'utf8')).filter(a => a.collection !== 'giant-climb' && !String(a.file || '').startsWith('assets/giant-climb/'));
await fs.writeFile(dataFile, JSON.stringify([...index, ...records], null, 2) + '\n');

// Credits, license evidence and report.
const used = [...new Set(records.map(r => r.source))];
const bySource = Object.entries(sources).filter(([, s]) => used.includes(s.name));
await fs.mkdir(path.join(outRoot, 'licenses'), { recursive: true });
for (const [id, s] of bySource) {
  const evidence = s.licenseFile ? await fs.readFile(path.join(cacheDir, id, s.licenseFile), 'utf8') : '';
  const excerpt = s.kind === 'git' ? evidence.split('\n').filter(l => /CC0/i.test(l)).join('\n') : evidence;
  await fs.writeFile(path.join(outRoot, 'licenses', `${id}.txt`), [`${s.name}`, `Author: ${s.author}`, `License: CC0 1.0 Universal — https://creativecommons.org/publicdomain/zero/1.0/`, `Source: ${s.repo || s.homepage}${s.commit ? ` @ ${s.commit}` : ''}${s.version ? ` (${s.package}@${s.version}, ${s.integrity})` : ''}`, `Evidence: ${s.note}`, '', excerpt.trim()].join('\n') + '\n');
}
const count = (list, key) => list.reduce((m, r) => (m[r[key]] = (m[r[key]] || 0) + 1, m), {});
const table = (obj, head) => `| ${head} | Count |\n|---|---:|\n` + Object.entries(obj).sort((a, b) => b[1] - a[1]).map(([k, v]) => `| ${k} | ${v} |`).join('\n');
await fs.writeFile(path.join(outRoot, 'CREDITS.md'), `# GIANT CLIMB asset collection — credits\n\nAll ${records.length} models in this folder are CC0 1.0 (public domain). Crediting is not required but appreciated.\n\n` +
  bySource.map(([id, s]) => `- **${s.name}** — ${s.author}. ${s.homepage}. ${records.filter(r => r.source === s.name).length} models. Evidence: \`licenses/${id}.txt\``).join('\n') + '\n');
const totalBytes = records.reduce((n, r) => n + r.optimization.outputBytes, 0), totalSource = records.reduce((n, r) => n + r.optimization.sourceBytes, 0);
await fs.writeFile(path.join(root, 'giant-climb/REPORT.md'), `# GIANT CLIMB asset collection report\n\nGenerated by \`scripts/giant-climb/import.mjs\`.\n\n- Imported: **${records.length}** GLB models (target ≈200; nothing was added only to reach the number)\n- License: all CC0 1.0, verified per source (see \`assets/giant-climb/licenses/\`)\n- Budgets: ≤ ${BUDGET.triangles.toLocaleString()} triangles and ≤ 1 MB per model\n- Total size: ${(totalBytes / 1048576).toFixed(2)} MB (sources ${(totalSource / 1048576).toFixed(2)} MB)\n- Max source triangles: ${Math.max(...records.map(r => r.optimization.sourceTriangles))}\n- Animated / rigged: ${records.filter(r => r.animated).length}\n- Climbable (climbable-surface or handhold role): ${records.filter(r => r.climbable).length}\n\n## By category\n\n${table(count(records, 'category'), 'Category')}\n\n## By source\n\n${table(count(records, 'source'), 'Source')}\n\n## Rejected during import\n\n${rejected.length ? rejected.map(r => `- \`${r.id}\` (${r.source}/${r.file}): ${r.reason}`).join('\n') : 'None.'}\n\n## Excluded during selection\n\n${excluded.map(x => `- **${x.item}** — ${x.reason}`).join('\n')}\n`);
console.log(`Done. ${records.length} records written. Rejected:`, rejected);
