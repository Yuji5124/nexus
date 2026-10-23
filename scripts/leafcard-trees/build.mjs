// Five lightweight "leaf card" trees for NEXUS (collection "leafcard-trees").
//
// Technique (as in game foliage and EZ-Tree, github.com/dgreenheck/ez-tree):
//   - a low-poly trunk and a few branches (5–6 sided tubes, smooth normals);
//   - foliage as large textured cards: each card is two crossed quads (EZ-Tree's
//     "double billboard"), cut out with an alpha mask (alphaMode MASK, cutoff 0.5)
//     and rendered double-sided;
//   - card normals point away from the crown centre, so the whole crown shades like
//     one soft volume instead of flat planes.
// Every texture is painted here (canvas 2D in headless Chromium, fixed seeds): a
// 512 px atlas of four leaf-cluster variants and a 128×256 bark strip per tree, so
// there are no third-party images. Output: one GLB per tree, 2 materials, a few
// hundred triangles. Deterministic: re-running gives the same files.
//
// Usage: node scripts/leafcard-trees/build.mjs [outDir]   (default assets/leafcard-trees)
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { Document, NodeIO } from '@gltf-transform/core';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');

async function globalModule(name) {
  try { return await import(name); } catch {}
  const globalRoot = execFileSync('npm', ['root', '-g']).toString().trim();
  return import(pathToFileURL(createRequire(path.join(globalRoot, 'noop.js')).resolve(name)).href);
}

