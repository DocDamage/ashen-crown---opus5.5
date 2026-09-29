"""320x168 battle backgrounds: stepped-band backdrop, mid-ground silhouettes, perspective floor."""
import math, random
from PIL import Image
from art.pix import Canvas, shade, hexc, mix, dither

BG = {
    # id: (sky_top, sky_bottom, far, mid, floor, accent, feature)
    "quarry": ("1e1a1c", "4a3a30", "5a4a3e", "3a3028", "6a5a48", "f0b040", "quarry"),
    "underways": ("0e1016", "2a2e3a", "383c48", "22262e", "44484e", "a82a2a", "arches"),
    "grove": ("2a4a2a", "6a8a4a", "3a5a2a", "243a1a", "5a6a3a", "d0a050", "trees"),
    "grove_flood": ("1e3a3e", "4a7a6a", "2e4a3a", "1a2e24", "3a5a5a", "a0e0e0", "trees_water"),
    "furnace": ("1a0e0a", "5a2a14", "4a3026", "2a1a14", "5a4638", "ff7a30", "pipes"),
    "archive": ("0e2a30", "3a7a7a", "a89a7e", "6a5e4a", "c8bc9e", "40a0a0", "shelves"),
    "sky": ("2a3a7a", "a8c0e0", "c8d0e0", "6a6a78", "a8a8a0", "d09a38", "cables"),
    "whitebone": ("3a4458", "a8b0c0", "d8d8dc", "8a8a98", "c8c8cc", "8a6ac8", "cells"),
    "vault": ("1a1028", "4a3a6a", "7a6a9a", "3a2a4a", "8a7a9a", "f0c070", "vault"),
    "conduit": ("080810", "22222c", "2e2e38", "14141c", "3a3a44", "ff4a4a", "machines"),
    "dais": ("100810", "3a1a2a", "4a2a3a", "1a0e14", "4a3a4a", "ff5a4a", "dais"),
    "crown": ("0a0a1a", "2a1a3a", "4a3a4a", "1a121a", "4a3a4a", "ffd080", "crown"),
    "crown_core": ("140608", "4a1014", "5a2a2a", "1e0a0c", "3a2a2e", "ff6a4a", "core"),
    "winter": ("5a7aa0", "d0e0f0", "e8f0f8", "a0b8d0", "d8e4f0", "ffc060", "ice"),
    "reef": ("020810", "0e2a4a", "1a3a5a", "081a2a", "2a3a4a", "80e0e0", "reef"),
    "field_r01": ("4a7ab8", "b0d0e8", "6a9a5a", "4a7a3a", "7a9a4a", "f0e0a0", "hills"),
    "field_r02": ("5a4a5a", "c09070", "6a5040", "4a3830", "7a6048", "ff8a40", "ridges"),
    "field_r03": ("3a7aa8", "b8e0e8", "d8ccae", "5a8a7a", "d8c8a0", "40a0a0", "coast"),
    "field_r04": ("3a4a8a", "c0c8e0", "a8a8a8", "6a6a7a", "a8a898", "c89a3a", "cliffs"),
    "field_r05": ("3a2a5a", "c8b8e0", "d8cce8", "8a7aa0", "c8bcd8", "e8e0f0", "salt"),
    "field_post": ("2a2030", "7a5a5a", "4a3a3e", "2a2228", "5a4a48", "e05a3a", "ash"),
}


