// assets/deep-boss-mure/*.glb (build_boss_mure.py が作る) から data/assets.json に collection "deep-boss-mure" の記録を書く。
//   python scripts/deep-boss-mure/build_boss_mure.py assets/deep-boss-mure
//   npm run deep-boss-mure   (この import と scan。scan だけを先に走らせると記録が重複するので、必ずこの順で)
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { NodeIO } from '@gltf-transform/core';
import { getBounds } from '@gltf-transform/functions';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../..');
const dataFile = path.join(root, 'data/assets.json');
const COLLECTION = 'deep-boss-mure';
const manifest = JSON.parse(await fs.readFile(path.join(root, `assets/${COLLECTION}/boss_mure_school.json`), 'utf8'));
const ITEMS = [
  { id: 'boss_mure_preview', name: 'The Kingless King (Mure) - Preview', thumb: 'boss_mure_preview', tags: ['boss', 'preview', 'fish-school'], roles: ['boss', 'reference'],
    description: `Silhouette preview of the 4,500 m boss "The Kingless King (Mure)": a quarter of the ${manifest.count.toLocaleString()} fish (${manifest.count / 4} fish, drawn about twice as large) as one vertex-coloured mesh, to check the shape: crown ring and spikes, head, hollow neck and chest, two feather-fan wings, three flowing tail ribbons.` },
  { id: 'boss_mure_fish', name: 'The Kingless King (Mure) - One Fish', thumb: 'boss_mure_fish', tags: ['boss', 'fish', 'instancing'], roles: ['boss', 'instancing-source'],
    description: 'One school fish of the boss as a 6-vertex, 8-triangle elongated octahedron (nose toward +Z), about 1.6 m long. Meant to be instanced for every fish listed in boss_mure_school.bin; replace with a nicer fish if wanted.' },
];
const io = new NodeIO();
const records = [];
for (const c of ITEMS) {
  const rel = `assets/${COLLECTION}/${c.id}.glb`;
  const stat = await fs.stat(path.join(root, rel));
  const doc = await io.read(path.join(root, rel));
  const b = getBounds(doc.getRoot().listScenes()[0]);
  const size = b.max.map((v, i) => Number((v - b.min[i]).toFixed(2)));
  records.push({
    id: c.id, name: c.name, title: c.name, collection: COLLECTION, category: 'boss', subcategory: 'boss', format: 'GLB', type: 'model',
    tags: [COLLECTION, 'deep-sea', 'pearl-sea', 'lowpoly', ...c.tags], gameRoles: c.roles, climbable: false, animated: false,
    description: `${c.description} ${size[0]} × ${size[1]} × ${size[2]} m (W × H × D). Suggested depth: around 4,500 m (a proposal, not a spec).`,
    file: rel, localPath: rel, thumbnail: `thumbnails/${COLLECTION}/${c.thumb}.png`,
    license: 'UNKNOWN', author: 'Yuji5124 (NEXUS original)', source: 'NEXUS original (scripts/deep-boss-mure)',
    sourceUrl: `https://github.com/Yuji5124/nexus/tree/main/scripts/${COLLECTION}`,
    licenseEvidence: 'Original geometry generated procedurally by scripts/deep-boss-mure/boss_mure.py; no third-party meshes, images or code. Follows the 4,500 m boss concept brief of the crustaceans-have-plans game. No licence declared yet.',
    units: { metresPerUnit: 1, nativeSize: size, suggestedSizeMetres: size, upAxis: 'Y' },
    optimization: { tool: 'hand-written glTF writer; vertex colours, no textures', outputBytes: stat.size },
    notes: 'The real boss is the fish layout in boss_mure_school.bin/.json (40,000 fish, float32 x 11 each), not this GLB. Boss faces +Z, tail toward -Z, 1 unit = 1 m. HP, attacks, hit boxes and defeat conditions are not decided.',
    recommendedFor: ['threejs', 'lowpoly', 'underwater', 'deep-sea', 'boss'], addedAt: '2026-11-05T00:00:00.000Z'
  });
}
const index = JSON.parse(await fs.readFile(dataFile, 'utf8')).filter((a) => a.collection !== COLLECTION);
await fs.writeFile(dataFile, JSON.stringify([...index, ...records], null, 2) + '\n');
console.log(`Registered ${records.length} ${COLLECTION} models.`);
