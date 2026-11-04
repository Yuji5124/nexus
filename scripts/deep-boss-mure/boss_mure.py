"""誰もいない王 (ムレ) の配置ジェネレータ。水深4,500m のボスの「形」だけを決める (純 Python。Blender なしで動く)。

コンセプト (ユーザーのコンセプトアート指示): 数万匹の小魚が集まって、存在しない王の姿をつくる。
  - 全長 200 m 超。鳳凰・マンタ・古代魚・王冠を融合した輪郭。大きな翼状のヒレ、長く流れる尾、頭上に魚群の王冠の輪。
  - 肉体は存在しない。すべてが独立した小魚の集合で、密度が頭・ヒレ・翼・尾・王冠の形をつくる。
  - 姿の中心部は完全に空洞 (背後の海や遺跡が見える)。指揮者や中心個体はいない。
  - 脱皮: 輪郭から小魚が剥がれて別の位置へ移り、古い輪郭を脱いで新しい形に変わる (破壊ではなく変化)。
  - 大きな牙・筋肉・爪・角は付けない。
ここで決めるのは見た目 (輪郭と配置) だけ。HP・攻撃・当たり判定・弱点・撃破条件は決めていない。

座標 (ボスのローカル): Blender の座標 (X 右、Y 後ろ、Z 上、前は -Y)。bin に書き出すときは glTF / Three.js の座標 (X 右、Y 上、前は +Z) へ
(x, y, z) -> (x, z, -y) と変換する。1 unit = 1 m。
"""
import math
import random
import struct
import json

PARTS = ("head", "crown_ring", "crown_spikes", "neck_chest", "wing_l", "wing_r", "tail", "moult")
PID = {n: i for i, n in enumerate(PARTS)}
COUNTS = {"head": 3000, "crown_ring": 1000, "crown_spikes": 800, "neck_chest": 6000, "wing_l": 9000, "wing_r": 9000, "tail": 6000, "moult": 5200}
FISH_LEN = 1.6          # 小魚 1 匹の基準の全長 (m)。ボスが 200 m を超えるので、1 匹ずつが見分けられる大きさ
COLORS = ("silver", "pearl", "gold", "pink")


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _mul(a, k):
    return (a[0] * k, a[1] * k, a[2] * k)


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _norm(a):
    l = math.sqrt(_dot(a, a)) or 1.0
    return (a[0] / l, a[1] / l, a[2] / l)


def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u ** 3 * p0[i] + 3 * u * u * t * p1[i] + 3 * u * t * t * p2[i] + t ** 3 * p3[i] for i in range(3))


def bez_d(p0, p1, p2, p3, t):
    u = 1 - t
    return _norm(tuple(3 * u * u * (p1[i] - p0[i]) + 6 * u * t * (p2[i] - p1[i]) + 3 * t * t * (p3[i] - p2[i]) for i in range(3)))


def frame(tangent, ref=(0, 0, 1)):
    side = _cross(tangent, ref)
    if _dot(side, side) < 1e-6:
        side = _cross(tangent, (1, 0, 0))
    side = _norm(side)
    up = _norm(_cross(side, tangent))
    return side, up


# ---------------------------------------------------------------- 骨組み (制御点)
HEAD_C = (0.0, -92.0, 76.0)
CROWN_C = (0.0, -88.0, 98.0)
NECK = ((0.0, -80.0, 68.0), (0.0, -62.0, 38.0), (0.0, -30.0, 34.0), (0.0, 0.0, 50.0))
SHOULDER = 22.0
HIP = (0.0, 6.0, 50.0)


def wing_feathers(sign):
    """翼の 9 本の羽 (制御点 4 つ + 幅の最大)。前縁 (上・外) から後縁 (下・後ろ) へ扇状に並ぶ。"""
    out = []
    s0 = (sign * 9.0, -24.0, 54.0)
    for k in range(9):
        t = k / 8
        L = 88 + 28 * math.sin(math.pi * (0.15 + 0.75 * t))
        d = _norm((sign * (1.0 - 0.38 * t), 0.18 + 1.05 * t, 0.62 - 1.45 * t))
        end = _add(s0, _mul(d, L))
        c1 = _add(s0, _add(_mul(d, L * 0.33), (0, -6.0 - 8 * t, 14.0 - 10 * t)))
        c2 = _add(s0, _add(_mul(d, L * 0.68), (0, 8.0 + 10 * t, 10.0 - 22 * t)))
        out.append((s0, c1, c2, end, 5.0 + 3.5 * math.sin(math.pi * t)))
    return out


