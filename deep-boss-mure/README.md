# DEEP-BOSS-MURE｜水深4,500m のボス「誰もいない王（ムレ）」の造形案

『甲殻類にも都合があります。』の水深 4,500m のボス「誰もいない王（ムレ）」を、コンセプト指示に沿って**見た目の形だけ**作った案です。**HP・攻撃・当たり判定・弱点・撃破条件は決めていません**（検証用の仮実装・提案）。

## 作りの考え方
- **肉体は無く、40,491 匹の小魚の位置だけで王の姿をつくります。** 一つのメッシュではなく「小魚 1 匹 + 配置データ」です。ゲーム側は `InstancedMesh` で 40,491 匹を描く想定。
- 輪郭は 鳳凰（広がる羽の翼）・マンタ（大きな翼状のヒレ）・古代魚（吻のある頭）・王冠（頭上の魚群の輪と 7 本の尖り）の融合。全長 約 257 m、翼幅 約 218 m。
- **中心は空洞**：首と胸は縦の4本の線と7つの輪だけで、間は何も置かない。翼は羽の帯、尾は 3 本の流れる帯。指揮者・中心個体はいない。
- **脱皮**：`moult` の小魚が輪郭から弧を描いて離れる流れ。ゲーム側で「部位を入れ替えて新しい形に作り直す」ときの材料にする提案（ルールではない）。
- 牙・筋肉・爪・角は無し。色は銀・真珠・淡い金・薄桃の 4 色。

## ファイル（`assets/deep-boss-mure/`）
| ファイル | 内容 |
|---|---|
| `boss_mure_school.bin` | 小魚の配置。1 匹 = float32 × 11（x y z dirX dirY dirZ u part phase size color）。40,491 匹 = 1.78 MB |
| `boss_mure_school.json` | 上の説明（欄・部位・色・座標系・注意） |
| `boss_mure_preview.glb` | 確認用。1/4 の間引き（10,122 匹・約 2 倍の大きさ）を頂点色の 1 メッシュにしたもの。80,000 三角形 |
| `boss_mure_fish.glb` | 小魚 1 匹（6 頂点・8 三角形・全長 1.6 m）。インスタンスの元。好きな魚に差し替えてよい |

座標は glTF / Three.js（Y 上、前 +Z、尾は -Z、1 unit = 1 m、原点はボスの腰の真下あたり）。

| 部位 | 匹数 |
|---|---|
| `head` | 3,000 |
| `crown_ring` | 1,000 |
| `crown_spikes` | 800 |
| `neck_chest` | 8,000 |
| `wing_l` | 8,496 |
| `wing_r` | 8,496 |
| `tail` | 5,499 |
| `moult` | 5,200 |

## ゲームでの使い方（案）
```js
const buf = await (await fetch('boss_mure_school.bin')).arrayBuffer();
const f = new Float32Array(buf);            // stride 11
const mesh = new THREE.InstancedMesh(fishGeometry, material, f.length / 11);
// i 番目: 位置 f[i*11..+3]、向き f[i*11+3..+6]、size = f[i*11+9]、color = f[i*11+10] (0 銀 / 1 真珠 / 2 金 / 3 桃)
```
泳ぐ動き（phase を使った揺れ）や脱皮の入れ替えはゲーム側で付けます。

## 作り直す
```sh
python scripts/deep-boss-mure/build_boss_mure.py assets/deep-boss-mure
npm run deep-boss-mure
# 確認画像: blender -b -P scripts/deep-boss-mure/render_boss_mure.py -- <glb> <png> front|three|side|close
```
形は `scripts/deep-boss-mure/boss_mure.py` の骨組み（`NECK`・`wing_feathers`・`tail_ribbons`・`COUNTS`）で変えられます。**注意**：GLB を置いたあと `npm run scan` だけを先に走らせると記録が重複します。必ず先に `npm run deep-boss-mure`。

## 確認できたことと未確認
- 確認：Blender 4.4 のヘッドレスで横・斜め・正面・拡大を描いて、冠・頭・羽の翼・流れる尾・空洞の胴が読めること、小魚 1 匹ずつが見分けられること。
- 未確認：Three.js でのインスタンス描画と性能、乳白色の海の中での見え方（確認画像は暗い青灰の背景に白）、脱皮の動き、潜水艦との大きさの比較、正面からの顔つき（頭は卵形のかたまりで、目の穴だけ）。
- 首と胴は縦の4本の線と7つの輪の開いた格子 (横に広い楕円、マンタ風) にして太くした。まだ鳥寄りに見える角度があり、胸びれの追加などは希望を聞いてから。

## 参考にしたもの（コード・素材は使っていません）
ユーザーの 4,500m ボスのコンセプト指示と画像（画像はリポジトリに入れていません）。
