# NEXUS

NEXUS is a GitHub-hosted personal 3D asset library for AI-assisted game development.

GitHub NEXUS → Codex / Claude Code → Three.js game.

GitHub is the source of truth. Open the online Library to search metadata, preview GLB/glTF, and copy reusable URLs. No Node server is needed for browsing.

- Library: https://yuji5124.github.io/nexus/
- Index: https://yuji5124.github.io/nexus/data/assets.json
- Raw index (works independently of Pages): https://raw.githubusercontent.com/Yuji5124/nexus/main/data/assets.json

## Publish

In GitHub Settings → Pages, select **GitHub Actions** as the source. The included workflow scans the repository, commits updated metadata, and deploys the static artifact on pushes to main. The URLs above are the configured destinations; check the deployment result before assuming Pages is online.

## Add assets

Add files such as `assets/nature/tree/tree_001.glb` and push to GitHub. GLB is preferred. glTF, FBX and OBJ may be stored; FBX/OBJ require conversion for the browser viewer. glTF dependencies must be committed next to the model.

Run `npm run scan` to generate `data/assets.json`. Edit the record's name, tags, license, author, source, sourceUrl, notes and recommendedFor, then commit both assets and metadata. Later scans preserve these fields. Unknown licenses remain UNKNOWN. Missing thumbnails remain empty; the detailed viewer loads the real model. GLB accessor bounds are geometry bounds and may not reflect transformed scene dimensions.

## GIANT CLIMB collection

215 CC0 GLB models for the GIANT CLIMB climbing game (giant robot exterior and interior, Tokyo streets and buildings, vehicles, characters, gameplay objects) live in `assets/giant-climb/` with thumbnails in `thumbnails/giant-climb/`. Each record has `collection: "giant-climb"`, `gameRoles`, `climbable`, `units.metresPerUnit` and a commit-pinned `sourceUrl`. The pipeline (`npm run giant-climb`), source catalog and license evidence are documented in [giant-climb/README.md](giant-climb/README.md) and [giant-climb/REPORT.md](giant-climb/REPORT.md).

## RANVORA ver2 collection

20 GLB models from the owner's own game [RANVORA ver2](https://github.com/Yuji5124/RANVORA-ver2) (commit `dd2657b`) live in `assets/ranvora-ver2/` with thumbnails in `thumbnails/ranvora-ver2/`: the two rigged heroes (33 bones, 7 shared clips), 15 procedural nature props (68 variants, one root child per variant), the furnished log cabin, and the slime enemy and its gel drop. Records have `collection: "ranvora-ver2"`; licence is UNKNOWN until the owner declares one. Rebuild with `npm run ranvora-ver2`; details in [ranvora-ver2/README.md](ranvora-ver2/README.md).
## LOWPOLY TREES collection

10 CC0 low-poly trees from GitHub live in `assets/lowpoly-trees/` with thumbnails in `thumbnails/lowpoly-trees/`: five from KayKit's official repositories (pine, round fir, orange and yellow autumn pines, dead tree) and five from Kenney (palm via pmndrs/market-assets; oak, autumn oak, branching tree and plateau tree from Nature Kit 2.1, verified byte-identical across three projects that bundle it). 50–490 triangles each. Records have `collection: "lowpoly-trees"` and `units.suggestedScale` for realistic heights. Rebuild with `npm run lowpoly-trees`; sources and the material fixes are in [lowpoly-trees/README.md](lowpoly-trees/README.md).
## LEAFCARD TREES collection

Five lightweight original trees built the game-foliage way: a low-poly trunk plus crossed alpha-masked leaf cards (the "double billboard" technique used by EZ-Tree), with every texture painted by the script. 144–388 triangles and 87–134 KB each, two materials. Files in `assets/leafcard-trees/`, records with `collection: "leafcard-trees"`. Rebuild or tweak with `npm run leafcard-trees`; details in [leafcard-trees/README.md](leafcard-trees/README.md).

## DEEP-SEA RUINS collection

25 original low-poly ancient-ruin models for deep-sea games live in `assets/deep-sea-ruins/` with thumbnails in `thumbnails/deep-sea-ruins/`: pillars (intact, broken, fallen), arch gates, walls, stairs, altar, obelisk, crab guardian statue, fountain, lantern stele, floor tiles and rune ring, rubble, four stations (forge, dock gate, scale, healing spring) and glowing deep-sea overgrowth. 500–1,550 triangles, 25–90 KB each (about 790 KB total), no textures (stone uses weathering vertex colours, glyphs and lamps are emissive). Records have `collection: "deep-sea-ruins"`; licence is UNKNOWN until the owner declares one. Built with Blender: `blender -b -P scripts/deep-sea-ruins/build_ruins.py -- assets/deep-sea-ruins thumbnails/deep-sea-ruins`, then `npm run deep-sea-ruins`. Details in [deep-sea-ruins/README.md](deep-sea-ruins/README.md); ongoing plan (ruins → enemies → effects → more) in [deep-sea-ruins/PROGRESS.md](deep-sea-ruins/PROGRESS.md).

