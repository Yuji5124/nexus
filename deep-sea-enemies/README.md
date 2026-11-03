# DEEP-SEA ENEMIES｜深海の敵キャラ

深海を舞台にしたアクションゲーム向けの、**敵キャラ 12 体**です。どれも**動きのつき (リグ + アニメ)** です。

- **モデル**：`assets/deep-sea-enemies/`（NEXUS の COLLECTION で `deep-sea-enemies` を選ぶと表示）／サムネイル：`thumbnails/deep-sea-enemies/`
- **軽さ**：1体 740〜2,484 三角形、56〜205 KB（合計約 1.5 MB）。**テクスチャなし**。
- **単位・向き**：1 unit = 1 m、Y が上、正面は +Z。原点は足元（浮遊・遊泳する敵は基準の高さ。寸法は `boundingBox` で確認）。
- **ライセンス**：NEXUS のオリジナル（スクリプトで生成）。まだライセンスを決めていないので `UNKNOWN` にしています。

## 12 体

| ID | 敵 | 動き | 区分 | アニメ | 大きさ (m) |
|---|---|---|---|---|---|
| `enemy_scout_drone` | 偵察ドローン (4枚ローター、赤い目) | 浮遊 | 群れ | Idle / Attack (急降下) | 約 2.9 × 1.1 × 2.7 |
| `enemy_crawler_bot` | 多脚ロボ (6脚、牙) | 歩行 | 群れ | Idle / Walk / Attack (脚で突く) | 約 3.6 × 1.2 × 2.7 |
| `enemy_gunner_turret` | 砲台 (三脚、回る頭、二連砲) | 据え置き | 群れ | Idle (見回し) / Attack (反動) | 約 2.9 × 2.4 × 3.5 |
| `enemy_bulwark_walker` | 重装 (4脚、大盾) | 歩行 | 強敵 | Idle / Walk / Attack (盾で叩く) | 約 3.5 × 2.7 × 3.4 |
| `enemy_jelly_drone` | クラゲ型 (半透明の傘、8本の触手) | 浮遊 | 群れ | Idle / Attack (傘がふくらみ触手が鞭) | 約 2.1 × 2.7 × 2.1 |
| `enemy_eel_bot` | ウナギ型 (8節、開く顎) | 遊泳 | 群れ | Idle / Swim / Attack (顎を開いて突進) | 約 1.0 × 1.0 × 8.8 |
| `enemy_urchin_mine` | ウニ型の機雷 (18本のとげ) | 据え置き | 群れ | Idle (脈動) / Attack (とげが伸びる) | 約 2.1 × 2.2 × 2.1 |
| `enemy_angler_lurebot` | チョウチンアンコウ型 (提灯、歯の顎) | 遊泳 | 強敵 | Idle / Attack (顎で噛む) | 約 3.9 × 2.5 × 4.8 |
| `enemy_squid_lancer` | イカ型の槍使い (8本の腕、2本の槍) | 遊泳 | 強敵 | Idle / Attack (槍の突き) | 約 2.7 × 1.9 × 6.5 |
| `enemy_ruin_sentinel` | 遺跡の番人 (石の巨人、約5m) | 歩行 | 強敵 | Idle / Walk / Attack (両拳の叩きつけ) | 約 4.3 × 5.3 × 1.6 |
| `enemy_stone_crab_guardian` | 石の蟹の守り神 (動く像) | 歩行 | 強敵 | Idle / Walk / Attack (ハサミで挟む) | 約 5.9 × 3.2 × 5.7 |
| `enemy_hammerhead_sweeper` | ハンマーヘッド型のサメ | 遊泳 | 強敵 | Idle / Swim / Attack (頭を振る) | 約 4.1 × 2.3 × 10.4 |

(大きさは `data/assets.json` の `dimensions` (幅 × 高さ × 奥行き、アニメ前の基本姿勢) の値。)

遺跡キット (`deep-sea-ruins`) の「蟹の守り神の像」は、`enemy_stone_crab_guardian` が動き出した姿です。

## 使い方 (Three.js)

```js
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import * as THREE from 'three';
new GLTFLoader().load(asset.rawUrl, (gltf) => {
  scene.add(gltf.scene);
  const mixer = new THREE.AnimationMixer(gltf.scene);
  const clip = THREE.AnimationClip.findByName(gltf.animations, 'Idle');
  mixer.clipAction(clip).play();      // Attack などは LoopOnce で割り込ませる
});
```

- **クリップ名はそろえてあります**：全員 `Idle`、動く敵は `Walk` か `Swim`、攻撃のある敵は `Attack`。ゲーム側は名前で切り替えるだけです。
- **リグ**：1パーツ = 1骨の剛体 (スキニングなし)。パーツは骨ノードの下のメッシュです。見た目 (ローポリ) を崩さずに動かせます。
- **材質**：`hull` (暗い鋼) / `armor` (装甲板) / `accent` (警告色のオレンジ) / `eye` (赤く光る目) / `glow` (シアンの動力) / `stone` / `rune` (石と紋様) / `glass` (半透明。クラゲだけ)。光る部分は発光マテリアルなので、ブルームを足すと映えます。
- 当たり判定は、`boundingBox` と大きさの目安から作ってください。

## 作り直す・増やすとき

```sh
# Blender 4.x / 5.x が必要 (ヘッドレスで GLB・アニメ・サムネイルを書き出す)
blender -b -P scripts/deep-sea-enemies/build_enemies.py -- assets/deep-sea-enemies thumbnails/deep-sea-enemies
npm run deep-sea-enemies     # data/assets.json に記録して scan
```

- 敵ごとに 1 つの関数 (`scout_drone` など) が、形・骨・アニメを持ちます。`MODELS` に 1 行足すと増やせます。第 4 引数以降に ID を並べると、その敵だけ作り直せます。
- 名前・説明・設計の目安は `scripts/deep-sea-enemies/catalog.mjs`。

## 参考にしたもの (コード・素材は一切使っていません)

| 参考 | ライセンス | 参考にした点 |
|---|---|---|
| アクションゲームの一般的な敵の役割分担 | - | 偵察 (浮遊・低HP) / 突進 / 砲台 (固定・遠距離) / 重装 (盾・高HP) / 触手の接触ダメージ、という役割の分け方 |
| [glTF Transform](https://github.com/donmccurdy/glTF-Transform) | MIT | 寸法・アニメの計測と記録 (NEXUS の既存の仕組みと同じ道具) |
| [three.js](https://github.com/mrdoob/three.js) | MIT | `AnimationMixer` による再生の前提 |

敵の役割は、ゲーム『甲殻類にも都合があります。』の試作の敵 (偵察・多脚・砲台・重装・クラゲ) を元に、このキット用に作り直したオリジナルです。

## 次に作るもの

進み具合は [../deep-sea-ruins/PROGRESS.md](../deep-sea-ruins/PROGRESS.md) を参照してください。
