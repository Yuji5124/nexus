"""DEEP-TRENCH ENEMIES: 深度3500m以降 (発光深海・沈没都市・深淵領域) の敵キャラ10体 (NEXUS オリジナル)。Blender (4.x/5.x) をヘッドレスで動かして、リグ付きの GLB とサムネイルを作る。

    blender -b -P scripts/deep-trench-enemies/build_trench_enemies.py -- <出力フォルダ> <サムネイルのフォルダ> [敵ID ...]

規約: deep-sea-enemies と同じ。1 unit = 1 m、原点は足元 (浮遊・遊泳する敵は基準の高さ)、glTF 出力後は Y が上、正面は +Z。
リグは 1 パーツ 1 骨の剛体 (スキニングなし)。全員 Idle、動く敵は Walk / Swim、攻撃のある敵は Attack。クリップ名は deep-sea-enemies と共通。
材質 (テクスチャなし): hull / armor / accent / eye / glow / stone / rune / glass に加えて、lume (紫の生物発光) / amber (琥珀色の灯り) / bone (骨色) / ghost (半透明の紫)
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
    "lume": ((0.78, 0.32, 1.0), 0.0, 0.4, 3.0),
    "amber": ((1.0, 0.62, 0.16), 0.0, 0.4, 3.2),
    "bone": ((0.78, 0.76, 0.68), 0.0, 0.8, None),
    "ghost": ((0.66, 0.5, 1.0), 0.0, 0.2, 0.9),
}


def make_mats():
    mats = {}
    for key, (rgb, metal, rough, emit) in MAT_DEF.items():
        m = bpy.data.materials.new("trench_" + key)
        m.use_nodes = True
        b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        b.inputs["Base Color"].default_value = (*rgb, 1)
        b.inputs["Metallic"].default_value = metal
        b.inputs["Roughness"].default_value = rough
        if emit:
            b.inputs["Base Color"].default_value = (rgb[0] * 0.25, rgb[1] * 0.25, rgb[2] * 0.25, 1)
            b.inputs["Emission Color"].default_value = (*rgb, 1)
            b.inputs["Emission Strength"].default_value = emit
        if key in ("glass", "ghost"):
            b.inputs["Alpha"].default_value = 0.45 if key == "glass" else 0.38
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


# ---------------------------------------------------------------- 敵 10 体 (3500m 以降)
# 各関数は Parts を作って、アニメの一覧 [(クリップ名, 最終フレーム, キーのフレーム, 姿勢の関数 fn(p, f))] を返す。

def lantern_swarm(e):
    e.bone("Root", (0, 0, 1.0))
    e.bone("Body", (0, 0, 1.0), "Root")
    e.bone("Halo", (0, 0, 1.0), "Body")
    e.sphere("Body", (0, 0, 1.0), (0.32, 0.32, 0.27), 12, "hull")
    e.sphere("Body", (0, 0, 0.9), (0.2, 0.2, 0.16), 10, "lume")
    e.sphere("Body", (0, -0.28, 1.04), (0.07, 0.07, 0.07), 6, "eye")
    for i in range(4):
        a = PI / 4 + i * PI / 2
        e.box("Body", (math.cos(a) * 0.36, math.sin(a) * 0.36, 1.02), (0.24, 0.05, 0.04), rot=(0, 0, a), key="armor")
    e.ring("Halo", (0, 0, 1.0), 0.58, 0.028, 24, key="amber")
    for i in range(3):
        a = i * 2 * PI / 3
        e.sphere("Halo", (math.cos(a) * 0.58, math.sin(a) * 0.58, 1.0), (0.07, 0.07, 0.07), 6, "amber")

    def idle(p, f):
        k = sin2(f, 60)
        p.move("Root", z=0.1 * k)
        p.rot("Halo", z=360.0 * f / 60)
        p.rot("Body", x=4 * k)

    def attack(p, f):
        k = math.sin(PI * f / 18)
        p.move("Root", y=-0.8 * k)
        p.scale("Body", s=1 + 0.18 * k)
        p.rot("Halo", z=360.0 * f / 18 * 1.5)
        p.scale("Halo", s=1 + 0.35 * k)

    return [("Idle", 60, tuple(range(0, 61, 10)), idle), ("Attack", 18, (0, 3, 6, 9, 12, 15, 18), attack)]


def viperfish_hunter(e):
    n = 4
    seg_len = 0.8
    e.bone("Root", (0, 0, 1.2))
    e.bone("Head", (0, 0, 1.2), "Root")
    e.bone("Jaw", (0, -0.35, 0.95), "Head")
    e.bone("Lure1", (0, -0.2, 1.55), "Head")
    e.bone("Lure2", (0, -0.7, 2.0), "Lure1")
    e.sphere("Head", (0, -0.55, 1.15), (0.62, 0.95, 0.46), 12, "armor")
    e.sphere("Head", (0, -0.4, 1.0), (0.5, 0.8, 0.3), 10, "hull")
    for sx in (-1, 1):
        e.sphere("Head", (sx * 0.4, -0.95, 1.3), (0.1, 0.1, 0.1), 6, "eye")
    e.box("Jaw", (0, -0.9, 0.77), (0.5, 1.3, 0.12), key="hull")
    for i in range(5):
        y = -0.5 - i * 0.22
        for sx in (-1, 1):
            e.cone("Jaw", (sx * 0.24, y, 0.82), r=0.045, h=0.32, seg=4, key="bone", base=True)
            e.cone("Head", (sx * 0.24, y - 0.04, 0.74), r=0.045, h=0.34, seg=4, rot=(PI, 0, 0), key="bone", base=True)
    e.limb("Lure1", (0, -0.2, 1.5), (0, -0.7, 2.0), 0.035, key="hull")
    e.limb("Lure2", (0, -0.7, 2.0), (0, -1.35, 1.85), 0.025, key="hull")
    e.sphere("Lure2", (0, -1.4, 1.8), (0.13, 0.13, 0.13), 8, "amber")
    segs = []
    prev = "Root"
    for i in range(n):
        y = i * seg_len
        nm = f"Seg{i}"
        e.bone(nm, (0, y, 1.2), prev)
        r = 0.55 - i * 0.1
        e.sphere(nm, (0, y + seg_len / 2, 1.2), (r, seg_len * 0.62, r * 0.85), 10, "hull" if i % 2 == 0 else "armor")
        e.box(nm, (0, y + seg_len / 2, 1.2 + r * 0.85), (0.05, seg_len * 0.8, 0.28 - i * 0.04), key="armor")
        for k in range(2):
            e.sphere(nm, (r * 0.78, y + 0.25 + k * 0.32, 1.12), (0.05, 0.05, 0.05), 5, "lume")
            e.sphere(nm, (-r * 0.78, y + 0.25 + k * 0.32, 1.12), (0.05, 0.05, 0.05), 5, "lume")
        segs.append(nm)
        prev = nm
    e.bone("Tail", (0, n * seg_len, 1.2), segs[-1])
    e.box("Tail", (0, n * seg_len + 0.35, 1.2), (0.05, 0.7, 0.9), key="accent")
    e.box("Tail", (0, n * seg_len + 0.15, 1.2), (0.05, 0.4, 0.45), rot=(0, 0, 0), key="armor")

    def wave(p, f, amp, period, lag):
        for i, nm in enumerate(segs):
            p.rot(nm, z=amp * (0.5 + i * 0.2) * sin2(f - i * lag, period))
        p.rot("Tail", z=amp * 1.2 * sin2(f - n * lag, period))
        p.rot("Head", z=-amp * 0.3 * sin2(f, period))

    def idle(p, f):
        wave(p, f, 6, 60, 6)
        p.rot("Lure1", x=8 * sin2(f, 60))
        p.rot("Lure2", x=14 * sin2(f - 8, 60))
        p.move("Root", z=0.05 * sin2(f, 60))

    def swim(p, f):
        wave(p, f, 12, 24, 2.4)
        p.rot("Lure2", x=12 * sin2(f - 4, 24))

    def attack(p, f):
        k = math.sin(PI * f / 18)
        p.rot("Jaw", x=42 * k)
        p.move("Root", y=-1.1 * k)
        p.rot("Head", x=-10 * k)
        for i, nm in enumerate(segs):
            p.rot(nm, z=14 * k * (1 if i % 2 == 0 else -1))

    return [("Idle", 60, (0, 10, 20, 30, 40, 50, 60), idle), ("Swim", 24, tuple(range(0, 25, 3)), swim), ("Attack", 18, (0, 3, 6, 9, 12, 15, 18), attack)]


def siphonophore_chain(e):
    n = 7
    e.bone("Root", (0, 0, 0.8))
    chain = []
    prev = "Root"
    for i in range(n):
        z = 0.8 + i * 0.75
        nm = f"Bell{i}"
        e.bone(nm, (0, 0, z), prev)
        rr = 0.42 - i * 0.03
        e.sphere(nm, (0, 0, z + 0.3), (rr, rr, rr * 0.8), 10, "glass")
        e.sphere(nm, (0, 0, z + 0.28), (rr * 0.45, rr * 0.45, rr * 0.4), 8, "lume")
        e.ring(nm, (0, 0, z + 0.04), rr * 0.92, 0.03, 18, key="armor")
        e.limb(nm, (0, 0, z + 0.3 + rr * 0.8), (0, 0, z + 0.75), 0.04, key="hull")
        for k in range(4):
            a = k * PI / 2 + i * 0.5
            e.limb(nm, (math.cos(a) * rr * 0.9, math.sin(a) * rr * 0.9, z + 0.05), (math.cos(a) * rr * 1.1, math.sin(a) * rr * 1.1, z - 0.42), 0.022, key="hull")
            e.sphere(nm, (math.cos(a) * rr * 1.1, math.sin(a) * rr * 1.1, z - 0.44), (0.045, 0.045, 0.045), 5, "amber")
        chain.append(nm)
        prev = nm
    e.sphere(chain[-1], (0, 0, 0.8 + n * 0.75 + 0.1), (0.14, 0.14, 0.14), 8, "amber")

    def idle(p, f):
        for i, nm in enumerate(chain):
            ph = sin2(f - i * 6, 80)
            p.rot(nm, x=7 * ph, y=5 * sin2(f - i * 6 + 20, 80))
            p.scale(nm, sx=1 + 0.05 * ph, sy=1 + 0.05 * ph, sz=1 - 0.07 * ph)
        p.move("Root", z=0.1 * sin2(f, 80))

    def attack(p, f):
        k = math.sin(PI * f / 24)
        for i, nm in enumerate(chain):
            p.rot(nm, x=26 * k * (1 if i % 2 == 0 else -1), y=14 * k)
            p.scale(nm, sx=1 + 0.3 * k, sy=1 + 0.3 * k, sz=1 - 0.2 * k)

    return [("Idle", 80, tuple(range(0, 81, 10)), idle), ("Attack", 24, (0, 4, 8, 12, 16, 20, 24), attack)]


def isopod_roller(e):
    e.bone("Root", (0, 0, 0.0))
    e.bone("Head", (0, 0, 0.0), "Root")
    e.sphere("Head", (0, -0.85, 0.5), (0.5, 0.42, 0.34), 10, "armor")
    for sx in (-1, 1):
        e.sphere("Head", (sx * 0.3, -1.12, 0.62), (0.09, 0.09, 0.09), 6, "eye")
        e.limb("Head", (sx * 0.12, -1.2, 0.5), (sx * 0.55, -1.9, 0.55), 0.02, key="bone")
    plates = []
    prev = "Root"
    for i in range(6):
        y = -0.5 + i * 0.5
        nm = f"Plate{i}"
        e.bone(nm, (0, y, 0.3), prev)
        r = 0.7 - abs(i - 2) * 0.09
        e.sphere(nm, (0, y + 0.25, 0.46), (r, 0.36, 0.42), 10, "armor" if i % 2 == 0 else "hull")
        e.ring(nm, (0, y + 0.02, 0.44), r * 0.98, 0.025, 14, rot=(PI / 2, 0, 0), key="bone")
        if i in (1, 3):
            e.sphere(nm, (0, y + 0.25, 0.86), (0.05, 0.05, 0.05), 5, "lume")
        for sx in (-1, 1):
            e.limb(nm, (sx * r * 0.85, y + 0.25, 0.3), (sx * (r + 0.28), y + 0.3, 0.0), 0.04, 0.025, 5, "bone")
        plates.append(nm)
        prev = nm
    e.cone(plates[-1], (0, 2.7, 0.4), r=0.25, h=0.5, seg=6, rot=(-PI / 2, 0, 0), key="armor")

    def walk(p, f):
        for i, nm in enumerate(plates):
            p.rot(nm, z=5 * sin2(f - i * 3, 24))
        p.move("Root", z=0.04 * abs(sin2(f, 24)))

    def idle(p, f):
        for i, nm in enumerate(plates):
            p.rot(nm, x=1.5 * sin2(f - i * 4, 60))
        p.rot("Head", x=3 * sin2(f, 60))

    def attack(p, f):
        k = math.sin(PI * f / 24)
        for nm in plates:
            p.rot(nm, x=26 * k)
        p.move("Root", y=-0.6 * k)
        p.rot("Head", x=-18 * k)

    return [("Idle", 60, (0, 15, 30, 45, 60), idle), ("Walk", 24, (0, 6, 12, 18, 24), walk), ("Attack", 24, (0, 4, 8, 12, 16, 20, 24), attack)]


def tubeworm_spitter(e):
    e.bone("Root", (0, 0, 0.0))
    e.cyl("Root", (0, 0, 0), (1.5, 1.1), 0.5, 9, key="stone", base=True)
    e.cyl("Root", (0.2, 0.1, 0.5), (1.0, 0.7), 0.35, 8, key="stone", base=True)
    rnd = random.Random(31)
    tubes = []
    for i in range(7):
        a = i * 2 * PI / 7 + 0.3
        rad = 0.0 if i == 0 else 0.7
        x, y = math.cos(a) * rad, math.sin(a) * rad
        h = 3.2 if i == 0 else 1.7 + rnd.uniform(0, 1.0)
        nm = f"Tube{i}"
        e.bone(nm, (x, y, 0.6), "Root")
        e.limb(nm, (x, y, 0.55), (x + math.cos(a) * 0.1, y + math.sin(a) * 0.1, 0.55 + h), 0.2 if i == 0 else 0.13, 0.16 if i == 0 else 0.1, 7, "bone")
        top = (x + math.cos(a) * 0.1, y + math.sin(a) * 0.1, 0.55 + h)
        for k in range(5):
            b = k * 2 * PI / 5
            e.limb(nm, top, (top[0] + math.cos(b) * 0.28, top[1] + math.sin(b) * 0.28, top[2] + 0.55), 0.045, 0.02, 4, "accent")
        e.sphere(nm, (top[0], top[1], top[2] + 0.1), (0.1, 0.1, 0.1), 6, "amber" if i == 0 else "lume")
        tubes.append((nm, a))

    def idle(p, f):
        for i, (nm, a) in enumerate(tubes):
            ph = sin2(f - i * 7, 70)
            p.rot(nm, x=math.cos(a) * 3 * ph, y=-math.sin(a) * 3 * ph)

    def attack(p, f):
        k = math.sin(PI * f / 20)
        for i, (nm, a) in enumerate(tubes):
            p.scale(nm, sx=1 + 0.2 * k, sy=1 + 0.2 * k, sz=1 + 0.3 * k)
            p.rot(nm, x=math.cos(a) * 14 * k, y=-math.sin(a) * 14 * k)

    return [("Idle", 70, tuple(range(0, 71, 10)), idle), ("Attack", 20, (0, 4, 8, 12, 16, 20), attack)]


def archive_warden(e):
    e.bone("Root", (0, 0, 2.0))
    e.bone("Core", (0, 0, 2.0), "Root")
    e.sphere("Core", (0, 0, 2.0), (0.95, 0.95, 0.9), 14, "stone")
    for k in range(3):
        a = k * PI / 3
        e.ring("Core", (0, 0, 2.0), 0.97, 0.05, 28, rot=(PI / 2, 0, a), key="rune")
    e.box("Core", (0, -0.86, 2.0), (0.7, 0.22, 0.14), key="amber")
    e.sphere("Core", (0, -0.9, 2.0), (0.08, 0.08, 0.08), 6, "eye")
    for sx in (-1, 1):
        e.limb("Core", (sx * 0.5, 0.2, 1.3), (sx * 0.7, 0.6, 0.5), 0.1, 0.05, 6, "stone")
        e.sphere("Core", (sx * 0.7, 0.6, 0.45), (0.1, 0.1, 0.1), 6, "rune")
    e.cone("Core", (0, 0, 1.0), r=0.5, h=0.7, seg=6, rot=(PI, 0, 0), key="stone", base=True)
    rings = []
    for i, (R, r) in enumerate(((1.5, 0.05), (1.9, 0.05), (2.3, 0.045))):
        nm = f"Ring{i}"
        e.bone(nm, (0, 0, 2.0), "Root")
        e.ring(nm, (0, 0, 2.0), R, r, 36, key="armor")
        for k in range(4):
            a = k * PI / 2 + i
            e.box(nm, (math.cos(a) * R, math.sin(a) * R, 2.0), (0.22, 0.22, 0.16), rot=(0, 0, a), key="rune")
        rings.append(nm)

    def idle(p, f):
        p.move("Root", z=0.1 * sin2(f, 80))
        p.rot("Ring0", x=360.0 * f / 80)
        p.rot("Ring1", y=-360.0 * f / 80)
        p.rot("Ring2", z=360.0 * f / 80, x=20)
        p.rot("Core", z=15 * sin2(f, 80))

    def attack(p, f):
        k = math.sin(PI * f / 24)
        p.rot("Ring0", x=360.0 * f / 24)
        p.rot("Ring1", y=-360.0 * f / 24)
        p.scale("Core", s=1 + 0.12 * k)
        for nm in rings:
            p.scale(nm, s=1 - 0.15 * k)
        p.move("Root", y=-0.5 * k)

    return [("Idle", 80, tuple(range(0, 81, 10)), idle), ("Attack", 24, (0, 4, 8, 12, 16, 20, 24), attack)]


def obelisk_stalker(e):
    e.bone("Root", (0, 0, 2.6))
    e.bone("Body", (0, 0, 2.6), "Root")
    e.bone("Crown", (0, 0, 5.6), "Body")
    e.cyl("Body", (0, 0, 2.7), (0.55, 0.3), 2.6, 4, rot=(0, 0, PI / 4), key="stone", base=True)
    e.box("Body", (0, 0, 2.55), (1.2, 1.2, 0.3), key="armor")
    e.box("Body", (0, -0.2, 3.9), (0.12, 0.5, 1.3), key="amber")
    e.cone("Body", (0, 0, 5.3), r=0.3, h=0.5, seg=4, rot=(0, 0, PI / 4), key="stone", base=True)
    for z in (3.0, 4.6):
        e.ring("Body", (0, 0, z), 0.42 if z < 4 else 0.36, 0.04, 4 * 4, key="rune")
    e.ring("Crown", (0, 0, 6.1), 0.9, 0.06, 32, key="armor")
    for k in range(6):
        a = k * PI / 3
        e.box("Crown", (math.cos(a) * 0.9, math.sin(a) * 0.9, 6.1), (0.2, 0.2, 0.14), rot=(0, 0, a), key="rune")
    legs = []
    for i, a in enumerate((PI * 1.5, PI * 1.5 + 2 * PI / 3, PI * 1.5 + 4 * PI / 3)):
        ux, uy = math.cos(a), math.sin(a)
        u = f"LegU{i}"
        l = f"LegL{i}"
        hip = (ux * 0.45, uy * 0.45, 2.5)
        knee = (ux * 1.5, uy * 1.5, 1.7)
        foot = (ux * 1.9, uy * 1.9, 0.0)
        e.bone(u, hip, "Root")
        e.bone(l, knee, u)
        e.limb(u, hip, knee, 0.13, 0.1, 6, "hull")
        e.sphere(u, knee, (0.16, 0.16, 0.16), 6, "armor")
        e.limb(l, knee, foot, 0.1, 0.07, 6, "armor")
        e.cone(l, (foot[0], foot[1], 0.0), r=0.16, h=0.2, seg=5, key="stone", base=True)
        legs.append((u, l, i))

    def walk(p, f):
        for u, l, i in legs:
            ph = sin2(f + i * 8, 24)
            p.rot(u, x=22 * ph)
            p.rot(l, x=-18 * max(0, -ph))
        p.move("Root", z=0.07 * abs(sin2(f, 12)))
        p.rot("Crown", z=360.0 * f / 24)

    def idle(p, f):
        p.rot("Crown", z=360.0 * f / 80)
        p.rot("Body", x=1.5 * sin2(f, 80))

    def attack(p, f):
        k = math.sin(PI * f / 24)
        p.rot("Body", x=-20 * k)
        p.move("Root", y=-0.5 * k, z=-0.25 * k)
        p.rot("Crown", z=360.0 * f / 24 * 2)

    return [("Idle", 80, tuple(range(0, 81, 10)), idle), ("Walk", 24, tuple(range(0, 25, 4)), walk), ("Attack", 24, (0, 4, 8, 12, 16, 20, 24), attack)]


def lamplighter(e):
    e.bone("Root", (0, 0, 2.2))
    e.bone("Body", (0, 0, 2.2), "Root")
    e.bone("ArmU", (0.25, -0.2, 3.0), "Body")
    e.bone("ArmL", (0.25, -1.0, 3.3), "ArmU")
    e.bone("Lantern", (0.25, -1.7, 3.0), "ArmL")
    e.cone("Body", (0, 0, 1.6), r=0.55, h=1.4, seg=6, rot=(PI, 0, 0), key="stone", base=True)
    e.sphere("Body", (0, 0, 3.3), (0.45, 0.45, 0.5), 10, "armor")
    e.box("Body", (0, -0.4, 3.35), (0.44, 0.1, 0.12), key="amber")
    e.sphere("Body", (0, -0.45, 3.35), (0.06, 0.06, 0.06), 6, "eye")
    e.ring("Body", (0, 0, 2.5), 0.6, 0.04, 20, key="rune")
    e.cone("Body", (0, 0, 3.75), r=0.12, h=0.5, seg=5, key="stone", base=True)
    skirt = []
    for i in range(6):
        a = i * PI / 3
        nm = f"Skirt{i}"
        e.bone(nm, (math.cos(a) * 0.4, math.sin(a) * 0.4, 2.6), "Body")
        e.limb(nm, (math.cos(a) * 0.4, math.sin(a) * 0.4, 2.6), (math.cos(a) * 0.55, math.sin(a) * 0.55, 1.2), 0.05, 0.015, 5, "hull")
        skirt.append((nm, a))
    e.limb("ArmU", (0.25, -0.2, 3.0), (0.25, -1.0, 3.3), 0.07, 0.06, 6, "armor")
    e.limb("ArmL", (0.25, -1.0, 3.3), (0.25, -1.7, 3.1), 0.06, 0.05, 6, "hull")
    e.limb("Lantern", (0.25, -1.7, 3.1), (0.25, -1.7, 2.75), 0.02, key="hull")
    e.cyl("Lantern", (0.25, -1.7, 2.6), (0.22, 0.14), 0.32, 6, key="glass")
    e.sphere("Lantern", (0.25, -1.7, 2.6), (0.12, 0.12, 0.14), 8, "amber")
    e.cone("Lantern", (0.25, -1.7, 2.76), r=0.2, h=0.12, seg=6, key="armor", base=True)

    def idle(p, f):
        p.move("Root", z=0.12 * sin2(f, 60))
        p.rot("ArmU", x=6 * sin2(f, 60))
        p.rot("Lantern", x=14 * sin2(f - 8, 60), y=10 * sin2(f - 4, 60))
        for nm, a in skirt:
            p.rot(nm, x=math.cos(a) * 8 * sin2(f - 6, 60), y=-math.sin(a) * 8 * sin2(f - 6, 60))

    def swim(p, f):
        idle(p, f)
        p.rot("Body", x=-12)

    def attack(p, f):
        k = math.sin(PI * f / 20)
        p.rot("ArmU", x=-40 * k)
        p.rot("ArmL", x=-30 * k)
        p.rot("Lantern", x=60 * k)
        p.scale("Lantern", s=1 + 0.5 * k)
        p.move("Root", y=-0.3 * k)

    return [("Idle", 60, (0, 10, 20, 30, 40, 50, 60), idle), ("Swim", 60, (0, 10, 20, 30, 40, 50, 60), swim), ("Attack", 20, (0, 5, 10, 15, 20), attack)]


def echo_manta(e):
    e.bone("Root", (0, 0, 2.0))
    e.bone("Body", (0, 0, 2.0), "Root")
    e.bone("WingL", (0.5, 0, 2.0), "Body")
    e.bone("WingR", (-0.5, 0, 2.0), "Body")
    e.sphere("Body", (0, 0, 2.0), (0.8, 1.5, 0.38), 12, "armor")
    e.sphere("Body", (0, -1.0, 2.05), (0.5, 0.6, 0.3), 10, "hull")
    for sx in (-1, 1):
        e.sphere("Body", (sx * 0.28, -1.5, 2.15), (0.09, 0.09, 0.09), 6, "eye")
        e.limb("Body", (sx * 0.2, -1.55, 2.0), (sx * 0.55, -2.2, 1.95), 0.07, 0.03, 5, "armor")
    e.box("Body", (0, 0.2, 2.35), (0.08, 1.1, 0.14), key="lume")
    e.sphere("Body", (0, 0.1, 2.28), (0.2, 0.3, 0.1), 8, "lume")
    for sx, nm in ((1, "WingL"), (-1, "WingR")):
        e.sphere(nm, (sx * 2.4, 0.15, 2.0), (2.1, 1.0, 0.07), 12, "ghost")
        e.limb(nm, (sx * 0.5, -0.4, 2.02), (sx * 4.2, 0.45, 2.0), 0.04, 0.02, 5, "armor")
        e.limb(nm, (sx * 0.5, 0.3, 2.0), (sx * 3.6, 1.0, 2.0), 0.03, 0.015, 5, "armor")
        e.sphere(nm, (sx * 3.0, 0.4, 2.02), (0.1, 0.1, 0.1), 6, "lume")
    tail = []
    prev = "Body"
    for i in range(5):
        y = 1.4 + i * 0.7
        nm = f"Tail{i}"
        e.bone(nm, (0, y, 2.0), prev)
        e.limb(nm, (0, y, 2.0), (0, y + 0.7, 2.0), 0.12 - i * 0.02, 0.1 - i * 0.02, 5, "hull")
        tail.append(nm)
        prev = nm
    e.sphere(tail[-1], (0, 1.4 + 5 * 0.7 + 0.1, 2.0), (0.1, 0.18, 0.1), 6, "lume")
    echoes = []
    for i in range(2):
        nm = f"Echo{i}"
        e.bone(nm, (0, 0, 2.0), "Root")
        oy = 2.6 + i * 1.5
        e.sphere(nm, (0, oy, 2.0), (0.7 - i * 0.12, 1.3 - i * 0.2, 0.3), 10, "ghost")
        for sx in (-1, 1):
            e.sphere(nm, (sx * 2.0, oy + 0.15, 2.0), (1.8 - i * 0.35, 0.8 - i * 0.12, 0.05), 10, "ghost")
        echoes.append(nm)

    def flap(p, f, amp, period):
        p.rot("WingL", y=amp * sin2(f, period))
        p.rot("WingR", y=-amp * sin2(f, period))
        for i, nm in enumerate(tail):
            p.rot(nm, z=10 * sin2(f - i * 4, period))
        for i, nm in enumerate(echoes):
            p.move(nm, z=0.18 * sin2(f - 8 * (i + 1), period))

    def idle(p, f):
        flap(p, f, 14, 60)
        p.move("Root", z=0.12 * sin2(f, 60))

    def swim(p, f):
        flap(p, f, 24, 30)

    def attack(p, f):
        k = math.sin(PI * f / 24)
        p.rot("WingL", y=-32 * k)
        p.rot("WingR", y=32 * k)
        p.move("Root", y=-2.0 * k)
        for i, nm in enumerate(echoes):
            p.move(nm, x=(2.2 + i * 1.5) * k * (1 if i == 0 else -1), y=-1.2 * k)

    return [("Idle", 60, (0, 10, 20, 30, 40, 50, 60), idle), ("Swim", 30, (0, 5, 10, 15, 20, 25, 30), swim), ("Attack", 24, (0, 4, 8, 12, 16, 20, 24), attack)]


def void_anemone(e):
    e.bone("Root", (0, 0, 0.0))
    e.cyl("Root", (0, 0, 0), (1.6, 1.2), 0.45, 10, key="stone", base=True)
    e.cyl("Root", (0, 0, 0.45), (0.55, 0.4), 1.6, 8, key="stone", base=True)
    e.ring("Root", (0, 0, 0.5), 1.15, 0.05, 28, key="rune")
    e.bone("Crown", (0, 0, 2.5), "Root")
    e.sphere("Crown", (0, 0, 2.2), (0.55, 0.55, 0.42), 10, "ghost")
    e.sphere("Crown", (0, 0, 2.2), (0.28, 0.28, 0.22), 8, "lume")
    e.ring("Crown", (0, 0, 3.4), 0.75, 0.04, 26, key="rune")
    ten = []
    for i in range(12):
        a = i * 2 * PI / 12
        x, y = math.cos(a) * 0.45, math.sin(a) * 0.45
        names = []
        prev = "Crown"
        for s in range(3):
            nm = f"T{i}_{s}"
            z0 = 2.1 + s * 0.0
            r0 = 0.45 + s * 0.42
            r1 = 0.45 + (s + 1) * 0.42
            zz0 = 2.2 + s * 0.55
            zz1 = 2.2 + (s + 1) * 0.55
            e.bone(nm, (math.cos(a) * r0, math.sin(a) * r0, zz0), prev)
            e.limb(nm, (math.cos(a) * r0, math.sin(a) * r0, zz0), (math.cos(a) * r1, math.sin(a) * r1, zz1), 0.06 - s * 0.012, 0.05 - s * 0.012, 5, "hull")
            e.sphere(nm, (math.cos(a) * r1, math.sin(a) * r1, zz1), (0.065, 0.065, 0.065), 5, "lume" if s == 2 else "armor")
            names.append(nm)
            prev = nm
        ten.append((a, names))

    def idle(p, f):
        k = sin2(f, 80)
        p.scale("Crown", sx=1 + 0.04 * k, sy=1 + 0.04 * k, sz=1 - 0.05 * k)
        p.rot("Crown", z=360.0 * f / 160)
        for a, names in ten:
            for s, nm in enumerate(names):
                ph = sin2(f - s * 6 - a * 6, 80)
                p.rot(nm, x=math.cos(a) * 9 * ph, y=-math.sin(a) * 9 * ph)

    def attack(p, f):
        k = math.sin(PI * f / 22)
        for a, names in ten:
            for s, nm in enumerate(names):
                p.rot(nm, x=math.cos(a) * 36 * k, y=-math.sin(a) * 36 * k)
        p.scale("Crown", s=1 + 0.2 * k)

    return [("Idle", 80, tuple(range(0, 81, 10)), idle), ("Attack", 22, (0, 4, 8, 12, 16, 22), attack)]


MODELS = [
    ("enemy_lantern_swarm", lantern_swarm),
    ("enemy_viperfish_hunter", viperfish_hunter),
    ("enemy_siphonophore_chain", siphonophore_chain),
    ("enemy_isopod_roller", isopod_roller),
    ("enemy_tubeworm_spitter", tubeworm_spitter),
    ("enemy_archive_warden", archive_warden),
    ("enemy_obelisk_stalker", obelisk_stalker),
    ("enemy_lamplighter", lamplighter),
    ("enemy_echo_manta", echo_manta),
    ("enemy_void_anemone", void_anemone),
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
