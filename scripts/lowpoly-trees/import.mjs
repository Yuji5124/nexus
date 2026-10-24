// Imports ten CC0 low-poly trees from GitHub into NEXUS (collection "lowpoly-trees").
//   pinned git sources → licence check → self-contained GLB in assets/lowpoly-trees/
//   → thumbnail → index record → licence copies. Run `npm run scan` afterwards
//   (`npm run lowpoly-trees` does both).
//
// Geometry, UVs and textures are not changed. Material fixes, recorded per asset
// in `optimization`:
//   - Kenney's exporters write metallicFactor 1, which renders black without an
//     environment map: untextured materials get metallic 0 / roughness 1.
//   - Kenney Nature Kit files come from UniGLTF 1.27, which stores the sRGB colour
//     in baseColorFactor (glTF expects linear), so the trees render washed out
//     (#29c9ab leaves show as #70e6d6). For UniGLTF files the factor is converted
//     sRGB → linear, which reproduces Kenney's own colours.
// Draco-compressed sources are decoded so the GLB loads without a decoder.
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { prune, getBounds } from '@gltf-transform/functions';
import draco3d from 'draco3dgltf';
import { renderThumbnails } from '../giant-climb/thumbnails.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const cache = path.join(root, '.cache/lowpoly-trees');
const outDir = path.join(root, 'assets/lowpoly-trees');
const thumbDir = path.join(root, 'thumbnails/lowpoly-trees');
const dataFile = path.join(root, 'data/assets.json');
const ADDED_AT = '2026-10-24T00:00:00.000Z';

const KENNEY_NATURE = 'Kenney Nature Kit 2.1 (CC0). The original zip is not hosted on GitHub; the files are taken from game projects that bundle the kit with its License.txt. The same bytes appear in three independent repositories (JasonLee228/cruiz, bborbe/driftline, and the Git LFS hashes in jpabloglez/trailpaw), and the GLBs still carry Kenney\'s exporter tag (UniGLTF-1.27), so they are unmodified originals.';

const sources = {
  'kaykit-hexagon': {
    name: 'KayKit Medieval Hexagon Pack 1.0', author: 'Kay Lousberg (www.kaylousberg.com)',
    repo: 'https://github.com/KayKit-Game-Assets/KayKit-Medieval-Hexagon-Pack-1.0', commit: '84fa4e91af6a88989be7c99e0891cede11f2ca38',
    root: 'addons/kaykit_medieval_hexagon_pack/Assets/gltf/decoration/nature', licenseFile: 'LICENSE.txt',
    evidence: 'Official KayKit GitHub repository; LICENSE.txt: "License: (Creative Commons Zero, CC0)".'
  },
  'kaykit-halloween': {
    name: 'KayKit Halloween Bits 1.0', author: 'Kay Lousberg (www.kaylousberg.com)',
    repo: 'https://github.com/KayKit-Game-Assets/KayKit-Halloween-Bits-1.0', commit: '6dc69bf6b2fa766a985754f35ec6a0324090e6c6',
    root: 'addons/kaykit_halloween_bits/Assets/gltf', licenseFile: 'LICENSE.txt',
    evidence: 'Official KayKit GitHub repository; LICENSE.txt: "License: (Creative Commons Zero, CC0)".'
  },
  'market': {
    name: 'Kenney models via pmndrs market-assets', author: 'Kenney (www.kenney.nl)',
    repo: 'https://github.com/pmndrs/market-assets', commit: 'c9cfa0236a012093edd5affe200808752375bd90', root: 'files/models',
    evidence: 'info.json lists creator "kenney" and license id 1 (= CC0 in pmndrs/market licenses.js); Kenney publishes this model as CC0.'
  },
  'kenney-cruiz': {
    name: 'Kenney Nature Kit 2.1 (bundled in JasonLee228/cruiz)', author: 'Kenney (www.kenney.nl)',
    repo: 'https://github.com/JasonLee228/cruiz', commit: '536be4266f70092fc7c33afac9f73a2ed31657a4',
    root: 'public/models/nature', licenseFile: 'public/models/nature/LICENSE-kenney-nature-kit.txt', evidence: KENNEY_NATURE
  },
  'kenney-driftline': {
    name: 'Kenney Nature Kit 2.1 (bundled in bborbe/driftline)', author: 'Kenney (www.kenney.nl)',
    repo: 'https://github.com/bborbe/driftline', commit: 'f93766d18320271128a5a06e36da63d8d40dd46f',
    root: 'assets/nature-kit', licenseFile: 'assets/LICENSES/kenney-nature-kit.txt', evidence: KENNEY_NATURE
  }
};

