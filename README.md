# NEXUS

NEXUS is a local-first 3D Asset Hub for searching free/CC0 assets, previewing models, keeping a reusable library, and sending approved files to registered game projects.

## Run locally

```sh
npm install
npm start
```

Open <http://localhost:4173>.

For a managed cloud preview, run `npm run preview` and expose TCP port `4173` through the environment's port-forwarding/preview setting. Binding to `0.0.0.0` makes the service reachable from an approved forward; it does not itself create a public tunnel or bypass the environment network policy.

The server is intentionally dependency-light: Node's built-in HTTP server provides the REST API and Three.js is used only by the browser preview. The UI runs in `LOCAL MODE`; it does not require a paid API key.

## v0.1 features

- Free-first and CC0-first catalog search with provider/type/GLB filters
- Provider-neutral catalog shape for Poly Haven, ambientCG, Kenney, BlenderKit Free, Quaternius, and future adapters
- Three.js orbit/zoom/pan preview with auto-rotate and grid controls
- Asset detail, source URL, license, author, tags, and technical facts
- Download into `library/` with metadata in `library/assets.json`
- Local `.glb` / `.gltf` import into the Library with an offline thumbnail placeholder
- Favorites stored locally in the browser with a saved-only filter
- 100 verified CC0 2D assets from the pinned PixelRubro collection, stored under `library/2d/`
- Project Bridge with configured project paths only
- `COPY THREE.JS` template generation without an AI service
- REST endpoints for assets, search, projects, library, download, and send
- MCP stdio server exposing asset search, library, download, and Project Bridge tools

## Project Bridge safety

Projects are declared in `config/projects.json`. The server resolves each `assetDir`, requires it to remain below the workspace, and writes only inside that directory. User-provided paths are never accepted by the API. Add a project explicitly before using `SEND TO PROJECT`.

## API

```text
GET  /api/search?q=tree&cc0=true&glb=true
GET  /api/assets
GET  /api/assets/:id
POST /api/import             { "filename": "tree.glb", "contentBase64": "..." }
POST /api/assets/:id/download
GET  /api/projects
POST /api/assets/:id/send   { "project": "Three.test" }
GET  /api/library
```

## Architecture and licensing note

NEXUS uses an independent implementation inspired by the public architecture ideas of `arielshad/3d-asset-server`: provider abstraction, REST boundaries, local downloads, license-aware results, and a web client. No source code from that project was copied into this repository. If code is later reused, its Apache-2.0 `NOTICE`, copyright, license, and modification requirements must be preserved.

The MCP adapter is intentionally a thin layer over the REST routes; provider-neutral core behavior remains shared with the web UI.

## Included 2D collection

The initial 2D stock is sourced from `PixelRubro/Pixel-Art-Prototyping-CC0-Collection` at commit `16c69ce913e2f1235941fd0c75e8b5340bd362ad`. Its repository includes a CC0 1.0 license and credits for the underlying tileset, UI, props, and Treasure Hunters sources. NEXUS stores the source URL and `CC0 1.0` license in each Library record. Review the upstream credits before redistribution.

## MCP

Start the local API with `npm start`, then register `node /workspace/nexus/mcp-server.js` as an MCP stdio server. Set `NEXUS_API_URL` when the API runs on another port. The adapter intentionally reuses the REST API, so Project Bridge safety checks and Library behavior remain identical for the web UI and agents.
