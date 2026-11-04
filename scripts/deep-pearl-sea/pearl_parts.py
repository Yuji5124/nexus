"""DEEP-PEARL SEA の部品 (水深4,500m「乳白色の海」の背景オブジェクト 20 点の形・一覧)。build_pearl_parts.py が読む。

『甲殻類にも都合があります。』のコンセプト (水深4,500m、世界の「脱皮」で生まれた真珠のように白く輝く海。白いサンゴ、半透明の殻の森、
真珠質の結晶、遠景の白い神殿とアーチ、巨大な抜け殻が地形になる、殻の粉が雪のように積もる) の背景を、見た目だけで部品にした案。
ボス (誰もいない王) の造形は含めない (ボスは別途 ChatGPT と進める)。脱皮の仕組みや遺跡の正体は決めていない。
向き・単位: 1 unit = 1 m、Blender の Z が上 (glTF は Y が上)、正面は Blender の -Y (glTF の +Z)、原点は底の中心。
"""
import math
import random

import bmesh
from mathutils import Matrix, Vector, Euler

PI = math.pi
KEYS = ("pearl", "nacre", "shadow", "gold", "jade", "pink", "glass", "leaf", "dust", "veil", "rosev", "jadev")


def extend_shape(Shape):
    class Shape2(Shape):
        def __init__(self):
            self.bm = {k: bmesh.new() for k in KEYS}

        def limb(self, p1, p2, r=0.08, r2=None, seg=6, key="pearl"):
            a, b = Vector(p1), Vector(p2)
            d = b - a
            rot = d.to_track_quat("Z", "Y").to_euler()
            self.cyl((a + b) / 2, (r, r if r2 is None else r2), d.length, seg, tuple(rot), key)

        def ellipsoid(self, loc, size, direction=(0, 0, 1), seg=8, key="pearl"):
            """size=(幅, 厚み, 長さ) の楕円体。長手 (size[2]) を direction へ向ける。"""
            v = bmesh.ops.create_uvsphere(self.bm[key], u_segments=seg, v_segments=max(4, seg // 2 + 1), radius=1)["verts"]
            rot = Vector(direction).normalized().to_track_quat("Z", "Y").to_euler()
            self._put(key, v, loc, size, tuple(rot))

        def open_cone(self, loc=(0, 0, 0), r=(1, 1), h=1, seg=24, rot=(0, 0, 0), key="veil"):
            res = bmesh.ops.create_cone(self.bm[key], cap_ends=False, cap_tris=False, segments=seg, radius1=r[0], radius2=max(r[1], 1e-4), depth=1)
            self._put(key, res["verts"], loc, (1, 1, h), rot)

        def ribbon(self, pts, width, key="veil"):
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

    return Shape2


def _dir(a, tilt):
    return Vector((math.sin(tilt) * math.cos(a), math.sin(tilt) * math.sin(a), math.cos(tilt)))


def _mound(s, R, h, key="pearl"):
    s.sphere((0, 0, 0), (R, R * 0.9, h), 12, key)


# ================================================================ 海底の植物・結晶・貝
def prop_pearl_coral(s):
    """白い枝サンゴ。真珠色の枝の先に、淡い桃色の粒。"""
    rnd = random.Random(31)
    _mound(s, 1.3, 0.35)

    def branch(p, d, length, r, depth):
        q = p + d * length
        s.limb(p, q, r, r * 0.72, 5, "pearl")
        if depth == 0:
            s.sphere(q, (r * 1.8,) * 3, 6, "pink")
            return
        for k in range(3 if depth > 1 else 2):
            a = rnd.uniform(0, 2 * PI)
            nd = (d + _dir(a, rnd.uniform(0.5, 0.9)) * 0.9).normalized()
            if nd.z < 0.25:
                nd.z = 0.25
                nd.normalize()
            branch(q, nd, length * 0.72, r * 0.72, depth - 1)

    for k in range(2):
        a = k * PI + 0.5
        branch(Vector((math.cos(a) * 0.35, math.sin(a) * 0.35, 0.2)), _dir(a, 0.3), 1.0, 0.12, 3)


def prop_nacre_leaf_forest(s):
    """半透明の殻の森。真珠質のうすい葉が束になって立つ (脈は不透明)。"""
    rnd = random.Random(5)
    _mound(s, 1.6, 0.3)
    for i in range(10):
        a = rnd.uniform(0, 2 * PI)
        d = rnd.uniform(0.0, 1.0)
        h = rnd.uniform(1.8, 4.0)
        base = Vector((math.cos(a) * d, math.sin(a) * d, 0.2))
        top = base + _dir(a + rnd.uniform(-0.5, 0.5), rnd.uniform(0.05, 0.4)) * h
        axis = top - base
        s.ellipsoid((base + top) / 2, (0.42, 0.04, h * 0.52), axis, 8, "leaf")
        s.limb(base, base + axis * 0.92, 0.03, 0.012, 4, "pearl")


def prop_pearl_crystal_giant(s):
    """真珠質の巨大な結晶。六角柱に先のとがった頭。最大 5 m。底に小さな真珠。"""
    rnd = random.Random(9)
    _mound(s, 1.8, 0.4)
    for i in range(6):
        a = i * 2 * PI / 6 + rnd.uniform(-0.3, 0.3)
        d = 0.0 if i == 0 else rnd.uniform(0.7, 1.4)
        h = 5.0 if i == 0 else rnd.uniform(1.8, 3.8)
        r = 0.55 if i == 0 else rnd.uniform(0.28, 0.45)
        tilt = 0.0 if i == 0 else rnd.uniform(0.1, 0.32)
        x, y = math.cos(a) * d, math.sin(a) * d
        rot = (math.sin(tilt) * math.sin(a), -math.sin(tilt) * math.cos(a), 0)
        s.cyl((x, y, 0.2), (r, r * 0.9), h, 6, rot=rot, base=True, key="nacre")
        top = Vector((x, y, 0.2)) + _dir(a + PI / 2, tilt) * h * 0.0 + Vector((0, 0, h))
        s.cone((top.x, top.y, top.z - 0.02), r=r * 0.9, h=r * 1.6, seg=6, rot=rot, key="pink", base=True)
    for i in range(9):
        a = rnd.uniform(0, 2 * PI)
        d = rnd.uniform(1.0, 1.9)
        s.sphere((math.cos(a) * d, math.sin(a) * d, 0.2), (0.16, 0.16, 0.16), 6, "pearl")


def prop_husk_arch(s):
    """巨大な抜け殻が作るアーチ (幅 14 m、高さ 7 m)。肋骨のような殻のリブが並び、奥は開いている。地形の一部に使う。"""
    n = 9
    pts = []
    for i in range(n):
        y = -6.0 + i * 12.0 / (n - 1)
        prof = math.sin(PI * (i + 0.5) / n) ** 0.55
        R = 1.6 + 5.0 * prof
        s.arc((0, y, 0), R=R, w=0.5, d=0.62, a0=0.0, a1=PI, seg=14, key="pearl")
        pts.append((0, y, R + 0.5))
        for sx in (-1, 1):
            s.sphere((sx * (R + 0.25), y, 0.3), (0.5, 0.5, 0.4), 7, "shadow")
    for i in range(n - 1):
        s.limb(pts[i], pts[i + 1], 0.2, 0.2, 6, "nacre")
    for i in range(1, n - 1, 2):
        s.sphere(pts[i], (0.32, 0.32, 0.32), 7, "pink")
    s.sphere((0, 0, -0.1), (8.5, 7.0, 0.5), 14, "pearl")


def prop_peeling_plates(s):
    """脱皮の層。古い殻の板が本のページのようにめくれ、下から新しい真珠質の層が出ている。"""
    s.sphere((0, 0, 0), (3.2, 2.6, 0.5), 12, "nacre")
    for i in range(6):
        t = i / 5
        s.box((-0.5 + i * 0.12, 0.0, 0.5 + i * 0.12), (3.8 - i * 0.28, 2.6 - i * 0.2, 0.1), rot=(0.12 + t * 0.62, 0.05 * i, 0.15 * i), base=True, key="pearl")
        s.box((-0.5 + i * 0.12, -1.25 + i * 0.1, 0.62 + i * 0.4 + t * 0.2), (3.7 - i * 0.28, 0.1, 0.22), rot=(0.12 + t * 0.62, 0.05 * i, 0.15 * i), key="shadow")
    for i in range(5):
        a = i * 2 * PI / 5 + 0.3
        s.sphere((math.cos(a) * 2.4, math.sin(a) * 2.0, 0.25), (0.18, 0.18, 0.18), 6, "pink")


def prop_pearl_clam(s):
    """真珠の大きな二枚貝。口を開け、中に真珠を抱く (幅 4 m)。"""
    s.sphere((0, 0, 0.45), (2.0, 1.7, 0.45), 14, "pearl")
    for k in range(9):
        a = -PI * 0.42 + k * PI * 0.84 / 8
        s.limb((math.sin(a) * 0.3, -math.cos(a) * 0.3, 0.7), (math.sin(a) * 1.9, -math.cos(a) * 1.6, 0.52), 0.05, 0.03, 4, "shadow")
    s.sphere((0, 0, 0.62), (1.7, 1.45, 0.2), 12, "nacre")
    s.sphere((0, 1.3, 1.5), (1.9, 0.5, 1.5), 12, "pearl")
    s.sphere((0, 1.15, 1.45), (1.65, 0.28, 1.3), 12, "nacre")
    for (x, y, r) in ((0.0, -0.1, 0.5), (0.7, 0.4, 0.28), (-0.8, 0.2, 0.22), (0.3, -0.7, 0.2), (-0.4, 0.6, 0.18)):
        s.sphere((x, y, 0.75 + r * 0.4), (r, r, r), 10, "pearl")
        s.sphere((x + r * 0.3, y - r * 0.3, 0.75 + r * 0.8), (r * 0.25, r * 0.25, r * 0.25), 5, "glass")


def prop_pearl_heap(s):
    """真珠の山。大小 60 個ほどの真珠が盛り上がる (幅 3 m)。"""
    rnd = random.Random(2)
    _mound(s, 1.5, 0.25, "shadow")
    for i in range(60):
        a = rnd.uniform(0, 2 * PI)
        d = abs(rnd.gauss(0, 0.6))
        r = rnd.uniform(0.12, 0.34)
        z = max(0.18, 0.7 - d * 0.5) * rnd.uniform(0.5, 1.0) + r * 0.5
        s.sphere((math.cos(a) * d, math.sin(a) * d, z), (r, r, r), 6, "pearl" if i % 5 else "pink")


def prop_shell_dust_dune(s):
    """殻の粉の吹きだまり。雪のように積もった低い砂丘で、風の筋と貝のかけらがある (幅 8 m)。"""
    rnd = random.Random(17)
    s.sphere((0, 0, 0), (4.2, 3.0, 0.7), 16, "pearl")
    for i in range(6):
        y = -1.8 + i * 0.7
        w = 3.2 * math.sqrt(max(0.05, 1 - (y / 2.7) ** 2))
        s.box((0, y, 0.55 + 0.04 * i), (w * 1.3, 0.08, 0.06), rot=(0, 0, 0.1 * (i % 2 - 0.5)), key="shadow")
    for i in range(7):
        a = rnd.uniform(0, 2 * PI)
        d = rnd.uniform(1.0, 3.0)
        s.box((math.cos(a) * d, math.sin(a) * d * 0.7, 0.3), (rnd.uniform(0.25, 0.5), rnd.uniform(0.2, 0.4), 0.06), rot=(rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), rnd.uniform(0, 3)), key="nacre")
    for i in range(14):
        a = rnd.uniform(0, 2 * PI)
        d = rnd.uniform(0.5, 3.5)
        s.sphere((math.cos(a) * d, math.sin(a) * d * 0.7, rnd.uniform(0.9, 2.6)), (0.05, 0.05, 0.05), 4, "dust")


# ================================================================ 遠景の白い遺跡 (正体は決めない)
def prop_white_colonnade(s):
    """白い列柱 (長さ 12 m、高さ 6 m)。梁が一部落ち、金の輪が柱を巻く。"""
    s.box((0, 0, 0), (13.0, 3.0, 0.4), base=True, key="pearl")
    for i in range(5):
        x = -5.0 + i * 2.5
        h = 5.4 if i != 3 else 3.2
        s.cyl((x, 0, 0.4), (0.55, 0.45), h, 12, base=True, flute=0.12, key="pearl")
        s.cyl((x, 0, 0.4 + h), (0.7, 0.7), 0.3, 12, base=True, key="pearl")
        s.cyl((x, 0, 0.4), (0.7, 0.7), 0.3, 12, base=True, key="pearl")
        s.ring((x, 0, 0.4 + h * 0.5), 0.55, 0.04, 20, key="gold", sub=4)
    s.box((-3.75, 0, 5.8), (3.0, 1.0, 0.6), base=True, key="pearl")
    s.box((-1.25, 0, 5.8), (2.3, 1.0, 0.6), rot=(0, 0.06, 0), base=True, key="pearl")
    s.box((2.4, 0, 3.5), (1.8, 0.9, 0.5), rot=(0.0, 0.5, 0.2), base=True, key="shadow")
    s.box((3.8, 0.4, 0.4), (0.8, 0.6, 0.5), rot=(0, 0, 0.5), base=True, key="pearl")


def prop_white_arch_gate(s):
    """石の大きなアーチ (高さ 8 m)。要石に金、柱の刻みが翡翠色にほのかに光る。"""
    s.box((0, 0, 0), (9.0, 2.6, 0.5), base=True, key="pearl")
    for sx in (-1, 1):
        s.box((sx * 3.1, 0, 0.5), (1.5, 1.6, 3.6), base=True, key="pearl")
        s.box((sx * 3.1, 0, 4.1), (1.7, 1.8, 0.35), base=True, key="shadow")
        for k in range(4):
            s.box((sx * 3.1, -0.82, 1.2 + k * 0.7), (0.9, 0.04, 0.12), key="jade")
    s.arc((0, 0, 4.4), R=2.35, w=0.95, d=1.4, a0=0.0, a1=PI, seg=16, key="pearl")
    s.box((0, 0, 7.75), (0.9, 1.5, 0.7), base=True, key="gold")
    s.ring((0, -0.72, 4.4), 1.9, 0.045, 28, rot=(PI / 2, 0, 0), key="jade", sub=4)


def prop_white_dome_pavilion(s):
    """ドームの小さな神殿 (高さ 7 m)。八本の柱の上に丸屋根、金の尖塔。"""
    for k, (R, h) in enumerate(((3.6, 0.3), (3.2, 0.3), (2.8, 0.3))):
        s.cyl((0, 0, k * 0.3), (R, R), h, 16, base=True, key="pearl")
    for i in range(8):
        a = i * PI / 4
        s.cyl((math.cos(a) * 2.3, math.sin(a) * 2.3, 0.9), (0.28, 0.24), 3.0, 10, base=True, key="pearl")
    s.cyl((0, 0, 3.9), (2.7, 2.7), 0.35, 16, base=True, key="shadow")
    s.sphere((0, 0, 4.2), (2.5, 2.5, 1.9), 16, "pearl")
    s.ring((0, 0, 4.25), 2.5, 0.06, 28, key="gold", sub=4)
    s.cone((0, 0, 6.0), r=0.14, h=1.3, seg=6, key="gold", base=True)
    s.sphere((0, 0, 6.0), (0.2, 0.2, 0.2), 8, "gold")
    s.cyl((0, -2.0, 0.9), (0.6, 0.6), 0.05, 12, base=True, key="jade")


def prop_terrace_falls(s):
    """段々になった白い岩の滝 (高さ 6 m)。薄い水の帯が段を流れ落ちる。"""
    levels = ((4.2, 0.0), (3.2, 1.6), (2.3, 3.2))
    for i, (R, z) in enumerate(levels):
        s.cyl((i * 0.35, 0, z), (R * 1.05, R), 1.7, 14, base=True, key="pearl")
        s.sphere((i * 0.35, 0, z + 1.7), (R * 0.95, R * 0.9, 0.12), 12, "nacre")
    for i, (R, z) in enumerate(levels[1:], start=1):
        for k in range(3):
            a = -PI / 2 + (k - 1) * 0.55
            x, y = i * 0.35 + math.cos(a) * (R * 1.06 + 0.04), math.sin(a) * (R * 1.06 + 0.04)
            s.box((x, y, z - 0.85), (0.8, 0.08, 1.7), rot=(0, 0, a + PI / 2), key="veil")
    for i in range(5):
        a = i * 2 * PI / 5
        s.cone((math.cos(a) * 3.8, math.sin(a) * 3.8, 0.0), r=0.3, h=0.8 + 0.2 * (i % 3), seg=5, key="pearl", base=True)


def prop_shell_spire(s):
    """らせん巻きの高い殻 (高さ 8 m)。段ごとに少しずつねじれ、縁が桃色。"""
    n = 12
    for i in range(n):
        r = 1.9 * (1 - i / (n + 2))
        z = i * 0.62
        s.cyl((0, 0, z), (r, r * 0.9), 0.66, 12, rot=(0.0, 0.0, i * 0.5), base=True, key="pearl")
        s.ring((r * 0.3, 0, z + 0.62), r * 0.85, 0.05, 18, key="pink" if i % 2 else "nacre", sub=4, rot=(0, 0, i * 0.3))
    s.cone((0, 0, n * 0.62), r=1.9 * (1 - n / (n + 2)), h=0.9, seg=10, key="nacre", base=True)
    s.sphere((0, -1.5, 0.5), (0.9, 0.5, 0.5), 8, "shadow")


# ================================================================ 光・粉・膜・泡 (半透明の効果)
def fx_light_curtain(s):
    """光の幕。海中のあらゆる方向からやわらかく差す光を表す、入れ子の広い光の筒 (高さ 25 m)。"""
    for r0, r1 in ((4.0, 9.0), (2.8, 6.5), (1.6, 4.0)):
        s.open_cone((0, 0, 12.5), (r0, r1), 25, 22, key="veil")
    s.cyl((0, 0, 0), (3.0, 3.0), 0.04, 20, base=True, key="rosev")


def fx_dust_current(s):
    """殻の粉の海流。粉の帯がゆるくらせんを描いて立ちのぼり、粒が混ざる (高さ 9 m)。"""
    for k in range(2):
        pts = []
        for i in range(36):
            t = i / 35
            ang = 2 * PI * (1.4 * t) + k * PI
            R = 1.0 + 1.6 * t
            pts.append((math.cos(ang) * R, math.sin(ang) * R, 9.0 * t))
        s.ribbon(pts, 0.8, "veil" if k == 0 else "rosev")
    rnd = random.Random(4)
    for i in range(36):
        t = rnd.uniform(0, 1)
        ang = 2 * PI * (1.4 * t) + rnd.choice((0, PI)) + rnd.uniform(-0.3, 0.3)
        R = 1.0 + 1.6 * t + rnd.uniform(-0.3, 0.5)
        s.sphere((math.cos(ang) * R, math.sin(ang) * R, 9.0 * t), (0.07, 0.07, 0.07), 4, "dust")


def fx_molt_sheet(s):
    """脱皮の膜。古い殻の薄い膜が、はがれて端から巻き上がる (幅 5 m)。"""
    nx, ny = 9, 7
    rows = []
    for j in range(ny):
        v = j / (ny - 1)
        pts = []
        for i in range(nx):
            u = i / (nx - 1)
            curl = max(0.0, u - 0.45) ** 1.4 * 5.0
            x = -2.5 + 5.0 * u * (1 - 0.18 * max(0.0, u - 0.45))
            y = -1.6 + 3.2 * v
            z = 0.4 + curl * 0.9 + 0.15 * math.sin(v * PI)
            pts.append((x, y + 0.2 * math.sin(u * 3), z))
        rows.append(pts)
    for j in range(ny - 1):
        mid = [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2) for a, b in zip(rows[j], rows[j + 1])]
        s.ribbon(mid, 3.2 / (ny - 1) * 1.05, "leaf")
    s.limb(Vector((-2.4, -1.6, 0.4)), Vector((-2.4, 1.6, 0.4)), 0.04, key="pearl")
    s.sphere((-2.4, 0.0, 0.4), (0.14, 0.14, 0.14), 6, "pink")