// [source, file, id, name, description, tags, gameRoles, target height in metres]
const trees = [
  ['kaykit-hexagon', 'tree_single_A.gltf', 'kaykit_pine', 'KayKit Pine', 'Classic low-poly pine: stacked dark-green cones on a short brown trunk.',
    ['pine', 'conifer', 'evergreen', 'forest', 'mountain'], ['scenery', 'obstacle'], 9],
  ['kaykit-hexagon', 'tree_single_B.gltf', 'kaykit_fir_round', 'KayKit Round Fir', 'Soft rounded fir with three bevelled tiers of green foliage.',
    ['fir', 'conifer', 'evergreen', 'forest', 'round'], ['scenery', 'obstacle'], 7],
  ['kaykit-halloween', 'tree_pine_orange_large.gltf', 'kaykit_pine_autumn_orange', 'KayKit Autumn Pine (Orange)', 'Shaggy layered pine in burnt-orange autumn colour.',
    ['pine', 'conifer', 'autumn', 'orange', 'fall', 'halloween'], ['scenery', 'obstacle'], 8],
  ['kaykit-halloween', 'tree_pine_yellow_large.gltf', 'kaykit_pine_autumn_yellow', 'KayKit Autumn Pine (Yellow)', 'Shaggy layered pine in golden-yellow autumn colour.',
    ['pine', 'conifer', 'autumn', 'yellow', 'gold', 'fall', 'halloween'], ['scenery', 'obstacle'], 8],
  ['kaykit-halloween', 'tree_dead_large.gltf', 'kaykit_dead_tree', 'KayKit Dead Tree', 'Bare, twisted dead tree with a few forked branches.',
    ['dead', 'bare', 'spooky', 'halloween', 'wasteland', 'swamp'], ['scenery', 'obstacle'], 7],
  ['market', 'palm-detailed-long/model.gltf', 'kenney_palm', 'Kenney Palm', 'Tall curved palm with a crown of broad drooping fronds.',
    ['palm', 'tropical', 'beach', 'island', 'resort'], ['scenery', 'obstacle'], 8],
  ['kenney-cruiz', 'tree_oak.glb', 'kenney_oak', 'Kenney Oak', 'Round faceted oak crown on a straight trunk, fresh green.',
    ['oak', 'broadleaf', 'deciduous', 'round', 'park', 'forest'], ['scenery', 'obstacle'], 7],
  ['kenney-driftline', 'tree_oak_fall.glb', 'kenney_oak_autumn', 'Kenney Autumn Oak', 'The round oak in autumn: warm orange crown on a pale birch-like trunk.',
    ['oak', 'broadleaf', 'deciduous', 'autumn', 'fall', 'orange'], ['scenery', 'obstacle'], 7],
  ['kenney-driftline', 'tree_detailed.glb', 'kenney_tree_branching', 'Kenney Branching Tree', 'Broadleaf tree whose trunk splits into side branches, each carrying its own faceted canopy.',
    ['broadleaf', 'deciduous', 'branching', 'park', 'forest'], ['scenery', 'obstacle'], 8],
  ['kenney-cruiz', 'tree_plateau.glb', 'kenney_tree_plateau', 'Kenney Plateau Tree', 'Umbrella-like tree with flat stacked canopies, reminiscent of an acacia or bonsai.',
    ['acacia', 'umbrella', 'savanna', 'broadleaf', 'bonsai', 'stylized'], ['scenery', 'obstacle'], 7]
];

const git = (cwd, ...args) => execFileSync('git', args, { cwd, stdio: ['ignore', 'pipe', 'inherit'], env: { ...process.env, GIT_LFS_SKIP_SMUDGE: '1', GIT_TERMINAL_PROMPT: '0' } }).toString().trim();
const sha256 = data => crypto.createHash('sha256').update(data).digest('hex');
const exists = file => fs.access(file).then(() => true, () => false);

async function fetchSource(id, s) {
  const dir = path.join(cache, id);
  const wanted = [...new Set(trees.filter(t => t[0] === id).map(t => path.posix.join(s.root, path.posix.dirname(t[1]))))];
  if (!(await exists(path.join(dir, '.git')))) { await fs.mkdir(dir, { recursive: true }); git(dir, 'init', '-q'); git(dir, 'remote', 'add', 'origin', s.repo); }
  git(dir, 'sparse-checkout', 'set', '--no-cone', ...wanted.map(w => `/${w}/`), ...(s.licenseFile ? [`/${s.licenseFile}`] : []));
  git(dir, 'fetch', '-q', '--depth', '1', '--filter=blob:none', 'origin', s.commit);
  git(dir, 'checkout', '-q', 'FETCH_HEAD');
  if (git(dir, 'rev-parse', 'HEAD') !== s.commit) throw new Error(`${id}: commit mismatch`);
  return dir;
}

