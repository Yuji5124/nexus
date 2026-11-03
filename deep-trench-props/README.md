# DEEP-TRENCH PROPS｜深度3500m以降のオブジェクト

深度 **3,500m 以降** (発光深海・沈没都市・深淵領域) を舞台にしたゲーム向けの、**オブジェクト 20 点**です。海底を飾る小道具・地形と、未知の自然現象の見た目（半透明の効果）が入っています。

- **モデル**：`assets/deep-trench-props/`（NEXUS の COLLECTION で `deep-trench-props` を選ぶと表示）／サムネイル：`thumbnails/deep-trench-props/`
- **軽さ**：1点 316〜3,464 三角形、21〜197 KB（合計約 1.5 MB）。**テクスチャなし**。
- **単位・向き**：1 unit = 1 m、Y が上、原点は底の中心（効果は基準点）、正面は +Z。
- **ライセンス**：NEXUS のオリジナル（スクリプトで生成）。まだライセンスを決めていないので `UNKNOWN` にしています。

## 出現深度と意味は「提案」です

『甲殻類にも都合があります。』の `docs/GAME_SPEC.md`・`docs/LORE_AND_STORY.md`・`docs/UNKNOWN_NATURAL_PHENOMENA.md` の方向性（発光深海／沈没都市の住居跡・記録装置・壁画・日用品／虹の海流と未知の現象）に**見た目だけ**を合わせています。古代文明の正体、壁画や記録装置の意味、現象の仕組みは**決めていません**（意図的に曖昧にしてあります）。出現深度も提案です。

### 発光深海 3,500〜8,000m

| ID | 名前 | 区分 | 大きさ (m) | 三角形 |
|---|---|---|---|---|
| `prop_glass_sponge` | Glass Sponge Colony | 小道具・地形 | 3.0 × 2.8 × 2.9 | 2,496 |
|  | Seven flared bone-white sponge tubes (0.8-2.4 m) with softly glowing mouths and ring ribs, on a stone base | | | |
| `prop_lamp_stalks` | Lamp Stalks | 小道具・地形 | 2.6 × 4.4 × 2.6 | 1,612 |
|  | Nine slender bent stalks (1.6-3.8 m) each tipped with a glowing bulb, violet or amber: a soft light grove for dark basins | | | |
| `prop_lume_coral` | Lume Coral | 小道具・地形 | 2.2 × 2.9 × 2.3 | 3,464 |
|  | Branching coral with pale branches and glowing violet tips, three trunks on a stone base | | | |
| `prop_nodule_field` | Manganese Nodule Field | 小道具・地形 | 4.7 × 0.7 × 4.1 | 1,316 |
|  | A patch of dark nodules, 26 loose and five cyan crystal glints, about 4.8 m across: a resource-gathering spot or seabed dressing | | | |
| `prop_tubeworm_garden` | Tubeworm Garden | 小道具・地形 | 3.6 × 3.0 × 3.8 | 1,316 |
|  | Sixteen white tubeworm tubes (0.9-2.6 m) tipped with orange-red plumes, on a rock mound: scenery version of the Tubeworm Spitter enemy | | | |
| `prop_whale_fall` | Whale Fall | 小道具・地形 | 5.9 × 3.0 × 15.0 | 2,728 |
|  | A whale skeleton lying on the seabed, about 15 m long: spine, eight rib pairs, skull and jaw, with violet bacterial mats glowing around the bones | | | |

### 沈没都市 8,000〜10,000m

| ID | 名前 | 区分 | 大きさ (m) | 三角形 |
|---|---|---|---|---|
| `prop_conduit_bundle` | Conduit Bundle | 小道具・地形 | 2.4 × 2.0 × 7.2 | 2,012 |
|  | Five iron pipes of different widths bundled by three clamps along 7 m, glowing seams at each end and a bend with an amber lamp | | | |
| `prop_data_obelisk` | Record Obelisk | 小道具・地形 | 3.2 × 8.2 × 3.2 | 600 |
|  | A stepped stone obelisk 8 m tall with ten rows of glowing glyph bars on the front and a ring at mid height | | | |
| `prop_dwelling_wall` | Dwelling Ruin Corner | 小道具・地形 | 7.1 × 3.7 × 7.4 | 316 |
|  | A collapsed house corner 6.4 m wide: walls of uneven height, an arched doorway, a window with an amber lamp and scattered blocks | | | |
| `prop_glow_rubble` | Glowing Rubble | 小道具・地形 | 3.6 × 1.6 × 3.8 | 316 |
|  | A heap of fourteen fallen blocks about 4 m across, with amber light leaking from its cracks | | | |
| `prop_mural_panel` | Mural Panel | 小道具・地形 | 4.8 × 3.8 × 0.7 | 2,104 |
|  | A framed stone panel 4.8 m wide and 3.8 m tall with concentric ring reliefs, amber spirals and a row of five glowing circles | | | |
| `prop_street_lamp` | Sunken Street Lamp | 小道具・地形 | 1.8 × 5.2 × 1.1 | 340 |
|  | A leaning iron lamp post 5.2 m tall with a curved arm and an amber lantern that still glows | | | |
| `prop_urn_set` | Everyday Ware Set | 小道具・地形 | 3.7 × 1.5 × 3.5 | 940 |
|  | Two urns, a bowl, a plate, a cup and a ladle: everyday objects one urn of which has a glowing rim | | | |

