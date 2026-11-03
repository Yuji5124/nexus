# DEEP-TRENCH ENEMIES｜深度3500m以降の敵キャラ

深度 **3,500m 以降** (発光深海・沈没都市・深淵領域) を舞台にしたゲーム向けの、**敵キャラ 10 体**です。どれも**動きのつき (リグ + アニメ)** です。ボスは含めません (ボスは別途 ChatGPT と進める方針)。

- **モデル**：`assets/deep-trench-enemies/`（NEXUS の COLLECTION で `deep-trench-enemies` を選ぶと表示）／サムネイル：`thumbnails/deep-trench-enemies/`
- **軽さ**：1体 652〜4,292 三角形、52〜315 KB（合計約 1.5 MB）。**テクスチャなし**。
- **単位・向き・リグ・クリップ名**：`deep-sea-enemies` と同じ（1 unit = 1 m、Y が上、正面は +Z、1パーツ 1 骨の剛体リグ、`Idle` / `Walk` / `Swim` / `Attack`）。同じ場面に並べられます。
- **ライセンス**：NEXUS のオリジナル（スクリプトで生成）。まだライセンスを決めていないので `UNKNOWN` にしています。

## 出現深度は「提案」です

『甲殻類にも都合があります。』の `docs/GAME_SPEC.md` の深度帯（第3海域 発光深海 3,000〜8,000m／第4海域 古代文明 8,000〜10,000m／第5海域 深淵領域 10,000〜12,000m）と、`docs/UNKNOWN_NATURAL_PHENOMENA.md` の現象案を読んで、**見た目の方向だけ**を合わせています。出現深度・強さ・攻撃の中身は決めていません（仕様ではなく、ゲーム側で決めてください）。古代文明の正体や現象の仕組みも決めていません（「番人」や「記録」などは見た目の呼び名です）。

## 10 体

### 発光深海 3,500〜8,000m

| ID | 敵 | 動き | 区分 | アニメ | 大きさ (m) | 三角形 |
|---|---|---|---|---|---|---|
| `enemy_isopod_roller` | Isopod Roller | 歩行 | 群れ | Attack / Idle / Walk | 2.0 × 1.4 × 4.9 | 1,940 |
|  | Giant isopod with six overlapping armour plates, twelve legs and long antennae | | | | | |
| `enemy_lantern_swarm` | Lantern Swarm Drone | 浮遊 | 群れ | Attack / Idle | 1.2 × 0.5 × 1.2 | 676 |
|  | Small glowing orb drone with a spinning amber halo ring, a red eye and an underside lamp | | | | | |
| `enemy_siphonophore_chain` | Siphonophore Chain | 据え置き | 群れ | Attack / Idle | 1.0 × 6.0 × 1.0 | 4,292 |
|  | A tall chain of seven glowing glass bells with dangling amber-tipped tentacles | | | | | |
| `enemy_tubeworm_spitter` | Tubeworm Spitter | 据え置き | 群れ | Attack / Idle | 3.0 × 4.3 × 2.9 | 900 |
|  | Cluster of seven white tubes on a vent mound, each tipped with orange plumes and a glow bud | | | | | |
| `enemy_viperfish_hunter` | Viperfish Hunter | 遊泳 | 強敵 | Attack / Idle / Swim | 1.2 × 1.3 × 5.5 | 1,640 |
|  | Armoured viperfish with a skull-like head, long fangs, a hinged jaw, photophore lights along the flanks and a dorsal lure | | | | | |

### 沈没都市 8,000〜10,000m

| ID | 敵 | 動き | 区分 | アニメ | 大きさ (m) | 三角形 |
|---|---|---|---|---|---|---|
| `enemy_archive_warden` | Archive Warden | 浮遊 | 強敵 | Attack / Idle | 4.7 × 2.7 × 4.7 | 2,440 |
|  | A stone orb with an amber eye slit, three counter-rotating glyph rings and two hanging stabilisers | | | | | |
| `enemy_lamplighter` | Lamplighter | 浮遊 | 群れ | Attack / Idle / Swim | 1.3 × 3.1 × 2.6 | 652 |
|  | Slender floating figure of stone and metal with a long arm holding a swinging amber lantern and six hanging strips | | | | | |
| `enemy_obelisk_stalker` | Obelisk Stalker | 歩行 | 強敵 | Attack / Idle / Walk | 3.6 × 6.2 × 3.1 | 1,036 |
|  | Seven-metre stone obelisk on three jointed legs, with a glowing vertical slit and a floating glyph crown | | | | | |

### 深淵領域 10,000〜12,000m

| ID | 敵 | 動き | 区分 | アニメ | 大きさ (m) | 三角形 |
|---|---|---|---|---|---|---|
| `enemy_echo_manta` | Echo Manta | 遊泳 | 強敵 | Attack / Idle / Swim | 8.9 × 0.8 × 7.4 | 1,564 |
|  | Dark manta with translucent violet wings, a glowing dorsal seam and two ghost copies trailing behind | | | | | |
| `enemy_void_anemone` | Void Anemone | 据え置き | 群れ | Attack / Idle | 3.5 × 3.9 × 3.5 | 2,424 |
|  | Stone-based anemone with a translucent bell, a violet core, twelve three-joint tentacles and a floating glyph ring | | | | | |

## 使い方 (Three.js)

`deep-sea-enemies/README.md` と同じです（`GLTFLoader` で読み、`AnimationMixer` でクリップ名を指定して再生）。半透明の材質 (`glass` / `ghost`) は透明パスで描かれます。紫 (`lume`) と琥珀 (`amber`) は発光材質なので、ブルームを足すと映えます。

## 見た目の約束

- 材質（テクスチャなし）：`hull` / `armor` / `accent` / `eye` / `glow` / `stone` / `rune` / `glass`（`deep-sea-enemies` と共通）に、`lume`（紫の生物発光）、`amber`（琥珀の灯り）、`bone`（骨色）、`ghost`（半透明の紫）を足しました。
- アニメは全員 `Idle`（ループ）。動く敵は `Walk` / `Swim`、攻撃のある敵は `Attack`。

## 作り直す・増やすとき

```sh
# Blender 4.x / 5.x が必要 (ヘッドレスで GLB とサムネイルを書き出す)
blender -b -P scripts/deep-trench-enemies/build_trench_enemies.py -- assets/deep-trench-enemies thumbnails/deep-trench-enemies
npm run deep-trench-enemies     # data/assets.json に記録して scan
```

- 形とアニメは `build_trench_enemies.py` の敵ごとの関数と `MODELS`、一覧（名前・説明・帯）は `catalog.mjs`。第 4 引数以降に ID を並べると、その敵だけ作り直せます。
- **注意**：新しい GLB を置いたあとに `npm run scan` だけを先に走らせると、記録が自動の簡易版で作られます。必ず先に `npm run deep-trench-enemies` で登録してください。

## 参考にしたもの (コード・素材は一切使っていません)

| 参考 | 参考にした点 |
|---|---|
| `crustaceans-have-plans` の `docs/GAME_SPEC.md`・`docs/UNKNOWN_NATURAL_PHENOMENA.md`・`docs/LORE_AND_STORY.md` | 深度帯と現象案（見た目の方向だけ）。文書は変更していません |
| 実在の深海生物 (ホウライエソ・クダクラゲ・ダイオウグソクムシ・チューブワーム・イソギンチャク・マンタ) | 形のモチーフ。実在の図や写真・コードは使っていません |
| `deep-sea-enemies` (同じ NEXUS) | リグ・アニメ・材質の約束 |
