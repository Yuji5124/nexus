// Imports the KIBA-REAL-CITY character set (CC0, rigged) into NEXUS.
//   pinned git sources → license check → GLB in assets/kiba-real-city/characters/
//   → thumbnail → index record (collection "kiba-real-city") → license copies.
// KayKit GLBs are stored unmodified. Kenney glTF files are Draco-decoded and
// packed as self-contained GLBs. Run `npm run scan` afterwards.
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { dedup, prune, unpartition, getBounds } from '@gltf-transform/functions';
import draco3d from 'draco3dgltf';
import { renderThumbnails } from '../giant-climb/thumbnails.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const cache = path.join(root, '.cache/kiba-real-city');
const outDir = path.join(root, 'assets/kiba-real-city/characters');
const thumbDir = path.join(root, 'thumbnails/kiba-real-city');
const dataFile = path.join(root, 'data/assets.json');

const sources = {
  'kaykit-adventurers': {
    name: 'KayKit Character Pack: Adventurers 1.0', author: 'Kay Lousberg (www.kaylousberg.com)',
    repo: 'https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0', commit: '672074b73ba276876a19e8816ecdc5241817ab47',
    root: 'addons/kaykit_character_pack_adventures/Characters/gltf', licenseFile: 'LICENSE.txt', copyAsIs: true,
    evidence: 'LICENSE.txt: "License: (Creative Commons Zero, CC0)"; same repo and commit listed on the Godot Asset Library (asset 2129).'
  },
  'kaykit-skeletons': {
    name: 'KayKit Character Pack: Skeletons 1.0', author: 'Kay Lousberg (www.kaylousberg.com)',
    repo: 'https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Skeletons-1.0', commit: '15b62b9bad122f72926c10fb14d622c73819fa54',
    root: 'addons/kaykit_character_pack_skeletons/Characters/gltf', licenseFile: 'LICENSE.txt', copyAsIs: true,
    evidence: 'LICENSE.txt: "License: (Creative Commons Zero, CC0)"; same repo and commit listed on the Godot Asset Library (asset 2566).'
  },
  'kenney-market': {
    name: 'Kenney characters via pmndrs market-assets', author: 'Kenney (www.kenney.nl)',
    repo: 'https://github.com/pmndrs/market-assets', commit: 'c9cfa0236a012093edd5affe200808752375bd90', root: 'files/models',
    evidence: 'info.json lists creator "kenney" and license id 1 (= CC0 in pmndrs/market licenses.js); Kenney publishes these packs as CC0.'
  },
  'kenney-mini-arena': {
    name: 'Kenney Mini Arena (Starter Kit Basic Scene)', author: 'Kenney (www.kenney.nl)',
    repo: 'https://github.com/KenneyNL/Starter-Kit-Basic-Scene', commit: 'a6927e66ff8dd8e173660ce4825abe773c65f683',
    root: 'sample/Mini Arena/Models/GLB format', licenseFile: 'README.md',
    evidence: 'README: "comes with the (CC0 licensed) Mini Arena pack".'
  }
};

