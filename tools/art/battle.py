"""48x64 side-view battle sprites (facing left) from pose data. 27 frames:
idle 0-3, attack 4-9, cast 10-13, hurt 14-15, guard 16-17, victory 18-21, KO 22, step 23-26."""
import math
from PIL import Image
from art.pix import Canvas, shade, hexc
from art.figures import FIG

W, H = 48, 64
OUT = (22, 16, 28, 255)
T_SKIN, T_HAIR, T_TOP, T_LEGS, T_BOOT, T_ACC, T_WEAP, T_CAPE, T_BACK = 1, 2, 3, 4, 5, 6, 7, 8, 9


def P(**kw):
    base = dict(dx=0, dy=0, lean=0, fa=(10, 20), ba=(-10, 10), fl=(8, 4), bl=(-8, 4), wpn=None, head=0, crouch=0, glow=False)
    base.update(kw)
    return base


POSES = {
    "idle": [P(dy=0), P(dy=0), P(dy=1), P(dy=1)],
    "attack": [P(fa=(-60, -40), lean=-4, dx=2), P(fa=(-120, -100), lean=-6, dx=2), P(fa=(80, 90), lean=8, dx=-6, fl=(30, 4), bl=(-20, 10)),
               P(fa=(100, 110), lean=10, dx=-8, fl=(34, 6), bl=(-24, 12)), P(fa=(70, 80), lean=6, dx=-5, fl=(20, 4)), P(fa=(30, 40), lean=2, dx=-2)],
    "cast": [P(fa=(60, 70), ba=(50, 60), lean=2), P(fa=(90, 95), ba=(80, 85), lean=4, glow=True), P(fa=(95, 100), ba=(85, 90), lean=4, glow=True),
             P(fa=(60, 70), ba=(40, 50), lean=2)],
    "hurt": [P(lean=-10, dx=4, fa=(-20, 0), ba=(-30, -10), head=-2), P(lean=-14, dx=6, fa=(-30, -10), ba=(-40, -20), head=-3, crouch=2)],
    "guard": [P(fa=(70, 140), ba=(50, 120), crouch=3, lean=4, fl=(20, 20), bl=(-10, 20)), P(fa=(70, 140), ba=(50, 120), crouch=4, lean=4, fl=(20, 22), bl=(-10, 22))],
    "victory": [P(fa=(160, 170), ba=(-10, 10), dy=-1), P(fa=(165, 175), ba=(-10, 10), dy=-2), P(fa=(160, 170), ba=(-10, 10), dy=-1), P(fa=(160, 170), ba=(-10, 10), dy=0)],
    "step": [P(fl=(25, 5), bl=(-20, 10), fa=(-15, -5), ba=(15, 25)), P(fl=(5, 15), bl=(-5, 20), dy=1), P(fl=(-20, 10), bl=(25, 5), fa=(15, 25), ba=(-15, -5)), P(fl=(-5, 20), bl=(5, 15), dy=1)],
}
ORDER = ["idle", "attack", "cast", "hurt", "guard", "victory", "ko", "step"]


def seg(ang, length):
    r = math.radians(ang)
    return (-math.sin(r) * length, math.cos(r) * length)


