"""Installs the owner's "Super Retro Ranch" pack (premium v32, by Gif) for the ranches (game/src/meta/ranch.gd).
Read docs/expansion/RANCH_PACK.md first: it is the readme for the pack (sheet layouts, frame orders, anchors).

Source: $ASHEN_ASSETS/Ranching/SuperRetroRanch (the owner's folder:
F:\\Ashen Crown\\The Ashen Crown\\Assets\\Ranching\\SuperRetroRanch), or a folder given on the command line.
$ASHEN_ASSETS defaults to the "Assets" folder beside the repo.
Target: game/assets/ext/ranch/ (git-ignored licensed art). Everything stays native 16 px (1 pack pixel = 1 logical
unit, drawn x3 nearest by the game); the RPG Maker 48 px re-exports are not used.
  pack/<path>          the pack's assets/ tree as is (animals, characters, crops, objects, tiles, buildings, icons,
                       visual_effects, weathers, user_interfaces/themes)
  autotiles/<name>.png the Godot "3x3 minimal" terrain sheets (engines/Godot/autotiles/3x3, 12x4 tiles of 16 px;
                       water = 4 frames side by side) + template_godot_3x3.png (the bit layout); plus
                       field_wet.png: field_02 with the tilled soil darkened to the watered colour of field_04,
                       field_04_wet.png: field_04 (furrows on brown soil) darkened again
  icons.png            ranch item icons (16x16 cells, 8 per row, order tools/content/ranch.py ICON_ORDER): crop icons,
                       signposts with crop icons as seed packets, egg, milk, wool, truffle, tools, dishes
  music/*.wav          the pack's field / village themes and night / rain ambients (played on the ranch maps)
Then build the maps' 48 px art:  python3 tools/maps48/maps/ranch.py   (reads ext/ranch, writes ext/maps48 + ext/ranch/x3)
and run a Godot import once:     cd game && godot --headless --path . --import
The game draws clean fallbacks (shapes, no icons) for anything missing, so a partial install is safe.
Usage: python3 tools/art/install_ranch.py [PACK_DIR] [--out DIR] [--check] [--no-music]"""
import importlib.util, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ASSETS = os.environ.get("ASHEN_ASSETS", os.path.join(os.path.dirname(REPO), "Assets"))
OUT = os.path.join(REPO, "game", "assets", "ext", "ranch")

_spec = importlib.util.spec_from_file_location("ranch_content", os.path.join(REPO, "tools", "content", "ranch.py"))
RC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(RC)

TREES = ["animals", "characters", "crops", "objects", "tiles", "buildings", "icons", "visual_effects", "weathers",
         "user_interfaces/themes"]
MUSIC = {"field.wav": "assets/musics/music_themes/field.wav", "village.wav": "assets/musics/music_themes/village.wav",
         "town.wav": "assets/musics/music_themes/town.wav", "night.wav": "assets/musics/ambients/night/night_01.wav",
         "rain.wav": "assets/musics/ambients/rain/rain_01.wav", "fanfare.wav": "assets/musics/ambients/melodies/fanfare/fanfare_01.wav"}
GODOT3 = "engines/Godot/autotiles/3x3"
# tools: lifted out of a farmer frame by removing every colour of the same farmer's idle sheet (what is left is the
# tool; the watering can also drops its spray). (sheet, frame column, frame row, drop spray) - frames are 32x32.
FOLK_IDLE = "characters/males/male_01/idle/male_01_idle_32x32.png"
TOOL_ICONS = {
    "RT01": ("characters/males/male_01/hoe/male_01_hoe_32x32_3frames.png", 0, 2, False),
    "RT02": ("characters/males/male_01/water/male_01_water_32x32_3frames.png", 0, 2, True),
    "RT03": ("objects/sickle/sickle_closed/sickle_closed_48x48.png", -1, -1, False),
}


def _img(path):
    from PIL import Image
    return Image.open(path).convert("RGBA")


