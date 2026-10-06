import * as THREE from "/vendor/three/build/three.module.js";
import { OrbitControls } from "/vendor/three/examples/jsm/controls/OrbitControls.js";
import { GLTFLoader } from "/vendor/three/examples/jsm/loaders/GLTFLoader.js";

const $ = (id) => document.getElementById(id);
let selectedType = "all";
let savedOnly = false;
let selectedAsset;
let scene, camera, renderer, controls, model, gridHelper, animation;

async function get(url, options) { const response = await fetch(url, options); const data = await response.json(); if (!response.ok) throw new Error(data.error || "Request failed"); return data; }
function badge(text, cc0 = false) { return `<span class="badge ${cc0 ? "cc0" : ""}">${text}</span>`; }
function favorites() { try { return JSON.parse(localStorage.getItem("nexus:favorites") || "[]"); } catch { return []; } }
function isFavorite(id) { return favorites().includes(id); }
function toggleFavorite(id) { const next = favorites().filter((item) => item !== id); if (!isFavorite(id)) next.push(id); localStorage.setItem("nexus:favorites", JSON.stringify(next)); updateSavedButton(); loadAssets(); }
function updateSavedButton() { $("savedFilter").textContent = `${savedOnly ? "♥" : "♡"} SAVED`; $("savedFilter").classList.toggle("active", savedOnly); if (selectedAsset) $("saveDetail").textContent = `${isFavorite(selectedAsset.id) ? "♥" : "♡"} ${isFavorite(selectedAsset.id) ? "SAVED" : "SAVE"}`; }
function renderCards(assets) {
  if (savedOnly) assets = assets.filter((asset) => isFavorite(asset.id));
  $("count").textContent = `${assets.length} asset${assets.length === 1 ? "" : "s"}`;
  $("grid").innerHTML = assets.length ? assets.map((asset) => `<article class="card" data-id="${asset.id}"><div class="thumb" style="background-image:url('${asset.thumbnail || ""}')"></div><div class="card-body"><div class="card-title"><h3>${asset.title}</h3><button class="save-button ${isFavorite(asset.id) ? "saved" : ""}" data-save="${asset.id}">${isFavorite(asset.id) ? "♥" : "♡"}</button></div><div class="provider">${asset.provider}</div><div class="badges">${badge(asset.format)}${badge(asset.license, asset.license.toLowerCase().includes("cc0"))}${asset.downloadable ? badge("DOWNLOAD") : ""}</div></div></article>`).join("") : '<div class="empty">No assets match these filters.</div>';
  document.querySelectorAll(".card").forEach((card) => card.addEventListener("click", () => openDetail(card.dataset.id)));
  document.querySelectorAll("[data-save]").forEach((button) => button.addEventListener("click", (event) => { event.stopPropagation(); toggleFavorite(button.dataset.save); }));
}
async function loadAssets() {
  const params = new URLSearchParams({ q: $("query").value, type: selectedType, provider: $("provider").value, free: $("free").checked, cc0: $("cc0").checked, glb: $("glb").checked });
  try { renderCards((await get(`/api/search?${params}`)).assets); } catch (error) { $("grid").innerHTML = `<div class="empty">${error.message}</div>`; }
}
function initViewer(asset) {
  const host = $("viewer"); host.innerHTML = "";
  scene = new THREE.Scene(); scene.background = new THREE.Color(0x0a0b0d);
  camera = new THREE.PerspectiveCamera(45, host.clientWidth / host.clientHeight, .01, 1000); camera.position.set(2.4, 1.6, 3.2);
  renderer = new THREE.WebGLRenderer({ antialias: true }); renderer.setPixelRatio(Math.min(devicePixelRatio, 2)); renderer.setSize(host.clientWidth, host.clientHeight); renderer.shadowMap.enabled = true; host.appendChild(renderer.domElement);
  scene.add(new THREE.HemisphereLight(0xddeeff, 0x222222, 2)); const key = new THREE.DirectionalLight(0xffffff, 3); key.position.set(3, 5, 2); key.castShadow = true; scene.add(key);
  gridHelper = new THREE.GridHelper(10, 20, 0x37403a, 0x202522); scene.add(gridHelper);
  controls = new OrbitControls(camera, renderer.domElement); controls.enableDamping = true; controls.autoRotate = true; controls.autoRotateSpeed = 1.5;
  if (asset.modelUrl) new GLTFLoader().load(asset.modelUrl, (gltf) => { model = gltf.scene; model.traverse((node) => { if (node.isMesh) { node.castShadow = true; node.receiveShadow = true; } }); scene.add(model); }, undefined, () => addPlaceholder()); else addPlaceholder();
  const resize = () => { if (!renderer) return; camera.aspect = host.clientWidth / host.clientHeight; camera.updateProjectionMatrix(); renderer.setSize(host.clientWidth, host.clientHeight); }; window.addEventListener("resize", resize, { once: true });
  const loop = () => { animation = requestAnimationFrame(loop); controls?.update(); renderer.render(scene, camera); }; loop();
}
function addPlaceholder() { const group = new THREE.Group(); const body = new THREE.Mesh(new THREE.IcosahedronGeometry(.85, 1), new THREE.MeshStandardMaterial({ color: 0xb7d35a, roughness: .7, flatShading: true })); body.position.y = .9; group.add(body); scene.add(group); model = group; }
async function openDetail(id) {
  selectedAsset = await get(`/api/assets/${id}`); $("detailProvider").textContent = `${selectedAsset.provider} / ${selectedAsset.type.toUpperCase()}`; $("detailTitle").textContent = selectedAsset.title; $("detailBadges").innerHTML = badge(selectedAsset.format) + badge(selectedAsset.license, selectedAsset.license.toLowerCase().includes("cc0")); $("source").href = selectedAsset.sourceUrl || "#"; $("facts").innerHTML = `<dt>LICENSE</dt><dd>${selectedAsset.license}</dd><dt>AUTHOR</dt><dd>${selectedAsset.author}</dd><dt>TRIANGLES</dt><dd>${selectedAsset.polygonCount || "—"}</dd><dt>FILE SIZE</dt><dd>${selectedAsset.fileSize || "—"}</dd>`; $("detailTags").textContent = selectedAsset.tags.map((tag) => `#${tag}`).join("  "); $("usedBy").textContent = selectedAsset.usedBy?.length ? selectedAsset.usedBy.join(" · ") : "No registered projects yet."; $("notice").textContent = ""; updateSavedButton(); $("detail").showModal(); initViewer(selectedAsset);
}
async function copyCode() { const path = `/assets/models/${selectedAsset.id}.glb`; await navigator.clipboard.writeText(`const loader = new GLTFLoader();\n\nloader.load(\n  '${path}',\n  (gltf) => {\n    gltf.scene.scale.set(1, 1, 1);\n    gltf.scene.position.set(0, 0, 0);\n    gltf.scene.traverse((node) => { if (node.isMesh) node.castShadow = true; });\n    scene.add(gltf.scene);\n  }\n);`); $("notice").textContent = "Three.js loader snippet copied."; }
async function downloadAsset() { try { const result = await get(`/api/assets/${selectedAsset.id}/download`, { method: "POST" }); $("notice").textContent = result.cached ? "Already in NEXUS Library." : `Downloaded to ${result.localPath}`; } catch (error) { $("notice").textContent = error.message; } }
async function sendToProject() { const projects = (await get("/api/projects")).projects; const project = prompt(`Send ${selectedAsset.title} to which project?\n\n${projects.map((p) => p.name).join("\n")}`, projects[0]?.name || ""); if (!project) return; try { const result = await get(`/api/assets/${selectedAsset.id}/send`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ project }) }); $("notice").textContent = `Sent to ${result.project}: ${result.filename}`; } catch (error) { $("notice").textContent = error.message; } }
async function importLocal(event) { const file = event.target.files[0]; if (!file) return; $("importStatus").textContent = `Importing ${file.name}…`; try { const bytes = new Uint8Array(await file.arrayBuffer()); let binary = ""; for (let i = 0; i < bytes.length; i += 0x8000) binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000)); const result = await get("/api/import", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ filename: file.name, name: file.name.replace(/\.(glb|gltf|png|jpe?g|webp)$/i, ""), contentBase64: btoa(binary) }) }); $("importStatus").textContent = `Imported ${result.title} into NEXUS Library.`; await loadAssets(); } catch (error) { $("importStatus").textContent = error.message; } finally { event.target.value = ""; } }
document.querySelectorAll("#types .chip").forEach((button) => button.addEventListener("click", () => { document.querySelector(".chip.active").classList.remove("active"); button.classList.add("active"); selectedType = button.dataset.type; loadAssets(); }));
["query", "free", "cc0", "glb", "provider"].forEach((id) => $(id).addEventListener(id === "query" ? "input" : "change", loadAssets));
$("importFile").addEventListener("change", importLocal);
$("savedFilter").addEventListener("click", () => { savedOnly = !savedOnly; updateSavedButton(); loadAssets(); });
$("saveDetail").addEventListener("click", () => { toggleFavorite(selectedAsset.id); });
$("close").addEventListener("click", () => { $("detail").close(); cancelAnimationFrame(animation); }); $("download").addEventListener("click", downloadAsset); $("copyCode").addEventListener("click", copyCode); $("send").addEventListener("click", sendToProject); $("rotate").addEventListener("click", () => { controls.autoRotate = !controls.autoRotate; $("rotate").textContent = `AUTO ROTATE: ${controls.autoRotate ? "ON" : "OFF"}`; }); $("gridToggle").addEventListener("click", () => { gridHelper.visible = !gridHelper.visible; $("gridToggle").textContent = `GRID: ${gridHelper.visible ? "ON" : "OFF"}`; });
document.addEventListener("keydown", (event) => { if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") { event.preventDefault(); $("query").focus(); } });
const providers = [...new Set((await get("/api/assets")).assets.map((asset) => asset.provider))]; providers.forEach((name) => $("provider").insertAdjacentHTML("beforeend", `<option value="${name.toLowerCase()}">${name}</option>`)); loadAssets();
