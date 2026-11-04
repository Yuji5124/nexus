# DEEP-PEARL SEA｜水深4,500m「乳白色の海」の背景オブジェクト

『甲殻類にも都合があります。』の水深 **4,500m**（世界の「脱皮」で生まれた、真珠のように白く輝く海）の**背景オブジェクト 20 点**です。コンセプトアート指示（白いサンゴ・半透明の殻の森・真珠質の結晶・遠景の白い神殿とアーチ・巨大な抜け殻が地形になる・殻の粉が雪のように積もる）を、見た目だけ部品にした案です。

- **ボス「誰もいない王（ムレ）」の造形は含みません**（ボスは別途 ChatGPT と進める方針）。ここにある小魚 2 点は、ふつうの小魚と群れの雲で、ボスの身体ではありません。
- **モデル**：`assets/deep-pearl-sea/`（NEXUS の COLLECTION で `deep-pearl-sea` を選ぶと表示）／サムネイル：`thumbnails/deep-pearl-sea/`
- **軽さ**：1点 126〜4,200 三角形、11〜257 KB（合計約 1.4 MB）。**テクスチャなし**。
- **単位・向き**：1 unit = 1 m、Y が上、原点は底の中心、正面は +Z。
- **ライセンス**：NEXUS のオリジナル（スクリプトで生成）。まだライセンスを決めていないので `UNKNOWN` にしています。

## 出現深度と意味は「提案」です

出現は水深 4,500m 付近の提案で、仕様ではありません。脱皮が起きる仕組み、神殿やアーチをつくった者、殻の粉の海流の意味は**決めていません**（見た目だけ）。

### 海底・遺跡の小道具と地形 (13 点)

| ID | 名前 | 内容 | 大きさ (m) | 三角形 |
|---|---|---|---|---|
| `prop_husk_arch` | Moulted Husk Arch | A giant empty husk forming an arch about 16 m wide and 8 m high: nine ribbed shell arcs joined by a ridge, open at the back | 16.6 × 7.9 × 14.0 | 2,324 |
| `prop_nacre_leaf_forest` | Nacre Leaf Forest | Ten translucent mother-of-pearl leaves up to 4 m tall with thin pearl veins on a pearl mound: the translucent shell forest of the milky sea | 3.1 × 4.3 × 3.0 | 904 |
| `prop_pearl_clam` | Pearl Clam | A giant open bivalve about 4 m wide holding five pearls on a nacre floor | 3.9 × 3.0 × 3.5 | 1,386 |
| `prop_pearl_coral` | Pearl Coral | White branching coral on a pearl mound, two trunks with pale pink tips, about 3 m tall | 2.5 × 3.2 × 2.3 | 2,432 |
| `prop_pearl_crystal_giant` | Giant Pearl Crystal | Six pearly hexagonal crystals with pink points, the tallest 6.5 m, with small pearls at the base | 3.5 × 6.5 × 3.5 | 708 |
| `prop_pearl_heap` | Pearl Heap | A heap of sixty pearls of mixed size (some pink) on a shadow-coloured base, about 3 m across | 2.9 × 1.4 × 3.2 | 2,304 |
| `prop_peeling_plates` | Peeling Shell Layers | Six old shell plates lifting like pages off a fresh nacre layer, with pink pearls around | 6.2 × 3.7 × 5.1 | 468 |
| `prop_shell_dust_dune` | Shell-dust Drift | A low drift of shell dust about 8 m wide, like snow, with wind lines, shell chips and a few floating motes | 8.3 × 3.3 × 5.9 | 748 |
| `prop_shell_spire` | Shell Spire | A tall spiral shell about 8 m high, twelve twisted whorls with pink and nacre rims | 4.1 × 8.3 × 3.9 | 2,356 |
| `prop_terrace_falls` | Terraced Falls | Three stacked white rock terraces about 5 m high with thin water curtains running down each step | 8.6 × 5.1 × 8.8 | 740 |
| `prop_white_arch_gate` | White Arch Gate | A stone arch gate about 8 m high with a gold keystone and faint jade marks on the pillars | 9.0 × 8.4 × 2.6 | 524 |
| `prop_white_colonnade` | White Colonnade | A 13 m colonnade of five fluted columns with gold rings, one broken, with a half-fallen beam | 13.0 × 6.5 × 3.0 | 1,520 |
| `prop_white_dome_pavilion` | White Dome Pavilion | A small domed temple about 7 m tall: three steps, eight columns, a gold ring and a gold finial | 7.2 × 7.3 × 7.2 | 1,136 |

