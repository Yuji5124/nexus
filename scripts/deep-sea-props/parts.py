"""DEEP-SEA PROPS の部品 (20 点の形・材質・一覧)。build_props.py が読む。

効果の素材 (fx_*) は、ゲームで半透明に重ねて使うメッシュ (beam / glass 材質は alpha blend)。
拾得品 (item_*) と小道具・地形 (prop_*) は、普通の不透明メッシュ。
"""
import math
import random

import bmesh
from mathutils import Matrix, Vector, Euler

PI = math.pi
KEYS = ("stone", "glow", "warm", "bio", "metal", "gold", "wood", "beam", "glass")


def extend_shape(Shape):
    """ruins の Shape に、リボン・開いた円すいなど、効果用の形を足した版を返す。"""

    class Shape2(Shape):
        def __init__(self):
            self.bm = {k: bmesh.new() for k in KEYS}

        def open_cone(self, loc=(0, 0, 0), r=(1, 1), h=1, seg=24, rot=(0, 0, 0), key="beam"):
            """上下の蓋がない円すい台 (光の筒)。r=(下の半径, 上の半径)。"""
            res = bmesh.ops.create_cone(self.bm[key], cap_ends=False, cap_tris=False, segments=seg, radius1=r[0], radius2=max(r[1], 1e-4), depth=1)
            self._put(key, res["verts"], loc, (1, 1, h), rot)

        def ribbon(self, pts, width, key="beam", twist=0.0):
            """点列に沿った帯 (両面表示向け)。pts は [(x,y,z)...]、width は帯の幅。"""
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

        def flat_ring(self, loc=(0, 0, 0), r0=1.0, r1=1.2, seg=48, key="beam", z0=0.0, z1=0.0):
            """平らな輪 (内半径 r0 から外半径 r1)。z0 / z1 で内外の高さを変えると、ふちが反ったラッパ状になる。"""
            bm = self.bm[key]
            inner = [bm.verts.new((r0 * math.cos(2 * PI * i / seg), r0 * math.sin(2 * PI * i / seg), z0)) for i in range(seg)]
            outer = [bm.verts.new((r1 * math.cos(2 * PI * i / seg), r1 * math.sin(2 * PI * i / seg), z1)) for i in range(seg)]
            for i in range(seg):
                n = (i + 1) % seg
                try:
                    bm.faces.new((inner[i], inner[n], outer[n], outer[i]))
                except ValueError:
                    pass
            self._put(key, inner + outer, loc, (1, 1, 1), (0, 0, 0))

    return Shape2


# ---------------------------------------------------------------- 効果 (半透明)
def fx_headlight_beam(s):
    """潜水艦・懐中電灯の光の筒。頂点が原点、+Z (Blender の -Y) 方向へ 14 m 広がる。"""
    s.open_cone((0, -7.0, 0), (0.05, 4.6), 14, 28, rot=(PI / 2, 0, 0), key="beam")
    s.open_cone((0, -6.0, 0), (0.03, 2.2), 12, 24, rot=(PI / 2, 0, 0), key="beam")
    s.sphere((0, -0.05, 0), (0.22, 0.22, 0.22), 8, key="warm")


def fx_light_shaft(s):
    """海面から差す光の柱 (30 m)。入れ子の筒を重ねて、中心ほど明るく見せる。"""
    for k, (r0, r1) in enumerate(((2.2, 4.6), (1.4, 3.0), (0.7, 1.5))):
        s.open_cone((0, 0, 15.0), (r0, r1), 30, 20, key="beam")
    s.cyl((0, 0, 0), (1.2, 1.2), 0.05, 20, base=True, key="beam")


def fx_bubble_cluster(s):
    rnd = random.Random(3)
    for i in range(16):
        h = 0.3 + i * 0.26
        r = 0.06 + rnd.uniform(0, 0.1) + i * 0.004
        s.sphere((rnd.uniform(-0.25, 0.25) * (1 + i * 0.05), rnd.uniform(-0.25, 0.25) * (1 + i * 0.05), h), (r, r, r), 8, key="glass")


