import http from "node:http";
import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { catalog } from "./src/catalog.js";

const root = path.dirname(fileURLToPath(import.meta.url));
const publicDir = path.join(root, "public");
const libraryFile = path.join(root, "library", "assets.json");
const projectsFile = path.join(root, "config", "projects.json");
const port = Number(process.env.PORT || 4173);
const host = process.env.HOST || "0.0.0.0";

const json = (res, status, value) => {
  res.writeHead(status, { "content-type": "application/json; charset=utf-8" });
  res.end(JSON.stringify(value));
};

async function readJson(file, fallback) {
  try { return JSON.parse(await fs.readFile(file, "utf8")); } catch { return fallback; }
}

async function body(req) {
  let text = "";
  for await (const chunk of req) {
    text += chunk;
    if (text.length > 80 * 1024 * 1024) throw new Error("Request is too large");
  }
  return text ? JSON.parse(text) : {};
}

function localAsset(record) {
  return {
    ...record,
    title: record.title || record.name,
    type: record.type || "model",
    format: record.format || "GLB",
    free: record.free ?? record.license?.toLowerCase().includes("cc0") ?? false,
    downloadable: false,
    tags: record.tags || ["local", "imported"],
    polygonCount: record.polygonCount || null,
    fileSize: record.fileSize || null,
    modelUrl: record.modelUrl || (record.type === "model" ? `/${record.localPath}` : null)
  };
}

async function allAssets() {
  const library = await readJson(libraryFile, []);
  return [...catalog, ...library.map(localAsset)];
}

function slug(value) {
  return String(value || "asset").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 56) || "asset";
}

