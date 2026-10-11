# ROAD DRIVER 選定モデル・検証レポート

- 採用: 45点、合計 1,520,616 bytes (1.45 MiB)。
- 三角形数: 合計 29,871、最大 2,588 / モデル。
- 形式: GLB 45/45。CC0-1.0 45/45。サムネイル 45/45。SHA-256重複なし。
- 検証: 選定前にNEXUS内215点の既存コレクションを調査。採用GLBをglTF Transform NodeIOで全件読み込み、三角形数を既存メタデータと照合。SHA-256は元ファイルと同一であることを確認。既存のThree.js GLTFLoaderサムネイル生成パイプラインを利用。
- 向き/スケール: 全モデルY-up。寸法と原点boundsはmanifestの値。vehicleはnative +Z前方を初期配置値とし、異なる道路座標系ならY軸180°回転。原単位倍率を各asset.units.metresPerUnitに記録。
- 軽量性評価: 全モデル 1 MiB 未満、最大三角形数は本表参照。繰り返し配置ではGLBを共有し、同形状の多数配置にInstancedMeshを推奨。テクスチャ付きは既存少数の街路樹/草/レース車両のみ。
- ライセンス: 全件CC0-1.0。各レコードのsourceUrlとlicenseEvidenceはmanifestに含み、原文書はlicenses/に収録。

## カテゴリー

| Category | Count |
|---|---:|
| VEHICLE | 12 |
| ROAD PROPS | 8 |
| CITY | 10 |
| NATURE | 6 |
| FUTURE | 9 |

## 採用一覧

