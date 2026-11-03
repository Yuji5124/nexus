# DEEP-SEA RUINS｜深海の古代遺跡キット

深海を舞台にしたゲーム向けの、**古代遺跡の3Dモデル 25 点**です。柱・アーチ・壁・階段・祭壇・オベリスク・守り神の像・泉・灯り・床・瓦礫・施設 (工房・ドック・天秤・泉)・深海生物のまとわり。

- **モデル**：`assets/deep-sea-ruins/`（NEXUS の COLLECTION で `deep-sea-ruins` を選ぶと表示）／サムネイル：`thumbnails/deep-sea-ruins/`
- **軽さ**：1点 500〜1,550 三角形、25〜90 KB（合計約 790 KB）。**テクスチャなし**。
- **単位・向き**：1 unit = 1 m、Y が上、原点は底面の中心（底が y = 0）。正面は +Z。
- **ライセンス**：NEXUS のオリジナル（スクリプトで生成）。まだライセンスを決めていないので `UNKNOWN` にしています（`LICENSE` を宣言したら `catalog.mjs` / `import.mjs` の `license` を直してください）。

## 内訳

| 区分 | モデル |
|---|---|
| 建造物 (structure) | `ruin_pillar_intact` `ruin_pillar_broken` `ruin_pillar_fallen` `ruin_arch_gate` `ruin_arch_broken` `ruin_wall_straight` `ruin_wall_broken` `ruin_altar` `ruin_obelisk` `ruin_guardian_statue` `ruin_dome_shrine` |
| 床・段 (floor) | `ruin_stairs` `ruin_platform_octagon` `ruin_rune_floor_ring` `ruin_floor_tile` |
| 飾り (decor) | `ruin_fountain` `ruin_lantern_stele` |
| 瓦礫 (rubble) | `ruin_rubble_a` `ruin_rubble_b` |
| 施設 (station) | `ruin_station_forge` (武器工房) `ruin_station_dock_gate` (潜水艦ドック) `ruin_station_scale` (交換所の天秤) `ruin_station_spring` (回復の泉) |
| 深海生物 (bio) | `ruin_coral_cluster` `ruin_tube_worms` |

## 見た目の約束

- **石**：頂点色で、下ほど暗く青緑に苔むす風化を付けています。形は少しゆがめた低ポリ（フラットシェーディング）。
- **光る部分**：紋様（シアン）・灯りと宝珠（琥珀）・深海生物の先端（緑）は**発光マテリアル**です。Three.js では `UnrealBloomPass` などのブルームを足すと光ります。
- **使い方の例**：遺跡の敷地は `ruin_floor_tile` / `ruin_rune_floor_ring` を床にし、`ruin_pillar_intact` を8本の輪に並べて中央に `ruin_altar`。入口に `ruin_arch_gate` と `ruin_guardian_statue`、四隅に `ruin_obelisk`、参道に `ruin_lantern_stele`、周りに `ruin_rubble_*` と `ruin_coral_cluster`。
- 各モデルは 2〜4 個のメッシュ（`*_stone` `*_glow` ほか）に分かれています。当たり判定は石のメッシュの外形から作ってください。

## 作り直す・増やすとき

```sh
# Blender 4.x / 5.x が必要 (ヘッドレスで GLB とサムネイルを書き出す)
blender -b -P scripts/deep-sea-ruins/build_ruins.py -- assets/deep-sea-ruins thumbnails/deep-sea-ruins
npm run deep-sea-ruins     # data/assets.json に記録して scan
```

- 形は `scripts/deep-sea-ruins/build_ruins.py` の関数 (`pillar_intact` など)。`MODELS` に 1 行足すと増やせます。第 4 引数以降にモデル ID を並べると、そのモデルだけ作り直せます。
- 名前・説明・用途は `scripts/deep-sea-ruins/catalog.mjs`。
- 風化の揺らぎはモデル名から決まるシードで固定です。同じ設定なら毎回同じファイルになります。

## 参考にしたもの (コード・素材は一切使っていません)

| 参考 | ライセンス | 参考にした点 |
|---|---|---|
| [KayKit Dungeon Remastered](https://github.com/KayKit-Game-Assets/KayKit-Dungeon-Remastered-1.0) | CC0 (配布元の表記) | 柱・壁・床・階段を**グリッドに並べるモジュール式キット**という分け方と、壊れた版を対にする考え方 |
| [Kenney の各キット](https://kenney.nl/assets) (Castle Kit など) | CC0 | 部品名の付け方、単位をそろえて置くだけで組み上がる寸法の決め方 |
| [glTF Transform](https://github.com/donmccurdy/glTF-Transform) | MIT | 寸法・容量の計測と記録 (NEXUS の既存の仕組みと同じ道具) |
| [three.js](https://github.com/mrdoob/three.js) | MIT | 実機での読み込み確認 (`GLTFLoader`) の前提 |

形そのものは、ゲーム『甲殻類にも都合があります。』の試作 (遺跡と施設の記号的な造形) を元に、このキット用に作り直したオリジナルです。

## 次に作るもの

進み具合は [PROGRESS.md](PROGRESS.md) を参照してください。