def _frames(path):
    """A pack strip 'name_WxH_Nframes.png' -> list of frame images (left to right)."""
    im = _img(path)
    m = re.search(r"_(\d+)x(\d+)(?:_[a-z]+)?(?:_(\d+)frames)?\.png$", os.path.basename(path))
    w, h = (int(m.group(1)), int(m.group(2))) if m else (im.height, im.height)
    n = int(m.group(3)) if m and m.group(3) else max(1, im.width // w)
    h = min(h, im.height)
    return [im.crop((i * w, 0, (i + 1) * w, h)) for i in range(n)]


def _cell16(frame):
    """Centre the frame's opaque part in a 16x16 cell (bottom-aligned if taller)."""
    from PIL import Image
    bb = frame.getbbox()
    f = frame.crop(bb) if bb else frame
    if f.width > 16 or f.height > 16:
        f.thumbnail((16, 16), Image.NEAREST)
    c = Image.new("RGBA", (16, 16))
    c.paste(f, ((16 - f.width) // 2, (16 - f.height) // 2), f)
    return c


def copy_trees(src, out, check):
    n = 0
    for t in TREES:
        d = os.path.join(src, "assets", t)
        if not os.path.isdir(d):
            print("  missing", t)
            continue
        for root, _, files in os.walk(d):
            for f in files:
                if not f.lower().endswith(".png"):
                    continue
                n += 1
                if check:
                    continue
                rel = os.path.relpath(os.path.join(root, f), os.path.join(src, "assets"))
                dst = os.path.join(out, "pack", rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                s = os.path.join(root, f)
                if not os.path.exists(dst) or os.path.getmtime(s) > os.path.getmtime(dst):
                    shutil.copy2(s, dst)
    return n


def copy_autotiles(src, out, check):
    from PIL import Image
    d = os.path.join(src, GODOT3)
    if not os.path.isdir(d):
        print("  missing", GODOT3)
        return 0
    n = 0
    os.makedirs(os.path.join(out, "autotiles"), exist_ok=True)
    for root, _, files in os.walk(d):
        for f in files:
            if not f.endswith(".png"):
                continue
            name = re.sub(r"^_RANCH_AUTOTILE_\d\d_", "", f).lower()
            if f.startswith("_RANCH_AUTOTILE_template"):
                name = "template_ranch_3x3.png"
            n += 1
            if not check:
                shutil.copy2(os.path.join(root, f), os.path.join(out, "autotiles", name))
    fp = os.path.join(out, "autotiles", "field_02.png")
    if not check and os.path.exists(fp):
        # watered beds: the tilled soil of field_02 in field_04's darker colours (the orange dirt rim is kept)
        im = _img(fp)
        px = im.load()
        swap = {(181, 109, 86): (134, 73, 75), (200, 129, 89): (161, 90, 82)}
        for y in range(im.height):
            for x in range(im.width):
                r, g, b, a = px[x, y]
                if (r, g, b) in swap:
                    px[x, y] = swap[(r, g, b)] + (a,)
        im.save(os.path.join(out, "autotiles", "field_wet.png"))
    fp4 = os.path.join(out, "autotiles", "field_04.png")
    if not check and os.path.exists(fp4):
        # watered beds on brown soil (the soot paddock): field_04's dark furrows darkened once more
        im = _img(fp4)
        px = im.load()
        swap = {(134, 73, 75): (112, 60, 64), (161, 90, 82): (136, 76, 74)}
        for y in range(im.height):
            for x in range(im.width):
                r, g, b, a = px[x, y]
                if (r, g, b) in swap:
                    px[x, y] = swap[(r, g, b)] + (a,)
        im.save(os.path.join(out, "autotiles", "field_04_wet.png"))
    return n


def _recolor(im, fn):
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = fn(r, g, b) + (a,)
    return im


def install_icons(src, out, check):
    from PIL import Image
    A = os.path.join(src, "assets")
    lum = lambda r, g, b: (r * 299 + g * 587 + b * 114) // 1000

    def pack(rel, frame=0):
        p = os.path.join(A, rel)
        if not os.path.exists(p):
            return None
        fr = _frames(p)
        return _cell16(fr[min(frame, len(fr) - 1)])

    icons = {}
    signs = _img(os.path.join(A, "objects/objects_01_16x16.png")) if os.path.exists(os.path.join(A, "objects/objects_01_16x16.png")) else None
    for cid, v in RC.CROPS.items():
        ic = pack("crops/%s/%s" % (cid, v[11]), v[12])
        if ic:
            icons[v[0]] = ic
        if signs is not None:
            c, r = v[13]
            icons[v[1]] = signs.crop((c * 16, r * 16, c * 16 + 16, r * 16 + 16))   # seed: the crop's signpost
    pot = pack("icons/potion_01_16x16.png")
    if pot:
        # milk: the red draught turned white (outline and glass kept)
        icons["RK01"] = _recolor(pot.copy(), lambda r, g, b: (min(255, 150 + lum(r, g, b)),) * 2 + (min(255, 160 + lum(r, g, b)),)
                                 if r > g + 40 else (r, g, b))
    icons["RK02"] = pack("animals/egg/idle/egg_idle_16x20.png")
    bun = pack("animals/bunnies/bunny_01/idle/bunny_01_idle_down_16x20.png")
    if bun:
        icons["RK03"] = bun
        icons["RA01"] = _recolor(bun.copy(), lambda r, g, b: (r, g * 45 // 100, b * 40 // 100) if lum(r, g, b) > 120 else (r, g, b))
    icons["RK04"] = None
    g2 = os.path.join(A, "tiles/ground_02_16x16.png")
    if os.path.exists(g2):
        icons["RK04"] = _cell16(_img(g2).crop((192, 16, 208, 32)))      # the dark mushroom: a truffle
    o2 = os.path.join(A, "objects/objects_02_16x16.png")
    icons["RF01"] = _cell16(_img(o2).crop((128, 16, 144, 32))) if os.path.exists(o2) else None   # the full pail: a stew
    icons["RF02"] = pack("animals/mouses/cheese_16x16_2frames.png", 1)
    icons["RF06"] = pack("animals/mouses/cheese_16x16_2frames.png", 0)
    icons["RF03"] = pack("crops/pumpkin/icon/pumpkin_icon_16x16_3frames.png", 0)
    icons["RF04"] = pack("icons/potion_02_16x16.png")
    icons["RF05"] = pack("icons/potion_03_16x16.png")
    icons["RF07"] = _recolor(pot.copy(), lambda r, g, b: (r // 3, min(255, g + 60), b // 2) if r > g + 40 else (r, g, b)) if pot else None
    idle_p = os.path.join(A, FOLK_IDLE)
    folk_pal = set()
    if os.path.exists(idle_p):
        ii = _img(idle_p)
        folk_pal = set(ii.get_flattened_data() if hasattr(ii, "get_flattened_data") else ii.getdata())
    for tid, (rel, col, row, spray) in TOOL_ICONS.items():
        p = os.path.join(A, rel)
        if not os.path.exists(p):
            continue
        im = _img(p)
        if col < 0:
            icons[tid] = _cell16(im)
            continue
        fr = im.crop((col * 32, row * 32, col * 32 + 32, row * 32 + 32))
        px = fr.load()
        for y in range(32):
            for x in range(32):
                c = px[x, y]
                if c in folk_pal or (spray and c[2] > 180 and c[1] > 150):
                    px[x, y] = (0, 0, 0, 0)
        icons[tid] = _cell16(fr)
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


def copy_music(src, out, check):
    n = 0
    for name, rel in MUSIC.items():
        p = os.path.join(src, rel)
        if not os.path.exists(p):
            continue
        n += 1
        if not check:
            os.makedirs(os.path.join(out, "music"), exist_ok=True)
            dst = os.path.join(out, "music", name)
            if not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(p):
                shutil.copy2(p, dst)
    return n


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
        old = [f for f in os.listdir(out) if f in ("crops.png", "crops.json", "crate.png")]   # the first pass's files
        for f in old:
            os.remove(os.path.join(out, f))
        for d in ("cow", "cow_black", "pig", "pig_black", "dove", "bunny", "cat", "fox", "mouse"):
            if os.path.isdir(os.path.join(out, d)):
                shutil.rmtree(os.path.join(out, d))
    print("install_ranch: %s -> %s%s" % (src, out, " (check only)" if check else ""))
    nt = copy_trees(src, out, check)
    na = copy_autotiles(src, out, check)
    ni = install_icons(src, out, check)
    nm = 0 if "--no-music" in sys.argv else copy_music(src, out, check)
    print("install_ranch: %d sheets, %d autotile sheets, %d icons, %d music files" % (nt, na, ni, nm))
    return 0


if __name__ == "__main__":
    sys.exit(main())
