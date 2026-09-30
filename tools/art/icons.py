"""Item icons (expansion Phase 2): one icon per item, assembled from the owner's icon packs into two atlases,
game/assets/ext/sprites/icons_11.png (list rows) and icons_24.png (detail panels), 32 cells per row.
Cell index = item["icon"] (sorted item id order, set by tools/compile_content.py).

Sources: Seveneves.ai 500+ RPG icons / 400+ gear icons / shields / hats (pixel art, 32px), HoriHori megapack
64px weapon icons and 20000-icon folders (reduced). Bows have no library icon; they are drawn here in code.
"""
import json, os, zlib
from PIL import Image, ImageDraw
from art.pix import lib_img

S7 = "seveneves/"
S7I = S7 + "500+ RPG Icons Pixel Art Pack/icons-%d.png"
S7G = S7 + "400+ RPG Gear Icons Pixel Art Pack/%s.png"
S7SH = S7 + "250+ RPG Shield Sprites Pixel Art Pack/%s.png"
S7HAT = S7 + "100+ RPG Hat Sprites Pixel Art Pack/%s.png"
HH4 = "HoriHori Assets/#4 - MegaPack  HoriHori Assets - Characters, Backgrounds, Portraits, Items!/Icons/64/"
HH5 = "HoriHori Assets/#5 - MegaPack  HoriHori Assets - Characters, Backgrounds, Portraits, Items!/Icons/64/"
HHK = "use this/20000 Icons RPG + Recolors - Full version/"

_grid = {}


def _runs(v):
    out, s = [], None
    for i, b in enumerate(list(v) + [False]):
        if b and s is None:
            s = i
        if not b and s is not None:
            out.append((s, i))
            s = None
    return out


def cell(sheet, r, c):
    """Icon at row r, column c of a sheet, found from the gaps between icons (grids are not exactly regular)."""
    im = lib_img(sheet)
    if sheet not in _grid:
        a = im.split()[3]
        W, H = im.size
        px = a.load()
        cols = [any(px[x, y] for y in range(H)) for x in range(W)]
        rows = [any(px[x, y] for x in range(W)) for y in range(H)]
        _grid[sheet] = (_runs(cols), _runs(rows))
    cr, rr = _grid[sheet]
    x0, x1 = cr[min(c, len(cr) - 1)]
    y0, y1 = rr[min(r, len(rr) - 1)]
    return im.crop((x0, y0, x1, y1))


def hh(path):
    return lib_img(path)


def _bow(seed):
    """A recurve bow in the pixel style of the packs (no bow icon exists in the library)."""
    woods = [(122, 78, 42), (150, 96, 50), (96, 60, 38), (176, 128, 70), (120, 110, 130), (160, 70, 50)]
    wood = woods[seed % len(woods)]
    im = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.arc((6, 3, 34, 31), 150, 300, fill=(28, 20, 16, 255), width=5)
    d.arc((7, 4, 33, 30), 152, 298, fill=wood + (255,), width=3)
    d.arc((8, 5, 32, 29), 160, 290, fill=tuple(min(255, int(v * 1.25)) for v in wood) + (255,), width=1)
    d.line((12, 6, 12, 28), fill=(232, 226, 210, 255), width=1)
    d.rectangle((6, 15, 9, 19), fill=(60, 40, 30, 255))
    d.line((13, 17, 28, 17), fill=(110, 90, 70, 255), width=1)
    d.polygon([(28, 15), (31, 17), (28, 19)], fill=(190, 196, 206, 255))
    return im