def draw_body(f, pose):
    c = Canvas(W, H)
    build = f.get("build", "normal")
    tw = {"broad": 8, "stocky": 7, "normal": 6, "lean": 6, "slim": 5}[build]
    hgt = f.get("height", 1.0)
    ground = 61
    leg_len = 19 * hgt
    torso_len = 16 * hgt
    cr = pose["crouch"]
    hx = 24 + pose["dx"]
    hy = ground - leg_len + pose["dy"] + cr
    lean = pose["lean"]
    nx = hx - lean * 0.5
    ny = hy - torso_len
    skin, top, top2, legs, boots = f["skin"], f["top"], f["top2"], f["legs"], f["boots"]
    hair = f["hair"]
    # ---- cape / coat tails behind
    if f.get("cape"):
        cp = f["cape"]
        c.poly([(nx + 1, ny + 1), (nx + tw + 2, ny + 2), (hx + tw + 6, hy + 10), (hx + 2, hy + 12)], shade(cp, -0.2), T_CAPE)
    if f.get("scarf"):
        sc = f["scarf"]
        c.line(nx + 2, ny + 1, nx + 14, ny + 10 + pose["dy"], sc, 3, T_ACC)
        c.line(nx + 14, ny + 10 + pose["dy"], nx + 18, ny + 16, sc, 3, T_ACC)
        c.rect(nx + 17, ny + 15, nx + 19, ny + 18, shade(sc, -0.35), T_ACC)
    # ---- back leg
    def leg(angles, col, bcol, tag):
        a1, a2 = angles
        kx, ky = seg(a1, leg_len * 0.5)
        k = (hx + kx, hy + ky)
        fx, fy = seg(a1 - a2, leg_len * 0.5)
        foot = (k[0] + fx, min(ground - 2, k[1] + fy))
        c.line(hx, hy, k[0], k[1], col, 5, tag)
        c.line(k[0], k[1], foot[0], foot[1], col, 5, tag)
        c.rect(foot[0] - 4, foot[1] - 1, foot[0] + 2, foot[1] + 2, bcol, T_BOOT)
    if not f.get("dress"):
        leg(pose["bl"], shade(legs, -0.25), shade(boots, -0.25), T_BACK)
    # ---- back arm
    def arm(angles, col, hcol, tag, front):
        a1, a2 = angles
        sx, sy = nx - (1 if front else -3), ny + 3
        ex, ey = seg(a1, 8 * hgt)
        e = (sx + ex, sy + ey)
        wx, wy = seg(a1 + a2 * 0.3, 8 * hgt)
        hand = (e[0] + wx, e[1] + wy)
        c.line(sx, sy, e[0], e[1], col, 4, tag)
        c.line(e[0], e[1], hand[0], hand[1], col, 4, tag)
        c.ellipse(hand[0], hand[1], 1.6, 1.6, hcol, T_SKIN if hcol == skin else T_ACC)
        return hand, a1 + a2 * 0.3
    sleeve = skin if f.get("sleeves") else top
    arm(pose["ba"], shade(sleeve, -0.25), shade(skin, -0.2), T_BACK, False)
    # ---- torso
    if f.get("dress"):
        c.poly([(nx - tw * 0.5, ny + 2), (nx + tw * 0.6, ny + 2), (hx + tw + 3, ground - 2), (hx - tw - 3, ground - 2)], legs, T_LEGS)
        c.rect(hx - tw - 3, ground - 2, hx + tw + 3, ground - 1, shade(legs, -0.3), T_LEGS)
    c.poly([(nx - tw * 0.55, ny + 1), (nx + tw * 0.55, ny + 1), (hx + tw * 0.55, hy + 1), (hx - tw * 0.55, hy + 1)], top, T_TOP)
    if f.get("coat") == "long":
        c.poly([(hx - tw * 0.6, hy - 2), (hx + tw * 0.7, hy - 2), (hx + tw + 2, hy + 12), (hx - tw * 0.3, hy + 12)], top2, T_TOP)
    if f.get("armor"):
        for i in range(3):
            yy = ny + 4 + i * 4
            c.line(nx - tw * 0.55 + (hx - nx) * (i / 4), yy, nx + tw * 0.55 + (hx - nx) * (i / 4), yy, shade(top, -0.35), 1, T_TOP)
        c.ellipse(nx + 1, ny + 3, 4, 3, shade(top, 0.2), T_ACC)
        if f.get("accent"):
            c.line(nx - 1, ny + 3, hx - 1, hy - 2, f["accent"], 1, T_ACC)
    if f.get("apron"):
        c.poly([(nx - tw * 0.6, ny + 5), (nx - tw * 0.1, ny + 5), (hx - tw * 0.1, hy + 10), (hx - tw * 0.7, hy + 10)], f["apron"], T_ACC)
    if f.get("waistcoat"):
        c.poly([(nx - tw * 0.55, ny + 1), (nx + tw * 0.3, ny + 1), (hx + tw * 0.3, hy - 1), (hx - tw * 0.55, hy - 1)], f["waistcoat"], T_ACC)
    if f.get("sash"):
        c.line(hx - tw * 0.6, hy - 2, hx + tw * 0.6, hy - 2, f["sash"], 2, T_ACC)
        c.line(hx + tw * 0.4, hy - 1, hx + tw * 0.7, hy + 6, f["sash"], 2, T_ACC)
    if f.get("harness"):
        c.line(nx + tw * 0.4, ny + 2, hx - tw * 0.4, hy - 2, f["harness"], 1, T_ACC)
    if f.get("rig"):
        c.line(hx - tw * 0.6, hy - 1, hx + tw * 0.6, hy - 1, f["rig"], 2, T_ACC)
        c.rect(hx + tw * 0.4, hy - 3, hx + tw * 0.4 + 3, hy + 2, shade(f["rig"], 0.15), T_ACC)
    if f.get("stole"):
        c.line(nx - tw * 0.5, ny + 1, nx + tw * 0.5, ny + 1, f["stole"], 3, T_ACC)
        c.line(nx - tw * 0.4, ny + 2, hx - tw * 0.5, hy + 4, f["stole"], 2, T_ACC)
    if f.get("satchel"):
        c.rect(hx + tw * 0.2, hy - 5, hx + tw * 0.2 + 7, hy + 2, f["satchel"], T_ACC)
        c.line(nx - tw * 0.4, ny + 1, hx + tw * 0.4, hy - 4, shade(f["satchel"], -0.25), 1, T_ACC)
    if f.get("maptube"):
        c.line(nx + tw * 0.4, ny - 2, hx + tw * 0.6, hy - 2, f["maptube"], 3, T_ACC)
    # ---- front leg
    if not f.get("dress"):
        leg(pose["fl"], legs, boots, T_LEGS)
    # ---- head
    hcx = nx - 1 + pose["head"] * 0.5
    hcy = ny - 7
    c.rect(nx - 1, ny - 2, nx + 1, ny + 1, skin, T_SKIN)
    c.ellipse(hcx, hcy, 5.5, 6.2, skin, T_SKIN)
    c.put(hcx - 6, hcy + 1, skin, T_SKIN)  # nose
    if f.get("scales"):
        for (ox, oy) in ((1, -3), (3, 1), (-1, 3), (2, 4)):
            c.put(hcx + ox, hcy + oy, shade(skin, -0.3), T_SKIN)
    # eye / brow / mouth
    eye = f.get("eye", (30, 20, 20, 255))
    c.put(hcx - 3, hcy - 1, eye, T_SKIN)
    c.put(hcx - 3, hcy - 2, shade(hair, 0.0), T_HAIR)
    c.put(hcx - 4, hcy + 3, shade(skin, -0.35), T_SKIN)
    if f.get("beard"):
        c.ellipse(hcx - 1, hcy + 4, 4, 2.5, f["beard"], T_HAIR)
    _hair_side(c, f, hcx, hcy)
    if f.get("goggles"):
        c.rect(hcx - 5, hcy - 6, hcx + 1, hcy - 5, f["goggles"], T_ACC)
        c.put(hcx - 4, hcy - 6, shade(f["goggles"], 0.4), T_ACC)
    if f.get("glasses"):
        c.rect(hcx - 5, hcy - 1, hcx - 2, hcy, f["glasses"], T_ACC)
    if f.get("hat"):
        c.ellipse(hcx, hcy - 6, 7, 2, f["hat"], T_ACC)
        c.ellipse(hcx + 1, hcy - 8, 4.5, 2.5, f["hat"], T_ACC)
    if f.get("scarf"):
        c.ellipse(nx, ny, 4, 2, f["scarf"], T_ACC)
    # ---- front arm + weapon
    fsleeve = skin if f.get("sleeves") else top
    hand_col = f.get("gauntlet") or (f.get("mitten") or skin)
    hand, ang = arm(pose["fa"], fsleeve, hand_col, T_TOP, True)
    if f.get("scar"):
        c.put(hand[0] + 2, hand[1] - 4, shade(skin, -0.4), T_SKIN)
        c.put(hand[0] + 1, hand[1] - 3, shade(skin, -0.4), T_SKIN)
    _weapon(c, f, hand, ang)
    if pose["glow"]:
        g = f.get("accent", (255, 220, 120, 255))
        c.ellipse(hand[0] - 3, hand[1], 2.5, 2.5, shade(g, 0.4), T_ACC)
    c.light(0.14)
    c.outline(OUT)
    return c


