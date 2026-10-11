// GIANT CLIMB asset collection: pinned sources and the curated selection.
// Every external file is fetched from an exact commit / package version and its
// license is recorded here. Assets whose license could not be verified are listed
// in `excluded` with the reason and are never imported.

export const sources = {
  'kenney-space-kit': {
    kind: 'npm',
    name: 'Kenney Space Kit 2.0',
    package: '@anabis/kenney-space-kit-mirror',
    version: '2.0.0',
    tarball: 'https://registry.npmjs.org/@anabis/kenney-space-kit-mirror/-/kenney-space-kit-mirror-2.0.0.tgz',
    integrity: 'sha512-mpXkBM9xtv8KlBjBolyYEYpsx8G3EcNyggZp4pQZ/+qFmKgG0256pbeXoiVB2f1iN6vVTfSHJhFxHEASJVVuUQ==',
    root: 'package/assets/Models/GLTF format',
    licenseFile: 'package/assets/License.txt',
    license: 'CC0-1.0',
    author: 'Kenney (www.kenney.nl)',
    homepage: 'https://kenney.nl/assets/space-kit',
    sourceUrl: 'https://www.npmjs.com/package/@anabis/kenney-space-kit-mirror/v/2.0.0',
    note: 'Unofficial npm mirror; ships Kenney\'s original License.txt (CC0 1.0). Only model files are used; the package script is never executed.'
  },
  'kenney-city-builder': {
    kind: 'git', name: 'Kenney Starter Kit City Builder', repo: 'https://github.com/KenneyNL/Starter-Kit-City-Builder',
    commit: '4535092b740b378b700efd9df9e27a631815b84a', root: 'models', licenseFile: 'README.md',
    license: 'CC0-1.0', author: 'Kenney (www.kenney.nl)', homepage: 'https://github.com/KenneyNL/Starter-Kit-City-Builder',
    note: 'README: "Sprites and 3D Models (CC0 licensed)"; project code is MIT and is not imported.'
  },
  'kenney-platformer': {
    kind: 'git', name: 'Kenney Starter Kit 3D Platformer', repo: 'https://github.com/KenneyNL/Starter-Kit-3D-Platformer',
    commit: '3fa8a04b1c01ab23db43123d4ce814a34c3fc7f0', root: 'models', licenseFile: 'README.md',
    license: 'CC0-1.0', author: 'Kenney (www.kenney.nl)', homepage: 'https://github.com/KenneyNL/Starter-Kit-3D-Platformer',
    note: 'README: "Sprites and 3D Models (CC0 licensed)"; project code is MIT and is not imported.'
  },
  'kenney-fps': {
    kind: 'git', name: 'Kenney Starter Kit FPS', repo: 'https://github.com/KenneyNL/Starter-Kit-FPS',
    commit: '185fd2326d74a5cf858cffc616f87cf9696f9cc0', root: 'models', licenseFile: 'README.md',
    license: 'CC0-1.0', author: 'Kenney (www.kenney.nl)', homepage: 'https://github.com/KenneyNL/Starter-Kit-FPS',
    note: 'README: "Sprites and 3D Models (CC0 licensed)"; project code is MIT and is not imported.'
  },
  'kenney-racing': {
    kind: 'git', name: 'Kenney Starter Kit Racing', repo: 'https://github.com/KenneyNL/Starter-Kit-Racing',
    commit: '2f2e5f2646dda89cb21d4e8539bab60c6e955dc8', root: 'models', licenseFile: 'README.md',
    license: 'CC0-1.0', author: 'Kenney (www.kenney.nl)', homepage: 'https://github.com/KenneyNL/Starter-Kit-Racing',
    note: 'README: "3D Models & sounds (CC0 licensed)"; project code is MIT and is not imported.'
  },
  'kenney-mini-arena': {
    kind: 'git', name: 'Kenney Mini Arena (Starter Kit Basic Scene)', repo: 'https://github.com/KenneyNL/Starter-Kit-Basic-Scene',
    commit: 'a6927e66ff8dd8e173660ce4825abe773c65f683', root: 'sample/Mini Arena/Models/GLB format', licenseFile: 'README.md',
    license: 'CC0-1.0', author: 'Kenney (www.kenney.nl)', homepage: 'https://github.com/KenneyNL/Starter-Kit-Basic-Scene',
    note: 'README: "comes with the (CC0 licensed) Mini Arena pack".'
  },
  'pmndrs-market': {
    kind: 'git', name: 'pmndrs market-assets', repo: 'https://github.com/pmndrs/market-assets',
    commit: 'c9cfa0236a012093edd5affe200808752375bd90', root: 'files/models', sparse: true,
    license: 'CC0-1.0', author: 'Kenney (www.kenney.nl)', homepage: 'https://github.com/pmndrs/market-assets',
    note: 'Only items whose info.json lists creator "kenney" and license id 1 (= CC0 in pmndrs/market src/helpers/constants/licenses.js). Kenney publishes these kits as CC0.'
  },
  'threejs-r180': {
    kind: 'raw', name: 'three.js r180 example models', repo: 'https://github.com/mrdoob/three.js',
    commit: '0af9729d0c143a86a1d725d6e2c3ad83301f3f34', baseUrl: 'https://raw.githubusercontent.com/mrdoob/three.js/0af9729d0c143a86a1d725d6e2c3ad83301f3f34/examples/models/gltf',
    license: 'CC0-1.0', author: 'Tomás Laulhé (Quaternius); modifications by Don McCurdy', homepage: 'https://github.com/mrdoob/three.js/tree/r180/examples/models/gltf/RobotExpressive',
    note: 'RobotExpressive/README.md: "Model by Tomás Laulhé ... CC0 1.0".'
  },
  'nexus-original': {
    kind: 'generated', name: 'NEXUS original (GIANT CLIMB)', script: 'scripts/giant-climb/generate-originals.mjs',
    license: 'CC0-1.0', author: 'NEXUS', homepage: 'https://github.com/Yuji5124/nexus/blob/main/scripts/giant-climb/generate-originals.mjs',
    note: 'Created procedurally for GIANT CLIMB in this repository and dedicated to the public domain (CC0 1.0).'
  }
};

