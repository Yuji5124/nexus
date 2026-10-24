# LOWPOLY TREES

GitHub 上の著作権フリー（CC0）のデータから選んだ、ローポリの木 10 種類です。

- **モデル**：`assets/lowpoly-trees/`（NEXUS の COLLECTION で `lowpoly-trees` を選ぶと表示）
- **ライセンス**：すべて **CC0 1.0**。商用・改変・再配布ができ、クレジットも不要です（任意で「Kenney」「Kay Lousberg」と書くと作者の応援になります）。証拠は `assets/lowpoly-trees/licenses/` に保存しています。
- **軽さ**：1 本あたり 50〜490 三角形、11〜36 KB。マテリアルは 1〜3 個で、大量に並べても軽く動きます。

## 10 種類

| ID | 木 | 三角形 | 推奨の倍率 → 高さ | 作者・出典 |
|---|---|---:|---|---|
| `kaykit_pine` | 松（濃い緑の三角形を重ねた定番の形） | 50 | ×7.5 → 9 m | KayKit Medieval Hexagon Pack |
| `kaykit_fir_round` | 丸いモミ（なめらかな 3 段） | 220 | ×5.8 → 7 m | KayKit Medieval Hexagon Pack |
| `kaykit_pine_autumn_orange` | 紅葉した松（オレンジ） | 318 | ×1.07 → 8 m | KayKit Halloween Bits |
| `kaykit_pine_autumn_yellow` | 黄葉した松（金色） | 318 | ×1.07 → 8 m | KayKit Halloween Bits |
| `kaykit_dead_tree` | 枯れ木 | 256 | ×1.38 → 7 m | KayKit Halloween Bits |
| `kenney_palm` | ヤシ | 488 | ×3.8 → 8 m | Kenney（pmndrs/market-assets 経由） |
| `kenney_oak` | オーク（丸い樹冠・青緑） | 196 | ×5.7 → 7 m | Kenney Nature Kit |
| `kenney_oak_autumn` | 紅葉したオーク（オレンジ・白い幹） | 196 | ×5.7 → 7 m | Kenney Nature Kit |
| `kenney_tree_branching` | 枝分かれした広葉樹 | 402 | ×6.0 → 8 m | Kenney Nature Kit |
| `kenney_tree_plateau` | 台地型の木（アカシア・盆栽風） | 215 | ×5.6 → 7 m | Kenney Nature Kit |

- 元のキットは実寸ではありません（多くは高さ 1.2 m 前後）。各レコードの `units.suggestedScale` を掛けると、上の表の高さになります。原点は幹の根元です。
- KayKit の 5 本は小さなカラーパレット画像（テクスチャ 1 枚）で色を付けています。Kenney の 5 本は色だけのマテリアルです。

## 出典

| 出典 | リポジトリとコミット | 使った木 |
|---|---|---|
| KayKit Medieval Hexagon Pack 1.0（公式） | [KayKit-Game-Assets/KayKit-Medieval-Hexagon-Pack-1.0](https://github.com/KayKit-Game-Assets/KayKit-Medieval-Hexagon-Pack-1.0) `84fa4e9` | 松・丸いモミ |
| KayKit Halloween Bits 1.0（公式） | [KayKit-Game-Assets/KayKit-Halloween-Bits-1.0](https://github.com/KayKit-Game-Assets/KayKit-Halloween-Bits-1.0) `6dc69bf` | 紅葉・黄葉の松、枯れ木 |
| Kenney（pmndrs のモデル集） | [pmndrs/market-assets](https://github.com/pmndrs/market-assets) `c9cfa02` | ヤシ |
| Kenney Nature Kit 2.1 | [JasonLee228/cruiz](https://github.com/JasonLee228/cruiz) `536be42`、[bborbe/driftline](https://github.com/bborbe/driftline) `f93766d` | オーク・紅葉オーク・枝分かれ・台地型 |

**Kenney Nature Kit について**：Kenney は Nature Kit を GitHub で配布していないため、このキットを Kenney のライセンス文と一緒に同梱しているゲームのリポジトリから取得しました。改変されていないことを次の方法で確かめています。

- 3 つの別々のリポジトリ（cruiz、driftline、[jpabloglez/trailpaw](https://github.com/jpabloglez/trailpaw) の Git LFS ハッシュ）で、同じファイルのハッシュが一致すること。
- ファイルに Kenney の書き出しツール名（UniGLTF-1.27）が残っていること。
- 同梱のライセンス文が Kenney 公式のもの（Nature Kit 2.1、CC0）であること。

## 加工した点

形・UV・テクスチャは変えていません。次の点だけ直しています（各レコードの `optimization` に記録）。

- **glTF を 1 つの GLB に**：KayKit とヤシは `.gltf`＋`.bin`＋画像の組なので、1 ファイルにまとめました。ヤシは Draco 圧縮を展開し、デコーダなしで読めるようにしています。
- **Kenney の金属度**：Kenney の書き出しは金属度が 1（鏡のような金属）になっていて、環境マップがないと真っ黒に見えます。テクスチャのないマテリアルを金属度 0・粗さ 1 にしました。
- **Kenney Nature Kit の色**：書き出しツール UniGLTF 1.27 が、色を本来とは別の色空間（sRGB）の値のまま保存しているため、そのままだと白っぽく見えます（葉 `#29c9ab` が `#70e6d6` になる）。色の値を正しい色空間（リニア）に変換し、Kenney 本来の色で表示されるようにしました。

## 作り直すとき

```sh
npm run lowpoly-trees
```

固定したコミットで各リポジトリを `.cache/lowpoly-trees/` に取得し、ライセンスを確認、GLB 化、サムネイル作成、`data/assets.json` の更新、`npm run scan` まで行います。
