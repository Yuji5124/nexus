"""DEEP-SEA SUBMARINE の部品 (潜水艦の改造パーツ 20 点の形・一覧)。build_sub_parts.py が読む。

『甲殻類にも都合があります。』の GAME_SPEC にある潜水艦の成長 (耐圧船殻・エンジン・ソナー・照明・貨物室・作業アームなど) と、
ゲーム側の潜水艦の全長 (14 m) に合わせた大きさ。デザインは NEXUS のオリジナルで、性能・価格・段階数は決めていない (見た目だけ)。
向き: 艦首が Blender の -Y (glTF の +Z)。外付けパーツは、艦に取り付ける点が原点で、外向きが +Z (glTF の +Y)。
船殻の区画は艦の軸 (Y) が長手方向で、原点は区画の中心。
"""
import math
import random

import bmesh
from mathutils import Matrix, Vector, Euler

PI = math.pi
KEYS = ("hull", "dark", "accent", "glow", "warm", "glass", "brass", "shell", "gold", "rubber")


def extend_shape(Shape):
    class Shape2(Shape):
        def __init__(self):
            self.bm = {k: bmesh.new() for k in KEYS}

        def limb(self, p1, p2, r=0.08, r2=None, seg=6, key="hull"):
            a, b = Vector(p1), Vector(p2)
            d = b - a
            rot = d.to_track_quat("Z", "Y").to_euler()
            self.cyl((a + b) / 2, (r, r if r2 is None else r2), d.length, seg, tuple(rot), key)

        def cylY(self, loc=(0, 0, 0), r=(1, 1), h=1, seg=16, key="hull"):
            """艦の軸 (Y) に沿った円柱。r=(後ろ側 (+Y) の半径, 前側 (-Y) の半径)。"""
            self.cyl(loc, r, h, seg, rot=(PI / 2, 0, 0), key=key)

        def ringY(self, loc=(0, 0, 0), R=1.0, r=0.05, seg=28, key="hull", sub=5):
            self.ring(loc, R, r, seg, rot=(PI / 2, 0, 0), key=key, sub=sub)

    return Shape2


# ---------------------------------------------------------------- 船殻 (耐圧)
def _hull_section(s, R, length, ribs, rib_r, plates, glow):
    s.cylY((0, 0, 0), (R, R), length, 24, "hull")
    n = ribs
    for i in range(n):
        y = -length / 2 + length * (i + 0.5) / n
        s.ringY((0, y, 0), R, rib_r, 28, "hull", 5)
    for sy in (-length / 2, length / 2):
        s.ringY((0, sy, 0), R + 0.02, rib_r * 1.25, 28, "dark", 5)
    s.cylY((0, 0, 0), (R * 1.003, R * 1.003), 0.16, 24, "accent")
    for k in range(plates):
        a = k * 2 * PI / plates
        s.box((math.cos(a) * (R + 0.04), 0, math.sin(a) * (R + 0.04)), (0.5, length * 0.56, 0.06), rot=(0, -a + PI / 2, 0), key="dark")
    if glow:
        s.cylY((0, 0, 0), (R * 1.01, R * 1.01), 0.04, 24, "glow")
    s.box((0, 0, R + 0.02), (0.8, 0.8, 0.08), key="dark")


def sub_hull_mk1(s):
    """耐圧船殻 第1段。細めのリブと、うすい補強板。"""
    _hull_section(s, 2.0, 4.0, 3, 0.08, 0, False)


def sub_hull_mk2(s):
    """耐圧船殻 第2段。リブが太くなり、外側の補強板が付く。"""
    _hull_section(s, 2.1, 4.0, 4, 0.12, 8, False)


def sub_hull_mk3(s):
    """耐圧船殻 第3段。厚い二重リブと全周の補強板。縫い目が光る。"""
    _hull_section(s, 2.25, 4.0, 5, 0.17, 12, True)
    for k in range(6):
        a = k * PI / 3
        s.box((math.cos(a) * 2.38, -1.2, math.sin(a) * 2.38), (0.22, 0.22, 0.14), rot=(0, -a, 0), key="brass")
        s.box((math.cos(a) * 2.38, 1.2, math.sin(a) * 2.38), (0.22, 0.22, 0.14), rot=(0, -a, 0), key="brass")