## DEEP-SEA ENEMIES collection

12 original low-poly enemies with a rigid-part armature and animation clips live in `assets/deep-sea-enemies/` with thumbnails in `thumbnails/deep-sea-enemies/`: scout drone, crawler bot, gunner turret, bulwark walker, jelly drone, eel bot, urchin mine, anglerfish lure bot, squid lancer, ruin sentinel (stone golem), stone crab guardian and hammerhead sweeper. Every enemy has `Idle`; movers add `Walk` or `Swim`; most add `Attack`. 740–2,484 triangles, 56–205 KB each (about 1.5 MB total), no textures. Records have `collection: "deep-sea-enemies"`, `animated: true` and the clip list in `animations`; licence is UNKNOWN until the owner declares one. Built with Blender: `blender -b -P scripts/deep-sea-enemies/build_enemies.py -- assets/deep-sea-enemies thumbnails/deep-sea-enemies`, then `npm run deep-sea-enemies`. Details in [deep-sea-enemies/README.md](deep-sea-enemies/README.md).

## DEEP-SEA PROPS collection

20 original low-poly objects in `assets/deep-sea-props/` with thumbnails in `thumbnails/deep-sea-props/`: 8 effect meshes (headlight beam, surface light shaft, bubble column, sonar pulse rings, shockwave ring, energy orb, spark burst, current vortex), 6 pickups (shard crystal, relic tablet, healing pearl, treasure chest, ancient coins, rune key) and 6 props / terrain pieces (basalt column cluster, large boulder, sunken anchor, hydrothermal vent chimney, crate stack, fan coral). The effect meshes use emissive alpha-blend materials (render them in the transparent pass, `depthWrite = false`). 168–1,388 triangles, 11–75 KB each (about 600 KB total), no textures. Records have `collection: "deep-sea-props"`; licence is UNKNOWN until the owner declares one. Built with Blender: `blender -b -P scripts/deep-sea-props/build_props.py -- assets/deep-sea-props thumbnails/deep-sea-props`, then `npm run deep-sea-props`. Details in [deep-sea-props/README.md](deep-sea-props/README.md).

## DEEP-TRENCH ENEMIES collection

10 original rigged low-poly enemies for depths from 3,500 m in `assets/deep-trench-enemies/` (thumbnails in `thumbnails/deep-trench-enemies/`), grouped by proposed depth band: luminous deep (lantern swarm drone, viperfish hunter, siphonophore chain, isopod roller, tubeworm spitter), sunken city (archive warden, obelisk stalker, lamplighter) and abyss (echo manta, void anemone). Same rig, clip names (`Idle` / `Walk` / `Swim` / `Attack`) and conventions as `deep-sea-enemies`; no bosses. 652–4,292 triangles, about 1.5 MB total, no textures. Records have `collection: "deep-trench-enemies"`; licence is UNKNOWN until the owner declares one. Built with Blender: `blender -b -P scripts/deep-trench-enemies/build_trench_enemies.py -- assets/deep-trench-enemies thumbnails/deep-trench-enemies`, then `npm run deep-trench-enemies`. Details in [deep-trench-enemies/README.md](deep-trench-enemies/README.md).

## DEEP-TRENCH PROPS collection

20 original low-poly objects for depths from 3,500 m in `assets/deep-trench-props/` (thumbnails in `thumbnails/deep-trench-props/`): luminous-deep scenery (lume coral, glass sponge colony, lamp stalks, whale fall, tubeworm garden, manganese nodule field), sunken-city dressing (street lamp, record obelisk, dwelling ruin corner, everyday ware, conduit bundle, mural panel, glowing rubble) and abyss phenomenon visuals (afterimage echo, phase rift, rainbow current, floating stones, pressure husk dome, unseen steps, abyssal monolith). The `alpha`-tagged models use emissive alpha-blend materials. Meanings of glyphs, murals and monoliths are deliberately left open. 316–3,464 triangles, about 1.5 MB total, no textures. Records have `collection: "deep-trench-props"`; licence is UNKNOWN until the owner declares one. Built with Blender: `blender -b -P scripts/deep-trench-props/build_trench_props.py -- assets/deep-trench-props thumbnails/deep-trench-props`, then `npm run deep-trench-props`. Details in [deep-trench-props/README.md](deep-trench-props/README.md).

## DEEP-SEA SUBMARINE collection