def tail_ribbons():
    out = []
    for k, (side, lift, w) in enumerate(((0.0, 8.0, 10.0), (-14.0, -6.0, 8.0), (14.0, -10.0, 8.0))):
        p0 = _add(HIP, (side * 0.15, 0.0, 0.0))
        p1 = _add(HIP, (side * 0.7, 36.0, 14.0 + lift))
        p2 = _add(HIP, (side * 1.5 - side * 0.5, 84.0, -8.0 + lift * 1.5))
        p3 = _add(HIP, (side * 2.0, 138.0, -26.0 + lift * 2.0))
        out.append((p0, p1, p2, p3, w))
    return out


# ---------------------------------------------------------------- 標本の取り方
def _rec(pos, d, u, part, rnd, color_bias=0.0):
    d = _norm(d)
    r = rnd.random()
    color = 0 if r < 0.45 else 1 if r < 0.78 else 2 if r < 0.93 + color_bias else 3
    return [pos[0], pos[1], pos[2], d[0], d[1], d[2], u, float(PID[part]), rnd.random(), rnd.uniform(0.8, 1.25), float(color)]


def _ribbon(rnd, pts, width_fn, thick, n, part, flow=1.0, shape=1.0, color_bias=0.0):
    out = []
    for _ in range(n):
        u = rnd.random() ** shape
        p = bez(*pts, u)
        tg = bez_d(*pts, u)
        side, up = frame(tg)
        w = width_fn(u)
        v = rnd.uniform(-1, 1) * w / 2
        z = rnd.uniform(-1, 1) * thick / 2
        pos = _add(p, _add(_mul(side, v), _mul(up, z)))
        d = _add(_mul(tg, flow), (rnd.gauss(0, 0.12), rnd.gauss(0, 0.12), rnd.gauss(0, 0.12)))
        out.append(_rec(pos, d, u, part, rnd, color_bias))
    return out


def _tube(rnd, pts, radius_fn, shell, n, part):
    out = []
    for _ in range(n):
        u = rnd.random()
        p = bez(*pts, u)
        tg = bez_d(*pts, u)
        n1, n2 = frame(tg, (1, 0, 0))
        th = rnd.uniform(0, 2 * math.pi)
        r = radius_fn(u) + rnd.uniform(0, shell)
        radial = _add(_mul(n1, math.cos(th)), _mul(n2, math.sin(th)))
        pos = _add(p, _mul(radial, r))
        swirl = _add(_mul(n1, -math.sin(th)), _mul(n2, math.cos(th)))
        d = _add(_mul(tg, -1.0), _mul(swirl, 0.6))  # 尾から頭へ向かう流れ
        out.append(_rec(pos, d, u, part, rnd))
    return out


def _outline(rnd, pts, radius_fn, n, part):
    """首・胸: 背中の線と腹の線の 2 本の帯だけ。間は空洞 (肉体が無いので、向こうの海が見える)。"""
    out = []
    for k in range(n):
        u = rnd.random()
        p = bez(*pts, u)
        tg = bez_d(*pts, u)
        sgn = 1.0 if k % 2 == 0 else -1.0
        r = radius_fn(u)
        pos = (p[0] + rnd.gauss(0, 1.6), p[1] + rnd.gauss(0, 0.8), p[2] + sgn * r + rnd.gauss(0, 0.9))
        d = _add(_mul(tg, -1.0), (rnd.gauss(0, 0.12), rnd.gauss(0, 0.12), rnd.gauss(0, 0.12)))
        out.append(_rec(pos, d, u, part, rnd))
    return out


