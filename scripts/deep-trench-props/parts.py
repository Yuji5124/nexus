"""DEEP-TRENCH PROPS の部品 (深度3500m以降のオブジェクト 20 点の形・一覧)。build_trench_props.py が読む。

帯: luminous-deep (3,500〜8,000m 発光深海) / sunken-city (8,000〜10,000m 沈没都市) / abyss (10,000〜12,000m 深淵領域)。
形は『甲殻類にも都合があります。』の docs (GAME_SPEC / LORE_AND_STORY / UNKNOWN_NATURAL_PHENOMENA) にある方向性を元にした提案で、
古代文明の正体や現象の仕組みは決めていない (見た目だけ)。alpha タグのあるものは半透明の材質を使う。
"""
import math
import random

import bmesh
from mathutils import Matrix, Vector, Euler

PI = math.pi
KEYS = ("stone", "glow", "warm", "bio", "metal", "beam", "glass", "lume", "amber", "bone", "ghost", "obs", "ray_r", "ray_y", "ray_g", "ray_c", "ray_v")


def extend_shape(Shape):
    """ruins の Shape に、リボン・開いた円すい・平らな輪・棒 (limb) を足した版を返す。"""

    class Shape2(Shape):
        def __init__(self):
            self.bm = {k: bmesh.new() for k in KEYS}

        def open_cone(self, loc=(0, 0, 0), r=(1, 1), h=1, seg=24, rot=(0, 0, 0), key="beam"):
            res = bmesh.ops.create_cone(self.bm[key], cap_ends=False, cap_tris=False, segments=seg, radius1=r[0], radius2=max(r[1], 1e-4), depth=1)
            self._put(key, res["verts"], loc, (1, 1, h), rot)

        def ribbon(self, pts, width, key="beam"):
            bm = self.bm[key]
            cols = []
            for i, p in enumerate(pts):
                p = Vector(p)
                nxt = Vector(pts[min(i + 1, len(pts) - 1)])
                prv = Vector(pts[max(i - 1, 0)])
                t = (nxt - prv).normalized()
                side = t.cross(Vector((0, 0, 1)))
                if side.length < 1e-4:
                    side = Vector((1, 0, 0))
                side.normalize()
                cols.append((bm.verts.new(p - side * width / 2), bm.verts.new(p + side * width / 2)))
            for i in range(len(cols) - 1):
                a, b = cols[i], cols[i + 1]
                try:
                    bm.faces.new((a[0], a[1], b[1], b[0]))
                except ValueError:
                    pass

        def limb(self, p1, p2, r=0.08, r2=None, seg=6, key="stone"):
            """p1 から p2 へ伸びる円柱 (先細り可)。"""
            a, b = Vector(p1), Vector(p2)
            d = b - a
            rot = d.to_track_quat("Z", "Y").to_euler()
            self.cyl((a + b) / 2, (r, r if r2 is None else r2), d.length, seg, tuple(rot), key)

    return Shape2


def _dir(a, tilt):
    return Vector((math.sin(tilt) * math.cos(a), math.sin(tilt) * math.sin(a), math.cos(tilt)))


# ================================================================ 3,500〜8,000m 発光深海
def prop_lume_coral(s):
    """紫に光る枝サンゴ。骨色の枝と、先端の発光する粒。"""
    rnd = random.Random(11)
    s.cyl((0, 0, 0), (1.1, 0.8), 0.45, 9, base=True, key="stone")

    def branch(p, d, length, r, depth):
        q = p + d * length
        s.limb(p, q, r, r * 0.75, 5, "bone")
        if depth == 0:
            s.sphere(q, (r * 1.9,) * 3, 6, "lume")
            return
        for k in range(3 if depth > 1 else 2):
            a = rnd.uniform(0, 2 * PI)
            nd = (d + _dir(a, rnd.uniform(0.5, 0.9)) * 0.9).normalized()
            if nd.z < 0.25:
                nd.z = 0.25
                nd.normalize()
            branch(q, nd, length * 0.72, r * 0.72, depth - 1)

    for k in range(3):
        a = k * 2 * PI / 3 + 0.4
        branch(Vector((math.cos(a) * 0.3, math.sin(a) * 0.3, 0.4)), _dir(a, 0.35), 0.95, 0.11, 3)


