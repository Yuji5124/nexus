"""DEEP-SEA SUBMARINE: 潜水艦の改造パーツ 20 点 (NEXUS オリジナル)。Blender 4.x / 5.x で動く。

ライブの Blender (Blender MCP) から:
    exec(open(r"<nexus>/scripts/deep-sea-submarine/build_sub_parts.py", encoding="utf-8").read(), {"__name__": "nexus_sub"})  のあと
    run(only=None)   # 全点を書き出し、ビューに並べる
ヘッドレス:
    blender -b -P scripts/deep-sea-submarine/build_sub_parts.py -- <出力フォルダ> <サムネイルのフォルダ> [モデルID ...]

形・一覧は sub_parts.py。規約: 1 unit = 1 m、Y が上、艦首が +Z (glTF)、取り付け点が原点。
ライブで実行しても、開いているシーンの既存オブジェクトには触らない (専用のコレクション NEXUS_SUB に作り、書き出したあと横に並べる)。
材質 (テクスチャなし): hull / dark / accent (オレンジ) / glow (シアン発光) / warm (灯り) / glass (半透明) / brass / shell (紫) / gold / rubber
"""
import bpy, bmesh, math, os, sys, random, json
from mathutils import Matrix, Vector, Euler

_here = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else r"C:\Users\hp\Desktop\nexus\scripts\deep-sea-submarine"
if _here not in sys.path:
    sys.path.insert(0, _here)
import importlib
import sub_parts as P  # noqa: E402
importlib.reload(P)

PI = math.pi
ROOT = os.path.abspath(os.path.join(_here, "..", ".."))
COLL = "NEXUS_SUB"


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






Shape2 = P.extend_shape(Shape)

# ---------------------------------------------------------------- 材質
MAT_DEF = {
    "hull": ((0.30, 0.36, 0.40), 0.6, 0.5, None, 1.0),
    "dark": ((0.08, 0.10, 0.13), 0.5, 0.55, None, 1.0),
    "accent": ((0.85, 0.30, 0.08), 0.2, 0.5, None, 1.0),
    "glow": ((0.16, 0.92, 0.86), 0.0, 0.4, 3.0, 1.0),
    "warm": ((1.0, 0.82, 0.45), 0.0, 0.4, 4.5, 1.0),
    "glass": ((0.7, 0.92, 1.0), 0.0, 0.1, 0.4, 0.35),
    "brass": ((0.80, 0.58, 0.24), 1.0, 0.35, None, 1.0),
    "shell": ((0.46, 0.20, 0.70), 0.0, 0.5, None, 1.0),
    "gold": ((1.0, 0.72, 0.22), 1.0, 0.32, None, 1.0),
    "rubber": ((0.03, 0.03, 0.04), 0.0, 0.9, None, 1.0),
}


def make_mats():
    mats = {}
    for key, (rgb, metal, rough, emit, alpha) in MAT_DEF.items():
        name = "sub_" + key
        m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
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
            for attr, val in (("blend_method", "BLEND"), ("surface_render_method", "BLENDED")):
                try:
                    setattr(m, attr, val)
                except (AttributeError, TypeError):
                    pass
        mats[key] = m
    return mats


def finalize(name, shape, mats):
    objs = []
    for key, bm in shape.bm.items():
        if not bm.verts:
            bm.free()
            continue
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        mesh = bpy.data.meshes.new(f"{name}_{key}")
        bm.to_mesh(mesh)
        bm.free()
        mesh.materials.append(mats[key])
        for p in mesh.polygons:
            p.use_smooth = False
        o = bpy.data.objects.new(f"{name}_{key}", mesh)
        objs.append(o)
    return objs


# ---------------------------------------------------------------- サムネイル (ライブのシーンの設定は、終わったら元に戻す)
def _engine():
    items = [i.identifier for i in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    for e in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "CYCLES"):
        if e in items:
            return e
    return items[0]