def _hair_side(c, f, x, y):
    hc = f["hair"]
    st = f.get("hair_style", "short_swept")
    c.ellipse(x + 1.5, y - 3, 5.5, 3.8, hc, T_HAIR)
    c.rect(x + 1, y - 3, x + 6, y + 2, hc, T_HAIR)
    if st in ("short_swept", "short_messy"):
        c.put(x - 5, y - 5, hc, T_HAIR)
        c.put(x - 4, y - 6, hc, T_HAIR)
        if st == "short_messy":
            c.put(x + 3, y - 8, hc, T_HAIR)
            c.put(x - 1, y - 8, hc, T_HAIR)
    elif st == "bob":
        c.rect(x, y - 3, x + 6, y + 4, hc, T_HAIR)
        c.rect(x - 5, y - 6, x - 1, y - 4, hc, T_HAIR)
    elif st in ("long", "braid"):
        c.rect(x + 1, y - 2, x + 6, y + 7, hc, T_HAIR)
        if st == "braid":
            c.line(x + 5, y + 6, x + 8, y + 20, hc, 2, T_HAIR)
            c.put(x + 8, y + 21, f.get("accent", hc), T_ACC)
    elif st == "tied":
        c.ellipse(x + 7, y - 3, 2, 2, hc, T_HAIR)
        c.line(x + 7, y - 1, x + 9, y + 6, hc, 2, T_HAIR)
    elif st == "cropped":
        c.ellipse(x + 1, y - 3, 5.8, 3.4, hc, T_HAIR)
    elif st in ("curls", "curls_short"):
        for (ox, oy) in ((-4, -6), (-1, -8), (2, -8), (5, -6), (6, -2), (6, 2)):
            c.ellipse(x + ox, y + oy, 1.6, 1.6, hc, T_HAIR)
        if st == "curls":
            c.ellipse(x + 5, y + 4, 2, 2, hc, T_HAIR)