def sub_shell_plating(s):
    """殻の補強。紫の巻き殻の板と金の縁が、船殻の外側を覆う (ハンスの殻を提供する場面の見た目案)。"""
    R = 2.1
    s.cylY((0, 0, 0), (R, R), 3.6, 24, "hull")
    for k in range(10):
        a = k * 2 * PI / 10
        s.box((math.cos(a) * (R + 0.14), 0, math.sin(a) * (R + 0.14)), (0.9, 3.2, 0.22), rot=(0, -a + PI / 2, 0), key="shell")
        s.box((math.cos(a) * (R + 0.27), 0, math.sin(a) * (R + 0.27)), (0.9, 3.3, 0.04), rot=(0, -a + PI / 2, 0), key="gold")
    for y in (-1.6, 0.0, 1.6):
        s.ringY((0, y, 0), R + 0.28, 0.06, 28, "gold", 4)
    pts = []
    for i in range(16):
        t = i / 15
        ang = 4.4 * PI * t
        rad = 0.9 * (1 - 0.86 * t)
        pts.append((rad * math.cos(ang), rad * math.sin(ang), t))
    for i, (px, py, t) in enumerate(pts):
        sc = 0.34 * (1 - 0.8 * t)
        s.sphere((px, 0.0, R + 0.55 + py), (sc, sc * 0.8, sc), 8, "shell" if i % 2 == 0 else "gold")


# ---------------------------------------------------------------- 推進・浮力・電源
def _propeller(s, loc, R, blades, hub_r, key="dark"):
    x, y, z = loc
    s.sphere((x, y, z), (hub_r, hub_r * 1.5, hub_r), 8, "accent")
    s.cone((x, y + hub_r * 1.4, z), r=hub_r * 0.8, h=hub_r * 1.2, seg=8, rot=(-PI / 2, 0, 0), key="accent")
    for k in range(blades):
        a = k * 2 * PI / blades
        s.box((x + math.cos(a) * R * 0.5, y, z + math.sin(a) * R * 0.5), (R * 0.86, 0.05, R * 0.3), rot=(0.55, 0, a), key=key)


def _duct(s, z, R, y0, y1, struts, key="hull"):
    """プロペラを囲む環 (ダクト)。前後の輪を細い桁でつなぐ。"""
    s.ringY((0, y0, z), R, R * 0.12, 26, key, 5)
    s.ringY((0, y1, z), R * 0.93, R * 0.1, 26, key, 5)
    for k in range(struts):
        a = k * 2 * PI / struts
        s.limb((math.cos(a) * R, y0, z + math.sin(a) * R), (math.cos(a) * R * 0.93, y1, z + math.sin(a) * R * 0.93), R * 0.04, key="dark")


def sub_thruster_small(s):
    """小型スラスター。環の中に 4 枚羽。後ろにモーター、下に取り付け台。原点は取り付け点。"""
    s.box((0, 0.3, 0.1), (0.7, 0.9, 0.2), key="dark")
    s.limb((0, 0.5, 0.1), (0, 0.9, 0.95), 0.08, key="dark")
    _duct(s, 0.95, 0.7, -0.15, 0.7, 6)
    s.ringY((0, -0.18, 0.95), 0.71, 0.03, 26, "accent", 4)
    s.cylY((0, 1.2, 0.95), (0.34, 0.2), 0.9, 12, "dark")
    for k in range(3):
        a = k * 2 * PI / 3 + 0.5
        s.limb((0, 0.85, 0.95), (math.cos(a) * 0.62, 0.55, 0.95 + math.sin(a) * 0.62), 0.03, key="dark")
    _propeller(s, (0, 0.2, 0.95), 0.58, 4, 0.14)


