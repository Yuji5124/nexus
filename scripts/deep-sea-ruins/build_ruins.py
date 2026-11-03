"""DEEP-SEA RUINS: 深海の古代遺跡キット (NEXUS オリジナル)。Blender (4.x/5.x) をヘッドレスで動かして GLB とサムネイルを作る。

    blender -b -P scripts/deep-sea-ruins/build_ruins.py -- <出力フォルダ> <サムネイルのフォルダ> [モデルID ...]

規約: 1 unit = 1 m、原点は足元の中心 (底面が 0)、glTF 出力後は Y が上。
材質は3種類だけ (どれもテクスチャなし):
  stone  ... 石。頂点色で「下ほど暗く青緑に苔むす」風化を付ける (Principled、Color Attribute)
  glow   ... 発光する紋様 (シアン)
  warm   ... 発光する灯り・宝珠 (琥珀)
  bio    ... 深海生物の発光部 (ピンクがかった緑)
形は記号的。外部のモデル・画像・コードは使っていない (参考にしたもの: scripts/deep-sea-ruins/README の「参考」を参照)。
"""
import bpy, bmesh, math, os, sys, random
from mathutils import Matrix, Vector, Euler

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = os.path.abspath(argv[0]) if argv else os.path.abspath("out")
THUMBS = os.path.abspath(argv[1]) if len(argv) > 1 else os.path.join(OUT, "_thumbs")
ONLY = set(argv[2:])
PI = math.pi
os.makedirs(OUT, exist_ok=True)
os.makedirs(THUMBS, exist_ok=True)