| ID | モデル | Category | Bytes | Triangles | Dimensions (native) | Materials | Textures | metres/unit |
|---|---|---|---:|---:|---|---:|---:|---:|
| kenney_sedan | Sedan | VEHICLE | 78,988 | 1,932 | 1.50 × 1.30 × 2.50 | 8 | 0 | 1.8 |
| kenney_sports_sedan | Sports Sedan | VEHICLE | 79,488 | 1,940 | 1.30 × 1.10 × 2.50 | 8 | 0 | 1.8 |
| kenney_hatchback | Hatchback | VEHICLE | 81,812 | 1,984 | 1.30 × 1.10 × 2.80 | 8 | 0 | 1.8 |
| kenney_suv | Suv | VEHICLE | 86,264 | 2,328 | 1.50 × 1.30 × 2.70 | 7 | 0 | 1.8 |
| kenney_taxi | Taxi | VEHICLE | 73,924 | 1,968 | 1.95 × 1.95 × 3.51 | 8 | 0 | 1.8 |
| kenney_van | Van | VEHICLE | 43,264 | 1,092 | 1.80 × 1.56 × 3.24 | 7 | 0 | 1.8 |
| kenney_truck | Truck | VEHICLE | 44,160 | 1,108 | 1.50 × 1.30 × 2.90 | 8 | 0 | 1.8 |
| kenney_truck_flat | Truck Flat | VEHICLE | 49,064 | 1,230 | 1.50 × 1.30 × 2.75 | 9 | 0 | 1.8 |
| kenney_delivery_truck | Delivery Truck | VEHICLE | 107,308 | 2,328 | 1.50 × 1.60 × 3.20 | 10 | 0 | 1.8 |
| kenney_police_car | Police Car | VEHICLE | 87,220 | 2,200 | 1.50 × 1.30 × 3.00 | 9 | 0 | 1.8 |
| kenney_ambulance | Ambulance | VEHICLE | 102,580 | 2,588 | 1.50 × 1.70 × 3.20 | 8 | 0 | 1.8 |
| racing_vehicle_truck_yellow | Vehicle Truck Yellow | VEHICLE | 56,956 | 989 | 1.50 × 1.55 × 2.80 | 1 | 1 | 1.8 |
| citykit_road_straight | Road Straight | ROAD PROPS | 14,544 | 54 | 1.00 × 0.05 × 1.00 | 1 | 1 | 12 |
| citykit_road_corner | Road Corner | ROAD PROPS | 17,160 | 126 | 1.00 × 0.06 × 1.00 | 1 | 1 | 12 |
| citykit_road_intersection | Road Intersection | ROAD PROPS | 18,840 | 154 | 1.00 × 0.05 × 1.00 | 1 | 1 | 12 |
| citykit_road_split | Road Split | ROAD PROPS | 16,516 | 100 | 1.00 × 0.05 × 1.00 | 1 | 1 | 12 |
| citykit_road_straight_lightposts | Road Straight Lightposts | ROAD PROPS | 20,644 | 190 | 1.00 × 0.55 × 1.00 | 1 | 1 | 12 |
| city_sidewalk_barrier | City Sidewalk Barrier | ROAD PROPS | 4,800 | 60 | 4.00 × 0.80 × 0.08 | 1 | 0 | 1 |
| city_traffic_light | City Traffic Light | ROAD PROPS | 12,892 | 152 | 4.15 × 5.50 × 0.41 | 5 | 0 | 1 |
| city_street_lamp | City Street Lamp | ROAD PROPS | 7,048 | 68 | 1.64 × 7.00 × 0.30 | 3 | 0 | 1 |
| city_apartment_block | City Apartment Block | CITY | 45,628 | 672 | 16.40 × 30.60 × 11.60 | 5 | 0 | 1 |
| city_corner_store | City Corner Store | CITY | 10,000 | 84 | 14.60 × 6.50 × 10.20 | 6 | 0 | 1 |
| city_office_tower | City Office Tower | CITY | 21,492 | 304 | 19.00 × 59.20 × 19.00 | 4 | 0 | 1 |
| city_pencil_building | City Pencil Building | CITY | 18,872 | 192 | 6.50 × 28.00 × 8.20 | 9 | 0 | 1 |
| citykit_building_garage | Building Garage | CITY | 21,504 | 196 | 1.00 × 0.55 × 1.00 | 1 | 1 | 12 |
| citykit_building_small_a | Building Small A | CITY | 33,796 | 452 | 1.00 × 0.95 × 1.00 | 1 | 1 | 12 |
| citykit_building_small_b | Building Small B | CITY | 39,996 | 600 | 1.00 × 1.63 × 1.00 | 1 | 1 | 12 |
| citykit_building_small_c | Building Small C | CITY | 54,328 | 834 | 1.00 × 1.75 × 1.00 | 1 | 1 | 12 |
| citykit_building_small_d | Building Small D | CITY | 33,260 | 448 | 1.00 × 1.00 × 1.05 | 1 | 1 | 12 |
| kenney_house_7 | House 7 | CITY | 19,040 | 398 | 1.20 × 0.85 × 0.81 | 4 | 0 | 8 |
| assets_nature_tree_demo_tree | NEXUS Low Poly Demo Tree | NATURE | 11,404 | 104 | 1.80 × 2.60 × 1.80 | 2 | 0 | 1 |
| citykit_grass | Grass | NATURE | 13,556 | 30 | 1.00 × 0.06 × 1.00 | 1 | 1 | 12 |
| citykit_grass_trees | Grass Trees | NATURE | 28,356 | 380 | 1.00 × 0.64 × 1.00 | 1 | 1 | 12 |
| citykit_grass_trees_tall | Grass Trees Tall | NATURE | 32,408 | 472 | 1.07 × 0.76 × 1.01 | 1 | 1 | 12 |
| fpskit_platform_large_grass | Platform Large Grass | NATURE | 18,980 | 180 | 5.20 × 0.50 × 5.20 | 1 | 1 | 2 |
| platformer_platform_grass_large_round | Platformer Platform Grass Large Round | NATURE | 16,352 | 124 | 5.00 × 0.50 × 5.00 | 1 | 1 | 1.3 |
| space_structure | Structure | FUTURE | 9,280 | 168 | 1.00 × 1.00 × 1.00 | 2 | 0 | 4 |
| space_structure_closed | Structure Closed | FUTURE | 13,188 | 264 | 1.00 × 1.00 × 1.00 | 3 | 0 | 4 |
| space_structure_detailed | Structure Detailed | FUTURE | 13,136 | 232 | 1.00 × 1.00 × 1.00 | 3 | 0 | 4 |
| space_supports_high | Supports High | FUTURE | 17,108 | 312 | 0.82 × 1.00 × 0.82 | 3 | 0 | 4 |
| space_supports_low | Supports Low | FUTURE | 11,168 | 184 | 0.82 × 0.50 × 0.82 | 3 | 0 | 4 |
| space_monorail_track_straight | Monorail TrackStraight | FUTURE | 2,980 | 28 | 0.20 × 0.13 × 1.00 | 2 | 0 | 4 |
| space_monorail_track_support | Monorail TrackSupport | FUTURE | 9,928 | 176 | 0.20 × 0.50 × 0.20 | 3 | 0 | 4 |
| space_monorail_track_corner_large | Monorail TrackCornerLarge | FUTURE | 8,240 | 204 | 1.60 × 0.13 × 1.60 | 2 | 0 | 4 |
| space_monorail_train_front | Monorail TrainFront | FUTURE | 13,144 | 242 | 0.60 × 0.80 × 1.05 | 3 | 0 | 4 |

NEXUSのdata/assets.json内の採用45レコードにroad-driverタグ、ROAD DRIVER分類、推奨用途、配置方法を追加しました。既存の他のアセットと検索機能はそのままです。
