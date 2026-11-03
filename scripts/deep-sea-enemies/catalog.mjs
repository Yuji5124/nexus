// DEEP-SEA ENEMIES の一覧。形とアニメは build_enemies.py にある。
// move: fly=浮遊 / walk=歩行 / swim=泳ぎ / static=据え置き。tier: swarm=群れの雑魚 / elite=強敵。hint は設計の目安 (仕様ではない)。
export const catalog = [
  { id: 'enemy_scout_drone', name: 'Scout Drone', move: 'fly', tier: 'swarm', tags: ['drone', 'flying', 'scout', 'rotor', 'robot'],
    description: 'Fast quad-rotor scout: flat armoured body, single red eye, glowing underside lamp. Attack = dive-bomb.', hint: 'Flies in groups; low HP; reveals the player to other enemies.' },
  { id: 'enemy_crawler_bot', name: 'Crawler Bot', move: 'walk', tier: 'swarm', tags: ['spider', 'crawler', 'six-legged', 'robot'],
    description: 'Six-legged crawler with a boxy hull, two eyes and spike fangs. Attack = front legs rear up and stab.', hint: 'Charges in a straight line; medium HP.' },
  { id: 'enemy_gunner_turret', name: 'Gunner Turret', move: 'static', tier: 'swarm', tags: ['turret', 'tripod', 'twin-gun', 'robot'],
    description: 'Tripod turret with a rotating head and twin barrels. Idle = scanning sweep; Attack = barrel recoil.', hint: 'Never moves; ranged fire; place on high ground.' },
  { id: 'enemy_bulwark_walker', name: 'Bulwark Walker', move: 'walk', tier: 'elite', tags: ['heavy', 'shield', 'walker', 'armoured', 'robot'],
    description: 'Four-legged armoured walker with a huge frontal shield plate carrying an orange ring. Attack = shield slam.', hint: 'High HP, slow; weak point is the rear glow.' },
  { id: 'enemy_jelly_drone', name: 'Jelly Drone', move: 'fly', tier: 'swarm', tags: ['jellyfish', 'drone', 'translucent', 'tentacles', 'robot'],
    description: 'Translucent bell with a glowing core and eight chained cable tentacles that sway. Attack = bell flares and tentacles whip.', hint: 'Drifts slowly; contact shock; bell uses alpha blending.' },
  { id: 'enemy_eel_bot', name: 'Eel Bot', move: 'swim', tier: 'swarm', tags: ['eel', 'serpent', 'segmented', 'robot'],
    description: 'Eight-segment mechanical eel with a hinged jaw and a glowing tail tip. Idle/Swim = body wave; Attack = lunge with open jaw.', hint: 'Fast swimmer; strikes from the side.' },
  { id: 'enemy_urchin_mine', name: 'Urchin Mine', move: 'static', tier: 'swarm', tags: ['mine', 'urchin', 'spikes', 'explosive'],
    description: 'Spiked sphere mine with a pulsing core and eighteen orange spikes. Attack = spikes extend and spin.', hint: 'Contact or proximity trigger; breakable; area damage.' },
  { id: 'enemy_angler_lurebot', name: 'Anglerfish Lure Bot', move: 'swim', tier: 'elite', tags: ['anglerfish', 'lure', 'jaw', 'ambush', 'robot'],
    description: 'Armoured anglerfish with a swaying glowing lure, hinged toothed jaw, fins and tail. Attack = jaw snap.', hint: 'Ambush predator: the lure draws the player in.' },
  { id: 'enemy_squid_lancer', name: 'Squid Lancer', move: 'swim', tier: 'elite', tags: ['squid', 'lancer', 'tentacles', 'spear', 'robot'],
    description: 'Armoured squid with eight waving arms and two long spear tentacles tipped in orange. Attack = spear thrust.', hint: 'Keeps distance; telegraphed thrust.' },
  { id: 'enemy_ruin_sentinel', name: 'Ruin Sentinel', move: 'walk', tier: 'elite', tags: ['golem', 'stone', 'sentinel', 'ancient', 'guardian'],
    description: 'Five-metre stone golem with glowing runes on chest, arms and legs and a red eye slit. Attack = overhead double-fist slam.', hint: 'Ruin guardian; slow, heavy hits; runes can mark weak points.' },
  { id: 'enemy_stone_crab_guardian', name: 'Stone Crab Guardian', move: 'walk', tier: 'elite', tags: ['crab', 'stone', 'guardian', 'claws', 'ancient'],
    description: 'Living version of the crab guardian statue: stone shell with rune ring, two big claws, six legs, eye stalks. Attack = claw snap.', hint: 'Pairs with the deep-sea-ruins crab statue; ambush when the player enters a ruin.' },
  { id: 'enemy_hammerhead_sweeper', name: 'Hammerhead Sweeper', move: 'swim', tier: 'elite', tags: ['shark', 'hammerhead', 'sweeper', 'robot'],
    description: 'Mechanical hammerhead shark with a glowing wide head, six-segment tail and side fins. Attack = head sweep.', hint: 'Patrols open water; sweeping head hit has a wide arc.' }
];