def fx_nacre_bubbles(s):
    """真珠色の泡。大小 16 個が、ゆるい柱になって上る (高さ 4.2 m)。"""
    rnd = random.Random(12)
    for i in range(16):
        t = i / 15
        r = 0.12 + 0.34 * t * rnd.uniform(0.6, 1.0)
        a = rnd.uniform(0, 2 * PI)
        d = rnd.uniform(0.0, 0.5) * (0.4 + t)
        s.sphere((math.cos(a) * d, math.sin(a) * d, 0.3 + t * 3.7), (r, r, r), 8, "glass")
        s.sphere((math.cos(a) * d + r * 0.3, math.sin(a) * d - r * 0.3, 0.3 + t * 3.7 + r * 0.35), (r * 0.18, r * 0.18, r * 0.18), 4, "dust")


def fx_iridescent_veil(s):
    """虹色のベール。長い三本の帯 (白・桃・翡翠) が、波打ちながら漂う (長さ 10 m)。"""
    for k, key in enumerate(("veil", "rosev", "jadev")):
        pts = []
        for i in range(30):
            t = i / 29
            x = -5.0 + 10.0 * t
            y = 0.7 * math.sin(t * 2 * PI + k * 1.3) + (k - 1) * 0.9
            z = 2.5 + 0.8 * math.sin(t * 3 * PI + k) + k * 0.35
            pts.append((x, y, z))
        s.ribbon(pts, 1.5 - 0.15 * k, key)