def _weapon(c, f, hand, ang):
    w = f.get("weapon")
    col = f.get("weapon_col", (200, 200, 200, 255))
    hx, hy = hand
    dx, dy = seg(ang + 180, 1)  # continue along forearm direction
    ux, uy = -dx, -dy
    if w in ("sword", "blade"):
        L = 17 if w == "sword" else 19
        tip = (hx + ux * L, hy + uy * L)
        c.line(hx, hy, tip[0], tip[1], col, 2, T_WEAP)
        c.line(hx - uy * 3, hy + ux * 3, hx + uy * 3, hy - ux * 3, shade(col, -0.45), 1, T_WEAP)
        if w == "blade":
            for i in range(4, L - 2, 4):
                c.put(hx + ux * i, hy + uy * i, (140, 120, 200, 255), T_WEAP)
    elif w == "knife":
        c.line(hx, hy, hx + ux * 8, hy + uy * 8, col, 2, T_WEAP)
    elif w in ("spear", "staff", "rod"):
        L = 30 if w == "spear" else (24 if w == "staff" else 18)
        a = (hx - ux * 8, hy - uy * 8)
        b = (hx + ux * (L - 8), hy + uy * (L - 8))
        c.line(a[0], a[1], b[0], b[1], col, 1 if w == "spear" else 2, T_WEAP)
        if w == "spear":
            c.line(b[0], b[1], b[0] + ux * 5, b[1] + uy * 5, (225, 230, 240, 255), 2, T_WEAP)
        elif w == "staff" and f.get("bell"):
            c.ellipse(b[0], b[1] + 2, 2.5, 2.5, f["bell"], T_ACC)
        elif w == "rod":
            c.ellipse(b[0], b[1], 2, 2, f.get("accent", (230, 170, 60, 255)), T_ACC)
    elif w == "wrench":
        b = (hx + ux * 12, hy + uy * 12)
        c.line(hx, hy, b[0], b[1], col, 2, T_WEAP)
        c.ellipse(b[0], b[1], 3, 3, shade(col, -0.1), T_WEAP)
        c.put(b[0] + ux, b[1] + uy, (40, 30, 30, 255), T_WEAP)
    elif w == "bow":
        px, py = -uy, ux
        top = (hx + px * 11, hy + py * 11)
        bot = (hx - px * 11, hy - py * 11)
        mid = (hx + ux * 4, hy + uy * 4)
        c.line(top[0], top[1], mid[0], mid[1], col, 2, T_WEAP)
        c.line(mid[0], mid[1], bot[0], bot[1], col, 2, T_WEAP)
        c.line(top[0], top[1], bot[0], bot[1], (230, 225, 210, 255), 1, T_WEAP)


def ko(f):
    base = draw_body(f, P(fa=(0, 0), ba=(0, 0), fl=(0, 0), bl=(0, 0)))
    img = base.image().rotate(90, expand=False, resample=Image.NEAREST)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(img, (0, 20), img)
    return out


def sheet(f):
    img = Image.new("RGBA", (W * 27, H), (0, 0, 0, 0))
    i = 0
    for name in ORDER:
        if name == "ko":
            img.paste(ko(f), (i * W, 0))
            i += 1
            continue
        for pose in POSES[name]:
            img.paste(draw_body(f, pose).image(), (i * W, 0))
            i += 1
    return img