def fx_sonar_ring(s):
    """ソナーの波紋。同心の3本の輪を重ねる (拡大させて使う)。"""
    for R, r in ((3.0, 0.07), (6.0, 0.06), (9.0, 0.05)):
        s.ring((0, 0, 0), R, r, 56, key="beam", sub=4)
    s.cyl((0, 0, 0), (0.25, 0.25), 0.12, 12, key="glow")


def fx_shockwave_ring(s):
    """衝撃波。ふちが反ったラッパ状の輪 (直径 8 m)。"""
    s.flat_ring((0, 0, 0), 2.4, 4.0, 48, key="beam", z0=0.0, z1=0.5)
    s.flat_ring((0, 0, 0), 2.0, 2.4, 48, key="glow", z0=0.0, z1=0.05)


def fx_energy_orb(s):
    s.sphere((0, 0, 1.0), (0.35, 0.35, 0.35), 10, key="glow")
    s.sphere((0, 0, 1.0), (0.9, 0.9, 0.9), 14, key="glass")
    s.ring((0, 0, 1.0), 1.15, 0.03, 36, key="glow", sub=4)
    s.ring((0, 0, 1.0), 1.15, 0.03, 36, rot=(PI / 2, 0, 0), key="glow", sub=4)
    s.ring((0, 0, 1.0), 1.35, 0.025, 36, rot=(PI / 3, 0, PI / 4), key="warm", sub=4)


def fx_spark_burst(s):
    golden = PI * (3 - math.sqrt(5))
    for i in range(28):
        y = 1 - 2 * (i + 0.5) / 28
        rr = math.sqrt(1 - y * y)
        d = Vector((math.cos(golden * i) * rr, math.sin(golden * i) * rr, y))
        a, b = Vector((0, 0, 1.2)) + d * 0.35, Vector((0, 0, 1.2)) + d * (1.3 + 0.3 * (i % 3))
        dd = b - a
        rot = dd.to_track_quat("Z", "Y").to_euler()
        s.cyl(((a + b) / 2).to_tuple(), (0.05, 0.0), dd.length, 5, rot=tuple(rot), key="warm" if i % 2 else "glow")
    s.sphere((0, 0, 1.2), (0.22, 0.22, 0.22), 8, key="warm")


def fx_current_vortex(s):
    """渦巻く海流の帯 (3 巻き、高さ 8 m)。"""
    for off in (0.0, PI):
        pts = []
        for i in range(60):
            t = i / 59
            a = off + t * 3 * 2 * PI
            r = 0.6 + 2.4 * t
            pts.append((math.cos(a) * r, math.sin(a) * r, 0.2 + 7.6 * t))
        s.ribbon(pts, 0.7 + 0.5 * 1, key="beam")
    s.open_cone((0, 0, 4.0), (0.3, 0.3), 8, 8, key="glass")


# ---------------------------------------------------------------- 拾得品
def item_shard_crystal(s):
    """欠片 (通貨)。シアンの結晶の束 (六角柱 + とがった先)。"""
    rnd = random.Random(2)
    s.cyl((0, 0, 0), (0.55, 0.45), 0.18, 8, base=True, key="stone")

    def crystal(x, y, tilt_a, tilt, h, w):
        d = Vector((math.sin(tilt) * math.cos(tilt_a), math.sin(tilt) * math.sin(tilt_a), math.cos(tilt)))
        p0 = Vector((x, y, 0.15))
        rot = tuple(d.to_track_quat("Z", "Y").to_euler())
        body = h * 0.7
        s.cyl(tuple(p0 + d * body / 2), (w, w), body, 6, rot=rot, key="glow")
        s.cyl(tuple(p0 + d * (body + h * 0.15)), (w, 0.0), h * 0.3, 6, rot=rot, key="glow")

    crystal(0.0, 0.0, 0.0, 0.0, 1.15, 0.2)
    for i in range(6):
        a = i * 2 * PI / 6 + rnd.uniform(-0.2, 0.2)
        crystal(math.cos(a) * 0.22, math.sin(a) * 0.22, a, 0.38 + rnd.uniform(0, 0.15), 0.62 + rnd.uniform(0, 0.3), 0.13)


