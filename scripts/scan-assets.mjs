import fs from "node:fs/promises";
import crypto from "node:crypto";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const dataFile = path.join(root, "data", "assets.json");
const sourceRoots = ["assets", "library/models", "library/2d"];
const supported = new Set([".glb", ".gltf", ".fbx", ".obj", ".png", ".jpg", ".jpeg", ".webp"]);

async function readJson(file, fallback) { try { return JSON.parse(await fs.readFile(file, "utf8")); } catch { return fallback; } }
async function filesUnder(directory) {
  try { await fs.access(directory); } catch { return []; }
  const entries = await fs.readdir(directory, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const full = path.join(directory, entry.name);
    if (entry.isDirectory()) files.push(...await filesUnder(full));
    else if (supported.has(path.extname(entry.name).toLowerCase())) files.push(full);
  }
  return files;
}

function idFor(relative) { return relative.replace(/\\/g, "/").replace(/\.[^.]+$/, "").replace(/[^a-zA-Z0-9]+/g, "_").replace(/^_+|_+$/g, "").toLowerCase(); }
function pathTags(relative) { return relative.replace(/\\/g, "/").split("/").flatMap((part) => part.replace(/\.[^.]+$/, "").split(/[^a-zA-Z0-9]+/)).map((tag) => tag.toLowerCase()).filter((tag) => tag && !/^\d+$/.test(tag)); }

function glbJson(buffer) {
  if (buffer.length < 20 || buffer.toString("ascii", 0, 4) !== "glTF") return null;
  let offset = 12;
  while (offset + 8 <= buffer.length) {
    const length = buffer.readUInt32LE(offset); const type = buffer.readUInt32LE(offset + 4); offset += 8;
    if (type === 0x4e4f534a) return JSON.parse(buffer.toString("utf8", offset, offset + length).replace(/\0+$/, "").trim());
    offset += length;
  }
  return null;
}

// World-space bounds: apply node transforms to each mesh's POSITION accessor box.
function multiply(a, b) { const r = new Array(16).fill(0); for (let c = 0; c < 4; c++) for (let rI = 0; rI < 4; rI++) for (let k = 0; k < 4; k++) r[c * 4 + rI] += a[k * 4 + rI] * b[c * 4 + k]; return r; }
function localMatrix(node) {
  if (node.matrix) return node.matrix;
  const [x, y, z, w] = node.rotation || [0, 0, 0, 1], [sx, sy, sz] = node.scale || [1, 1, 1], [tx, ty, tz] = node.translation || [0, 0, 0];
  return [(1 - 2 * (y * y + z * z)) * sx, 2 * (x * y + z * w) * sx, 2 * (x * z - y * w) * sx, 0, 2 * (x * y - z * w) * sy, (1 - 2 * (x * x + z * z)) * sy, 2 * (y * z + x * w) * sy, 0, 2 * (x * z + y * w) * sz, 2 * (y * z - x * w) * sz, (1 - 2 * (x * x + y * y)) * sz, 0, tx, ty, tz, 1];
}
function sceneBounds(doc) {
  const scene = doc?.scenes?.[doc.scene ?? 0]; if (!scene) return null;
  let min = [Infinity, Infinity, Infinity], max = [-Infinity, -Infinity, -Infinity];
  const visit = (index, parent) => {
    const node = doc.nodes?.[index]; if (!node) return; const m = multiply(parent, localMatrix(node));
    for (const primitive of doc.meshes?.[node.mesh]?.primitives || []) {
      const a = doc.accessors?.[primitive.attributes?.POSITION]; if (!a?.min || !a?.max) continue;
      for (let i = 0; i < 8; i++) { const p = [i & 1 ? a.max[0] : a.min[0], i & 2 ? a.max[1] : a.min[1], i & 4 ? a.max[2] : a.min[2]];
        for (let j = 0; j < 3; j++) { const v = m[j] * p[0] + m[4 + j] * p[1] + m[8 + j] * p[2] + m[12 + j]; min[j] = Math.min(min[j], v); max[j] = Math.max(max[j], v); } }
    }
    for (const child of node.children || []) visit(child, m);
  };
  for (const index of scene.nodes || []) visit(index, [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]);
  return Number.isFinite(min[0]) ? { min: min.map(v => Number(v.toFixed(4))), max: max.map(v => Number(v.toFixed(4))) } : null;
}