def sub_thruster_large(s):
    """大型エンジン。環の中に 5 枚羽、後ろに太い本体と光る噴出口。取り付け台つき。"""
    s.box((0, 0.7, 0.15), (1.4, 1.8, 0.3), key="dark")
    for sx in (-1, 1):
        s.limb((sx * 0.4, 0.7, 0.3), (sx * 0.55, 1.2, 1.5), 0.1, key="dark")
    _duct(s, 1.55, 1.15, -0.6, 0.9, 8)
    s.ringY((0, -0.62, 1.55), 1.17, 0.045, 28, "accent", 4)
    s.ringY((0, 0.2, 1.55), 1.14, 0.04, 28, "brass", 4)
    s.cylY((0, 1.9, 1.55), (0.75, 0.5), 1.8, 18, "hull")
    s.cylY((0, 3.0, 1.55), (0.52, 0.74), 0.5, 18, "dark")
    s.ringY((0, 3.28, 1.55), 0.5, 0.06, 22, "glow", 4)
    for k in range(5):
        a = k * 2 * PI / 5 + 0.3
        s.limb((0, 1.1, 1.55), (math.cos(a) * 1.02, 0.6, 1.55 + math.sin(a) * 1.02), 0.045, key="dark")
    _propeller(s, (0, 0.1, 1.55), 1.0, 5, 0.22)


def sub_ballast_tank(s):
    """バラストタンク。横に並んだ二本の筒、バンド、バルブのハンドル。"""
    s.box((0, 0, 0.06), (2.2, 3.0, 0.12), key="dark")
    for sx in (-0.55, 0.55):
        s.cylY((sx, 0, 0.62), (0.5, 0.5), 2.6, 18, "hull")
        s.sphere((sx, 1.3, 0.62), (0.5, 0.3, 0.5), 12, "hull")
        s.sphere((sx, -1.3, 0.62), (0.5, 0.3, 0.5), 12, "hull")
        for y in (-0.8, 0.0, 0.8):
            s.ringY((sx, y, 0.62), 0.5, 0.05, 20, "accent", 4)
    s.limb((0, 0, 0.62), (0, 0, 1.45), 0.07, key="brass")
    s.ring((0, 0, 1.5), 0.3, 0.05, 20, key="accent", sub=4)
    for k in range(4):
        a = k * PI / 2
        s.limb((0, 0, 1.5), (math.cos(a) * 0.28, math.sin(a) * 0.28, 1.5), 0.025, key="brass")
    s.limb((0.55, 1.4, 0.95), (0.0, 0.0, 1.3), 0.04, key="rubber")


def sub_battery_pack(s):
    """バッテリー。4 つのセルを枠に収め、残量の帯が光る。"""
    s.box((0, 0, 0.1), (2.4, 1.6, 0.2), key="dark")
    for ix in range(4):
        x = -0.9 + ix * 0.6
        s.box((x, 0, 0.7), (0.5, 1.4, 1.0), key="hull")
        s.box((x, -0.71, 0.75), (0.34, 0.03, 0.7), key="glow")
        s.cyl((x, 0.3, 1.2), (0.09, 0.09), 0.1, 8, base=True, key="brass")
    s.box((0, 0, 1.28), (2.5, 0.12, 0.1), key="dark")
    s.box((0, 0.7, 1.28), (2.5, 0.1, 0.1), key="dark")
    s.limb((0.9, 0.5, 1.25), (1.5, 0.9, 0.6), 0.05, key="rubber")
    s.box((1.5, 0.9, 0.5), (0.2, 0.2, 0.2), key="accent")


# ---------------------------------------------------------------- 探知・照明
def sub_sonar_dish(s):
    """ソナーのパラボラ。旋回台とマストの上で、皿が少し前を向く。"""
    s.cyl((0, 0, 0), (0.5, 0.35), 0.35, 12, base=True, key="dark")
    s.cyl((0, 0, 0.35), (0.12, 0.12), 0.9, 8, base=True, key="hull")
    s.sphere((0, 0, 1.3), (0.22, 0.22, 0.22), 8, "accent")
    s.cyl((0, -0.25, 1.5), (0.18, 1.0), 0.5, 20, rot=(-PI / 2 + 0.25, 0, 0), key="hull")
    s.cyl((0, -0.52, 1.56), (0.12, 0.92), 0.06, 20, rot=(-PI / 2 + 0.25, 0, 0), key="glow")
    s.limb((0, -0.1, 1.5), (0, -0.75, 1.62), 0.025, key="brass")
    s.sphere((0, -0.78, 1.64), (0.07, 0.07, 0.07), 6, "glow")
    for k in range(3):
        a = k * 2 * PI / 3 + 0.5
        s.limb((0, -0.2, 1.5), (math.cos(a) * 0.8, -0.45, 1.5 + math.sin(a) * 0.8), 0.02, key="dark")


