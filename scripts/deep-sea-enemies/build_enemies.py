"""DEEP-SEA ENEMIES: 深海の敵キャラ12体 (NEXUS オリジナル)。Blender (4.x/5.x) をヘッドレスで動かして、リグ付きの GLB とサムネイルを作る。

    blender -b -P scripts/deep-sea-enemies/build_enemies.py -- <出力フォルダ> <サムネイルのフォルダ> [敵ID ...]

規約: 1 unit = 1 m、原点は足元 (浮遊する敵は基準の高さ)、glTF 出力後は Y が上、正面は +Z。
リグ: 骨は 1 パーツ 1 骨のゆるい剛体リグ (スキニングなし)。パーツは骨に固定して動かす (ローポリの見た目を壊さない)。
アニメ: 全員 Idle (ループ)。動く敵は Walk / Swim、攻撃のある敵は Attack を持つ。名前は全員そろえてある。
材質 (テクスチャなし): hull 暗い鋼 / armor 明るい装甲板 / accent 警告色のオレンジ / eye 赤い目 / glow シアンの動力 / stone 石 / rune 石の紋様 / glass 半透明
"""
import bpy, bmesh, math, os, sys, random
from mathutils import Matrix, Vector, Euler

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = os.path.abspath(argv[0]) if argv else os.path.abspath("out")
THUMBS = os.path.abspath(argv[1]) if len(argv) > 1 else os.path.join(OUT, "_thumbs")
ONLY = set(argv[2:])
PI = math.pi
FPS = 30
os.makedirs(OUT, exist_ok=True)
os.makedirs(THUMBS, exist_ok=True)