function gltfStats(doc) {
  const accessors = doc?.accessors || []; let vertices = 0; let triangles = 0; let min; let max;
  for (const mesh of doc?.meshes || []) for (const primitive of mesh.primitives || []) {
    const position = primitive.attributes?.POSITION;
    if (position == null || !accessors[position]) continue;
    const accessor = accessors[position]; vertices += accessor.count || 0;
    if (accessor.min && accessor.max) { min = min ? min.map((v, i) => Math.min(v, accessor.min[i])) : [...accessor.min]; max = max ? max.map((v, i) => Math.max(v, accessor.max[i])) : [...accessor.max]; }
    const index = primitive.indices == null ? null : accessors[primitive.indices];
    triangles += Math.floor((index?.count ?? accessor.count ?? 0) / 3);
  }
  const world = sceneBounds(doc); if (world) { min = world.min; max = world.max; }
  const dimensions = min && max ? max.map((v, i) => Number((v - min[i]).toFixed(4))) : null;
  return { vertices, triangles, meshCount: doc?.meshes?.length || 0, materialCount: doc?.materials?.length || 0, textureCount: doc?.textures?.length || 0, animations: (doc?.animations || []).map((item) => item.name || "unnamed"), boundingBox: min && max ? { min, max } : null, dimensions };
}

async function scanFile(file, existing) {
  const relative = path.relative(root, file).replace(/\\/g, "/"); const extension = path.extname(file).toLowerCase(); const stat = await fs.stat(file);
  const old = existing.find((item) => item.localPath === relative || item.file === relative || item.id === idFor(relative));
  const parts = relative.split("/"); const category = old?.category || (parts[1] && parts[0] === "assets" ? parts[1] : "local"); const subcategory = old?.subcategory || (parts[2] && parts[0] === "assets" ? parts[2] : undefined);
  let stats = {}; if (extension === ".glb") { try { stats = gltfStats(glbJson(await fs.readFile(file))); } catch { stats = {}; } }
  const format = extension === ".gltf" ? "glTF" : extension.slice(1).toUpperCase();
  const isImage = [".png", ".jpg", ".jpeg", ".webp"].includes(extension);
  return { ...old, id: old?.id || idFor(relative), name: old?.name || path.basename(file, extension), title: old?.title || old?.name || path.basename(file, extension), category, ...(subcategory ? { subcategory } : {}), tags: old?.tags?.length ? old.tags : [...new Set(pathTags(relative))], file: relative, localPath: relative, thumbnail: old?.thumbnail || (isImage ? `/${relative}` : "thumbnail missing"), format, type: old?.type || (isImage ? "texture" : "model"), size: stat.size, fileSize: stat.size, vertices: stats.vertices ?? old?.vertices ?? null, triangles: stats.triangles ?? old?.triangles ?? null, polygonCount: stats.triangles ?? old?.polygonCount ?? null, meshCount: stats.meshCount ?? old?.meshCount ?? null, materials: stats.materialCount ?? old?.materials ?? null, textures: stats.textureCount ?? old?.textures ?? null, animations: stats.animations ?? old?.animations ?? [], animated: (stats.animations || old?.animations || []).length > 0, boundingBox: stats.boundingBox ?? old?.boundingBox ?? null, dimensions: stats.dimensions ?? old?.dimensions ?? null, scale: old?.scale ?? 1, license: old?.license || "UNKNOWN", source: old?.source || "", sourceUrl: old?.sourceUrl || "", author: old?.author || "", addedAt: old?.addedAt || stat.birthtime.toISOString(), notes: old?.notes || "", recommendedFor: old?.recommendedFor || [] };
}

const existing = await readJson(dataFile, await readJson(path.join(root, "library/assets.json"), [])); const discovered = [];
for (const source of sourceRoots) for (const file of await filesUnder(path.join(root, source))) discovered.push(await scanFile(file, existing));
const discoveredPaths = new Set(discovered.map((item) => item.localPath || item.file));
const preserved = existing.filter((item) => !discoveredPaths.has(item.localPath || item.file));
await fs.mkdir(path.dirname(dataFile), { recursive: true });
const records = await Promise.all(discovered.map(async (item) => {
  const assetPath = item.file;
  const encoded = assetPath.split("/").map(encodeURIComponent).join("/");
  const sha256 = crypto.createHash('sha256').update(await fs.readFile(path.join(root,assetPath))).digest('hex');
  return { ...item, sha256, path: assetPath, source: item.source || item.provider || "", rawUrl: `https://raw.githubusercontent.com/Yuji5124/nexus/main/${encoded}`, previewUrl: `https://yuji5124.github.io/nexus/${encoded}`, thumbnail: item.type === "texture" ? assetPath : item.thumbnail === "thumbnail missing" ? null : item.thumbnail };
}));
await fs.writeFile(dataFile, JSON.stringify(records, null, 2) + "\n");
console.log(`Scanned ${discovered.length} files; preserved ${preserved.length} metadata-only records.`);