def item_relic_tablet(s):
    """遺物。輪付きの石板 (台座つき)。"""
    s.cyl((0, 0, 0), (0.5, 0.45), 0.12, 8, base=True, key="stone")
    s.box((0, 0, 0.12), (0.8, 0.14, 0.9), base=True, key="stone")
    s.ring((0, -0.08, 0.7), 0.26, 0.04, 20, rot=(PI / 2, 0, 0), key="glow", sub=5)
    s.box((0, -0.08, 0.42), (0.34, 0.03, 0.05), key="glow")
    s.box((0, 0, 1.08), (0.9, 0.18, 0.12), base=False, key="stone")
    s.sphere((0, -0.1, 0.7), (0.07, 0.04, 0.07), 6, key="warm")


def item_heal_pearl(s):
    """回復の真珠。開いた二枚貝の中で光る。"""
    for k, sz in enumerate((1, -1)):
        s.sphere((0, 0, 0.22 + 0.0), (0.62, 0.55, 0.2), 12, key="stone")
    s.sphere((0, 0, 0.38), (0.62, 0.55, 0.16), 12, key="stone")
    s.sphere((0, 0, 0.5), (0.26, 0.26, 0.26), 12, key="glass")
    s.sphere((0, 0, 0.5), (0.14, 0.14, 0.14), 10, key="bio")
    for i in range(5):
        a = i * PI / 4 - PI / 2 + PI / 8
        s.box((math.cos(a) * 0.52, math.sin(a) * 0.46, 0.28), (0.05, 0.3, 0.06), rot=(0, 0, a), key="stone")


def item_treasure_chest(s):
    s.box((0, 0, 0), (1.3, 0.8, 0.55), base=True, key="wood")
    s.box((0, 0, 0.55), (1.3, 0.8, 0.12), base=True, key="metal")
    s.cyl((0, 0, 0.67), (0.4, 0.4), 1.3, 10, rot=(0, PI / 2, 0), key="wood")
    for x in (-0.5, 0.0, 0.5):
        s.box((x, 0, 0.35), (0.1, 0.84, 0.95), key="metal")
    s.box((0, -0.42, 0.55), (0.2, 0.06, 0.24), key="gold")
    s.sphere((0, -0.46, 0.55), (0.05, 0.03, 0.05), 6, key="glow")
    for sx in (-1, 1):
        s.box((sx * 0.6, 0.38, 0.32), (0.12, 0.06, 0.12), key="gold")


def item_ancient_coin(s):
    for i in range(5):
        s.cyl((0.0 + 0.02 * (i % 2), 0.0, i * 0.07), (0.3, 0.3), 0.06, 14, base=True, key="gold")
    s.ring((0.0, 0.0, 0.36), 0.2, 0.02, 20, key="glow", sub=4)
    s.cyl((0.55, 0.2, 0.0), (0.3, 0.3), 0.06, 14, rot=(0.0, 0.0, 0.0), base=True, key="gold")
    s.cyl((0.62, -0.25, 0.03), (0.3, 0.3), 0.06, 14, rot=(0.5, 0.2, 0.0), key="gold")


def item_rune_key(s):
    """古代の鍵。輪の持ち手と、紋様の歯。"""
    s.ring((0, 0, 0.9), 0.24, 0.05, 20, rot=(PI / 2, 0, 0), key="gold", sub=6)
    s.cyl((0, 0, 0.0), (0.05, 0.05), 0.75, 8, base=True, key="gold")
    s.box((0.1, 0, 0.1), (0.2, 0.06, 0.1), key="gold")
    s.box((0.1, 0, 0.28), (0.14, 0.06, 0.1), key="gold")
    s.box((0.08, 0, 0.46), (0.1, 0.06, 0.1), key="gold")
    s.sphere((0, 0, 0.9), (0.09, 0.05, 0.09), 8, key="glow")
    s.cyl((0, 0, 0.7), (0.09, 0.09), 0.06, 8, key="gold")


