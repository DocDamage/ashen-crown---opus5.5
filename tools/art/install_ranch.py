"""Installs the owner's "Super Retro Ranch" pack (premium) for the ranches (game/src/meta/ranch.gd).

Source: $ASHEN_ASSETS/Ranching/SuperRetroRanch (the owner's folder:
F:\\Ashen Crown\\The Ashen Crown\\Assets\\Ranching\\SuperRetroRanch), or a folder given on the command line.
$ASHEN_ASSETS defaults to the "Assets" folder beside the repo.
Target: game/assets/ext/ranch/ (git-ignored licensed art):
  <key>/field.png + field.json   animals in the HeroArt field format (rows down/left/right/up, column 0 standing,
                                 1..4 walking), cut from the pack's 48px RPG Maker MV sheets
                                 (engines/RPG_Maker_MV_MZ/animals: 3x4 frames; 48x60 small animals, 96x96 cows and
                                 pigs). Keys: cow, cow_black, pig, pig_black, dove, bunny, cat, fox, mouse.
  crops.png + crops.json         crop plots: one row per crop (tools/content/ranch.py CROPS order), columns
                                 young / ripe, 54x96 cells. The pack has crops only at 16px: scaled x3 nearest.
  crate.png                      the produce crate (16px pack crate x3)
  icons.png                      ranch item icons, 16x16 cells, 8 per row, ranch.py ICON_ORDER (drawn at UI scale
                                 like the fishing icons)
The game draws clean fallbacks (shapes, no icons) for anything missing, so a partial install is safe.
After installing, run a Godot import once:  cd game && godot --headless --path . --import
Usage: python3 tools/art/install_ranch.py [PACK_DIR] [--out DIR] [--check]
  --check  only report which source files were found; --out writes somewhere other than game/assets/ext/ranch."""
import importlib.util, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ASSETS = os.environ.get("ASHEN_ASSETS", os.path.join(os.path.dirname(REPO), "Assets"))
OUT = os.path.join(REPO, "game", "assets", "ext", "ranch")

_spec = importlib.util.spec_from_file_location("ranch_content", os.path.join(REPO, "tools", "content", "ranch.py"))
RC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(RC)

MV = "engines/RPG_Maker_MV_MZ/animals/"
ANIMALS = {   # key -> 48px MV sheet (3 columns x 4 rows: down, left, right, up)
    "cow": MV + "cows/cow_01/brown/move/_RANCH_ANIMAL_cow_01_brown_move.png",
    "cow_black": MV + "cows/cow_01/black/move/_RANCH_ANIMAL_cow_01_black_move.png",
    "pig": MV + "pigs/pig_01/pink/move/_RANCH_ANIMAL_pig_01_pink_move.png",
    "pig_black": MV + "pigs/pig_01/black/move/_RANCH_ANIMAL_pig_01_black_move.png",
    "dove": MV + "birds/bird_01/fly/_RANCH_ANIMAL_bird_01_fly.png",
    "bunny": MV + "bunnies/bunny_01/move/_RANCH_ANIMAL_bunny_01_move.png",
    "cat": MV + "cats/cat_01/move/_RANCH_ANIMAL_cat_01_move.png",
    "fox": MV + "foxes/fox_01/move/_RANCH_ANIMAL_fox_01_move.png",
    "mouse": MV + "mouses/mouse_01/move/_RANCH_ANIMAL_mouse_01_move.png",
}
RIPE_FRAME = {"pepper": 9, "tomato": 17}          # default: frame 5 (frame 6 is the withered plant)
YOUNG_FRAME = {"pepper": 5, "tomato": 6}          # default: frame 2
ICON_FRAME = {"wheat": 5, "tomato": 3, "bamboo": 0, "pumpkin": 2}   # default: the last frame of the icon strip
CRATE = ("assets/objects/objects_01_16x16.png", 4, 2)   # 16px cell (column, row)
CELL = (54, 96)


def _img(path):
    from PIL import Image
    return Image.open(path).convert("RGBA")