def sub_sonar_array(s):
    """曲面のハイドロフォン列 (3 × 5 個)。艦の側面に貼る板。"""
    s.box((0, 0, 0.06), (3.0, 1.8, 0.12), key="dark")
    s.box((0, 0, 0.14), (3.0, 1.8, 0.04), key="hull", rot=(0, 0, 0))
    for ix in range(5):
        for iy in range(3):
            x, y = -1.2 + ix * 0.6, -0.55 + iy * 0.55
            s.cyl((x, y, 0.12), (0.2, 0.17), 0.14, 10, base=True, key="rubber")
            s.sphere((x, y, 0.28), (0.07, 0.07, 0.05), 6, "glow" if (ix + iy) % 2 == 0 else "accent")
    for sx in (-1, 1):
        for sy in (-1, 1):
            s.cyl((sx * 1.4, sy * 0.8, 0.12), (0.07, 0.07), 0.1, 6, base=True, key="brass")


def sub_headlamp(s):
    """前照灯。反射板とレンズ、保護の格子。原点は取り付け点。"""
    s.cyl((0, 0, 0), (0.3, 0.22), 0.25, 10, base=True, key="dark")
    s.cyl((0, -0.2, 0.55), (0.45, 0.38), 0.5, 18, rot=(PI / 2, 0, 0), key="hull")
    s.ringY((0, -0.5, 0.55), 0.45, 0.05, 20, "accent", 4)
    s.cone((0, 0.0, 0.55), r=0.38, h=0.45, seg=16, rot=(-PI / 2, 0, 0), key="dark")
    s.sphere((0, -0.2, 0.55), (0.18, 0.18, 0.18), 10, "warm")
    s.cylY((0, -0.46, 0.55), (0.4, 0.4), 0.05, 18, "glass")
    for k in range(4):
        a = k * PI / 4
        s.limb((math.cos(a) * 0.46, -0.55, 0.55 + math.sin(a) * 0.46), (-math.cos(a) * 0.46, -0.55, 0.55 - math.sin(a) * 0.46), 0.012, key="dark")
    s.ringY((0, -0.55, 0.55), 0.46, 0.015, 18, "dark", 4)


def sub_floodlight_bar(s):
    """作業用の投光灯バー (2.8 m)。6 つの灯りが並ぶ。"""
    s.box((0, 0, 0.1), (3.0, 0.3, 0.2), key="dark")
    s.box((0, 0, 0.3), (2.9, 0.5, 0.25), key="hull")
    for k in range(6):
        x = -1.25 + k * 0.5
        s.box((x, -0.27, 0.3), (0.38, 0.04, 0.18), key="dark")
        s.box((x, -0.3, 0.3), (0.32, 0.03, 0.12), key="warm")
    for sx in (-1, 1):
        s.box((sx * 1.5, 0, 0.3), (0.12, 0.55, 0.3), key="accent")
        s.limb((sx * 1.2, 0.1, 0.0), (sx * 1.2, 0.1, -0.2), 0.04, key="dark")