# ---------------------------------------------------------------- 小道具・地形
def prop_basalt_cluster(s):
    rnd = random.Random(7)
    for i in range(11):
        a = rnd.uniform(0, 2 * PI)
        d = rnd.uniform(0.0, 1.8)
        r = rnd.uniform(0.35, 0.7)
        h = rnd.uniform(0.8, 4.2) * (1.1 - d * 0.25)
        s.cyl((math.cos(a) * d, math.sin(a) * d, 0), (r * 1.1, r), h, 6, rot=(0, 0, rnd.uniform(0, 3)), base=True, key="stone")


def prop_boulder_large(s):
    rnd = random.Random(4)
    s.sphere((0, 0, 1.0), (2.1, 1.8, 1.4), 12, key="stone")
    for i in range(5):
        a = rnd.uniform(0, 2 * PI)
        s.sphere((math.cos(a) * 1.7, math.sin(a) * 1.5, 0.5), (rnd.uniform(0.5, 0.9),) * 3, 8, key="stone")


def prop_anchor(s):
    """沈んだ錨 (錆びた鉄)。"""
    s.cyl((0, 0, 0.0), (0.12, 0.1), 3.2, 8, base=True, key="metal")
    s.ring((0, 0, 3.4), 0.28, 0.07, 20, rot=(PI / 2, 0, 0), key="metal", sub=6)
    s.box((0, 0, 2.7), (1.6, 0.14, 0.14), key="metal")
    s.arc((0, 0, 0.35), R=1.0, w=0.2, d=0.2, a0=PI, a1=2 * PI, seg=14, key="metal")
    for sx in (-1, 1):
        s.cone((sx * 1.1, 0, 0.55), r=0.28, h=0.55, seg=5, rot=(0, sx * -0.6, 0), key="metal", base=False)
    s.box((0, 0, 0.1), (0.5, 0.2, 0.2), key="metal")
    s.sphere((0.35, 0.12, 0.9), (0.18, 0.15, 0.18), 6, key="bio")


def prop_vent_chimney(s):
    """熱水噴出孔の煙突 (チムニー)。上が光る。"""
    s.cyl((0, 0, 0), (1.9, 1.4), 0.7, 10, base=True, key="stone")
    s.cyl((0, 0, 0.7), (1.2, 0.7), 3.4, 9, base=True, key="stone")
    s.cyl((0, 0, 4.0), (0.7, 0.55), 0.6, 9, base=True, key="stone")
    s.cyl((0, 0, 4.58), (0.45, 0.4), 0.05, 12, base=True, key="warm")
    for i in range(6):
        a = i * PI / 3 + 0.3
        s.cyl((math.cos(a) * 1.3, math.sin(a) * 1.3, 0.55), (0.14, 0.08), 0.9 + 0.2 * (i % 3), 6, base=True, key="stone")
        s.sphere((math.cos(a) * 1.3, math.sin(a) * 1.3, 1.5 + 0.2 * (i % 3)), (0.12, 0.12, 0.12), 6, key="bio")
    s.cyl((0.8, 0.2, 0.7), (0.3, 0.2), 1.6, 7, rot=(0.0, 0.3, 0.0), base=True, key="stone")


def prop_crate_stack(s):
    s.box((0, 0, 0), (1.2, 1.2, 1.0), base=True, key="wood")
    s.box((1.25, 0.1, 0), (1.1, 1.1, 0.9), rot=(0, 0, 0.2), base=True, key="wood")
    s.box((0.2, 0.0, 1.0), (1.0, 1.0, 0.9), rot=(0, 0, -0.3), base=True, key="wood")
    for (x, y, z, sz, rz) in ((0, 0, 0.5, 1.2, 0), (1.25, 0.1, 0.45, 1.1, 0.2), (0.2, 0, 1.45, 1.0, -0.3)):
        for dx in (-1, 1):
            s.box((x + dx * sz * 0.42, y, z), (0.08, sz * 1.02, sz * 0.8), rot=(0, 0, rz), key="metal")
    s.cyl((-1.1, -0.3, 0), (0.45, 0.45), 1.0, 12, base=True, key="metal")
    s.ring((-1.1, -0.3, 0.35), 0.46, 0.03, 18, key="metal", sub=4)
    s.ring((-1.1, -0.3, 0.7), 0.46, 0.03, 18, key="metal", sub=4)