const characters = [
  ['kaykit-adventurers', 'Knight.glb', 'kaykit_knight', 'KayKit Knight', 'Armoured knight with sword and shield.', ['knight', 'fantasy', 'hero', 'melee']],
  ['kaykit-adventurers', 'Barbarian.glb', 'kaykit_barbarian', 'KayKit Barbarian', 'Barbarian warrior with axe.', ['barbarian', 'fantasy', 'warrior', 'melee']],
  ['kaykit-adventurers', 'Mage.glb', 'kaykit_mage', 'KayKit Mage', 'Robed mage with staff.', ['mage', 'fantasy', 'caster']],
  ['kaykit-adventurers', 'Rogue.glb', 'kaykit_rogue', 'KayKit Rogue', 'Agile rogue with daggers and crossbow.', ['rogue', 'fantasy', 'ranged']],
  ['kaykit-adventurers', 'Rogue_Hooded.glb', 'kaykit_rogue_hooded', 'KayKit Rogue Hooded', 'Hooded variant of the rogue.', ['rogue', 'hooded', 'fantasy']],
  ['kaykit-skeletons', 'Skeleton_Warrior.glb', 'kaykit_skeleton_warrior', 'KayKit Skeleton Warrior', 'Skeleton warrior enemy.', ['skeleton', 'undead', 'enemy', 'melee']],
  ['kaykit-skeletons', 'Skeleton_Mage.glb', 'kaykit_skeleton_mage', 'KayKit Skeleton Mage', 'Skeleton mage enemy.', ['skeleton', 'undead', 'enemy', 'caster']],
  ['kaykit-skeletons', 'Skeleton_Rogue.glb', 'kaykit_skeleton_rogue', 'KayKit Skeleton Rogue', 'Skeleton rogue enemy.', ['skeleton', 'undead', 'enemy']],
  ['kaykit-skeletons', 'Skeleton_Minion.glb', 'kaykit_skeleton_minion', 'KayKit Skeleton Minion', 'Small skeleton minion enemy.', ['skeleton', 'undead', 'enemy', 'minion']],
  ['kenney-market', 'zombie-1/model.gltf', 'kenney_zombie_1', 'Kenney Zombie 1', 'Blocky zombie, rigged (no animations).', ['zombie', 'undead', 'enemy', 'blocky']],
  ['kenney-market', 'zombie-2/model.gltf', 'kenney_zombie_2', 'Kenney Zombie 2', 'Blocky zombie variant, rigged (no animations).', ['zombie', 'undead', 'enemy', 'blocky']],
  ['kenney-market', 'pirate-captain/model.gltf', 'kenney_pirate_captain', 'Kenney Pirate Captain', 'Blocky pirate captain, rigged (no animations).', ['pirate', 'blocky', 'npc']],
  ['kenney-market', 'pirate-officer/model.gltf', 'kenney_pirate_officer', 'Kenney Pirate Officer', 'Blocky pirate officer, rigged (no animations).', ['pirate', 'blocky', 'npc']],
  ['kenney-market', 'pirate-crew/model.gltf', 'kenney_pirate_crew', 'Kenney Pirate Crew', 'Blocky pirate crew member, rigged (no animations).', ['pirate', 'blocky', 'npc']],
  ['kenney-mini-arena', 'character-soldier.glb', 'kenney_arena_soldier', 'Kenney Arena Soldier', 'Tiny soldier with idle/walk/sprint/jump/attack clips.', ['soldier', 'chibi', 'player', 'tiny']]
];

const git = (cwd, ...args) => execFileSync('git', args, { cwd, stdio: ['ignore', 'pipe', 'inherit'], env: { ...process.env, GIT_LFS_SKIP_SMUDGE: '1' } }).toString().trim();
const sha256 = data => crypto.createHash('sha256').update(data).digest('hex');
const exists = file => fs.access(file).then(() => true, () => false);

async function fetchSource(id, s) {
  const dir = path.join(cache, id);
  const wanted = [...new Set(characters.filter(c => c[0] === id).map(c => path.posix.join(s.root, path.posix.dirname(c[1]))))];
  if (!(await exists(path.join(dir, '.git')))) {
    await fs.mkdir(dir, { recursive: true });
    git(dir, 'init', '-q'); git(dir, 'remote', 'add', 'origin', s.repo);
  }
  git(dir, 'sparse-checkout', 'set', '--no-cone', ...wanted.map(w => `/${w}/`), ...(s.licenseFile ? [`/${s.licenseFile}`] : []));
  git(dir, 'fetch', '-q', '--depth', '1', '--filter=blob:none', 'origin', s.commit);
  git(dir, 'checkout', '-q', 'FETCH_HEAD');
  if (git(dir, 'rev-parse', 'HEAD') !== s.commit) throw new Error(`${id}: commit mismatch`);
  return dir;
}