def _frames(path):
    """A pack strip 'name_WxH_Nframes.png' -> list of frame images."""
    im = _img(path)
    m = re.search(r"_(\d+)x(\d+)(?:_(\d+)frames)?\.png$", os.path.basename(path))
    w, h = (int(m.group(1)), int(m.group(2))) if m else (im.height, im.height)
    n = int(m.group(3)) if m and m.group(3) else max(1, im.width // w)
    return [im.crop((i * w, 0, (i + 1) * w, h)) for i in range(n)]


def _find(src, rel_dir, pattern):
    d = os.path.join(src, rel_dir)
    if not os.path.isdir(d):
        return None
    for f in sorted(os.listdir(d)):
        if re.match(pattern, f):
            return os.path.join(d, f)
    return None


def install_animal(src, out, key, rel, check):
    p = os.path.join(src, rel)
    if not os.path.exists(p):
        print("  missing", key, rel)
        return False
    if check:
        print("  found", key)
        return True
    from PIL import Image
    im = _img(p)
    cw, ch = im.width // 3, im.height // 4
    sheet = Image.new("RGBA", (cw * 5, ch * 4))
    bottom = 0
    for row in range(4):
        for i, col in enumerate([1, 0, 1, 2, 1]):     # standing, then the RPG Maker walk cycle 0-1-2-1
            cell = im.crop((col * cw, row * ch, (col + 1) * cw, (row + 1) * ch))
            bb = cell.getbbox()
            if bb:
                bottom = max(bottom, bb[3])
            sheet.paste(cell, (i * cw, row * ch))
    d = os.path.join(out, key)
    os.makedirs(d, exist_ok=True)
    sheet.save(os.path.join(d, "field.png"))
    meta = {"cell": [cw, ch], "foot": [cw // 2, max(1, bottom - 1)], "fps": 6,
            "rows": {r: {"row": i, "n": 4} for i, r in enumerate(["down", "left", "right", "up"])}}
    json.dump(meta, open(os.path.join(d, "field.json"), "w"))
    return True


def _cell16(frame, w=16, h=16):
    """Bottom-centre a frame into a w x h cell (crops are bottom-aligned on their tile)."""
    from PIL import Image
    c = Image.new("RGBA", (w, h))
    c.paste(frame, ((w - frame.width) // 2, h - frame.height), frame)
    return c


def install_crops(src, out, check):
    from PIL import Image
    order = list(RC.CROPS)
    sheet = Image.new("RGBA", (CELL[0] * 2, CELL[1] * len(order)))
    seeds, ok = {}, 0
    for r, cid in enumerate(order):
        p = _find(src, "assets/crops/%s/growth_basic" % cid, r".*\.png$")
        if not p:
            print("  missing crop", cid)
            continue
        ok += 1
        if check:
            continue
        fr = _frames(p)
        ripe = fr[min(len(fr) - 1, RIPE_FRAME.get(cid, 5))]
        young = fr[min(len(fr) - 1, YOUNG_FRAME.get(cid, 2))]
        for c, f in enumerate([young, ripe]):
            big = f.resize((f.width * 3, f.height * 3), Image.NEAREST)
            sheet.paste(big, (c * CELL[0] + (CELL[0] - big.width) // 2, r * CELL[1] + CELL[1] - big.height), big)
        s = fr[0]
        seeds[cid] = s.crop((max(0, (s.width - 16) // 2), max(0, s.height - 16), max(0, (s.width - 16) // 2) + 16, s.height))
    if check or ok == 0:
        return ok, seeds
    sheet.save(os.path.join(out, "crops.png"))
    json.dump({"cell": list(CELL), "order": order, "cols": ["young", "ripe"]}, open(os.path.join(out, "crops.json"), "w"))
    return ok, seeds


def _recolor(im, fn):
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = fn(r, g, b) + (a,)
    return im


def install_icons(src, out, seeds, check):
    from PIL import Image
    A = os.path.join(src, "assets")

    def icon_of(cid):
        p = _find(src, "assets/crops/%s/icon" % cid, r".*\.png$")
        if not p:
            return None
        fr = _frames(p)
        return _cell16(fr[min(ICON_FRAME.get(cid, len(fr) - 1), len(fr) - 1)])

    def pack(rel, frame=0):
        p = os.path.join(A, rel)
        if not os.path.exists(p):
            return None
        fr = _frames(p)
        f = fr[min(frame, len(fr) - 1)]
        bb = f.getbbox()
        return _cell16(f.crop(bb) if bb else f)

    lum = lambda r, g, b: (r * 299 + g * 587 + b * 114) // 1000
    icons = {}
    pot = pack("icons/potion_01_16x16.png")
    if pot:
        # milk: the red draught turned white (outline and glass kept)
        icons["RK01"] = _recolor(pot.copy(), lambda r, g, b: (min(255, 150 + lum(r, g, b)),) * 2 + (min(255, 160 + lum(r, g, b)),)
                                 if r > g + 40 else (r, g, b))
        icons["RF01"] = pot
    icons["RK02"] = pack("animals/egg/idle/egg_idle_16x20.png")
    caul = icon_of("cauliflower")
    if caul:
        icons["RK03"] = _recolor(caul.copy(), lambda r, g, b: (min(255, 90 + lum(r, g, b)),) * 3 if lum(r, g, b) > 40 else (r, g, b))
        icons["RA01"] = _recolor(icons["RK03"].copy(), lambda r, g, b: (r, g * 45 // 100, b * 40 // 100) if lum(r, g, b) > 60 else (r, g, b))
    pota = icon_of("potato")
    if pota:
        icons["RK04"] = _recolor(pota.copy(), lambda r, g, b: (r * 40 // 100, g * 36 // 100, b * 40 // 100) if lum(r, g, b) > 30 else (r, g, b))
    for cid, v in RC.CROPS.items():
        ic = icon_of(cid)
        if ic:
            icons[v[0]] = ic
        if cid in seeds:
            icons[v[1]] = seeds[cid]
    icons["RF02"] = pack("animals/mouses/cheese_16x16_2frames.png", 1)
    icons["RF06"] = pack("animals/mouses/cheese_16x16_2frames.png", 0)
    icons["RF03"] = icon_of("pumpkin")
    icons["RF04"] = pack("icons/potion_02_16x16.png")
    icons["RF05"] = pack("icons/potion_03_16x16.png")
    have = [i for i in RC.ICON_ORDER if icons.get(i) is not None]
    print("  icons: %d of %d" % (len(have), len(RC.ICON_ORDER)))
    if check or not have:
        return len(have)
    rows = (len(RC.ICON_ORDER) + 7) // 8
    sheet = Image.new("RGBA", (128, rows * 16))
    for n, iid in enumerate(RC.ICON_ORDER):
        if icons.get(iid) is not None:
            sheet.paste(icons[iid], ((n % 8) * 16, (n // 8) * 16), icons[iid])
    sheet.save(os.path.join(out, "icons.png"))
    return len(have)


def install_crate(src, out, check):
    from PIL import Image
    p = os.path.join(src, CRATE[0])
    if not os.path.exists(p):
        print("  missing crate sheet")
        return False
    if check:
        return True
    im = _img(p)
    c = im.crop((CRATE[1] * 16, CRATE[2] * 16, CRATE[1] * 16 + 16, CRATE[2] * 16 + 16))
    bb = c.getbbox() or (0, 0, 16, 16)
    c = c.crop(bb)
    c.resize((c.width * 3, c.height * 3), Image.NEAREST).save(os.path.join(out, "crate.png"))
    return True


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check = "--check" in sys.argv
    out = OUT
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
        args = [a for a in args if a != out]
    src = args[0] if args else os.path.join(ASSETS, "Ranching", "SuperRetroRanch")
    if not os.path.isdir(src):
        print("install_ranch: pack not found at %s - nothing installed (the game draws fallbacks)" % src)
        return 0
    try:
        import PIL  # noqa: F401
    except ImportError:
        print("install_ranch: Pillow is required (pip install pillow)")
        return 1
    if not check:
        os.makedirs(out, exist_ok=True)
    print("install_ranch: %s -> %s%s" % (src, out, " (check only)" if check else ""))
    na = sum(install_animal(src, out, k, rel, check) for k, rel in ANIMALS.items())
    nc, seeds = install_crops(src, out, check)
    ni = install_icons(src, out, seeds, check)
    cr = install_crate(src, out, check)
    print("install_ranch: animals %d/%d, crops %d/%d, icons %d, crate %s" % (na, len(ANIMALS), nc, len(RC.CROPS), ni, "ok" if cr else "missing"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
