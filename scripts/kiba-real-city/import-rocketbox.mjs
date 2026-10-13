// Imports realistic (≈7.5-head) rigged humans from the Microsoft Rocketbox
// Avatar Library (MIT) into NEXUS as self-contained GLBs.
//
//   FBX2GLTF=/path/to/FBX2glTF node scripts/kiba-real-city/import-rocketbox.mjs
//   npm run scan
//
// Requires FBX2glTF (e.g. `npm i fbx2gltf@0.9.7-p1` elsewhere, then
// node_modules/fbx2gltf/bin/Linux/FBX2glTF) and ImageMagick `convert`.
// Steps: pinned sparse git fetch → FBX2glTF (hipoly mesh + 80-joint rig) →
// TGA textures converted to JPEG (head 2048 px, other parts 1024 px) and
// attached by material name → non-metallic PBR → GLB → thumbnail → record.
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { prune, dedup, getBounds } from '@gltf-transform/functions';
import { renderThumbnails } from '../giant-climb/thumbnails.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const cache = path.join(root, '.cache/kiba-real-city/rocketbox');
const work = path.join(root, '.cache/kiba-real-city/rocketbox-work');
const outDir = path.join(root, 'assets/kiba-real-city/realistic');
const thumbDir = path.join(root, 'thumbnails/kiba-real-city');
const dataFile = path.join(root, 'data/assets.json');
const repo = 'https://github.com/microsoft/Microsoft-Rocketbox';
const commit = '0943055db6ec570bcef9f2c8b41c9e5467c808f9';
const fbx2gltf = process.env.FBX2GLTF;
if (!fbx2gltf) throw new Error('Set FBX2GLTF to the FBX2glTF binary path.');

const avatars = [
  ['Military_Male_01', 'Soldier in ACU camouflage with helmet and gear.', ['military', 'soldier']],
  ['Military_Male_02', 'Soldier in ACU camouflage with cap.', ['military', 'soldier']],
  ['Military_Male_03', 'Soldier in ACU camouflage with helmet.', ['military', 'soldier']],
  ['Military_Male_04', 'Soldier in ACU camouflage with helmet and goggles.', ['military', 'soldier']],
  ['Military_Female_01', 'Female soldier in ACU camouflage with helmet.', ['military', 'soldier', 'female']],
  ['Military_Female_02', 'Female soldier in ACU camouflage.', ['military', 'soldier', 'female']],
  ['Police_Male_02', 'Tactical police / SWAT officer in black gear with balaclava.', ['police', 'swat', 'tactical']],
  ['Police_Female_01', 'Female tactical police / SWAT officer with helmet.', ['police', 'swat', 'tactical', 'female']],
  ['Police_Male_01', 'Police officer in blue uniform.', ['police', 'officer']],
  ['Police_Male_03', 'Police officer in dark uniform with cap.', ['police', 'officer']],
  ['Security_Male_01', 'Security guard in dark uniform.', ['security', 'guard']],
  ['Security_Female_01', 'Female security guard in dark uniform.', ['security', 'guard', 'female']],
  ['Pilot_Male_01', 'Airline pilot in uniform.', ['pilot', 'uniform']],
  ['Pilot_Female_02', 'Female airline pilot in uniform.', ['pilot', 'uniform', 'female']],
  ['Fire_Male_01', 'Firefighter in turnout gear with helmet.', ['firefighter', 'rescue']],
  ['Fire_Female_01', 'Female firefighter in turnout gear with helmet.', ['firefighter', 'rescue', 'female']],
  ['Sports_Male_04', 'Athlete in tank top and shorts.', ['athlete', 'sports']],
  ['Sports_Female_02', 'Female athlete in tank top and trousers.', ['athlete', 'sports', 'female']],
  ['Business_Male_01', 'Businessman in dark suit and tie.', ['business', 'suit']],
  ['Business_Female_01', 'Businesswoman in dark suit.', ['business', 'suit', 'female']]
];

const git = (cwd, ...args) => execFileSync('git', args, { cwd, stdio: ['ignore', 'pipe', 'inherit'], env: { ...process.env, GIT_LFS_SKIP_SMUDGE: '1' } }).toString().trim();
const exists = file => fs.access(file).then(() => true, () => false);
const sha256 = data => crypto.createHash('sha256').update(data).digest('hex');
const folder = name => `Assets/Avatars/Professions/${name}`;
const ANIM = 'Assets/Animations';
const clipFiles = name => {
  const g = /_Female_/.test(name) ? 'f' : 'm';
  return {
    Idle: `${ANIM}/all_animations_max_motextr_static/${g}_idle_neutral_01.max.fbx`,
    Walk: `${ANIM}/all_animations_max_motextr_xy/${g}_walk_neutral_01.max.fbx`,
    Run: `${ANIM}/all_animations_max_motextr_xy/${g}_run_neutral_01.max.fbx`
  };
};
const allClipFiles = [...new Set(['Military_Male_01', 'Military_Female_01'].flatMap(n => Object.values(clipFiles(n))))];
const converted = new Map();
async function convertClip(file) {
  if (!converted.has(file)) {
    const out = path.join(work, 'anim_' + path.basename(file).replace(/\W+/g, '_'));
    execFileSync(fbx2gltf, ['--binary', '-i', path.join(cache, file), '-o', out], { stdio: 'ignore' });
    converted.set(file, `${out}.glb`);
  }
  return converted.get(file);
}

