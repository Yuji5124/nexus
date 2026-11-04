"""誰もいない王 (ムレ) の書き出し (純 Python。Blender なしで動く)。

  python scripts/deep-pearl-sea/build_boss_mure.py <出力フォルダ>

出力:
  boss_mure_school.bin      40,000 匹の小魚の配置 (float32 x 11、manifest 参照)。ゲームはこれを InstancedMesh で描く想定。
  boss_mure_school.json     bin の説明 (欄・部位・色・座標・大きさ)
  boss_mure_preview.glb     確認用 (1/4 の間引き + 小魚を大きめに)。1 匹 = 6 頂点の細長い八面体、頂点色で 4 色。
  boss_mure_fish.glb        小魚 1 匹の低ポリ (インスタンス用の元)。
"""
import json
import math
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boss_mure as B

PALETTE = ((0.86, 0.88, 0.92), (0.97, 0.93, 0.88), (0.96, 0.80, 0.42), (0.95, 0.72, 0.80))


def fish_tris(length=1.0):
    """1 匹: 細長い八面体 (+Z が鼻)。頂点 6、三角形 8。"""
    l, w, h = length, length * 0.16, length * 0.22
    v = [(0, 0, l * 0.55), (0, 0, -l * 0.45), (w, 0, 0), (-w, 0, 0), (0, h, 0), (0, -h * 0.8, 0)]
    # 尾びれ代わりに後ろの頂点を少し広げる
    v[1] = (0, 0, -l * 0.5)
    idx = [(0, 2, 4), (0, 4, 3), (0, 3, 5), (0, 5, 2), (1, 4, 2), (1, 3, 4), (1, 5, 3), (1, 2, 5)]
    return v, idx


def _rot_to(d):
    """+Z を d に向ける行列の列 (right, up, fwd)。"""
    f = B._norm(d)
    r = B._cross((0, 1, 0), f)
    if B._dot(r, r) < 1e-6:
        r = B._cross((1, 0, 0), f)
    r = B._norm(r)
    u = B._cross(f, r)
    return r, u, f


def _pad(b):
    return b + b"\0" * ((4 - len(b) % 4) % 4)


def write_glb(path, positions, indices, colors, name, material_name="school"):
    pos = b"".join(struct.pack("<3f", *p) for p in positions)
    col = b"".join(struct.pack("<4B", *[int(c * 255) for c in c4]) for c4 in colors)
    big = len(positions) > 65535
    idx = b"".join(struct.pack("<I" if big else "<H", i) for tri in indices for i in tri)
    parts = [_pad(pos), _pad(col), _pad(idx)]
    offs = [0, len(parts[0]), len(parts[0]) + len(parts[1])]
    binary = b"".join(parts)
    xs = [p[0] for p in positions]
    ys = [p[1] for p in positions]
    zs = [p[2] for p in positions]
    gltf = {
        "asset": {"version": "2.0", "generator": "NEXUS boss_mure.py"},
        "scene": 0, "scenes": [{"nodes": [0]}], "nodes": [{"mesh": 0, "name": name}],
        "meshes": [{"name": name, "primitives": [{"attributes": {"POSITION": 0, "COLOR_0": 1}, "indices": 2, "material": 0}]}],
        "materials": [{"name": material_name, "pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0.3, "roughnessFactor": 0.35},
                       "emissiveFactor": [0.08, 0.08, 0.10], "doubleSided": True, "extras": {"note": "vertex colour = silver / pearl / gold / pink"}}],
        "buffers": [{"byteLength": len(binary)}],
        "bufferViews": [{"buffer": 0, "byteOffset": offs[0], "byteLength": len(pos), "target": 34962},
                        {"buffer": 0, "byteOffset": offs[1], "byteLength": len(col), "target": 34962},
                        {"buffer": 0, "byteOffset": offs[2], "byteLength": len(idx), "target": 34963}],
        "accessors": [{"bufferView": 0, "componentType": 5126, "count": len(positions), "type": "VEC3", "min": [min(xs), min(ys), min(zs)], "max": [max(xs), max(ys), max(zs)]},
                      {"bufferView": 1, "componentType": 5121, "normalized": True, "count": len(colors), "type": "VEC4"},
                      {"bufferView": 2, "componentType": 5125 if big else 5123, "count": len(indices) * 3, "type": "SCALAR"}],
    }
    js = _pad(json.dumps(gltf, separators=(",", ":")).encode()).replace(b"\0", b" ") if False else json.dumps(gltf, separators=(",", ":")).encode()
    js += b" " * ((4 - len(js) % 4) % 4)
    with open(path, "wb") as fh:
        fh.write(struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(js) + 8 + len(binary)))
        fh.write(struct.pack("<I4s", len(js), b"JSON") + js)
        fh.write(struct.pack("<I4s", len(binary), b"BIN\0") + binary)
    return len(positions), len(indices)


def preview(fish, every=4, grow=2.2):
    P, I, C = [], [], []
    base_v, base_i = fish_tris(B.FISH_LEN * grow)
    for n, f in enumerate(fish):
        if n % every:
            continue
        x, y, z, dx, dy, dz = B.to_three([f])[0][:6]
        r, u, fw = _rot_to((dx, dy, dz))
        s = f[9]
        o = len(P)
        for (vx, vy, vz) in base_v:
            P.append((x + (r[0] * vx + u[0] * vy + fw[0] * vz) * s, y + (r[1] * vx + u[1] * vy + fw[1] * vz) * s, z + (r[2] * vx + u[2] * vy + fw[2] * vz) * s))
            C.append(PALETTE[int(f[10])] + (1.0,))
        I += [(o + a, o + b, o + c) for a, b, c in base_i]
    return P, I, C


def main(out):
    os.makedirs(out, exist_ok=True)
    fish = B.build()
    n = B.write_bin(os.path.join(out, "boss_mure_school.bin"), fish)
    man = B.manifest(fish)
    json.dump(man, open(os.path.join(out, "boss_mure_school.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    P, I, C = preview(fish)
    pv = write_glb(os.path.join(out, "boss_mure_preview.glb"), P, I, C, "boss_mure_preview")
    v, i = fish_tris(B.FISH_LEN)
    write_glb(os.path.join(out, "boss_mure_fish.glb"), v, i, [PALETTE[0] + (1.0,)] * 6, "boss_mure_fish")
    print("fish", n, "preview verts/tris", pv[0], pv[1])


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "assets/deep-pearl-sea/boss-mure")