def render_thumb(scn, objs, path):
    r = scn.render
    saved = dict(engine=r.engine, rx=r.resolution_x, ry=r.resolution_y, pct=r.resolution_percentage, fp=r.filepath, ft=r.film_transparent, ff=r.image_settings.file_format, cm=r.image_settings.color_mode, cam=scn.camera, world=scn.world)
    r.engine = _engine()
    r.resolution_x = r.resolution_y = 256
    r.resolution_percentage = 100
    r.film_transparent = True
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGBA"
    lo = Vector((1e9,) * 3)
    hi = Vector((-1e9,) * 3)
    for o in objs:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, w))
            hi = Vector(map(max, hi, w))
    c = (lo + hi) / 2
    rad = max((hi - lo).length * 0.5, 0.5)
    w = bpy.data.worlds.new("nexus_sub_w")
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = (0.18, 0.28, 0.36, 1)
    bg.inputs[1].default_value = 1.0
    scn.world = w
    tmp = []
    for loc, e, sz in (((4, -5, 6), 900, 6), ((-6, -2, 3), 300, 6), ((0, 6, 4), 260, 6)):
        ld = bpy.data.lights.new("nexus_sub_l", "AREA")
        ld.energy = e * rad * rad * 0.35
        ld.size = sz * rad * 0.5
        lo_ = bpy.data.objects.new("nexus_sub_l", ld)
        scn.collection.objects.link(lo_)
        lo_.location = c + Vector(loc) * rad * 0.5
        lo_.rotation_euler = (c - lo_.location).to_track_quat("-Z", "Y").to_euler()
        tmp.append(lo_)
    cd = bpy.data.cameras.new("nexus_sub_c")
    cd.lens = 50
    cam = bpy.data.objects.new("nexus_sub_c", cd)
    scn.collection.objects.link(cam)
    cam.location = c + Vector((0.9, -1.0, 0.55)).normalized() * rad * 2.7
    cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
    scn.camera = cam
    r.filepath = path
    keep = set(objs) | set(tmp) | {cam}
    hidden = [(o, o.hide_render) for o in scn.objects if o not in keep]
    for o, _ in hidden:
        o.hide_render = True
    bpy.ops.render.render(write_still=True)
    for o, h in hidden:
        o.hide_render = h
    for o in tmp + [cam]:
        bpy.data.objects.remove(o)
    for ld in [d for d in bpy.data.lights if d.name.startswith("nexus_sub_l")]:
        bpy.data.lights.remove(ld)
    for cd_ in [d for d in bpy.data.cameras if d.name.startswith("nexus_sub_c")]:
        bpy.data.cameras.remove(cd_)
    bpy.data.worlds.remove(w)
    scn.world = saved["world"]
    scn.camera = saved["cam"]
    r.engine, r.resolution_x, r.resolution_y, r.resolution_percentage = saved["engine"], saved["rx"], saved["ry"], saved["pct"]
    r.filepath, r.film_transparent = saved["fp"], saved["ft"]
    r.image_settings.file_format, r.image_settings.color_mode = saved["ff"], saved["cm"]


def run(only=None, out=None, thumbs=None, layout=True, headless=False):
    out = os.path.abspath(out or os.path.join(ROOT, "assets", "deep-sea-submarine"))
    thumbs = os.path.abspath(thumbs or os.path.join(ROOT, "thumbnails", "deep-sea-submarine"))
    os.makedirs(out, exist_ok=True)
    os.makedirs(thumbs, exist_ok=True)
    scn = bpy.context.scene
    coll = bpy.data.collections.get(COLL) or bpy.data.collections.new(COLL)
    if coll.name not in [c.name for c in scn.collection.children]:
        scn.collection.children.link(coll)
    mats = make_mats()
    only = set(only or [])
    done = []
    for n, (mid, fn, _j, kind, name, desc, roles, tags) in enumerate(P.MODELS):
        if only and mid not in only:
            continue
        for o in [o for o in coll.objects if o.name.startswith(mid + "_")]:
            bpy.data.objects.remove(o)
        for me in [me for me in bpy.data.meshes if me.name.startswith(mid + "_") and me.users == 0]:
            bpy.data.meshes.remove(me)
        s = Shape2()
        fn(s)
        objs = finalize(mid, s, mats)
        for o in objs:
            coll.objects.link(o)
        for o in bpy.context.view_layer.objects:
            o.select_set(False)
        for o in objs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        bpy.ops.export_scene.gltf(filepath=os.path.join(out, mid + ".glb"), export_format="GLB", use_selection=True, export_yup=True)
        render_thumb(scn, objs, os.path.join(thumbs, mid + ".png"))
        if layout and not headless:
            off = Vector(((n % 5) * 9.0 + 12.0, -(n // 5) * 9.0, 0.0))
            for o in objs:
                o.location = off
        done.append(mid)
        print("built", mid)
    if not only:
        cat = [{"id": m[0], "kind": m[3], "name": m[4], "description": m[5], "roles": m[6], "tags": m[7]} for m in P.MODELS]
        with open(os.path.join(_here, "catalog.json"), "w", encoding="utf-8") as fh:
            json.dump(cat, fh, ensure_ascii=False, indent=2)
            fh.write(chr(10))
    print("OK", len(done))
    return done


if __name__ == "__main__" and "--" in sys.argv:
    _a = sys.argv[sys.argv.index("--") + 1:]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    run(only=_a[2:], out=_a[0] if _a else None, thumbs=_a[1] if len(_a) > 1 else None, layout=False, headless=True)
