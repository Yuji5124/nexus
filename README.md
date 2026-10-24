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
