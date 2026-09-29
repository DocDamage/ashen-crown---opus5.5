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