def fit(im, n):
    b = im.getbbox()
    if b:
        im = im.crop(b)
    s = max(im.size)
    sq = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    sq.paste(im, ((s - im.width) // 2, (s - im.height) // 2))
    out = sq.resize((n, n), Image.LANCZOS)
    px = out.load()
    for y in range(n):
        for x in range(n):
            r, g, bl, a = px[x, y]
            px[x, y] = (r, g, bl, 255 if a > 110 else 0)
    return out


# ---- pools (each entry: a callable returning an RGBA image) -----------------------------------------------------
def _s7(sheet_no, cells):
    return [(lambda r=r, c=c: cell(S7I % sheet_no, r, c)) for r, c in cells]


def _gear(name, n=64, rows=8, cols=8):
    """Gear sheets are an exact 8x8 grid of 32px icons (their chains touch, so gap detection cannot split them)."""
    return [(lambda i=i: lib_img(S7G % name).crop(((i % cols) * 32, (i // cols) * 32, (i % cols) * 32 + 32, (i // cols) * 32 + 32)))
            for i in range(n)]


def _exists(rel):
    from art.pix import lib_path
    return os.path.exists(lib_path(rel))


def _hh(prefix, count, folder=HH5, start=1):
    """HoriHori 64px icons `prefix<n>.png`, taken from whichever megapack folder holds them."""
    out = []
    for i in range(start, start + 60):
        for f in (folder, HH4 if folder == HH5 else HH5):
            rel = f + "%s%d.png" % (prefix, i)
            if _exists(rel):
                out.append(lambda rel=rel: hh(rel))
                break
        if len(out) >= count:
            break
    return out


def _hk(name, count=12):
    return [(lambda rel=rel: hh(rel)) for rel in [HHK + "%s/%s%d.png" % (name, name, i) for i in range(1, count + 1)] if _exists(rel)]


POOLS = None


def pools():
    global POOLS
    if POOLS is None:
        POOLS = {
            "sword": _hh("sword_", 12, HH4) + _hh("gold_sword_", 8, HH4) + _hh("flame_sword_", 8, HH4),
            "runeblade": _hh("crystal_blade_", 12, HH5) + _hh("void_sword_", 6, HH4) + _hh("blood_sword_", 6, HH4),
            "rod": _s7(2, [(5, 10), (5, 11), (6, 9), (6, 10), (7, 0), (7, 1), (7, 2), (7, 4), (7, 5), (7, 6)]) + _hh("magic_weapon_", 8, HH4),
            "spear": _hh("trident_", 12, HH4) + _s7(2, [(7, 3)]),
            "hammer": _hh("battle_axe_", 10, HH4) + _hh("axe_", 10, HH4),
            "bow": [(lambda i=i: _bow(i)) for i in range(6)],
            "staff": _hh("staff_", 16, HH4),
            "dagger": _hh("ember_dagger_", 16, HH5),
            "plate": _s7(3, [(0, 10), (0, 12), (0, 11), (1, 10)]),
            "robe": _hk("Arcane robe", 6) + _hk("Teacher's robe", 6) + _hk("Supreme's robe", 6) + _hk("Artic robe", 6),
            "leather": _s7(3, [(1, 11), (1, 10), (4, 3), (4, 10)]) + _hk("Dark coat", 6),
            "head": [(lambda i=i: cell(S7HAT % "hats-1", i // 6, i % 6)) for i in range(36)] + _hk("Metal helmet", 6) + _hk("Roman helmet", 6),
            "shield": _s7(3, [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 1)]),
            "focus": _s7(2, [(1, 7), (5, 7), (6, 7), (6, 8)]),
            "charm": _s7(3, [(6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (7, 1), (7, 2), (7, 4)]),
            "accessory": _s7(2, [(5, 12), (7, 7), (7, 9), (7, 10), (7, 11)]) + _hk("Amber ring", 4) + _hk("Plated ring", 4)
                         + _hk("Blood ring", 3) + _hk("Elf bracelet", 4) + _hk("Nobleman's bracelet", 3) + _gear("gloves", 16)
                         + _hk("Rare earring", 3) + _hk("Sky pendant", 3) + _hk("Leather boots", 3) + _hk("Golden boots", 3),
            "potion": _gear("potions"),
            "bomb": _s7(3, [(5, 2), (5, 3)]),
            "tent": _s7(3, [(5, 9), (6, 0)]),
            "scroll": _s7(2, [(0, 9), (0, 10), (0, 11), (1, 8), (1, 9), (1, 10), (1, 11), (1, 12), (2, 7), (2, 8), (2, 9),
                              (2, 10), (2, 11), (5, 4), (5, 5), (5, 6), (5, 8), (5, 9), (6, 5), (6, 6)]),
            "book": _s7(2, [(5, 0), (5, 1), (5, 2), (5, 3), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4)]),
            "keyitem": _hk("Antique key", 8),
            "ore": _hk("Gemstone", 2) + _hk("Gems", 4),
        }
    return POOLS


OWNER_KIND = {"C01": "sword", "C02": "rod", "C03": "spear", "C04": "hammer", "C05": "bow", "C06": "staff", "C07": "runeblade", "C08": "dagger"}


def category(it):
    k = it["kind"]
    if k == "weapon":
        return OWNER_KIND.get(it.get("owner", "C01"), "sword")
    if k == "armor":
        if it.get("slot") == "head":
            return "head"
        if it.get("slot") == "offhand":
            a = it.get("allowed", [])
            return "focus" if a == ["C02"] else ("charm" if a == ["C08"] else "shield")
        a = it.get("allowed", [])
        if "C02" in a or "C06" in a:
            return "robe"
        if "C05" in a or "C08" in a:
            return "leather"
        return "plate"
    if k == "accessory":
        return "accessory"
    if k == "consumable":
        sp = it.get("special", "")
        if sp in ("tent", "waystone"):
            return "tent"
        ops = it.get("ops", [])
        if ops and ops[0].get("op") == "damage":
            return "bomb"
        return "potion"
    if k == "material":
        return "ore"
    if it["id"].startswith("K_") and ("PASS" in it["id"] or "KEYS" in it["id"]):
        return "keyitem"
    if "MANUAL" in it["id"] or "LEDGER" in it["id"] or "REGISTER" in it["id"]:
        return "book"
    return "scroll"


def build_icons(items):
    """-> (atlas11, atlas24, sources). Items in sorted-id order, each category's pool used in turn."""
    P = pools()
    ids = sorted(items)
    n = max([len(ids)] + [int(items[i].get("icon", 0)) + 1 for i in ids])
    rows = (n + 31) // 32
    a11 = Image.new("RGBA", (32 * 11, rows * 11), (0, 0, 0, 0))
    a24 = Image.new("RGBA", (32 * 24, rows * 24), (0, 0, 0, 0))
    used = {}
    for i, iid in enumerate(ids):
        it = items[iid]
        i = int(it.get("icon", i))   # cell = item.icon (items added after the sorted pass get cells at the end)
        cat = category(it)
        pool = P[cat]
        k = used.get(cat, 0)
        used[cat] = k + 1
        # spread picks across the pool so neighbouring tiers differ; stable per item
        j = (k * 7 + zlib.crc32(iid.encode()) % 3) % len(pool)
        try:
            src = pool[j]()
        except (FileNotFoundError, KeyError, OSError):
            src = pool[0]()
        a11.paste(fit(src, 11), ((i % 32) * 11, (i // 32) * 11))
        a24.paste(fit(src, 24), ((i % 32) * 24, (i // 32) * 24))
    return a11, a24


SOURCES = [S7I % 2, S7I % 3, S7G % "potions", S7G % "ammies", S7HAT % "hats-1", HH4, HH5, HHK]


def build_library(save_ext):
    root = os.path.join(os.path.dirname(__file__), "..", "..", "game", "content", "content.json")
    items = json.load(open(root))["items"]
    # systems s2 items (icon_base) take cells after the base atlas: tools/art/icons_gear2.py appends them afterwards
    items = {k: v for k, v in items.items() if "icon_base" not in v}
    a11, a24 = build_icons(items)
    save_ext(a11, "sprites/icons_11.png", "item_icons", SOURCES, note="11px item icons, 32/row, cell = item.icon")
    save_ext(a24, "sprites/icons_24.png", "item_icons", SOURCES, note="24px item icons, 32/row, cell = item.icon")