def prop_glass_sponge(s):
    """ガラス海綿の群れ。ラッパ型の骨色の筒で、口が淡く光る。"""
    s.cyl((0, 0, 0), (1.5, 1.1), 0.35, 9, base=True, key="stone")
    rnd = random.Random(5)
    for i in range(7):
        a = rnd.uniform(0, 2 * PI)
        d = 0.0 if i == 0 else rnd.uniform(0.35, 1.0)
        x, y = math.cos(a) * d, math.sin(a) * d
        h = 2.4 if i == 0 else rnd.uniform(0.8, 1.9)
        s.cyl((x, y, 0.3), (0.2, 0.34), h, 9, base=True, key="bone")
        s.cyl((x, y, 0.3 + h), (0.34, 0.34), 0.05, 9, base=True, key="lume")
        for k in range(3):
            b = k * 2 * PI / 3
            s.ring((x, y, 0.3 + h * (0.3 + 0.2 * k)), 0.27 + 0.05 * k, 0.018, 12, key="bone", sub=4)


def prop_lamp_stalks(s):
    """灯りの茎。細く曲がった茎の先に、球根のような発光体 (紫と琥珀)。"""
    rnd = random.Random(21)
    s.cyl((0, 0, 0), (1.3, 0.9), 0.4, 8, base=True, key="stone")
    for i in range(9):
        a = rnd.uniform(0, 2 * PI)
        d = rnd.uniform(0.0, 0.9)
        x, y = math.cos(a) * d, math.sin(a) * d
        h = rnd.uniform(1.6, 3.8)
        lean = rnd.uniform(0.2, 0.6)
        p0 = Vector((x, y, 0.3))
        p1 = p0 + Vector((math.cos(a) * lean * 0.4, math.sin(a) * lean * 0.4, h * 0.55))
        p2 = p0 + Vector((math.cos(a) * lean * 1.1, math.sin(a) * lean * 1.1, h))
        s.limb(p0, p1, 0.055, 0.045, 5, "bone")
        s.limb(p1, p2, 0.045, 0.035, 5, "bone")
        s.sphere(p2 + Vector((0, 0, 0.1)), (0.17, 0.17, 0.2), 8, "lume" if i % 3 else "amber")
        s.ring(p2, 0.14, 0.015, 10, key="bone", sub=4)


def prop_whale_fall(s):
    """鯨骨生物群集。横たわる鯨の骨格 (全長約 13 m)。骨のまわりに細菌マットが紫に光る。"""
    s.sphere((0, 0, 0.1), (3.0, 7.0, 0.35), 12, key="stone")
    for i in range(16):
        y = -5.2 + i * 0.62
        r = 0.34 - abs(i - 6) * 0.012
        s.cyl((0, y, 0.55), (r, r * 0.9), 0.44, 8, rot=(PI / 2, 0, 0), key="bone")
        s.box((0, y, 0.55 + r), (0.12, 0.3, 0.45), key="bone")
    for i in range(8):
        y = -3.6 + i * 0.62
        R = 2.1 - abs(i - 3) * 0.26
        s.arc((0, y, 0.45), R=R, w=0.17, d=0.2, a0=0.0, a1=PI * 0.62, seg=10, key="bone")
        s.arc((0, y, 0.45), R=R, w=0.17, d=0.2, a0=PI * 0.38, a1=PI, seg=10, key="bone")
    s.sphere((0, -6.3, 0.9), (1.2, 1.7, 0.85), 10, key="bone")
    s.box((0, -7.2, 0.5), (1.0, 2.0, 0.18), key="bone")
    for sx in (-1, 1):
        s.sphere((sx * 0.5, -6.4, 1.3), (0.17, 0.17, 0.17), 6, key="stone")
    for (x, y, r) in ((1.4, -1.0, 0.6), (-1.6, 0.8, 0.5), (0.8, 2.4, 0.45), (-0.9, -3.4, 0.5), (1.9, -3.0, 0.35)):
        s.sphere((x, y, 0.28), (r, r * 0.8, 0.08), 8, key="lume")
    for i in range(6):
        y = 3.5 + i * 0.35
        s.limb((0, y, 0.45), (0.0, y + 0.3, 0.9 - i * 0.07), 0.07, 0.04, 5, "bone")