async function checkLicense(id, dir, file) {
  const s = sources[id];
  if (id === 'kenney-market') {
    const info = JSON.parse(await fs.readFile(path.join(dir, s.root, path.dirname(file), 'info.json'), 'utf8'));
    if (info.creator !== 'kenney' || info.license !== 1) throw new Error(`${file}: not Kenney/CC0`);
    return;
  }
  if (!/CC0/.test(await fs.readFile(path.join(dir, s.licenseFile), 'utf8'))) throw new Error(`${id}: license file does not state CC0`);
}

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'draco3d.decoder': await draco3d.createDecoderModule() });
await fs.mkdir(path.join(outDir, 'licenses'), { recursive: true });
const dirs = {};
for (const [id, s] of Object.entries(sources)) {
  dirs[id] = await fetchSource(id, s);
  const evidence = s.licenseFile ? (await fs.readFile(path.join(dirs[id], s.licenseFile), 'utf8')).split('\n').filter(l => id.startsWith('kaykit') || /CC0/i.test(l)).join('\n') : '';
  await fs.writeFile(path.join(outDir, 'licenses', `${id}.txt`), [s.name, `Author: ${s.author}`, 'License: CC0 1.0 Universal — https://creativecommons.org/publicdomain/zero/1.0/', `Source: ${s.repo} @ ${s.commit}`, `Evidence: ${s.evidence}`, '', evidence.trim()].join('\n') + '\n');
}

const records = [];
for (const [id, file, slug, name, description, tags] of characters) {
  const s = sources[id], src = path.join(dirs[id], s.root, file);
  await checkLicense(id, dirs[id], file);
  const input = await fs.readFile(src);
  const document = await io.read(src);
  let glb;
  if (s.copyAsIs) glb = input;
  else {
    for (const ext of document.getRoot().listExtensionsUsed()) if (ext.extensionName === 'KHR_draco_mesh_compression') ext.dispose();
    await document.transform(dedup(), prune(), unpartition());
    glb = Buffer.from(await io.writeBinary(document));
  }
  const rel = `assets/kiba-real-city/characters/${slug}.glb`;
  await fs.writeFile(path.join(root, rel), glb);
  const b = getBounds(document.getRoot().listScenes()[0]), size = b.max.map((v, i) => Number((v - b.min[i]).toFixed(3)));
  const clips = document.getRoot().listAnimations().length;
  records.push({
    id: slug, name, title: name, collection: 'kiba-real-city', category: 'character', format: 'GLB', type: 'model',
    tags: ['kiba-real-city', 'character', 'humanoid', 'rigged', ...(clips ? ['animated'] : []), 'lowpoly', 'cc0', ...tags],
    gameRoles: ['character', ...(tags.includes('enemy') ? ['enemy'] : [])], climbable: false, animated: clips > 0,
    description: `${description} ${clips ? `${clips} animation clips.` : 'Rig only; retarget animations such as the Quaternius UAL sets.'}`,
    file: rel, localPath: rel, thumbnail: `thumbnails/kiba-real-city/${slug}.png`,
    license: 'CC0-1.0', licenseUrl: 'https://creativecommons.org/publicdomain/zero/1.0/', author: s.author, source: s.name,
    sourceUrl: `${s.repo}/blob/${s.commit}/${[s.root, file].join('/').split('/').map(encodeURIComponent).join('/')}`,
    sourceFile: [s.root, file].join('/'), sourceRevision: s.commit, sourceSha256: sha256(input), licenseEvidence: s.evidence,
    units: { metresPerUnit: 1, nativeSize: size, suggestedSizeMetres: size, upAxis: 'Y' },
    optimization: s.copyAsIs ? { tool: 'none (stored unmodified)', sourceBytes: input.length, outputBytes: glb.length } : { tool: 'glTF Transform 4: Draco decoded, dedup, prune, textures embedded, glTF→GLB', sourceBytes: input.length, outputBytes: glb.length },
    notes: '', recommendedFor: ['kiba-real-city', 'threejs', 'character'], addedAt: '2026-10-13T00:00:00.000Z'
  });
}

await renderThumbnails(thumbDir, records.map(r => path.join(root, r.file)));
const index = JSON.parse(await fs.readFile(dataFile, 'utf8')).filter(a => !records.some(r => r.id === a.id));
await fs.writeFile(dataFile, JSON.stringify([...index, ...records], null, 2) + '\n');
console.log(`Imported ${records.length} characters.`);