async function checkLicense(id, dir, file) {
  const s = sources[id];
  if (id === 'market') {
    const info = JSON.parse(await fs.readFile(path.join(dir, s.root, path.dirname(file), 'info.json'), 'utf8'));
    if (info.creator !== 'kenney' || info.license !== 1) throw new Error(`${file}: not Kenney/CC0`);
    return;
  }
  if (!/Creative Commons Zero, CC0/.test(await fs.readFile(path.join(dir, s.licenseFile), 'utf8'))) throw new Error(`${id}: licence file does not state CC0`);
}

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'draco3d.decoder': await draco3d.createDecoderModule() });
await fs.rm(outDir, { recursive: true, force: true });
await fs.mkdir(path.join(outDir, 'licenses'), { recursive: true });
const dirs = {};
for (const [id, s] of Object.entries(sources)) {
  dirs[id] = await fetchSource(id, s);
  const text = s.licenseFile ? (await fs.readFile(path.join(dirs[id], s.licenseFile), 'utf8')).trim() : '';
  await fs.writeFile(path.join(outDir, 'licenses', `${id}.txt`), [s.name, `Author: ${s.author}`, 'License: CC0 1.0 Universal — https://creativecommons.org/publicdomain/zero/1.0/', `Source: ${s.repo} @ ${s.commit}`, `Evidence: ${s.evidence}`, '', text].join('\n') + '\n');
}

const records = [];
for (const [sourceId, file, id, name, description, tags, gameRoles, targetHeight] of trees) {
  const s = sources[sourceId], sourceFile = [s.root, file].join('/'), src = path.join(dirs[sourceId], sourceFile);
  await checkLicense(sourceId, dirs[sourceId], file);
  const input = await fs.readFile(src);
  const document = await io.read(src);
  let draco = false;
  for (const ext of document.getRoot().listExtensionsUsed()) if (ext.extensionName === 'KHR_draco_mesh_compression') { ext.dispose(); draco = true; }
  const toLinear = c => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
  const generator = (await io.readAsJSON(src)).json.asset?.generator ?? ''; // io.read() replaces it with its own name
  const uniGltf = /^UniGLTF/.test(generator);
  let colourFixed = 0;
  if (uniGltf) for (const m of document.getRoot().listMaterials()) {
    const [r, g, bl, a] = m.getBaseColorFactor(); m.setBaseColorFactor([toLinear(r), toLinear(g), toLinear(bl), a]); colourFixed++;
  }
  let metalFixed = 0;
  for (const m of document.getRoot().listMaterials()) {
    if (!m.getBaseColorTexture() && !m.getMetallicRoughnessTexture() && m.getMetallicFactor() > 0) { m.setMetallicFactor(0); m.setRoughnessFactor(1); metalFixed++; }
  }
  await document.transform(prune());
  const glb = Buffer.from(await io.writeBinary(document));
  const rel = `assets/lowpoly-trees/${id}.glb`;
  await fs.writeFile(path.join(root, rel), glb);
  const b = getBounds(document.getRoot().listScenes()[0]), size = b.max.map((v, i) => Number((v - b.min[i]).toFixed(3)));
  const scale = Number((targetHeight / size[1]).toFixed(3));
  const steps = [file.endsWith('.gltf') ? 'glTF (with its .bin and texture, if any) converted to one self-contained GLB' : 'GLB re-written', ...(draco ? ['Draco decoded'] : []), ...(colourFixed ? [`${colourFixed} base colour(s) converted sRGB → linear (UniGLTF 1.27 stored sRGB values)`] : []), ...(metalFixed ? [`${metalFixed} untextured material(s): metallic 1 → 0, roughness → 1 (Kenney exports render black otherwise)`] : []), 'unused data pruned'];
  records.push({
    id, name, title: name, collection: 'lowpoly-trees', category: 'tree', subcategory: 'tree', format: 'GLB', type: 'model',
    tags: [...new Set(['lowpoly-trees', 'tree', 'lowpoly', 'nature', 'cc0', ...tags])], gameRoles, climbable: false, animated: false,
    description: `${description} Native height ${size[1]} units; scale ×${scale} for a ${targetHeight} m tree.`,
    file: rel, localPath: rel, thumbnail: `thumbnails/lowpoly-trees/${id}.png`,
    license: 'CC0-1.0', licenseUrl: 'https://creativecommons.org/publicdomain/zero/1.0/', author: s.author, source: s.name,
    sourceUrl: `${s.repo}/blob/${s.commit}/${sourceFile.split('/').map(encodeURIComponent).join('/')}`,
    sourceFile, sourceRevision: s.commit, sourceSha256: sha256(input), licenseEvidence: s.evidence,
    units: { metresPerUnit: scale, nativeSize: size, suggestedScale: scale, suggestedSizeMetres: size.map(v => Number((v * scale).toFixed(2))), upAxis: 'Y' },
    optimization: { tool: `glTF Transform 4: ${steps.join('; ')}`, sourceBytes: input.length, outputBytes: glb.length },
    notes: 'Origin at the base of the trunk. The kit is not to real-world scale; use units.suggestedScale for a realistic height.',
    recommendedFor: ['threejs', 'lowpoly', 'nature', 'forest'], addedAt: ADDED_AT
  });
}

await fs.rm(thumbDir, { recursive: true, force: true });
await renderThumbnails(thumbDir, records.map(r => path.join(root, r.file)));
const index = JSON.parse(await fs.readFile(dataFile, 'utf8')).filter(a => a.collection !== 'lowpoly-trees');
await fs.writeFile(dataFile, JSON.stringify([...index, ...records], null, 2) + '\n');
console.log(`Imported ${records.length} trees.`);
