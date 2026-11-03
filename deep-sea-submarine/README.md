# DEEP-SEA SUBMARINE｜潜水艦の改造パーツ

『甲殻類にも都合があります。』の潜水艦（全長 14 m）に付ける**改造パーツ 20 点**です。`docs/GAME_SPEC.md` の「潜水艦の成長：耐圧船殻・エンジン・ソナー・照明・貨物室・作業アームなど」に合わせた見た目の案で、**性能・価格・段階数は決めていません**。

- **モデル**：`assets/deep-sea-submarine/`（NEXUS の COLLECTION で `deep-sea-submarine` を選ぶと表示）／サムネイル：`thumbnails/deep-sea-submarine/`
- **軽さ**：1点 232〜2,536 三角形、16〜135 KB（合計約 1.3 MB）。**テクスチャなし**。
- **単位・向き**：1 unit = 1 m、Y が上、艦首が +Z。**外付けパーツは取り付け点が原点で、外向きが +Y**。船殻の区画は中心が原点で、長手方向が Z。
- **ライセンス**：NEXUS のオリジナル（スクリプトで生成）。まだライセンスを決めていないので `UNKNOWN` にしています。
- **作り方**：**Blender MCP（ライブの Blender 5.2）** から作りました。開いているシーンの既存オブジェクトには触らず、専用のコレクション `NEXUS_SUB` に作って、書き出したあと横に並べています。ヘッドレスでも同じスクリプトで作れます。

## 20 点

### 船殻 (耐圧・補強)

| ID | 名前 | 内容 | 大きさ (m) | 三角形 |
|---|---|---|---|---|
| `sub_hull_mk1` | Pressure Hull Section Mk1 | First-stage pressure hull section, 4 m long and 4 m across: thin ribs, end flanges, an orange band and a hatch pad | 4.2 × 4.2 × 4.2 | 1,596 |
| `sub_hull_mk2` | Pressure Hull Section Mk2 | Second-stage pressure hull section: thicker ribs plus eight outer armour plates on a 4.2 m diameter shell | 4.5 × 4.5 × 4.3 | 1,972 |
| `sub_hull_mk3` | Pressure Hull Section Mk3 | Third-stage pressure hull section: heavy ribs, twelve armour plates, brass bolt blocks and a glowing seam on a 4.5 m diameter shell | 5.0 × 5.0 × 4.4 | 2,536 |
| `sub_shell_plating` | Shell Reinforcement Plating | Hull section wrapped in ten purple shell plates with gold edging and a gold-and-purple spiral shell on top: a look for the shell the hermit crab donates to the sub | 4.9 × 6.2 × 3.6 | 2,028 |

### 推進・浮力・電源

| ID | 名前 | 内容 | 大きさ (m) | 三角形 |
|---|---|---|---|---|
| `sub_ballast_tank` | Ballast Tank | Twin horizontal tanks with domed ends, orange bands and a brass valve wheel on a base plate | 2.2 × 1.6 × 3.2 | 1,964 |
| `sub_battery_pack` | Battery Pack | Four battery cells in a frame with glowing charge strips, brass terminals and a cable | 2.9 × 1.3 × 1.8 | 276 |
| `sub_thruster_large` | Main Engine | Large engine pod: a ducted five-blade propeller, a thick motor body with a glowing exhaust ring, and a mounting plate with two struts | 2.6 × 2.8 × 4.1 | 1,744 |
| `sub_thruster_small` | Small Thruster | Ducted four-blade thruster on a bracket with a rear motor | 1.6 × 1.7 × 1.9 | 1,124 |

### 探知 (ソナー)

| ID | 名前 | 内容 | 大きさ (m) | 三角形 |
|---|---|---|---|---|
| `sub_sonar_array` | Hydrophone Array | Flat 3 by 5 array of rubber-ringed transducers with glowing and orange dots on a 3 m plate | 3.0 × 0.3 × 1.8 | 1,184 |
| `sub_sonar_dish` | Sonar Dish | Parabolic sonar dish with a glowing face, a feed horn and three struts on a rotating mast | 2.0 × 2.5 × 1.4 | 404 |

### 照明

| ID | 名前 | 内容 | 大きさ (m) | 三角形 |
|---|---|---|---|---|
| `sub_floodlight_bar` | Floodlight Bar | Work-light bar 3 m wide with six warm lamps and orange end caps | 3.1 × 0.7 × 0.6 | 232 |
| `sub_headlamp` | Headlamp | Round headlamp with a reflector cone, glowing bulb, glass lens and a protective grille, on a short bracket | 1.0 × 1.1 × 0.9 | 716 |

### 作業・貨物・テザー

