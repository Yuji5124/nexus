# RANVORA ver2

[RANVORA ver2](https://github.com/Yuji5124/RANVORA-ver2)（three.js × Blender の低ポリ箱庭ゲーム）の 3D データです。

- **モデル**：`assets/ranvora-ver2/`（NEXUS の COLLECTION で `ranvora-ver2` を選ぶと表示）
- **元にしたコミット**：`Yuji5124/RANVORA-ver2` の `dd2657be122dae3d512280b010f3dfb054c9dde8`（PR #6 マージ時点）
- **単位**：1 unit = 1 m、Y が上、正面は +Z。原点は足元（接地点）です。
- **ライセンス**：持ち主（Yuji5124）のオリジナル作品です。まだライセンスを決めていないため、NEXUS では `UNKNOWN` にしています。決まったら各レコードの `license` を書き換えてください。

## 取り込み済み（20 点）

### 主人公（2 体・ボーン 33 本・7 アクション）

| ID | 内容 | 三角形 | サイズ |
|---|---|---:|---:|
| `ranvora_v2_traveler` | 謎の旅人（ver2 の既定の主人公）。フードとマントの約 3.5 頭身 | 4,814 | 479 KB |
| `ranvora_v2_original_hero` | 初代 RANVORA 主人公（比較・復旧用） | 15,162 | 706 KB |

- 2 体は同じ骨格で、アクションも共通です：Idle, Walk, Run, Jump, SwordSlash, StaffSwing, MagicCast。
- 剣・杖・魔法エフェクトは別メッシュで、手のボーンに付いています。
- ver2 の `.gltf.json`（バッファ埋め込み形式）を GLB に詰め替えただけで、形・骨格・アニメーションの数値は変えていません。
- ゲーム内では旅人を 1.32 倍、初代を 1.3 倍にして使っています（`units.gameScale`）。

### 自然物（15 種類・68 バリエーション）

ver2 のコード（`src/world/Props.ts`）が既定のシードで作るものと同じ形・色です。1 つの GLB に、その種類のバリエーションを X 方向に横並びで入れています（ルート直下の子 1 つ = 1 バリエーション）。

| ID | 内容 | 数 | 三角形 |
|---|---|---:|---:|
| `ranvora_v2_pine` | 松（針葉樹） | 5 | 1,170 |
| `ranvora_v2_spruce` | トウヒ（細長い針葉樹） | 4 | 1,108 |
| `ranvora_v2_broadleaf` | オーク風の広葉樹 | 5 | 4,430 |
| `ranvora_v2_autumn` | 紅葉したカエデ | 4 | 3,352 |
| `ranvora_v2_birch` | 白樺 | 5 | 4,770 |
| `ranvora_v2_sakura` | 桜 | 4 | 2,996 |
| `ranvora_v2_willow` | 柳 | 3 | 10,725 |
| `ranvora_v2_cypress` | イトスギ | 4 | 808 |
| `ranvora_v2_dead` | 枯れ木 | 3 | 858 |
| `ranvora_v2_bush` | 茂み | 5 | 420 |
| `ranvora_v2_rock` | 岩（大岩・平石・岩の群れ） | 8 | 660 |
| `ranvora_v2_mossy_rock` | 苔むした岩 | 4 | 320 |
| `ranvora_v2_crag` | 尖った岩山 | 4 | 180 |
| `ranvora_v2_pebbles` | 小石 | 4 | 420 |
| `ranvora_v2_flowers` | 花の群れ（黄・ピンク・白） | 6 | 660 |

- 頂点カラー＋マテリアル 1 つのフラットシェーディングです。テクスチャはありません。
- **ver2 に戻すとき**：GLB を `public/models/` に置き、`src/assets/manifest.ts` の `MODEL_OVERRIDES` に同じキーで登録すれば、そのまま散布に使えます（ver2 の読み込みは子の位置を無視するので、横並びのままで大丈夫です）。
- **1 本だけ使うとき**：ルート直下の子を 1 つ取り出し、X 位置を 0 に戻してください。

### 建物・敵・アイテム（3 点）

| ID | 内容 | 三角形 | サイズ |
|---|---|---:|---:|
| `ranvora_v2_log_cabin` | 中に入れる丸太小屋（室内 8 × 6.4 m、家具・暖炉付き） | 10,934 | 1.5 MB |
| `ranvora_v2_slime` | スライム（最初の敵） | 196 | 14 KB |
| `ranvora_v2_slime_gel` | スライムゼリー（スライムが落とす素材） | 8 | 2 KB |

- **丸太小屋**：ver2 の世界と同じシード（1378）で作りました。コードで描いた木目・屋根・石のテクスチャを埋め込んでいます。暖炉とランタンの明かり（点光源 2 つ）と炎の揺れはコード側の演出なので外しました。凹凸（バンプ）も glTF に入らないため外れています。当たり判定と床の高さは `Cabin.ts` にあり、GLB には入っていません。
- **スライム・ゼリー**：止まった姿です。跳ねる・つぶれる・光るなどの動きは ver2 のコード（`src/combat/EnemyView.ts`）で付けています。

## 取り込まなかったもの

- **地形・川・道・草・雲**：その世界専用の形か、シェーダーで動くもので、単体のモデルになりません。
- **繊細な木（EZ-Tree）**：外部ライブラリ（ez-tree）の樹皮・葉のテクスチャを使っています。ライブラリのテクスチャの権利を確かめていないため、今回は入れていません。
- **Blender の低ポリキット（`blender/lowpoly_kit.py`）**：Blender で実行して作るもので、ver2 のリポジトリには書き出した GLB がありません。

## 作り直すとき

```sh
npm run ranvora-ver2
```

`.cache/ranvora-ver2` に RANVORA ver2 を上のコミットで取得し、主人公の GLB 変換、ヘッドレス Chromium での書き出し（ver2 自身の Vite でビルド）、サムネイル作成、`data/assets.json` の更新、`npm run scan` まで行います。手元のチェックアウトを使うときは `RANVORA_VER2_DIR=<パス>` を指定します（同じコミットで、`node_modules` が必要です）。新しい ver2 を取り込むときは、`scripts/ranvora-ver2/import.mjs` の `COMMIT` を変えてください。
