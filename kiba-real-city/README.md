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

### リアル等身の人型（20 体・MIT ライセンス）

7〜8 頭身のリアルな人物です。[Microsoft Rocketbox Avatar Library](https://github.com/microsoft/Microsoft-Rocketbox)（コミット `0943055`）から、軍人・特殊部隊・警察・警備・パイロット・消防士・アスリート・ビジネスの 20 体を選んでいます。

| ID | 内容 | 身長 | 三角形 | サイズ |
|---|---|---:|---:|---:|
| `rocketbox_business_female_01` | Businesswoman in dark suit | 1.74 m | 8,966 | 2.9 MB |
| `rocketbox_business_male_01` | Businessman in dark suit and tie | 1.81 m | 7,435 | 2.2 MB |
| `rocketbox_fire_female_01` | Female firefighter in turnout gear with helmet | 1.87 m | 11,988 | 3.7 MB |
| `rocketbox_fire_male_01` | Firefighter in turnout gear with helmet | 1.86 m | 8,551 | 2.8 MB |
| `rocketbox_military_female_01` | Female soldier in ACU camouflage with helmet | 1.78 m | 13,015 | 3.9 MB |
| `rocketbox_military_female_02` | Female soldier in ACU camouflage | 1.78 m | 12,957 | 4.0 MB |
| `rocketbox_military_male_01` | Soldier in ACU camouflage with helmet and gear | 1.84 m | 15,387 | 4.7 MB |
| `rocketbox_military_male_02` | Soldier in ACU camouflage with cap | 1.81 m | 8,231 | 3.6 MB |
| `rocketbox_military_male_03` | Soldier in ACU camouflage with helmet | 1.85 m | 15,517 | 4.1 MB |
| `rocketbox_military_male_04` | Soldier in ACU camouflage with helmet and goggles | 1.85 m | 14,907 | 3.8 MB |
| `rocketbox_pilot_female_02` | Female airline pilot in uniform | 1.78 m | 8,458 | 2.8 MB |
| `rocketbox_pilot_male_01` | Airline pilot in uniform | 1.84 m | 7,664 | 2.1 MB |
| `rocketbox_police_female_01` | Female tactical police / SWAT officer with helmet | 1.85 m | 13,514 | 4.4 MB |
| `rocketbox_police_male_01` | Police officer in blue uniform | 1.81 m | 8,687 | 3.3 MB |
| `rocketbox_police_male_02` | Tactical police / SWAT officer in black gear with balaclava | 1.84 m | 10,881 | 3.2 MB |
| `rocketbox_police_male_03` | Police officer in dark uniform with cap | 1.86 m | 12,445 | 3.4 MB |
| `rocketbox_security_female_01` | Female security guard in dark uniform | 1.74 m | 8,973 | 3.0 MB |
| `rocketbox_security_male_01` | Security guard in dark uniform | 1.83 m | 9,515 | 3.2 MB |
| `rocketbox_sports_female_02` | Female athlete in tank top and trousers | 1.74 m | 8,580 | 2.6 MB |
| `rocketbox_sports_male_04` | Athlete in tank top and shorts | 1.80 m | 7,520 | 2.6 MB |

- **ライセンス：MIT**（Copyright (c) 2020 Microsoft）。商用利用・改変・再配布ができます。CC0 と違い、**配布するときは著作権表示とライセンス文を同梱する**必要があります。ライセンス文は `assets/kiba-real-city/realistic/licenses/` に保存しています。
- **リグ**：全員が同じ 80 関節（3ds Max Biped）です。**Idle・Walk・Run** の 3 種類を各モデルに埋め込みました（男女別の Rocketbox 公式モーション。Walk と Run はその場で動く形に加工済み）。同じ骨格向けのモーションが配布元にさらに 417 種あり、必要なら追加できます。
- **加工内容**：FBX を FBX2glTF で GLB に変換しました。TGA テクスチャは JPEG（顔 2048px、その他 1024px）に変換し、カラーとノーマルマップを付けています。スペキュラーマップは glTF の方式と合わないため外しました。
- **再生成**：`FBX2GLTF=<FBX2glTF のパス> node scripts/kiba-real-city/import-rocketbox.mjs` を実行し、続けて `npm run scan` を実行します。ImageMagick が必要です。

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