### 半透明の効果 (5 点)

| ID | 名前 | 内容 | 大きさ (m) | 三角形 |
|---|---|---|---|---|
| `fx_dust_current` | Shell-dust Current | Two translucent bands and 36 specks of dust spiralling 1.4 turns up a 9 m column: the unseen current the dust draws | 5.1 × 9.0 × 5.6 | 1,004 |
| `fx_iridescent_veil` | Iridescent Veil | Three wavy translucent ribbons (white, pink, jade) drifting along 10 m | 10.6 × 2.3 × 4.5 | 174 |
| `fx_light_curtain` | Light Curtain | Three nested wide translucent light shafts, 25 m high and up to 18 m across, for the soft light that comes from every direction | 17.8 × 25.0 × 18.0 | 208 |
| `fx_molt_sheet` | Moulting Sheet | A thin translucent sheet of old shell, 5 m across, peeling off and curling up at one end | 4.6 × 2.2 × 3.4 | 152 |
| `fx_nacre_bubbles` | Nacre Bubbles | Sixteen translucent bubbles of growing size in a loose 4 m column, each with a tiny highlight | 1.3 × 4.1 × 1.5 | 1,408 |

### 小魚 (2 点)

| ID | 名前 | 内容 | 大きさ (m) | 三角形 |
|---|---|---|---|---|
| `fauna_pearl_fish` | Pearl Fish | One small pearl-white fish 0.5 m long with a gold tail, fins and eyes | 0.3 × 0.3 × 0.6 | 126 |
| `fx_fish_swarm_cloud` | Fish Swarm Cloud | Seventy small fish in a loose S-shaped flow 14 m long, all heading the same way, no leader | 14.0 × 4.3 × 8.3 | 4,200 |

(大きさは `data/assets.json` の `dimensions` の値。)

## 見た目の約束

- **色**：白（`pearl`）・桃がかった真珠（`nacre`）・薄桃（`pink`）・翡翠（`jade`）・薄紫の影（`shadow`）・金（`gold`）。青一色にならないよう、白・淡い金・翡翠・薄桃・虹色の偏光を混ぜる前提です。`pearl` / `nacre` / `pink` / `jade` は弱く発光するので、少しブルームを足すと映えます。
- **半透明（`alpha` タグ）**：`glass` / `leaf` / `dust` / `veil` / `rosev` / `jadev` は alpha blend の発光。Three.js では透明パスで描き、`depthWrite = false` にしてください。拡大・回転・フェードはコードで付けます（アニメは入れていません）。
- **使い方の案**：`prop_husk_arch` と `prop_peeling_plates` は「抜け殻が地形になる／殻が剥がれて新しい層が出る」表現、`fx_molt_sheet` は脱皮の膜、`fx_dust_current` は殻の粉が描く海流、`fx_light_curtain` は全方向からのやわらかい光に使えます。
- 遺跡・敵・小道具・潜水艦のコレクションと同じ約束（単位・向き）です。

## 作り直す・増やすとき

```sh
# ヘッドレス (Blender 4.x / 5.x)
blender -b -P scripts/deep-pearl-sea/build_pearl_parts.py -- assets/deep-pearl-sea thumbnails/deep-pearl-sea
npm run deep-pearl-sea     # data/assets.json に記録して scan
```

- ライブの Blender (Blender MCP) では `exec(open("scripts/deep-pearl-sea/build_pearl_parts.py").read(), {"__name__": "nexus_pearl"})` のあと `run()` で、専用コレクション `NEXUS_PEARL` に作って並べられます（今回は Blender MCP に接続できなかったため、ヘッドレスの Blender 4.4 で作りました）。
- 形・名前・説明は `scripts/deep-pearl-sea/pearl_parts.py`。**注意**：新しい GLB を置いたあとに `npm run scan` だけを先に走らせると記録が簡易版で重複します。必ず先に `npm run deep-pearl-sea` で登録してください。

## 参考にしたもの (コード・素材は一切使っていません)

| 参考 | 参考にした点 |
|---|---|
| ユーザーのコンセプトアート指示と画像（水深4,500m・乳白色の海） | 色・地形・遺跡・脱皮の表現の方向。画像そのものはリポジトリに入れていません |
| `crustaceans-have-plans` の `docs/UNKNOWN_NATURAL_PHENOMENA.md`・`docs/LORE_AND_STORY.md` | 脱皮は自然現象で、怪物や遺跡は必ずしも悪ではない、という設定 |