def _head(rnd, n):
    out = []
    ax, ay, az = 7.5, 17.0, 8.5
    eyes = [(sx * 6.0, HEAD_C[1] - 8.0, HEAD_C[2] + 2.0) for sx in (-1, 1)]
    while len(out) < n:
        v = _norm((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1)))
        taper = 1.0 - 0.55 * max(0.0, -v[1]) ** 1.5  # 前 (-Y) ほど細くして、古代魚の吻にする
        thick = 1.0 + rnd.uniform(0.0, 0.22)
        pos = (HEAD_C[0] + ax * v[0] * taper * thick, HEAD_C[1] + ay * v[1] * thick, HEAD_C[2] + az * v[2] * taper * thick)
        if any(math.dist(pos, e) < 2.6 for e in eyes):
            continue  # 目は空いた穴 (輪郭に小魚が避ける)
        swirl = _norm(_cross((0, 1, 0), v))
        out.append(_rec(pos, _add(_mul(swirl, 1.0), (0, -0.4, 0)), (v[1] + 1) / 2, "head", rnd))
    return out


def _crown(rnd, n_ring, n_spike):
    out = []
    R, tube = 9.5, 1.5
    tilt = 0.28  # 後ろへ傾ける
    for _ in range(n_ring):
        a = rnd.uniform(0, 2 * math.pi)
        base = (math.cos(a) * R, math.sin(a) * R * math.cos(tilt), math.sin(a) * R * math.sin(tilt))
        tg = _norm((-math.sin(a), math.cos(a) * math.cos(tilt), math.cos(a) * math.sin(tilt)))
        off = (rnd.gauss(0, tube * 0.5), rnd.gauss(0, tube * 0.5), rnd.gauss(0, tube * 0.5))
        pos = _add(_add(CROWN_C, base), off)
        out.append(_rec(pos, _add(tg, (0, 0, 0.0)), a / (2 * math.pi), "crown_ring", rnd, 0.05))
    for _ in range(n_spike):
        k = rnd.randrange(7)
        a = k * 2 * math.pi / 7 + math.pi / 7
        base = (math.cos(a) * R, math.sin(a) * R * math.cos(tilt), math.sin(a) * R * math.sin(tilt))
        up = _norm((math.cos(a) * 0.35, math.sin(a) * 0.35, 1.0))
        u = rnd.random() ** 0.8
        h = 4.0 + (11.0 if k % 2 == 0 else 7.0) * u
        pos = _add(_add(CROWN_C, base), _mul(up, h))
        spread = (1.0 - u) * 0.9
        pos = _add(pos, (rnd.gauss(0, spread), rnd.gauss(0, spread), 0.0))
        out.append(_rec(pos, up, u, "crown_spikes", rnd, 0.05))
    return out


def _moult(rnd, n, curves):
    """脱皮: 輪郭から剥がれた小魚が、少し離れた弧を描いて別の位置へ向かう。curves = 母体の曲線 (制御点 4 つ) の一覧。"""
    out = []
    for _ in range(n):
        pts = rnd.choice(curves)
        t0 = rnd.uniform(0.35, 0.95)
        a = bez(*pts, t0)
        tg = bez_d(*pts, t0)
        side, up = frame(tg)
        out_dir = _norm(_add(_mul(side, rnd.choice((-1, 1)) * rnd.uniform(0.6, 1.0)), _mul(up, rnd.uniform(-0.8, 0.8))))
        t1 = min(1.0, t0 + rnd.uniform(0.12, 0.3))
        b = bez(*pts, t1)
        reach = rnd.uniform(10.0, 28.0)
        ctrl = _add(_mul(_add(a, b), 0.5), _mul(out_dir, reach))
        u = rnd.random()
        p = _add(_add(_mul(a, (1 - u) ** 2), _mul(ctrl, 2 * u * (1 - u))), _mul(b, u * u))
        d = _norm(_add(_mul(_sub(ctrl, a), 2 * (1 - u)), _mul(_sub(b, ctrl), 2 * u)))
        p = _add(p, (rnd.gauss(0, 0.9), rnd.gauss(0, 0.9), rnd.gauss(0, 0.9)))
        out.append(_rec(p, d, u, "moult", rnd, 0.04))
    return out