def prop_tubeworm_garden(s):
    """チューブワームの園。白い筒の先から赤橙色の房が出ている。"""
    rnd = random.Random(2)
    s.cyl((0, 0, 0), (1.9, 1.5), 0.5, 10, base=True, key="stone")
    for i in range(16):
        a = rnd.uniform(0, 2 * PI)
        d = rnd.uniform(0.0, 1.3)
        x, y = math.cos(a) * d, math.sin(a) * d
        h = rnd.uniform(0.9, 2.6)
        t = rnd.uniform(0.0, 0.25)
        top = Vector((x + math.cos(a) * t * h, y + math.sin(a) * t * h, 0.4 + h))
        s.limb(Vector((x, y, 0.35)), top, 0.11, 0.085, 6, "bone")
        for k in range(5):
            b = k * 2 * PI / 5 + i
            s.limb(top, top + Vector((math.cos(b) * 0.2, math.sin(b) * 0.2, 0.42)), 0.032, 0.012, 4, "warm")


def prop_nodule_field(s):
    """マンガン団塊の原 (採取物の置き場)。暗い丸石が転がり、数個の金属光沢が光る。"""
    rnd = random.Random(13)
    s.sphere((0, 0, 0.0), (2.4, 2.1, 0.22), 12, key="stone")
    for i in range(26):
        a = rnd.uniform(0, 2 * PI)
        d = rnd.uniform(0.0, 2.0)
        r = rnd.uniform(0.14, 0.34)
        s.sphere((math.cos(a) * d, math.sin(a) * d, r * 0.55), (r, r * rnd.uniform(0.8, 1.0), r * 0.75), 7, key="stone")
    for i in range(5):
        a = i * 2 * PI / 5 + 0.7
        s.cone((math.cos(a) * 1.2, math.sin(a) * 1.1, 0.05), r=0.07, h=0.34, seg=5, key="glow", base=True)


# ================================================================ 8,000〜10,000m 沈没都市 (見た目だけ。文明の正体は決めない)
def prop_street_lamp(s):
    """傾いた街灯。琥珀色の灯りがまだ残る。"""
    s.cyl((0, 0, 0), (0.55, 0.4), 0.5, 8, base=True, key="stone")
    s.cyl((0, 0, 0.5), (0.13, 0.09), 4.2, 8, rot=(0, 0.07, 0), base=True, key="metal")
    s.ring((0.25, 0, 3.0), 0.16, 0.025, 12, key="metal", sub=4)
    s.arc((0.55, 0, 4.55), R=0.55, w=0.07, d=0.08, a0=0.0, a1=PI * 0.9, seg=10, key="metal")
    s.cyl((1.05, 0, 4.4), (0.22, 0.14), 0.4, 6, key="glass")
    s.sphere((1.05, 0, 4.4), (0.12, 0.12, 0.16), 8, "amber")
    s.cone((1.05, 0, 4.58), r=0.24, h=0.16, seg=6, key="metal", base=True)


def prop_data_obelisk(s):
    """記録装置のオベリスク (8 m)。正面に光る記録の列。"""
    s.box((0, 0, 0), (3.2, 3.2, 0.4), base=True)
    s.box((0, 0, 0.4), (2.6, 2.6, 0.4), base=True)
    s.cyl((0, 0, 0.8), (0.95, 0.5), 6.6, 4, rot=(0, 0, PI / 4), base=True, key="stone")
    s.cone((0, 0, 7.4), r=0.4, h=0.8, seg=4, rot=(0, 0, PI / 4), base=True, key="stone")
    rnd = random.Random(8)
    for i in range(10):
        z = 1.7 + i * 0.5
        w = 0.62 - i * 0.03
        n = rnd.choice((2, 3))
        for k in range(n):
            x = (k - (n - 1) / 2) * (w * 0.8)
            s.box((x, -0.62 + i * 0.026, z), (w / n * rnd.uniform(0.6, 0.95), 0.05, 0.1), key="amber" if i % 4 == 3 else "glow")
    s.ring((0, 0, 5.2), 0.95, 0.045, 20, key="glow")