// Short helper: e(source, file, category, tags, roles, extra)
const e = (source, file, category, tags, roles, extra = {}) => ({ source, file, category, tags, roles, ...extra });

const CORRIDOR = ['robot', 'interior', 'corridor', 'scifi', 'modular'];
const PIPE = ['robot', 'interior', 'pipe', 'industrial', 'modular'];
const PLATFORM = ['platform', 'scifi', 'modular', 'ledge'];

export const assets = [
  // --- Space Kit: robot interior corridors (modular, 1 tile) ---
  ...['corridor', 'corridor_corner', 'corridor_cornerRound', 'corridor_cornerRoundWindow', 'corridor_cross', 'corridor_detailed', 'corridor_end', 'corridor_open', 'corridor_roof', 'corridor_split', 'corridor_wall', 'corridor_wallCorner', 'corridor_window', 'corridor_windowClosed']
    .map(n => e('kenney-space-kit', `${n}.glb`, 'robot-interior', CORRIDOR, ['walkable-floor', 'modular-kit'])),
  // --- Space Kit: pipes, conduits (robot veins / climbable pipes) ---
  ...['pipe_corner', 'pipe_cornerDiagonal', 'pipe_cornerRound', 'pipe_cornerRoundLarge', 'pipe_cross', 'pipe_end', 'pipe_entrance', 'pipe_open', 'pipe_rampLarge', 'pipe_rampSmall', 'pipe_ring', 'pipe_ringHigh', 'pipe_ringHighEnd', 'pipe_ringSupport', 'pipe_split', 'pipe_straight', 'pipe_supportHigh', 'pipe_supportLow']
    .map(n => e('kenney-space-kit', `${n}.glb`, 'robot-interior', PIPE, ['climbable-surface', 'modular-kit'])),
  // --- Space Kit: platforms / catwalk floors ---
  ...['platform_center', 'platform_corner', 'platform_cornerOpen', 'platform_cornerRound', 'platform_end', 'platform_high', 'platform_large', 'platform_long', 'platform_low', 'platform_side', 'platform_small', 'platform_smallDiagonal', 'platform_straight']
    .map(n => e('kenney-space-kit', `${n}.glb`, 'platform', PLATFORM, ['platform', 'modular-kit'])),
  // --- Space Kit: structure, scaffolding, stairs, rails ---
  ...['structure', 'structure_closed', 'structure_detailed', 'structure_diagonal', 'supports_high', 'supports_low']
    .map(n => e('kenney-space-kit', `${n}.glb`, 'robot-interior', ['robot', 'frame', 'scaffold', 'lattice', 'industrial'], ['climbable-surface', 'modular-kit'])),
  ...['stairs', 'stairs_corner', 'stairs_short']
    .map(n => e('kenney-space-kit', `${n}.glb`, 'robot-interior', ['stairs', 'interior', 'scifi', 'modular'], ['walkable-floor', 'modular-kit'])),
  ...['rail', 'rail_corner', 'rail_end', 'rail_middle']
    .map(n => e('kenney-space-kit', `${n}.glb`, 'robot-interior', ['railing', 'handrail', 'catwalk', 'scifi'], ['handhold', 'modular-kit'])),
  // --- Space Kit: machinery ---
  ...['machine_barrel', 'machine_barrelLarge', 'machine_generator', 'machine_generatorLarge', 'machine_wireless', 'machine_wirelessCable']
    .map(n => e('kenney-space-kit', `${n}.glb`, 'robot-interior', ['robot', 'machine', 'generator', 'industrial', 'scifi'], ['obstacle', 'decoration'])),
  ...['desk_computer', 'desk_computerCorner', 'desk_computerScreen']
    .map(n => e('kenney-space-kit', `${n}.glb`, 'robot-interior', ['robot', 'control-room', 'computer', 'console', 'core'], ['decoration'])),
  ...['barrel', 'barrels', 'barrels_rail']
    .map(n => e('kenney-space-kit', `${n}.glb`, 'prop', ['barrel', 'industrial', 'scifi'], ['obstacle', 'decoration'])),
  // --- Space Kit: exterior hardware usable on the robot body ---
  ...['hangar_largeA', 'hangar_roundA', 'hangar_roundGlass', 'hangar_smallA']
    .map(n => e('kenney-space-kit', `${n}.glb`, 'robot-exterior', ['robot', 'armor', 'dome', 'hangar', 'scifi'], ['climbable-surface', 'platform'])),
  ...['gate_complex', 'gate_simple']
    .map(n => e('kenney-space-kit', `${n}.glb`, 'robot-interior', ['robot', 'gate', 'door', 'entrance', 'scifi'], ['landmark'])),
  ...['satelliteDish', 'satelliteDish_detailed', 'satelliteDish_large']
    .map(n => e('kenney-space-kit', `${n}.glb`, 'robot-exterior', ['robot', 'antenna', 'sensor', 'dish', 'rooftop'], ['decoration', 'landmark'])),
  ...['chimney', 'chimney_detailed']
    .map(n => e('kenney-space-kit', `${n}.glb`, 'robot-exterior', ['robot', 'exhaust', 'stack', 'industrial'], ['obstacle', 'hazard'])),
  ...['rocket_baseA', 'rocket_fuelA', 'rocket_finsA', 'rocket_sidesA', 'rocket_topA']
    .map(n => e('kenney-space-kit', `${n}.glb`, 'robot-exterior', ['robot', 'thruster', 'booster', 'modular', 'scifi'], ['modular-kit', 'climbable-surface'])),
  ...['turret_single', 'turret_double']
    .map(n => e('kenney-space-kit', `${n}.glb`, 'robot-exterior', ['robot', 'turret', 'defense', 'enemy'], ['hazard', 'enemy'])),
  // --- Space Kit: monorail (Tokyo elevated transit) ---
  ...['monorail_trackStraight', 'monorail_trackCornerLarge', 'monorail_trackCornerSmall', 'monorail_trackSlope', 'monorail_trackSupport', 'monorail_trackSupportCorner']
    .map(n => e('kenney-space-kit', `${n}.glb`, 'city-street', ['city', 'tokyo', 'monorail', 'track', 'elevated', 'modular'], ['platform', 'modular-kit'])),
  ...['monorail_trainFront', 'monorail_trainPassenger', 'monorail_trainEnd']
    .map(n => e('kenney-space-kit', `${n}.glb`, 'vehicle', ['city', 'tokyo', 'monorail', 'train', 'vehicle'], ['vehicle-prop', 'platform'])),

  // --- Kenney City Builder: city blocks and roads ---
  ...['building-small-a', 'building-small-b', 'building-small-c', 'building-small-d', 'building-garage']
    .map(n => e('kenney-city-builder', `${n}.glb`, 'city-building', ['city', 'building', 'tile', 'lowpoly'], ['climbable-surface', 'background'])),
  ...['road-straight', 'road-straight-lightposts', 'road-corner', 'road-intersection', 'road-split', 'pavement', 'pavement-fountain']
    .map(n => e('kenney-city-builder', `${n}.glb`, 'city-street', ['city', 'road', 'street', 'tile', 'modular'], ['walkable-floor', 'modular-kit'])),
  ...['grass', 'grass-trees', 'grass-trees-tall']
    .map(n => e('kenney-city-builder', `${n}.glb`, 'city-street', ['city', 'park', 'tree', 'tile'], ['walkable-floor', 'background'])),

  // --- Kenney 3D Platformer: gameplay building blocks ---
  ...['platform', 'platform-medium', 'platform-large', 'platform-grass-large-round']
    .map(n => e('kenney-platformer', `${n}.glb`, 'platform', ['platform', 'platformer', 'lowpoly'], ['platform'], { name: `Platformer ${n}` })),
  e('kenney-platformer', 'platform-falling.glb', 'gameplay', ['platform', 'falling', 'trap'], ['platform', 'hazard']),
  e('kenney-platformer', 'brick.glb', 'gameplay', ['brick', 'block', 'breakable'], ['obstacle']),
  e('kenney-platformer', 'block-coin.glb', 'gameplay', ['block', 'coin', 'item'], ['collectible']),
  e('kenney-platformer', 'coin.glb', 'gameplay', ['coin', 'collectible', 'pickup'], ['collectible']),
  e('kenney-platformer', 'flag.glb', 'gameplay', ['flag', 'checkpoint', 'goal'], ['goal']),
  e('kenney-platformer', 'cloud.glb', 'environment', ['cloud', 'sky', 'altitude'], ['background']),
  e('kenney-platformer', 'character.glb', 'character', ['character', 'player', 'hero', 'animated', 'placeholder'], ['character']),

  // --- Kenney FPS ---
  e('kenney-fps', 'enemy-flying.glb', 'character', ['drone', 'enemy', 'flying', 'robot'], ['enemy', 'hazard']),
  e('kenney-fps', 'wall-high.glb', 'platform', ['wall', 'block', 'modular'], ['climbable-surface', 'obstacle']),
  e('kenney-fps', 'wall-low.glb', 'platform', ['wall', 'block', 'low', 'modular'], ['obstacle', 'platform']),
  e('kenney-fps', 'platform-large-grass.glb', 'platform', ['platform', 'grass'], ['platform']),

  // --- Kenney Racing vehicles ---
  ...['vehicle-truck-red', 'vehicle-truck-yellow', 'vehicle-truck-green', 'vehicle-motorcycle']
    .map(n => e('kenney-racing', `${n}.glb`, 'vehicle', ['vehicle', 'truck', 'street', 'city'], ['vehicle-prop', 'platform'])),

  // --- Kenney Mini Arena: generic blocks / rubble ---
  ...['block', 'stairs', 'column', 'column-damaged', 'floor-detail']
    .map(n => e('kenney-mini-arena', `${n}.glb`, 'platform', ['block', 'ruin', 'rubble', 'stone', 'modular'], ['platform', 'obstacle'], { name: `Arena ${n}` })),

  // --- Kenney Car Kit / characters via pmndrs market (glTF -> GLB) ---
  ...['ambulance', 'delivery-truck', 'firetruck', 'garbage-truck', 'hatchback', 'police-car', 'sedan', 'sports-sedan', 'suv', 'taxi', 'truck', 'truck-flat', 'van']
    .map(n => e('pmndrs-market', `${n}/model.gltf`, 'vehicle', ['vehicle', 'car', 'street', 'city', 'traffic'], ['vehicle-prop', 'platform'], { slug: n })),
  ...['male', 'survivor-male', 'survivor-female', 'skater-male', 'skater-female', 'cyborg-female']
    .map(n => e('pmndrs-market', `${n}/model.gltf`, 'character', ['character', 'npc', 'civilian', 'rigged'], ['character'], { slug: n })),
  ...['house-4', 'house-5', 'house-7']
    .map(n => e('pmndrs-market', `${n}/model.gltf`, 'city-building', ['city', 'house', 'residential', 'building'], ['climbable-surface', 'background'], { slug: n })),

  // --- three.js r180: rigged robot (placeholder for the giant robot / enemy) ---
  e('threejs-r180', 'RobotExpressive/RobotExpressive.glb', 'character', ['robot', 'mecha', 'rigged', 'animated', 'giant', 'placeholder'], ['character', 'enemy'], {
    name: 'Robot Expressive', notes: 'Rigged and animated robot with 14 clips. Scale up as a stand-in for the giant robot during prototyping.'
  })
];

