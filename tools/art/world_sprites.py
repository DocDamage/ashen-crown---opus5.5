"""24x32 world sprites: 4 directions x (idle + 4 walk) + 6 emotive poses, feet on y=31."""
from art.pix import Canvas, shade, hexc

W, H = 24, 32
OUT = (26, 20, 32, 255)

# material tags for lighting passes
T_SKIN, T_HAIR, T_TOP, T_LEGS, T_BOOT, T_ACC, T_WEAP, T_CAPE = 1, 2, 3, 4, 5, 6, 7, 8


def _widths(build):
    return {"broad": (5, 18), "stocky": (6, 17), "normal": (7, 16), "lean": (7, 16), "slim": (8, 15)}[build]


def draw_world(f, direction, frame, pose=None):
    c = Canvas(W, H)
    h = f.get("height", 1.0)
    dy = int(round((1.0 - h) * 12))           # shorter characters: everything above the feet shifts down
    bob = 1 if frame in (1, 3) else 0
    step = {0: 0, 1: 1, 2: 0, 3: -1, 4: 0}[frame]
    x0, x1 = _widths(f.get("build", "normal"))
    skin, hair, top, top2, legs, boots = f["skin"], f["hair"], f["top"], f["top2"], f["legs"], f["boots"]
    y_neck = 14 + dy + bob
    y_hip = 23 + (dy // 2) + bob
    side = direction in ("left", "right")
    cape = f.get("cape")
    # ---------------- cape behind (front/side views)
    if cape and direction != "up":
        if side:
            c.poly([(13, y_neck + 1), (17, y_neck + 1), (18 + (1 if frame in (1, 3) else 0), y_hip + 5), (13, y_hip + 5)], shade(cape, -0.15), T_CAPE)
        else:
            c.rect(x0, y_neck + 2, x1, y_hip + 3, shade(cape, -0.2), T_CAPE)
    if f.get("scarf") and direction != "down":
        sc = f["scarf"]
        if side:
            tail = 17 + (frame % 2)
            c.line(13, y_neck + 1, tail + 2, y_neck + 6, sc, 2, T_ACC)
            c.put(tail + 3, y_neck + 7, shade(sc, -0.3), T_ACC)
        else:
            c.line(10, y_neck + 1, 9, y_hip + 2, sc, 2, T_ACC)
            c.line(13, y_neck + 1, 14, y_hip + 1, sc, 2, T_ACC)
    # ---------------- legs
    if f.get("dress"):
        hem = y_hip + 5
        c.poly([(x0 + 1, y_hip - 2), (x1 - 1, y_hip - 2), (x1 + 1, hem), (x0 - 1, hem)], legs, T_LEGS)
        c.rect(x0 + 2, hem + 1, x0 + 4, 30, shade(legs, -0.4), T_LEGS)
        c.rect(x1 - 4, hem + 1, x1 - 2, 30, shade(legs, -0.4), T_LEGS)
        c.rect(x0 + 1 + (1 if step > 0 else 0), 30, x0 + 4, 31, boots, T_BOOT)
        c.rect(x1 - 4, 30, x1 - 1 - (1 if step < 0 else 0), 31, boots, T_BOOT)
    elif side:
        # scissor legs in profile (facing left)
        fx = -2 * step
        c.rect(11 + fx, y_hip, 13 + fx, 29, legs, T_LEGS)
        c.rect(12 - fx, y_hip, 14 - fx, 29, shade(legs, -0.2), T_LEGS)
        c.rect(10 + fx, 30, 13 + fx, 31, boots, T_BOOT)
        c.rect(11 - fx, 30, 14 - fx, 31, shade(boots, -0.2), T_BOOT)
    else:
        lx0, rx0 = 8, 13
        ll = 29 - (1 if step > 0 else 0)
        rl = 29 - (1 if step < 0 else 0)
        c.rect(lx0, y_hip, lx0 + 2, ll, legs, T_LEGS)
        c.rect(rx0, y_hip, rx0 + 2, rl, legs, T_LEGS)
        c.rect(lx0 - 1 + (0 if direction == "down" else 1), ll + 1, lx0 + 2, ll + 2, boots, T_BOOT)
        c.rect(rx0, rl + 1, rx0 + 3 - (0 if direction == "down" else 1), rl + 2, boots, T_BOOT)
    # ---------------- torso
    if side:
        tx0, tx1 = 9, 15
        if f.get("build") in ("broad", "stocky"):
            tx0, tx1 = 8, 16
    else:
        tx0, tx1 = x0, x1
    c.rect(tx0, y_neck + 1, tx1, y_hip, top, T_TOP)
    c.rect(tx0, y_hip - 1, tx1, y_hip, top2, T_TOP)   # belt line / hem shade
    if f.get("coat") == "long":
        if side:
            c.poly([(tx0, y_hip), (tx1, y_hip), (tx1 + 1, y_hip + 5), (tx0 + 1, y_hip + 5)], top, T_TOP)
        else:
            c.rect(tx0, y_hip, tx0 + 2, y_hip + 5, top, T_TOP)
            c.rect(tx1 - 2, y_hip, tx1, y_hip + 5, top, T_TOP)
            if direction == "up":
                c.rect(tx0, y_hip, tx1, y_hip + 5, top, T_TOP)
    if f.get("armor"):
        # segmented plate: horizontal bands and pauldrons
        for yy in range(y_neck + 3, y_hip, 3):
            c.rect(tx0, yy, tx1, yy, shade(top, -0.35), T_TOP)
        if not side:
            c.rect(tx0 - 1, y_neck + 1, tx0 + 2, y_neck + 3, shade(top, 0.15), T_ACC)
            c.rect(tx1 - 2, y_neck + 1, tx1 + 1, y_neck + 3, shade(top, 0.15), T_ACC)
        else:
            c.rect(11, y_neck + 1, 14, y_neck + 3, shade(top, 0.15), T_ACC)
        if f.get("accent") and direction == "down":
            c.rect(11, y_neck + 2, 12, y_hip - 2, f["accent"], T_ACC)
    if f.get("apron") and direction != "up":
        ap = f["apron"]
        if side:
            c.rect(tx0, y_neck + 4, tx0 + 2, y_hip + 3, ap, T_ACC)
        else:
            c.rect(tx0 + 1, y_neck + 3, tx1 - 1, y_hip + 3, ap, T_ACC)
    if f.get("waistcoat") and direction != "up":
        wc = f["waistcoat"]
        if side:
            c.rect(tx0, y_neck + 1, tx1 - 2, y_hip - 1, wc, T_ACC)
        else:
            c.rect(tx0, y_neck + 1, tx0 + 3, y_hip - 1, wc, T_ACC)
            c.rect(tx1 - 3, y_neck + 1, tx1, y_hip - 1, wc, T_ACC)
    if f.get("sash"):
        c.rect(tx0, y_hip - 2, tx1, y_hip - 1, f["sash"], T_ACC)
        if direction == "down":
            c.rect(tx1 - 1, y_hip, tx1, y_hip + 2, f["sash"], T_ACC)
    if f.get("harness") and direction != "up":
        c.line(tx0 + 1, y_neck + 1, tx1 - 1, y_hip - 2, f["harness"], 1, T_ACC)
    if f.get("rig"):
        c.rect(tx0, y_hip - 2, tx1, y_hip - 1, f["rig"], T_ACC)
        if not side:
            c.rect(tx1 - 1, y_hip - 3, tx1 + 1, y_hip + 1, shade(f["rig"], 0.2), T_ACC)
    if f.get("stole"):
        st = f["stole"]
        if side:
            c.rect(10, y_neck + 1, 13, y_neck + 3, st, T_ACC)
            c.rect(10, y_neck + 3, 11, y_hip, st, T_ACC)
        else:
            c.rect(tx0, y_neck + 1, tx1, y_neck + 2, st, T_ACC)
            if direction == "down":
                c.rect(tx0 + 1, y_neck + 2, tx0 + 2, y_hip + 1, st, T_ACC)
                c.rect(tx1 - 2, y_neck + 2, tx1 - 1, y_hip + 1, st, T_ACC)
    # ---------------- arms
    arm_sw = step
    if pose == "arms_up":
        arm_sw = 0
    if side:
        ax = 11 + (-arm_sw)
        sleeve = skin if f.get("sleeves") else top
        c.rect(ax, y_neck + 2, ax + 2, y_hip - 1, sleeve, T_TOP)
        c.rect(ax, y_hip, ax + 1, y_hip + 1, skin if not f.get("gauntlet") else f["gauntlet"], T_SKIN)
    else:
        sleeve = skin if f.get("sleeves") else top
        la, ra = arm_sw, -arm_sw
        if pose == "arms_up":
            c.rect(tx0 - 2, y_neck - 4, tx0 - 1, y_neck + 2, sleeve, T_TOP)
            c.rect(tx1 + 1, y_neck - 4, tx1 + 2, y_neck + 2, sleeve, T_TOP)
            c.rect(tx0 - 2, y_neck - 6, tx0 - 1, y_neck - 5, skin, T_SKIN)
            c.rect(tx1 + 1, y_neck - 6, tx1 + 2, y_neck - 5, skin, T_SKIN)
        else:
            c.rect(tx0 - 2, y_neck + 2 + la, tx0 - 1, y_hip - 1 + la, sleeve, T_TOP)
            c.rect(tx1 + 1, y_neck + 2 + ra, tx1 + 2, y_hip - 1 + ra, sleeve, T_TOP)
            lh = f.get("mitten") if (f.get("mitten") and direction == "down") else skin
            rh = f.get("gauntlet") or skin
            c.rect(tx0 - 2, y_hip + la, tx0 - 1, y_hip + 1 + la, lh, T_SKIN)
            c.rect(tx1 + 1, y_hip + ra, tx1 + 2, y_hip + 1 + ra, rh, T_ACC if f.get("gauntlet") else T_SKIN)
            if f.get("scar") and direction == "down":
                c.put(tx0 - 2, y_hip - 3 + la, shade(skin, -0.35), T_SKIN)
                c.put(tx0 - 1, y_hip - 4 + la, shade(skin, -0.35), T_SKIN)
    if f.get("satchel"):
        s = f["satchel"]
        if direction == "down":
            c.line(tx0, y_neck + 1, tx1, y_hip - 2, shade(s, -0.2), 1, T_ACC)
            c.rect(tx1, y_hip - 3, tx1 + 3, y_hip + 1, s, T_ACC)
        elif side:
            c.rect(14, y_hip - 4, 17, y_hip, s, T_ACC)
        else:
            c.rect(tx0 - 2, y_hip - 3, tx0 + 1, y_hip + 1, s, T_ACC)
    if f.get("maptube") and direction != "down":
        c.line(15 if direction == "up" else 15, y_neck, 16 if direction == "up" else 17, y_hip, f["maptube"], 2, T_ACC)
    if f.get("bell") and direction == "down":
        c.rect(tx1 - 2, y_hip, tx1 - 1, y_hip + 2, f["bell"], T_ACC)
    # ---------------- head
    hy = 4 + dy + bob
    if pose == "head_down":
        hy += 1
    if side:
        c.rect(8, hy + 3, 14, hy + 10, skin, T_SKIN)     # face block
        c.put(7, hy + 7, skin, T_SKIN)                   # nose
        c.rect(12, hy + 10, 13, hy + 11, skin, T_SKIN)   # neck
    else:
        c.rect(8, hy + 3, 15, hy + 10, skin, T_SKIN)
        c.rect(9, hy + 2, 14, hy + 11, skin, T_SKIN)
        c.rect(11, hy + 11, 12, hy + 11, shade(skin, -0.2), T_SKIN)
    if f.get("scales"):
        for (sx, sy) in ((9, 9), (14, 8), (10, 4), (13, 5)):
            if c.get(sx, hy + sy - 4 + 4) is not None and not side:
                c.put(sx, hy + sy, shade(skin, -0.28), T_SKIN)
        if side:
            c.put(12, hy + 8, shade(skin, -0.28), T_SKIN)
            c.put(10, hy + 5, shade(skin, -0.28), T_SKIN)
    _hair(c, f, direction, hy)
    # face features
    eye = f.get("eye", (30, 20, 20, 255))
    if direction == "down":
        c.put(10, hy + 7, eye, T_SKIN)
        c.put(13, hy + 7, eye, T_SKIN)
        if pose != "head_down":
            c.put(11, hy + 9, shade(skin, -0.3), T_SKIN)
            c.put(12, hy + 9, shade(skin, -0.3), T_SKIN)
        if f.get("goggles"):
            c.rect(9, hy + 2, 14, hy + 3, f["goggles"], T_ACC)
            c.put(11, hy + 2, shade(f["goggles"], -0.4), T_ACC)
        if f.get("glasses"):
            c.put(9, hy + 7, f["glasses"], T_ACC)
            c.put(14, hy + 7, f["glasses"], T_ACC)
            c.rect(11, hy + 6, 12, hy + 6, f["glasses"], T_ACC)
        if f.get("beard"):
            c.rect(9, hy + 9, 14, hy + 11, f["beard"], T_HAIR)
            c.rect(11, hy + 9, 12, hy + 9, shade(skin, -0.3), T_SKIN)
    elif side:
        c.put(9, hy + 7, eye, T_SKIN)
        if f.get("goggles"):
            c.rect(8, hy + 2, 12, hy + 3, f["goggles"], T_ACC)
        if f.get("glasses"):
            c.rect(8, hy + 6, 10, hy + 7, f["glasses"], T_ACC)
        if f.get("beard"):
            c.rect(8, hy + 9, 12, hy + 11, f["beard"], T_HAIR)
    if f.get("hat"):
        ht = f["hat"]
        c.rect(7, hy + 1, 16, hy + 2, ht, T_ACC)
        c.rect(8, hy - 1, 15, hy + 1, ht, T_ACC)
    if f.get("scarf") and direction != "up":
        sc = f["scarf"]
        if side:
            c.rect(9, hy + 10, 14, hy + 12, sc, T_ACC)
        else:
            c.rect(8, hy + 10, 15, hy + 12, sc, T_ACC)
            if direction == "down":
                c.rect(14, hy + 12, 15, hy + 17 + bob, sc, T_ACC)
    if cape and direction == "up":
        c.poly([(x0 - 1, y_neck + 1), (x1 + 1, y_neck + 1), (x1 + 2, y_hip + 5), (x0 - 2, y_hip + 5)], cape, T_CAPE)
        c.line(12, y_neck + 2, 12, y_hip + 5, shade(cape, -0.35), 1, T_CAPE)  # split at the shoulders
        if f.get("maptube"):
            c.line(15, y_neck, 17, y_hip, f["maptube"], 2, T_ACC)
    elif cape and not side:
        c.rect(x0 - 1, y_neck + 1, x0, y_neck + 3, cape, T_CAPE)
        c.rect(x1, y_neck + 1, x1 + 1, y_neck + 3, cape, T_CAPE)
    # weapon (carried on back / side)
    _carried_weapon(c, f, direction, y_neck, y_hip)
    c.light(0.16)
    c.outline(OUT)
    if direction == "right":
        c = c.flip()
    return c


def _hair(c, f, direction, hy):
    hc = f["hair"]
    st = f.get("hair_style", "short_swept")
    side = direction in ("left", "right")
    if direction == "up":
        c.rect(8, hy + 1, 15, hy + 10, hc, 2)
        c.rect(9, hy, 14, hy + 1, hc, 2)
        if st in ("long", "braid", "tied"):
            c.rect(9, hy + 10, 14, hy + 13, hc, 2)
        if st == "braid":
            c.rect(11, hy + 13, 12, hy + 19, hc, 2)
            c.put(11, hy + 20, f.get("accent", hc), 6)
        if st == "tied":
            c.rect(11, hy + 11, 12, hy + 15, hc, 2)
        if st in ("curls", "curls_short"):
            for x in range(8, 16, 2):
                c.put(x, hy + 10, shade(hc, -0.2), 2)
        return
    if side:
        c.rect(9, hy, 14, hy + 3, hc, 2)
        c.rect(12, hy + 3, 15, hy + 8, hc, 2)
        c.rect(8, hy + 1, 9, hy + 3, hc, 2)
        if st in ("long", "braid", "tied"):
            c.rect(13, hy + 8, 15, hy + 11, hc, 2)
        if st == "braid":
            c.rect(14, hy + 11, 15, hy + 18, hc, 2)
        if st == "tied":
            c.rect(15, hy + 4, 16, hy + 9, hc, 2)
        if st == "bob":
            c.rect(12, hy + 8, 14, hy + 10, hc, 2)
        if st in ("curls", "curls_short"):
            c.put(8, hy, hc, 2)
            c.put(15, hy + 2, hc, 2)
            c.put(15, hy + 6, hc, 2)
        return
    # front
    c.rect(8, hy, 15, hy + 3, hc, 2)
    c.rect(9, hy - 1, 14, hy, hc, 2)
    c.rect(7, hy + 2, 8, hy + 6, hc, 2)
    c.rect(15, hy + 2, 16, hy + 6, hc, 2)
    if st == "short_swept":
        c.rect(9, hy + 3, 11, hy + 4, hc, 2)
    elif st == "short_messy":
        c.put(10, hy + 4, hc, 2)
        c.put(13, hy + 4, hc, 2)
        c.put(8, hy - 1, hc, 2)
    elif st == "bob":
        c.rect(7, hy + 2, 8, hy + 10, hc, 2)
        c.rect(15, hy + 2, 16, hy + 10, hc, 2)
        c.rect(9, hy + 3, 13, hy + 4, hc, 2)
    elif st in ("long", "braid"):
        c.rect(7, hy + 2, 8, hy + 12, hc, 2)
        c.rect(15, hy + 2, 16, hy + 12, hc, 2)
        if st == "braid":
            c.rect(15, hy + 10, 16, hy + 17, hc, 2)
            c.put(16, hy + 18, f.get("accent", hc), 6)
    elif st == "tied":
        c.rect(10, hy + 3, 14, hy + 3, hc, 2)
    elif st == "cropped":
        c.rect(8, hy, 15, hy + 2, hc, 2)
    elif st in ("curls", "curls_short"):
        for x in range(8, 16, 2):
            c.put(x, hy - 1, hc, 2)
        c.put(7, hy + 1, hc, 2)
        c.put(16, hy + 1, hc, 2)
        if st == "curls":
            c.rect(7, hy + 2, 8, hy + 8, hc, 2)
            c.rect(15, hy + 2, 16, hy + 8, hc, 2)


def _carried_weapon(c, f, direction, y_neck, y_hip):
    w = f.get("weapon")
    col = f.get("weapon_col", (200, 200, 200, 255))
    if not w:
        return
    if direction == "up":
        if w in ("spear", "staff", "bow"):
            c.line(9, y_neck - 6, 16, y_hip + 4, col, 1, 7)
        elif w in ("sword", "blade"):
            c.line(14, y_neck - 3, 10, y_hip + 2, col, 1, 7)
            c.put(14, y_neck - 3, shade(col, -0.4), 7)
    elif direction in ("left", "right"):
        if w in ("spear", "staff"):
            c.line(16, y_neck - 8, 16, y_hip + 6, col, 1, 7)
            if w == "spear":
                c.rect(16, y_neck - 11, 16, y_neck - 8, (220, 226, 236, 255), 7)
        elif w == "bow":
            c.line(15, y_neck - 2, 17, y_hip, col, 1, 7)
        elif w in ("sword", "blade", "knife", "wrench", "rod"):
            c.line(14, y_hip - 1, 16, y_hip + 3, col, 1, 7)
    else:
        if w in ("spear", "staff"):
            c.line(19, y_neck - 8, 19, y_hip + 6, col, 1, 7)
            if w == "spear":
                c.rect(19, y_neck - 11, 19, y_neck - 8, (220, 226, 236, 255), 7)
            if w == "staff" and f.get("bell"):
                c.rect(18, y_neck - 9, 20, y_neck - 7, f["bell"], 6)
        elif w == "bow":
            c.line(4, y_neck - 2, 4, y_hip + 2, col, 1, 7)
            c.put(5, y_neck - 3, col, 7)
            c.put(5, y_hip + 3, col, 7)


POSES = [("arms_up", 0), ("head_down", 0), (None, 1), ("arms_up", 2), (None, 0), ("head_down", 2)]


def sheet(f):
    """Rows: down, left, right, up (5 frames each: idle + 4 walk); row 4: 6 emotive poses (front)."""
    from PIL import Image
    img = Image.new("RGBA", (W * 6, H * 5), (0, 0, 0, 0))
    for r, d in enumerate(["down", "left", "right", "up"]):
        for fr in range(5):
            img.paste(draw_world(f, d, fr).image(), (fr * W, r * H))
    for i, (pose, fr) in enumerate(POSES):
        img.paste(draw_world(f, "down", fr, pose).image(), (i * W, 4 * H))
    return img


# =================================================================================================================
# Library build (owner-licensed Time Fantasy art -> game/assets/ext/, git-ignored).
# Heroes and most named NPCs are assembled from Time Fantasy *Elements* pieces (finalbossblues' layered character
# kit: 48x48 frames, 23 columns x 4 directions S/W/E/N) and palette-remapped toward the character bible colours in
# figures.py. Generic townsfolk roles use finalbossblues' NPC-animation frames (38x36) as drawn.
# World sheet: 6 x 5 cells of CW x CH; rows down,left,right,up = idle + walk (TF 0,1,2,1); row 4 = six poses.
# =================================================================================================================
import colorsys as _cs
from art.pix import lib_img as _lib_img, shade as _shade, hexc as _hexc

EL = "characters/Elements Character Generator/"
EL_ORDER = ["backextra", "backhair", "bottom", "top", "head", "frontextra", "hair", "hat", "weapon"]
EL_ORDER_N = ["bottom", "top", "head", "frontextra", "hair", "backhair", "backextra", "hat", "weapon"]
EL_DIR = {"down": 0, "left": 1, "right": 2, "up": 3}
CW, CH = 32, 36                     # world cell; feet 2px above the cell bottom (= tile bottom)
EL_BOX = (8, -3)                    # crop origin of a world cell inside a 48x48 Elements frame
NA_BOX = (3, -2)                    # same for 38x36 NPC-animation frames

# Source palette families (dark -> light) shared by all Elements pieces, with the index the target colour anchors to.
FAM = {
    "skin": (["73172d", "bb7547", "dba463", "f4d29c", "faf4d6"], 3),
    "cloth": (["4e182a", "871247", "d21e3c", "fb6028"], 2),
    "leather": (["49392d", "866037", "c59159"], 1),
    "gold": (["f9d51a"], 0),
    "white": (["bbc1f6", "ffffff"], 1),          # collars / capelets / tabards (top layer only)
    "legs": (["20275b", "185cbf", "2c8cd8", "63c7ee"], 1),
    "boots": (["4a2c1c", "a26320", "d69738"], 1),
    "trim": (["9bd65c"], 0),
    "hair": (["250809", "480e11", "a0480e", "f9a31b", "fffc40"], 3),
    "backhair": (["5c1435", "b3356c", "e86abe", "fcb5f2"], 2),
    "tie": (["313919", "4e6827", "66942e", "81c035"], 2),
    "cape": (["2f2961", "8446b4", "c668d4", "f396e5"], 1),
    "fx": (["2a356a", "3d61a9", "6493ce", "a6c3e3"], 2),
    "hat": (["431216", "7d5338", "d5a038", "fee457", "fff9bd"], 2),
    "hat2": (["143464", "596792", "a2abd0", "deebf0"], 1),
    "eye": (["1a7a3e"], 0),
}
LAYER_ONLY = {"white": ("top",), "eye": ("head",)}


def _lum(c):
    return (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) / 255.0


def _ramp_map(fam, target, cols=None, ai=0):
    """Map each source colour of a family onto target with the same relative light/dark offsets (cool shadows,
    warm highlights via pix.shade)."""
    if cols is None:
        cols, ai = FAM[fam]
    src = [_hexc(c) if isinstance(c, str) else tuple(c) + (255,) for c in cols]
    la = _lum(src[ai])
    lt = _lum(target)
    out = {}
    for s in src:
        ls = _lum(s)
        if ls >= la:
            f = (0.2 if fam in ("hair", "backhair") else 0.75) * (ls - la) / max(1e-3, 1.0 - la)
        else:
            f = (ls - la) / max(1e-3, la) * (0.85 if lt > 0.25 else 0.6)
        out[s[:3]] = _shade(target, max(-0.85, min(0.8, f)))[:3]
    return out


def el_layer(t, name, colours):
    """One Elements piece, palette-remapped. colours: family -> target RGBA (families absent are left as drawn)."""
    rel = EL + ("core/" if (t, name) in (("bottom", "bottom0"), ("top", "top0")) else "assets/") + f"{t}/{name}.png"
    img = _lib_img(rel).copy()
    lut = {}
    for fam, tgt in colours.items():
        base = fam.split("@")[0]
        if base not in FAM:
            continue
        if base in LAYER_ONLY and t not in LAYER_ONLY[base]:
            continue
        if "@" in fam and fam.split("@")[1] != t:
            continue
        lut.update(_ramp_map(base, tgt))
    if lut:
        px = img.load()
        for y in range(img.height):
            for x in range(img.width):
                p = px[x, y]
                if p[3] and p[:3] in lut:
                    px[x, y] = lut[p[:3]] + (p[3],)
    return img, rel


def el_compose(spec, weapon=False):
    """Full 1104x192 Elements sheet for a spec -> (image, [library sources]). North row uses the north layer order."""
    from PIL import Image
    layers = {}
    srcs = []
    for t, n in spec["parts"].items():
        if t == "weapon" and not weapon:
            continue
        layers[t], rel = el_layer(t, n, spec.get("colours", {}))
        srcs.append(rel)
    out = Image.new("RGBA", (1104, 192), (0, 0, 0, 0))
    for r in range(4):
        order = EL_ORDER_N if r == 3 else EL_ORDER
        band = Image.new("RGBA", (1104, 48), (0, 0, 0, 0))
        for t in order:
            if t in layers:
                band.alpha_composite(layers[t].crop((0, r * 48, 1104, r * 48 + 48)))
        out.paste(band, (0, r * 48))
    return out, srcs


def el_frame(sheet, direction, col):
    r = EL_DIR[direction] if isinstance(direction, str) else direction
    return sheet.crop((col * 48, r * 48, col * 48 + 48, r * 48 + 48))


def _c(h):
    return _hexc(h) if isinstance(h, str) else h


def _spec(parts, **colours):
    return {"parts": parts, "colours": {k.replace("__", "@"): _c(v) for k, v in colours.items()}}


def hero_specs():
    from art.figures import FIG
    f = FIG
    return _with_eyes({
        # Dain: snouted head + tail recoloured to crimson scales, charcoal plate over red straps
        "C01": _spec(dict(head="head20", top="top11", bottom="bottom8", backextra="tail1", weapon="sword1"),
                     skin=f["C01"]["skin"], cape=f["C01"]["skin"], cloth=f["C01"]["top"], leather=f["C01"]["accent"],
                     legs=f["C01"]["legs"], boots="4a3a3a"),
        # Tessa: short dark bob, cobalt long coat, amber spectacles
        "C02": _spec(dict(head="head1", hair="hair11", top="top4", bottom="bottom1", frontextra="frontextra8"),
                     skin=f["C02"]["skin"], hair=f["C02"]["hair"], cloth=f["C02"]["top"], legs=f["C02"]["legs"],
                     boots=f["C02"]["boots"], fx=f["C02"]["goggles"], eye="5a3a2a"),
        # Corren: messy brown hair, teal breastplate + ochre scarf (capelet recoloured), leather harness
        "C03": _spec(dict(head="head1", hair="hair4", top="top10", bottom="bottom2", weapon="spear1"),
                     skin=f["C03"]["skin"], hair=f["C03"]["hair"], cloth=f["C03"]["top"], white=f["C03"]["scarf"],
                     leather=f["C03"]["harness"], legs=f["C03"]["legs"], boots=f["C03"]["boots"], trim=f["C03"]["scarf"]),
        # Ivo: grey curls + beard, cream shirt with rolled sleeves under a dark apron-vest, copper rig belt
        "C04": _spec(dict(head="head1", hair="hair25", frontextra="frontextra1", top="top5", bottom="bottom3", weapon="hammer"),
                     skin=f["C04"]["skin"], hair=f["C04"]["hair"], fx=f["C04"]["beard"], cloth=f["C04"]["top"],
                     leather=f["C04"]["apron"], legs=f["C04"]["legs"], boots=f["C04"]["boots"], white=f["C04"]["rig"]),
        # Nera: long dark braid, moss cape, khaki tunic
        "C05": _spec(dict(head="head1", hair="hair5", backhair="backhair4", top="top2", bottom="bottom6",
                          backextra="backextra1", weapon="bow1arrow1"),
                     skin=f["C05"]["skin"], hair=f["C05"]["hair"], backhair=f["C05"]["hair"], tie=f["C05"]["maptube"],
                     cloth=f["C05"]["top"], cape=f["C05"]["cape"], legs=f["C05"]["legs"], boots=f["C05"]["boots"],
                     trim=f["C05"]["maptube"]),
        # Oriel: cropped silver hair, plum robe + skirt, ivory stole (gold trim -> brass)
        "C06": _spec(dict(head="head1", hair="hair7", top="top8", bottom="bottom5"),
                     skin=f["C06"]["skin"], hair=f["C06"]["hair"], cloth=f["C06"]["top"], leather=f["C06"]["stole"],
                     gold=f["C06"]["bell"], legs=f["C06"]["legs"], trim=f["C06"]["stole"], boots=f["C06"]["boots"]),
        # Sable: black hair tied back with a white tie, black-violet long coat
        "C07": _spec(dict(head="head1", hair="hair5", backhair="backhair5", top="top4", bottom="bottom1", weapon="sword4"),
                     skin=f["C07"]["skin"], hair=f["C07"]["hair"], backhair=f["C07"]["hair"], tie="eeeef4",
                     cloth=f["C07"]["top"], legs=f["C07"]["legs"], boots="2a2230", eye=f["C07"]["eye"]),
        # Pip: short brown curls, cream shirt + rust waistcoat, green sash
        "C08": _spec(dict(head="head1", hair="hair6", top="top5", bottom="bottom2", weapon="daggers"),
                     skin=f["C08"]["skin"], hair=f["C08"]["hair"], cloth=f["C08"]["top"], leather=f["C08"]["waistcoat"],
                     legs=f["C08"]["legs"], boots=f["C08"]["boots"], trim=f["C08"]["sash"]),
    }, f)


def _with_eyes(specs, figs):
    for k, sp in specs.items():
        sp["colours"].setdefault("eye", figs[k].get("eye", _hexc("2a1a10")))
    return specs


def npc_specs():
    from art.figures import NPCS as N
    def s(k, parts, **kw):
        n = N[k]
        base = dict(skin=n["skin"], hair=n["hair"], backhair=n["hair"], cloth=n["top"], legs=n["legs"], boots="3a2a24", eye=n["eye"])
        base.update(kw)
        return _spec(parts, **base)
    return {
        "mara": s("mara", dict(head="head1", hair="hair5", backhair="backhair2", top="top7", bottom="bottom5"), leather=N["mara"]["apron"], white="e8e0d0"),
        "inspector": s("inspector", dict(head="head7", hair="hair5", top="top3", bottom="bottom1", hat="hat11"), hat2=N["inspector"]["hat"], leather="3a3440"),
        "rook": s("rook", dict(head="head1", hair="hair4", frontextra="frontextra8", top="top4", bottom="bottom1"), fx="5a5a60"),
        "voss": s("voss", dict(head="head7", hair="hair3", top="top12", bottom="bottom8", backextra="backextra1"), white=N["voss"]["gauntlet"], cape=N["voss"]["cape"], leather="3a2a2a"),
        "pell": s("pell", dict(head="head1", hair="hair1", top="top7", bottom="bottom2"), leather=N["pell"]["apron"], white="d0d0c8"),
        "jori": s("jori", dict(head="head2", hair="hair6", frontextra="frontextra8", top="top1", bottom="bottom3"), fx="6a6a70", leather="5a4a3a"),
        "edda": s("edda", dict(head="head4", hair="hair5", backhair="backhair5", top="top10", bottom="bottom2"), white=N["edda"]["scarf"], tie=N["edda"]["scarf"]),
        "sen": s("sen", dict(head="head4", hair="hair22", backhair="backhair9", top="top8", bottom="bottom5"), leather="e8e0f0", gold="c0a0e0"),
        "ansel": s("ansel", dict(head="head5", hair="hair3", top="top1", bottom="bottom1"), leather="4a4450"),
        "ilyr": s("ilyr", dict(head="head20", hair="hair4", top="top2", bottom="bottom3", backextra="tail2"), cape=N["ilyr"]["skin"]),
        "worker": s("worker", dict(head="head2", top="top9", bottom="bottom3", hat="hat12"), leather="6a5a44"),
        "clerk": s("clerk", dict(head="head6", hair="hair5", top="top1", bottom="bottom1"), leather="3a3a44"),
        "keeper": s("keeper", dict(head="head1", hair="hair1", top="top7", bottom="bottom2"), leather=N["keeper"]["apron"]),
        "sailor": s("sailor", dict(head="head2", hair="hair3", top="top25", bottom="bottom1", hat="hat11"), hat2=N["sailor"]["hat"]),
        "volunteer": s("volunteer", dict(head="head20", hair="hair22", top="top9", bottom="bottom2", backextra="tail1"), cape=N["volunteer"]["skin"]),
        "survivor": s("survivor", dict(head="head3", hair="hair7", top="top2", bottom="bottom3")),
        "apprentice": s("apprentice", dict(head="head4", hair="hair10", top="top4", bottom="bottom1")),
        "patient": s("patient", dict(head="head4", hair="hair22", backhair="backhair1", top="top8", bottom="bottom5"), leather="c8c0b0", gold="c8c0b0"),
        "scholar": s("scholar", dict(head="head4", hair="hair22", backhair="backhair2", frontextra="frontextra8", top="top8", bottom="bottom5"), fx="8a8a90", leather="3a2a3a"),
        "pilot": s("pilot", dict(head="head2", hair="hair3", frontextra="frontextra3", top="top10", bottom="bottom8"), white=N["pilot"]["scarf"], fx="a07a3a"),
        "soldier": s("soldier", dict(head="head1", top="top11", bottom="bottom8", hat="hat6"), hat="8a8a94", leather="4a3a2a"),
        "noble": s("noble", dict(head="head4", hair="hair22", backhair="backhair10", top="top27", bottom="bottom5"), gold="e0c060"),
    }


# NPC-animation (finalbossblues) characters used as drawn, for generic roles.
NA = "finalbossblues/npc-animations/individual_frames/"
NPC_ANIM = {"child": ("children", "child1"), "elder": ("elders", "elder2"), "guard": ("knights", "knight1"),
            "farmer": ("farmer", "farmer1"), "baker": ("household", "chef"), "monk": ("townsfolk", "folk3")}

WORLD_POSES = [("down", 4), ("down", 6), ("down", 0), ("down", 5), ("down", 1), ("down", 6)]   # Elements cols


def el_world_sheet(full):
    from PIL import Image
    img = Image.new("RGBA", (CW * 6, CH * 5), (0, 0, 0, 0))
    ox, oy = EL_BOX
    def cell(fr):
        return fr.crop((ox, oy, ox + CW, oy + CH))
    for r, d in enumerate(["down", "left", "right", "up"]):
        for i, col in enumerate([1, 0, 1, 2, 1]):
            img.paste(cell(el_frame(full, d, col)), (i * CW, r * CH))
    for i, (d, col) in enumerate(WORLD_POSES):
        img.paste(cell(el_frame(full, d, col)), (i * CW, 4 * CH))
    return img


def na_world_sheet(folder, name):
    from PIL import Image
    img = Image.new("RGBA", (CW * 6, CH * 5), (0, 0, 0, 0))
    ox, oy = NA_BOX
    srcs = []
    def fr(d, k):
        rel = f"{NA}{folder}/{name}_{d} ({k}).png"
        srcs.append(rel)
        return _lib_img(rel).crop((ox, oy, ox + CW, oy + CH))
    for r, d in enumerate(["down", "left", "right", "up"]):
        for i, k in enumerate([2, 1, 2, 3, 2]):
            img.paste(fr(d, k), (i * CW, r * CH))
    for i, (d, k) in enumerate([("down", 1), ("down", 3), ("left", 2), ("right", 2), ("down", 2), ("up", 2)]):
        img.paste(fr(d, k), (i * CW, 4 * CH))
    return img, srcs


# Dain: Time Fantasy Beast Tribes lizard hero (walk + emote sheets and matching MV side-view battler), recoloured
# from green scales / grey plate / brown cape to crimson scales / charcoal plate / dark-red cloth.
DAIN_SRC = {"walk": "finalbossblues/100/beast_hero_3.png", "emote": "finalbossblues/100/beast_hero_3_emote.png",
            "sv": "finalbossblues/100/sv_battler/beast_hero_3_sv.png"}
TF_OUTLINE = (53, 64, 72)


def dain_lut():
    from art.figures import FIG
    f = FIG["C01"]
    lut = {}
    lut.update(_ramp_map(None, f["skin"], ["2f4d41", "2f7132", "4aa10d", "89bc1e"], 2))
    lut.update(_ramp_map(None, f["top"], ["484562", "485369", "748c7d", "aec3be"], 2))
    lut.update(_ramp_map(None, f["accent"], ["6c3c4a", "7d5643", "9b6b53", "bf8264"], 2))
    return lut


def tf_recolour(img, lut, strip_shadow=True, feet=None):
    """Apply a colour LUT; optionally drop Time Fantasy's baked ground shadow (outline-coloured pixels below the
    feet row of each frame: `feet` = (frame_h, feet_row))."""
    img = img.copy()
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            p = px[x, y]
            if p[3] and p[:3] in lut:
                px[x, y] = lut[p[:3]] + (p[3],)
    if strip_shadow and feet:
        fh, fr = feet
        for y in range(img.height):
            if y % fh <= fr:
                continue
            for x in range(img.width):
                p = px[x, y]
                if p[3] and p[:3] == TF_OUTLINE:
                    above = px[x, y - 1]
                    if not (y % fh == fr + 1 and above[3] and above[:3] != TF_OUTLINE):
                        px[x, y] = (0, 0, 0, 0)
    return img


def dain_world_sheet():
    from PIL import Image
    walk = tf_recolour(_lib_img(DAIN_SRC["walk"]), dain_lut(), feet=(36, 32))
    emo = tf_recolour(_lib_img(DAIN_SRC["emote"]), dain_lut(), feet=(36, 32))
    img = Image.new("RGBA", (CW * 6, CH * 5), (0, 0, 0, 0))
    ox, oy = (CW - 26) // 2, 1                     # TF feet row 32 -> cell row 33, like the Elements cells
    for r in range(4):
        for i, k in enumerate([1, 0, 1, 2, 1]):
            img.paste(walk.crop((k * 26, r * 36, k * 26 + 26, r * 36 + 36)), (i * CW + ox, r * CH + oy))
    for i, (r, k) in enumerate([(3, 0), (1, 1), (0, 0), (3, 1), (0, 1), (1, 2)]):
        img.paste(emo.crop((k * 26, r * 36, k * 26 + 26, r * 36 + 36)), (i * CW + ox, 4 * CH + oy))
    return img, [DAIN_SRC["walk"], DAIN_SRC["emote"]]


def build_library(save_ext):
    note = f"{CW}x{CH}; rows down,left,right,up (idle + TF walk 0,1,2,1); row4 six poses"
    img, srcs = dain_world_sheet()
    save_ext(img, "sprites/world/C01.png", "world_sprite", srcs, note, "TF Beast Tribes lizard hero, recoloured")
    for cid, spec in list(hero_specs().items()) + list(npc_specs().items()):
        if cid == "C01":
            continue
        full, srcs = el_compose(spec)
        save_ext(el_world_sheet(full), f"sprites/world/{cid}.png", "world_sprite", srcs, note,
                 "Time Fantasy Elements pieces, palette-remapped to docs/03 colours")
    for cid, (folder, name) in NPC_ANIM.items():
        img, srcs = na_world_sheet(folder, name)
        save_ext(img, f"sprites/world/{cid}.png", "world_sprite", srcs, note, "Time Fantasy NPC animations")