# ---------------------------------------------------------------- 作業・貨物・テザー
def sub_manipulator_arm(s):
    """作業アーム。旋回台・上腕・肘・前腕・手首・2 本爪 (休めの姿勢で約 4 m)。"""
    s.cyl((0, 0, 0), (0.6, 0.5), 0.35, 14, base=True, key="dark")
    s.cyl((0, 0, 0.35), (0.38, 0.32), 0.4, 14, base=True, key="hull")
    s.sphere((0, 0, 0.9), (0.3, 0.3, 0.3), 10, "accent")
    s.limb((0, 0, 0.9), (0.0, -1.6, 1.7), 0.17, 0.14, 8, "hull")
    s.ringY((0.0, -0.5, 1.22), 0.2, 0.03, 12, "accent", 4)
    s.sphere((0, -1.6, 1.7), (0.24, 0.24, 0.24), 10, "accent")
    s.limb((0, -1.6, 1.7), (0.0, -3.0, 1.05), 0.13, 0.1, 8, "hull")
    s.sphere((0, -3.0, 1.05), (0.15, 0.15, 0.15), 8, "dark")
    for sx in (-1, 1):
        s.limb((sx * 0.06, -3.0, 1.05), (sx * 0.17, -3.5, 0.9), 0.06, 0.04, 6, "dark")
        s.limb((sx * 0.17, -3.5, 0.9), (sx * 0.06, -3.82, 0.72), 0.045, 0.02, 5, "brass")
    s.limb((0.0, -1.0, 1.2), (0.0, -1.5, 1.2), 0.04, key="rubber")


def sub_tether_winch(s):
    """テザーのウインチ。巻き取りドラム・フランジ・ケーブルの巻き・案内ローラー・フック。"""
    s.box((0, 0, 0.1), (2.2, 1.6, 0.2), key="dark")
    for sx in (-0.7, 0.7):
        s.box((sx, 0, 0.7), (0.12, 1.5, 1.0), key="hull")
    s.cyl((0, 0, 0.9), (0.55, 0.55), 1.3, 16, rot=(0, PI / 2, 0), key="dark")
    for sx in (-0.66, 0.66):
        s.cyl((sx, 0, 0.9), (0.9, 0.9), 0.08, 18, rot=(0, PI / 2, 0), key="hull")
    for i in range(8):
        s.ring((-0.55 + i * 0.16, 0, 0.9), 0.62, 0.04, 20, rot=(0, PI / 2, 0), key="brass", sub=4)
    s.box((0.9, 0.5, 0.45), (0.5, 0.5, 0.5), key="accent")
    s.limb((0.0, -0.8, 1.2), (0.0, -1.5, 0.5), 0.05, key="dark")
    s.ring((0, -1.6, 0.45), 0.18, 0.03, 14, rot=(0, PI / 2, 0), key="brass", sub=4)
    s.limb((0.0, -0.62, 1.4), (0.0, -1.5, 0.65), 0.018, key="brass")
    s.ring((0, -1.6, 0.2), 0.1, 0.03, 12, rot=(PI / 2, 0, 0), key="brass", sub=4)
    s.cone((0.0, -1.6, 0.05), r=0.07, h=0.18, seg=5, rot=(PI, 0, 0), key="brass", base=True)


def sub_cargo_pod(s):
    """貨物ポッド。両端が丸い筒に、扉・バンド・取り付けのレール。"""
    s.box((0, 0, 0.1), (3.2, 1.1, 0.2), key="dark")
    s.cylY((0, 0, 0.95), (0.85, 0.85), 2.6, 20, "hull")
    for sy in (-1.3, 1.3):
        s.sphere((0, sy, 0.95), (0.85, 0.5, 0.85), 14, "hull")
    for y in (-0.9, 0.0, 0.9):
        s.ringY((0, y, 0.95), 0.86, 0.045, 22, "accent", 4)
    s.box((0, 0, 1.78), (0.9, 1.4, 0.06), key="dark")
    s.box((0, 0.02, 1.82), (0.14, 0.9, 0.08), key="brass")
    s.box((0.9, 0.0, 0.95), (0.06, 1.4, 0.5), key="dark")
    s.sphere((0, -1.62, 0.95), (0.1, 0.1, 0.1), 6, "glow")
    for sx in (-1, 1):
        s.box((sx * 0.7, 0, 0.35), (0.12, 2.8, 0.2), key="dark")