def build(seed=7, scale=1.0):
    """戻り値: 小魚の記録のリスト (各 11 個の float: x y z dx dy dz u part phase size color。Blender 座標)。"""
    rnd = random.Random(seed)
    fish = []
    fish += _head(rnd, int(COUNTS["head"] * scale))
    fish += _crown(rnd, int(COUNTS["crown_ring"] * scale), int(COUNTS["crown_spikes"] * scale))
    fish += _outline(rnd, NECK, lambda u: 2.2 * (6.0 + 7.0 * math.sin(math.pi * min(1.0, u * 1.1)) ** 0.8 + 3.0 * u), int(COUNTS["neck_chest"] * scale), "neck_chest")
    curves = []
    for sign, part in ((-1, "wing_l"), (1, "wing_r")):
        feathers = wing_feathers(sign)
        per = int(COUNTS[part] * scale) // len(feathers)
        for (p0, p1, p2, p3, wmax) in feathers:
            curves.append((p0, p1, p2, p3))
            fish += _ribbon(rnd, (p0, p1, p2, p3), lambda u, wmax=wmax: wmax * (0.35 + 0.65 * math.sin(math.pi * min(1.0, u * 0.85 + 0.12))) * (1.0 - 0.8 * max(0.0, u - 0.85) / 0.15), 1.8, per, part, flow=1.0, shape=0.9)
    per = int(COUNTS["tail"] * scale) // 3
    for (p0, p1, p2, p3, wmax) in tail_ribbons():
        curves.append((p0, p1, p2, p3))
        fish += _ribbon(rnd, (p0, p1, p2, p3), lambda u, wmax=wmax: 2.5 + (wmax - 2.5) * math.sin(math.pi * min(1.0, u * 0.9)) ** 0.7 - 2.0 * max(0.0, u - 0.9) / 0.1, 1.6, per, "tail", flow=-1.0, shape=1.05)
    fish += _moult(rnd, int(COUNTS["moult"] * scale), curves)
    return fish


def to_three(fish):
    """Blender 座標 -> glTF / Three.js 座標 (x, y, z) -> (x, z, -y) を、位置と向きの両方に。"""
    out = []
    for f in fish:
        out.append([f[0], f[2], -f[1], f[3], f[5], -f[4]] + f[6:])
    return out


def write_bin(path, fish):
    tf = to_three(fish)
    with open(path, "wb") as fh:
        for f in tf:
            fh.write(struct.pack("<11f", *f))
    return len(tf)


def manifest(fish):
    cnt = {n: 0 for n in PARTS}
    for f in fish:
        cnt[PARTS[int(f[7])]] += 1
    xs = [f[0] for f in fish]
    ys = [f[1] for f in fish]
    zs = [f[2] for f in fish]
    return {
        "name": "誰もいない王 (ムレ) / The Kingless King (Mure)",
        "version": 1,
        "count": len(fish),
        "stride": 11,
        "fields": ["x", "y", "z", "dirX", "dirY", "dirZ", "u", "part", "phase", "size", "color"],
        "dtype": "float32 little-endian",
        "coordinates": "glTF / Three.js: X right, Y up, forward +Z, 1 unit = 1 m (Blender (x,y,z) -> (x,z,-y)). Boss faces +Z; its tail extends toward -Z.",
        "parts": [{"id": PID[n], "name": n, "count": cnt[n]} for n in PARTS],
        "colors": list(COLORS),
        "fishLengthMetres": FISH_LEN,
        "boundingBoxBlender": {"min": [round(min(xs), 1), round(min(ys), 1), round(min(zs), 1)], "max": [round(max(xs), 1), round(max(ys), 1), round(max(zs), 1)]},
        "notes": [
            "x y z = rest position; dirX/Y/Z = unit flow direction (the fish's nose); u = 0..1 position along its part's curve; phase = 0..1 random for animation offset; size = 0.8..1.25 scale on fishLengthMetres; color indexes `colors`.",
            "The centre of the silhouette is empty by construction: every fish lies on a shell (head, neck/chest tube), a thin ribbon (wing feathers, tail, crown spikes) or a ring. No fish is the leader.",
            "Moulting (suggested): reassign fish between parts / blend each fish between its rest position and the `moult` streams, then re-form. Not a rule, only a suggestion.",
            "HP, attacks, hit boxes, weak points and defeat conditions are NOT decided here.",
        ],
    }
