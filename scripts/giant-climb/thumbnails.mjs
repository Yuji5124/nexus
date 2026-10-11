// Renders 256×256 PNG thumbnails for GLB files with three.js in headless Chromium.
// Usage: node scripts/giant-climb/thumbnails.mjs <out-dir> <file.glb>...
// Playwright is resolved from the project or the global install (npm i -g playwright).
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');

async function loadPlaywright() {
  try { return await import('playwright'); } catch {}
  const globalRoot = execFileSync('npm', ['root', '-g']).toString().trim();
  return import(pathToFileURL(createRequire(path.join(globalRoot, 'noop.js')).resolve('playwright')).href);
}

const page = `<!doctype html><html><body style="margin:0;background:transparent">
<script type="importmap">{"imports":{"three":"/node_modules/three/build/three.module.js","three/addons/":"/node_modules/three/examples/jsm/"}}</script>
<script type="module">
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
const size = 256, renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setSize(size, size); renderer.outputColorSpace = THREE.SRGBColorSpace; document.body.append(renderer.domElement);
const loader = new GLTFLoader();
window.renderThumb = async url => {
  const gltf = await loader.loadAsync(url), scene = new THREE.Scene();
  scene.add(new THREE.HemisphereLight(0xffffff, 0x5a6070, 2.2));
  const sun = new THREE.DirectionalLight(0xffffff, 2.4); sun.position.set(4, 8, 6); scene.add(sun);
  scene.add(gltf.scene); gltf.scene.updateMatrixWorld(true);
  const box = new THREE.Box3().setFromObject(gltf.scene, true), sphere = box.getBoundingSphere(new THREE.Sphere());
  const camera = new THREE.PerspectiveCamera(30, 1, sphere.radius / 100, sphere.radius * 100);
  const dir = new THREE.Vector3(1, 0.8, 1.25).normalize();
  camera.position.copy(sphere.center).addScaledVector(dir, sphere.radius / Math.sin(THREE.MathUtils.degToRad(15)) * 1.02);
  camera.lookAt(sphere.center);
  renderer.setClearColor(0x000000, 0); renderer.render(scene, camera);
  scene.traverse(n => { n.geometry?.dispose(); for (const m of [].concat(n.material || [])) { for (const v of Object.values(m)) if (v?.isTexture) v.dispose(); m.dispose(); } });
  return renderer.domElement.toDataURL('image/png');
};
window.ready = true;
</script></body></html>`;

export async function renderThumbnails(outDir, files) {
  const mime = { '.js': 'text/javascript', '.glb': 'model/gltf-binary', '.png': 'image/png' };
  const server = http.createServer(async (req, res) => {
    const url = decodeURIComponent(new URL(req.url, 'http://x').pathname);
    if (url === '/') { res.writeHead(200, { 'content-type': 'text/html' }); return res.end(page); }
    const file = path.resolve(root, '.' + url);
    if (!file.startsWith(root + path.sep)) { res.writeHead(403); return res.end(); }
    try { const data = await fs.readFile(file); res.writeHead(200, { 'content-type': mime[path.extname(file)] || 'application/octet-stream' }); res.end(data); }
    catch { res.writeHead(404); res.end(); }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const playwright = await loadPlaywright(), chromium = playwright.chromium || playwright.default.chromium;
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const tab = await browser.newPage({ viewport: { width: 256, height: 256 } });
  await tab.goto(`http://127.0.0.1:${server.address().port}/`);
  await tab.waitForFunction(() => window.ready);
  await fs.mkdir(outDir, { recursive: true });
  const written = [];
  for (const file of files) {
    const rel = '/' + path.relative(root, path.resolve(file)).split(path.sep).map(encodeURIComponent).join('/');
    const dataUrl = await tab.evaluate(url => window.renderThumb(url), rel);
    const target = path.join(outDir, path.basename(file).replace(/\.glb$/i, '.png'));
    await fs.writeFile(target, Buffer.from(dataUrl.split(',')[1], 'base64'));
    written.push(target);
  }
  await browser.close(); server.close();
  return written;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const [outDir, ...files] = process.argv.slice(2);
  console.log(`Rendered ${(await renderThumbnails(outDir, files)).length} thumbnails`);
}