def prop_dwelling_wall(s):
    """住居跡の角。戸口のアーチと窓、崩れた壁の上端。"""
    s.box((0, 0.1, -0.05), (6.4, 5.2, 0.35), base=False, key="stone")
    s.box((-1.9, 0, 0), (2.6, 0.5, 3.0), base=True)
    s.box((1.9, 0, 0), (2.6, 0.5, 2.2), rot=(0, 0, 0.0), base=True)
    s.box((0, 0, 2.55), (1.5, 0.5, 0.9), base=True)
    s.arc((0, 0, 1.9), R=0.7, w=0.3, d=0.5, a0=0.0, a1=PI, seg=12, key="stone")
    s.box((-3.1, 2.3, 0), (0.5, 4.6, 2.5), base=True)
    s.box((-3.1, 2.3, 2.45), (0.5, 1.6, 0.9), rot=(0, 0.12, 0), base=True)
    s.box((-1.9, 0, 1.3), (0.7, 0.58, 0.7), key="glass")
    s.box((-1.9, -0.31, 1.3), (0.75, 0.05, 0.05), key="amber")
    s.box((0, 1.1, 0.7), (0.5, 0.5, 0.6), key="stone")
    s.sphere((0, 1.1, 1.25), (0.14, 0.14, 0.14), 6, "amber")
    rnd = random.Random(3)
    for i in range(6):
        a = rnd.uniform(0, 2 * PI)
        s.box((math.cos(a) * 2.3 + 0.8, -1.6 + math.sin(a) * 0.9, 0), (rnd.uniform(0.4, 0.9),) * 3, rot=(0, 0, rnd.uniform(0, 3)), base=True)


def prop_urn_set(s):
    """日用品。壺・鉢・皿・杯。つやのない骨色で、一つは縁が光る。"""
    s.sphere((0, 0, 0.6), (0.55, 0.55, 0.62), 12, key="bone")
    s.cyl((0, 0, 1.1), (0.28, 0.22), 0.3, 12, base=True, key="bone")
    s.ring((0, 0, 1.4), 0.26, 0.04, 14, key="bone", sub=4)
    s.ring((0, 0, 0.62), 0.56, 0.02, 20, key="glow", sub=4)
    s.sphere((1.2, 0.4, 0.4), (0.4, 0.4, 0.42), 10, key="stone")
    s.cyl((1.2, 0.4, 0.78), (0.2, 0.18), 0.24, 10, base=True, key="stone")
    s.cyl((-1.0, 0.7, 0.0), (0.45, 0.8), 0.38, 14, base=True, key="bone")
    s.cyl((-1.0, 0.7, 0.34), (0.7, 0.7), 0.03, 14, base=True, key="stone")
    s.cyl((0.1, -1.1, 0.0), (0.9, 0.9), 0.07, 16, base=True, key="bone")
    s.cyl((0.1, -1.1, 0.07), (0.5, 0.5), 0.02, 16, base=True, key="stone")
    s.cyl((-0.7, -1.4, 0.0), (0.16, 0.24), 0.3, 10, base=True, key="bone")
    s.limb((0.9, -0.9, 0.05), (1.7, -1.3, 0.12), 0.05, 0.04, 6, "bone")
    s.sphere((1.75, -1.3, 0.13), (0.14, 0.14, 0.05), 8, key="bone")


def prop_conduit_bundle(s):
    """導管の束 (7 m)。太さの違う管が留め具で束ねられ、継ぎ目が光る。"""
    for i, (x, z, r) in enumerate(((0, 0.45, 0.32), (0.7, 0.35, 0.24), (-0.65, 0.3, 0.2), (0.25, 1.0, 0.18), (-0.3, 0.9, 0.14))):
        s.cyl((x, 0, z), (r, r), 7.0, 10, rot=(PI / 2, 0, 0), key="metal")
        for y in (-3.4, 3.4):
            s.ring((x, y, z), r * 1.02, 0.03, 14, rot=(PI / 2, 0, 0), key="glow", sub=4)
    for y in (-2.4, 0.0, 2.4):
        s.box((0, y, 0.0), (2.2, 0.35, 0.18), key="stone", base=True)
        s.ring((0.05, y, 0.7), 1.05, 0.05, 22, rot=(PI / 2, 0, 0), scale=(1.0, 0.9, 1), key="metal", sub=4)
    s.arc((0.1, 3.5, 0.3), R=0.9, w=0.28, d=0.28, a0=0.0, a1=PI / 2, seg=10, key="metal", rot=(PI / 2, 0, 0))
    s.sphere((0.1, -3.55, 0.55), (0.3, 0.12, 0.3), 8, key="amber")


