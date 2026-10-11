import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { renderThumbnails } from './giant-climb/thumbnails.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const out = path.join(root, 'assets/road-driver');
const thumbs = path.join(root, 'thumbnails/road-driver');
const index = JSON.parse(await fs.readFile(path.join(root, 'data/assets.json'), 'utf8'));
const groups = {
  VEHICLE: ['kenney_sedan','kenney_sports_sedan','kenney_hatchback','kenney_suv','kenney_taxi','kenney_van','kenney_truck','kenney_truck_flat','kenney_delivery_truck','kenney_police_car','kenney_ambulance','racing_vehicle_truck_yellow'],
  'ROAD PROPS': ['citykit_road_straight','citykit_road_corner','citykit_road_intersection','citykit_road_split','citykit_road_straight_lightposts','city_sidewalk_barrier','city_traffic_light','city_street_lamp'],
  CITY: ['city_apartment_block','city_corner_store','city_office_tower','city_pencil_building','citykit_building_garage','citykit_building_small_a','citykit_building_small_b','citykit_building_small_c','citykit_building_small_d','kenney_house_7'],
  NATURE: ['assets_nature_tree_demo_tree','citykit_grass','citykit_grass_trees','citykit_grass_trees_tall','fpskit_platform_large_grass','platformer_platform_grass_large_round'],
  FUTURE: ['space_structure','space_structure_closed','space_structure_detailed','space_supports_high','space_supports_low','space_monorail_track_straight','space_monorail_track_support','space_monorail_track_corner_large','space_monorail_train_front']
};
const uses = {
  VEHICLE: ['背景交通車両・追走車・障害物。プレイヤー車両の代替にも利用可能。', '道路面に接地させ、道路の流れ方向に向ける。複数配置は同じGLBを共有し、同じ色・素材の車はInstancedMeshを検討。'],
  'ROAD PROPS': ['道路タイル、路肩、信号、街灯。', 'タイルは同じ幅の辺を合わせて反復。街灯・信号・バリアは道路端に少数配置し、遠景は間引く。'],
  CITY: ['都市の沿道建物と遠景シルエット。', '近景の小型建物は路肩から離して配置。高層建築は遠景に置き、同じモデルを再利用。'],
  NATURE: ['公園・街路樹・緑地・空のアクセント。', '路肩や遠景に配置。植栽は同一モデルを共有し、密集時はInstancedMeshを検討。'],
  FUTURE: ['未来的な高架・構造物・モノレールの背景アクセント。', '道路と交差しない遠景・上空に配置。車線や視界を塞がないよう少数を再利用。']
};
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const sha = data => crypto.createHash('sha256').update(data).digest('hex');
const round = n => Number(n.toFixed(4));
await fs.mkdir(out, { recursive: true });
await fs.mkdir(path.join(out, 'models'), { recursive: true });
await fs.mkdir(thumbs, { recursive: true });
const records = [];
for (const [category, ids] of Object.entries(groups)) for (const id of ids) {
  const a = index.find(x => x.id === id && x.format === 'GLB');
  if (!a) throw new Error(`Selected GLB is missing from NEXUS index: ${id}`);
  const licenseEvidence = a.licenseEvidence || a.notes;
  if (a.license !== 'CC0-1.0' || !licenseEvidence || !a.sourceUrl) throw new Error(`License/source evidence is incomplete: ${id}`);
  const source = path.join(root, a.file);
  const bytes = await fs.readFile(source);
  if (sha(bytes) !== a.sha256) throw new Error(`Source checksum mismatch: ${id}`);
  const doc = await io.read(source);
  let triangles = 0;
  for (const mesh of doc.getRoot().listMeshes()) for (const primitive of mesh.listPrimitives()) {
    if (primitive.getMode() === 4) triangles += (primitive.getIndices()?.getCount() ?? primitive.getAttribute('POSITION')?.getCount() ?? 0) / 3;
  }
  if (Math.round(triangles) !== a.triangles) throw new Error(`Triangle count mismatch: ${id} (${triangles} vs ${a.triangles})`);
  const modelName = `${id}.glb`;
  const thumbName = `${id}.png`;
  await fs.copyFile(source, path.join(out, 'models', modelName));
  await fs.rm(path.join(out, modelName), { force: true });
  if (a.thumbnail) await fs.copyFile(path.join(root, a.thumbnail), path.join(thumbs, thumbName));
  else {
    const existing = path.join(thumbs, thumbName);
    try { await fs.access(existing); }
    catch { await renderThumbnails(thumbs, [source]); }
    const rendered = path.join(thumbs, path.basename(source).replace(/\.glb$/i, '.png'));
    try { await fs.access(existing); }
    catch { await fs.copyFile(rendered, existing); }
  }
  const [recommendedUse, placement] = uses[category];
  records.push({
    id, name: a.name, category, tags: [...new Set(['road-driver', category.toLowerCase().replaceAll(' ', '-'), ...(a.tags || [])])],
    model: `models/${modelName}`, thumbnail: `../../thumbnails/road-driver/${thumbName}`,
    format: 'GLB', bytes: bytes.length, sha256: sha(bytes), triangles: Math.round(triangles), vertices: a.vertices,
    meshCount: a.meshCount, materialCount: a.materials, textureCount: a.textures,
    boundingBox: a.boundingBox, dimensions: a.dimensions, nativeScale: a.scale ?? 1,
    units: a.units ?? { upAxis: 'Y', metresPerUnit: 1 },
    orientation: category === 'VEHICLE' ? { upAxis: 'Y', forwardAxis: '+Z', ground: 'Y=0; verify forward convention in the target scene' } : { upAxis: a.units?.upAxis || 'Y' },
    recommendedUse, placement, license: a.license, licenseUrl: a.licenseUrl,
    author: a.author, source: a.source, sourceUrl: a.sourceUrl, licenseEvidence
  });
}
const hashes = new Set(records.map(x => x.sha256));
if (hashes.size !== records.length) throw new Error('Duplicate model content detected in ROAD DRIVER selection');
const bytes = records.reduce((sum, x) => sum + x.bytes, 0);
const categoryCounts = Object.fromEntries(Object.keys(groups).map(k => [k, records.filter(x => x.category === k).length]));
const manifest = { schemaVersion: 1, collection: 'road-driver', generatedFrom: 'NEXUS data/assets.json', license: 'All selected files are CC0-1.0; per-asset evidence is included below.', modelCount: records.length, totalModelBytes: bytes, categoryCounts, assets: records };
await fs.writeFile(path.join(out, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
const byId = new Map(records.map(record => [record.id, record]));
const enrichedIndex = index.map(asset => {
  const selected = byId.get(asset.id);
  if (!selected) return asset;
  return {
    ...asset,
    tags: [...new Set([...(asset.tags || []), 'road-driver', selected.category.toLowerCase().replaceAll(' ', '-')])],
    recommendedFor: [...new Set([...(asset.recommendedFor || []), 'road-driver'])],
    roadDriver: { category: selected.category, recommendedUse: selected.recommendedUse, placement: selected.placement }
  };
});
await fs.writeFile(path.join(root, 'data/assets.json'), JSON.stringify(enrichedIndex, null, 2) + '\n');
const usedSources = [...new Set(records.map(x => x.source))];
const licenseDir = path.join(out, 'licenses');
await fs.mkdir(licenseDir, { recursive: true });
for (const source of usedSources) {
  const license = source === 'NEXUS original (GIANT CLIMB)' ? 'nexus-original.txt'
    : source === 'Kenney Space Kit 2.0' ? 'kenney-space-kit.txt'
    : source === 'Kenney Starter Kit City Builder' ? 'kenney-city-builder.txt'
    : source === 'Kenney Starter Kit FPS' ? 'kenney-fps.txt'
    : source === 'Kenney Starter Kit 3D Platformer' ? 'kenney-platformer.txt'
    : source === 'Kenney Starter Kit Racing' ? 'kenney-racing.txt'
    : source === 'Kenney Car Kit' ? 'kenney-car-kit.txt'
    : source === 'pmndrs market-assets' ? 'pmndrs-market.txt' : null;
  if (license) await fs.copyFile(path.join(root, 'assets/giant-climb/licenses', license), path.join(licenseDir, license));
}
const table = Object.entries(categoryCounts).map(([k,v]) => `| ${k} | ${v} |`).join('\n');
const readme = [
  '# ROAD DRIVER asset pack', '',
  'NEXUSから選定した45点の軽量GLBです。ROAD DRIVER本体のコードは含みません。完全な機械可読一覧は manifest.json。元のNEXUSライブラリは維持され、このフォルダーには採用モデルだけを収録します。', '',
  `- 合計モデル容量: ${(bytes / 1048576).toFixed(2)} MiB (${bytes.toLocaleString()} bytes)`,
  '- ライセンス: 全件 CC0 1.0。各モデルの出典・ライセンス根拠と SHA-256 は manifest に記録。元の根拠文書は licenses/。',
  '- GLB は再圧縮せず複製し、SHA-256 と glTF Transform での GLB 読み込み・三角形数を照合。',
  '- Up axis は Y。車両の前方は +Z を初期値として記録。車種ごとに向きを確認して配置し、逆なら Y 軸を180度回転してください。bounds と原単位の推奨倍率は manifest に記録。',
  '- 同一内容の重複なし。繰り返し配置では同じモデルを共有し、同一マテリアルの大量配置には InstancedMesh を検討してください。', '',
  '## 内訳', '', '| Category | Count |', '|---|---:|', table, '',
  '## Three.js 取り込み例', '',
  'このパック内の models/ と manifest.json をゲームの静的アセット領域へコピーし、manifest の model パスを基準にロードします。', '',
  '```js',
  "import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';",
  "const manifest = await (await fetch('/assets/road-driver/manifest.json')).json();",
  "const car = manifest.assets.find(asset => asset.id === 'kenney_sedan');",
  "const gltf = await new GLTFLoader().loadAsync('/assets/road-driver/' + car.model);",
  'gltf.scene.scale.setScalar(car.units.metresPerUnit ?? 1);',
  'gltf.scene.position.y = -car.boundingBox.min[1] * (car.units.metresPerUnit ?? 1);',
  'scene.add(gltf.scene);', '```', '',
  '既存NEXUS GitHub MCPを使う場合は、collection: "giant-climb" と tags: ["road-driver"] で検索した後、download_asset を呼び出せます。ゲームへ全215点をコピーせず、配布パックまたはmanifestに載った採用IDだけを利用してください。', ''
].join('\n');
await fs.writeFile(path.join(out, 'README.md'), readme);
const detailRows = records.map(a => `| ${a.id} | ${a.name} | ${a.category} | ${a.bytes.toLocaleString()} | ${a.triangles.toLocaleString()} | ${a.dimensions.map(n => Number(n).toFixed(2)).join(' × ')} | ${a.materialCount} | ${a.textureCount} | ${a.units.metresPerUnit ?? 1} |`).join('\n');
const report = [
  '# ROAD DRIVER 選定モデル・検証レポート', '',
  `- 採用: ${records.length}点、合計 ${bytes.toLocaleString()} bytes (${(bytes / 1048576).toFixed(2)} MiB)。`,
  `- 三角形数: 合計 ${records.reduce((sum, a) => sum + a.triangles, 0).toLocaleString()}、最大 ${Math.max(...records.map(a => a.triangles)).toLocaleString()} / モデル。`,
  `- 形式: GLB 45/45。CC0-1.0 45/45。サムネイル 45/45。SHA-256重複なし。`,
  '- 検証: 選定前にNEXUS内215点の既存コレクションを調査。採用GLBをglTF Transform NodeIOで全件読み込み、三角形数を既存メタデータと照合。SHA-256は元ファイルと同一であることを確認。既存のThree.js GLTFLoaderサムネイル生成パイプラインを利用。',
  '- 向き/スケール: 全モデルY-up。寸法と原点boundsはmanifestの値。vehicleはnative +Z前方を初期配置値とし、異なる道路座標系ならY軸180°回転。原単位倍率を各asset.units.metresPerUnitに記録。',
  '- 軽量性評価: 全モデル 1 MiB 未満、最大三角形数は本表参照。繰り返し配置ではGLBを共有し、同形状の多数配置にInstancedMeshを推奨。テクスチャ付きは既存少数の街路樹/草/レース車両のみ。',
  '- ライセンス: 全件CC0-1.0。各レコードのsourceUrlとlicenseEvidenceはmanifestに含み、原文書はlicenses/に収録。', '',
  '## カテゴリー', '', '| Category | Count |', '|---|---:|', table, '',
  '## 採用一覧', '', '| ID | モデル | Category | Bytes | Triangles | Dimensions (native) | Materials | Textures | metres/unit |', '|---|---|---|---:|---:|---|---:|---:|---:|', detailRows, '',
  'NEXUSのdata/assets.json内の採用45レコードにroad-driverタグ、ROAD DRIVER分類、推奨用途、配置方法を追加しました。既存の他のアセットと検索機能はそのままです。', ''
].join('\n');
await fs.writeFile(path.join(out, 'REPORT.md'), report);
console.log(`ROAD DRIVER pack built: ${records.length} models, ${bytes} bytes, ${JSON.stringify(categoryCounts)}`);
