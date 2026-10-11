// Fetches every pinned GIANT CLIMB source into .cache/giant-climb/sources.
// git sources are fetched at an exact commit, npm tarballs are checked against
// their registry integrity hash. Downloaded content is treated as data only:
// nothing from it is executed.
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { EnvHttpProxyAgent, setGlobalDispatcher } from 'undici';
import { sources, assets } from '../../giant-climb/catalog.mjs';

if (process.env.HTTPS_PROXY || process.env.https_proxy) setGlobalDispatcher(new EnvHttpProxyAgent());
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
export const cacheDir = path.join(root, '.cache/giant-climb/sources');
const git = (cwd, ...args) => execFileSync('git', args, { cwd, stdio: ['ignore', 'pipe', 'inherit'] }).toString().trim();
const exists = file => fs.access(file).then(() => true, () => false);

async function download(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${url}: HTTP ${response.status}`);
  return Buffer.from(await response.arrayBuffer());
}

async function fetchGit(id, source) {
  const dir = path.join(cacheDir, id);
  if (await exists(path.join(dir, '.git')) && git(dir, 'rev-parse', 'HEAD') === source.commit) return;
  await fs.rm(dir, { recursive: true, force: true });
  await fs.mkdir(dir, { recursive: true });
  git(dir, 'init', '-q');
  git(dir, 'remote', 'add', 'origin', source.repo);
  if (source.sparse) {
    const dirs = [...new Set(assets.filter(a => a.source === id).map(a => `${source.root}/${path.posix.dirname(a.file)}`))];
    git(dir, 'sparse-checkout', 'set', '--cone', ...dirs);
  }
  git(dir, 'fetch', '-q', '--depth', '1', '--filter=blob:none', 'origin', source.commit);
  git(dir, 'checkout', '-q', 'FETCH_HEAD');
  if (git(dir, 'rev-parse', 'HEAD') !== source.commit) throw new Error(`${id}: commit mismatch`);
}

async function fetchNpm(id, source) {
  const dir = path.join(cacheDir, id);
  if (await exists(path.join(dir, source.licenseFile))) return;
  const data = await download(source.tarball);
  const [algorithm, expected] = source.integrity.split('-');
  if (crypto.createHash(algorithm).update(data).digest('base64') !== expected) throw new Error(`${id}: integrity mismatch`);
  await fs.rm(dir, { recursive: true, force: true });
  await fs.mkdir(dir, { recursive: true });
  const tarball = path.join(dir, 'package.tgz');
  await fs.writeFile(tarball, data);
  execFileSync('tar', ['xzf', tarball, '-C', dir, '--no-same-owner', '--no-same-permissions']);
}

async function fetchRaw(id, source) {
  const dir = path.join(cacheDir, id);
  for (const asset of assets.filter(a => a.source === id)) {
    for (const file of [asset.file, path.posix.join(path.posix.dirname(asset.file), 'README.md')]) {
      const target = path.join(dir, file);
      if (await exists(target)) continue;
      await fs.mkdir(path.dirname(target), { recursive: true });
      await fs.writeFile(target, await download(`${source.baseUrl}/${file}`));
    }
  }
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  for (const [id, source] of Object.entries(sources)) {
    if (source.kind === 'generated') continue;
    process.stdout.write(`${id} … `);
    await ({ git: fetchGit, npm: fetchNpm, raw: fetchRaw })[source.kind](id, source);
    console.log('ok');
  }
}
