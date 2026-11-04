"""確認用レンダー (ヘッドレス Blender): blender -b -P render_boss_mure.py -- <glb> <出力png> [front|three|side|close]"""
import sys, math
import bpy
from mathutils import Vector

a = sys.argv[sys.argv.index("--") + 1:]
glb, out = a[0], a[1]
view = a[2] if len(a) > 2 else "front"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
for o in bpy.data.objects:
    if o.type == "MESH":
        for m in o.data.materials:
            nt = m.node_tree
            b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
            vc = nt.nodes.new("ShaderNodeVertexColor")
            vc.layer_name = o.data.color_attributes[0].name if o.data.color_attributes else "Color"
            nt.links.new(vc.outputs["Color"], b.inputs["Base Color"])
            nt.links.new(vc.outputs["Color"], b.inputs["Emission Color"])
            b.inputs["Emission Strength"].default_value = 0.35
w = bpy.data.worlds.new("w")
bpy.context.scene.world = w
w.use_nodes = True
bg = next((n for n in w.node_tree.nodes if n.type == "BACKGROUND"), None) or w.node_tree.nodes.new("ShaderNodeBackground")
out_n = next((n for n in w.node_tree.nodes if n.type == "OUTPUT_WORLD"), None) or w.node_tree.nodes.new("ShaderNodeOutputWorld")
w.node_tree.links.new(bg.outputs[0], out_n.inputs[0])
bg.inputs[0].default_value = (0.16, 0.27, 0.34, 1)
bg.inputs[1].default_value = 1.0
s = bpy.context.scene
s.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [i.identifier for i in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
s.render.resolution_x, s.render.resolution_y = 1400, 900
sun = bpy.data.lights.new("sun", "SUN")
sun.energy = 3.0
so = bpy.data.objects.new("sun", sun)
bpy.context.collection.objects.link(so)
so.rotation_euler = (math.radians(50), 0, math.radians(30))
cam = bpy.data.cameras.new("c")
co = bpy.data.objects.new("c", cam)
bpy.context.collection.objects.link(co)
s.camera = co
tgt = {"front": ((0, 38, 0), (0, 0, 40)), "three": ((0, 38, 0), (0, 0, 40)), "side": ((0, 38, 0), (0, 0, 40)), "close": ((0, 0, 0), (0, 0, 0))}
# glTF 座標 (Y 上、前 +Z、翼幅 X、尾は -Z)
if view == "front":
    co.location, tc, cam.lens = (0, 55, 560), (0, 55, 0), 40
elif view == "three":
    co.location, tc, cam.lens = (330, 160, 430), (0, 55, 0), 40
elif view == "side":
    co.location, tc, cam.lens = (560, 60, 0), (0, 55, -10), 40
else:
    co.location, tc, cam.lens = (9, 78, 118), (0, 74, 85), 50
cam.clip_end = 2000
d = Vector(tc) - Vector(co.location)
co.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
s.render.filepath = out
bpy.ops.render.render(write_still=True)
