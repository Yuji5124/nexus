// Original low-poly GIANT CLIMB assets, built procedurally with three.js and
// exported as GLB. Output is CC0 1.0 (see assets/giant-climb/CREDITS.md).
// Units are metres, +Y up, origin at bottom centre. The player is ~1.4 m tall.
// Each object merges its parts into one mesh per palette material, so a model
// costs 1–5 draw calls; material names (gc_steel, gc_glow, …) are stable so game
// code can swap or tint them.
import * as THREE from 'three';
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

globalThis.FileReader = class {
  readAsArrayBuffer(blob) { blob.arrayBuffer().then(v => { this.result = v; this.onloadend?.(); }); }
  readAsDataURL(blob) { blob.arrayBuffer().then(v => { this.result = 'data:' + blob.type + ';base64,' + Buffer.from(v).toString('base64'); this.onloadend?.(); }); }
};

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
export const outDir = path.join(root, '.cache/giant-climb/sources/nexus-original');

const palette = {
  steel: [0x5d6d7e, 0.55, 0.45], steelDark: [0x343b45, 0.5, 0.55], armor: [0xe8e4da, 0.2, 0.6],
  red: [0xd8433a, 0.15, 0.55], yellow: [0xf2c12e, 0.1, 0.6], black: [0x1f2228, 0.3, 0.7],
  glow: [0x39e3ff, 0, 0.4, 0x39e3ff], glowRed: [0xff4a3d, 0, 0.4, 0xff3020], glowAmber: [0xffb22e, 0, 0.4, 0xff9a10],
  concrete: [0xbab4a6, 0, 0.9], concreteDark: [0x8a857b, 0, 0.9], glass: [0x6ea4c8, 0.3, 0.2], window: [0x2c3e50, 0.2, 0.3],
  asphalt: [0x3a3d42, 0, 0.95], white: [0xf3f3f0, 0, 0.7], tile: [0xd9cbb3, 0, 0.85], wood: [0x8b5a3c, 0, 0.8],
  green: [0x4f9a54, 0, 0.8], blue: [0x2f6fb8, 0.1, 0.5], orange: [0xe8742a, 0.1, 0.6], cable: [0x23262b, 0.1, 0.8]
};
const materials = {};
function material(key) {
  if (!materials[key]) {
    const [color, metalness, roughness, emissive] = palette[key];
    materials[key] = new THREE.MeshStandardMaterial({ name: 'gc_' + key, color, metalness, roughness, ...(emissive ? { emissive, emissiveIntensity: 1.6 } : {}) });
  }
  return materials[key];
}

class Kit {
  constructor() { this.parts = new Map(); }
  add(geometry, color, { p = [0, 0, 0], r = [0, 0, 0], s = [1, 1, 1] } = {}) {
    const m = new THREE.Matrix4().compose(new THREE.Vector3(...p), new THREE.Quaternion().setFromEuler(new THREE.Euler(...r)), new THREE.Vector3(...s));
    const g = (geometry.index ? geometry.toNonIndexed() : geometry.clone()).applyMatrix4(m);
    for (const name of Object.keys(g.attributes)) if (name !== 'position') g.deleteAttribute(name);
    g.computeVertexNormals();
    if (!this.parts.has(color)) this.parts.set(color, []);
    this.parts.get(color).push(g); return this;
  }
  box(w, h, d, color, p = [0, h / 2, 0], r) { return this.add(new THREE.BoxGeometry(w, h, d), color, { p, r }); }
  cyl(rt, rb, h, seg, color, p = [0, h / 2, 0], r) { return this.add(new THREE.CylinderGeometry(rt, rb, h, seg), color, { p, r }); }
  ball(radius, color, p, detail = 1) { return this.add(new THREE.IcosahedronGeometry(radius, detail), color, { p }); }
  ring(radius, tube, color, p, r, seg = 12) { return this.add(new THREE.TorusGeometry(radius, tube, 4, seg), color, { p, r }); }
  tube(points, radius, color, seg = 16) { return this.add(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points.map(v => new THREE.Vector3(...v))), seg, radius, 5), color); }
  build(name) {
    const group = new THREE.Group(); group.name = name;
    for (const [color, geometries] of this.parts) {
      const mesh = new THREE.Mesh(mergeGeometries(geometries), material(color)); mesh.name = `${name}_${color}`; group.add(mesh);
    }
    return group;
  }
}
const k = () => new Kit();
const deg = d => d * Math.PI / 180;
const rivets = (kit, w, h, z, y0, color = 'steelDark') => { for (const x of [-w / 2 + 0.25, w / 2 - 0.25]) for (const y of [y0 + 0.25, y0 + h - 0.25]) kit.cyl(0.08, 0.08, 0.06, 6, color, [x, y, z], [Math.PI / 2, 0, 0]); };
const grip = (kit, x, y, z, w = 0.7, color = 'yellow') => { kit.box(0.08, 0.08, 0.22, color, [x - w / 2, y, z + 0.11]).box(0.08, 0.08, 0.22, color, [x + w / 2, y, z + 0.11]).box(w + 0.08, 0.08, 0.08, color, [x, y, z + 0.22]); };

