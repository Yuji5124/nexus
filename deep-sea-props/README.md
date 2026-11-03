# DEEP-SEA PROPS｜深海の効果・拾得品・小道具

深海を舞台にしたゲーム向けの、**オブジェクト 20 点**です。光や波などの**効果の素材 8 点**、拾うと嬉しい**拾得品 6 点**、海底を飾る**小道具・地形 6 点**。

- **モデル**：`assets/deep-sea-props/`（NEXUS の COLLECTION で `deep-sea-props` を選ぶと表示）／サムネイル：`thumbnails/deep-sea-props/`
- **軽さ**：1点 168〜1,388 三角形、11〜75 KB（合計約 614 KB）。**テクスチャなし**。
- **単位・向き**：1 unit = 1 m、Y が上、原点は底の中心（効果は基準点）、正面は +Z。
- **ライセンス**：NEXUS のオリジナル（スクリプトで生成）。まだライセンスを決めていないので `UNKNOWN` にしています。

## 効果の素材 (effect) — 半透明に重ねて使う

| ID | 名前 | 内容 | 大きさ (m) |
|---|---|---|---|
| `fx_bubble_cluster` | Bubble Column | Sixteen translucent bubbles of growing size rising in a loose column about 4.1 m tall | 1.0 × 4.1 × 1.0 |
| `fx_current_vortex` | Current Vortex | Two translucent ribbons spiralling three turns up an 8 m column: the look of a strong deep-sea current or whirlpool | 7.2 × 8.0 × 6.8 |
| `fx_energy_orb` | Energy Orb | Glowing core inside a translucent shell with three orbiting rings (cyan and amber) | 2.4 × 2.4 × 2.4 |
| `fx_headlight_beam` | Headlight Beam | Translucent light cone for a submarine headlight or flashlight: apex at the origin, 14 m long, 9 m wide at the end, with a brighter inner cone and an amber lamp point | 9.2 × 9.2 × 14.2 |
| `fx_light_shaft` | Light Shaft | 30 m tall tapered light shaft from the surface, three nested translucent cylinders so the centre reads brighter | 9.2 × 30.0 × 9.2 |
| `fx_shockwave_ring` | Shockwave Ring | Flared ring-shaped shockwave, 8 m across, with a bright glowing inner lip | 8.0 × 0.5 × 8.0 |
| `fx_sonar_ring` | Sonar Pulse Rings | Three concentric thin rings (3, 6, 9 m radius) plus a glowing centre disc | 18.1 × 0.1 × 18.1 |
| `fx_spark_burst` | Spark Burst | Twenty-eight radial spikes (alternating cyan and amber) around a hot core | 3.5 × 3.3 × 3.2 |

- 材質 `beam` / `glass` は **alpha blend**（半透明）で、発光しています。Three.js では透明パスで描き、`depthWrite = false` にし、光らせたいときは `AdditiveBlending` にします。拡大・回転・フェードはコードで付けてください（アニメは入れていません）。

## 拾得品 (item) — ゲームで拾えるもの

| ID | 名前 | 内容 | 大きさ (m) |
|---|---|---|---|
| `item_ancient_coin` | Ancient Coins | A stack of five gold coins with a glowing glyph ring on top and two loose coins beside it | 1.2 × 0.5 × 1.0 |
| `item_heal_pearl` | Healing Pearl | Healing pickup: an open stone bivalve cradling a glass pearl with a green glowing heart | 1.2 × 0.7 × 1.1 |
| `item_relic_tablet` | Relic Tablet | Relic pickup: a small stone tablet on a base with a glowing ring glyph and an amber stud, about 1.2 m tall | 1.0 × 1.2 × 1.0 |
| `item_rune_key` | Rune Key | Key pickup: gold key with a round bow, three teeth and a glowing glyph gem | 0.6 × 1.2 × 0.2 |
| `item_shard_crystal` | Shard Crystal | Currency pickup: a cluster of six glowing cyan crystals on a small stone base, about 1.3 m tall | 1.1 × 1.3 × 1.1 |
| `item_treasure_chest` | Sunken Treasure Chest | Closed barrel-lidded wooden chest with iron bands, a gold lock plate and a glowing keyhole, 1.3 m wide | 1.3 × 1.2 × 0.9 |

## 小道具・地形 (prop)

| ID | 名前 | 内容 | 大きさ (m) |
|---|---|---|---|
| `prop_anchor` | Sunken Anchor | Rusted iron anchor standing upright, 4.6 m tall, with a ring, stock bar, curved arms and a little coral growth | 3.0 × 4.6 × 0.5 |
| `prop_basalt_cluster` | Basalt Column Cluster | Eleven six-sided basalt columns of different heights (0.8-4.2 m): the rock of the blue-phosphor basin, and a fine cliff dressing | 2.7 × 3.9 × 3.0 |
| `prop_boulder_large` | Large Boulder | A big lumpy boulder (4.2 m wide) with five smaller lumps around its base | 4.4 × 2.8 × 4.1 |
| `prop_coral_fan` | Fan Coral | Fan-shaped sea fan: a stem on a stone base fanning into eleven branches with glowing tips and three arcs of fine mesh | 3.2 × 2.3 × 0.9 |
| `prop_crate_stack` | Crate Stack | Three wooden crates with iron straps stacked and tilted, plus a banded barrel | 3.5 × 1.9 × 1.5 |
| `prop_vent_chimney` | Hydrothermal Vent Chimney | Stacked stone chimney 4.6 m tall with a glowing amber mouth, ringed by small stalks with glowing green tips | 3.6 × 4.7 × 3.8 |

(大きさは `data/assets.json` の `dimensions` の値。)

## 見た目の約束

- **石**：頂点色で、下ほど暗く青緑に苔むす風化。形は少しゆがめた低ポリ（フラットシェーディング）。
- **光る部分**：`glow`（シアン）・`warm`（琥珀）・`bio`（緑）は発光マテリアル。ブルームを足すと映えます。`metal`（錆びた鉄）・`gold`・`wood` は普通の不透明材質です。
- 遺跡キット (`deep-sea-ruins`) と敵キャラ (`deep-sea-enemies`) と同じ約束 (単位・向き・材質の考え方) なので、同じ場面に並べられます。

## 作り直す・増やすとき

```sh
# Blender 4.x / 5.x が必要 (ヘッドレスで GLB とサムネイルを書き出す)
blender -b -P scripts/deep-sea-props/build_props.py -- assets/deep-sea-props thumbnails/deep-sea-props
npm run deep-sea-props     # data/assets.json に記録して scan
```

- 形・材質・名前・説明は `scripts/deep-sea-props/parts.py` の関数と `MODELS`（元データ）。1 行足すと増やせます。`catalog.json` は全点を作り直すと自動で書き直されます。
- 第 4 引数以降に ID を並べると、そのモデルだけ作り直せます。

## 参考にしたもの (コード・素材は一切使っていません)

| 参考 | ライセンス | 参考にした点 |
|---|---|---|
| 一般的なゲームの VFX の作り方 (光の筒・衝撃波リング・ソナー波) | - | 半透明のメッシュに発光を持たせ、拡大とフェードで見せる、という作り方 |
| [glTF Transform](https://github.com/donmccurdy/glTF-Transform) | MIT | 寸法・容量の計測と記録 (NEXUS の既存の仕組みと同じ道具) |
| [three.js](https://github.com/mrdoob/three.js) | MIT | 透明パス・`AdditiveBlending` での描画の前提 |

## 次に作るもの

進み具合は [../deep-sea-ruins/PROGRESS.md](../deep-sea-ruins/PROGRESS.md) を参照してください。