def prop_mural_panel(s):
    """壁画パネル (幅 4.2 m)。額縁の中に、同心円・渦・並んだ印の浮き彫り。意味は決めていない。"""
    s.box((0, 0, 0), (4.8, 0.7, 0.3), base=True)
    s.box((0, 0, 0.3), (4.2, 0.4, 3.2), base=True)
    for sx in (-2.2, 2.2):
        s.box((sx, 0, 0.3), (0.28, 0.6, 3.4), base=True)
    s.box((0, 0, 3.5), (4.7, 0.6, 0.28), base=True)
    for i, R in enumerate((0.3, 0.62, 0.95)):
        s.ring((-0.9, -0.24, 2.0), R, 0.03, 28, rot=(PI / 2, 0, 0), key="stone", sub=4)
    s.ring((-0.9, -0.26, 2.0), 1.25, 0.022, 32, rot=(PI / 2, 0, 0), key="amber", sub=4)
    s.sphere((-0.9, -0.26, 2.0), (0.14, 0.05, 0.14), 8, "glow")
    s.arc((1.2, -0.24, 2.0), R=0.4, w=0.06, d=0.05, a0=0.0, a1=PI * 1.5, seg=14, key="amber", rot=(0, 0, 0))
    s.arc((1.2, -0.24, 2.0), R=0.8, w=0.06, d=0.05, a0=PI * 0.5, a1=PI * 2.0, seg=16, key="amber", rot=(0, 0, 0))
    for i, rr in enumerate((0.2, 0.26, 0.17, 0.3, 0.22)):
        s.ring((-1.7 + i * 0.85, -0.24, 0.9), rr, 0.03, 18, rot=(PI / 2, 0, 0), key="glow", sub=4)
    for i in range(7):
        s.box((-1.8 + i * 0.6, -0.23, 3.1), (0.28, 0.04, 0.08), key="stone")


def prop_glow_rubble(s):
    """崩れた石材の山。割れ目から琥珀色の光がもれる。"""
    rnd = random.Random(19)
    for i in range(14):
        a = rnd.uniform(0, 2 * PI)
        d = rnd.uniform(0.0, 2.0)
        sz = rnd.uniform(0.5, 1.3) * (1.2 - d * 0.25)
        s.box((math.cos(a) * d, math.sin(a) * d, 0), (sz, sz * rnd.uniform(0.7, 1.2), sz * rnd.uniform(0.5, 0.9)), rot=(rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), rnd.uniform(0, 3)), base=True)
    for i in range(7):
        a = i * 2 * PI / 7 + 0.2
        s.box((math.cos(a) * 0.9, math.sin(a) * 0.9, 0.45), (0.08, 0.5 + 0.2 * (i % 3), 0.05), rot=(0, 0, a + 1.2), key="amber")
    s.sphere((0, 0, 0.5), (0.35, 0.35, 0.2), 8, "amber")


# ================================================================ 10,000〜12,000m 深淵領域 (現象の見た目案。仕組みは決めていない)
def fx_afterimage_ghost(s):
    """存在の余韻。同じ形 (細長い菱形) の半透明の写しが 4 つ、後ろへ並んで薄れていく。"""
    for i, (sc, key) in enumerate(((1.0, "ghost"), (0.9, "ghost"), (0.78, "beam"), (0.66, "beam"))):
        y = i * 1.7
        s.sphere((0, y, 1.6), (0.9 * sc, 1.5 * sc, 0.7 * sc), 6, key)
        s.sphere((0, y - 0.9 * sc, 1.7), (0.1 * sc, 0.1 * sc, 0.1 * sc), 6, "lume")
        s.ring((0, y, 1.6), 1.15 * sc, 0.02, 22, rot=(PI / 2, 0, 0), scale=(1.0, 1.0, 1.4), key="lume", sub=4)