# ================================================================ 小魚 (ボスの王の身体とは別の、ふつうの群れ用)
def fauna_pearl_fish(s):
    """真珠色の小魚 1 匹 (全長 0.5 m)。胴・金色の尾・目・背びれ。群れで複製して使う。"""
    s.sphere((0, 0, 0), (0.09, 0.26, 0.11), 7, "pearl")
    s.cone((0, 0.28, 0), r=0.1, h=0.26, seg=4, rot=(-PI / 2, 0, 0), key="gold")
    s.cone((0, 0.0, 0.1), r=0.05, h=0.15, seg=3, rot=(0, 0, 0), key="nacre")
    for sx in (-1, 1):
        s.sphere((sx * 0.07, -0.15, 0.04), (0.022, 0.022, 0.022), 4, "shadow")
        s.cone((sx * 0.09, -0.02, -0.04), r=0.035, h=0.14, seg=3, rot=(0, sx * 1.2, 0), key="nacre")


def fx_fish_swarm_cloud(s):
    """小魚の群れの雲。70 匹の小魚が、ゆるい S 字の流れになって同じ向きに泳ぐ (長さ 14 m)。中心の個体はない。"""
    rnd = random.Random(23)
    for i in range(70):
        t = rnd.uniform(0, 1)
        x = -7.0 + 14.0 * t
        y = 2.2 * math.sin(t * 2 * PI) + rnd.gauss(0, 0.9)
        z = 3.0 + 1.2 * math.sin(t * PI * 3) + rnd.gauss(0, 0.8)
        dx = 1.0
        dy = 2.2 * 2 * PI / 14.0 * math.cos(t * 2 * PI)
        d = Vector((dx, dy + rnd.gauss(0, 0.15), rnd.gauss(0, 0.1))).normalized()
        sc = rnd.uniform(0.8, 1.2)
        loc = Vector((x, y, z))
        s.ellipsoid(loc, (0.08 * sc, 0.1 * sc, 0.24 * sc), d, 6, "pearl" if i % 4 else "nacre")
        s.ellipsoid(loc - d * 0.3 * sc, (0.07 * sc, 0.02 * sc, 0.12 * sc), d, 4, "gold")


