# KIBA-REAL-CITY — キャラクター素材候補

KIBA-REAL-CITY 用のキャラクター（人型素体）候補リストです。機械向けの同じ内容は [character-candidates.json](character-candidates.json) にあります。

> **状態：候補（未取得・未検証）**
> 内容は依頼時に共有された情報をそのまま記録したものです。モデルファイルはまだ NEXUS に取り込んでいません。
> ライセンスと配布ページは、取り込み前に配布元で確認してください（この環境からは quaternius.com に接続できず、未確認です）。
> 5 パックとも Quaternius 作のパックと思われます。配布ページの URL は推定で、元の共有ではリンクが失われていました。

| # | パック | 内容 | 用途の目安 | ライセンス | 形式 |
|---|---|---|---|---|---|
| 1 | **Universal Base Characters**（Regular / Teen） | 6 種類の素体から選択、リグ付き | **最も 7 頭身に近づけやすい候補** | CC0 | glTF / FBX |
| 2 | **Ultimate Modular Men** | 男性 11 種類、24 アニメーション。衣装やパーツを変更可能 | 男性キャラクター・市民 | CC0 | glTF / FBX |
| 3 | **Ultimate Modular Women** | 女性 10 種類、24 アニメーション | 少し柔らかいデザインの主人公向き | CC0 | glTF / FBX |
| 4 | **RPG Character Pack** | ファンタジー系 6 種類 | 武器を持つ冒険者・戦士 | CC0 | FBX / OBJ / Blend |
| 5 | **Cyberpunk Game Kit** | SF 系の主人公と敵キャラクター | 未来都市を舞台にするゲーム向き | CC0 | glTF / FBX |

## 配布ページ（推定・未確認）

1. Universal Base Characters — https://quaternius.com/packs/universalbasecharacters.html
2. Ultimate Modular Men — https://quaternius.com/packs/ultimatemodularmen.html
3. Ultimate Modular Women — https://quaternius.com/packs/ultimatemodularwomen.html
4. RPG Character Pack — https://quaternius.com/packs/rpgcharacters.html
5. Cyberpunk Game Kit — https://quaternius.com/packs/cyberpunkgamekit.html

## 取り込み時のメモ

- NEXUS の他コレクションと同じく、単一 GLB（テクスチャ埋め込み）に変換し、ライセンス証拠と出典 URL を保存します。
- RPG Character Pack は glTF 配布がないため、FBX から GLB への変換が必要です。
- 7 頭身に合わせる場合は、Universal Base Characters（Regular）を基準素体にし、頭部スケールを調整するのが近道です。