# ---------------------------------------------------------------- 形の道具 (bmesh)
class Shape:
    """材質ごとの bmesh を持つ。part() で形を足す。"""

    def __init__(self):
        self.bm = {k: bmesh.new() for k in ("stone", "glow", "warm", "bio")}

    def _put(self, key, verts, loc, scale, rot):
        m = Matrix.Translation(loc) @ Euler(rot).to_matrix().to_4x4() @ Matrix.Diagonal((*scale, 1))
        bmesh.ops.transform(self.bm[key], matrix=m, verts=verts)

    def box(self, loc=(0, 0, 0), size=(1, 1, 1), rot=(0, 0, 0), key="stone", base=False):
        """size は全幅。base=True なら loc の z を底面の高さにする。"""
        v = bmesh.ops.create_cube(self.bm[key], size=1)["verts"]
        c = (loc[0], loc[1], loc[2] + size[2] / 2 if base else loc[2])
        self._put(key, v, c, size, rot)

    def cyl(self, loc=(0, 0, 0), r=(1, 1), h=1, seg=12, rot=(0, 0, 0), key="stone", base=False, flute=0.0):
        """円柱・円すい台。r=(下の半径, 上の半径)。flute>0 なら溝 (半径を交互に縮める)。"""
        res = bmesh.ops.create_cone(self.bm[key], cap_ends=True, cap_tris=False, segments=seg, radius1=r[0], radius2=max(r[1], 1e-4), depth=1)
        verts = res["verts"]
        if flute > 0:
            for v in verts:
                a = math.atan2(v.co.y, v.co.x)
                k = int(round(a / (2 * PI / seg))) % 2
                if k == 1 and abs(v.co.z) > 1e-6 or (k == 1 and True):
                    f = 1 - flute
                    v.co.x *= f
                    v.co.y *= f
        c = (loc[0], loc[1], loc[2] + h / 2 if base else loc[2])
        self._put(key, verts, c, (1, 1, h), rot)

    def cone(self, loc=(0, 0, 0), r=1, h=1, seg=8, rot=(0, 0, 0), key="stone", base=False):
        self.cyl(loc, (r, 0.0), h, seg, rot, key, base)

    def sphere(self, loc=(0, 0, 0), r=(1, 1, 1), seg=10, key="stone"):
        v = bmesh.ops.create_uvsphere(self.bm[key], u_segments=seg, v_segments=max(4, seg // 2 + 1), radius=1)["verts"]
        self._put(key, v, loc, r, (0, 0, 0))

    def ring(self, loc=(0, 0, 0), R=1.0, r=0.05, seg=36, rot=(0, 0, 0), key="glow", scale=(1, 1, 1), sub=6):
        """太さのある輪 (トーラス)。XY 平面。"""
        bm = self.bm[key]
        grid = []
        for i in range(seg):
            a = 2 * PI * i / seg
            row = []
            for j in range(sub):
                b = 2 * PI * j / sub
                rad = R + r * math.cos(b)
                row.append(bm.verts.new((rad * math.cos(a), rad * math.sin(a), r * math.sin(b))))
            grid.append(row)
        for i in range(seg):
            n = (i + 1) % seg
            for j in range(sub):
                k = (j + 1) % sub
                try:
                    bm.faces.new((grid[i][j], grid[i][k], grid[n][k], grid[n][j]))
                except ValueError:
                    pass
        self._put(key, [v for row in grid for v in row], loc, scale, rot)

    def arc(self, loc=(0, 0, 0), R=3.0, w=0.8, d=1.0, a0=0.0, a1=PI, seg=16, key="stone", rot=(0, 0, 0)):
        """アーチの帯 (XZ 平面の半円)。w=厚み (半径方向)、d=奥行き (Y)。"""
        bm = self.bm[key]
        cols = []
        for i in range(seg + 1):
            a = a0 + (a1 - a0) * i / seg
            cols.append([bm.verts.new((rad * math.cos(a), y, rad * math.sin(a))) for rad in (R, R + w) for y in (-d / 2, d / 2)])
        for i in range(seg):
            b, c = cols[i], cols[i + 1]
            for q in ((b[0], b[1], c[1], c[0]), (b[2], c[2], c[3], b[3]), (b[0], c[0], c[2], b[2]), (b[1], b[3], c[3], c[1])):
                try:
                    bm.faces.new(q)
                except ValueError:
                    pass
        for end in (cols[0], cols[-1]):
            try:
                bm.faces.new((end[0], end[1], end[3], end[2]))
            except ValueError:
                pass
        self._put(key, [v for col in cols for v in col], loc, (1, 1, 1), rot)


# ---------------------------------------------------------------- 材質
def make_mats():
    mats = {}
    m = bpy.data.materials.new("ruin_stone")
    m.use_nodes = True
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    col = nt.nodes.new("ShaderNodeVertexColor")
    col.layer_name = "Col"
    nt.links.new(col.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.88
    mats["stone"] = m
    for key, rgb, strength in (("glow", (0.16, 0.92, 0.86), 3.0), ("warm", (1.0, 0.66, 0.2), 3.5), ("bio", (0.55, 1.0, 0.7), 2.2)):
        m = bpy.data.materials.new("ruin_" + key)
        m.use_nodes = True
        b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        b.inputs["Base Color"].default_value = (rgb[0] * 0.25, rgb[1] * 0.25, rgb[2] * 0.25, 1)
        b.inputs["Emission Color"].default_value = (*rgb, 1)
        b.inputs["Emission Strength"].default_value = strength
        b.inputs["Roughness"].default_value = 0.4
        mats[key] = m
    return mats


def weather(bm, seed, jitter, tint):
    """石の風化: 頂点を少しゆがめ、下ほど暗く青緑に苔むす頂点色を付ける。"""
    rnd = random.Random(seed)
    zs = [v.co.z for v in bm.verts] or [0.0]
    z0, z1 = min(zs), max(zs)
    span = max(z1 - z0, 1e-3)
    key = {}
    for v in bm.verts:
        k = (round(v.co.x, 3), round(v.co.y, 3), round(v.co.z, 3))
        if k not in key:
            key[k] = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * jitter
        v.co += key[k]
    lay = bm.loops.layers.color.get("Col") or bm.loops.layers.color.new("Col")
    for f in bm.faces:
        for lp in f.loops:
            h = (lp.vert.co.z - z0) / span
            moss = max(0.0, 1.0 - h * 2.2)
            n = 0.88 + 0.24 * (hash((round(lp.vert.co.x, 2), round(lp.vert.co.y, 2))) % 97) / 97.0
            r = (0.30 + 0.30 * h) * tint[0] * n
            g = (0.42 + 0.30 * h) * tint[1] * n
            b = (0.46 + 0.26 * h) * tint[2] * n
            r, g, b = r * (1 - 0.65 * moss), g * (1 - 0.3 * moss), b * (1 - 0.2 * moss)
            lp[lay] = (r, g, b, 1.0)


def finalize(name, shape, mats, jitter=0.02, tint=(1, 1, 1), flat=True):
    """bmesh → オブジェクト。 戻り値: オブジェクトのリスト。"""
    objs = []
    for key, bm in shape.bm.items():
        if not bm.verts:
            bm.free()
            continue
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        if key == "stone":
            weather(bm, hash(name) % 100000, jitter, tint)
        mesh = bpy.data.meshes.new(f"{name}_{key}")
        bm.to_mesh(mesh)
        bm.free()
        mesh.materials.append(mats[key])
        o = bpy.data.objects.new(f"{name}_{key}" if len(shape.bm) > 1 else name, mesh)
        bpy.context.scene.collection.objects.link(o)
        for p in mesh.polygons:
            p.use_smooth = not flat
        objs.append(o)
    return objs


# ---------------------------------------------------------------- 遺跡の部品
def glyph_bar(s, loc, size, rot=(0, 0, 0)):
    s.box(loc, size, rot, key="glow")


def pillar_intact(s, h=5.6, r=0.8):
    s.box((0, 0, 0), (r * 2.7, r * 2.7, 0.45), base=True)
    s.cyl((0, 0, 0.45), (r * 1.25, r * 1.05), 0.3, 12, base=True)
    s.cyl((0, 0, 0.75), (r, r * 0.86), h - 1.5, 16, base=True, flute=0.07)
    s.cyl((0, 0, h - 0.75), (r * 1.05, r * 1.2), 0.25, 12, base=True)
    s.box((0, 0, h - 0.5), (r * 2.5, r * 2.5, 0.5), base=True)
    for z in (h * 0.3, h * 0.68):
        s.ring((0, 0, z), r * 0.93, 0.045, 24, key="glow")


def pillar_broken(s, h=2.6, r=0.8):
    s.box((0, 0, 0), (r * 2.7, r * 2.7, 0.45), base=True)
    s.cyl((0, 0, 0.45), (r * 1.25, r * 1.05), 0.3, 12, base=True)
    s.cyl((0, 0, 0.75), (r, r * 0.9), h - 0.75, 16, base=True, flute=0.07)
    # 折れた断面のぎざぎざ
    for i in range(5):
        a = i * 2 * PI / 5 + 0.3
        s.cone((math.cos(a) * r * 0.45, math.sin(a) * r * 0.45, h - 0.05), r=0.3, h=0.5 + 0.25 * (i % 3), seg=5, base=True)
    s.ring((0, 0, h * 0.45), r * 0.95, 0.04, 24, key="glow")


def pillar_fallen(s):
    for i, (x, z, ry) in enumerate(((0, 0.75, 0), (2.1, 0.7, 0.05), (4.3, 0.76, -0.04))):
        s.cyl((x, 0, z), (0.78, 0.78), 1.9, 14, rot=(0, PI / 2 + ry, 0), flute=0.05)
    s.ring((2.1, 0, 0.7), 0.82, 0.04, 20, rot=(0, PI / 2, 0), key="glow")
    s.box((5.6, 0.3, 0.45), (1.6, 1.4, 0.9), rot=(0.1, 0.2, 0.45))


def arch_gate(s, span=8.0, h=6.5, r=0.75):
    for sx in (-1, 1):
        x = sx * span / 2
        s.box((x, 0, 0), (r * 2.8, r * 2.8, 0.5), base=True)
        s.cyl((x, 0, 0.5), (r, r * 0.9), h - 0.5, 14, base=True, flute=0.06)
        s.box((x, 0, h), (r * 2.6, r * 2.6, 0.45), base=True)
        s.ring((x, 0, h * 0.35), r * 0.95, 0.04, 22, key="glow")
    # 半円のアーチ
    s.arc((0, 0, h + 0.45), R=span / 2 - r * 1.3, w=0.9, d=1.6, seg=18)
    s.box((0, 0, h + 0.45 + span / 2 - r * 1.3 + 0.55), (1.2, 1.7, 1.1), base=False)
    s.sphere((0, -0.9, h + 0.45 + span / 2 - r * 1.3 + 0.55), (0.32, 0.12, 0.32), 8, key="warm")
    s.arc((0, -0.85, h + 0.45), R=span / 2 - r * 1.3 + 0.38, w=0.1, d=0.1, seg=22, key="glow")


def arch_broken(s, span=8.0, h=6.5, r=0.75):
    x = -span / 2
    s.box((x, 0, 0), (r * 2.8, r * 2.8, 0.5), base=True)
    s.cyl((x, 0, 0.5), (r, r * 0.9), h - 0.5, 14, base=True, flute=0.06)
    s.box((x, 0, h), (r * 2.6, r * 2.6, 0.45), base=True)
    s.arc((0, 0, h + 0.45), R=span / 2 - r * 1.3, w=0.9, d=1.6, a0=PI * 0.55, a1=PI, seg=8)
    s.ring((x, 0, h * 0.35), r * 0.95, 0.04, 22, key="glow")
    s.cyl((span / 2, 0, 0), (r, r * 0.9), 1.9, 12, base=True, flute=0.06)
    for i in range(4):
        s.box((span / 2 - 1.2 + i * 0.9, 2.2 + 0.3 * i, 0.4), (1.3, 1.0, 0.8), rot=(0.2 * i, 0.1, 0.5 * i))


def wall_straight(s, length=4.0, h=2.6):
    s.box((0, 0, 0), (length, 0.9, 0.35), base=True)
    for i in range(3):
        s.box((0, 0, 0.35 + i * (h - 0.6) / 3), (length * (0.97 - 0.01 * i), 0.7, (h - 0.6) / 3 - 0.03), base=True)
    s.box((0, 0, h - 0.25), (length * 0.98, 0.95, 0.25), base=True)
    s.box((0, -0.36, h * 0.5), (length * 0.6, 0.05, 0.07), key="glow")
    s.box((0, -0.36, h * 0.5 - 0.35), (length * 0.34, 0.05, 0.07), key="glow")


def wall_broken(s, length=4.0, h=2.6):
    s.box((0, 0, 0), (length, 0.9, 0.35), base=True)
    for i in range(4):
        x = -length / 2 + (i + 0.5) * length / 4
        hh = h * (0.35 + 0.5 * ((i * 37) % 5) / 4)
        s.box((x, 0, 0.35), (length / 4 - 0.05, 0.7, hh - 0.35), base=True)
    for i in range(3):
        s.box((-0.8 + i * 1.0, 1.1 + 0.1 * i, 0.25), (0.8, 0.6, 0.5), rot=(0.1 * i, 0.1, 0.8 * i))


def stairs(s, w=4.0, steps=6, run=0.7, rise=0.32):
    for i in range(steps):
        s.box((0, -i * run, 0), (w - i * 0.05, run + 0.05, rise * (steps - i)), base=True)
    s.box((w / 2 + 0.2, -steps * run / 2 + run / 2, 0), (0.4, steps * run, rise * steps + 0.3), base=True)
    s.box((-w / 2 - 0.2, -steps * run / 2 + run / 2, 0), (0.4, steps * run, rise * steps + 0.3), base=True)
    for i in range(steps):
        s.box((0, -i * run - run * 0.4, rise * (steps - i) - 0.02), (w * 0.5, 0.05, 0.04), key="glow")


def platform_octagon(s, r=6.0):
    s.cyl((0, 0, 0), (r, r - 0.3), 0.4, 8, base=True)
    s.cyl((0, 0, 0.4), (r - 0.9, r - 1.1), 0.4, 8, base=True)
    s.ring((0, 0, 0.82), r - 1.7, 0.05, 40, key="glow")
    for i in range(8):
        a = i * PI / 4 + PI / 8
        s.box((math.cos(a) * (r - 2.6), math.sin(a) * (r - 2.6), 0.82), (0.1, 1.2, 0.05), rot=(0, 0, a), key="glow")


def altar(s):
    s.box((0, 0, 0), (4.4, 4.4, 0.5), base=True)
    s.box((0, 0, 0.5), (3.6, 3.6, 0.6), base=True)
    s.box((0, 0, 1.1), (3.0, 3.0, 0.5), base=True)
    s.ring((0, 0, 1.62), 1.0, 0.05, 30, key="glow")
    s.sphere((0, 0, 1.9), (0.3, 0.3, 0.3), 8, key="warm")
    for sx in (-1, 1):
        for sy in (-1, 1):
            s.box((sx * 1.3, sy * 1.3, 1.6), (0.35, 0.35, 0.3), base=False)


def obelisk(s, h=11.0):
    s.box((0, 0, 0), (2.7, 2.7, 0.7), base=True)
    s.cyl((0, 0, 0.7), (1.05, 0.55), h, 4, rot=(0, 0, PI / 4), base=True)
    s.cone((0, 0, 0.7 + h), r=0.62, h=1.4, seg=4, rot=(0, 0, PI / 4), key="glow", base=True)
    for i in range(5):
        z = 1.6 + i * (h - 2.4) / 4
        half = 1.05 - (1.05 - 0.55) * (z - 0.7) / h
        s.box((0, -half * 0.74, z), (half * 0.9, 0.08, 0.16), key="glow")
        s.box((half * 0.74, 0, z), (0.08, half * 0.9, 0.16), key="glow")


def guardian_statue(s):
    """蟹をかたどった守り神の像 (記号的)。正面は Blender の -Y (glTF の +Z)。"""
    s.box((0, 0, 0), (3.4, 3.4, 1.2), base=True)
    s.box((0, 0, 1.2), (2.8, 2.8, 0.3), base=True)
    s.sphere((0, 0, 2.5), (1.55, 1.3, 0.95), 12)
    s.sphere((0, -0.2, 3.25), (0.9, 0.8, 0.3), 10)
    for sx in (-1, 1):
        # 大きなハサミ (正面へ突き出す腕)
        s.cyl((sx * 1.55, -0.9, 2.5), (0.42, 0.34), 2.2, 8, rot=(1.25, 0, sx * 0.3))
        s.sphere((sx * 1.95, -2.1, 2.7), (0.75, 0.9, 0.6), 9)
        s.cone((sx * 1.6, -3.1, 2.7), r=0.42, h=1.6, seg=6, rot=(PI / 2, 0, 0))
        s.cone((sx * 2.4, -3.0, 2.7), r=0.38, h=1.5, seg=6, rot=(PI / 2, 0, 0))
        # 目 (柄の先で光る)
        s.cyl((sx * 0.55, -0.9, 3.3), (0.07, 0.07), 0.9, 6, base=True)
        s.sphere((sx * 0.55, -0.9, 4.3), (0.26, 0.26, 0.26), 8, key="warm")
        s.cyl((sx * 1.45, 0.7, 1.5), (0.2, 0.14), 1.4, 6, rot=(0, sx * 0.5, 0))
    s.box((0, -1.35, 2.05), (1.4, 0.14, 0.14), key="glow")
    s.box((0, -1.35, 2.75), (0.9, 0.14, 0.14), key="glow")


def fountain(s):
    s.cyl((0, 0, 0), (2.6, 2.4), 0.9, 12, base=True)
    s.cyl((0, 0, 0.9), (2.1, 2.1), 0.15, 24, base=True, key="glow")
    for i in range(6):
        a = i * PI / 3
        s.box((math.cos(a) * 3.0, math.sin(a) * 3.0, 1.2), (1.5, 0.3, 2.9), rot=(0.28, 0, a + PI / 2), base=False)
        s.box((math.cos(a) * 3.1, math.sin(a) * 3.1, 2.55), (1.45, 0.34, 0.1), rot=(0.28, 0, a + PI / 2), key="glow")
    s.sphere((0, 0, 1.9), (0.5, 0.5, 0.5), 10, key="glow")


def lantern_stele(s, h=3.4):
    s.box((0, 0, 0), (1.1, 1.1, 0.35), base=True)
    s.cyl((0, 0, 0.35), (0.34, 0.28), h - 1.0, 6, base=True)
    s.box((0, 0, h - 0.65), (0.9, 0.9, 0.18), base=True)
    for sx, sy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        s.box((sx * 0.3, sy * 0.3, h - 0.28), (0.12 if sx else 0.5, 0.12 if sy else 0.5, 0.6), base=False)
    s.cone((0, 0, h - 0.5), r=0.65, h=0.45, seg=4, rot=(0, 0, PI / 4), base=True)
    s.sphere((0, 0, h - 0.5), (0.2, 0.2, 0.27), 8, key="warm")


def rune_floor_ring(s, R=7.0):
    s.cyl((0, 0, 0), (R + 0.6, R + 0.6), 0.2, 40, base=True)
    s.ring((0, 0, 0.22), R, 0.07, 56, key="glow")
    s.ring((0, 0, 0.22), R - 1.3, 0.05, 48, key="glow")
    for i in range(12):
        a = i * PI / 6
        s.box((math.cos(a) * (R - 0.65), math.sin(a) * (R - 0.65), 0.22), (0.1, 1.0, 0.05), rot=(0, 0, a), key="glow")


def floor_tile(s, size=4.0):
    s.box((0, 0, 0), (size, size, 0.3), base=True)
    s.box((0, 0, 0.3), (size - 0.5, size - 0.5, 0.06), base=True)
    s.box((0, 0, 0.36), (size * 0.6, 0.07, 0.04), key="glow", base=True)
    s.box((0, 0, 0.36), (0.07, size * 0.6, 0.04), key="glow", base=True)


def rubble(s, seed=1, n=8):
    rnd = random.Random(seed)
    for i in range(n):
        r = 1.2 * (1 - 0.1 * i)
        a = rnd.uniform(0, 2 * PI)
        d = rnd.uniform(0, 1.6) * (1 + i * 0.05)
        sz = (rnd.uniform(0.5, 1.6), rnd.uniform(0.5, 1.3), rnd.uniform(0.35, 0.9))
        s.box((math.cos(a) * d, math.sin(a) * d, 0.1), sz, rot=(rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), rnd.uniform(0, PI)), base=True)
    if seed == 2:
        s.cyl((1.4, 0.4, 0.5), (0.7, 0.7), 1.2, 12, rot=(0, PI / 2, 0.6), flute=0.05)


def dome_shrine(s):
    s.cyl((0, 0, 0), (4.2, 4.0), 0.5, 10, base=True)
    for i in range(6):
        a = i * PI / 3
        x, y = math.cos(a) * 3.1, math.sin(a) * 3.1
        s.cyl((x, y, 0.5), (0.4, 0.34), 4.4, 10, base=True, flute=0.06)
        s.box((x, y, 4.9), (0.9, 0.9, 0.25), base=True)
    s.ring((0, 0, 5.3), 3.1, 0.22, 36, key="stone")
    s.ring((0, 0, 5.3), 3.1, 0.06, 36, key="glow", scale=(1, 1, 1), sub=4)
    s.cyl((0, 0, 5.1), (3.3, 0.5), 1.3, 12, base=True)
    s.sphere((0, 0, 7.0), (0.4, 0.4, 0.4), 10, key="warm")
    s.sphere((0, 0, 1.2), (0.5, 0.5, 0.5), 10, key="glow")


def station_forge(s):
    s.cyl((0, 0, 0), (4.0, 3.8), 0.6, 8, base=True)
    for sx in (-1, 1):
        s.box((sx * 3.0, -1.6, 0.6), (1.1, 1.1, 4.4), base=True)
        s.box((sx * 3.0, -1.6, 5.0), (1.6, 1.6, 0.4), base=True)
        s.ring((sx * 3.0, -1.6, 2.4), 0.62, 0.04, 4, key="glow", rot=(0, 0, PI / 4))
    s.box((0, -1.6, 5.4), (7.2, 1.2, 0.7), base=True)
    s.ring((0, -2.3, 3.4), 1.5, 0.15, 28, rot=(PI / 2, 0, 0), key="glow")
    s.box((0, 0.3, 0.6), (1.5, 0.9, 0.9), base=True)
    s.box((0, 0.3, 1.5), (2.4, 0.9, 0.45), base=True)
    s.cone((1.9, 0.3, 1.5), r=0.4, h=1.3, seg=6, rot=(0, PI / 2, 0))
    s.cyl((-2.2, 1.6, 0.6), (0.8, 0.95), 0.4, 10, base=True)
    s.cone((-2.2, 1.6, 1.0), r=0.5, h=1.2, seg=6, key="warm", base=True)


def station_dock_gate(s):
    for sx in (-1, 1):
        x = sx * 3.8
        s.box((x, -1.4, 0), (1.9, 1.9, 0.6), base=True)
        s.box((x, -1.4, 0.6), (1.2, 1.2, 5.0), base=True)
        s.box((x, -1.4, 5.6), (1.7, 1.7, 0.4), base=True)
        s.ring((x, -1.4, 2.2), 0.7, 0.04, 4, key="glow", rot=(0, 0, PI / 4))
    s.arc((0, -1.4, 6.0), R=3.6, w=0.5, d=1.0, seg=20)
    s.arc((0, -0.85, 6.0), R=3.6, w=0.1, d=0.1, seg=20, key="glow")
    s.sphere((0, -1.4, 10.4), (0.4, 0.4, 0.4), 8, key="glow")
    for sx in (-1, 1):
        s.cyl((sx * 2.3, 1.9, 0), (0.45, 0.35), 1.2, 8, base=True)
        s.ring((sx * 2.3, 1.9, 1.15), 0.34, 0.07, 14, key="glow")


def station_scale(s):
    s.cyl((0, 0, 0), (4.0, 3.8), 0.6, 8, base=True)
    s.box((0, -1.2, 0.6), (0.9, 0.9, 4.6), base=True)
    s.box((0, -1.2, 5.2), (6.0, 0.4, 0.3), base=True)
    s.sphere((0, -1.2, 5.65), (0.4, 0.4, 0.4), 8, key="glow")
    for sx in (-1, 1):
        px = sx * 2.7
        s.cyl((px, -1.2, 3.3), (0.5, 1.1), 0.4, 12, base=True)
        s.sphere((px, -1.2, 3.85), (0.34, 0.34, 0.34), 8, key="warm")
        for a in (0, 2.1, 4.2):
            s.cyl((px + math.cos(a) * 0.45, -1.2 + math.sin(a) * 0.45, 4.3), (0.03, 0.03), 1.8, 4)
    for sx in (-1, 1):
        s.box((sx * 2.2, 2.2, 0.6), (1.8, 0.7, 0.5), base=True)


def station_spring(s):
    s.cyl((0, 0, 0), (4.0, 3.8), 0.5, 10, base=True)
    s.cyl((0, 0, 0.5), (2.5, 2.3), 0.8, 12, base=True)
    s.cyl((0, 0, 1.3), (2.1, 2.1), 0.1, 24, base=True, key="glow")
    for i in range(6):
        a = i * PI / 3
        s.box((math.cos(a) * 3.2, math.sin(a) * 3.2, 0.5), (1.5, 0.3, 3.0), rot=(0.28, 0, a + PI / 2), base=True)
        s.box((math.cos(a) * 3.25, math.sin(a) * 3.25, 3.35), (1.4, 0.34, 0.1), rot=(0.28, 0, a + PI / 2), key="glow")
    s.sphere((0, 0, 2.6), (0.6, 0.6, 0.6), 10, key="glow")


def coral_cluster(s):
    """遺跡にまとわりつく深海のサンゴ・ウミエラ (発光する先端)。"""
    rnd = random.Random(5)
    for i in range(9):
        a = rnd.uniform(0, 2 * PI)
        d = rnd.uniform(0.0, 1.3)
        h = rnd.uniform(0.8, 2.4)
        x, y = math.cos(a) * d, math.sin(a) * d
        s.cyl((x, y, 0), (0.12, 0.06), h, 6, rot=(rnd.uniform(-0.2, 0.2), rnd.uniform(-0.2, 0.2), 0), base=True)
        s.sphere((x, y, h), (0.17, 0.17, 0.17), 6, key="bio")
    s.cyl((0, 0, 0), (1.6, 1.3), 0.35, 9, base=True)


def tube_worms(s):
    rnd = random.Random(8)
    for i in range(14):
        a = rnd.uniform(0, 2 * PI)
        d = rnd.uniform(0.0, 1.1)
        h = rnd.uniform(0.7, 1.9)
        s.cyl((math.cos(a) * d, math.sin(a) * d, 0), (0.1, 0.07), h, 6, rot=(rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), 0), base=True)
        s.cone((math.cos(a) * d, math.sin(a) * d, h), r=0.14, h=0.28, seg=6, key="bio", base=True)
    s.cyl((0, 0, 0), (1.4, 1.2), 0.3, 9, base=True)


MODELS = [
    # id, builder, kwargs, 風化の強さ, 色調
    ("ruin_pillar_intact", pillar_intact, {}, 0.025, (1, 1, 1)),
    ("ruin_pillar_broken", pillar_broken, {}, 0.03, (0.95, 1, 1)),
    ("ruin_pillar_fallen", pillar_fallen, {}, 0.03, (0.95, 1, 1)),
    ("ruin_arch_gate", arch_gate, {}, 0.025, (1, 1, 1)),
    ("ruin_arch_broken", arch_broken, {}, 0.035, (0.95, 1, 1)),
    ("ruin_wall_straight", wall_straight, {}, 0.025, (1, 1, 1)),
    ("ruin_wall_broken", wall_broken, {}, 0.035, (0.95, 1, 1)),
    ("ruin_stairs", stairs, {}, 0.02, (1, 1, 1)),
    ("ruin_platform_octagon", platform_octagon, {}, 0.02, (1, 1, 1)),
    ("ruin_altar", altar, {}, 0.02, (1, 1, 1)),
    ("ruin_obelisk", obelisk, {}, 0.02, (1, 1, 1)),
    ("ruin_guardian_statue", guardian_statue, {}, 0.03, (1, 1, 1)),
    ("ruin_fountain", fountain, {}, 0.025, (1, 1, 1)),
    ("ruin_lantern_stele", lantern_stele, {}, 0.02, (1, 1, 1)),
    ("ruin_rune_floor_ring", rune_floor_ring, {}, 0.02, (1, 1, 1)),
    ("ruin_floor_tile", floor_tile, {}, 0.015, (1, 1, 1)),
    ("ruin_rubble_a", rubble, {"seed": 1}, 0.04, (0.95, 1, 1)),
    ("ruin_rubble_b", rubble, {"seed": 2, "n": 7}, 0.04, (0.95, 1, 1)),
    ("ruin_dome_shrine", dome_shrine, {}, 0.025, (1, 1, 1)),
    ("ruin_station_forge", station_forge, {}, 0.025, (1.0, 0.96, 0.92)),
    ("ruin_station_dock_gate", station_dock_gate, {}, 0.025, (0.95, 1, 1.05)),
    ("ruin_station_scale", station_scale, {}, 0.025, (1.05, 1.02, 0.95)),
    ("ruin_station_spring", station_spring, {}, 0.025, (0.95, 1.05, 1.0)),
    ("ruin_coral_cluster", coral_cluster, {}, 0.02, (1, 1, 1)),
    ("ruin_tube_worms", tube_worms, {}, 0.02, (1, 1, 1)),
]


# ---------------------------------------------------------------- 書き出しとサムネイル
def setup_render():
    scn = bpy.context.scene
    try:
        scn.render.engine = "BLENDER_EEVEE_NEXT"
    except TypeError:
        try:
            scn.render.engine = "BLENDER_EEVEE"
        except TypeError:
            scn.render.engine = "CYCLES"
    if scn.render.engine == "CYCLES":
        scn.cycles.samples = 48
    scn.render.resolution_x = scn.render.resolution_y = 256
    scn.render.film_transparent = True
    scn.render.image_settings.file_format = "PNG"
    scn.render.image_settings.color_mode = "RGBA"


def render_thumb(objs, path):
    scn = bpy.context.scene
    lo = Vector((1e9,) * 3)
    hi = Vector((-1e9,) * 3)
    for o in objs:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, w))
            hi = Vector(map(max, hi, w))
    c = (lo + hi) / 2
    r = max((hi - lo).length * 0.5, 0.5)
    w = bpy.data.worlds.new("w")
    scn.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = (0.18, 0.28, 0.36, 1)
    bg.inputs[1].default_value = 1.0
    lights = []
    for loc, e, sz in (((4, -5, 6), 900, 6), ((-6, -2, 3), 300, 6), ((0, 6, 4), 260, 6)):
        bpy.ops.object.light_add(type="AREA", location=(c.x + loc[0] * r * 0.5, c.y + loc[1] * r * 0.5, c.z + loc[2] * r * 0.5))
        L = bpy.context.object
        L.data.energy = e * r * r * 0.35
        L.data.size = sz * r * 0.5
        L.rotation_euler = (c - L.location).to_track_quat("-Z", "Y").to_euler()
        lights.append(L)
    bpy.ops.object.camera_add(location=c + Vector((0.9, -1.0, 0.55)).normalized() * r * 2.7)
    cam = bpy.context.object
    cam.data.lens = 50
    cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
    scn.camera = cam
    scn.render.filepath = path
    bpy.ops.render.render(write_still=True)
    for L in lights + [cam]:
        bpy.data.objects.remove(L)


def clear_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    setup_render()
    mats = make_mats()
    done = []
    for mid, fn, kw, jitter, tint in MODELS:
        if ONLY and mid not in ONLY:
            continue
        clear_scene()
        s = Shape()
        fn(s, **kw)
        objs = finalize(mid, s, mats, jitter=jitter, tint=tint)
        for o in objs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, mid + ".glb"), export_format="GLB", use_selection=True, export_yup=True)
        render_thumb(objs, os.path.join(THUMBS, mid + ".png"))
        done.append(mid)
        print("built", mid)
    print("OK", len(done))


main()