export const excluded = [
  { item: 'pmndrs-market: helicopter, bike, headphones, mechanical keyboards and other Blend Swap uploads', reason: 'License stated only by the aggregator; the original Blend Swap pages could not be reached to verify.' },
  { item: 'pmndrs-market: creativetrio / saravieira items (bridge, wind turbine, library, sci-fi crate, ...)', reason: 'CC0 stated only by the aggregator metadata with no upstream license file; excluded to stay conservative.' },
  { item: 'pmndrs-market: food models (202), pirate kit, castle tower', reason: 'Off-theme for GIANT CLIMB (Tokyo / giant robot).' },
  { item: 'Kenney Space Kit: aliens, astronauts, spacecraft, rovers, weapons, meteors, craters, lunar terrain, crystals', reason: 'Off-theme (space setting) for a Tokyo giant-robot climb.' },
  { item: 'Kenney Starter Kits: weapons, particles, medieval props (banner, statue, trophy, swords), race-track pieces', reason: 'Off-theme or not useful as level geometry.' },
  { item: 'kenney.nl, quaternius.com, poly.pizza, polyhaven.com, opengameart.org direct downloads', reason: 'Not reachable from the build environment (egress policy); only GitHub/npm-hosted copies with license files were used.' },
  { item: 'three.js Xbot / Soldier / Michelle', reason: 'Mixamo-derived; redistribution terms are not CC0.' }
];
