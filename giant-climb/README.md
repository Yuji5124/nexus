# GIANT CLIMB アセットコレクション

3Dクライミングアクション「GIANT CLIMB」（東京に現れた巨大ロボットを登り、内部を探索して中枢を停止させる）向けに、NEXUS へ登録した **215 点の GLB モデル** です。

- すべて **CC0 1.0**（パブリックドメイン）。商用利用・改変・再配布にクレジット表記は不要です（任意で [CREDITS](../assets/giant-climb/CREDITS.md)）。
- すべて**単一ファイル GLB**（テクスチャ埋め込み済み・Draco 圧縮なし）。Three.js でも Java 3D 系ローダーでもそのまま読めます。
- 1 モデルあたり **20,000 三角形以下・1 MB 以下**（実際の最大は 3,237 三角形、合計約 4.9 MB）。
- 各モデルにサムネイル（`thumbnails/giant-climb/*.png`）、出典 URL（コミット固定）、元ファイルの SHA-256、ゲーム用途タグを付けています。

集計と除外理由は [REPORT.md](REPORT.md) を参照してください。

## 内訳

| カテゴリ | 点数 | 内容 |
|---|---:|---|
| `robot-interior` | 66 | 通路・配管・足場フレーム・階段・手すり・機械・制御卓・動力コア・縦穴ハシゴ |
| `robot-exterior` | 40 | 装甲板（手掛かり付き）・関節・ピストン・手のひら・指・足・背骨・頭部・アンテナ・スラスター |
| `city-street` | 26 | 首都高風高架道路・歩道橋・電柱・信号・自販機・横断歩道・モノレール軌道・道路タイル |
| `platform` | 25 | 汎用足場・ブロック・壁 |
| `vehicle` | 20 | 乗用車・タクシー・パトカー・救急車・消防車・トラック・モノレール車両 |
| `city-building` | 16 | オフィスタワー・マンション・ペンシルビル・コンビニ・屋上給水塔・室外機・看板・電波塔 |
| `gameplay` | 9 | チェックポイント・収集アイテム（ナット・エネルギーセル・コイン）・停止レバー・ゴール旗 |
| `character` | 9 | プレイヤー仮モデル（アニメ付き）・市民（リグ付き）・飛行ドローン敵・ロボット（14 アニメーション） |
| `prop` / `environment` | 4 | ドラム缶・雲 |

出典：Kenney Space Kit（97）、NEXUS オリジナル（56）、Kenney Car Kit ほか（pmndrs market 経由、22）、Kenney Starter Kits（39）、Quaternius RobotExpressive（1）。

## AI / ゲームコードからの使い方

インデックス：`https://raw.githubusercontent.com/Yuji5124/nexus/main/data/assets.json`（`collection === "giant-climb"` で絞り込み）

主なフィールド：

| フィールド | 意味 |
|---|---|
| `gameRoles` | `climbable-surface` 登れる面 / `handhold` 掴める / `platform` 乗れる / `walkable-floor` 歩ける床 / `modular-kit` タイル状に並べる / `obstacle` / `hazard` / `goal` / `collectible` / `enemy` / `character` / `vehicle-prop` / `landmark` / `decoration` / `background` |
| `climbable` | `gameRoles` に `climbable-surface` か `handhold` を含むと `true` |
| `units.metresPerUnit` | ゲーム内でメートルに合わせるための推奨倍率（モデル自体は元スケールのまま） |
| `units.suggestedSizeMetres` | 推奨倍率をかけたときのサイズ [x, y, z]（m） |
| `dimensions` / `boundingBox` | ノード変換を反映したワールド座標の寸法（モデル単位） |
| `sourceUrl` / `sourceRevision` / `sourceSha256` | 出典ファイル（コミット固定）と元データのハッシュ |

スケールの目安：プレイヤー（少年）≈ 1.4 m。NEXUS オリジナルは 1 単位 = 1 m、原点は底面中央、+Y が上です。Space Kit は 1 単位 = 4 m（通路幅 4 m）、City Builder は 1 単位 = 12 m（1 ブロック）。巨大ロボット（RobotExpressive）は `metresPerUnit: 12` で約 54 m になります。

```js
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
const index = await (await fetch('https://raw.githubusercontent.com/Yuji5124/nexus/main/data/assets.json')).json();
const holds = index.filter(a => a.collection === 'giant-climb' && a.gameRoles.includes('handhold'));
const asset = index.find(a => a.id === 'robot_armor_plate_handholds');
new GLTFLoader().load(asset.previewUrl, gltf => {
  gltf.scene.scale.setScalar(asset.units.metresPerUnit);
  scene.add(gltf.scene);
});
```

NEXUS オリジナルはマテリアル名が固定（`gc_steel`, `gc_armor`, `gc_red`, `gc_yellow`, `gc_glow`, `gc_glowRed`, `gc_glass` など）なので、名前で色替え・発光演出ができます。MCP サーバーの `search_assets` でも `collection: "giant-climb"`、`role`、`climbable` で検索できます。

## 再生成

```sh
npm ci
npm run giant-climb        # 出典取得 → 生成 → 最適化 → サムネイル → メタデータ → scan
```

- `scripts/giant-climb/fetch-sources.mjs` — `giant-climb/catalog.mjs` の固定コミット / npm integrity で出典を `.cache/` に取得。取得物は実行しません。
- `scripts/giant-climb/generate-originals.mjs` — GIANT CLIMB 専用のオリジナル 56 点を Three.js で手続き生成。
- `scripts/giant-climb/import.mjs` — ライセンス確認（ソースごとの証拠ファイル / market の `info.json`）、重複排除、glTF Transform（dedup・prune・weld・unpartition、Draco 展開、テクスチャ埋め込み）、予算チェック、出力、メタデータ、CREDITS / REPORT 作成。条件を満たさないものは採用しません。
- `scripts/giant-climb/thumbnails.mjs` — ヘッドレス Chromium（Playwright）で 256×256 サムネイルを描画。

アセットを追加・除外するときは `giant-climb/catalog.mjs` を編集して再実行してください。

## 制約・注意

- この環境からは kenney.nl / quaternius.com / poly.pizza / polyhaven.com / opengameart.org に直接アクセスできなかったため、GitHub・npm 上にライセンス文書付きで公開されているコピーのみを使いました。
- 規約を出典元で確認できなかったもの（Blend Swap 由来など）は、アグリゲーターが CC0 と表示していても除外しています。
- 依頼文の添付コンセプト画像はこのセッションでは受け取れていないため、配色や形状は依頼文の記述（ローポリ・ブロック感・PS2 世代の軽さ・巨大感）に合わせています。
- 市民キャラクターはリグのみ（アニメーションなし）、Kenney 住宅は郊外風の造形です。