// 1. Fetch exactly the pinned commit, only the selected avatar folders.
if (!(await exists(path.join(cache, '.git')))) {
  await fs.mkdir(cache, { recursive: true });
  git(cache, 'init', '-q'); git(cache, 'remote', 'add', 'origin', repo);
}
git(cache, 'sparse-checkout', 'set', '--no-cone', '/LICENSE.md', '/README.md', ...avatars.map(([n]) => `/${folder(n)}/`), ...allClipFiles.map(f => `/${f}`));
git(cache, 'fetch', '-q', '--depth', '1', '--filter=blob:none', 'origin', commit);
git(cache, 'checkout', '-q', 'FETCH_HEAD');
if (git(cache, 'rev-parse', 'HEAD') !== commit) throw new Error('Rocketbox commit mismatch');
const license = await fs.readFile(path.join(cache, 'LICENSE.md'), 'utf8');
if (!/^MIT License/.test(license)) throw new Error('Rocketbox LICENSE.md is not MIT');

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
await fs.mkdir(outDir, { recursive: true });
await fs.mkdir(work, { recursive: true });
const records = [];
for (const [name, description, tags] of avatars) {
  const dir = path.join(cache, folder(name));
  const fbx = path.join(dir, 'Export', `${name}.fbx`);
  const tmp = path.join(work, name);
  execFileSync(fbx2gltf, ['--binary', '-i', fbx, '-o', tmp], { stdio: 'ignore' });
  const document = await io.read(`${tmp}.glb`);
  const rootDoc = document.getRoot();
  for (const t of rootDoc.listTextures()) t.dispose();
  for (const a of rootDoc.listAnimations()) a.dispose();
  const textures = await fs.readdir(path.join(dir, 'Textures'));
  const image = async (file, size) => {
    const jpg = path.join(work, `${name}-${file.replace(/\.tga$/i, '')}-${size}.jpg`);
    execFileSync('convert', [path.join(dir, 'Textures', file), '-resize', `${size}x${size}>`, '-quality', '88', jpg]);
    return document.createTexture(file.replace(/\.tga$/i, '')).setMimeType('image/jpeg').setImage(await fs.readFile(jpg));
  };
  // Texture files are named <material>_color/_normal; a few material names carry
  // typos (e.g. "m172_equpiment"), so fall back to the closest texture prefix.
  const distance = (a, b) => { const d = Array.from({ length: b.length + 1 }, (_, i) => i); for (const ca of a) { let prev = d[0]++; for (let j = 1; j <= b.length; j++) { const tmp = d[j]; d[j] = Math.min(d[j] + 1, d[j - 1] + 1, prev + (ca === b[j - 1] ? 0 : 1)); prev = tmp; } } return d[b.length]; };
  const find = (base, kind) => {
    const exact = textures.find(f => f.toLowerCase().startsWith(`${base}_${kind}`.toLowerCase()));
    if (exact) return exact;
    const candidates = textures.filter(f => new RegExp(`_${kind}`, 'i').test(f)).map(f => [f, distance(base.toLowerCase(), f.toLowerCase().split(`_${kind}`)[0])]).sort((x, y) => x[1] - y[1]);
    return candidates[0]?.[1] <= 2 ? candidates[0][0] : undefined;
  };
  for (const material of rootDoc.listMaterials()) {
    const base = material.getName(), size = /head/i.test(base) ? 2048 : 1024;
    const color = find(base, 'color');
    const normal = find(base, 'normal');
    if (!color) throw new Error(`${name}: no colour texture for ${base}`);
    material.setBaseColorTexture(await image(color, size)).setBaseColorFactor([1, 1, 1, 1]).setMetallicFactor(0).setRoughnessFactor(0.75);
    if (normal) material.setNormalTexture(await image(normal, size));
    if (/hair|eyelash/i.test(base)) material.setAlphaMode('MASK').setAlphaCutoff(0.5);
  }
  // Embed Idle / Walk / Run from the Rocketbox animation library (same Biped
  // bone names). Walk and Run are made in-place by removing the root's linear drift.
  const joints = new Map(rootDoc.listSkins()[0].listJoints().map(n => [n.getName(), n]));
  for (const [clip, file] of Object.entries(clipFiles(name))) {
    const animDoc = await io.read(await convertClip(file));
    const animation = document.createAnimation(clip);
    for (const channel of animDoc.getRoot().listAnimations()[0].listChannels()) {
      const target = joints.get(channel.getTargetNode()?.getName());
      if (!target) continue;
      const sampler = channel.getSampler(), input = sampler.getInput(), output = sampler.getOutput();
      const values = output.getArray().slice();
      if (clip !== 'Idle' && channel.getTargetPath() === 'translation' && target.getName() === 'Bip01') {
        const n = output.getCount();
        for (let c = 0; c < 3; c++) {
          const first = values[c], last = values[(n - 1) * 3 + c], drift = last - first;
          if (Math.abs(drift) < 0.05) continue; // keep vertical bob, remove forward travel
          for (let i = 0; i < n; i++) values[i * 3 + c] -= drift * (i / (n - 1));
        }
      }
      const buffer = rootDoc.listBuffers()[0];
      const newInput = document.createAccessor().setBuffer(buffer).setType(input.getType()).setArray(input.getArray().slice());
      const newOutput = document.createAccessor().setBuffer(buffer).setType(output.getType()).setArray(values);
      const newSampler = document.createAnimationSampler().setInput(newInput).setOutput(newOutput).setInterpolation(sampler.getInterpolation());
      animation.addSampler(newSampler).addChannel(document.createAnimationChannel().setTargetNode(target).setTargetPath(channel.getTargetPath()).setSampler(newSampler));
    }
  }
  await document.transform(dedup(), prune());
  rootDoc.getAsset().generator = 'NEXUS Rocketbox import (FBX2glTF + glTF Transform)';
  const glb = Buffer.from(await io.writeBinary(document));
  const slug = `rocketbox_${name.toLowerCase()}`, rel = `assets/kiba-real-city/realistic/${slug}.glb`;
  await fs.writeFile(path.join(root, rel), glb);
  const b = getBounds(rootDoc.listScenes()[0]), size = b.max.map((v, i) => Number((v - b.min[i]).toFixed(3)));
  const source = await fs.readFile(fbx);
  records.push({
    id: slug, name: `Rocketbox ${name.replace(/_/g, ' ')}`, title: `Rocketbox ${name.replace(/_/g, ' ')}`, collection: 'kiba-real-city', category: 'character', format: 'GLB', type: 'model',
    tags: ['kiba-real-city', 'character', 'humanoid', 'realistic', '7-head', 'rigged', 'animated', 'rocketbox', ...tags],
    gameRoles: ['character'], climbable: false, animated: true,
    description: `${description} Realistic proportions (~7.5 heads), 80-joint 3ds Max Biped rig, PBR colour + normal maps. Embedded clips: Idle, Walk, Run (in-place) from the Rocketbox animation library; 417 more compatible clips exist upstream.`,
    file: rel, localPath: rel, thumbnail: `thumbnails/kiba-real-city/${slug}.png`,
    license: 'MIT', licenseUrl: 'https://github.com/microsoft/Microsoft-Rocketbox/blob/' + commit + '/LICENSE.md', author: 'Microsoft / Rocketbox Studios',
    source: 'Microsoft Rocketbox Avatar Library', sourceUrl: `${repo}/blob/${commit}/${folder(name)}/Export/${name}.fbx`,
    sourceFile: `${folder(name)}/Export/${name}.fbx`, sourceRevision: commit, sourceSha256: sha256(source),
    licenseEvidence: 'Repository LICENSE.md is the MIT License (Copyright (c) 2020 Microsoft); README: "The library of avatars is now released under MIT License" (Nov 2020). Keep the notice in assets/kiba-real-city/realistic/licenses/ with redistributed copies.',
    units: { metresPerUnit: 1, nativeSize: size, suggestedSizeMetres: size, upAxis: 'Y' },
    optimization: { tool: 'FBX2glTF 0.9.7 (hipoly mesh + skin) + glTF Transform; TGA → JPEG (head 2048 px, others 1024 px), metallic 0 / roughness 0.75', sourceBytes: source.length, outputBytes: glb.length },
    notes: 'MIT licence: commercial use allowed; include the copyright and licence notice when redistributing. Specular maps were not carried over (glTF uses metallic-roughness).',
    recommendedFor: ['kiba-real-city', 'threejs', 'character', 'realistic'], addedAt: '2026-10-13T00:00:00.000Z'
  });
  console.log(name, glb.length);
}

await fs.mkdir(path.join(outDir, 'licenses'), { recursive: true });
await fs.writeFile(path.join(outDir, 'licenses', 'Microsoft-Rocketbox-LICENSE.md'), `Source: ${repo} @ ${commit}\n\n${license}`);
await renderThumbnails(thumbDir, records.map(r => path.join(root, r.file)));
const index = JSON.parse(await fs.readFile(dataFile, 'utf8')).filter(a => !records.some(r => r.id === a.id));
await fs.writeFile(dataFile, JSON.stringify([...index, ...records], null, 2) + '\n');
console.log(`Imported ${records.length} Rocketbox avatars.`);