def prop_coral_fan(s):
    """扇形のサンゴ (ウミウチワ)。細い枝が扇状に広がる。"""
    s.cyl((0, 0, 0), (0.45, 0.35), 0.25, 8, base=True, key="stone")
    s.cyl((0, 0, 0.2), (0.1, 0.08), 0.5, 6, base=True, key="bio")
    for i in range(11):
        a = -PI / 2.4 + i * (PI / 1.2) / 10
        x, z = math.sin(a) * 1.6, 0.6 + math.cos(a) * 1.6
        d = Vector((x, 0, z - 0.7))
        rot = d.to_track_quat("Z", "Y").to_euler()
        s.cyl((x * 0.5, 0, 0.7 + (z - 0.7) * 0.5), (0.05, 0.02), d.length, 5, rot=tuple(rot), key="bio")
        s.sphere((x, 0, z), (0.07, 0.07, 0.07), 5, key="glow")
    for k in range(3):
        R = 0.7 + k * 0.45
        pts = [(math.sin(-0.9 + j * 1.8 / 14) * R, 0.0, 0.7 + math.cos(-0.9 + j * 1.8 / 14) * R) for j in range(15)]
        s.ribbon(pts, 0.03, key="bio")


MODELS = [
    # id, 関数, 風化, 色調, 区分, 名前, 説明, 用途, タグ
    ("fx_headlight_beam", fx_headlight_beam, 0.0, "effect", "Headlight Beam", "Translucent light cone for a submarine headlight or flashlight: apex at the origin, 14 m long, 9 m wide at the end, with a brighter inner cone and an amber lamp point. Faces +Z.", ["effect", "light"], ["beam", "light-cone", "headlight", "volumetric", "alpha"]),
    ("fx_light_shaft", fx_light_shaft, 0.0, "effect", "Light Shaft", "30 m tall tapered light shaft from the surface, three nested translucent cylinders so the centre reads brighter. Stand it vertically in shallow water.", ["effect", "light"], ["god-ray", "light-shaft", "sunbeam", "volumetric", "alpha"]),
    ("fx_bubble_cluster", fx_bubble_cluster, 0.0, "effect", "Bubble Column", "Sixteen translucent bubbles of growing size rising in a loose column about 4.1 m tall. Scale or animate upward.", ["effect"], ["bubbles", "rising", "water", "alpha"]),
    ("fx_sonar_ring", fx_sonar_ring, 0.0, "effect", "Sonar Pulse Rings", "Three concentric thin rings (3, 6, 9 m radius) plus a glowing centre disc. Animate the scale to make an expanding sonar wave.", ["effect"], ["sonar", "pulse", "ring", "wave", "alpha"]),
    ("fx_shockwave_ring", fx_shockwave_ring, 0.0, "effect", "Shockwave Ring", "Flared ring-shaped shockwave, 8 m across, with a bright glowing inner lip. Expand and fade for hit and landing effects.", ["effect"], ["shockwave", "impact", "ring", "alpha"]),
    ("fx_energy_orb", fx_energy_orb, 0.0, "effect", "Energy Orb", "Glowing core inside a translucent shell with three orbiting rings (cyan and amber). Usable as a charge-up, projectile or power core.", ["effect"], ["orb", "energy", "charge", "projectile", "emissive"]),
    ("fx_spark_burst", fx_spark_burst, 0.0, "effect", "Spark Burst", "Twenty-eight radial spikes (alternating cyan and amber) around a hot core. Spin and scale up for a hit-spark or explosion flash.", ["effect"], ["spark", "burst", "hit", "explosion", "emissive"]),
    ("fx_current_vortex", fx_current_vortex, 0.0, "effect", "Current Vortex", "Two translucent ribbons spiralling three turns up an 8 m column: the look of a strong deep-sea current or whirlpool. Rotate slowly around Y.", ["effect"], ["vortex", "current", "whirlpool", "spiral", "alpha"]),
    ("item_shard_crystal", item_shard_crystal, 0.02, "item", "Shard Crystal", "Currency pickup: a cluster of six glowing cyan crystals on a small stone base, about 1.3 m tall.", ["collectible"], ["shard", "crystal", "currency", "pickup", "emissive"]),
    ("item_relic_tablet", item_relic_tablet, 0.02, "item", "Relic Tablet", "Relic pickup: a small stone tablet on a base with a glowing ring glyph and an amber stud, about 1.2 m tall.", ["collectible"], ["relic", "tablet", "artifact", "pickup", "glyph"]),
    ("item_heal_pearl", item_heal_pearl, 0.015, "item", "Healing Pearl", "Healing pickup: an open stone bivalve cradling a glass pearl with a green glowing heart.", ["collectible"], ["pearl", "shell", "healing", "pickup"]),
    ("item_treasure_chest", item_treasure_chest, 0.01, "item", "Sunken Treasure Chest", "Closed barrel-lidded wooden chest with iron bands, a gold lock plate and a glowing keyhole, 1.3 m wide.", ["collectible", "interactable"], ["chest", "treasure", "loot", "container"]),
    ("item_ancient_coin", item_ancient_coin, 0.0, "item", "Ancient Coins", "A stack of five gold coins with a glowing glyph ring on top and two loose coins beside it.", ["collectible"], ["coin", "gold", "currency", "pickup"]),
    ("item_rune_key", item_rune_key, 0.0, "item", "Rune Key", "Key pickup: gold key with a round bow, three teeth and a glowing glyph gem. 1.2 m tall.", ["collectible"], ["key", "gold", "puzzle", "pickup"]),
    ("prop_basalt_cluster", prop_basalt_cluster, 0.03, "prop", "Basalt Column Cluster", "Eleven six-sided basalt columns of different heights (0.8-4.2 m): the rock of the blue-phosphor basin, and a fine cliff dressing.", ["obstacle", "decoration"], ["basalt", "columns", "rock", "terrain"]),
    ("prop_boulder_large", prop_boulder_large, 0.04, "prop", "Large Boulder", "A big lumpy boulder (4.2 m wide) with five smaller lumps around its base. Use as seabed cover or a wall.", ["obstacle", "decoration"], ["boulder", "rock", "terrain", "cover"]),
    ("prop_anchor", prop_anchor, 0.02, "prop", "Sunken Anchor", "Rusted iron anchor standing upright, 4.6 m tall, with a ring, stock bar, curved arms and a little coral growth.", ["landmark", "decoration"], ["anchor", "shipwreck", "rust", "metal"]),
    ("prop_vent_chimney", prop_vent_chimney, 0.03, "prop", "Hydrothermal Vent Chimney", "Stacked stone chimney 4.6 m tall with a glowing amber mouth, ringed by small stalks with glowing green tips.", ["landmark", "hazard"], ["vent", "chimney", "hydrothermal", "black-smoker"]),
    ("prop_crate_stack", prop_crate_stack, 0.01, "prop", "Crate Stack", "Three wooden crates with iron straps stacked and tilted, plus a banded barrel. Shipwreck and supply-cache dressing.", ["obstacle", "decoration"], ["crate", "barrel", "cargo", "shipwreck"]),
    ("prop_coral_fan", prop_coral_fan, 0.015, "prop", "Fan Coral", "Fan-shaped sea fan: a stem on a stone base fanning into eleven branches with glowing tips and three arcs of fine mesh. 3.2 m wide.", ["decoration"], ["coral", "sea-fan", "bioluminescent", "overgrowth"]),
]