20 original low-poly submarine upgrade parts in `assets/deep-sea-submarine/` (thumbnails in `thumbnails/deep-sea-submarine/`), scaled for the 14 m submarine of the crustaceans-have-plans game: pressure hull sections Mk1–Mk3 and a purple-and-gold shell reinforcement, small and large thrusters, ballast tank, battery pack, sonar dish and hydrophone array, headlamp and floodlight bar, manipulator arm, tether winch, cargo pod, sample rack, hatch tower, dome viewport, antenna mast and a repair kit. Design only: tiers, stats and prices are not decided. 232–2,536 triangles, about 1.3 MB total, no textures; only the `glass` material is alpha-blended. Records have `collection: "deep-sea-submarine"`; licence is UNKNOWN until the owner declares one. Built through Blender MCP (live Blender 5.2) or headless: `blender -b -P scripts/deep-sea-submarine/build_sub_parts.py -- assets/deep-sea-submarine thumbnails/deep-sea-submarine`, then `npm run deep-sea-submarine`. Details in [deep-sea-submarine/README.md](deep-sea-submarine/README.md).

## DEEP-PEARL SEA collection

20 original low-poly background objects for the 4,500 m "milky pearl sea" of the crustaceans-have-plans game, in `assets/deep-pearl-sea/` (thumbnails in `thumbnails/deep-pearl-sea/`): white coral, a translucent nacre leaf forest, giant pearl crystals, a moulted husk arch, peeling shell layers, a pearl clam, a pearl heap, a shell-dust drift, a white colonnade, an arch gate, a domed pavilion, terraced falls and a spiral shell spire, plus translucent effects (light curtain, shell-dust current, moulting sheet, nacre bubbles, iridescent veil) and two ordinary small-fish pieces. The boss is not modelled (it is being designed separately). 126–4,200 triangles, about 1.4 MB total, no textures; translucent materials use alpha blending. Records have `collection: "deep-pearl-sea"`; licence is UNKNOWN until the owner declares one. Built with Blender (headless or Blender MCP): `blender -b -P scripts/deep-pearl-sea/build_pearl_parts.py -- assets/deep-pearl-sea thumbnails/deep-pearl-sea`, then `npm run deep-pearl-sea`. Details in [deep-pearl-sea/README.md](deep-pearl-sea/README.md).

## DEEP-BOSS-MURE collection

A design proposal for the 4,500 m boss "The Kingless King (Mure)" of the crustaceans-have-plans game, in `assets/deep-boss-mure/`: a procedurally generated layout of 40,491 small fish (`boss_mure_school.bin` + `.json`, float32 x 11 per fish, meant for an InstancedMesh) that forms a crowned phoenix/manta/ancient-fish silhouette about 257 m long and 218 m across with a hollow body, plus a quarter-density preview GLB and a one-fish GLB. Looks only: HP, attacks, hit boxes and defeat conditions are not decided. Build with `python scripts/deep-boss-mure/build_boss_mure.py assets/deep-boss-mure`, then `npm run deep-boss-mure`. Details in [deep-boss-mure/README.md](deep-boss-mure/README.md).

## Use from Codex / Claude Code

Fetch the raw index URL above, search name/category/tags/recommendedFor, inspect the license, then use previewUrl in Three.js:

```js
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
new GLTFLoader().load(asset.previewUrl, gltf => scene.add(gltf.scene));
```

For reproducible game builds, pin a commit in rawUrl rather than using main.

The MCP server fetches GitHub directly and needs no local NEXUS asset checkout or HTTP server. Configure a stdio command:

```json
{
  "mcpServers": {
    "nexus": {
      "command": "npx",
      "args": ["--yes", "--package=github:Yuji5124/nexus", "nexus-mcp"],
      "env": { "NEXUS_PROJECT_ROOT": "C:\\Users\\hp\\Desktop\\my-game" }
    }
  }
}
```

Tools: search_assets (query, collection, role, climbable, category, tags, format, maxTriangles, animated), get_asset, get_asset_url, list_assets, find_similar_assets, download_asset. download_asset writes only under the consuming game's NEXUS_PROJECT_ROOT, rejects escaping symlinks, and refuses overwrite. Multi-file glTF downloads are not supported; use GLB.

## Developer setup

```sh
npm ci
npm run build
npm run preview
```

Development preview serves the same static artifact at port 4173. It is optional for production use.

The existing 100 CC0 pixel images are retained as 2D resources under library/2d. They are not 3D models or 100 distinct object types. Their source is PixelRubro/Pixel-Art-Prototyping-CC0-Collection, commit 16c69ce913e2f1235941fd0c75e8b5340bd362ad. One original CC0 procedural tree GLB is included to demonstrate 3D search and preview. External catalog examples are excluded from the published index.
