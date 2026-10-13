# KIBA-REAL-CITY

KIBA-REAL-CITY プロジェクトの素材置き場です。

- **取り込み済みモデル**：`assets/kiba-real-city/`（NEXUS の COLLECTION で `kiba-real-city` を選ぶと表示）
- **候補リスト（未取得）**：[character-candidates.md](character-candidates.md)

## 取り込み済み

### FORGE メカ（7 体・すべて CC0）

| ID | モデル | 高さ | 三角形 | アニメーション |
|---|---|---:|---:|---|
| `forge_atlas_09` | ATLAS / 09 — 歴戦の重装巨大メカ（シアンの発光コア） | 18 m | 26,519 | 10 種（Sentinel, Walk, Run, PunchCombo, KneelFire, Backflip, Hit 系, Knockback, Collapse） |
| `forge_aether_02` | AETHER / 02 — 白いスリムな人型、スモークガラスの胸とバイザー | 14 m | 24,310 | 11 種（上記＋DodgeRoll） |
| `forge_seraph_03` | SERAPH / 03 — 銀の可動翼と腕キャノンを持つ黒チタンのメカ | 20 m | 30,858 | 9 種（Flight, WingDeploy ほか） |
| `forge_ronin_04` | RONIN / 04 — 刀を持つ赤い侍メカ | 16 m | 31,533 | 12 種（SwordSlash, SwordCombo, SwordBlock, BladeSalute ほか） |
| `forge_scorpio_05` | SCORPIO / 05 — ハサミと尾の毒針を持つサソリ型メカ | 17 m | 30,445 | 6 種（ClawSlash, StingerStrike ほか） |
| `forge_titan_06` ⚠ | TITAN / 06 — 1970 年代風スーパーロボット（青い装甲、ロケットパンチ） | 19 m | 27,579 | 6 種（RocketPunch, ChestBeam ほか） |
| `forge_vanguard_07` ⚠ | VANGUARD / 07 — リアルロボット系の軍用メカ（ビームライフルと盾） | 18 m | 27,320 | 7 種（RifleBurst, ShieldGuard, BoostJump ほか） |

- **出典**：[RamonLinares/atlas-09](https://github.com/RamonLinares/atlas-09)（FORGE — Character Lab）、コミット `1b8fb9d54160215c071c5a29a49b1c36dc01f0df` の `public/models/`
- **ライセンス**：CC0 1.0（作者 Ramon Linares）。商用・改変・再配布可、クレジット不要。証拠は `assets/kiba-real-city/mecha/licenses/` に保存しています。
- **加工**：なし。配布元の GLB をそのまま保存しています（SHA-256 一致）。
- **スケール**：1 単位 = 1 m（実寸）。原点は足元です。
- ⚠ **TITAN / 06 と VANGUARD / 07**：有名な既存ロボット作品によく似たデザインです。CC0 は作者自身の権利しか対象にしません（配布元の `ASSET-LICENSE.md` にも「第三者の権利・商標は含まない」と明記）。商用で使う場合は、形や配色を変えるなどの検討をおすすめします。NEXUS では `ip-caution` タグを付けています。

### Quaternius アニメーション（2 本・CC0）

| ID | 内容 |
|---|---|
| `quaternius_ual1_selected` | Universal Animation Library 1 から 9 クリップ（Walk_Loop, Jog_Fwd_Loop, Sprint_Loop, Punch_Jab, Punch_Cross, Death01, Hit_Chest, Hit_Head, Roll） |
| `quaternius_ual2_selected` | Universal Animation Library 2 から 7 クリップ（Melee_Hook, Melee_Hook_Rec, Hit_Knockback, Sword_Regular_Combo, Sword_Block, Sword_Regular_B, Sword_Regular_B_Rec） |

- 骨格とアニメーションだけのファイルです（メッシュなし、プレビューには何も映りません）。Universal Base Characters など人型リグにリターゲットして使います。
- 作者：Quaternius、Gonzalo Furnier。CC0 1.0（元のライセンス文と `provenance.json` を `assets/kiba-real-city/animations/licenses/` に保存）。
- atlas-09 リポジトリが公式配布から切り出したサブセットで、ハッシュは同リポジトリの記録と一致しています。

### 取り込んでいないもの（atlas-09 リポジトリ内）

- 各メカの Blender ソース（`blender/*.blend`）：編集用。必要なら追加できます。
- Tripo の生成直後／リトポ直後の中間メッシュ（`assets/*/source`, `assets/*/retopo`）：リグ・アニメーションなしの途中データのため除外しました。

### 注意

- FORGE メカはすべて AI 生成を含む工程で作られています（OpenAI の画像生成でコンセプト → Tripo で 3D 化 → Blender でリグとアニメーション。歩行・パンチなどは Quaternius の CC0 アニメーションを転用）。詳細は配布元の `ASSET-PROVENANCE.md` にあります。
- メカは 1 体あたり 6〜8 MB・2.4〜3.2 万三角形・2048px テクスチャのヒーロー素材です。画面に 1〜2 体出すボスや主役メカ向けで、大量配置には向きません。軽量版が必要なら、テクスチャ縮小などで別途作成します。
