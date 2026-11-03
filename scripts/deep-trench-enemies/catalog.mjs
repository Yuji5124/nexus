// DEEP-TRENCH ENEMIES の一覧 (深度3500m以降)。形とアニメは build_trench_enemies.py にある。
// zone: luminous-deep=発光深海 3,500〜8,000m / sunken-city=沈没都市 8,000〜10,000m / abyss=深淵領域 10,000〜12,000m (どれも出現深度の提案で、仕様ではない)。
// move: fly=浮遊 / walk=歩行 / swim=泳ぎ / static=据え置き。tier: swarm=群れの雑魚 / elite=強敵。ボスは含めない。
export const ZONES = {
  'luminous-deep': { label: 'luminous deep', range: '3,500-8,000 m' },
  'sunken-city': { label: 'sunken city', range: '8,000-10,000 m' },
  abyss: { label: 'abyss', range: '10,000-12,000 m' }
};
export const catalog = [
  { id: 'enemy_lantern_swarm', name: 'Lantern Swarm Drone', zone: 'luminous-deep', move: 'fly', tier: 'swarm', tags: ['drone', 'lantern', 'halo', 'flying', 'swarm'],
    description: 'Small glowing orb drone with a spinning amber halo ring, a red eye and an underside lamp. Attack = dash with the halo flaring.', hint: 'Flies in large groups; low HP; the light draws other enemies.' },
  { id: 'enemy_viperfish_hunter', name: 'Viperfish Hunter', zone: 'luminous-deep', move: 'swim', tier: 'elite', tags: ['viperfish', 'fangs', 'lure', 'fish', 'predator'],
    description: 'Armoured viperfish with a skull-like head, long fangs, a hinged jaw, photophore lights along the flanks and a dorsal lure. Attack = open-jaw lunge.', hint: 'Ambush predator; the dorsal lure marks its head.' },
  { id: 'enemy_siphonophore_chain', name: 'Siphonophore Chain', zone: 'luminous-deep', move: 'static', tier: 'swarm', tags: ['siphonophore', 'colony', 'bells', 'translucent', 'hazard'],
    description: 'A tall chain of seven glowing glass bells with dangling amber-tipped tentacles. Idle = slow sway; Attack = bells pulse and lash.', hint: 'Drifting hazard column; contact shock; bells use alpha blending.' },
  { id: 'enemy_isopod_roller', name: 'Isopod Roller', zone: 'luminous-deep', move: 'walk', tier: 'swarm', tags: ['isopod', 'armoured', 'roller', 'crawler'],
    description: 'Giant isopod with six overlapping armour plates, twelve legs and long antennae. Attack = curls up and lunges forward.', hint: 'Charges along the seabed; armour plates take reduced damage.' },
  { id: 'enemy_tubeworm_spitter', name: 'Tubeworm Spitter', zone: 'luminous-deep', move: 'static', tier: 'swarm', tags: ['tubeworm', 'vent', 'plume', 'turret'],
    description: 'Cluster of seven white tubes on a vent mound, each tipped with orange plumes and a glow bud. Attack = tubes lengthen and the plumes flare.', hint: 'Fixed ranged hazard; place near vents.' },
  { id: 'enemy_archive_warden', name: 'Archive Warden', zone: 'sunken-city', move: 'fly', tier: 'elite', tags: ['warden', 'gyroscope', 'rings', 'stone', 'guardian'],
    description: 'A stone orb with an amber eye slit, three counter-rotating glyph rings and two hanging stabilisers. Attack = the rings align and the core flares.', hint: 'Guards record sites; the rings are the weak point. Its makers are left unexplained.' },
  { id: 'enemy_obelisk_stalker', name: 'Obelisk Stalker', zone: 'sunken-city', move: 'walk', tier: 'elite', tags: ['obelisk', 'tripod', 'stone', 'walker', 'crown'],
    description: 'Seven-metre stone obelisk on three jointed legs, with a glowing vertical slit and a floating glyph crown. Attack = leans forward as the crown spins.', hint: 'Slow, tall and heavy; the legs are the target.' },
  { id: 'enemy_lamplighter', name: 'Lamplighter', zone: 'sunken-city', move: 'fly', tier: 'swarm', tags: ['lantern', 'lure', 'floating', 'support'],
    description: 'Slender floating figure of stone and metal with a long arm holding a swinging amber lantern and six hanging strips. Attack = raises and swings the lantern.', hint: 'Support enemy that lights up the player for others.' },
  { id: 'enemy_echo_manta', name: 'Echo Manta', zone: 'abyss', move: 'swim', tier: 'elite', tags: ['manta', 'echo', 'afterimage', 'translucent', 'phenomenon'],
    description: 'Dark manta with translucent violet wings, a glowing dorsal seam and two ghost copies trailing behind. Attack = dash while the copies split to the sides.', hint: 'Visual for the lingering-presence phenomenon: the copies show where it was a moment ago.' },
  { id: 'enemy_void_anemone', name: 'Void Anemone', zone: 'abyss', move: 'static', tier: 'swarm', tags: ['anemone', 'tentacles', 'ring', 'hazard', 'phenomenon'],
    description: 'Stone-based anemone with a translucent bell, a violet core, twelve three-joint tentacles and a floating glyph ring. Attack = tentacles whip outward.', hint: 'Area hazard; tentacle tips glow violet.' }
];