def sub_sample_rack(s):
    """標本ラック。6 本のガラス管に、光る内容物と留め具。"""
    s.box((0, 0, 0.08), (2.0, 1.0, 0.16), key="dark")
    s.box((0, 0, 1.5), (2.0, 1.0, 0.12), key="hull")
    for sx in (-1, 1):
        for sy in (-1, 1):
            s.cyl((sx * 0.95, sy * 0.45, 0.0), (0.05, 0.05), 1.5, 6, base=True, key="dark")
    for ix in range(3):
        for iy in range(2):
            x, y = -0.6 + ix * 0.6, -0.25 + iy * 0.5
            s.cyl((x, y, 0.2), (0.17, 0.17), 1.2, 10, base=True, key="glass")
            s.cyl((x, y, 0.2), (0.12, 0.12), 0.35 + 0.18 * ((ix + iy * 3) % 4), 8, base=True, key=("glow", "warm", "shell")[(ix + iy) % 3])
            s.cyl((x, y, 1.42), (0.18, 0.18), 0.1, 10, base=True, key="rubber")
    s.box((0, 0.51, 0.8), (1.8, 0.04, 0.3), key="accent")


# ---------------------------------------------------------------- 乗員・通信・補修
def sub_hatch_module(s):
    """出入り口のハッチ塔。ハンドル付きの丸い蓋、手すり、足がかり、ランプ。"""
    s.cyl((0, 0, 0), (1.0, 0.85), 0.4, 20, base=True, key="hull")
    s.cyl((0, 0, 0.4), (0.78, 0.7), 1.0, 20, base=True, key="hull")
    s.ring((0, 0, 1.38), 0.72, 0.07, 24, key="accent", sub=4)
    s.cyl((0, 0, 1.42), (0.62, 0.6), 0.1, 20, base=True, key="dark")
    s.ring((0, 0, 1.56), 0.28, 0.04, 16, key="brass", sub=4)
    for k in range(4):
        a = k * PI / 2
        s.limb((0, 0, 1.56), (math.cos(a) * 0.26, math.sin(a) * 0.26, 1.56), 0.02, key="brass")
    for sx in (-1, 1):
        s.arc((sx * 0.7, 0, 1.44), R=0.55, w=0.05, d=0.05, a0=0.0, a1=PI, seg=8, key="brass", rot=(0, 0, PI / 2))
    for k in range(4):
        s.box((0, -0.78, 0.5 + k * 0.28), (0.4, 0.05, 0.05), key="brass")
    s.sphere((0.55, 0.3, 1.5), (0.1, 0.1, 0.1), 8, "warm")


def sub_dome_viewport(s):
    """ドーム型の窓。ガラスの半球、枠、ボルト、内側のほのかな灯り。"""
    s.cyl((0, 0, 0), (1.3, 1.25), 0.3, 24, base=True, key="hull")
    s.ring((0, 0, 0.32), 1.15, 0.1, 28, key="dark", sub=5)
    s.sphere((0, 0, 0.3), (1.1, 1.1, 0.85), 18, "glass")
    s.sphere((0, 0, 0.35), (0.3, 0.3, 0.2), 10, "warm")
    for k in range(12):
        a = k * PI / 6
        s.cyl((math.cos(a) * 1.15, math.sin(a) * 1.15, 0.38), (0.06, 0.06), 0.1, 6, base=True, key="brass")
    s.arc((0, 0, 0.3), R=1.1, w=0.04, d=0.05, a0=0.0, a1=PI, seg=14, key="dark")
    s.arc((0, 0, 0.3), R=1.1, w=0.04, d=0.05, a0=0.0, a1=PI, seg=14, key="dark", rot=(0, 0, PI / 2))


