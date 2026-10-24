// Runs inside headless Chromium (bundled by RANVORA ver2's own Vite).
// Builds the procedural objects with RANVORA ver2's code at a pinned commit
// and returns each one as a GLB (base64). Nothing here changes their shape.
import * as THREE from 'three';
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';
import { ProceduralProps } from '@ver2/world/Props';
import { createCabin } from '@ver2/world/Cabin';
import { EnemyView } from '@ver2/combat/EnemyView';
import { WORLD } from '@ver2/world/config';

// Same spacing as RANVORA ver2's #gallery view (src/world/Gallery.ts).
const SPACING = {
  pine: 5.5, spruce: 5, broadleaf: 7, birch: 5, autumn: 6.5, sakura: 7.5, willow: 8, cypress: 4, dead: 5.5,
  bush: 2.5, rock: 3.2, mossyRock: 3.2, crag: 3, pebbles: 2, flowers: 1.6,
};

const exporter = new GLTFExporter();
const toBase64 = buffer => {
  const bytes = new Uint8Array(buffer); let out = '';
  for (let i = 0; i < bytes.length; i += 0x8000) out += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(out);
};
const glb = async object => toBase64(await exporter.parseAsync(object, { binary: true, onlyVisible: true }));

// One GLB per prop kind. Each root child is one variant (RANVORA ver2's GLB rule),
// laid out in a row along +X so a preview shows them all. ver2's
// AssetLoader.toPropSource() ignores the children's positions, so the file can be
// registered back in src/assets/manifest.ts MODEL_OVERRIDES unchanged.
function propScene(key) {
  const source = ProceduralProps[key]();
  const root = new THREE.Group(); root.name = key;
  source.variants.forEach((parts, i) => {
    const variant = new THREE.Group();
    variant.name = `${key}_${String.fromCharCode(65 + i)}`;
    variant.position.x = i * SPACING[key];
    for (const part of parts) variant.add(Object.assign(new THREE.Mesh(part.geometry, part.material), { name: `${variant.name}_mesh` }));
    root.add(variant);
  });
  return { scene: root, variants: source.variants.length };
}

window.exportAll = async () => {
  const out = {};
  for (const key of Object.keys(SPACING)) {
    const { scene, variants } = propScene(key);
    out[key] = { glb: await glb(scene), variants };
  }

  // Log cabin exactly as the world builds it (seed = WORLD.seed + 41), at the origin.
  const cabin = createCabin(WORLD.seed + 41, new THREE.Vector3(), 0).group;
  const lights = [];
  cabin.traverse(o => { if (o.isLight) lights.push(o); });
  for (const light of lights) light.removeFromParent();
  cabin.name = 'LogCabin';
  out.cabin = { glb: await glb(cabin), removedLights: lights.length };

  // Slime enemy (body + eyes) and its drop, as EnemyView draws them.
  const view = new EnemyView(new THREE.Scene());
  const slime = view.makeEnemy({ id: 1, kind: 'slime' }).root;
  slime.name = 'Slime'; slime.removeFromParent();
  out.slime = { glb: await glb(slime) };
  const gel = new THREE.Mesh(view.gelGeo, view.gelMat); gel.name = 'SlimeGel'; gel.position.y = 0.16;
  const gelRoot = new THREE.Group(); gelRoot.name = 'SlimeGel'; gelRoot.add(gel);
  out.slimeGel = { glb: await glb(gelRoot) };
  return out;
};
window.ready = true;