### 深淵領域 10,000〜12,000m

| ID | 名前 | 区分 | 大きさ (m) | 三角形 |
|---|---|---|---|---|
| `fx_afterimage_ghost` | Afterimage Echo | 効果・半透明 | 2.3 × 2.3 × 7.6 | 992 |
|  | Four translucent copies of a diamond body, spaced 1.7 m apart and fading backwards, each with a violet ring and a tiny eye | | | |
| `fx_phase_rift` | Phase Rift | 効果・半透明 | 2.4 × 5.3 × 2.4 | 1,048 |
|  | A tall oval rift 5.3 m high: glowing double frame, a translucent wobbling face and ten glowing shards | | | |
| `fx_pressure_husk` | Pressure Husk Dome | 効果・半透明 | 8.1 × 6.6 × 8.1 | 1,672 |
|  | A translucent dome 8 m wide and 3.2 m high (its lower half lies below the ground plane) with a glowing rim and three violet shell lines | | | |
| `fx_rainbow_current` | Rainbow Current | 効果・半透明 | 5.2 × 12.0 × 5.3 | 400 |
|  | Five translucent ribbons (red, yellow, green, cyan, violet) twisting 1.6 turns up a 12 m column and widening as they rise | | | |
| `prop_abyss_monolith` | Abyssal Monolith | 小道具・地形 | 5.2 × 12.8 × 5.1 | 580 |
|  | A light-swallowing black pillar 12.8 m tall on two steps, with one thin glowing seam and a floating ring with three violet beads | | | |
| `prop_floating_stones` | Floating Stones | 小道具・地形・半透明 | 6.1 × 5.1 × 5.4 | 1,224 |
|  | Nine stones drifting at 1-6 m in a loose ring, violet underlight on each and thin translucent threads linking them | | | |
| `prop_invisible_steps` | Unseen Steps | 小道具・地形・半透明 | 6.0 × 4.6 × 6.1 | 360 |
|  | Six faint translucent slabs (1.6 x 1.1 m) spiralling up 4.5 m, only their edges glowing | | | |

(大きさは `data/assets.json` の `dimensions` の値。)

## 見た目の約束

- **石**：頂点色で、下ほど暗く青緑に苔むす風化。形は少しゆがめた低ポリ（フラットシェーディング）。
- **光る部分**：`glow`（シアン）・`warm`（橙）・`bio`（緑）・`lume`（紫）・`amber`（琥珀）は発光材質。ブルームを足すと映えます。`metal`（錆びた鉄）・`bone`（骨色）・`obs`（光を吸う黒）は不透明です。
- **半透明（`alpha` タグ）**：`beam` / `glass` / `ghost` / `ray_*` は alpha blend で発光しています。Three.js では透明パスで描き、`depthWrite = false` にし、光らせたいときは `AdditiveBlending` にします。`prop_floating_stones` と `prop_invisible_steps` は、半透明の部分と不透明の部分が混ざっています。拡大・回転・フェードはコードで付けてください（アニメは入れていません）。
- `deep-sea-ruins` / `deep-sea-enemies` / `deep-sea-props` と同じ約束（単位・向き・材質の考え方）です。

## 作り直す・増やすとき

```sh
# Blender 4.x / 5.x が必要 (ヘッドレスで GLB とサムネイルを書き出す)
blender -b -P scripts/deep-trench-props/build_trench_props.py -- assets/deep-trench-props thumbnails/deep-trench-props
npm run deep-trench-props     # data/assets.json に記録して scan
```

- 形・名前・説明・帯は `scripts/deep-trench-props/parts.py` の関数と `MODELS`（元データ。タグの最初が帯）。`catalog.json` は全点を作り直すと自動で書き直されます。
- **注意**：新しい GLB を置いたあとに `npm run scan` だけを先に走らせると、記録が自動の簡易版で作られます。必ず先に `npm run deep-trench-props` で登録してください。

## 参考にしたもの (コード・素材は一切使っていません)

| 参考 | 参考にした点 |
|---|---|
| `crustaceans-have-plans` の `docs/GAME_SPEC.md`・`docs/LORE_AND_STORY.md`・`docs/UNKNOWN_NATURAL_PHENOMENA.md` | 深度帯と現象案（見た目の方向だけ）。文書は変更していません |
| 実在の深海の景観 (鯨骨生物群集・ガラス海綿・チューブワーム・マンガン団塊) | 形のモチーフ。実在の図や写真・コードは使っていません |