// ---------------------------------------------------------------- textures (browser side)
const painter = `<!doctype html><body><script>
function rng(seed){let a=seed>>>0;return()=>{a=(a+0x6d2b79f5)>>>0;let t=a;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return((t^(t>>>14))>>>0)/4294967296;};}
const hsl=(h,s,l,a=1)=>'hsla('+h+','+s+'%,'+l+'%,'+a+')';
function bez(p0,p1,p2,t){const u=1-t;return[u*u*p0[0]+2*u*t*p1[0]+t*t*p2[0],u*u*p0[1]+2*u*t*p1[1]+t*t*p2[1]];}

// One leaf: pointed oval with a lighter midrib, lit from the top-left.
function leaf(g,x,y,ang,len,wid,col,r){
  g.save();g.translate(x,y);g.rotate(ang);
  g.beginPath();g.moveTo(0,0);g.quadraticCurveTo(len*0.45,-wid,len,0);g.quadraticCurveTo(len*0.45,wid,0,0);g.closePath();
  const grad=g.createLinearGradient(0,-wid,0,wid);grad.addColorStop(0,hsl(col[0],col[1],col[2]+10));grad.addColorStop(1,hsl(col[0]+4,col[1],col[2]-6));
  g.fillStyle=grad;g.fill();g.lineWidth=1;g.strokeStyle=hsl(col[0]+6,col[1],Math.max(8,col[2]-22),0.55);g.stroke();
  g.beginPath();g.moveTo(len*0.08,0);g.quadraticCurveTo(len*0.5,-wid*0.12,len*0.9,0);g.lineWidth=1;g.strokeStyle=hsl(col[0]-6,col[1]-10,col[2]+18,0.6);g.stroke();
  g.restore();
}

// Broadleaf cluster in a 256 cell: twigs fanning up from the bottom, leaves along them.
function cluster(g,ox,oy,r,p){
  g.save();g.beginPath();g.rect(ox+2,oy+2,252,252);g.clip();
  const base=[ox+128,oy+238],twigs=[];
  for(let i=0;i<p.twigs;i++){const a=-Math.PI/2+(i/(p.twigs-1)-0.5)*p.spread+(r()-0.5)*0.25,L=150+r()*55;
    const end=[base[0]+Math.cos(a)*L,base[1]+Math.sin(a)*L*1.05],mid=[base[0]+Math.cos(a)*L*0.45+(r()-0.5)*30,base[1]+Math.sin(a)*L*0.5];twigs.push([base,mid,end]);}
  for(const [a,b,c] of twigs){g.beginPath();g.moveTo(a[0],a[1]);g.quadraticCurveTo(b[0],b[1],c[0],c[1]);g.lineCap='round';g.lineWidth=p.twigWidth;g.strokeStyle=p.twig;g.stroke();
    g.lineWidth=p.twigWidth*0.4;g.strokeStyle=p.twigLight;g.stroke();}
  const leaves=[];
  // Most leaves hug the twigs (offset sideways), the rest fill a rounded mass around
  // the upper middle, so each cell reads as a dense clump with twigs peeking out.
  for(let i=0;i<p.leaves;i++){let x,y,ang;const len=p.len[0]+r()*(p.len[1]-p.len[0]);
    if(r()<0.68){const tw=twigs[Math.floor(r()*twigs.length)],t=0.12+Math.pow(r(),0.75)*0.9,pt=bez(tw[0],tw[1],tw[2],Math.min(1,t));
      const d=bez(tw[0],tw[1],tw[2],Math.min(1,t+0.02)),dir=Math.atan2(d[1]-pt[1],d[0]-pt[0]),side=r()<0.5?-1:1,off=r()*16;
      x=pt[0]+Math.cos(dir+side*1.57)*off;y=pt[1]+Math.sin(dir+side*1.57)*off;ang=dir+side*(0.4+r()*0.9);}
    else{const a=r()*Math.PI*2,d=Math.sqrt(r());x=ox+128+Math.cos(a)*d*p.mass[0];y=oy+p.mass[2]+Math.sin(a)*d*p.mass[1];ang=r()*Math.PI*2;}
    if(x<ox+len*0.6||x>ox+256-len*0.6||y<oy+len*0.6)continue;leaves.push([x,y,ang,len]);}
  leaves.sort((a,b)=>a[1]-b[1]>0?-1:1); // paint lower leaves last so the top looks layered under light
  leaves.reverse();
  for(const [x,y,ang,len] of leaves){const up=1-(y-oy)/256,pal=p.palette[Math.floor(r()*p.palette.length)];
    leaf(g,x,y,ang,len,len*p.width,[pal[0]+(r()-0.5)*8,pal[1],pal[2]+up*12+(r()-0.5)*10],r);}
  if(p.flowers)for(let i=0;i<p.flowers;i++){const [x,y]=leaves[Math.floor(r()*leaves.length)];g.beginPath();g.arc(x+(r()-0.5)*14,y+(r()-0.5)*14,3+r()*2,0,7);g.fillStyle=p.flowerColor;g.fill();}
  g.restore();
}

// Conifer frond in a 256 cell: stem from the bottom (trunk side) to the top (tip),
// side shoots, and dense needles. Wider near the trunk so a sloped card reads as a skirt.
function frond(g,ox,oy,r,p){
  g.save();g.beginPath();g.rect(ox+2,oy+2,252,252);g.clip();
  const stem=t=>[ox+128+Math.sin(t*3)*6,oy+250-t*240];
  const needles=(x0,y0,x1,y1,len,width)=>{const n=Math.hypot(x1-x0,y1-y0)/2.2,ang=Math.atan2(y1-y0,x1-x0);
    for(let i=0;i<n;i++){const t=i/n,x=x0+(x1-x0)*t,y=y0+(y1-y0)*t,l=len*(1-t*0.55);
      for(const s of[-1,1]){const a=ang+s*(0.75+r()*0.3),pal=p.palette[Math.floor(r()*p.palette.length)];
        g.beginPath();g.moveTo(x,y);g.lineTo(x+Math.cos(a)*l,y+Math.sin(a)*l);g.lineWidth=width;g.strokeStyle=hsl(pal[0],pal[1],pal[2]+(1-t)*-6+r()*14);g.stroke();}}};
  const shoots=[];for(let i=0;i<p.shoots;i++){const t=0.08+i/p.shoots*0.85,[x,y]=stem(t),side=i%2?1:-1,w=(1-t)*p.reach+18;
    shoots.push([x,y,x+side*w,y-w*0.55-8]);}
  for(const s of shoots){g.beginPath();g.moveTo(s[0],s[1]);g.lineTo(s[2],s[3]);g.lineWidth=2;g.strokeStyle=p.twig;g.stroke();}
  const [sx,sy]=stem(0),[ex,ey]=stem(1);g.beginPath();g.moveTo(sx,sy);g.lineTo(ex,ey);g.lineWidth=3;g.strokeStyle=p.twig;g.stroke();
  for(const s of shoots)needles(...s,p.needle,2);
  needles(sx,sy,ex,ey,p.needle*1.15,2.2);
  g.restore();
}

function bark(g,r,p){
  g.fillStyle=hsl(...p.base);g.fillRect(0,0,128,256);
  for(let i=0;i<220;i++){const x=r()*128,w=1+r()*3.5,l=20+r()*90,y=r()*256,d=(r()-0.5)*p.contrast;
    g.fillStyle=hsl(p.base[0]+(r()-0.5)*6,p.base[1],p.base[2]+d,0.55);g.fillRect(x,y,w,l);g.fillRect(x-128,y,w,l);g.fillRect(x,y-256,w,l);}
  for(let i=0;i<p.cracks;i++){const x=r()*128,y=r()*256;g.fillStyle=hsl(p.base[0],p.base[1],p.base[2]-p.contrast*0.9,0.7);g.fillRect(x,y,2+r()*3,30+r()*80);}
  if(p.rings)for(let i=0;i<p.rings;i++){const y=r()*256;g.fillStyle=hsl(p.base[0],p.base[1]-5,p.base[2]-14,0.5);g.fillRect(0,y,128,1.5+r()*1.5);}
}

window.paint=(spec)=>{
  const c=document.createElement('canvas');c.width=c.height=512;const g=c.getContext('2d');const r=rng(spec.seed);
  for(let i=0;i<4;i++){const ox=(i%2)*256,oy=Math.floor(i/2)*256;spec.leaf.kind==='frond'?frond(g,ox,oy,r,spec.leaf):cluster(g,ox,oy,r,spec.leaf);}
  const b=document.createElement('canvas');b.width=128;b.height=256;bark(b.getContext('2d'),rng(spec.seed+7),spec.bark);
  return{leaves:c.toDataURL('image/png'),bark:b.toDataURL('image/png')};
};
window.ready=true;
</script></body>`;

