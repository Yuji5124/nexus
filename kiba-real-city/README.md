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

### 人型キャラクター（15 体・すべて CC0）

| ID | 名前 | 内容 | アニメ数 | 三角形 | サイズ |
|---|---|---|---:|---:|---:|
| `kaykit_barbarian` | KayKit Barbarian | Barbarian warrior with axe | 76 | 6,543 | 3.4 MB |
| `kaykit_knight` | KayKit Knight | Armoured knight with sword and shield | 76 | 6,952 | 3.5 MB |
| `kaykit_mage` | KayKit Mage | Robed mage with staff | 76 | 5,683 | 3.4 MB |
| `kaykit_rogue` | KayKit Rogue | Agile rogue with daggers and crossbow | 76 | 6,377 | 3.4 MB |
| `kaykit_rogue_hooded` | KayKit Rogue Hooded | Hooded variant of the rogue | 76 | 6,035 | 3.4 MB |
| `kaykit_skeleton_mage` | KayKit Skeleton Mage | Skeleton mage enemy | 95 | 4,588 | 4.5 MB |
| `kaykit_skeleton_minion` | KayKit Skeleton Minion | Small skeleton minion enemy | 95 | 5,288 | 4.6 MB |
| `kaykit_skeleton_rogue` | KayKit Skeleton Rogue | Skeleton rogue enemy | 95 | 5,278 | 4.6 MB |
| `kaykit_skeleton_warrior` | KayKit Skeleton Warrior | Skeleton warrior enemy | 95 | 5,934 | 4.6 MB |
| `kenney_arena_soldier` | Kenney Arena Soldier | Tiny soldier with idle/walk/sprint/jump/attack clips | 32 | 513 | 0.1 MB |
| `kenney_pirate_captain` | Kenney Pirate Captain | Blocky pirate captain, rigged (no animations) | 0 | 428 | 0.0 MB |
| `kenney_pirate_crew` | Kenney Pirate Crew | Blocky pirate crew member, rigged (no animations) | 0 | 356 | 0.0 MB |
| `kenney_pirate_officer` | Kenney Pirate Officer | Blocky pirate officer, rigged (no animations) | 0 | 466 | 0.0 MB |
| `kenney_zombie_1` | Kenney Zombie 1 | Blocky zombie, rigged (no animations) | 0 | 1,604 | 0.2 MB |
| `kenney_zombie_2` | Kenney Zombie 2 | Blocky zombie variant, rigged (no animations) | 0 | 1,604 | 0.1 MB |

- **KayKit（9 体）**：Kay Lousberg 作。[Adventurers 1.0](https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0)（`672074b`）と [Skeletons 1.0](https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Skeletons-1.0)（`15b62b9`）の公式 GitHub から取得し、無加工で保存しています。全員が同じ 41 関節リグで、攻撃・移動・被弾など 76〜95 種のアニメーションを内蔵しています。Godot Asset Library にも同じリポジトリとコミットが登録されています。
- **Kenney（6 体）**：ゾンビ 2 体と海賊 3 体（pmndrs market 経由、Kenney 作で CC0）はリグのみでアニメーションなしです。Quaternius UAL などを移植して使います。Arena Soldier（Mini Arena）は 32 種のアニメーション付きです。glTF / 外部テクスチャを単一 GLB にまとめています。
- ライセンス証拠は `assets/kiba-real-city/characters/licenses/` にあります。再生成は `node scripts/kiba-real-city/import-characters.mjs` → `npm run scan` です。
- **既に NEXUS にある CC0 人型（GIANT CLIMB 収録・7 体）**：`kenney_male`, `kenney_survivor_male`, `kenney_survivor_female`, `kenney_skater_male`, `kenney_skater_female`, `kenney_cyborg_female`（リグのみ）、`platformer_character`（アニメ 4 種）。候補として合わせて選べます。
- **除外したもの**：100 Avatars（Polygonal Mind）は CC-BY 4.0 で「大きな改変なしの販売禁止」の条件付きのため除外しました。npm パッケージ内の KayKit 複製（Ranger など）は、KayKit のライセンス文が同梱されておらず出所を確認できないため除外しました。

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