MODELS = [
    # id, 関数, 風化 (使わない), 区分, 名前, 説明, 用途, タグ
    ("prop_pearl_coral", prop_pearl_coral, 0.0, "prop", "Pearl Coral", "White branching coral on a pearl mound, two trunks with pale pink tips, about 3 m tall.", ["decoration"], ["flora", "coral", "white", "seafloor"]),
    ("prop_nacre_leaf_forest", prop_nacre_leaf_forest, 0.0, "prop", "Nacre Leaf Forest", "Ten translucent mother-of-pearl leaves up to 4 m tall with thin pearl veins on a pearl mound: the translucent shell forest of the milky sea.", ["decoration"], ["flora", "shell-forest", "translucent", "nacre", "alpha"]),
    ("prop_pearl_crystal_giant", prop_pearl_crystal_giant, 0.0, "prop", "Giant Pearl Crystal", "Six pearly hexagonal crystals with pink points, the tallest 6.5 m, with small pearls at the base.", ["landmark", "decoration"], ["crystal", "pearl", "nacre", "landmark"]),
    ("prop_husk_arch", prop_husk_arch, 0.0, "prop", "Moulted Husk Arch", "A giant empty husk forming an arch about 16 m wide and 8 m high: nine ribbed shell arcs joined by a ridge, open at the back. Part of the terrain.", ["landmark", "terrain"], ["husk", "moult", "arch", "terrain", "landmark"]),
    ("prop_peeling_plates", prop_peeling_plates, 0.0, "prop", "Peeling Shell Layers", "Six old shell plates lifting like pages off a fresh nacre layer, with pink pearls around. The look of the seafloor moulting.", ["decoration", "terrain"], ["moult", "layers", "plates", "terrain"]),
    ("prop_pearl_clam", prop_pearl_clam, 0.0, "prop", "Pearl Clam", "A giant open bivalve about 4 m wide holding five pearls on a nacre floor.", ["decoration", "collectible"], ["clam", "pearl", "shell", "seafloor"]),
    ("prop_pearl_heap", prop_pearl_heap, 0.0, "prop", "Pearl Heap", "A heap of sixty pearls of mixed size (some pink) on a shadow-coloured base, about 3 m across.", ["decoration", "collectible"], ["pearl", "heap", "treasure"]),
    ("prop_shell_dust_dune", prop_shell_dust_dune, 0.0, "prop", "Shell-dust Drift", "A low drift of shell dust about 8 m wide, like snow, with wind lines, shell chips and a few floating motes.", ["decoration", "terrain"], ["dust", "dune", "seafloor", "snow"]),
    ("prop_white_colonnade", prop_white_colonnade, 0.0, "prop", "White Colonnade", "A 13 m colonnade of five fluted columns with gold rings, one broken, with a half-fallen beam.", ["landmark", "decoration"], ["ruin", "colonnade", "temple", "white"]),
    ("prop_white_arch_gate", prop_white_arch_gate, 0.0, "prop", "White Arch Gate", "A stone arch gate about 8 m high with a gold keystone and faint jade marks on the pillars. Its makers are left unexplained.", ["landmark", "gate"], ["ruin", "arch", "gate", "temple"]),
    ("prop_white_dome_pavilion", prop_white_dome_pavilion, 0.0, "prop", "White Dome Pavilion", "A small domed temple about 7 m tall: three steps, eight columns, a gold ring and a gold finial.", ["landmark"], ["ruin", "dome", "temple", "pavilion"]),
    ("prop_terrace_falls", prop_terrace_falls, 0.0, "prop", "Terraced Falls", "Three stacked white rock terraces about 5 m high with thin water curtains running down each step.", ["landmark", "scenery"], ["terrace", "waterfall", "rock", "scenery", "alpha"]),
    ("prop_shell_spire", prop_shell_spire, 0.0, "prop", "Shell Spire", "A tall spiral shell about 8 m high, twelve twisted whorls with pink and nacre rims.", ["landmark"], ["spire", "shell", "spiral", "landmark"]),
    ("fx_light_curtain", fx_light_curtain, 0.0, "effect", "Light Curtain", "Three nested wide translucent light shafts, 25 m high and up to 18 m across, for the soft light that comes from every direction.", ["effect"], ["light", "curtain", "volumetric", "alpha"]),
    ("fx_dust_current", fx_dust_current, 0.0, "effect", "Shell-dust Current", "Two translucent bands and 36 specks of dust spiralling 1.4 turns up a 9 m column: the unseen current the dust draws.", ["effect"], ["dust", "current", "spiral", "alpha"]),
    ("fx_molt_sheet", fx_molt_sheet, 0.0, "effect", "Moulting Sheet", "A thin translucent sheet of old shell, 5 m across, peeling off and curling up at one end.", ["effect"], ["moult", "sheet", "peel", "alpha"]),
    ("fx_nacre_bubbles", fx_nacre_bubbles, 0.0, "effect", "Nacre Bubbles", "Sixteen translucent bubbles of growing size in a loose 4 m column, each with a tiny highlight.", ["effect"], ["bubbles", "rising", "nacre", "alpha"]),
    ("fx_iridescent_veil", fx_iridescent_veil, 0.0, "effect", "Iridescent Veil", "Three wavy translucent ribbons (white, pink, jade) drifting along 10 m.", ["effect"], ["veil", "ribbon", "iridescent", "alpha"]),
    ("fauna_pearl_fish", fauna_pearl_fish, 0.0, "fauna", "Pearl Fish", "One small pearl-white fish 0.5 m long with a gold tail, fins and eyes. Meant to be instanced for ambient schools.", ["ambient"], ["fish", "small", "ambient", "instancing"]),
    ("fx_fish_swarm_cloud", fx_fish_swarm_cloud, 0.0, "fauna", "Fish Swarm Cloud", "Seventy small fish in a loose S-shaped flow 14 m long, all heading the same way, no leader. An ordinary school; not a boss body.", ["ambient"], ["fish", "swarm", "school", "ambient"]),
]