def build_bg(key):
    top, bot, far, mid, floor, acc, feat = [hexc(v) if i < 6 else v for i, v in enumerate(BG[key])]
    c = Canvas(320, 168)
    rnd = random.Random(key)
    horizon = 96
    # stepped dithered backdrop
    bands = 8
    for y in range(horizon):
        t = y / horizon
        b = int(t * bands) / bands
        b2 = min(1.0, b + 1.0 / bands)
        frac = (t - b) * bands
        for x in range(320):
            col = mix(top, bot, b2 if dither(x, y, frac) else b)
            c.put(x, y, col, 1)
    # far silhouettes
    for x in range(0, 320):
        h = 18 + int(10 * math.sin(x * 0.03 + len(key)) + 6 * math.sin(x * 0.11))
        for y in range(horizon - h, horizon):
            c.put(x, y, far if y > horizon - h + 1 else shade(far, 0.2), 2)
    # floor with perspective lines
    for y in range(horizon, 168):
        t = (y - horizon) / (168 - horizon)
        for x in range(320):
            col = shade(floor, -0.25 + t * 0.3)
            if (y - horizon) % max(2, int(3 + t * 10)) == 0:
                col = shade(col, -0.1)
            c.put(x, y, col, 3)
    for i in range(-8, 9):
        x0 = 160 + i * 14
        x1 = 160 + i * 60
        c.line(x0, horizon, x1, 167, shade(floor, -0.18), 1, 3)
    # features
    if feat == "quarry":
        for x in (20, 90, 250, 300):
            c.poly([(x - 16, horizon + 4), (x - 6, 20), (x + 10, 30), (x + 18, horizon + 4)], mid, 4)
        c.line(0, 70, 320, 64, (90, 80, 70, 255), 2, 5)
        for x in range(0, 320, 12):
            c.rect(x, 64, x + 2, 72, (70, 56, 40, 255), 5)
        for (x, y) in ((140, 40), (200, 30), (60, 50)):
            c.ellipse(x, y, 3, 5, (200, 70, 80, 255), 6)
            c.put(x - 1, y - 2, (255, 180, 180, 255), 6)
    elif feat == "arches":
        for x in range(0, 330, 64):
            c.rect(x, 10, x + 10, horizon + 6, mid, 4)
            for a in range(0, 54):
                y = 30 - int(18 * math.sin(a / 54 * math.pi))
                c.rect(x + 10 + a, y, x + 10 + a, y + 5, mid, 4)
        c.rect(0, horizon - 8, 320, horizon + 2, (30, 60, 80, 255), 5)
    elif feat in ("trees", "trees_water"):
        for i in range(9):
            x = 10 + i * 38 + rnd.randint(-8, 8)
            c.rect(x - 3, 30, x + 3, horizon + 6, shade(mid, -0.2), 4)
            c.ellipse(x, 30, 22, 20, mid, 4)
            c.ellipse(x - 6, 24, 10, 8, shade(mid, 0.15), 4)
        if feat == "trees_water":
            for y in range(120, 168):
                for x in range(320):
                    if dither(x, y, 0.5):
                        c.put(x, y, mix(c.get(x, y), hexc("2e5a6a"), 0.6), 3)
    elif feat == "pipes":
        for x in range(10, 320, 46):
            c.rect(x, 0, x + 10, horizon + 4, (120, 80, 50, 255), 4)
            c.rect(x, 0, x + 2, horizon + 4, (170, 120, 70, 255), 4)
            for y in (20, 60):
                c.rect(x - 2, y, x + 12, y + 3, (90, 60, 40, 255), 4)
        for i in range(30):
            c.put(rnd.randrange(320), rnd.randrange(horizon), acc, 6)
    elif feat == "shelves":
        for x in range(0, 320, 40):
            c.rect(x + 2, 16, x + 36, horizon, shade(mid, -0.1), 4)
            for y in range(20, horizon, 10):
                c.rect(x + 4, y, x + 34, y + 1, shade(mid, 0.2), 4)
                for bx in range(x + 5, x + 33, 3):
                    c.rect(bx, y - 7, bx + 1, y - 1, [acc, hexc("c05a3a"), hexc("d8c890")][rnd.randrange(3)], 5)
        for y in range(130, 168):
            for x in range(320):
                if dither(x, y, 0.35):
                    c.put(x, y, mix(c.get(x, y), hexc("2a8a8a"), 0.4), 3)
    elif feat == "cables":
        for i in range(4):
            c.line(0, 20 + i * 18, 320, 40 + i * 10, (60, 60, 70, 255), 2, 4)
        for x in (40, 280):
            c.rect(x, 10, x + 14, horizon + 10, (120, 120, 130, 255), 4)
        for i in range(12):
            x, y = rnd.randrange(320), rnd.randrange(60)
            c.ellipse(x, y, 14, 4, (230, 236, 244, 255), 5)
    elif feat == "cells":
        for x in range(0, 320, 50):
            c.rect(x + 4, 20, x + 44, horizon, mid, 4)
            for bx in range(x + 8, x + 42, 5):
                c.rect(bx, 24, bx + 1, horizon - 2, shade(mid, -0.35), 4)
        for i in range(40):
            c.put(rnd.randrange(320), rnd.randrange(horizon), (255, 255, 255, 255), 6)
    elif feat == "vault":
        for r in (140, 110, 80):
            for a in range(0, 180):
                x = 160 + int(r * math.cos(math.radians(a)))
                y = horizon + 10 - int(r * 0.5 * math.sin(math.radians(a)))
                if 0 <= y < horizon + 10:
                    c.rect(x, y, x + 1, y + 1, shade(mid, 0.2), 4)
        for x in (60, 160, 260):
            c.ellipse(x, 60, 5, 5, acc, 5)
    elif feat in ("machines", "dais", "crown", "core"):
        for x in range(0, 320, 36):
            c.rect(x, 20, x + 24, horizon + 4, mid, 4)
            c.rect(x + 8, 30, x + 16, 36, acc if (x // 36) % 2 == 0 else shade(acc, -0.5), 5)
        if feat == "dais":
            c.poly([(90, horizon + 20), (230, horizon + 20), (200, horizon - 10), (120, horizon - 10)], shade(floor, 0.1), 5)
        if feat in ("crown", "core"):
            for a in range(12):
                ang = a * math.pi / 6
                c.line(160, 50, 160 + math.cos(ang) * 150, 50 + math.sin(ang) * 60, shade(acc, -0.4), 1, 6)
            c.ellipse(160, 50, 18, 18, acc if feat == "core" else shade(acc, -0.3), 6)
    elif feat == "ice":
        for i in range(10):
            x = rnd.randrange(320)
            c.poly([(x - 8, horizon + 4), (x, horizon - 40 - rnd.randrange(30)), (x + 8, horizon + 4)], (220, 236, 250, 255), 4)
        for i in range(60):
            c.put(rnd.randrange(320), rnd.randrange(168), (255, 255, 255, 255), 6)
    elif feat == "reef":
        for i in range(14):
            x = rnd.randrange(320)
            c.ellipse(x, horizon + rnd.randrange(-10, 10), 12, 20, (60, 40, 60, 255), 4)
        for i in range(8):
            c.ellipse(rnd.randrange(320), rnd.randrange(80), 2, 2, acc, 6)
    elif feat in ("hills", "ridges", "coast", "cliffs", "salt", "ash"):
        for i in range(5):
            x = rnd.randrange(320)
            c.ellipse(x, horizon + 4, 50, 22, mid, 4)
        if feat == "coast":
            c.rect(0, horizon - 6, 320, horizon, hexc("2a8aa8"), 5)
        if feat == "ash":
            for i in range(50):
                c.put(rnd.randrange(320), rnd.randrange(horizon), acc if i % 5 == 0 else (120, 110, 110, 255), 6)
    return c.image()


def build(save):
    for k in BG:
        img = build_bg(k)
        spec = LIB_BG.get(k)
        if spec:   # same painted perspective ground + set pieces as the library panoramas (no library needed)
            img = _props(_ground(img, spec), spec.get("props", k), spec)
        save(img.convert("RGB"), f"sprites/bg/{k}.png", "battle_bg", "320x168", k)


# =================================================================================================================
# FF6-style panoramas from the owner's library (ansimuz Legacy Collection parallax layers) -> game/assets/ext/.
# Upper band: parallax layers composited at 1x (never resampled), tiled horizontally, colour-graded to the region.
# Lower band: a painted perspective ground plane (projected procedural texture, haze at the horizon) whose ramp is
# sampled from the panorama so the two halves read as one place, plus region set pieces painted with the same
# volume shader as the enemies (tools/art/enemies.paint).
# =================================================================================================================
AN = "ansimuz/Legacy Collection/Assets/"
GE = AN + "Gothicvania/Environments/"
WE = AN + "Warped/Environments/"
TE = AN + "TinyRPG/Environments/"
HZ = 96   # screen horizon row

# layers: [(path, top_y or None=bottom-aligned in a 240-high composite, x_offset)]; hz: composite row placed at
# the screen horizon; grade: (shadow, mid, light, strength); ground: (texture, dark, mid, light, accent)
LIB_BG = {
    "quarry": dict(layers=[(GE + "Mountain Dusk/Version C/layers/sky.png", None, 0), (GE + "Mountain Dusk/Version C/layers/far-mountains.png", None, 0),
                           (GE + "Mountain Dusk/Version C/layers/canyon.png", None, 90)],
                   hz=168, grade=("241a20", "7a6450", "ecd8b0", 0.7), ground=("dirt", "4a3a2e", "7a6248", "a88a64", "f0b040"),
                   props="quarry"),
    "underways": dict(layers=[(WE + "bulkhead-walls/v1/layers/bulkhead-walls-back.png", None, 0),
                              (WE + "bulkhead-walls/v1/layers/cols.png", None, 0),
                              (WE + "bulkhead-walls/v1/layers/bulkhead-walls-pipes.png", None, 0)],
                      hz=196, grade=("0e1420", "3a4a5a", "b8c8c0", 0.35), ground=("canal", "1a2230", "3a4654", "68788a", "a8d0d0"),
                      props="underways"),
    "grove": dict(layers=[(GE + "forest-road-background/PNG/back.png", None, 0), (GE + "forest-road-background/PNG/middle.png", None, 0)],
                  hz=214, grade=("122418", "4a6a34", "e0e0a0", 0.2), ground=("grass", "243a1c", "4a6a2c", "7a9a44", "d0a050"),
                  props="grove"),
    "grove_flood": dict(layers=[(GE + "mist-forest-background/layers/mist-forest-background-back.png", None, 0),
                                (GE + "mist-forest-background/layers/mist-forest-background-back-trees.png", None, 0),
                                (GE + "mist-forest-background/layers/mist-forest-background-tree.png", None, 20)],
                        hz=196, grade=("14302e", "4a7a6a", "d8f0e0", 0.3), ground=("water", "163a3a", "2e5a58", "6a9a90", "c8f0e8"),
                        props="grove_flood"),
    "furnace": dict(layers=[(WE + "parallax-industrial-web/Layers/bg.png", None, 0), (WE + "parallax-industrial-web/Layers/far-buildings.png", None, 0),
                            (WE + "parallax-industrial-web/Layers/buildings.png", None, 30)],
                    hz=214, grade=("200a0c", "8a3a20", "ffc070", 0.8), ground=("grate", "2a1a16", "5a3a2a", "8a5a3a", "ff7a30"),
                    props="furnace"),
    "archive": dict(layers=[(GE + "Old-dark-Castle-tileset-Files/PNG/old-dark-castle-interior-background.png", None, -40)],
                    hz=196, grade=("0e2230", "3a6a6a", "e8e8c8", 0.45), ground=("flood_tiles", "12303a", "2e5a60", "6a9a94", "e8f0d0"),
                    props="archive"),
    "sky": dict(layers=[(GE + "Day-Platformer/PNG/sky.png", "fill", 0), (GE + "Day-Platformer/PNG/clouds.png", 70, 0),
                        (WE + "Ocean View Files/Layers/Day/Clouds.png", 40, 100)],
                hz=200, grade=("2a3a7a", "7a90c0", "fff8e8", 0.2), ground=("stone", "5a5a6a", "8a8a94", "c0c0c4", "d09a38"),
                props="sky"),
    "whitebone": dict(layers=[(GE + "Gothic-Castle-Files/PNG/layers/gothic-castle-background.png", None, 0)],
                      hz=212, grade=("2a2c44", "9a9ab0", "fbf8f0", 0.7), ground=("tiles", "6a6a80", "a8a8b8", "e0e0e8", "8a6ac8"),
                      props="whitebone"),
    "vault": dict(layers=[(GE + "treasure-hoard-platform/PNG/background.png", None, 0), (GE + "treasure-hoard-platform/PNG/back-gold.png", None, 0)],
                  hz=200, grade=("24163a", "8a6aa8", "f8e4d0", 0.85), ground=("crystal", "2a1e3e", "5a4a7a", "9a8ab8", "f0c070"),
                  props="vault"),
    "conduit": dict(layers=[(WE + "Scifi lab Files/layers/back.png", None, 0), (WE + "Scifi lab Files/layers/middle.png", None, 0)],
                    hz=200, grade=("140810", "5a2a34", "ffa090", 0.7), ground=("grate", "1a1418", "3a2e34", "5a4a50", "ff4a4a"),
                    props="conduit"),
    "dais": dict(layers=[(WE + "alien-environment/PNG/layers/background.png", None, 0), (WE + "alien-environment/PNG/layers/back-structures.png", None, 0)],
                 hz=204, grade=("140610", "5a1e2a", "ffb090", 0.75), ground=("dais", "1e1016", "4a2a36", "7a4a56", "ff5a4a"),
                 props="dais"),
    "crown": dict(layers=[(WE + "another-world/PNG/layered/composed-bg.png", None, 0)],
                  hz=206, grade=("100820", "5a3a60", "ffe0a0", 0.65), ground=("tiles", "1e1428", "3e2e4a", "6a5a74", "ffd080"),
                  props="crown"),
    "crown_core": dict(layers=[(GE + "lava-background/PNG/background.png", None, 0), (GE + "lava-background/PNG/middle-rocks.png", None, 0)],
                       hz=200, grade=("1a0406", "6a1418", "ffb080", 0.55), ground=("grate", "1e0a0c", "3a1a1c", "6a2e2e", "ff6a4a"),
                       props="crown_core"),
    "winter": dict(layers=[(GE + "Mountain Dusk/version A/Layers/sky.png", None, 0), (GE + "Mountain Dusk/version A/Layers/far-clouds.png", None, 0),
                           (GE + "Mountain Dusk/version A/Layers/far-mountains.png", None, 0), (GE + "Mountain Dusk/version A/Layers/mountains.png", None, 0),
                           (GE + "Mountain Dusk/version A/Layers/trees.png", None, 0)],
                   hz=222, grade=("2a3a64", "7a98c0", "f8fcff", 0.8), ground=("snow", "7a90b0", "b8cce0", "eef4fa", "ffffff"),
                   props="winter"),
    "reef": dict(layers=[(GE + "Underwater Fantasy/PNG/layers/far.png", None, 0), (GE + "Underwater Fantasy/PNG/layers/sand.png", None, 0),
                         (GE + "Underwater Fantasy/PNG/layers/foreground-1.png", None, 0)],
                 hz=176, grade=("040c20", "1e4a6a", "a0e0e0", 0.35), ground=("sand", "0e2236", "24445a", "4a7080", "80e0e0"),
                 props="reef"),
    "field_r01": dict(layers=[(GE + "Day-Platformer/PNG/sky.png", "fill", 0), (GE + "Day-Platformer/PNG/clouds.png", 60, 0),
                              (GE + "Day-Platformer/PNG/trees.png", None, 0)],
                      hz=160, grade=("1e3a5a", "6a9a5a", "fff8d8", 0.15), ground=("grass", "3a5a24", "5a8a34", "8ab04a", "f0e0a0"),
                      props="field"),
    "field_r02": dict(layers=[(GE + "Rocky Pass Files/PNG/back.png", None, 0), (GE + "Rocky Pass Files/PNG/middle.png", None, 0)],
                      hz=176, grade=("2a1a24", "9a5a3a", "ffd8a0", 0.35), ground=("dirt", "4a2e24", "7a4a34", "a86a44", "ff8a40"),
                      props="ridges"),
    "field_r03": dict(layers=[(WE + "Ocean View Files/Layers/Day/Back.png", None, 0), (WE + "Ocean View Files/Layers/Day/Clouds.png", None, 0),
                              (WE + "Ocean View Files/Layers/Day/Middle.png", None, 0)],
                      hz=150, grade=("1a3a6a", "5a9ab0", "fff8e0", 0.15), ground=("sand", "8a7a5a", "c8b88c", "ece0b8", "40a0a0"),
                      props="coast"),
    "field_r04": dict(layers=[(GE + "Mountain Dusk/version B/Layers/sky.png", None, 0), (GE + "Mountain Dusk/version B/Layers/far-mountains.png", None, 0),
                              (GE + "Mountain Dusk/version B/Layers/middle-mountains.png", None, 0), (GE + "Mountain Dusk/version B/Layers/far-trees.png", None, 0)],
                      hz=212, grade=("283060", "7a88b0", "fff0d8", 0.55), ground=("rock", "4a4a58", "7a7a84", "a8a8a8", "c89a3a"),
                      props="cliffs"),
    "field_r05": dict(layers=[(GE + "Rocky Beach environment/layers/background.png", None, 0), (GE + "Rocky Beach environment/layers/mountain.png", None, 0)],
                      hz=200, grade=("3a2a5a", "a898c8", "fcf6ff", 0.7), ground=("salt", "8a7aa0", "c0b4d4", "ece6f4", "e8e0f0"),
                      props="salt"),
    "field_post": dict(layers=[(GE + "Gothic-Horror-Files/PNG/layers/clouds.png", None, 0), (GE + "Gothic-Horror-Files/PNG/layers/town.png", None, 0)],
                       hz=210, grade=("1e1418", "6a4a48", "f0b090", 0.75), ground=("ash", "2a2024", "4a3a3a", "6a5654", "e05a3a"),
                       props="ash"),
}


def _composite(spec):
    from art.pix import lib_img
    CH = 240
    comp = Image.new("RGBA", (320, CH), (0, 0, 0, 255))
    first = True
    for path, top, xo in spec["layers"]:
        im = lib_img(path)
        if top == "fill":
            # a narrow gradient strip: tile it across and extend its end rows (no resampling)
            strip = Image.new("RGBA", (320, CH))
            for x in range(0, 320, im.width):
                strip.paste(im, (x, 0))
            top_row = im.crop((0, 0, 1, 1)).resize((320, 1))
            bot_row = im.crop((0, im.height - 1, 1, im.height)).resize((320, 1))
            for y in range(im.height, CH):
                strip.paste(bot_row, (0, y))
            comp.alpha_composite(strip)
            first = False
            continue
        y = CH - im.height if top is None else top
        if first:
            # extend the first layer's top/bottom rows so the composite never shows void
            col_top = im.crop((0, 0, im.width, 1))
            for yy in range(0, max(0, y)):
                for x in range(-xo % im.width - im.width, 320, im.width):
                    comp.alpha_composite(col_top, (max(0, x), yy)) if x >= 0 else comp.alpha_composite(col_top.crop((-x, 0, im.width, 1)), (0, yy))
        x = -(xo % im.width)
        while x < 320:
            if x < 0:
                comp.alpha_composite(im.crop((-x, max(0, -y), im.width, im.height)), (0, max(0, y)))
            else:
                comp.alpha_composite(im.crop((0, max(0, -y), im.width, im.height)), (x, max(0, y)))
            x += im.width
        first = False
    return comp


def _grade(img, g):
    import numpy as np
    sh, md, li, k = hexc(g[0]), hexc(g[1]), hexc(g[2]), g[3]
    a = np.array(img).astype(float)
    lum = (a[:, :, :3] @ np.array([0.3, 0.59, 0.11])) / 255.0
    sh, md, li = [np.array(v[:3], float) for v in (sh, md, li)]
    t = np.clip(lum / 0.5, 0, 1)[..., None]
    t2 = np.clip((lum - 0.5) / 0.5, 0, 1)[..., None]
    gm = np.where((lum < 0.5)[..., None], sh + (md - sh) * t, md + (li - md) * t2)
    a[:, :, :3] = a[:, :, :3] * (1 - k) + gm * k
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def _h(x, y, s=0):
    """Deterministic hash noise in [0,1)."""
    n = (x * 374761393 + y * 668265263 + s * 2147483647) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65536.0


def _vnoise(u, v, s=0):
    iu, iv = math.floor(u), math.floor(v)
    fu, fv = u - iu, v - iv
    fu, fv = fu * fu * (3 - 2 * fu), fv * fv * (3 - 2 * fv)
    a, b = _h(iu, iv, s), _h(iu + 1, iv, s)
    c, d = _h(iu, iv + 1, s), _h(iu + 1, iv + 1, s)
    return a + (b - a) * fu + (c - a) * fv + (a - b - c + d) * fu * fv


def _ground_val(kind, u, v, x, y):
    """Texture value in 0..4 (ramp index, float) plus an accent flag, for world coords (u,v)."""
    n = _vnoise(u * 2.2, v * 2.6, 1) * 0.55 + _vnoise(u * 5.5, v * 6.0, 2) * 0.45
    acc = False
    if kind in ("dirt", "ash", "rock"):
        val = 1.4 + n * 1.8
        cell = _h(int(u * 0.8), int(v * 0.8), 5)
        if cell > 0.82 and (u * 0.8 % 1) < 0.5 and (v * 0.8 % 1) < 0.4:
            val = 3.2                         # scattered stones
        if kind == "ash" and _h(int(u * 3), int(v * 3), 9) > 0.985:
            acc = True
        if kind == "rock" and (_vnoise(u * 0.5, v * 1.5, 7) > 0.72):
            val = 0.8
    elif kind in ("tiles", "flood_tiles", "crystal", "dais", "stone"):
        su = 0.9 if kind != "dais" else 1.2
        tu, tv = u / su, v / su
        edge = (tu % 1) < 0.07 or (tv % 1) < 0.1
        base = 2.0 + (_h(int(tu), int(tv), 3) - 0.5) * 1.0 + n * 0.5
        val = 0.8 if edge else base

        if kind == "dais" and abs(u) < 1.2:
            val = 3.0 if not edge else 1.6
            acc = (tv % 1) < 0.1
    elif kind in ("grass",):
        val = 1.2 + n * 2.2
        if _h(int(u * 4), int(v * 6), 6) > 0.9:
            val += 1.0
    elif kind in ("water", "canal"):
        rip = math.sin(v * 9.0 + _vnoise(u * 1.6, v * 1.2, 3) * 4.0)
        val = 1.8 + rip * 0.5 + n * 0.3
        acc = rip > 0.92
        if kind == "canal" and abs(u) > 3.2:
            tu, tv = u / 1.4, v / 1.4
            val = 0.9 if ((tu % 1) < 0.08 or (tv % 1) < 0.12) else 2.2 + n * 0.6
            acc = False
    elif kind == "grate":
        tu, tv = u / 1.2, v / 1.2
        seamv = (tu % 1) < 0.06 or (tv % 1) < 0.09
        val = 0.6 if seamv else 1.8 + n * 1.2
        if not seamv and (tu % 1) > 0.85 and (tv % 1) > 0.8:
            val = 3.4                         # rivets
        acc = seamv and _vnoise(u * 0.4, v * 0.4, 8) > 0.62
    elif kind in ("snow", "salt"):
        val = 2.4 + n * 1.4
        acc = _h(int(u * 5), int(v * 7), 11) > 0.992
        if kind == "salt":
            su, sv = u * 1.3, v * 1.3
            ds = []
            for gx in range(int(math.floor(su)) - 1, int(math.floor(su)) + 2):
                for gy in range(int(math.floor(sv)) - 1, int(math.floor(sv)) + 2):
                    px_, py_ = gx + _h(gx, gy, 21), gy + _h(gx, gy, 22)
                    ds.append((px_ - su) ** 2 + (py_ - sv) ** 2)
            ds.sort()
            if math.sqrt(ds[1]) - math.sqrt(ds[0]) < 0.06:
                val = 1.1                     # polygonal salt-crust cracks
    elif kind == "sand":
        val = 1.8 + math.sin(v * 3.0 + u * 0.4 + n * 2) * 0.6 + n * 0.8
    else:
        val = 2 + n
    return val, acc


def _ground(img, spec):
    import numpy as np
    kind, dk, md, li, ac = spec["ground"]
    dk, md, li, ac = hexc(dk), hexc(md), hexc(li), hexc(ac)
    ramp = [shade(dk, -0.25), dk, md, li, shade(li, 0.25)]
    px = img.load()
    # haze colour: average of the panorama's last rows at the horizon
    a = np.array(img)[HZ - 6:HZ, :, :3].reshape(-1, 3).mean(0)
    haze = (int(a[0]), int(a[1]), int(a[2]), 255)
    for y in range(HZ, 168):
        d = y - HZ + 4.0
        z = 60.0 / d                   # depth
        for x in range(320):
            u = (x - 160) / 40.0 * z
            v = z * 1.2
            val, acc = _ground_val(kind, u, v, x, y)
            # 2x2 ordered dither between ramp steps keeps the FF6 cluster look
            fl = math.floor(val)
            if (val - fl) > (0.44 + 0.12 * ((x + y) % 2)):
                fl += 1
            col = ramp[max(0, min(4, int(fl)))]
            if acc:
                col = mix(col, ac, 0.75)
            t = max(0.0, 1.0 - (y - HZ) / 26.0)
            col = mix(col, haze, t * 0.65)
            if y > 150:
                col = shade(col, -0.12 * (y - 150) / 18)
            px[x, y] = col
    # contact line / reflections for water floors
    if kind in ("water", "flood_tiles", "canal"):
        for y in range(HZ, 168):
            sy = 2 * HZ - y - 2
            if sy < 0:
                break
            wob = int(round(math.sin(y * 0.9) * 1.5))
            for x in range(320):
                if kind == "canal" and abs((x - 160) / 40.0 * 60.0 / (y - HZ + 4.0)) > 3.2:
                    continue
                r = px[max(0, min(319, x + wob)), sy]
                px[x, y] = mix(px[x, y], r, 0.35 * max(0, 1 - (y - HZ) / 60))
    return img


def _props(img, key, spec):
    """Region set pieces standing on the ground line, painted with the enemy volume shader."""
    from art.enemies import paint, cap, path, seam, rivet, glow
    from art.pix import Canvas
    c = Canvas(320, 168)
    rnd = random.Random(key)
    g = hexc(spec["ground"][2])
    ac = hexc(spec["ground"][4])
    if key == "quarry":
        wood = hexc("7a5a3a")
        for x0 in (6, 250):
            for k in range(3):
                cap(c, x0 + k * 22, 42, x0 + k * 22, HZ + 6, 2, 2, wood, 10 + k)
            for yy in (54, 76):
                cap(c, x0 - 4, yy, x0 + 50, yy, 1.6, 1.6, shade(wood, 0.1), 14)
            path(c, [(x0, HZ + 4), (x0 + 22, 54), (x0 + 44, HZ + 4)], [1.2, 1.2, 1.2], shade(wood, -0.1), 15)
        cap(c, 60, 30, 250, 36, 0.8, 0.8, hexc("3a3230"), 16)                      # cable
        c.poly([(150, 36), (170, 36), (168, 48), (152, 48)], hexc("8a6a3a"), 17)   # ore bucket
        for x, y in ((120, 70), (196, 64)):
            glow(c, x, y, 2, 3, hexc("f0b040"))
    elif key == "underways":
        for x0 in (-10, 150, 290):
            c.poly([(x0, 0), (x0 + 40, 0), (x0 + 40, HZ + 2), (x0, HZ + 2)], hexc("2a3240"), 10)
        glow(c, 130, 50, 3, 4, hexc("f0c070"))
        glow(c, 200, 50, 3, 4, hexc("f0c070"))
    elif key in ("grove", "grove_flood"):
        for x0 in (8, 292):
            path(c, [(x0, HZ + 8), (x0 + 3, 40), (x0 - 2, 0)], [9, 7, 6], hexc("4a3a28"), 10 + (x0 > 100))
            for k in range(4):
                path(c, [(x0, HZ + 4), (x0 - 10 + k * 7, HZ + 10)], [3, 1.5], hexc("3e3020"), 12)
    elif key == "furnace":
        for x0 in (20, 280):
            cap(c, x0, -4, x0, HZ + 4, 7, 7, hexc("6a4a36"), 10 + (x0 > 100))
            for yy in (18, 52, 80):
                c.rect(x0 - 9, yy, x0 + 9, yy + 3, hexc("4a3228"), 12)
        path(c, [(20, 30), (80, 30), (100, 12), (220, 12), (240, 30), (280, 30)], [4, 4, 4, 4, 4, 4], hexc("7a5a40"), 13)
        for x in (60, 150, 240):
            glow(c, x, HZ - 6, 5, 3, ac)
    elif key == "archive":
        book = [hexc("8a3a2a"), hexc("3a5a6a"), hexc("c8b070"), hexc("5a3a5a")]
        for x0 in (4, 244):
            c.rect(x0, 18, x0 + 70, HZ + 6, hexc("4a3424"), 10 + (x0 > 100))
            for yy in range(24, HZ, 14):
                c.rect(x0 + 3, yy, x0 + 67, yy + 10, hexc("20140e"), 8)
                xx = x0 + 4
                while xx < x0 + 64:
                    w = 2 + rnd.randrange(3)
                    c.rect(xx, yy + 2 + rnd.randrange(3), xx + w - 1, yy + 10, book[rnd.randrange(4)], 12 + rnd.randrange(3))
                    xx += w + 1
    elif key == "sky":
        for (x0, y0, w) in ((40, 60, 46), (250, 44, 56), (150, 30, 30)):
            c.ellipse(x0, y0, w, 7, hexc("9aa890"), 10)
            c.poly([(x0 - w * 0.8, y0 + 2), (x0 + w * 0.8, y0 + 2), (x0 + 4, y0 + w * 0.7)], hexc("7a6a5a"), 11)
            c.ellipse(x0 - w * 0.3, y0 - 8, w * 0.3, 8, hexc("4a7a4a"), 12)
        cap(c, 0, 20, 320, 40, 0.7, 0.7, hexc("3a3a4a"), 13)
    elif key == "whitebone":
        for x0 in range(0, 330, 64):
            c.rect(x0, 16, x0 + 10, HZ + 4, hexc("d8d8e0"), 10)
            c.ellipse(x0 + 5, 16, 8, 4, hexc("e8e8f0"), 11)
        for x0 in (100, 180):
            for k in range(6):
                cap(c, x0 + k * 7, 40, x0 + k * 7, HZ, 1.2, 1.2, hexc("8a8aa0"), 12)
            glow(c, x0 + 18, 34, 4, 2, ac)
    elif key == "vault":
        for (x0, h) in ((20, 50), (46, 30), (270, 60), (300, 36), (160, 24)):
            c.poly([(x0 - 8, HZ + 4), (x0, HZ - h), (x0 + 8, HZ + 4)], hexc("b8a0d8"), 10 + (x0 % 3))
        for x in (90, 230):
            glow(c, x, 60, 3, 4, ac)
    elif key in ("conduit", "dais", "crown_core"):
        for x0 in (14, 298):
            cap(c, x0, 0, x0, HZ + 4, 8, 8, hexc("3a3440"), 10 + (x0 > 100))
            for yy in range(10, HZ, 16):
                glow(c, x0, yy, 2, 1.5, ac)
        if key == "dais":
            c.ellipse(96, HZ + 34, 90, 20, hexc("3a2230"), 12)
            c.ellipse(96, HZ + 32, 80, 16, hexc("5a3440"), 13)
    elif key == "crown":
        for x0 in (30, 290):
            cap(c, x0, 10, x0, HZ + 6, 6, 6, hexc("4a3a54"), 10 + (x0 > 100))
            c.poly([(x0 - 10, 10), (x0 - 6, -4), (x0, 8), (x0 + 6, -4), (x0 + 10, 10)], hexc("c8a048"), 12)
    elif key == "winter":
        for (x0, h) in ((10, 40), (34, 24), (296, 46)):
            c.poly([(x0 - 10, HZ + 4), (x0, HZ - h), (x0 + 10, HZ + 4)], hexc("d0e4f4"), 10 + (x0 > 100))
    elif key == "reef":
        for x0 in (16, 300):
            for k in range(4):
                path(c, [(x0 + k * 5, HZ + 6), (x0 + k * 6 - 6, HZ - 30 - k * 8), (x0 + k * 4, HZ - 50 - k * 6)], [2, 1.6, 1], hexc("3a6a5a"), 10 + k)
        for k in range(10):
            c.ellipse(rnd.randrange(320), rnd.randrange(HZ), 1, 1, hexc("a0f0f0"), 8)
    elif key == "ash":
        for x0 in (40, 270):
            path(c, [(x0, HZ + 4), (x0 + 2, 50), (x0 - 8, 30)], [4, 3, 2], hexc("2a2224"), 10)
        for k in range(30):
            c.put(rnd.randrange(320), rnd.randrange(HZ), ac if k % 4 == 0 else hexc("8a7a78"), 8)
    img.alpha_composite(paint(c, texture=0.0).image())
    return img


def build_lib_bg(key):
    spec = LIB_BG[key]
    comp = _composite(spec)
    if spec.get("gain"):
        comp = comp.point(lambda v, g=spec["gain"]: min(255, int(v * g)))
    comp = _grade(comp, spec["grade"])
    top = spec["hz"] - HZ
    out = Image.new("RGBA", (320, 168), (0, 0, 0, 255))
    out.paste(comp.crop((0, max(0, top), 320, max(0, top) + 168)), (0, max(0, -top)))
    out = _ground(out, spec)
    out = _props(out, spec.get("props", key), spec)
    return out, [p for p, _, _ in spec["layers"]]


def build_library(save_ext):
    for key in LIB_BG:
        try:
            img, srcs = build_lib_bg(key)
        except FileNotFoundError as e:
            print("bgs: library source missing for", key, e)
            continue
        save_ext(img.convert("RGB"), f"sprites/bg/{key}.png", "battle_bg", srcs, "320x168",
                 "FF6-style panorama: graded parallax layers + painted perspective ground + painted set pieces")
