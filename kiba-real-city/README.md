# KIBA-REAL-CITY

KIBA-REAL-CITY プロジェクトの素材置き場です。

- **取り込み済みモデル**：`assets/kiba-real-city/`（NEXUS の COLLECTION で `kiba-real-city` を選ぶと表示）
- **候補リスト（未取得）**：[character-candidates.md](character-candidates.md)

## 取り込み済み

| ID | モデル | 高さ | 三角形 | アニメーション | サイズ |
|---|---|---:|---:|---|---:|
| `forge_atlas_09` | FORGE ATLAS / 09 — 歴戦の重装巨大メカ（シアンの発光コア） | 18 m | 26,519 | 10 種（Sentinel, Walk, Run, PunchCombo, KneelFire, Backflip, HitChest, HitHead, Knockback, Collapse） | 6.9 MB |
| `forge_ronin_04` | FORGE RONIN / 04 — 刀を持つ赤い侍メカ | 16 m | 31,533 | 12 種（上記の一部＋SwordSlash, SwordCombo, SwordBlock, BladeSalute） | 7.6 MB |

- **出典**：[RamonLinares/atlas-09](https://github.com/RamonLinares/atlas-09)（FORGE — Character Lab）、コミット `1b8fb9d54160215c071c5a29a49b1c36dc01f0df` の `public/models/`
- **ライセンス**：CC0 1.0（作者 Ramon Linares）。商用・改変・再配布可、クレジット不要。証拠は `assets/kiba-real-city/mecha/licenses/` に保存しています。
- **加工**：なし。配布元の GLB をそのまま保存しています（SHA-256 一致）。リグ・PBR テクスチャ・アニメーションは無加工です。
- **スケール**：1 単位 = 1 m（実寸）。原点は足元です。

### 注意

- 両モデルとも AI 生成を含む工程で作られています（OpenAI の画像生成でコンセプト → Tripo で 3D 化 → Blender でリグとアニメーション。歩行・パンチなどは Quaternius の CC0 アニメーションを転用）。詳細は配布元の `ASSET-PROVENANCE.md` にあります。
- 1 体あたり約 7 MB・2〜3 万三角形・2048px テクスチャのヒーロー素材です。画面に 1〜2 体出すボスや主役メカ向けで、大量配置には向きません。軽量版が必要なら、テクスチャ縮小などで別途作成します。
