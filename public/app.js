import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { searchAssets } from './search.js';
const $ = id => document.getElementById(id);
const base = new URL('./', location.href);
let assets = [], selected, savedOnly = false, disposeViewer = () => {};
let toggleRotate = () => {}, toggleGrid = () => {}, toggleWire = () => {}, toggleBounds = () => {};
const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const favorites = () => { try { const ids=JSON.parse(localStorage.getItem('nexus:favorites') || '[]'); return Array.isArray(ids) ? ids : []; } catch { return []; } };
const assetUrl = asset => asset.previewUrl || new URL(asset.path, base).href;
function save(id) { const ids = favorites(); localStorage.setItem('nexus:favorites',JSON.stringify(ids.includes(id) ? ids.filter(x=>x!==id) : [...ids,id])); render(); }
function render() {
  let results = searchAssets(assets, {query:$('query').value,category:$('category').value,format:$('format').value,license:$('license').value,tags:$('tags').value,maxTriangles:$('maxTriangles').value,animated:$('animated').value === '' ? undefined : $('animated').value === 'true'});
  if (savedOnly) results = results.filter(a=>favorites().includes(a.id));
  $('count').textContent = results.length + ' assets';
  $('grid').innerHTML = results.map(a=>'<article class="card" data-id="'+escape(a.id)+'"><div class="thumb">'+(a.thumbnail ? '<img loading="lazy" src="'+escape(new URL(a.thumbnail.replace(/^\//,''),base).href)+'" style="width:100%;height:100%;object-fit:contain" alt="">' : '<span style="display:block;padding:55px;text-align:center">◇<br>3D PREVIEW</span>')+'</div><div class="card-body"><h3>'+escape(a.name)+'</h3><p class="provider">'+escape(a.category)+'</p><div class="badges"><span class="badge">'+escape(a.format)+'</span><span class="badge">'+escape(a.license || 'UNKNOWN')+'</span><span class="badge">'+(a.triangles == null ? '—' : a.triangles.toLocaleString())+' triangles</span></div><p class="provider">'+escape((a.tags || []).join(' · '))+'</p></div></article>').join('') || '<p class="empty">No matching assets.</p>';
  document.querySelectorAll('[data-id]').forEach(card=>card.onclick=()=>openAsset(assets.find(a=>a.id===card.dataset.id)));
}
function viewer(asset) {
  disposeViewer(); const host=$('viewer'); host.replaceChildren();
  if (['PNG','JPG','JPEG','WEBP'].includes(asset.format.toUpperCase())) { const img=document.createElement('img'); img.src=new URL(asset.path,base).href; img.style='width:100%;height:430px;object-fit:contain'; host.append(img); return; }
  if (!['GLB','GLTF'].includes(asset.format.toUpperCase())) { host.textContent='Stored file. Convert to GLB to preview.'; return; }
  const scene=new THREE.Scene(); scene.background=new THREE.Color(0x0a0b0d);
  const camera=new THREE.PerspectiveCamera(45,1,.01,10000); camera.position.set(3,2,4);
  const renderer=new THREE.WebGLRenderer({antialias:true}); host.append(renderer.domElement);
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));
  const controls=new OrbitControls(camera,renderer.domElement); controls.enableDamping=true; controls.autoRotate=true;
  scene.add(new THREE.HemisphereLight(0xffffff,0x444444,3));
  const light=new THREE.DirectionalLight(0xffffff,3); light.position.set(3,5,4); scene.add(light);
  const grid=new THREE.GridHelper(10,20); scene.add(grid);
  let model, box, stopped=false;
  toggleRotate=()=>controls.autoRotate=!controls.autoRotate;
  toggleGrid=()=>grid.visible=!grid.visible;
  toggleWire=()=>model?.traverse(n=>{if(n.isMesh) for(const m of [].concat(n.material)) m.wireframe=!m.wireframe;});
  toggleBounds=()=>{if(box) box.visible=!box.visible;};
  new GLTFLoader().load(new URL(asset.path,base).href,gltf=>{
    if(stopped) return; model=gltf.scene; scene.add(model);
    const bounds=new THREE.Box3().setFromObject(model), size=bounds.getSize(new THREE.Vector3()), center=bounds.getCenter(new THREE.Vector3());
    const radius=Math.max(size.x,size.y,size.z,.1); controls.target.copy(center); camera.position.copy(center).add(new THREE.Vector3(radius*1.5,radius,radius*1.5)); camera.far=radius*100+100; camera.updateProjectionMatrix(); controls.update();
    box=new THREE.Box3Helper(bounds,0xd8ff55); box.visible=false; scene.add(box);
  },undefined,error=>{$('notice').textContent='Model could not be loaded: '+error.message;});
  const observer=new ResizeObserver(()=>{const w=host.clientWidth,h=Math.max(host.clientHeight,300); camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h);}); observer.observe(host);
  renderer.setAnimationLoop(()=>{controls.update();renderer.render(scene,camera);});
  disposeViewer=()=>{stopped=true;observer.disconnect();renderer.setAnimationLoop(null);controls.dispose();scene.traverse(n=>{n.geometry?.dispose();for(const m of [].concat(n.material || [])) m.dispose();});renderer.dispose();};
}
function openAsset(asset) {
  selected=asset; $('name').textContent=asset.name; $('source').textContent=asset.source || 'GitHub NEXUS'; $('assetTags').textContent=(asset.tags || []).join(' · ');
  $('facts').innerHTML=Object.entries({License:asset.license || 'UNKNOWN',Author:asset.author || '—',Format:asset.format,Size:asset.size+' bytes',Triangles:asset.triangles ?? '—',Materials:asset.materials ?? '—',Animations:(asset.animations || []).length}).map(([k,v])=>'<dt>'+escape(k)+'</dt><dd>'+escape(v)+'</dd>').join('');
  $('notice').textContent=''; $('download').href=assetUrl(asset); $('download').target='_blank'; $('detail').showModal(); viewer(asset);
}
async function copy(text) { try { await navigator.clipboard.writeText(text); $('notice').textContent='Copied.'; } catch { $('notice').textContent=text; } }
$('copyUrl').onclick=()=>copy(assetUrl(selected));
$('copyPath').onclick=()=>copy(selected.path);
$('copyCode').onclick=()=>copy("import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';\nconst loader = new GLTFLoader();\nloader.load("+JSON.stringify(assetUrl(selected))+", (gltf) => { scene.add(gltf.scene); });");
$('favorite').onclick=()=>save(selected.id);
$('rotate').onclick=()=>toggleRotate(); $('gridToggle').onclick=()=>toggleGrid(); $('wire').onclick=()=>toggleWire(); $('bounds').onclick=()=>toggleBounds();
$('close').onclick=()=>$('detail').close(); $('detail').addEventListener('close',()=>disposeViewer());
$('saved').onclick=()=>{savedOnly=!savedOnly;$('saved').classList.toggle('active',savedOnly);render();};
for(const id of ['query','category','format','license','maxTriangles','animated','tags']) $(id).addEventListener('input',render);
document.addEventListener('keydown',e=>{if((e.metaKey||e.ctrlKey)&&e.key==='k'){e.preventDefault();$('query').focus();}});
try {
  const response=await fetch(new URL('data/assets.json',base)); if(!response.ok) throw new Error('Index HTTP '+response.status);
  assets=await response.json(); $('total').textContent=assets.length;
  for(const key of ['category','format','license']) for(const value of [...new Set(assets.map(a=>a[key]).filter(Boolean))].sort()) {const option=document.createElement('option');option.value=value;option.textContent=value;$ (key).append(option);}
  render();
} catch(error) {$('count').textContent='Asset index unavailable';$('grid').textContent=error.message;}