def fx_phase_rift(s):
    """場所の重なり。縦に長い裂け目の枠と、向こう側が揺れる半透明の面 (高さ 5 m)。"""
    s.ring((0, 0, 2.6), 2.2, 0.07, 40, rot=(PI / 2, 0, 0), scale=(0.42, 1.0, 1.0), key="glow", sub=5)
    s.ring((0, 0, 2.6), 1.9, 0.035, 36, rot=(PI / 2, 0, 0), scale=(0.42, 1.0, 1.0), key="lume", sub=4)
    s.sphere((0, 0, 2.6), (0.9, 0.025, 2.1), 14, "ghost")
    for i in range(10):
        a = i * 2 * PI / 10 + 0.3
        s.cone((math.cos(a) * 1.0, 0.0, 2.6 + math.sin(a) * 2.4), r=0.07, h=0.5, seg=4, rot=(0, 0, 0), key="glow", base=False)
    s.cyl((0, 0, 0), (1.2, 0.9), 0.15, 12, base=True, key="stone")


def fx_rainbow_current(s):
    """虹の海流。五色の細い帯が、ゆるくねじれながら 12 m 立ち上る。"""
    keys = ("ray_r", "ray_y", "ray_g", "ray_c", "ray_v")
    for k, key in enumerate(keys):
        pts = []
        for i in range(41):
            t = i / 40
            ang = 2 * PI * (1.6 * t) + k * (2 * PI / 5)
            R = 0.8 + 1.5 * t + 0.1 * math.sin(6 * t + k)
            pts.append((math.cos(ang) * R, math.sin(ang) * R, 12.0 * t))
        s.ribbon(pts, 0.7 + 0.5 * (k % 2) * 0.3, key)


def prop_floating_stones(s):
    """重さの漂流。宙に浮く石の輪 (高さ 6 m)。下面が紫に光り、細い糸 (半透明) でつながる。"""
    rnd = random.Random(14)
    pts = []
    for i in range(9):
        a = i * 2 * PI / 9 + rnd.uniform(-0.2, 0.2)
        R = rnd.uniform(1.6, 2.6)
        z = 1.0 + (i % 3) * 1.6 + rnd.uniform(0, 0.7)
        sz = rnd.uniform(0.5, 1.0)
        p = (math.cos(a) * R, math.sin(a) * R, z)
        pts.append(p)
        s.sphere(p, (sz, sz * 0.85, sz * 0.7), 8, key="stone")
        s.cyl((p[0], p[1], z - sz * 0.62), (sz * 0.5, sz * 0.1), 0.12, 8, key="lume")
    for i in range(9):
        s.limb(pts[i], pts[(i + 1) % 9], 0.012, 0.012, 4, "beam")
    s.ring((0, 0, 0.05), 2.1, 0.03, 36, key="lume", sub=4)


def fx_pressure_husk(s):
    """圧力の抜け殻。ドーム状の半透明の領域 (半径 4 m、高さ 3.2 m)。縁と殻の線が光る。"""
    s.sphere((0, 0, 0), (4.0, 4.0, 3.2), 18, "ghost")
    s.ring((0, 0, 0.03), 4.0, 0.05, 44, key="glow", sub=4)
    for z, R in ((1.0, 3.8), (2.0, 3.1), (2.8, 1.9)):
        s.ring((0, 0, z), R, 0.025, 36, key="lume", sub=4)
    s.cyl((0, 0, 0), (4.0, 4.0), 0.03, 30, base=True, key="beam")
    s.cone((0, 0, 3.0), r=0.12, h=0.4, seg=5, key="glow", base=True)


def prop_invisible_steps(s):
    """見えない足場。薄く透ける板が 6 枚、らせん状に上へ続く (縁だけ光る)。"""
    for i in range(6):
        a = i * 0.95
        R = 2.4
        x, y, z = math.cos(a) * R, math.sin(a) * R, 0.5 + i * 0.9
        s.box((x, y, z), (1.6, 1.1, 0.1), rot=(0, 0, a + PI / 2), key="ghost")
        for sx, sy, w, d in ((0, 0.55, 1.6, 0.04), (0, -0.55, 1.6, 0.04), (0.8, 0, 0.04, 1.1), (-0.8, 0, 0.04, 1.1)):
            ca, sa = math.cos(a + PI / 2), math.sin(a + PI / 2)
            s.box((x + sx * ca - sy * sa, y + sx * sa + sy * ca, z + 0.06), (w, d, 0.04), rot=(0, 0, a + PI / 2), key="glow")