function importedThumbnail(title) {
  const label = String(title || "LOCAL ASSET").slice(0, 24).replace(/[<>&]/g, "");
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="640" height="420"><rect width="100%" height="100%" fill="#172018"/><path d="M0 340 190 180l110 90 120-130 220 200v80H0z" fill="#b7d35a" opacity=".8"/><text x="28" y="52" fill="#e8ebef" font-family="sans-serif" font-size="22">${label}</text><text x="28" y="390" fill="#0a0b0d" font-family="sans-serif" font-size="16">NEXUS LIBRARY</text></svg>`;
  return `data:image/svg+xml,${encodeURIComponent(svg)}`;
}

async function importAsset(input) {
  const filename = String(input.filename || "");
  const extension = path.extname(filename).toLowerCase();
  const imageExtensions = [".png", ".jpg", ".jpeg", ".webp"];
  const modelExtensions = [".glb", ".gltf"];
  if (![...modelExtensions, ...imageExtensions].includes(extension)) throw new Error("Only GLB, glTF, PNG, JPG, and WebP files can be imported");
  if (typeof input.contentBase64 !== "string" || !input.contentBase64) throw new Error("Asset content is required");
  const title = String(input.name || path.basename(filename, extension)).slice(0, 120);
  const id = `local-${Date.now()}-${slug(title)}`;
  const isImage = imageExtensions.includes(extension);
  const relative = `library/${isImage ? "2d" : "models"}/${id}${extension}`;
  const destination = path.join(root, relative);
  await fs.mkdir(path.dirname(destination), { recursive: true });
  const data = Buffer.from(input.contentBase64, "base64");
  if (data.length > 50 * 1024 * 1024) throw new Error("Asset exceeds the 50 MB import limit");
  await fs.writeFile(destination, data);
  const library = await readJson(libraryFile, []);
  const record = { id, name: title, title, provider: String(input.provider || "NEXUS Library"), sourceUrl: input.sourceUrl || null,
    license: String(input.license || "UNKNOWN LICENSE"), author: String(input.author || "Local import"),
    format: extension === ".gltf" ? "glTF" : extension.slice(1).toUpperCase(), type: isImage ? "texture" : "model", localPath: relative,
    downloadedAt: new Date().toISOString(), usedBy: [], tags: input.tags || ["local", "imported"],
    thumbnail: isImage ? `/${relative}` : importedThumbnail(title), fileSize: data.length,
    sha256: crypto.createHash("sha256").update(data).digest("hex") };
  await fs.writeFile(libraryFile, JSON.stringify([...library, record], null, 2) + "\n");
  return localAsset(record);
}

function score(asset) {
  return (asset.license.toLowerCase().includes("cc0") ? 40 : 0)
    + (asset.free ? 20 : 0)
    + (asset.format === "GLB" || asset.format === "glTF" ? 10 : 0)
    + (asset.downloadable ? 5 : 0);
}

async function sendAsset(asset, projectName) {
  const config = await readJson(projectsFile, { projects: [] });
  const project = config.projects.find((item) => item.name === projectName);
  if (!project) throw new Error("Project is not registered");
  const projectRoot = path.resolve(root, project.assetDir);
  const workspaceRoot = path.resolve(root, "..");
  if (!projectRoot.startsWith(workspaceRoot + path.sep)) throw new Error("Project path is outside the workspace");
  const filename = `${asset.id}.${asset.format.toLowerCase() === "gltf" ? "gltf" : "glb"}`;
  const destination = path.resolve(projectRoot, filename);
  if (!destination.startsWith(projectRoot + path.sep)) throw new Error("Invalid destination");
  await fs.mkdir(projectRoot, { recursive: true });
  if (asset.localPath) {
    const localSource = path.resolve(root, asset.localPath);
    if (!localSource.startsWith(path.resolve(root, "library") + path.sep)) throw new Error("Invalid library source");
    await fs.copyFile(localSource, destination);
  } else {
    if (!asset.modelUrl) throw new Error("This provider does not expose a direct model download yet");
    const response = await fetch(asset.modelUrl);
    if (!response.ok) throw new Error(`Provider download failed (${response.status})`);
    await fs.writeFile(destination, Buffer.from(await response.arrayBuffer()));
  }
  const library = await readJson(libraryFile, []);
  const record = library.find((item) => item.id === asset.id) || {
    id: asset.id, name: asset.title, provider: asset.provider, sourceUrl: asset.sourceUrl,
    license: asset.license, author: asset.author, format: asset.format,
    localPath: path.relative(root, destination), downloadedAt: new Date().toISOString(), usedBy: []
  };
  if (!record.usedBy.includes(projectName)) record.usedBy.push(projectName);
  const next = [...library.filter((item) => item.id !== asset.id), record];
  await fs.writeFile(libraryFile, JSON.stringify(next, null, 2) + "\n");
  return { project: projectName, destination, filename, library: record };
}

async function downloadAsset(asset) {
  if (!asset.modelUrl) throw new Error("This provider does not expose a direct model download yet");
  const library = await readJson(libraryFile, []);
  const existing = library.find((item) => item.id === asset.id);
  if (existing) return { ...existing, cached: true };
  const response = await fetch(asset.modelUrl);
  if (!response.ok) throw new Error(`Provider download failed (${response.status})`);
  const extension = asset.modelUrl.toLowerCase().includes(".gltf") ? "gltf" : "glb";
  const relative = `models/${asset.id}.${extension}`;
  const destination = path.join(root, "library", relative);
  await fs.mkdir(path.dirname(destination), { recursive: true });
  await fs.writeFile(destination, Buffer.from(await response.arrayBuffer()));
  const record = { id: asset.id, name: asset.title, provider: asset.provider, sourceUrl: asset.sourceUrl,
    license: asset.license, author: asset.author, format: asset.format, localPath: `library/${relative}`,
    downloadedAt: new Date().toISOString(), usedBy: [] };
  await fs.writeFile(libraryFile, JSON.stringify([...library, record], null, 2) + "\n");
  return record;
}

async function route(req, res, url) {
  if (url.pathname === "/api/health") return json(res, 200, { ok: true, mode: "local" });
  if (url.pathname === "/api/import" && req.method === "POST") {
    try { return json(res, 201, await importAsset(await body(req))); }
    catch (error) { return json(res, 400, { error: error.message }); }
  }
  if (url.pathname === "/api/assets" || url.pathname === "/api/search") {
    const q = (url.searchParams.get("q") || "").toLowerCase();
    const type = (url.searchParams.get("type") || "all").toLowerCase();
    const provider = (url.searchParams.get("provider") || "all").toLowerCase();
    const free = url.searchParams.get("free") !== "false";
    const cc0 = url.searchParams.get("cc0") === "true";
    const glb = url.searchParams.get("glb") === "true";
    const assets = (await allAssets()).filter((asset) => {
      const text = `${asset.title} ${asset.provider} ${asset.tags.join(" ")}`.toLowerCase();
      return (!q || text.includes(q)) && (type === "all" || asset.type === type)
        && (provider === "all" || asset.provider.toLowerCase() === provider)
        && (!free || asset.free) && (!cc0 || asset.license.toLowerCase().includes("cc0"))
        && (!glb || asset.format === "GLB");
    }).sort((a, b) => score(b) - score(a));
    return json(res, 200, { assets, total: assets.length });
  }
  if (url.pathname.startsWith("/api/assets/")) {
    const parts = url.pathname.split("/").filter(Boolean);
    const id = parts[2];
    const asset = (await allAssets()).find((item) => item.id === id);
    if (!asset) return json(res, 404, { error: "Asset not found" });
    const library = await readJson(libraryFile, []);
    const enriched = { ...asset, usedBy: library.find((item) => item.id === id)?.usedBy || [] };
    if (req.method === "POST" && parts[3] === "download") {
      try { return json(res, 200, await downloadAsset(asset)); }
      catch (error) { return json(res, 400, { error: error.message }); }
    }
    if (req.method === "POST" && parts[3] === "send") {
      try { return json(res, 200, await sendAsset(asset, (await body(req)).project)); }
      catch (error) { return json(res, 400, { error: error.message }); }
    }
    return json(res, 200, enriched);
  }
  if (url.pathname === "/api/projects") return json(res, 200, await readJson(projectsFile, { projects: [] }));
  if (url.pathname === "/api/library") return json(res, 200, await readJson(libraryFile, []));
  return json(res, 404, { error: "Not found" });
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || "localhost"}`);
  if (url.pathname.startsWith("/api/")) {
    try { await route(req, res, url); } catch (error) { json(res, 500, { error: error.message }); }
    return;
  }
  const isVendor = url.pathname.startsWith("/vendor/three/");
  const isLibrary = url.pathname.startsWith("/library/");
  const requested = url.pathname === "/" ? "/index.html" : url.pathname;
  const file = isVendor
    ? path.resolve(root, "node_modules/three", url.pathname.slice("/vendor/three/".length))
    : isLibrary ? path.resolve(root, url.pathname.slice(1))
    : path.resolve(publicDir, `.${requested}`);
  const allowedRoot = isVendor ? path.resolve(root, "node_modules/three") : isLibrary ? path.resolve(root, "library") : publicDir;
  if (!file.startsWith(allowedRoot + path.sep)) return json(res, 400, { error: "Invalid path" });
  try {
    const data = await fs.readFile(file);
    const type = file.endsWith(".html") ? "text/html" : file.endsWith(".css") ? "text/css"
      : file.endsWith(".png") ? "image/png" : file.endsWith(".jpg") || file.endsWith(".jpeg") ? "image/jpeg"
      : file.endsWith(".webp") ? "image/webp" : "text/javascript";
    res.writeHead(200, { "content-type": `${type}; charset=utf-8` }); res.end(data);
  } catch { json(res, 404, { error: "Not found" }); }
});

server.listen(port, host, () => console.log(`NEXUS running at http://${host}:${port}`));