def sub_antenna_mast(s):
    """通信マスト。アンテナ、小型の皿、信号リング、先端の灯り。"""
    s.cyl((0, 0, 0), (0.45, 0.3), 0.3, 10, base=True, key="dark")
    s.cyl((0, 0, 0.3), (0.1, 0.07), 3.2, 8, base=True, key="hull")
    for z, r in ((1.2, 0.35), (2.0, 0.28), (2.8, 0.22)):
        s.ring((0, 0, z), r, 0.025, 16, key="glow", sub=4)
    for sx in (-1, 1):
        s.limb((0, 0, 2.3), (sx * 0.6, 0, 2.5), 0.025, key="brass")
        s.box((sx * 0.62, 0, 2.55), (0.04, 0.4, 0.4), key="hull")
    s.cyl((0, -0.1, 1.7), (0.0, 0.3), 0.18, 12, rot=(-PI / 2, 0, 0), key="hull")
    s.limb((0, 0, 3.5), (0, 0, 4.0), 0.012, key="brass")
    s.sphere((0, 0, 4.05), (0.09, 0.09, 0.09), 8, "accent")


def sub_repair_kit(s):
    """修理キット。取っ手付きの箱に、開いたトレーと工具 (レンチ・溶接の補修板・ボルト)。"""
    s.box((0, 0, 0), (1.6, 0.9, 0.6), base=True, key="accent")
    s.box((0, 0, 0.6), (1.62, 0.92, 0.08), key="dark")
    s.arc((0, 0, 0.62), R=0.38, w=0.05, d=0.06, a0=0.0, a1=PI, seg=10, key="brass")
    for sx in (-1, 1):
        s.box((sx * 0.5, 0.46, 0.3), (0.16, 0.05, 0.16), key="brass")
    s.box((0, -0.46, 0.35), (0.5, 0.04, 0.2), key="hull")
    s.box((0, -0.472, 0.35), (0.14, 0.02, 0.1), key="glow")
    s.box((0.9, 0.0, 0.05), (0.1, 0.9, 0.1), key="dark")
    s.limb((1.25, -0.2, 0.06), (1.9, 0.25, 0.06), 0.05, key="hull")
    s.ring((1.2, -0.25, 0.06), 0.11, 0.04, 12, key="hull", sub=4)
    s.ring((1.95, 0.3, 0.06), 0.09, 0.04, 12, key="hull", sub=4)
    s.box((1.4, 0.6, 0.0), (0.5, 0.4, 0.04), base=True, key="shell")
    for i in range(3):
        s.cyl((1.9 + i * 0.15, -0.5, 0.0), (0.05, 0.05), 0.07, 6, base=True, key="brass")