// name, category, tags, roles, description, builder
export const originals = [
  // ---------- Giant robot exterior ----------
  ['robot_armor_plate', 'robot-exterior', ['robot', 'armor', 'plate', 'panel', 'mecha'], ['climbable-surface'], '4×4 m bevelled armour plate with rivets; tile it over the robot body.', () => {
    const t = k().box(4, 4, 0.4, 'armor', [0, 2, 0]).box(3.6, 3.6, 0.1, 'steel', [0, 2, 0.24]); rivets(t, 4, 4, 0.32, 0); return t; }],
  ['robot_armor_plate_handholds', 'robot-exterior', ['robot', 'armor', 'plate', 'handhold', 'climb', 'mecha'], ['climbable-surface', 'handhold'], '4×4 m armour plate with a ladder of yellow grip bars — the core climbing surface.', () => {
    const t = k().box(4, 4, 0.4, 'armor', [0, 2, 0]).box(0.5, 4, 0.06, 'red', [-1.6, 2, 0.22]); for (let y = 0.5; y < 4; y += 0.8) grip(t, 0.3, y, 0.2, 0.9); rivets(t, 4, 4, 0.22, 0); return t; }],
  ['robot_armor_plate_vented', 'robot-exterior', ['robot', 'armor', 'vent', 'grille', 'mecha'], ['climbable-surface', 'handhold'], 'Armour plate with horizontal vent slats that double as footholds.', () => {
    const t = k().box(4, 4, 0.4, 'armor', [0, 2, 0]).box(3, 2.4, 0.1, 'black', [0, 2, 0.22]); for (let y = 1.0; y <= 3.0; y += 0.4) t.box(3.1, 0.12, 0.3, 'steel', [0, y, 0.3], [deg(-25), 0, 0]); return t; }],
  ['robot_armor_curved', 'robot-exterior', ['robot', 'armor', 'curved', 'shoulder', 'mecha'], ['climbable-surface'], 'Quarter-cylinder armour shell (radius 3 m) for shoulders, thighs and chest edges.', () => {
    const t = k(); t.add(new THREE.CylinderGeometry(3, 3, 4, 8, 1, true, 0, Math.PI / 2), 'armor', { p: [0, 2, 0] }).add(new THREE.CylinderGeometry(2.7, 2.7, 4.02, 8, 1, true, 0, Math.PI / 2), 'steelDark', { p: [0, 2, 0] });
    for (const y of [0.15, 3.85]) t.add(new THREE.CylinderGeometry(3.08, 3.08, 0.3, 8, 1, true, 0, Math.PI / 2), 'red', { p: [0, y, 0] }); return t; }],
  ['robot_shoulder_pauldron', 'robot-exterior', ['robot', 'shoulder', 'armor', 'pauldron', 'mecha'], ['platform', 'climbable-surface'], 'Big stepped shoulder guard; its flat top is a resting platform.', () =>
    k().box(7, 1.2, 6, 'armor', [0, 0.6, 0]).box(6, 1.0, 5, 'armor', [0, 1.7, 0]).box(5, 0.6, 4, 'red', [0, 2.5, 0]).box(7.2, 0.3, 0.6, 'yellow', [0, 0.9, 3.0]).box(0.8, 0.8, 0.2, 'glow', [2.6, 1.7, 2.55])],
  ['robot_ball_joint', 'robot-exterior', ['robot', 'joint', 'ball', 'mecha'], ['obstacle'], 'Ball joint with a collar ring for shoulders and hips.', () =>
    k().ball(2, 'steelDark', [0, 2, 0], 1).ring(2.05, 0.25, 'steel', [0, 2, 0], [Math.PI / 2, 0, 0], 10).cyl(1.2, 1.4, 0.6, 8, 'steel', [0, 0.3, 0])],
  ['robot_hinge_joint', 'robot-exterior', ['robot', 'joint', 'hinge', 'elbow', 'knee', 'mecha'], ['platform', 'obstacle'], 'Elbow / knee hinge: a 4 m axle drum between two yokes.', () =>
    k().cyl(1.4, 1.4, 3, 10, 'steelDark', [0, 1.5, 0], [0, 0, Math.PI / 2]).box(0.6, 3.2, 3.2, 'armor', [-1.8, 1.6, 0]).box(0.6, 3.2, 3.2, 'armor', [1.8, 1.6, 0]).cyl(0.5, 0.5, 4.2, 8, 'yellow', [0, 1.5, 0], [0, 0, Math.PI / 2])],
  ['robot_piston', 'robot-exterior', ['robot', 'piston', 'hydraulic', 'mecha'], ['climbable-surface'], '6 m hydraulic piston; chrome rod plus sleeve — a pole the player can shimmy up.', () =>
    k().cyl(0.45, 0.45, 3.4, 8, 'steelDark', [0, 1.7, 0]).cyl(0.25, 0.25, 3, 8, 'steel', [0, 4.4, 0]).cyl(0.6, 0.6, 0.4, 8, 'yellow', [0, 0.2, 0]).cyl(0.5, 0.5, 0.4, 8, 'yellow', [0, 5.9, 0])],
  ['robot_forearm_segment', 'robot-exterior', ['robot', 'arm', 'forearm', 'mecha', 'segment'], ['climbable-surface', 'platform'], '8 m chunky forearm block with vents and side rails — a horizontal walkway when the arm is lowered.', () => {
    const t = k().box(4, 4, 8, 'armor', [0, 2, 0]).box(4.1, 0.5, 8.1, 'red', [0, 3.3, 0]); for (let z = -3; z <= 3; z += 1.5) t.box(0.2, 1.2, 0.8, 'black', [2.05, 1.6, z]); t.box(0.2, 0.2, 7, 'yellow', [-2.2, 2.6, 0]); return t; }],
  ['robot_hand_palm', 'robot-exterior', ['robot', 'hand', 'palm', 'mecha', 'giant'], ['platform'], 'Open palm (6 m) — the platform the robot lifts the player on.', () => {
    const t = k().box(6, 1.2, 6, 'armor', [0, 0.6, 0]).box(5.4, 0.2, 5.4, 'steel', [0, 1.3, 0]).box(2, 0.3, 2, 'glow', [0, 1.4, 0]);
    for (const x of [-2.1, -0.7, 0.7, 2.1]) t.box(1.1, 1.0, 2.2, 'armor', [x, 0.9, 4.1]).box(1.1, 0.2, 0.2, 'steelDark', [x, 1.0, 3.0]); return t; }],
  ['robot_finger_segment', 'robot-exterior', ['robot', 'finger', 'hand', 'mecha'], ['platform', 'climbable-surface'], '2.4 m finger phalanx with knuckle drum.', () =>
    k().box(1.2, 1.1, 2.4, 'armor', [0, 0.55, 0]).cyl(0.5, 0.5, 1.3, 8, 'steelDark', [0, 0.55, -1.3], [0, 0, Math.PI / 2]).box(1.25, 0.2, 2.0, 'steel', [0, 1.1, 0.1])],
  ['robot_fingertip', 'robot-exterior', ['robot', 'finger', 'tip', 'hand', 'mecha'], ['platform'], 'Tapered fingertip that caps a finger chain.', () =>
    k().box(1.2, 1.1, 1.4, 'armor', [0, 0.55, 0]).cyl(0.35, 0.6, 1.0, 6, 'armor', [0, 0.55, 1.2], [Math.PI / 2, 0, 0]).box(0.8, 0.12, 0.6, 'red', [0, 1.12, 0])],
  ['robot_foot', 'robot-exterior', ['robot', 'foot', 'leg', 'mecha', 'giant'], ['platform', 'climbable-surface'], 'Robot foot (10 m long) with toe plates — the first climb from street level.', () =>
    k().box(7, 2.5, 10, 'armor', [0, 1.25, 0]).box(7.2, 0.8, 10.2, 'steelDark', [0, 0.4, 0]).box(6, 2, 3, 'armor', [0, 3.5, -2]).box(7.3, 0.4, 0.6, 'yellow', [0, 1.8, 5.0]).box(1.4, 0.8, 0.2, 'glowAmber', [-2.4, 1.6, 5.1]).box(1.4, 0.8, 0.2, 'glowAmber', [2.4, 1.6, 5.1])],
  ['robot_spine_segment', 'robot-exterior', ['robot', 'spine', 'back', 'mecha'], ['climbable-surface', 'handhold'], 'Vertebra-like back segment; stack vertically to build the robot spine climb.', () =>
    k().box(3, 2, 2, 'steelDark', [0, 1, 0]).box(5, 0.6, 1.6, 'armor', [0, 1.6, 0]).box(1.2, 1.4, 1.2, 'red', [0, 1.2, 1.4]).cyl(0.4, 0.4, 2.2, 8, 'steel', [0, 1, 0])],
  ['robot_head', 'robot-exterior', ['robot', 'head', 'visor', 'mecha', 'giant', 'goal'], ['landmark', 'goal'], 'Blocky robot head (8 m) with glowing visor and crest — the final climb target.', () =>
    k().box(8, 6, 7, 'armor', [0, 3, 0]).box(7, 1.4, 0.4, 'black', [0, 3.8, 3.55]).box(6.4, 0.7, 0.2, 'glowRed', [0, 3.8, 3.8]).box(1.2, 2.5, 6, 'red', [0, 7.2, -0.5]).box(9, 1.4, 2, 'steel', [0, 1.6, 0]).box(0.6, 3, 0.6, 'steelDark', [3.6, 7.5, -2])],
  ['robot_eye_sensor', 'robot-exterior', ['robot', 'eye', 'sensor', 'camera', 'mecha'], ['decoration', 'hazard'], 'Round optical sensor housing with glowing lens.', () =>
    k().cyl(1.2, 1.4, 1, 10, 'steelDark', [0, 0.5, 0], [Math.PI / 2, 0, 0]).cyl(0.8, 0.8, 0.2, 10, 'glowRed', [0, 0.5, 0.55], [Math.PI / 2, 0, 0]).ring(1.25, 0.12, 'yellow', [0, 0.5, 0.45], [0, 0, 0], 10)],
  ['robot_antenna', 'robot-exterior', ['robot', 'antenna', 'head', 'mecha'], ['handhold', 'decoration'], '6 m antenna mast with warning-light tip.', () =>
    k().cyl(0.6, 0.8, 0.6, 6, 'steelDark', [0, 0.3, 0]).cyl(0.12, 0.2, 5, 6, 'steel', [0, 3.1, 0]).ball(0.3, 'glowRed', [0, 5.8, 0], 0).ring(0.5, 0.06, 'yellow', [0, 2, 0], [Math.PI / 2, 0, 0], 8).ring(0.4, 0.06, 'yellow', [0, 3.8, 0], [Math.PI / 2, 0, 0], 8)],
  ['robot_thruster_nozzle', 'robot-exterior', ['robot', 'thruster', 'jet', 'booster', 'hazard'], ['hazard'], 'Back-pack thruster bell; fires as a timed hazard.', () =>
    k().cyl(1.2, 1.8, 2.4, 10, 'steelDark', [0, 1.2, 0]).cyl(1.25, 1.25, 0.6, 10, 'red', [0, 2.6, 0]).cyl(1.3, 1.3, 0.1, 10, 'glowAmber', [0, 0.05, 0])],
  ['robot_hatch_door', 'robot-exterior', ['robot', 'hatch', 'door', 'entrance', 'interior'], ['landmark'], 'Maintenance hatch frame with warning stripes — entrance to the robot interior.', () => {
    const t = k().box(4, 4, 0.5, 'armor', [0, 2, 0]).box(2.4, 2.8, 0.3, 'steelDark', [0, 1.7, 0.2]).box(0.4, 0.4, 0.2, 'glow', [1.6, 3.2, 0.3]);
    for (let i = -1; i <= 1; i += 0.5) t.box(0.3, 0.3, 0.08, i % 1 === 0 ? 'yellow' : 'black', [i, 3.45, 0.29]); grip(t, 0, 1.7, 0.33, 0.6, 'steel'); return t; }],
  ['robot_ladder_rungs', 'robot-exterior', ['robot', 'ladder', 'rungs', 'climb'], ['handhold', 'climbable-surface'], '6 m service ladder bolted to the hull.', () => {
    const t = k().box(0.12, 6, 0.12, 'steel', [-0.4, 3, 0.25]).box(0.12, 6, 0.12, 'steel', [0.4, 3, 0.25]); for (let y = 0.3; y < 6; y += 0.4) t.box(0.8, 0.07, 0.07, 'yellow', [0, y, 0.25]); return t; }],
  ['robot_grip_handle', 'robot-exterior', ['robot', 'handhold', 'grip', 'climb'], ['handhold'], 'Single grab handle; scatter on surfaces to author climb routes.', () => { const t = k().box(1, 0.5, 0.1, 'steelDark', [0, 0.25, 0.05]); grip(t, 0, 0.25, 0.1, 0.7); return t; }],
  ['robot_ledge_bracket', 'robot-exterior', ['robot', 'ledge', 'bracket', 'platform'], ['platform'], '2 m cantilever ledge for a rest stop on a sheer wall.', () =>
    k().box(2, 0.25, 1.2, 'steel', [0, 1.0, 0.6]).box(0.2, 1.0, 1.0, 'steelDark', [-0.8, 0.5, 0.5]).box(0.2, 1.0, 1.0, 'steelDark', [0.8, 0.5, 0.5]).box(2.05, 0.08, 0.1, 'yellow', [0, 1.15, 1.2])],
  ['robot_gear_large', 'robot-exterior', ['robot', 'gear', 'cog', 'machine', 'rotating'], ['platform', 'hazard'], '4 m rotating gear (rotate around Z) — a moving platform.', () => {
    const t = k().cyl(1.8, 1.8, 0.6, 16, 'steel', [0, 0, 0], [Math.PI / 2, 0, 0]).cyl(0.5, 0.5, 0.8, 8, 'red', [0, 0, 0], [Math.PI / 2, 0, 0]);
    for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; t.box(0.5, 0.45, 0.6, 'steel', [Math.cos(a) * 2, Math.sin(a) * 2, 0], [0, 0, a]); } return t; }],
  ['robot_warning_beacon', 'robot-exterior', ['robot', 'beacon', 'light', 'warning'], ['decoration'], 'Rotating warning beacon.', () =>
    k().cyl(0.35, 0.4, 0.2, 8, 'steelDark', [0, 0.1, 0]).cyl(0.28, 0.3, 0.45, 8, 'glowAmber', [0, 0.42, 0]).cyl(0.1, 0.3, 0.12, 8, 'steelDark', [0, 0.7, 0])],

  // ---------- Robot interior ----------
  ['interior_catwalk_straight', 'robot-interior', ['robot', 'interior', 'catwalk', 'grate', 'modular'], ['walkable-floor', 'handhold', 'modular-kit'], '4 m grated catwalk with handrails (2 m wide).', () => {
    const t = k().box(2, 0.12, 4, 'steelDark', [0, 0, 0]); for (let z = -1.8; z <= 1.8; z += 0.4) t.box(2, 0.04, 0.06, 'steel', [0, 0.08, z]);
    for (const x of [-0.95, 0.95]) { t.box(0.06, 0.06, 4, 'yellow', [x, 1.0, 0]).box(0.06, 0.06, 4, 'steel', [x, 0.5, 0]); for (const z of [-1.9, 0, 1.9]) t.box(0.06, 1, 0.06, 'steel', [x, 0.5, z]); } return t; }],
  ['interior_catwalk_corner', 'robot-interior', ['robot', 'interior', 'catwalk', 'corner', 'modular'], ['walkable-floor', 'modular-kit'], '2×2 m catwalk corner piece.', () =>
    k().box(2, 0.12, 2, 'steelDark', [0, 0, 0]).box(0.06, 0.06, 2, 'yellow', [-0.95, 1, 0]).box(2, 0.06, 0.06, 'yellow', [0, 1, -0.95]).box(0.06, 1, 0.06, 'steel', [-0.95, 0.5, -0.95])],
  ['interior_shaft_ladder', 'robot-interior', ['robot', 'interior', 'shaft', 'ladder', 'vertical'], ['climbable-surface', 'handhold'], '8 m vertical maintenance shaft (open front) with ladder.', () => {
    const t = k().box(3, 8, 0.2, 'steelDark', [0, 4, -1.4]).box(0.2, 8, 3, 'steel', [-1.4, 4, 0]).box(0.2, 8, 3, 'steel', [1.4, 4, 0]);
    for (let y = 0.4; y < 8; y += 0.4) t.box(0.8, 0.06, 0.06, 'yellow', [0, y, -1.05]); for (let y = 1; y < 8; y += 2) t.box(0.3, 0.3, 0.05, 'glow', [1.28, y, -1.0]); return t; }],
  ['interior_control_console', 'robot-interior', ['robot', 'interior', 'console', 'control-room', 'core'], ['decoration', 'goal'], 'Pilot-less control console with glowing screens.', () =>
    k().box(3, 1, 1.2, 'steelDark', [0, 0.5, 0]).box(3, 0.2, 1.0, 'steel', [0, 1.1, 0.1], [deg(-20), 0, 0]).box(2.6, 1.2, 0.1, 'black', [0, 1.9, -0.45]).box(2.4, 1.0, 0.05, 'glow', [0, 1.9, -0.38]).box(0.2, 0.08, 0.2, 'glowRed', [-1, 1.25, 0.3]).box(0.2, 0.08, 0.2, 'glowAmber', [-0.6, 1.25, 0.3])],
  ['interior_power_core', 'robot-interior', ['robot', 'core', 'reactor', 'goal', 'boss', 'glow'], ['goal', 'landmark'], 'Reactor core — the shutdown target. Glowing crystal held by clamps.', () => {
    const t = k().cyl(2.2, 2.6, 0.8, 8, 'steelDark', [0, 0.4, 0]).cyl(2.6, 2.2, 0.8, 8, 'steelDark', [0, 5.6, 0]).add(new THREE.OctahedronGeometry(1.4, 0), 'glow', { p: [0, 3, 0], s: [1, 1.6, 1] });
    for (let i = 0; i < 4; i++) { const a = i * Math.PI / 2 + Math.PI / 4; t.box(0.4, 4.4, 0.4, 'red', [Math.cos(a) * 2, 3, Math.sin(a) * 2]); } t.ring(1.9, 0.12, 'yellow', [0, 3, 0], [Math.PI / 2, 0, 0], 12); return t; }],
  ['interior_power_conduit', 'robot-interior', ['robot', 'interior', 'conduit', 'energy', 'pipe', 'glow'], ['climbable-surface', 'hazard'], '4 m energy conduit with glowing windows; runs along walls.', () => {
    const t = k().cyl(0.4, 0.4, 4, 8, 'steelDark', [0, 0.4, 0], [Math.PI / 2, 0, 0]); for (let z = -1.5; z <= 1.5; z += 1) t.box(0.82, 0.3, 0.4, 'glow', [0, 0.4, z]); t.box(0.9, 0.12, 0.2, 'steel', [0, 0.06, -2]).box(0.9, 0.12, 0.2, 'steel', [0, 0.06, 2]); return t; }],
  ['interior_machine_rack', 'robot-interior', ['robot', 'interior', 'machine', 'rack', 'server'], ['obstacle', 'climbable-surface'], '3 m equipment rack with blinking lights; stack as climbable blocks.', () => {
    const t = k().box(1.6, 3, 1.2, 'steelDark', [0, 1.5, 0]); for (let y = 0.5; y < 3; y += 0.5) t.box(1.4, 0.35, 0.05, 'black', [0, y, 0.62]).box(0.12, 0.06, 0.03, y % 1 ? 'glow' : 'glowAmber', [0.5, y, 0.66]); return t; }],
  ['interior_cable_bundle', 'robot-interior', ['robot', 'interior', 'cable', 'wire', 'swing'], ['handhold', 'decoration'], 'Hanging cable bundle (6 m span, 2 m sag) — grab-and-swing.', () =>
    k().tube([[-3, 4, 0], [-1.5, 2.6, 0.1], [0, 2.1, 0], [1.5, 2.6, -0.1], [3, 4, 0]], 0.14, 'cable', 20).tube([[-3, 4, 0.3], [-1.5, 2.4, 0.4], [0, 1.9, 0.3], [1.5, 2.4, 0.2], [3, 4, 0.3]], 0.1, 'red', 20).tube([[-3, 4, -0.3], [-1.5, 2.8, -0.3], [0, 2.3, -0.4], [1.5, 2.8, -0.3], [3, 4, -0.3]], 0.1, 'yellow', 20).box(0.6, 0.6, 1, 'steel', [-3, 4, 0]).box(0.6, 0.6, 1, 'steel', [3, 4, 0])],
  ['interior_steam_vent', 'robot-interior', ['robot', 'interior', 'vent', 'steam', 'hazard', 'trap'], ['hazard'], 'Floor steam vent; spawn particles above it as a timed hazard.', () => {
    const t = k().box(2, 0.2, 2, 'steelDark', [0, 0.1, 0]); for (let x = -0.6; x <= 0.6; x += 0.3) t.box(0.12, 0.06, 1.4, 'black', [x, 0.22, 0]); t.box(2.05, 0.06, 0.15, 'yellow', [0, 0.2, 0.95]).box(2.05, 0.06, 0.15, 'yellow', [0, 0.2, -0.95]); return t; }],
  ['interior_moving_lift', 'robot-interior', ['robot', 'interior', 'lift', 'elevator', 'moving', 'platform'], ['platform'], '3×3 m lift platform with guide posts — animate along Y.', () =>
    k().box(3, 0.3, 3, 'steel', [0, 0.15, 0]).box(3.05, 0.06, 0.2, 'yellow', [0, 0.32, 1.4]).box(3.05, 0.06, 0.2, 'yellow', [0, 0.32, -1.4]).box(0.15, 1.1, 0.15, 'steelDark', [-1.4, 0.85, 0]).box(0.15, 1.1, 0.15, 'steelDark', [1.4, 0.85, 0]).box(2.95, 0.08, 0.08, 'yellow', [0, 1.35, 0])],

  // ---------- Tokyo city ----------
  ['city_office_tower', 'city-building', ['city', 'tokyo', 'office', 'skyscraper', 'building', 'tall'], ['climbable-surface', 'landmark'], '60 m glass office tower with setback crown and rooftop helipad.', () => {
    const t = k().box(18, 50, 18, 'glass', [0, 25, 0]).box(14, 8, 14, 'glass', [0, 54, 0]).box(18.4, 3, 18.4, 'concrete', [0, 1.5, 0]).box(10, 1, 10, 'concreteDark', [0, 58.5, 0]).cyl(3, 3, 0.2, 10, 'yellow', [0, 59.1, 0]);
    for (let y = 4; y < 50; y += 3.5) t.box(18.2, 0.4, 18.2, 'concrete', [0, y, 0]); for (const x of [-9, 9]) for (const z of [-9, 9]) t.box(1, 50, 1, 'concrete', [x, 25, z]); return t; }],
  ['city_apartment_block', 'city-building', ['city', 'tokyo', 'apartment', 'mansion', 'balcony', 'building'], ['climbable-surface', 'platform'], '10-storey apartment block with balconies — every balcony is a ledge.', () => {
    const t = k().box(16, 30, 10, 'tile', [0, 15, 0]).box(16.4, 0.6, 10.4, 'concreteDark', [0, 30.3, 0]);
    for (let y = 3; y < 30; y += 3) { t.box(16, 0.2, 1.4, 'concrete', [0, y, 5.7]).box(16, 1.0, 0.1, 'white', [0, y + 0.6, 6.35]); for (let x = -6; x <= 6; x += 4) t.box(2.4, 2, 0.1, 'window', [x, y + 1.2, 5.02]); } return t; }],
  ['city_pencil_building', 'city-building', ['city', 'tokyo', 'pencil-building', 'zakkyo', 'signage', 'building'], ['climbable-surface', 'handhold'], 'Narrow Tokyo "pencil" building with stacked vertical signboards.', () => {
    const t = k().box(6, 27, 8, 'concrete', [0, 13.5, 0]).box(6.2, 1, 8.2, 'concreteDark', [0, 27.5, 0]);
    for (let y = 3; y < 27; y += 3) t.box(4.6, 2, 0.1, 'window', [0, y + 1, 4.03]); const colors = ['red', 'yellow', 'blue', 'green', 'orange', 'white'];
    for (let i = 0; i < 6; i++) t.box(0.3, 3, 1.4, colors[i], [3.25, 5 + i * 3.6, 3]); return t; }],
  ['city_corner_store', 'city-building', ['city', 'tokyo', 'konbini', 'convenience-store', 'shop', 'building'], ['platform', 'background'], 'Generic (unbranded) 24h convenience store with striped fascia.', () =>
    k().box(14, 4.5, 10, 'white', [0, 2.25, 0]).box(12, 2.8, 0.1, 'glass', [0, 1.6, 5.02]).box(14.2, 0.5, 10.2, 'green', [0, 4.0, 0]).box(14.2, 0.3, 10.2, 'blue', [0, 3.6, 0]).box(3, 2, 0.4, 'white', [6, 5.5, 4.5]).box(3, 0.4, 0.5, 'glowAmber', [6, 6.1, 4.5]).box(1.2, 0.8, 1.2, 'concreteDark', [-4, 4.9, -2])],
  ['city_rooftop_water_tank', 'city-building', ['city', 'tokyo', 'rooftop', 'water-tank', 'prop'], ['platform', 'obstacle'], 'Rooftop water tank on steel legs.', () => {
    const t = k().cyl(1.6, 1.6, 2.6, 10, 'white', [0, 3.3, 0]).cyl(1.7, 1.7, 0.2, 10, 'blue', [0, 4.6, 0]); for (const x of [-1, 1]) for (const z of [-1, 1]) t.box(0.15, 2, 0.15, 'steel', [x, 1, z]); t.box(2.4, 0.12, 2.4, 'steel', [0, 2, 0]); return t; }],
  ['city_rooftop_ac_unit', 'city-building', ['city', 'tokyo', 'rooftop', 'air-conditioner', 'outdoor-unit', 'prop'], ['platform', 'obstacle'], 'Air-conditioner outdoor unit — the classic Tokyo rooftop/back-alley step.', () =>
    k().box(1, 0.7, 0.4, 'white', [0, 0.35, 0]).cyl(0.26, 0.26, 0.04, 10, 'steelDark', [-0.15, 0.36, 0.21], [Math.PI / 2, 0, 0]).box(0.25, 0.5, 0.02, 'steel', [0.33, 0.35, 0.21]).box(1.05, 0.05, 0.45, 'concreteDark', [0, 0.02, 0])],
  ['city_billboard_frame', 'city-building', ['city', 'tokyo', 'billboard', 'sign', 'rooftop', 'neon'], ['climbable-surface', 'platform'], 'Rooftop billboard with lattice frame (blank face — add your own art).', () => {
    const t = k().box(10, 4, 0.3, 'white', [0, 6, 0]).box(9.4, 3.4, 0.05, 'glowAmber', [0, 6, 0.17]); for (const x of [-4, 0, 4]) t.box(0.25, 4, 0.25, 'steel', [x, 2, -0.6]).box(0.15, 4.4, 0.15, 'steel', [x, 2.1, -1.6], [deg(-15), 0, 0]); t.box(10, 0.15, 1, 'steelDark', [0, 3.9, 0.5]); return t; }],
  ['city_radio_tower', 'city-building', ['city', 'tokyo', 'tower', 'lattice', 'landmark', 'red-white'], ['climbable-surface', 'landmark'], 'Generic red-and-white lattice broadcast tower (80 m), climbable truss.', () => {
    const t = k(); const h = 80, levels = 10;
    for (let i = 0; i < levels; i++) { const y0 = i * h / levels, y1 = y0 + h / levels, w0 = 16 * (1 - i / levels) + 2, w1 = 16 * (1 - (i + 1) / levels) + 2, color = i % 2 ? 'white' : 'orange';
      for (const [sx, sz] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) { const a = new THREE.Vector3(sx * w0 / 2, y0, sz * w0 / 2), b = new THREE.Vector3(sx * w1 / 2, y1, sz * w1 / 2), len = a.distanceTo(b);
        const g = new THREE.CylinderGeometry(0.35, 0.35, len, 4); const mid = a.clone().add(b).multiplyScalar(0.5); const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), b.clone().sub(a).normalize());
        t.add(g, color, { p: mid.toArray(), r: new THREE.Euler().setFromQuaternion(q).toArray().slice(0, 3) }); }
      t.box(w1 + 0.6, 0.4, 0.4, color, [0, y1, w1 / 2]).box(w1 + 0.6, 0.4, 0.4, color, [0, y1, -w1 / 2]).box(0.4, 0.4, w1 + 0.6, color, [w1 / 2, y1, 0]).box(0.4, 0.4, w1 + 0.6, color, [-w1 / 2, y1, 0]); }
    t.box(7, 3, 7, 'white', [0, 31.5, 0]).cyl(0.3, 0.5, 12, 6, 'white', [0, 86, 0]); return t; }],
  ['city_elevated_highway', 'city-street', ['city', 'tokyo', 'highway', 'expressway', 'elevated', 'road', 'modular'], ['walkable-floor', 'platform', 'modular-kit'], '20 m elevated expressway deck (2 lanes, 10 m high) on a T-pier — tile along Z.', () => {
    const t = k().box(12, 1.2, 20, 'concrete', [0, 10, 0]).box(10.6, 0.05, 20, 'asphalt', [0, 10.63, 0]).box(0.5, 1.2, 20, 'concreteDark', [-5.75, 11.2, 0]).box(0.5, 1.2, 20, 'concreteDark', [5.75, 11.2, 0]);
    for (let z = -8; z <= 8; z += 4) t.box(0.15, 0.02, 2, 'white', [0, 10.67, z]); t.box(2.4, 9.4, 2.4, 'concrete', [0, 4.7, 0]).box(9, 1.6, 2.6, 'concrete', [0, 8.6, 0]).box(0.3, 3, 0.3, 'steel', [5.75, 13.3, 0]).box(1.4, 0.2, 0.3, 'steel', [5.1, 14.8, 0]).box(0.6, 0.1, 0.3, 'glowAmber', [4.5, 14.68, 0]); return t; }],
  ['city_highway_ramp', 'city-street', ['city', 'tokyo', 'highway', 'ramp', 'slope', 'road'], ['walkable-floor', 'platform'], '20 m sloped highway ramp rising 0→5 m.', () => {
    const t = k(); t.add(new THREE.BoxGeometry(12, 1, 20.6), 'concrete', { p: [0, 2.5, 0], r: [-Math.atan2(5, 20), 0, 0] }).add(new THREE.BoxGeometry(10.6, 0.05, 20.6), 'asphalt', { p: [0, 3.03, 0], r: [-Math.atan2(5, 20), 0, 0] }); t.box(2, 3, 2, 'concrete', [0, 1.5, 4]); return t; }],
  ['city_pedestrian_bridge', 'city-street', ['city', 'tokyo', 'footbridge', 'hodokyo', 'bridge', 'stairs'], ['walkable-floor', 'platform'], 'Pedestrian overpass (歩道橋) with stairs on both ends spanning a 16 m road.', () => {
    const t = k().box(2.5, 0.4, 16, 'blue', [0, 5.2, 0]).box(0.08, 1.1, 16, 'white', [-1.2, 5.95, 0]).box(0.08, 1.1, 16, 'white', [1.2, 5.95, 0]);
    for (const z of [-8, 8]) { t.box(0.5, 5, 0.5, 'blue', [-1, 2.5, z]).box(0.5, 5, 0.5, 'blue', [1, 2.5, z]); for (let i = 0; i < 16; i++) t.box(2.5, 0.2, 0.4, 'concrete', [0, 5 - i * 0.32, z + Math.sign(z) * (0.6 + i * 0.4)]); } return t; }],
  ['city_utility_pole', 'city-street', ['city', 'tokyo', 'utility-pole', 'denchu', 'wires', 'street'], ['climbable-surface', 'handhold'], 'Concrete utility pole with transformer and crossarms (12 m) — iconic Tokyo street climb.', () =>
    k().cyl(0.15, 0.22, 12, 8, 'concrete', [0, 6, 0]).box(2.2, 0.15, 0.15, 'steelDark', [0, 11.2, 0]).box(1.6, 0.15, 0.15, 'steelDark', [0, 10.2, 0]).cyl(0.35, 0.35, 1, 8, 'steel', [0.45, 8.5, 0]).box(0.4, 0.6, 0.15, 'yellow', [0, 2.5, 0.2]).cyl(0.04, 0.04, 0.3, 4, 'white', [-0.9, 11.4, 0]).cyl(0.04, 0.04, 0.3, 4, 'white', [0.9, 11.4, 0])
      .tube([[-0.9, 11.4, 0], [-0.9, 10.8, 5], [-0.9, 11.4, 10]], 0.03, 'cable', 8).tube([[0.9, 11.4, 0], [0.9, 10.8, 5], [0.9, 11.4, 10]], 0.03, 'cable', 8)],
  ['city_vending_machine', 'city-street', ['city', 'tokyo', 'vending-machine', 'jidohanbaiki', 'prop'], ['obstacle', 'platform'], 'Drink vending machine with lit display (unbranded).', () =>
    k().box(1, 1.8, 0.75, 'red', [0, 0.9, 0]).box(0.84, 0.9, 0.05, 'glowAmber', [0, 1.25, 0.38]).box(0.5, 0.18, 0.05, 'black', [0, 0.3, 0.38]).box(0.16, 0.3, 0.05, 'steel', [0.3, 0.75, 0.38])],
  ['city_traffic_light', 'city-street', ['city', 'tokyo', 'traffic-light', 'signal', 'street'], ['handhold', 'decoration'], 'Horizontal Japanese-style traffic signal on a cantilever mast.', () =>
    k().cyl(0.12, 0.15, 5.5, 8, 'steel', [0, 2.75, 0]).box(4, 0.12, 0.12, 'steel', [2, 5.3, 0]).box(1.6, 0.5, 0.35, 'steelDark', [3.2, 5.0, 0]).cyl(0.17, 0.17, 0.06, 8, 'glow', [2.7, 5.0, 0.2], [Math.PI / 2, 0, 0]).cyl(0.17, 0.17, 0.06, 8, 'yellow', [3.2, 5.0, 0.2], [Math.PI / 2, 0, 0]).cyl(0.17, 0.17, 0.06, 8, 'glowRed', [3.7, 5.0, 0.2], [Math.PI / 2, 0, 0])],
  ['city_street_lamp', 'city-street', ['city', 'tokyo', 'street-lamp', 'light', 'street'], ['handhold', 'decoration'], '7 m street lamp.', () =>
    k().cyl(0.1, 0.14, 7, 8, 'steel', [0, 3.5, 0]).box(1.2, 0.1, 0.1, 'steel', [0.6, 6.9, 0]).box(0.6, 0.15, 0.3, 'steelDark', [1.2, 6.85, 0]).box(0.5, 0.05, 0.25, 'glowAmber', [1.2, 6.76, 0])],
  ['city_crosswalk_road', 'city-street', ['city', 'tokyo', 'road', 'crosswalk', 'zebra', 'tile'], ['walkable-floor', 'modular-kit'], '10×10 m road tile with zebra crossing.', () => {
    const t = k().box(10, 0.1, 10, 'asphalt', [0, 0.05, 0]); for (let x = -4; x <= 4; x += 1) t.box(0.5, 0.02, 3, 'white', [x, 0.11, 0]); t.box(0.15, 0.02, 3, 'white', [0, 0.11, 3.5]).box(0.15, 0.02, 3, 'white', [0, 0.11, -3.5]); return t; }],
  ['city_sidewalk_barrier', 'city-street', ['city', 'tokyo', 'guardrail', 'barrier', 'street'], ['obstacle', 'handhold'], '4 m sidewalk guard rail.', () => {
    const t = k(); for (const x of [-1.9, 0, 1.9]) t.box(0.08, 0.8, 0.08, 'white', [x, 0.4, 0]); t.box(4, 0.1, 0.06, 'white', [0, 0.75, 0]).box(4, 0.1, 0.06, 'white', [0, 0.4, 0]); return t; }],
  ['city_rubble_pile', 'city-street', ['city', 'rubble', 'debris', 'destruction', 'concrete'], ['obstacle', 'platform'], 'Concrete debris left in the robot\'s footsteps.', () =>
    k().box(2, 1, 1.6, 'concrete', [0, 0.4, 0], [0.2, 0.4, 0.1]).box(1.4, 0.8, 1.2, 'concreteDark', [1.2, 0.3, 0.6], [0.3, -0.5, 0.2]).box(1, 0.6, 1, 'concrete', [-1.1, 0.25, -0.5], [-0.2, 0.9, 0.3]).box(2.6, 0.1, 0.1, 'steelDark', [0.2, 0.9, 0.2], [0.1, 0.7, 0.4])],

  // ---------- Gameplay ----------
  ['gameplay_checkpoint', 'gameplay', ['checkpoint', 'save', 'beacon', 'glow'], ['goal'], 'Checkpoint pad with light pillar.', () =>
    k().cyl(1, 1.1, 0.25, 10, 'steelDark', [0, 0.125, 0]).cyl(0.8, 0.8, 0.05, 10, 'glow', [0, 0.27, 0]).cyl(0.12, 0.12, 2.2, 6, 'steel', [0, 1.35, 0]).ball(0.22, 'glow', [0, 2.6, 0], 0)],
  ['gameplay_bolt_collectible', 'gameplay', ['collectible', 'bolt', 'nut', 'pickup', 'score'], ['collectible'], 'Hex-nut collectible (0.5 m) — spin it in-game.', () =>
    k().cyl(0.25, 0.25, 0.14, 6, 'yellow', [0, 0.25, 0], [Math.PI / 2, 0, 0]).cyl(0.1, 0.1, 0.16, 8, 'steelDark', [0, 0.25, 0], [Math.PI / 2, 0, 0])],
  ['gameplay_energy_cell', 'gameplay', ['collectible', 'energy', 'battery', 'stamina', 'pickup'], ['collectible'], 'Stamina / grip energy cell pickup.', () =>
    k().cyl(0.18, 0.18, 0.5, 8, 'glow', [0, 0.35, 0]).cyl(0.2, 0.2, 0.1, 8, 'steelDark', [0, 0.1, 0]).cyl(0.2, 0.2, 0.1, 8, 'steelDark', [0, 0.6, 0]).cyl(0.06, 0.06, 0.08, 6, 'steel', [0, 0.69, 0])],
  ['gameplay_shutdown_switch', 'gameplay', ['goal', 'switch', 'lever', 'shutdown', 'core'], ['goal'], 'Emergency shutdown lever pedestal for the robot core.', () =>
    k().box(1.2, 1.1, 0.8, 'steelDark', [0, 0.55, 0]).box(1.25, 0.12, 0.85, 'yellow', [0, 1.1, 0]).box(0.12, 0.9, 0.12, 'steel', [0, 1.5, 0], [deg(25), 0, 0]).ball(0.14, 'red', [0, 1.92, 0.2], 0).box(0.8, 0.3, 0.05, 'glowRed', [0, 0.8, 0.41])]
];

export async function generate() {
  await fs.mkdir(outDir, { recursive: true });
  const exporter = new GLTFExporter();
  for (const [name, , , , , build] of originals) {
    const scene = new THREE.Scene(); scene.add(build().build(name));
    const glb = await exporter.parseAsync(scene, { binary: true });
    await fs.writeFile(path.join(outDir, name + '.glb'), Buffer.from(glb));
  }
  return originals.length;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) console.log(`Generated ${await generate()} original GLBs in ${path.relative(root, outDir)}`);