# ---------------------------------------------------------------- 形 (骨ごと・材質ごとの bmesh)
class Parts:
    def __init__(self):
        self.bm = {}
        self.bones = {}  # 名前 -> (支点, 親)
        self.order = []

    def bone(self, name, pivot, parent=None):
        self.bones[name] = (Vector(pivot), parent)
        self.order.append(name)

    def _bm(self, bone, key):
        k = (bone, key)
        if k not in self.bm:
            self.bm[k] = bmesh.new()
        return self.bm[k]

    def _put(self, bone, key, verts, loc, scale, rot):
        m = Matrix.Translation(loc) @ Euler(rot).to_matrix().to_4x4() @ Matrix.Diagonal((*scale, 1))
        bmesh.ops.transform(self._bm(bone, key), matrix=m, verts=verts)

    def box(self, bone, loc=(0, 0, 0), size=(1, 1, 1), rot=(0, 0, 0), key="hull", base=False):
        v = bmesh.ops.create_cube(self._bm(bone, key), size=1)["verts"]
        self._put(bone, key, v, (loc[0], loc[1], loc[2] + size[2] / 2 if base else loc[2]), size, rot)

    def cyl(self, bone, loc=(0, 0, 0), r=(1, 1), h=1, seg=10, rot=(0, 0, 0), key="hull", base=False):
        v = bmesh.ops.create_cone(self._bm(bone, key), cap_ends=True, cap_tris=False, segments=seg, radius1=r[0], radius2=max(r[1], 1e-4), depth=1)["verts"]
        self._put(bone, key, v, (loc[0], loc[1], loc[2] + h / 2 if base else loc[2]), (1, 1, h), rot)

    def cone(self, bone, loc=(0, 0, 0), r=1, h=1, seg=8, rot=(0, 0, 0), key="hull", base=False):
        self.cyl(bone, loc, (r, 0.0), h, seg, rot, key, base)

    def sphere(self, bone, loc=(0, 0, 0), r=(1, 1, 1), seg=10, key="hull"):
        v = bmesh.ops.create_uvsphere(self._bm(bone, key), u_segments=seg, v_segments=max(4, seg // 2 + 1), radius=1)["verts"]
        self._put(bone, key, v, loc, r, (0, 0, 0))

    def ring(self, bone, loc=(0, 0, 0), R=1.0, r=0.05, seg=28, rot=(0, 0, 0), key="accent", sub=5):
        bm = self._bm(bone, key)
        grid = []
        for i in range(seg):
            a = 2 * PI * i / seg
            grid.append([bm.verts.new(((R + r * math.cos(2 * PI * j / sub)) * math.cos(a), (R + r * math.cos(2 * PI * j / sub)) * math.sin(a), r * math.sin(2 * PI * j / sub))) for j in range(sub)])
        for i in range(seg):
            n = (i + 1) % seg
            for j in range(sub):
                k = (j + 1) % sub
                try:
                    bm.faces.new((grid[i][j], grid[i][k], grid[n][k], grid[n][j]))
                except ValueError:
                    pass
        self._put(bone, key, [v for row in grid for v in row], loc, (1, 1, 1), rot)

    def limb(self, bone, p1, p2, r=0.08, r2=None, seg=8, key="hull"):
        """p1 から p2 へ伸びる円柱 (先細り可)。"""
        a, b = Vector(p1), Vector(p2)
        d = b - a
        rot = d.to_track_quat("Z", "Y").to_euler()
        self.cyl(bone, (a + b) / 2, (r, r if r2 is None else r2), d.length, seg, tuple(rot), key)


# ---------------------------------------------------------------- 材質
MAT_DEF = {
    "hull": ((0.10, 0.14, 0.18), 0.6, 0.5, None),
    "armor": ((0.30, 0.36, 0.40), 0.55, 0.45, None),
    "accent": ((0.85, 0.30, 0.08), 0.2, 0.5, None),
    "eye": ((1.0, 0.08, 0.06), 0.0, 0.3, 4.0),
    "glow": ((0.16, 0.92, 0.86), 0.0, 0.4, 3.0),
    "stone": ((0.30, 0.38, 0.40), 0.0, 0.9, None),
    "rune": ((0.16, 0.92, 0.86), 0.0, 0.4, 3.0),
    "glass": ((0.55, 0.85, 1.0), 0.0, 0.2, 0.6),
}


def make_mats():
    mats = {}
    for key, (rgb, metal, rough, emit) in MAT_DEF.items():
        m = bpy.data.materials.new("enemy_" + key)
        m.use_nodes = True
        b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        b.inputs["Base Color"].default_value = (*rgb, 1)
        b.inputs["Metallic"].default_value = metal
        b.inputs["Roughness"].default_value = rough
        if emit:
            b.inputs["Base Color"].default_value = (rgb[0] * 0.25, rgb[1] * 0.25, rgb[2] * 0.25, 1)
            b.inputs["Emission Color"].default_value = (*rgb, 1)
            b.inputs["Emission Strength"].default_value = emit
        if key == "glass":
            b.inputs["Alpha"].default_value = 0.45
            m.blend_method = "BLEND"
        mats[key] = m
    return mats


# ---------------------------------------------------------------- リグとアニメの道具
class Poser:
    """骨の向きはすべて +Y に揃えてあるので、骨の軸 = アーマチュアの軸 (X 右 / Y 後ろ / Z 上)。角度は度。"""

    def __init__(self, arm):
        self.arm = arm
        for pb in arm.pose.bones:
            pb.rotation_mode = "QUATERNION"
        self.rot_ = {}
        self.loc_ = {}
        self.scl_ = {}

    def rot(self, bone, x=0.0, y=0.0, z=0.0):
        q = Euler((math.radians(x), math.radians(y), math.radians(z)), "XYZ").to_quaternion()
        self.rot_[bone] = q @ self.rot_[bone] if bone in self.rot_ else q

    def move(self, bone, x=0.0, y=0.0, z=0.0):
        self.loc_[bone] = self.loc_.get(bone, Vector()) + Vector((x, y, z))

    def scale(self, bone, s=1.0, sx=None, sy=None, sz=None):
        self.scl_[bone] = Vector((sx if sx is not None else s, sy if sy is not None else s, sz if sz is not None else s))

    def key(self, frame):
        for pb in self.arm.pose.bones:
            pb.rotation_quaternion = self.rot_.get(pb.name, (1, 0, 0, 0))
            pb.location = self.loc_.get(pb.name, (0, 0, 0))
            pb.scale = self.scl_.get(pb.name, (1, 1, 1))
            pb.keyframe_insert("rotation_quaternion", frame=frame)
            pb.keyframe_insert("location", frame=frame)
            pb.keyframe_insert("scale", frame=frame)
        self.rot_, self.loc_, self.scl_ = {}, {}, {}


def sin2(f, n):
    return math.sin(2 * PI * f / n)


def cos2(f, n):
    return math.cos(2 * PI * f / n)


# ---------------------------------------------------------------- 敵 12 体
# 各関数は Parts を作って、アニメの一覧 [(クリップ名, 最終フレーム, キーのフレーム, 姿勢の関数 fn(p, f))] を返す。

def scout_drone(e):
    e.bone("Root", (0, 0, 1.3))
    e.bone("Body", (0, 0, 1.3), "Root")
    rotors = {"FL": (-0.95, -0.85), "FR": (0.95, -0.85), "BL": (-0.95, 0.85), "BR": (0.95, 0.85)}
    e.sphere("Body", (0, 0, 1.3), (0.72, 0.8, 0.34), 12, "hull")
    e.ring("Body", (0, 0, 1.3), 0.78, 0.06, 28, key="accent")
    e.sphere("Body", (0, 0.1, 1.52), (0.46, 0.5, 0.15), 10, "armor")
    e.sphere("Body", (0, -0.64, 1.32), (0.24, 0.12, 0.24), 10, "eye")
    e.ring("Body", (0, -0.7, 1.32), 0.27, 0.04, 14, rot=(PI / 2, 0, 0), key="armor")
    e.sphere("Body", (0, 0, 1.0), (0.22, 0.22, 0.1), 8, "glow")
    e.limb("Body", (0, 0.45, 1.5), (0, 0.6, 1.95), 0.025, key="armor")
    e.sphere("Body", (0, 0.6, 1.97), (0.06, 0.06, 0.06), 6, "accent")
    for n, (x, y) in rotors.items():
        b = "Rot" + n
        e.bone(b, (x, y, 1.45), "Body")
        e.limb("Body", (x * 0.4, y * 0.4, 1.32), (x, y, 1.42), 0.06, 0.05, 6, "armor")
        e.cyl(b, (x, y, 1.45), (0.1, 0.1), 0.12, 8, key="hull")
        e.box(b, (x, y, 1.54), (0.95, 0.12, 0.025), key="armor")
        e.box(b, (x, y, 1.54), (0.12, 0.95, 0.025), key="armor")

    def idle(p, f):
        p.move("Root", z=0.1 * sin2(f, 30))
        p.rot("Body", x=3 * sin2(f, 30), y=3 * cos2(f, 30))
        for n in rotors:
            p.rot("Rot" + n, z=(1 if n in ("FL", "BR") else -1) * 72 * (f / 3))

    def attack(p, f):
        k = math.sin(PI * f / 18)
        p.move("Root", y=-1.4 * k, z=-0.5 * k)
        p.rot("Root", x=-32 * k)
        idle(p, f)

    return [("Idle", 30, tuple(range(0, 31, 3)), idle), ("Attack", 18, (0, 3, 6, 9, 12, 15, 18), attack)]


def crawler_bot(e):
    e.bone("Root", (0, 0, 0))
    e.bone("Body", (0, 0, 0.75), "Root")
    e.box("Body", (0, 0.05, 0.75), (1.3, 1.9, 0.55), key="hull")
    e.box("Body", (0, 0.0, 1.08), (1.0, 1.5, 0.12), key="armor")
    e.box("Body", (0, -1.0, 0.8), (0.9, 0.5, 0.45), key="hull")
    for sx in (-1, 1):
        e.sphere("Body", (sx * 0.28, -1.28, 0.9), (0.14, 0.1, 0.14), 8, "eye")
        e.cone("Body", (sx * 0.2, -1.32, 0.62), r=0.07, h=0.35, seg=5, rot=(PI / 2, 0, 0), key="accent")
    e.ring("Body", (0, 0.1, 0.75), 0.7, 0.04, 20, rot=(0, 0, 0), key="accent")
    e.box("Body", (0, 0.95, 0.85), (0.6, 0.25, 0.35), key="armor")
    e.sphere("Body", (0, 1.1, 0.9), (0.2, 0.1, 0.2), 8, "glow")
    legs = {}
    for side, sx in (("L", -1), ("R", 1)):
        for i, y in enumerate((-0.6, 0.0, 0.6)):
            u, l = f"Leg_{side}{i}_U", f"Leg_{side}{i}_L"
            hip = (sx * 0.6, y, 0.75)
            knee = (sx * 1.35, y - 0.1, 1.0)
            foot = (sx * 1.75, y - 0.2, 0.0)
            e.bone(u, hip, "Body")
            e.bone(l, knee, u)
            e.limb(u, hip, knee, 0.1, 0.08, 7, "hull")
            e.sphere(u, knee, (0.12, 0.12, 0.12), 6, "armor")
            e.limb(l, knee, foot, 0.08, 0.04, 7, "hull")
            e.cone(l, foot, r=0.06, h=0.12, seg=5, rot=(PI, 0, 0), key="accent")
            legs[(side, i)] = (sx, u, l)

    def gait(p, t, amp):
        for (side, i), (sx, u, l) in legs.items():
            ph = t + (0.5 if (i % 2) != (sx > 0) else 0.0)
            w = math.sin(2 * PI * ph)
            up = max(0.0, w)
            p.rot(u, y=-sx * amp * up, z=sx * 12 * w)
            p.rot(l, y=-sx * amp * 0.6 * up)

    def idle(p, f):
        p.move("Body", z=0.02 * sin2(f, 60))
        for (side, i), (sx, u, l) in legs.items():
            p.rot(u, z=sx * 3 * sin2(f + i * 8, 60))

    def walk(p, f):
        gait(p, f / 24, 24)
        p.move("Body", z=abs(sin2(f, 12)) * 0.05)
        p.rot("Body", y=2 * sin2(f, 12))

    def attack(p, f):
        k = math.sin(PI * f / 16)
        p.rot("Body", x=-14 * k)
        p.move("Body", y=-0.35 * k)
        for side, sx in (("L", -1), ("R", 1)):
            p.rot(f"Leg_{side}0_U", y=-sx * 55 * k, x=-25 * k)
            p.rot(f"Leg_{side}0_L", y=-sx * 35 * k)

    return [("Idle", 60, (0, 15, 30, 45, 60), idle), ("Walk", 24, tuple(range(0, 25, 3)), walk), ("Attack", 16, (0, 4, 8, 12, 16), attack)]


def gunner_turret(e):
    e.bone("Root", (0, 0, 0))
    e.bone("Turret", (0, 0, 1.55), "Root")
    e.bone("Barrel", (0, -0.3, 1.8), "Turret")
    e.cyl("Root", (0, 0, 0), (1.3, 1.1), 0.35, 8, base=True, key="hull")
    for i in range(3):
        a = i * 2 * PI / 3 + PI / 2
        e.limb("Root", (math.cos(a) * 0.3, math.sin(a) * 0.3, 1.2), (math.cos(a) * 1.45, math.sin(a) * 1.45, 0.1), 0.12, 0.09, 7, "armor")
        e.sphere("Root", (math.cos(a) * 1.5, math.sin(a) * 1.5, 0.07), (0.2, 0.2, 0.1), 6, "accent")
    e.cyl("Root", (0, 0, 0.35), (0.45, 0.4), 1.1, 8, base=True, key="hull")
    e.ring("Root", (0, 0, 1.45), 0.45, 0.07, 18, key="accent")
    e.cyl("Turret", (0, 0, 1.55), (0.7, 0.7), 0.3, 10, key="armor")
    e.box("Turret", (0, 0.05, 1.9), (1.0, 1.0, 0.55), key="hull")
    e.box("Turret", (0, 0.4, 2.25), (0.8, 0.5, 0.15), key="armor")
    e.sphere("Turret", (0, -0.5, 1.95), (0.2, 0.12, 0.2), 8, "eye")
    for sx in (-1, 1):
        e.box("Turret", (sx * 0.58, 0.1, 1.9), (0.18, 0.7, 0.45), key="armor")
        e.cyl("Barrel", (sx * 0.28, -0.95, 1.82), (0.1, 0.1), 1.3, 8, rot=(PI / 2, 0, 0), key="hull")
        e.cyl("Barrel", (sx * 0.28, -1.65, 1.82), (0.15, 0.15), 0.3, 8, rot=(PI / 2, 0, 0), key="accent")
    e.sphere("Turret", (0, 0.6, 1.85), (0.2, 0.1, 0.2), 8, "glow")

    def idle(p, f):
        p.rot("Turret", z=26 * sin2(f, 90))
        p.rot("Barrel", x=2 * sin2(f, 45))

    def attack(p, f):
        k = max(0.0, 1 - f / 9.0) if f < 9 else max(0.0, 1 - (f - 9) / 9.0)
        p.move("Barrel", y=0.35 * k)
        p.rot("Barrel", x=-5 * k)
        p.move("Turret", y=0.12 * k)

    return [("Idle", 90, (0, 15, 30, 45, 60, 75, 90), idle), ("Attack", 18, (0, 2, 4, 9, 11, 13, 18), attack)]


def bulwark_walker(e):
    e.bone("Root", (0, 0, 0))
    e.bone("Body", (0, 0, 1.4), "Root")
    e.bone("Shield", (0, -1.25, 1.6), "Body")
    e.box("Body", (0, 0.1, 1.6), (2.0, 2.3, 1.1), key="hull")
    e.box("Body", (0, 0.1, 2.25), (1.6, 1.9, 0.25), key="armor")
    e.box("Body", (0, 1.25, 1.6), (1.2, 0.35, 0.8), key="armor")
    e.sphere("Body", (0, 1.45, 1.6), (0.3, 0.1, 0.3), 8, "glow")
    e.box("Body", (0, -1.15, 2.05), (0.7, 0.45, 0.4), key="hull")
    e.sphere("Body", (0, -1.4, 2.08), (0.3, 0.08, 0.1), 8, "eye")
    # 大盾 (正面)
    e.box("Shield", (0, -1.55, 1.7), (2.4, 0.3, 2.0), key="armor")
    e.box("Shield", (0, -1.72, 1.7), (1.9, 0.12, 1.5), key="hull")
    e.ring("Shield", (0, -1.8, 1.75), 0.55, 0.06, 18, rot=(PI / 2, 0, 0), key="accent")
    for sx in (-1, 1):
        e.box("Shield", (sx * 0.85, -1.8, 2.5), (0.5, 0.1, 0.1), key="accent")
        e.box("Shield", (sx * 0.85, -1.8, 0.95), (0.5, 0.1, 0.1), key="accent")
    legs = []
    for side, sx in (("L", -1), ("R", 1)):
        for i, y in enumerate((-0.7, 0.8)):
            u, l = f"Leg_{side}{i}_U", f"Leg_{side}{i}_L"
            hip, knee, foot = (sx * 0.95, y, 1.4), (sx * 1.4, y, 0.8), (sx * 1.45, y - 0.1, 0.0)
            e.bone(u, hip, "Body")
            e.bone(l, knee, u)
            e.limb(u, hip, knee, 0.2, 0.17, 7, "hull")
            e.sphere(u, knee, (0.22, 0.22, 0.22), 7, "armor")
            e.limb(l, knee, foot, 0.17, 0.1, 7, "hull")
            e.box(l, (foot[0], foot[1], 0.07), (0.55, 0.65, 0.14), key="armor")
            legs.append((sx, i, u, l))

    def idle(p, f):
        p.move("Body", z=0.025 * sin2(f, 60))
        p.rot("Shield", x=2 * sin2(f, 60))

    def walk(p, f):
        t = f / 36
        for sx, i, u, l in legs:
            ph = t + (0.5 if (i % 2) != (sx > 0) else 0.0)
            w = math.sin(2 * PI * ph)
            up = max(0.0, w)
            p.rot(u, x=-18 * w)
            p.rot(l, x=22 * up)
        p.move("Body", z=0.04 * abs(sin2(f, 18)))
        p.rot("Body", y=2 * sin2(f, 36))

    def attack(p, f):
        k = math.sin(PI * f / 20)
        p.rot("Body", x=-10 * k)
        p.move("Body", y=-0.6 * k)
        p.rot("Shield", x=-35 * k)

    return [("Idle", 60, (0, 15, 30, 45, 60), idle), ("Walk", 36, tuple(range(0, 37, 4)), walk), ("Attack", 20, (0, 5, 10, 15, 20), attack)]


def jelly_drone(e):
    e.bone("Root", (0, 0, 2.2))
    e.bone("Bell", (0, 0, 2.2), "Root")
    n_t = 8
    e.sphere("Bell", (0, 0, 2.2), (1.0, 1.0, 0.7), 14, "glass")
    e.ring("Bell", (0, 0, 2.0), 1.0, 0.05, 28, key="armor")
    e.sphere("Bell", (0, 0, 2.15), (0.34, 0.34, 0.3), 10, "glow")
    for i in range(6):
        a = i * PI / 3
        e.limb("Bell", (math.cos(a) * 0.4, math.sin(a) * 0.4, 2.5), (math.cos(a) * 0.15, math.sin(a) * 0.15, 2.88), 0.035, key="armor")
    e.sphere("Bell", (0, 0, 2.9), (0.1, 0.1, 0.1), 6, "accent")
    chains = []
    for i in range(n_t):
        a = i * 2 * PI / n_t
        x, y = math.cos(a) * 0.8, math.sin(a) * 0.8
        names = []
        prev = "Bell"
        for s in range(3):
            nm = f"T{i}_{s}"
            e.bone(nm, (x, y, 2.0 - s * 0.55), prev)
            e.limb(nm, (x, y, 2.0 - s * 0.55), (x, y, 2.0 - (s + 1) * 0.55), 0.05 - s * 0.01, 0.045 - s * 0.01, 5, "hull")
            e.sphere(nm, (x, y, 2.0 - (s + 1) * 0.55), (0.055, 0.055, 0.055), 5, "glow")
            names.append(nm)
            prev = nm
        chains.append((a, names))

    def idle(p, f):
        k = sin2(f, 40)
        p.move("Root", z=0.12 * k)
        p.scale("Bell", sx=1 + 0.05 * k, sy=1 + 0.05 * k, sz=1 - 0.07 * k)
        for a, names in chains:
            for s, nm in enumerate(names):
                ph = sin2(f - s * 5, 40)
                p.rot(nm, x=math.cos(a) * 10 * ph, y=-math.sin(a) * 10 * ph)

    def attack(p, f):
        k = math.sin(PI * f / 20)
        p.scale("Bell", sx=1 + 0.25 * k, sy=1 + 0.25 * k, sz=1 - 0.18 * k)
        for a, names in chains:
            for s, nm in enumerate(names):
                p.rot(nm, x=math.cos(a) * 32 * k, y=-math.sin(a) * 32 * k)
        p.move("Root", z=-0.3 * k)

    return [("Idle", 40, (0, 8, 16, 24, 32, 40), idle), ("Attack", 20, (0, 5, 10, 15, 20), attack)]


def eel_bot(e):
    n = 8
    seg_len = 0.9
    e.bone("Root", (0, 0, 1.0))
    prev = "Root"
    segs = []
    for i in range(n):
        y = i * seg_len
        nm = f"Seg{i}"
        e.bone(nm, (0, y, 1.0), prev)
        r = 0.42 - i * 0.042
        e.sphere(nm, (0, y + seg_len / 2, 1.0), (r, seg_len * 0.62, r), 10, "hull" if i % 2 == 0 else "armor")
        e.ring(nm, (0, y + 0.1, 1.0), r * 1.0, 0.04, 14, rot=(PI / 2, 0, 0), key="accent")
        e.box(nm, (0, y + seg_len / 2, 1.0 + r), (0.05, seg_len * 0.7, 0.18), key="accent")
        segs.append(nm)
        prev = nm
    e.bone("Head", (0, 0, 1.0), "Root")
    e.bone("Jaw", (0, -0.35, 0.8), "Head")
    e.sphere("Head", (0, -0.55, 1.05), (0.5, 0.75, 0.42), 12, "armor")
    e.sphere("Head", (0, -1.0, 1.05), (0.34, 0.35, 0.3), 10, "armor")
    for sx in (-1, 1):
        e.sphere("Head", (sx * 0.3, -0.95, 1.25), (0.1, 0.12, 0.1), 6, "eye")
    e.box("Jaw", (0, -0.75, 0.72), (0.5, 1.0, 0.14), key="hull")
    for i in range(5):
        e.cone("Jaw", (-0.2 + i * 0.1, -1.0, 0.8), r=0.04, h=0.16, seg=4, key="armor", base=True)
        e.cone("Head", (-0.2 + i * 0.1, -0.95, 0.9), r=0.04, h=0.16, seg=4, rot=(PI, 0, 0), key="armor", base=True)
    e.cone(segs[-1], (0, n * seg_len - 0.05, 1.0), r=0.12, h=0.7, seg=6, rot=(-PI / 2, 0, 0), key="glow")

    def wave(p, f, amp, period, lag):
        for i, nm in enumerate(segs):
            p.rot(nm, z=amp * (0.5 + i * 0.12) * sin2(f - i * lag, period))
        p.rot("Head", z=amp * 0.5 * sin2(f + lag, period))

    def idle(p, f):
        wave(p, f, 7, 60, 6)
        p.move("Root", z=0.05 * sin2(f, 60))

    def swim(p, f):
        wave(p, f, 14, 24, 2.4)
        p.move("Root", z=0.03 * sin2(f, 24))

    def attack(p, f):
        k = math.sin(PI * f / 18)
        for i, nm in enumerate(segs):
            p.rot(nm, z=(28 - i * 3) * k * (1 if i % 2 == 0 else -1) * 0.8)
        p.rot("Jaw", x=38 * k)
        p.move("Root", y=-0.9 * k)
        p.rot("Head", x=-8 * k)

    return [("Idle", 60, (0, 10, 20, 30, 40, 50, 60), idle), ("Swim", 24, tuple(range(0, 25, 3)), swim), ("Attack", 18, (0, 3, 6, 9, 12, 15, 18), attack)]


def urchin_mine(e):
    e.bone("Root", (0, 0, 1.0))
    e.bone("Core", (0, 0, 1.0), "Root")
    e.bone("Spikes", (0, 0, 1.0), "Root")
    e.sphere("Core", (0, 0, 1.0), (0.62, 0.62, 0.62), 12, "hull")
    e.ring("Core", (0, 0, 1.0), 0.64, 0.05, 24, key="armor")
    e.ring("Core", (0, 0, 1.0), 0.64, 0.05, 24, rot=(PI / 2, 0, 0), key="armor")
    e.sphere("Core", (0, -0.5, 1.05), (0.2, 0.15, 0.2), 8, "eye")
    e.sphere("Core", (0, 0, 1.0), (0.3, 0.3, 0.3), 8, "glow")
    dirs = []
    golden = PI * (3 - math.sqrt(5))
    for i in range(18):
        yy = 1 - 2 * (i + 0.5) / 18
        rr = math.sqrt(1 - yy * yy)
        th = golden * i
        d = Vector((math.cos(th) * rr, math.sin(th) * rr, yy))
        dirs.append(d)
        e.limb("Spikes", Vector((0, 0, 1.0)) + d * 0.55, Vector((0, 0, 1.0)) + d * 1.15, 0.09, 0.0, 6, "accent")
        e.sphere("Spikes", Vector((0, 0, 1.0)) + d * 0.6, (0.1, 0.1, 0.1), 5, "armor")

    def idle(p, f):
        k = 0.5 + 0.5 * sin2(f, 40)
        p.scale("Core", 1 + 0.08 * k)
        p.move("Root", z=0.08 * sin2(f, 80))
        p.rot("Spikes", z=6 * sin2(f, 80))

    def attack(p, f):
        k = math.sin(PI * f / 14)
        p.scale("Spikes", 1 + 0.5 * k)
        p.scale("Core", 1 + 0.2 * k)
        p.rot("Spikes", z=40 * k)

    return [("Idle", 40, (0, 10, 20, 30, 40), idle), ("Attack", 14, (0, 3, 7, 10, 14), attack)]


def angler_lurebot(e):
    e.bone("Root", (0, 0, 1.4))
    e.bone("Body", (0, 0, 1.4), "Root")
    e.bone("Jaw", (0, -1.0, 1.15), "Body")
    e.bone("Lure0", (0, -0.2, 2.15), "Body")
    e.bone("Lure1", (0, -1.2, 2.9), "Lure0")
    e.bone("Tail", (0, 1.3, 1.4), "Body")
    e.bone("FinL", (-0.9, 0.0, 1.2), "Body")
    e.bone("FinR", (0.9, 0.0, 1.2), "Body")
    e.sphere("Body", (0, 0, 1.45), (1.15, 1.45, 1.0), 14, "hull")
    e.sphere("Body", (0, -0.2, 1.95), (0.85, 1.0, 0.4), 10, "armor")
    for i in range(4):
        e.ring("Body", (0, -0.5 + i * 0.5, 1.45), 0.92 - abs(i - 1.2) * 0.05, 0.04, 20, rot=(PI / 2, 0, 0), key="accent")
    for sx in (-1, 1):
        e.sphere("Body", (sx * 0.55, -1.15, 1.9), (0.16, 0.12, 0.16), 6, "eye")
    # 顎と歯
    e.box("Jaw", (0, -1.25, 0.95), (1.6, 1.3, 0.22), key="hull")
    for i in range(7):
        x = -0.65 + i * 0.22
        e.cone("Jaw", (x, -1.8, 1.05), r=0.07, h=0.34, seg=5, key="armor", base=True)
        e.cone("Body", (x, -1.7, 1.25), r=0.07, h=0.34, seg=5, rot=(PI, 0, 0), key="armor", base=True)
    # 提灯
    e.limb("Lure0", (0, -0.2, 2.15), (0, -1.2, 2.9), 0.05, 0.04, 6, "armor")
    e.limb("Lure1", (0, -1.2, 2.9), (0, -1.9, 2.55), 0.04, 0.03, 6, "armor")
    e.sphere("Lure1", (0, -1.95, 2.5), (0.22, 0.22, 0.22), 8, "glow")
    # ひれと尾
    for sx, nm in ((-1, "FinL"), (1, "FinR")):
        e.box(nm, (sx * 1.35, 0.0, 1.2), (0.9, 0.9, 0.08), rot=(0, 0, sx * 0.5), key="armor")
    e.box("Tail", (0, 1.9, 1.4), (0.1, 1.0, 1.1), key="armor")
    e.box("Tail", (0, 2.3, 1.4), (0.1, 0.7, 1.7), rot=(0, 0, 0), key="accent")

    def idle(p, f):
        p.move("Root", z=0.1 * sin2(f, 60))
        p.rot("Lure0", x=10 * sin2(f, 40))
        p.rot("Lure1", x=18 * sin2(f - 5, 40))
        p.rot("Tail", z=14 * sin2(f, 30))
        p.rot("FinL", y=-12 * sin2(f, 30))
        p.rot("FinR", y=12 * sin2(f, 30))

    def attack(p, f):
        k = math.sin(PI * f / 14)
        p.rot("Jaw", x=42 * k)
        p.move("Root", y=-0.8 * k)
        p.rot("Lure0", x=-25 * k)
        p.rot("Tail", z=20 * k)

    return [("Idle", 60, (0, 10, 20, 30, 40, 50, 60), idle), ("Attack", 14, (0, 3, 5, 8, 11, 14), attack)]


def squid_lancer(e):
    e.bone("Root", (0, 0, 2.0))
    e.bone("Mantle", (0, 0, 2.0), "Root")
    e.bone("Head", (0, -0.6, 2.0), "Mantle")
    e.cone("Mantle", (0, 1.0, 2.0), r=0.8, h=2.4, seg=10, rot=(PI / 2, 0, 0), key="hull")
    e.sphere("Mantle", (0, 0.2, 2.0), (0.8, 0.9, 0.8), 12, "armor")
    for sx in (-1, 1):
        e.box("Mantle", (sx * 0.75, 1.6, 2.0), (0.9, 1.1, 0.07), rot=(0, 0, sx * 0.25), key="armor")
        e.sphere("Head", (sx * 0.5, -0.8, 2.15), (0.2, 0.15, 0.2), 8, "eye")
    e.sphere("Head", (0, -0.75, 2.0), (0.62, 0.55, 0.6), 10, "hull")
    e.ring("Mantle", (0, 0.5, 2.0), 0.8, 0.05, 20, rot=(PI / 2, 0, 0), key="accent")
    e.sphere("Mantle", (0, 1.2, 2.5), (0.12, 0.35, 0.1), 6, "glow")
    arms = []
    for i in range(8):
        a = i * 2 * PI / 8
        x, z = math.cos(a) * 0.4, 2.0 + math.sin(a) * 0.4
        names = []
        prev = "Head"
        for s in range(2):
            nm = f"Arm{i}_{s}"
            p0 = (x * (1 + s * 0.5), -1.05 - s * 0.75, z + (math.sin(a) * 0.1 * s) - s * 0.15)
            p1 = (x * (1.6 + s * 0.5), -1.8 - s * 0.75, z + (math.sin(a) * 0.15 * (s + 1)) - (s + 1) * 0.15)
            e.bone(nm, p0, prev)
            e.limb(nm, p0, p1, 0.1 - s * 0.03, 0.08 - s * 0.03, 6, "hull")
            names.append(nm)
            prev = nm
        arms.append((a, names))
    spears = []
    for sx in (-1, 1):
        nm = "Spear" + ("L" if sx < 0 else "R")
        e.bone(nm, (sx * 0.3, -1.0, 2.3), "Head")
        e.limb(nm, (sx * 0.3, -1.0, 2.3), (sx * 0.5, -3.6, 2.5), 0.06, 0.05, 6, "armor")
        e.cone(nm, (sx * 0.5, -3.9, 2.5), r=0.14, h=0.7, seg=6, rot=(PI / 2, 0, 0), key="accent")
        spears.append((sx, nm))

    def idle(p, f):
        p.move("Root", z=0.15 * sin2(f, 60))
        p.rot("Mantle", x=2 * sin2(f, 60))
        for a, names in arms:
            for s, nm in enumerate(names):
                p.rot(nm, x=9 * math.sin(2 * PI * (f - s * 6 - a * 3) / 40))
        for sx, nm in spears:
            p.rot(nm, z=sx * 3 * sin2(f, 60))

    def attack(p, f):
        k = math.sin(PI * f / 16)
        p.move("Root", y=-1.0 * k)
        p.rot("Mantle", x=-12 * k)
        for sx, nm in spears:
            p.move(nm, y=-1.1 * k)
            p.rot(nm, x=-4 * k)
        for a, names in arms:
            for nm in names:
                p.rot(nm, x=-14 * k)

    return [("Idle", 60, (0, 10, 20, 30, 40, 50, 60), idle), ("Attack", 16, (0, 4, 8, 12, 16), attack)]


def ruin_sentinel(e):
    e.bone("Root", (0, 0, 0))
    e.bone("Hips", (0, 0, 2.0), "Root")
    e.bone("Torso", (0, 0, 2.4), "Hips")
    e.bone("Head", (0, -0.1, 4.0), "Torso")
    e.box("Hips", (0, 0, 2.0), (1.7, 1.1, 0.7), key="stone")
    e.box("Torso", (0, 0, 3.2), (2.3, 1.4, 1.7), key="stone")
    e.box("Torso", (0, -0.73, 3.2), (1.2, 0.08, 1.1), key="rune")
    e.ring("Torso", (0, -0.78, 3.3), 0.42, 0.045, 18, rot=(PI / 2, 0, 0), key="rune")
    e.box("Head", (0, -0.1, 4.25), (0.95, 0.9, 0.85), key="stone")
    e.box("Head", (0, -0.58, 4.3), (0.7, 0.06, 0.12), key="eye")
    e.cone("Head", (0, -0.1, 4.7), r=0.3, h=0.55, seg=4, key="stone", base=True)
    for side, sx in (("L", -1), ("R", 1)):
        s_nm, e_nm, h_nm = f"Shoulder_{side}", f"Elbow_{side}", f"Hand_{side}"
        e.bone(s_nm, (sx * 1.35, 0, 3.7), "Torso")
        e.bone(e_nm, (sx * 1.65, 0, 2.7), s_nm)
        e.bone(h_nm, (sx * 1.7, 0, 1.7), e_nm)
        e.sphere(s_nm, (sx * 1.4, 0, 3.7), (0.55, 0.55, 0.55), 8, "stone")
        e.limb(s_nm, (sx * 1.5, 0, 3.6), (sx * 1.65, 0, 2.7), 0.38, 0.32, 8, "stone")
        e.sphere(e_nm, (sx * 1.65, 0, 2.7), (0.38, 0.38, 0.38), 7, "stone")
        e.limb(e_nm, (sx * 1.65, 0, 2.7), (sx * 1.7, 0, 1.8), 0.34, 0.3, 8, "stone")
        e.ring(e_nm, (sx * 1.68, 0, 2.3), 0.35, 0.04, 14, key="rune")
        e.box(h_nm, (sx * 1.72, 0, 1.45), (0.85, 0.9, 0.8), key="stone")
        e.cone(h_nm, (sx * 1.72, -0.1, 1.05), r=0.28, h=0.4, seg=5, rot=(PI, 0, 0), key="stone")
    for side, sx in (("L", -1), ("R", 1)):
        t_nm, k_nm = f"Thigh_{side}", f"Shin_{side}"
        e.bone(t_nm, (sx * 0.6, 0, 1.9), "Hips")
        e.bone(k_nm, (sx * 0.6, 0, 1.0), t_nm)
        e.limb(t_nm, (sx * 0.6, 0, 1.9), (sx * 0.6, 0, 1.0), 0.48, 0.4, 8, "stone")
        e.limb(k_nm, (sx * 0.6, 0, 1.0), (sx * 0.6, 0, 0.2), 0.4, 0.46, 8, "stone")
        e.box(k_nm, (sx * 0.6, -0.2, 0.1), (0.9, 1.3, 0.2), key="stone")
        e.ring(k_nm, (sx * 0.6, 0, 0.7), 0.42, 0.04, 14, key="rune")

    def idle(p, f):
        k = sin2(f, 80)
        p.move("Hips", z=0.04 * k)
        p.rot("Torso", x=2 * k)
        p.rot("Head", x=-2 * k, z=4 * sin2(f, 120))
        for side, sx in (("L", -1), ("R", 1)):
            p.rot(f"Shoulder_{side}", z=sx * 3 * k)

    def walk(p, f):
        t = f / 32
        for side, sx in (("L", -1), ("R", 1)):
            ph = t + (0.5 if sx > 0 else 0.0)
            w = math.sin(2 * PI * ph)
            p.rot(f"Thigh_{side}", x=-22 * w)
            p.rot(f"Shin_{side}", x=26 * max(0.0, w))
            p.rot(f"Shoulder_{side}", x=18 * w)
        p.move("Hips", z=0.07 * abs(sin2(f, 16)))
        p.rot("Torso", z=4 * sin2(f, 32))

    def attack(p, f):
        k = math.sin(PI * f / 24)
        up = max(0.0, math.sin(PI * min(f, 12) / 12)) * (1 if f <= 12 else max(0.0, 1 - (f - 12) / 4))
        for side in ("L", "R"):
            p.rot(f"Shoulder_{side}", x=-150 * up + 70 * (k if f > 12 else 0))
            p.rot(f"Elbow_{side}", x=-30 * up)
        p.rot("Torso", x=-12 * up + 16 * (k if f > 12 else 0))
        p.move("Hips", z=-0.15 * (k if f > 12 else 0))

    return [("Idle", 80, (0, 20, 40, 60, 80), idle), ("Walk", 32, tuple(range(0, 33, 4)), walk), ("Attack", 24, (0, 4, 8, 12, 14, 16, 20, 24), attack)]


def stone_crab_guardian(e):
    e.bone("Root", (0, 0, 0))
    e.bone("Body", (0, 0, 1.4), "Root")
    e.sphere("Body", (0, 0, 1.55), (1.7, 1.45, 0.95), 14, "stone")
    e.sphere("Body", (0, -0.1, 2.25), (1.0, 0.85, 0.3), 10, "stone")
    e.ring("Body", (0, 0, 1.55), 1.62, 0.06, 28, key="rune")
    for i in range(5):
        a = -PI / 2 + (i - 2) * 0.5
        e.cone("Body", (math.cos(a) * 1.35, math.sin(a) * 1.15, 2.0), r=0.14, h=0.5, seg=5, key="stone", base=True)
    for sx in (-1, 1):
        e.cyl("Body", (sx * 0.55, -1.2, 2.1), (0.07, 0.07), 0.8, 6, key="stone", base=True)
        e.sphere("Body", (sx * 0.55, -1.2, 2.95), (0.2, 0.2, 0.2), 8, "eye")
    e.box("Body", (0, -1.42, 1.75), (1.1, 0.1, 0.1), key="rune")
    arms = []
    for side, sx in (("L", -1), ("R", 1)):
        a_nm, c_nm, p0_nm, p1_nm = f"Arm_{side}", f"Claw_{side}", f"PincerA_{side}", f"PincerB_{side}"
        e.bone(a_nm, (sx * 1.5, -0.5, 1.7), "Body")
        e.bone(c_nm, (sx * 2.1, -1.8, 1.7), a_nm)
        e.bone(p0_nm, (sx * 1.85, -2.5, 1.7), c_nm)
        e.bone(p1_nm, (sx * 2.45, -2.5, 1.7), c_nm)
        e.limb(a_nm, (sx * 1.4, -0.5, 1.7), (sx * 2.1, -1.8, 1.7), 0.34, 0.3, 8, "stone")
        e.sphere(c_nm, (sx * 2.2, -2.1, 1.7), (0.8, 0.95, 0.65), 10, "stone")
        e.cone(p0_nm, (sx * 1.85, -3.3, 1.7), r=0.38, h=1.5, seg=6, rot=(PI / 2, 0, 0), key="stone")
        e.cone(p1_nm, (sx * 2.55, -3.2, 1.7), r=0.34, h=1.4, seg=6, rot=(PI / 2, 0, 0), key="stone")
        e.ring(c_nm, (sx * 2.2, -2.1, 2.3), 0.35, 0.04, 12, key="rune")
        arms.append((sx, a_nm, c_nm, p0_nm, p1_nm))
    legs = []
    for side, sx in (("L", -1), ("R", 1)):
        for i, y in enumerate((-0.5, 0.2, 0.9)):
            u, l = f"Leg_{side}{i}_U", f"Leg_{side}{i}_L"
            hip, knee, foot = (sx * 1.4, y, 1.5), (sx * 2.2, y + 0.1, 1.8), (sx * 2.7, y + 0.2, 0.0)
            e.bone(u, hip, "Body")
            e.bone(l, knee, u)
            e.limb(u, hip, knee, 0.2, 0.17, 7, "stone")
            e.limb(l, knee, foot, 0.17, 0.08, 7, "stone")
            legs.append((sx, i, u, l))

    def idle(p, f):
        p.move("Body", z=0.03 * sin2(f, 60))
        for sx, a, c, p0, p1 in arms:
            p.rot(a, z=sx * 4 * sin2(f, 60))
            p.rot(p0, z=sx * (5 + 5 * sin2(f, 40)))
            p.rot(p1, z=-sx * (5 + 5 * sin2(f, 40)))

    def walk(p, f):
        t = f / 28
        for sx, i, u, l in legs:
            ph = t + (0.5 if (i % 2) != (sx > 0) else 0.0)
            w = math.sin(2 * PI * ph)
            up = max(0.0, w)
            p.rot(u, y=-sx * 22 * up, z=sx * 10 * w)
            p.rot(l, y=-sx * 14 * up)
        p.move("Body", z=0.05 * abs(sin2(f, 14)))
        p.rot("Body", y=2 * sin2(f, 14))

    def attack(p, f):
        k = math.sin(PI * f / 16)
        snap = max(0.0, math.sin(PI * max(0.0, f - 6) / 8)) if f >= 6 else 0.0
        p.move("Body", y=-0.5 * k)
        p.rot("Body", x=-8 * k)
        for sx, a, c, p0, p1 in arms:
            p.rot(a, z=-sx * 14 * k)
            p.rot(p0, z=sx * (28 - 40 * snap))
            p.rot(p1, z=-sx * (28 - 40 * snap))

    return [("Idle", 60, (0, 15, 30, 45, 60), idle), ("Walk", 28, tuple(range(0, 29, 4)), walk), ("Attack", 16, (0, 4, 6, 8, 10, 12, 16), attack)]


def hammerhead_sweeper(e):
    n = 6
    seg = 1.0
    e.bone("Root", (0, 0, 1.6))
    e.bone("Body", (0, 0, 1.6), "Root")
    e.bone("Head", (0, -1.2, 1.6), "Body")
    e.sphere("Body", (0, 0.2, 1.6), (0.95, 1.7, 0.85), 14, "hull")
    e.sphere("Body", (0, 0.1, 2.15), (0.6, 1.3, 0.25), 10, "armor")
    for i in range(3):
        e.ring("Body", (0, -0.3 + i * 0.6, 1.6), 0.8, 0.04, 18, rot=(PI / 2, 0, 0), key="accent")
    e.box("Body", (0, 0.2, 2.5), (0.1, 1.2, 0.8), rot=(0.4, 0, 0), key="armor")
    for sx in (-1, 1):
        e.box("Body", (sx * 1.2, -0.2, 1.2), (1.5, 0.9, 0.08), rot=(0.25 * sx, 0, sx * 0.5), key="armor")
    # ハンマー状の頭
    e.box("Head", (0, -1.75, 1.6), (3.6, 0.8, 0.45), key="armor")
    e.box("Head", (0, -1.4, 1.6), (1.2, 0.9, 0.6), key="hull")
    for sx in (-1, 1):
        e.sphere("Head", (sx * 1.65, -2.05, 1.62), (0.17, 0.12, 0.17), 8, "eye")
        e.cone("Head", (sx * 1.8, -1.75, 1.6), r=0.2, h=0.5, seg=5, rot=(0, sx * PI / 2, 0), key="accent")
    e.box("Head", (0, -2.18, 1.6), (2.6, 0.06, 0.1), key="glow")
    prev = "Body"
    segs = []
    for i in range(n):
        y = 1.6 + i * seg
        nm = f"Tail{i}"
        e.bone(nm, (0, y - 0.3, 1.6), prev)
        r = 0.62 - i * 0.085
        e.sphere(nm, (0, y + 0.2, 1.6), (r, seg * 0.62, r), 10, "hull" if i % 2 == 0 else "armor")
        segs.append(nm)
        prev = nm
    e.box(segs[-1], (0, 1.6 + n * seg + 0.1, 1.6), (0.1, 0.9, 1.6), key="accent")

    def idle(p, f):
        p.move("Root", z=0.12 * sin2(f, 60))
        for i, nm in enumerate(segs):
            p.rot(nm, z=(5 + i * 2.5) * sin2(f - i * 5, 60))
        p.rot("Head", z=-4 * sin2(f, 60))

    def swim(p, f):
        for i, nm in enumerate(segs):
            p.rot(nm, z=(8 + i * 4) * sin2(f - i * 2.4, 24))
        p.rot("Head", z=-9 * sin2(f, 24))
        p.rot("Body", z=3 * sin2(f, 24))

    def attack(p, f):
        k = math.sin(PI * f / 18)
        p.rot("Head", z=70 * k * (1 if f < 9 else -1) * (1 if f < 9 else 0.6))
        p.rot("Body", z=22 * k)
        p.move("Root", y=-0.6 * k)
        for i, nm in enumerate(segs):
            p.rot(nm, z=-12 * k)

    return [("Idle", 60, (0, 10, 20, 30, 40, 50, 60), idle), ("Swim", 24, tuple(range(0, 25, 3)), swim), ("Attack", 18, (0, 3, 6, 9, 12, 15, 18), attack)]


MODELS = [
    ("enemy_scout_drone", scout_drone),
    ("enemy_crawler_bot", crawler_bot),
    ("enemy_gunner_turret", gunner_turret),
    ("enemy_bulwark_walker", bulwark_walker),
    ("enemy_jelly_drone", jelly_drone),
    ("enemy_eel_bot", eel_bot),
    ("enemy_urchin_mine", urchin_mine),
    ("enemy_angler_lurebot", angler_lurebot),
    ("enemy_squid_lancer", squid_lancer),
    ("enemy_ruin_sentinel", ruin_sentinel),
    ("enemy_stone_crab_guardian", stone_crab_guardian),
    ("enemy_hammerhead_sweeper", hammerhead_sweeper),
]


# ---------------------------------------------------------------- 組み立て (アーマチュア・パーツの固定・アニメ)
def jitter(bm, seed, amp):
    rnd = random.Random(seed)
    seen = {}
    for v in bm.verts:
        k = (round(v.co.x, 3), round(v.co.y, 3), round(v.co.z, 3))
        if k not in seen:
            seen[k] = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * amp
        v.co += seen[k]


def assemble(name, parts, anims, mats):
    scn = bpy.context.scene
    scn.render.fps = FPS
    data = bpy.data.armatures.new(name + "_Rig")
    data.display_type = "STICK"
    arm = bpy.data.objects.new(name + "_Armature", data)
    scn.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    arm.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    for bn in parts.order:
        pivot, _ = parts.bones[bn]
        eb = data.edit_bones.new(bn)
        eb.head = pivot
        eb.tail = pivot + Vector((0, 0.25, 0))  # +Y に揃える (骨の軸 = アーマチュアの軸)
    for bn in parts.order:
        par = parts.bones[bn][1]
        if par:
            data.edit_bones[bn].parent = data.edit_bones[par]
    bpy.ops.object.mode_set(mode="OBJECT")

    objs = []
    for (bone, key), bm in parts.bm.items():
        if not bm.verts:
            bm.free()
            continue
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        if key in ("hull", "armor", "stone"):
            jitter(bm, hash((name, bone, key)) % 100000, 0.012)
        mesh = bpy.data.meshes.new(f"{name}_{bone}_{key}")
        bm.to_mesh(mesh)
        bm.free()
        mesh.materials.append(mats[key])
        for p in mesh.polygons:
            p.use_smooth = False
        o = bpy.data.objects.new(f"{bone}_{key}", mesh)
        scn.collection.objects.link(o)
        b = data.bones[bone]
        o.parent = arm
        o.parent_type = "BONE"
        o.parent_bone = bone
        o.matrix_parent_inverse = (arm.matrix_world @ b.matrix_local @ Matrix.Translation((0, b.length, 0))).inverted()
        objs.append(o)

    p = Poser(arm)
    arm.animation_data_create()
    for clip, last, keys, fn in anims:
        act = bpy.data.actions.new(clip)
        act.use_fake_user = True
        arm.animation_data.action = act
        for f in keys:
            fn(p, f)
            p.key(f)
        act.frame_range = (0, last)
    arm.animation_data.action = None
    for pb in arm.pose.bones:
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)
        pb.scale = (1, 1, 1)
    return arm, objs


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
    bg.inputs[0].default_value = (0.2, 0.28, 0.36, 1)
    bg.inputs[1].default_value = 1.0
    tmp = []
    for loc, e, sz in (((-4, -5, 6), 900, 6), ((6, -2, 3), 320, 6), ((0, 6, 4), 280, 6)):
        bpy.ops.object.light_add(type="AREA", location=(c.x + loc[0] * r * 0.5, c.y + loc[1] * r * 0.5, c.z + loc[2] * r * 0.5))
        L = bpy.context.object
        L.data.energy = e * r * r * 0.35
        L.data.size = sz * r * 0.5
        L.rotation_euler = (c - L.location).to_track_quat("-Z", "Y").to_euler()
        tmp.append(L)
    bpy.ops.object.camera_add(location=c + Vector((-0.8, -1.0, 0.45)).normalized() * r * 2.8)
    cam = bpy.context.object
    cam.data.lens = 50
    cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
    scn.camera = cam
    scn.render.filepath = path
    bpy.ops.render.render(write_still=True)
    for L in tmp + [cam]:
        bpy.data.objects.remove(L)


def clear_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for a in list(bpy.data.actions):
        bpy.data.actions.remove(a)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m)
    for a in list(bpy.data.armatures):
        bpy.data.armatures.remove(a)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    setup_render()
    mats = make_mats()
    done = []
    for mid, fn in MODELS:
        if ONLY and mid not in ONLY:
            continue
        clear_scene()
        parts = Parts()
        anims = fn(parts)
        arm, objs = assemble(mid, parts, anims, mats)
        bpy.ops.object.select_all(action="DESELECT")
        arm.select_set(True)
        for o in objs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = arm
        bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, mid + ".glb"), export_format="GLB", use_selection=True, export_yup=True,
                                  export_animations=True, export_animation_mode="ACTIONS", export_force_sampling=True, export_frame_range=False)
        render_thumb(objs, os.path.join(THUMBS, mid + ".png"))
        done.append(mid)
        print("built", mid, [a[0] for a in anims])
    print("OK", len(done))


main()
