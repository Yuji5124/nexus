import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const dist = path.join(root, 'dist');
await fs.mkdir(dist, { recursive: true });
await fs.cp(path.join(root, 'public'), dist, { recursive: true });
await fs.copyFile(path.join(root, 'src/search.js'), path.join(dist, 'search.js'));
for (const dir of ['data', 'assets', 'thumbnails', 'library/2d', 'library/models']) {
  try { await fs.access(path.join(root, dir)); } catch { continue; }
  await fs.cp(path.join(root, dir), path.join(dist, dir), { recursive: true });
}
await fs.cp(path.join(root, 'node_modules/three'), path.join(dist, 'vendor/three'), { recursive: true });
console.log('GitHub Pages artifact built in dist/');