def prop_abyss_monolith(s):
    """深淵のモノリス (12 m)。光を吸う黒い柱。細い光の筋と、浮かぶ輪だけが見える。"""
    s.box((0, 0, 0), (4.4, 4.4, 0.35), base=True)
    s.box((0, 0, 0.35), (3.2, 3.2, 0.35), base=True)
    s.cyl((0, 0, 0.7), (1.7, 1.15), 11.0, 4, rot=(0, 0, PI / 4), base=True, key="obs")
    s.cone((0, 0, 11.7), r=1.15, h=1.1, seg=4, rot=(0, 0, PI / 4), base=True, key="obs")
    s.box((0, -1.1, 6.0), (0.09, 0.05, 8.0), key="glow")
    s.box((0, -1.1, 6.0), (0.5, 0.05, 0.09), key="lume")
    s.ring((0, 0, 8.6), 2.5, 0.06, 40, rot=(0.0, 0.0, 0.0), key="glow", sub=5)
    for i in range(3):
        a = i * 2 * PI / 3
        s.sphere((math.cos(a) * 2.5, math.sin(a) * 2.5, 8.6), (0.16, 0.16, 0.16), 6, "lume")


MODELS = [
    # id, 関数, 風化, 区分, 名前, 説明, 用途, タグ (最初のタグ = 帯)
    ("prop_lume_coral", prop_lume_coral, 0.02, "prop", "Lume Coral", "Branching coral with pale branches and glowing violet tips, three trunks on a stone base. About 2.9 m tall; the bioluminescent dressing of the luminous deep.", ["decoration"], ["luminous-deep", "coral", "bioluminescent", "overgrowth"]),
    ("prop_glass_sponge", prop_glass_sponge, 0.02, "prop", "Glass Sponge Colony", "Seven flared bone-white sponge tubes (0.8-2.4 m) with softly glowing mouths and ring ribs, on a stone base.", ["decoration"], ["luminous-deep", "sponge", "glass-sponge", "seafloor"]),
    ("prop_lamp_stalks", prop_lamp_stalks, 0.02, "prop", "Lamp Stalks", "Nine slender bent stalks (1.6-3.8 m) each tipped with a glowing bulb, violet or amber: a soft light grove for dark basins.", ["decoration"], ["luminous-deep", "stalk", "bioluminescent", "lamp"]),
    ("prop_whale_fall", prop_whale_fall, 0.04, "prop", "Whale Fall", "A whale skeleton lying on the seabed, about 15 m long: spine, eight rib pairs, skull and jaw, with violet bacterial mats glowing around the bones. A landmark.", ["landmark"], ["luminous-deep", "whale-fall", "skeleton", "landmark", "bones"]),
    ("prop_tubeworm_garden", prop_tubeworm_garden, 0.02, "prop", "Tubeworm Garden", "Sixteen white tubeworm tubes (0.9-2.6 m) tipped with orange-red plumes, on a rock mound: scenery version of the Tubeworm Spitter enemy.", ["decoration"], ["luminous-deep", "tubeworm", "vent", "seafloor"]),
    ("prop_nodule_field", prop_nodule_field, 0.03, "prop", "Manganese Nodule Field", "A patch of dark nodules, 26 loose and five cyan crystal glints, about 4.8 m across: a resource-gathering spot or seabed dressing.", ["collectible", "decoration"], ["luminous-deep", "nodules", "resource", "seabed"]),
    ("prop_street_lamp", prop_street_lamp, 0.02, "prop", "Sunken Street Lamp", "A leaning iron lamp post 5.2 m tall with a curved arm and an amber lantern that still glows. Street dressing for the sunken city.", ["landmark", "decoration"], ["sunken-city", "lamp", "street", "metal"]),
    ("prop_data_obelisk", prop_data_obelisk, 0.03, "prop", "Record Obelisk", "A stepped stone obelisk 8 m tall with ten rows of glowing glyph bars on the front and a ring at mid height. Looks like a recording device; its meaning is left open.", ["landmark", "interactable"], ["sunken-city", "obelisk", "record", "glyph"]),
    ("prop_dwelling_wall", prop_dwelling_wall, 0.04, "prop", "Dwelling Ruin Corner", "A collapsed house corner 6.4 m wide: walls of uneven height, an arched doorway, a window with an amber lamp and scattered blocks.", ["decoration", "shelter"], ["sunken-city", "house", "wall", "ruin"]),
    ("prop_urn_set", prop_urn_set, 0.01, "prop", "Everyday Ware Set", "Two urns, a bowl, a plate, a cup and a ladle: everyday objects one urn of which has a glowing rim. A fun prop the hermit crab can mistake for tools.", ["decoration", "collectible"], ["sunken-city", "urn", "pottery", "daily-life"]),
    ("prop_conduit_bundle", prop_conduit_bundle, 0.02, "prop", "Conduit Bundle", "Five iron pipes of different widths bundled by three clamps along 7 m, glowing seams at each end and a bend with an amber lamp.", ["decoration", "obstacle"], ["sunken-city", "pipe", "conduit", "infrastructure"]),
    ("prop_mural_panel", prop_mural_panel, 0.02, "prop", "Mural Panel", "A framed stone panel 4.8 m wide and 3.8 m tall with concentric ring reliefs, amber spirals and a row of five glowing circles. The meaning of the pictures is left open.", ["landmark", "interactable"], ["sunken-city", "mural", "relief", "wall"]),
    ("prop_glow_rubble", prop_glow_rubble, 0.04, "prop", "Glowing Rubble", "A heap of fourteen fallen blocks about 4 m across, with amber light leaking from its cracks.", ["obstacle", "decoration"], ["sunken-city", "rubble", "debris", "ruin"]),
    ("fx_afterimage_ghost", fx_afterimage_ghost, 0.0, "effect", "Afterimage Echo", "Four translucent copies of a diamond body, spaced 1.7 m apart and fading backwards, each with a violet ring and a tiny eye. Visual for the lingering-presence phenomenon.", ["effect"], ["abyss", "afterimage", "echo", "phenomenon", "alpha"]),
    ("fx_phase_rift", fx_phase_rift, 0.0, "effect", "Phase Rift", "A tall oval rift 5.3 m high: glowing double frame, a translucent wobbling face and ten glowing shards. Visual for places overlapping.", ["effect", "interactable"], ["abyss", "rift", "portal", "phenomenon", "alpha"]),
    ("fx_rainbow_current", fx_rainbow_current, 0.0, "effect", "Rainbow Current", "Five translucent ribbons (red, yellow, green, cyan, violet) twisting 1.6 turns up a 12 m column and widening as they rise. Visual for the final-depth rainbow current.", ["effect"], ["abyss", "rainbow", "current", "ribbon", "alpha"]),
    ("prop_floating_stones", prop_floating_stones, 0.03, "prop", "Floating Stones", "Nine stones drifting at 1-6 m in a loose ring, violet underlight on each and thin translucent threads linking them. Visual for the weight-drift phenomenon.", ["landmark", "platform"], ["abyss", "floating", "stones", "phenomenon", "alpha"]),
    ("fx_pressure_husk", fx_pressure_husk, 0.0, "effect", "Pressure Husk Dome", "A translucent dome 8 m wide and 3.2 m high (its lower half lies below the ground plane) with a glowing rim and three violet shell lines. Visual for an area that keeps an earlier pressure.", ["effect", "safe-zone"], ["abyss", "dome", "pressure", "phenomenon", "alpha"]),
    ("prop_invisible_steps", prop_invisible_steps, 0.0, "prop", "Unseen Steps", "Six faint translucent slabs (1.6 x 1.1 m) spiralling up 4.5 m, only their edges glowing. Visual for the invisible-footing phenomenon.", ["platform"], ["abyss", "steps", "platform", "phenomenon", "alpha"]),
    ("prop_abyss_monolith", prop_abyss_monolith, 0.0, "prop", "Abyssal Monolith", "A light-swallowing black pillar 12.8 m tall on two steps, with one thin glowing seam and a floating ring with three violet beads. Its meaning is left open.", ["landmark"], ["abyss", "monolith", "landmark", "mystery"]),
]
