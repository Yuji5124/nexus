# ROAD DRIVER asset pack

NEXUSから選定した45点の軽量GLBです。ROAD DRIVER本体のコードは含みません。完全な機械可読一覧は manifest.json。元のNEXUSライブラリは維持され、このフォルダーには採用モデルだけを収録します。

- 合計モデル容量: 1.45 MiB (1,520,616 bytes)
- ライセンス: 全件 CC0 1.0。各モデルの出典・ライセンス根拠と SHA-256 は manifest に記録。元の根拠文書は licenses/。
- GLB は再圧縮せず複製し、SHA-256 と glTF Transform での GLB 読み込み・三角形数を照合。
- Up axis は Y。車両の前方は +Z を初期値として記録。車種ごとに向きを確認して配置し、逆なら Y 軸を180度回転してください。bounds と原単位の推奨倍率は manifest に記録。
- 同一内容の重複なし。繰り返し配置では同じモデルを共有し、同一マテリアルの大量配置には InstancedMesh を検討してください。

## 内訳

| Category | Count |
|---|---:|
| VEHICLE | 12 |
| ROAD PROPS | 8 |
| CITY | 10 |
| NATURE | 6 |
| FUTURE | 9 |

## Three.js 取り込み例

このパック内の models/ と manifest.json をゲームの静的アセット領域へコピーし、manifest の model パスを基準にロードします。

```js
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
const manifest = await (await fetch('/assets/road-driver/manifest.json')).json();
const car = manifest.assets.find(asset => asset.id === 'kenney_sedan');
const gltf = await new GLTFLoader().loadAsync('/assets/road-driver/' + car.model);
gltf.scene.scale.setScalar(car.units.metresPerUnit ?? 1);
gltf.scene.position.y = -car.boundingBox.min[1] * (car.units.metresPerUnit ?? 1);
scene.add(gltf.scene);
```

既存NEXUS GitHub MCPを使う場合は、collection: "giant-climb" と tags: ["road-driver"] で検索した後、download_asset を呼び出せます。ゲームへ全215点をコピーせず、配布パックまたはmanifestに載った採用IDだけを利用してください。