| ID | 名前 | 内容 | 大きさ (m) | 三角形 |
|---|---|---|---|---|
| `sub_cargo_pod` | Cargo Pod | Capsule cargo pod 3.2 m long with a top hatch, three orange bands, a side door and mounting rails | 3.2 × 1.9 × 3.6 | 1,104 |
| `sub_manipulator_arm` | Manipulator Arm | Three-segment work arm with a swivel base, orange joints and a two-finger brass claw | 1.2 × 1.9 × 4.4 | 612 |
| `sub_sample_rack` | Sample Rack | Rack of six glass sample tubes with glowing contents (cyan, amber, purple) and rubber caps | 2.0 × 1.6 × 1.0 | 716 |
| `sub_tether_winch` | Tether Winch | Winch with a flanged drum wound in brass cable, a guide arm, a hook and an orange motor housing | 2.2 × 1.8 × 2.7 | 1,788 |

### 乗員・通信・補修

| ID | 名前 | 内容 | 大きさ (m) | 三角形 |
|---|---|---|---|---|
| `sub_antenna_mast` | Antenna Mast | 4 m communications mast with three glowing rings, small panel antennas, a dish and an orange tip light | 1.3 × 4.1 × 0.9 | 618 |
| `sub_dome_viewport` | Dome Viewport | Glass dome window 2.6 m across with a framing ring, twelve bolts, a cross frame and a soft interior lamp | 2.6 × 2.0 × 2.6 | 1,268 |
| `sub_hatch_module` | Hatch Tower | Round hatch tower 2 m tall with a wheel-handled lid, handrails, a ladder and a warm lamp | 2.0 × 2.0 × 2.0 | 876 |
| `sub_repair_kit` | Repair Kit | Orange toolbox with a handle, open side tray and loose tools: a wrench, a purple patch plate and bolts | 3.1 × 1.1 × 1.4 | 452 |

(大きさは `data/assets.json` の `dimensions` の値。)

## 段階の見せ方（案）

- 船殻 `sub_hull_mk1` → `mk2` → `mk3` は、リブが太くなり、補強板が増え、`mk3` は縫い目が光ります（**耐圧の段階の見た目**の案）。
- `sub_shell_plating` は、紫の巻き殻の板と金の縁。ハンスが約3,500mで殻を提供する場面の見た目の案です（`docs/CAMPAIGN_TO_3500.md` の「紫色と金色の巻き殻を補強として装着」に合わせました）。
- `sub_repair_kit` には紫の補修板を入れてあり、戦闘後の修理の場面に使えます。

## 見た目の約束

- **材質**：`hull`（鋼）・`dark`（暗い部品）・`accent`（オレンジ）・`brass`・`gold`・`shell`（紫）・`rubber` は不透明。`glow`（シアン）・`warm`（灯り）は発光なので、ブルームを足すと映えます。
- **半透明**：`glass`（前照灯のレンズ、ドームの窓、標本ラックの管）だけが alpha blend です。Three.js では透明パスで描いてください。
- 遺跡・敵・小道具のコレクションと同じ約束（単位・向き）です。

## 作り直す・増やすとき

```sh
# ヘッドレス (Blender 4.x / 5.x)
blender -b -P scripts/deep-sea-submarine/build_sub_parts.py -- assets/deep-sea-submarine thumbnails/deep-sea-submarine
npm run deep-sea-submarine     # data/assets.json に記録して scan
```

- ライブの Blender (Blender MCP) では、`exec(open("scripts/deep-sea-submarine/build_sub_parts.py").read(), {"__name__": "nexus_sub"})` のあと `run()` で全点（`run(only=["sub_headlamp"])` で 1 点）を書き出し、`NEXUS_SUB` コレクションに並べます。
- 形・名前・説明は `scripts/deep-sea-submarine/sub_parts.py` の関数と `MODELS`（元データ）。`catalog.json` は全点を作り直すと自動で書き直されます。
- **注意**：新しい GLB を置いたあとに `npm run scan` だけを先に走らせると、記録が簡易版で重複します。必ず先に `npm run deep-sea-submarine` で登録してください。

## 参考にしたもの (コード・素材は一切使っていません)

| 参考 | 参考にした点 |
|---|---|
| `crustaceans-have-plans` の `docs/GAME_SPEC.md`・`docs/CAMPAIGN_TO_3500.md`・`src/adventure/main.ts` の `subLength: 14` | 改造パーツの種類、潜水艦の大きさ、ハンスの殻の配色。文書とコードは変更していません |
| 実在の潜水機・探査機の一般的な装備 (耐圧殻のリブ・スラスターのダクト・ソナーの皿・投光灯・マニピュレーター・ウインチ) | 形のモチーフ。実在の図面や写真・コードは使っていません |