MODELS = [
    # id, 関数, 風化 (使わない), 区分, 名前, 説明, 用途, タグ (最初のタグ = 系統)
    ("sub_hull_mk1", sub_hull_mk1, 0.0, "hull", "Pressure Hull Section Mk1", "First-stage pressure hull section, 4 m long and 4 m across: thin ribs, end flanges, an orange band and a hatch pad. Axis along the sub (Y in glTF is up, the long axis is Z).", ["upgrade"], ["hull", "pressure", "tier1", "section"]),
    ("sub_hull_mk2", sub_hull_mk2, 0.0, "hull", "Pressure Hull Section Mk2", "Second-stage pressure hull section: thicker ribs plus eight outer armour plates on a 4.2 m diameter shell.", ["upgrade"], ["hull", "pressure", "tier2", "section"]),
    ("sub_hull_mk3", sub_hull_mk3, 0.0, "hull", "Pressure Hull Section Mk3", "Third-stage pressure hull section: heavy ribs, twelve armour plates, brass bolt blocks and a glowing seam on a 4.5 m diameter shell.", ["upgrade"], ["hull", "pressure", "tier3", "section"]),
    ("sub_shell_plating", sub_shell_plating, 0.0, "hull", "Shell Reinforcement Plating", "Hull section wrapped in ten purple shell plates with gold edging and a gold-and-purple spiral shell on top: a look for the shell the hermit crab donates to the sub.", ["upgrade", "story"], ["hull", "shell", "reinforcement", "purple-gold"]),
    ("sub_thruster_small", sub_thruster_small, 0.0, "propulsion", "Small Thruster", "Ducted four-blade thruster on a bracket with a rear motor. Thrust axis along the sub; mount point at the origin.", ["upgrade"], ["thruster", "propeller", "engine", "small"]),
    ("sub_thruster_large", sub_thruster_large, 0.0, "propulsion", "Main Engine", "Large engine pod: a ducted five-blade propeller, a thick motor body with a glowing exhaust ring, and a mounting plate with two struts. About 4 m long.", ["upgrade"], ["thruster", "engine", "propeller", "large"]),
    ("sub_ballast_tank", sub_ballast_tank, 0.0, "propulsion", "Ballast Tank", "Twin horizontal tanks with domed ends, orange bands and a brass valve wheel on a base plate.", ["upgrade"], ["ballast", "tank", "buoyancy", "valve"]),
    ("sub_battery_pack", sub_battery_pack, 0.0, "propulsion", "Battery Pack", "Four battery cells in a frame with glowing charge strips, brass terminals and a cable.", ["upgrade"], ["battery", "power", "cells"]),
    ("sub_sonar_dish", sub_sonar_dish, 0.0, "sensor", "Sonar Dish", "Parabolic sonar dish with a glowing face, a feed horn and three struts on a rotating mast.", ["upgrade"], ["sonar", "dish", "sensor", "mast"]),
    ("sub_sonar_array", sub_sonar_array, 0.0, "sensor", "Hydrophone Array", "Flat 3 by 5 array of rubber-ringed transducers with glowing and orange dots on a 3 m plate.", ["upgrade"], ["sonar", "array", "hydrophone", "panel"]),
    ("sub_headlamp", sub_headlamp, 0.0, "light", "Headlamp", "Round headlamp with a reflector cone, glowing bulb, glass lens and a protective grille, on a short bracket.", ["upgrade"], ["lamp", "headlight", "light", "lens"]),
    ("sub_floodlight_bar", sub_floodlight_bar, 0.0, "light", "Floodlight Bar", "Work-light bar 3 m wide with six warm lamps and orange end caps.", ["upgrade"], ["lamp", "floodlight", "light", "bar"]),
    ("sub_manipulator_arm", sub_manipulator_arm, 0.0, "tool", "Manipulator Arm", "Three-segment work arm with a swivel base, orange joints and a two-finger brass claw. Rest pose reaches about 4 m forward.", ["upgrade", "tool"], ["arm", "manipulator", "claw", "work"]),
    ("sub_tether_winch", sub_tether_winch, 0.0, "tool", "Tether Winch", "Winch with a flanged drum wound in brass cable, a guide arm, a hook and an orange motor housing.", ["upgrade", "tool"], ["winch", "tether", "cable", "hook"]),
    ("sub_cargo_pod", sub_cargo_pod, 0.0, "tool", "Cargo Pod", "Capsule cargo pod 3.2 m long with a top hatch, three orange bands, a side door and mounting rails.", ["upgrade", "storage"], ["cargo", "pod", "storage", "capsule"]),
    ("sub_sample_rack", sub_sample_rack, 0.0, "tool", "Sample Rack", "Rack of six glass sample tubes with glowing contents (cyan, amber, purple) and rubber caps.", ["upgrade", "storage"], ["samples", "rack", "tubes", "storage"]),
    ("sub_hatch_module", sub_hatch_module, 0.0, "crew", "Hatch Tower", "Round hatch tower 2 m tall with a wheel-handled lid, handrails, a ladder and a warm lamp.", ["upgrade", "entrance"], ["hatch", "entrance", "ladder", "tower"]),
    ("sub_dome_viewport", sub_dome_viewport, 0.0, "crew", "Dome Viewport", "Glass dome window 2.6 m across with a framing ring, twelve bolts, a cross frame and a soft interior lamp.", ["upgrade", "window"], ["window", "dome", "viewport", "glass"]),
    ("sub_antenna_mast", sub_antenna_mast, 0.0, "crew", "Antenna Mast", "4 m communications mast with three glowing rings, small panel antennas, a dish and an orange tip light.", ["upgrade"], ["antenna", "mast", "comms", "radio"]),
    ("sub_repair_kit", sub_repair_kit, 0.0, "crew", "Repair Kit", "Orange toolbox with a handle, open side tray and loose tools: a wrench, a purple patch plate and bolts. Fits a post-battle repair scene.", ["pickup", "story"], ["repair", "toolbox", "wrench", "patch"]),
]