def build(save):
    for cid, f in FIG.items():
        save(sheet(f), f"sprites/battle/{cid}.png", "battle_sprite", "48x64 x27: idle4 attack6 cast4 hurt2 guard2 victory4 ko1 step4")


# =================================================================================================================
# Library build: same 27-frame 48x64 layout (see module docstring), facing left, feet on row 62.
# Heroes C02-C08: frames taken from the recoloured Time Fantasy Elements sheet (west row) built for the world sprite.
# Dain (C01): the matching Beast Tribes lizard MV side-view battler, recoloured the same way as his world sprite.
# =================================================================================================================
def _el_battle(spec, bow=False):
    from art import world_sprites as ws
    plain, srcs = ws.el_compose(spec)
    armed, srcs2 = ws.el_compose(spec, weapon=True)
    atk = [15, 16, 17, 18, 17] if bow else [10, 11, 12, 13, 14]
    seq = ([(plain, 1, 1, 0)] * 4 +
           [(armed, 1, c, 0) for c in atk] + [(plain, 1, 1, 0)] +
           [(plain, 1, c, 0) for c in (3, 4, 5, 5)] +
           [(plain, 1, 6, 2), (plain, 1, 6, 4)] +
           [(plain, 1, 15, 0), (plain, 1, 15, 1)] +
           [(plain, 0, c, 0) for c in (3, 4, 5, 4)] +
           [(plain, 1, 22, "ko")] +
           [(plain, 1, c, 0) for c in (0, 1, 2, 1)])
    img = Image.new("RGBA", (W * 27, H), (0, 0, 0, 0))
    for i, (sh, r, c, dx) in enumerate(seq):
        fr = sh.crop((c * 48, r * 48, c * 48 + 48, r * 48 + 48))
        oy = 29 if dx == "ko" else 32
        img.paste(fr, (i * W + (0 if dx == "ko" else dx), oy), fr)
    return img, sorted(set(srcs + srcs2))


SV_MOTION = {"walk": 0, "wait": 1, "chant": 2, "guard": 3, "damage": 4, "evade": 5, "thrust": 6, "swing": 7,
             "missile": 8, "skill": 9, "spell": 10, "item": 11, "escape": 12, "victory": 13, "dying": 14,
             "abnormal": 15, "sleep": 16, "dead": 17}


def _sv_battle(sv_img):
    """MV side-view battler (9x6 of 48x48; motion m in column-group m//6, row m%6) -> 27-frame sheet."""
    def f(m, k):
        n = SV_MOTION[m]
        x, y = ((n // 6) * 3 + k) * 48, (n % 6) * 48
        return sv_img.crop((x, y, x + 48, y + 48))
    seq = ([f("walk", k) for k in (1, 1, 1, 1)] +
           [f("swing", k) for k in (0, 1, 2)] + [f("swing", 2), f("swing", 2), f("walk", 1)] +
           [f("chant", 0), f("chant", 1), f("spell", 1), f("spell", 2)] +
           [f("damage", 0), f("damage", 1)] + [f("guard", 0), f("guard", 1)] +
           [f("victory", k) for k in (0, 1, 2, 1)] + [f("dead", 0)] +
           [f("walk", k) for k in (0, 1, 2, 1)])
    img = Image.new("RGBA", (W * 27, H), (0, 0, 0, 0))
    for i, fr in enumerate(seq):
        img.paste(fr, (i * W, 20), fr)
    return img


def build_library(save_ext):
    from art import world_sprites as ws
    frames = "48x64 x27: idle4 attack6 cast4 hurt2 guard2 victory4 ko1 step4 (facing left, feet row 62)"
    sv = ws.tf_recolour(ws._lib_img(ws.DAIN_SRC["sv"]), ws.dain_lut(), feet=(48, 42))
    save_ext(_sv_battle(sv), "sprites/battle/C01.png", "battle_sprite", [ws.DAIN_SRC["sv"]], frames,
             "TF Beast Tribes lizard side-view battler, recoloured")
    for cid, spec in ws.hero_specs().items():
        if cid == "C01":
            continue
        img, srcs = _el_battle(spec, bow=spec["parts"].get("weapon", "").startswith("bow"))
        save_ext(img, f"sprites/battle/{cid}.png", "battle_sprite", srcs, frames,
                 "Time Fantasy Elements west-facing frames, recoloured")