// ---------------------------------------------------------------- geometry helpers
const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const mul = (a, s) => [a[0] * s, a[1] * s, a[2] * s];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const norm = a => { const l = Math.hypot(...a) || 1; return mul(a, 1 / l); };
const lerp3 = (a, b, t) => add(a, mul(sub(b, a), t));
function rng(seed) {
  let a = seed >>> 0;
  const next = () => { a = (a + 0x6d2b79f5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  return { next, range: (lo, hi) => lo + (hi - lo) * next() };
}

class Part {
  constructor() { this.p = []; this.n = []; this.uv = []; this.i = []; }
  vertex(p, n, uv) { this.p.push(...p); this.n.push(...n); this.uv.push(...uv); return this.p.length / 3 - 1; }
  tri(a, b, c) { this.i.push(a, b, c); }
  get triangles() { return this.i.length / 3; }
}

/** Smooth tapered tube through pts (parallel-transport rings); v runs along the length. */
function tube(part, pts, radii, sides, { flare = 0, vScale = 0.6 } = {}) {
  let n0 = null, v = 0; const rings = [];
  for (let i = 0; i < pts.length; i++) {
    const t = norm(sub(pts[Math.min(i + 1, pts.length - 1)], pts[Math.max(i - 1, 0)]));
    n0 = n0 ? norm(sub(n0, mul(t, dot(t, n0)))) : norm(Math.abs(t[1]) < 0.9 ? cross(t, [0, 1, 0]) : [1, 0, 0]);
    const b = cross(t, n0);
    if (i) v += Math.hypot(...sub(pts[i], pts[i - 1])) * vScale;
    const ring = [];
    for (let s = 0; s <= sides; s++) {
      const a = (s / sides) * Math.PI * 2, dir = add(mul(n0, Math.cos(a)), mul(b, Math.sin(a)));
      const r = radii[i] * (i === 0 && flare ? 1 + flare * (0.6 + 0.4 * Math.cos(a * 2)) : 1);
      ring.push(part.vertex(add(pts[i], mul(dir, r)), dir, [s / sides, v]));
    }
    rings.push(ring);
  }
  for (let i = 0; i < rings.length - 1; i++) for (let s = 0; s < sides; s++) {
    const a = rings[i][s], b = rings[i][s + 1], c = rings[i + 1][s + 1], d = rings[i + 1][s];
    part.tri(a, c, b); part.tri(a, d, c);
  }
}

/** Curve from start along dir, bending toward `pull` and wobbling a little. */
function limb(r, start, dir, length, segs, { pull = [0, 1, 0], bend = 0, wobble = 0.08 } = {}) {
  const pts = [start]; let d = norm(dir), p = start;
  for (let i = 0; i < segs; i++) {
    d = norm(add(lerp3(d, norm(pull), bend), [r.range(-wobble, wobble), r.range(-wobble, wobble) * 0.5, r.range(-wobble, wobble)]));
    p = add(p, mul(d, length / segs)); pts.push(p);
  }
  return pts;
}
const taper = (n, a, b) => Array.from({ length: n }, (_, i) => a + (b - a) * (i / (n - 1)));

/**
 * Leaf card: two crossed quads ("double billboard") centred at c, w × h, facing
 * `facing` (horizontal direction) and tilted. Normals blend from the crown centre
 * outward. UVs come from one of the four atlas cells.
 */
function card(part, c, w, h, facing, tilt, cell, crown, { anchorBottom = false, roll = 0 } = {}) {
  const f = norm([facing[0], 0, facing[2]]), side = norm(cross([0, 1, 0], f));
  const u0 = (cell % 2) * 0.5 + 0.004, v0 = Math.floor(cell / 2) * 0.5 + 0.004, du = 0.492;
  for (const k of [0, 1]) {
    let right = k ? f : side;
    let up = [0, 1, 0];
    // tilt the card about its right axis, then roll it a little for variety
    const fwd = norm(cross(right, up));
    up = norm(add(mul(up, Math.cos(tilt)), mul(fwd, Math.sin(tilt))));
    right = norm(add(mul(right, Math.cos(roll)), mul(up, Math.sin(roll))));
    up = norm(cross(fwd, right)); if (up[1] < 0) up = mul(up, -1);
    const o = anchorBottom ? c : sub(c, mul(up, h / 2));
    const corners = [[-0.5, 0], [0.5, 0], [0.5, 1], [-0.5, 1]].map(([x, y]) => add(add(o, mul(right, x * w)), mul(up, y * h)));
    const uvs = [[u0, v0 + du], [u0 + du, v0 + du], [u0 + du, v0], [u0, v0]];
    const ids = corners.map((p, j) => part.vertex(p, norm(add(norm(sub(p, crown)), [0, 0.35, 0])), uvs[j]));
    part.tri(ids[0], ids[1], ids[2]); part.tri(ids[0], ids[2], ids[3]);
  }
}

/** Sloped skirt card for conifers: from the trunk at `top` outward and down to radius. */
function skirt(part, top, yaw, radius, drop, width, cell, crown) {
  const out = [Math.cos(yaw), 0, Math.sin(yaw)], side = [-out[2], 0, out[0]];
  const tip = add(add(top, mul(out, radius)), [0, -drop, 0]);
  const u0 = (cell % 2) * 0.5 + 0.004, v0 = Math.floor(cell / 2) * 0.5 + 0.004, du = 0.492;
  const corners = [add(top, mul(side, -width * 0.18)), add(top, mul(side, width * 0.18)), add(tip, mul(side, width / 2)), add(tip, mul(side, -width / 2))];
  const uvs = [[u0, v0 + du], [u0 + du, v0 + du], [u0 + du, v0], [u0, v0]];
  const ids = corners.map((p, j) => part.vertex(p, norm(add(norm(sub(p, crown)), [0, 0.5, 0])), uvs[j]));
  part.tri(ids[0], ids[1], ids[2]); part.tri(ids[0], ids[2], ids[3]);
}

const yawDir = a => [Math.cos(a), 0, Math.sin(a)];

/** Extra cards on an ellipsoid shell around the crown centre, facing outward. */
function fillCrown(part, r, centre, radii, count, size) {
  for (let i = 0; i < count; i++) {
    const yaw = i * 2.39996 + r.range(-0.3, 0.3), el = r.range(-0.35, 0.75), d = r.range(0.45, 0.75);
    const p = [centre[0] + Math.cos(yaw) * Math.cos(el) * radii[0] * d, centre[1] + Math.sin(el) * radii[1] * d, centre[2] + Math.sin(yaw) * Math.cos(el) * radii[2] * d];
    card(part, p, size * r.range(0.85, 1.1), size * r.range(0.85, 1.05), yawDir(yaw), el * 0.5, i % 4, centre, { roll: r.range(-0.35, 0.35) });
  }
}

// ---------------------------------------------------------------- species
const species = [
  {
    id: 'leafcard_young_tree', name: 'Leaf-Card Young Tree', nameJa: '若木（Y 字）', seed: 7101, height: 4.2,
    description: 'Young broadleaf tree: slim orange-brown trunk forking into a Y, with bright green leaf-cluster cards along the branches.',
    tags: ['young', 'broadleaf', 'deciduous', 'park', 'garden', 'y-shaped'],
    leaf: { kind: 'cluster', twigs: 5, spread: 1.7, leaves: 170, len: [20, 30], width: 0.42, mass: [92, 78, 108], twigWidth: 4, twig: '#b4561c', twigLight: '#e08a3c', palette: [[95, 62, 42], [88, 66, 48], [102, 55, 36]] },
    bark: { base: [24, 62, 42], contrast: 16, cracks: 10 },
    build(r, wood, leaves) {
      const crown = [0, 3.1, 0];
      const stem = limb(r, [0, 0, 0], [0.04, 1, 0], 1.7, 3, { wobble: 0.04 });
      tube(wood, stem, taper(4, 0.13, 0.09), 6, { flare: 0.35 });
      const fork = stem.at(-1), tips = [];
      for (const s of [-1, 1]) {
        const arm = limb(r, add(fork, [0, -0.12, 0]), [s * 0.55, 1, s * 0.15], 2.2, 3, { pull: [s * 0.3, 1, 0], bend: 0.15, wobble: 0.06 });
        tube(wood, arm, taper(arm.length, 0.08, 0.03), 5);
        const twig = limb(r, arm[1], [s * 1, 0.6, -s * 0.6], 1.0, 2, { wobble: 0.1 });
        tube(wood, twig, taper(twig.length, 0.04, 0.015), 4);
        tips.push(arm.at(-1), arm[2], twig.at(-1));
      }
      tips.forEach((p, i) => card(leaves, add(p, [0, 0.2, 0]), 1.7, 1.6, norm(sub(p, [0, p[1], 0])), r.range(-0.2, 0.3), i % 4, crown, { roll: r.range(-0.3, 0.3) }));
      fillCrown(leaves, r, crown, [1.35, 1.0, 1.25], 6, 1.6);
      card(leaves, [0, 4.1, 0], 1.6, 1.3, [1, 0, 0.3], 0, 0, crown);
    }
  },
  {
    id: 'leafcard_tall_tree', name: 'Leaf-Card Tall Tree', nameJa: '高い広葉樹', seed: 7202, height: 6.5,
    description: 'Tall broadleaf tree: straight orange-brown trunk with branches spiralling up and leafy cards drooping from their ends.',
    tags: ['tall', 'broadleaf', 'deciduous', 'forest', 'park'],
    leaf: { kind: 'cluster', twigs: 6, spread: 1.8, leaves: 180, len: [18, 28], width: 0.4, mass: [95, 80, 112], twigWidth: 3.5, twig: '#a24e1d', twigLight: '#d97c36', palette: [[100, 58, 40], [92, 62, 46], [110, 50, 34]] },
    bark: { base: [22, 58, 38], contrast: 18, cracks: 14 },
    build(r, wood, leaves) {
      const crown = [0, 4.3, 0];
      const trunk = limb(r, [0, 0, 0], [0, 1, 0], 5.6, 6, { wobble: 0.03 });
      tube(wood, trunk, taper(trunk.length, 0.16, 0.04), 6, { flare: 0.4 });
      for (let i = 0; i < 7; i++) {
        const at = trunk[2 + Math.floor(i * 0.6)], yaw = i * 2.4, len = 1.5 - i * 0.12;
        const br = limb(r, at, add(yawDir(yaw), [0, 0.9, 0]), len, 2, { pull: [0, 1, 0], bend: 0.1, wobble: 0.07 });
        tube(wood, br, taper(br.length, 0.055, 0.02), 4);
        card(leaves, add(br.at(-1), [0, 0.05, 0]), 1.8 - i * 0.07, 1.9, yawDir(yaw), r.range(0.1, 0.35), i % 4, crown, { roll: r.range(-0.3, 0.3) });
      }
      fillCrown(leaves, r, crown, [1.25, 1.9, 1.25], 8, 1.7);
      card(leaves, add(trunk.at(-1), [0, -0.1, 0]), 1.6, 1.7, [1, 0, 0.5], 0, 1, crown);
    }
  },
  {
    id: 'leafcard_old_tree', name: 'Leaf-Card Old Gnarled Tree', nameJa: '老木（ねじれた幹）', seed: 7303, height: 4.6,
    description: 'Old gnarled tree: thick twisting beige-grey trunk with flared roots, heavy limbs leaning out and yellow-green leaf clusters at their tips.',
    tags: ['old', 'gnarled', 'ancient', 'broadleaf', 'forest', 'fantasy', 'landmark'],
    leaf: { kind: 'cluster', twigs: 5, spread: 1.8, leaves: 150, len: [22, 34], width: 0.48, mass: [95, 80, 110], twigWidth: 3.5, twig: '#6e5a3e', twigLight: '#9a8460', palette: [[78, 70, 46], [86, 66, 52], [70, 72, 40]] },
    bark: { base: [36, 24, 58], contrast: 22, cracks: 26, rings: 8 },
    build(r, wood, leaves) {
      const crown = [0.15, 3.7, 0];
      const trunk = []; for (let i = 0; i <= 5; i++) { const t = i / 5; trunk.push([Math.sin(t * 2.6) * 0.32, t * 2.6, Math.cos(t * 2.2) * 0.16 - 0.16]); }
      tube(wood, trunk, [0.5, 0.41, 0.35, 0.31, 0.28, 0.25], 7, { flare: 0.7 });
      for (let i = 0; i < 5; i++) { // roots creeping over the ground
        const yaw = i * 1.26 + 0.4, root = [add([0, 0.45, 0], mul(yawDir(yaw), 0.2)), add([0, 0.16, 0], mul(yawDir(yaw), 0.62)), add([0, -0.06, 0], mul(yawDir(yaw), 0.95))];
        tube(wood, root, [0.22, 0.13, 0.07], 5);
      }
      const limbs = [[0.8, 0.9, 0.1], [-0.9, 0.8, 0.3], [0.1, 0.9, -0.9], [0.2, 1, 0.9], [-0.5, 1.2, -0.4]];
      const tips = [];
      limbs.forEach((d, i) => {
        const br = limb(r, trunk[4 - (i % 2)], d, 1.9, 3, { pull: [d[0], 0.5, d[2]], bend: 0.05, wobble: 0.12 });
        tube(wood, br, taper(br.length, 0.17, 0.05), 5);
        tips.push(br.at(-1), br[2]);
      });
      tips.forEach((p, i) => card(leaves, add(p, [0, 0.25, 0]), i % 2 ? 1.9 : 2.4, i % 2 ? 1.7 : 2.1, norm(sub(p, [crown[0], p[1], crown[2]])), r.range(0.1, 0.4), i % 4, crown, { roll: r.range(-0.4, 0.4) }));
      fillCrown(leaves, r, crown, [2.0, 1.1, 1.9], 6, 2.2);
      card(leaves, add(trunk.at(-1), [0, 0.9, 0]), 2.2, 1.7, [1, 0, 0], 0, 2, crown);
    }
  },
  {
    id: 'leafcard_column_tree', name: 'Leaf-Card Columnar Tree', nameJa: '縦長の木（段重ね）', seed: 7404, height: 6.2,
    description: 'Narrow upright tree: straight trunk wrapped in four stacked tiers of leaf cards that form a tall, slightly tapering column.',
    tags: ['columnar', 'upright', 'narrow', 'broadleaf', 'avenue', 'hedge-row'],
    leaf: { kind: 'cluster', twigs: 4, spread: 1.5, leaves: 190, len: [18, 27], width: 0.44, mass: [92, 84, 116], twigWidth: 3, twig: '#5d4a32', twigLight: '#8a734f', palette: [[98, 52, 36], [90, 56, 44], [105, 48, 30]] },
    bark: { base: [30, 22, 44], contrast: 18, cracks: 18 },
    build(r, wood, leaves) {
      const crown = [0, 3.8, 0];
      const trunk = limb(r, [0, 0, 0], [0, 1, 0], 5.8, 5, { wobble: 0.02 });
      tube(wood, trunk, taper(trunk.length, 0.16, 0.05), 6, { flare: 0.3 });
      const tiers = 5;
      for (let t = 0; t < tiers; t++) {
        const y = 1.2 + t * 1.0, w = 2.3 - t * 0.25;
        for (let k = 0; k < 4; k++) {
          const yaw = k * Math.PI / 2 + t * 0.45 + r.range(-0.15, 0.15);
          card(leaves, add([0, y, 0], mul(yawDir(yaw), w * 0.2)), w, w * 0.95, yawDir(yaw), 0.4, (k + t) % 4, crown, { anchorBottom: true, roll: r.range(-0.15, 0.15) });
        }
      }
      card(leaves, [0, 6.1, 0], 1.2, 1.3, [1, 0, 0.4], 0, 1, crown);
    }
  },
  {
    id: 'leafcard_fir', name: 'Leaf-Card Fir', nameJa: 'モミ（針葉樹）', seed: 7505, height: 6.8,
    description: 'Fir tree: thin trunk with five tiers of sloping needle-frond cards arranged like stacked pyramids, narrowing to a pointed top.',
    tags: ['fir', 'pine', 'conifer', 'evergreen', 'forest', 'christmas', 'mountain'],
    leaf: { kind: 'frond', shoots: 18, reach: 112, needle: 16, twig: '#5b3d24', palette: [[118, 52, 24], [124, 48, 30], [110, 56, 34], [130, 40, 22]] },
    bark: { base: [22, 40, 30], contrast: 16, cracks: 20 },
    build(r, wood, leaves) {
      const crown = [0, 3.4, 0];
      const trunk = limb(r, [0, 0, 0], [0, 1, 0], 6.8, 5, { wobble: 0.01 });
      tube(wood, trunk, taper(trunk.length, 0.15, 0.03), 6, { flare: 0.3 });
      const tiers = 6;
      for (let t = 0; t < tiers; t++) {
        const f = t / (tiers - 1), y = 1.5 + f * 4.7, radius = 2.45 - f * 1.55, n = 9 - Math.round(f * 3);
        const width = (Math.PI * 2 * radius / n) * 1.55;
        for (let k = 0; k < n; k++) skirt(leaves, [0, y, 0], k * Math.PI * 2 / n + t * 0.45 + r.range(-0.08, 0.08), radius, radius * 0.72, width, (k + t) % 4, crown);
      }
      card(leaves, [0, 6.1, 0], 0.9, 1.1, [1, 0, 0.3], 0, 0, crown, { anchorBottom: true });
    }
  }
];

// ---------------------------------------------------------------- assembly
async function paintTextures() {
  const playwright = await globalModule('playwright'), chromium = playwright.chromium || playwright.default.chromium;
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await browser.newPage(); await page.setContent(painter); await page.waitForFunction(() => window.ready);
  const out = {};
  for (const s of species) out[s.id] = await page.evaluate(spec => window.paint(spec), { seed: s.seed, leaf: s.leaf, bark: s.bark });
  await browser.close();
  return out;
}

const sharpMod = await globalModule('sharp'), sharp = sharpMod.default || sharpMod;
const png = async dataUrl => Buffer.from(await sharp(Buffer.from(dataUrl.split(',')[1], 'base64')).png({ palette: true, quality: 90, effort: 10, compressionLevel: 9 }).toBuffer());
const jpg = async dataUrl => Buffer.from(await sharp(Buffer.from(dataUrl.split(',')[1], 'base64')).jpeg({ quality: 82, mozjpeg: true }).toBuffer());

function primitive(doc, buffer, part, material) {
  const f32 = (arr, type) => doc.createAccessor().setType(type).setArray(new Float32Array(arr)).setBuffer(buffer);
  const idx = doc.createAccessor().setType('SCALAR').setArray(part.p.length / 3 > 65535 ? new Uint32Array(part.i) : new Uint16Array(part.i)).setBuffer(buffer);
  return doc.createPrimitive().setAttribute('POSITION', f32(part.p, 'VEC3')).setAttribute('NORMAL', f32(part.n, 'VEC3')).setAttribute('TEXCOORD_0', f32(part.uv, 'VEC2')).setIndices(idx).setMaterial(material);
}

export async function build(outDir) {
  await fs.mkdir(outDir, { recursive: true });
  const textures = await paintTextures(), io = new NodeIO(), results = [];
  for (const s of species) {
    const r = rng(s.seed), wood = new Part(), leaves = new Part();
    s.build(r, wood, leaves);
    const doc = new Document(), buffer = doc.createBuffer();
    doc.getRoot().getAsset().generator = 'NEXUS leafcard-trees (scripts/leafcard-trees/build.mjs)';
    const barkTex = doc.createTexture('bark').setImage(await jpg(textures[s.id].bark)).setMimeType('image/jpeg');
    const leafTex = doc.createTexture('leaves').setImage(await png(textures[s.id].leaves)).setMimeType('image/png');
    const barkMat = doc.createMaterial('bark').setBaseColorTexture(barkTex).setRoughnessFactor(0.95).setMetallicFactor(0);
    const leafMat = doc.createMaterial('leaves').setBaseColorTexture(leafTex).setAlphaMode('MASK').setAlphaCutoff(0.5).setDoubleSided(true).setRoughnessFactor(0.8).setMetallicFactor(0);
    const mesh = doc.createMesh(s.id).addPrimitive(primitive(doc, buffer, wood, barkMat)).addPrimitive(primitive(doc, buffer, leaves, leafMat));
    const node = doc.createNode(s.id).setMesh(mesh);
    doc.createScene(s.id).addChild(node);
    const glb = Buffer.from(await io.writeBinary(doc));
    const file = path.join(outDir, `${s.id}.glb`);
    await fs.writeFile(file, glb);
    results.push({ ...s, file, triangles: wood.triangles + leaves.triangles, trunkTriangles: wood.triangles, cards: leaves.triangles / 2, bytes: glb.length });
  }
  return results;
}

export { species };

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const outDir = path.resolve(process.argv[2] ?? path.join(root, 'assets/leafcard-trees'));
  for (const t of await build(outDir)) console.log(`${t.id.padEnd(24)} ${String(t.triangles).padStart(4)} tris (trunk ${t.trunkTriangles}, ${t.cards} card quads)  ${(t.bytes / 1024).toFixed(0)} KB`);
}
