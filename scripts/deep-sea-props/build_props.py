"""DEEP-SEA PROPS: 深海の効果・拾得品・小道具 20 点 (NEXUS オリジナル)。Blender (4.x/5.x) をヘッドレスで動かして GLB とサムネイルを作る。

    blender -b -P scripts/deep-sea-props/build_props.py -- <出力フォルダ> <サムネイルのフォルダ> [モデルID ...]

形・材質の定義は parts.py にある。規約: 1 unit = 1 m、原点は底の中心 (効果は基準点)、glTF 出力後は Y が上、正面は +Z。
(Shape・風化・書き出しは scripts/deep-sea-ruins/build_ruins.py と同じものを、このファイルに取り込んである)
材質: stone (頂点色で風化) / glow・warm・bio (発光) / metal (錆びた鉄) / gold / wood /
      beam (光・波の半透明、発光) / glass (半透明のガラス・泡)
"""
import bpy, bmesh, math, os, sys, random
from mathutils import Matrix, Vector, Euler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parts as P  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = os.path.abspath(argv[0]) if argv else os.path.abspath("out")
THUMBS = os.path.abspath(argv[1]) if len(argv) > 1 else os.path.join(OUT, "_thumbs")
ONLY = set(argv[2:])
PI = math.pi
os.makedirs(OUT, exist_ok=True)
os.makedirs(THUMBS, exist_ok=True)


# ---------------------------------------------------------------- 形の道具 (ruins と共通 + 効果用の形)
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
MAT_DEF = {
    "glow": ((0.16, 0.92, 0.86), 0.0, 0.4, 3.0, 1.0),
    "warm": ((1.0, 0.66, 0.2), 0.0, 0.4, 3.5, 1.0),
    "bio": ((0.55, 1.0, 0.7), 0.0, 0.4, 2.2, 1.0),
    "metal": ((0.30, 0.22, 0.17), 0.7, 0.62, None, 1.0),
    "gold": ((1.0, 0.72, 0.22), 1.0, 0.32, None, 1.0),
    "wood": ((0.32, 0.20, 0.12), 0.0, 0.85, None, 1.0),
    "beam": ((0.45, 0.9, 1.0), 0.0, 0.3, 2.0, 0.26),
    "glass": ((0.7, 0.92, 1.0), 0.0, 0.1, 0.5, 0.35),
}


def make_mats():
    mats = {}
    m = bpy.data.materials.new("prop_stone")
    m.use_nodes = True
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    col = nt.nodes.new("ShaderNodeVertexColor")
    col.layer_name = "Col"
    nt.links.new(col.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.88
    mats["stone"] = m
    for key, (rgb, metal, rough, emit, alpha) in MAT_DEF.items():
        m = bpy.data.materials.new("prop_" + key)
        m.use_nodes = True
        b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        b.inputs["Base Color"].default_value = (*rgb, 1)
        b.inputs["Metallic"].default_value = metal
        b.inputs["Roughness"].default_value = rough
        if emit:
            b.inputs["Base Color"].default_value = (rgb[0] * 0.25, rgb[1] * 0.25, rgb[2] * 0.25, 1)
            b.inputs["Emission Color"].default_value = (*rgb, 1)
            b.inputs["Emission Strength"].default_value = emit
        if alpha < 1.0:
            b.inputs["Alpha"].default_value = alpha
            m.blend_method = "BLEND"
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



Shape2 = P.extend_shape(Shape)
MODELS = P.MODELS


def build_model(mid, fn, jitter):
    s = Shape2()
    fn(s)
    return s


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
    for mid, fn, jitter, kind, name, desc, roles, tags in MODELS:
        if ONLY and mid not in ONLY:
            continue
        clear_scene()
        s = build_model(mid, fn, jitter)
        objs = finalize(mid, s, mats, jitter=jitter, tint=(1, 1, 1))
        for o in objs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, mid + ".glb"), export_format="GLB", use_selection=True, export_yup=True)
        render_thumb(objs, os.path.join(THUMBS, mid + ".png"))
        done.append(mid)
        print("built", mid)
    if not ONLY:
        # 一覧 (catalog.json) を書く。import.mjs が読む。ここ (parts.py の MODELS) が元データ
        import json
        cat = [{"id": m[0], "kind": m[3], "name": m[4], "description": m[5], "roles": m[6], "tags": m[7]} for m in MODELS]
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "catalog.json"), "w", encoding="utf-8") as fh:
            json.dump(cat, fh, ensure_ascii=False, indent=2)
            fh.write(chr(10))
    print("OK", len(done))


main()
