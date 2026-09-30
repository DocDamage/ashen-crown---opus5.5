"""Townsfolk importer: Assets/_processed/townsfolk sheets (5 cols stand + 4 walk; rows south, west, east, north; 129px
cells; adults ~62px) -> game/assets/ext/npcs/<stem>/field.png + field.json (same layout as heroes: rows down, left,
right, up; column 0 standing), cropped to a common cell with the feet aligned; plus npcs/npc_map.json mapping the game's
NPC sprite keys to candidate townsfolk (the game picks one per NPC id for variety)."""
import os, json
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ASSETS = os.environ.get("ASHEN_ASSETS", os.path.join(os.path.dirname(REPO), "Assets"))
SRC = os.path.join(ASSETS, "_processed", "townsfolk")
OUT = os.path.join(REPO, "game", "assets", "ext", "npcs")

MAP = {
    "worker": ["cozy_village/village_blacksmith", "kingdom_citizens/village_blacksmith", "steampunk/clockwork_engineer_male",
               "steampunk/young_apprentice_engineer_free_character", "cozy_village/fisherman"],
    "elder": ["cozy_village/village_elder", "kingdom_citizens/elder_scholar"],
    "survivor": ["cozy_village/fisherman", "cozy_village/flower_gardener", "cozy_village/shepherd_girl",
                 "cozy_village/village_farmer", "kingdom_citizens/herbalist", "kingdom_citizens/tavern_waitress"],
    "guard": ["kingdom_citizens/royal_guard"],
    "soldier": ["kingdom_citizens/royal_guard", "dark_gothic/dark_fantasy_gothic_knight_pixel"],
    "child": ["cozy_village/village_kid_free"],
    "keeper": ["kingdom_citizens/tavern_keeper", "cozy_village/traveling_merchant", "kingdom_citizens/traveling_merchant", "cozy_village/caf_owner"],
    "monk": ["cozy_village/librarian", "kingdom_citizens/elder_scholar", "psych_horror/the_weeping_nun_female"],
    "pilot": ["steampunk/airship_captain_male", "steampunk/sky_navigator"],
    "farmer": ["cozy_village/village_farmer"],
    "baker": ["cozy_village/village_baker", "kingdom_citizens/village_baker"],
    "sailor": ["cozy_village/fisherman", "atlantis/sea_dragon_hunter"],
    "scholar": ["kingdom_citizens/elder_scholar", "cozy_village/librarian"],
    "patient": ["cozy_village/shepherd_girl", "cozy_village/flower_gardener"],
    "mara": ["steampunk/clockwork_huntress_female"],
    "inspector": ["steampunk/iron_baron_male"],
    "noble": ["kingdom_citizens/noble_lady"],
    "clerk": ["kingdom_citizens/guild_receptionist"],
    "apprentice": ["steampunk/young_apprentice_engineer_free_character"],
    "volunteer": ["cozy_village/shepherd_girl"],
    "pell": ["kingdom_citizens/traveling_merchant"],
    "jori": ["steampunk/sky_navigator"],
    "edda": ["kingdom_citizens/herbalist"],
    "ansel": ["cozy_village/librarian"],
    "sen": ["samurai_yokai/shrine_maiden_warrior_female"],
    "rook": ["dark_dungeon/shadow_dungeon_assassin_male"],
}
ROWS = [("down", 0), ("left", 1), ("right", 2), ("up", 3)]
CELL = 129


def bbox(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1) if len(xs) else None


def clean(f):
    """Drop pixels that spilled in from the neighbouring cell: keep the largest blob and anything touching its box."""
    from scipy import ndimage
    a = f[..., 3] > 0
    lab, n = ndimage.label(a, structure=np.ones((3, 3)))
    if n <= 1:
        return f
    sizes = ndimage.sum(a, lab, range(1, n + 1))
    main = int(np.argmax(sizes)) + 1
    ys, xs = np.nonzero(lab == main)
    x0, x1, y0, y1 = xs.min() - 3, xs.max() + 3, ys.min() - 3, ys.max() + 3
    keep = np.zeros_like(a)
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        if sl is None:
            continue
        cy0, cy1, cx0, cx1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        touches_edge = cx0 == 0 or cx1 == a.shape[1]
        inside = cx1 >= x0 and cx0 <= x1 and cy1 >= y0 and cy0 <= y1
        if i == main or (inside and not (touches_edge and sizes[i - 1] < sizes[main - 1] * 0.25)):
            keep |= lab == i
    g = f.copy()
    g[~keep] = 0
    return g


def _segments(profile, gap, min_len):
    segs, start, empty = [], None, 0
    for i, v in enumerate(profile):
        if v:
            if start is None:
                start = i
            empty = 0
            end = i
        elif start is not None:
            empty += 1
            if empty >= gap:
                segs.append([start, end + 1]); start = None
    if start is not None:
        segs.append([start, end + 1])
    # merge slivers into their nearest neighbour
    out = []
    for sgm in segs:
        if out and (sgm[1] - sgm[0] < min_len or out[-1][1] - out[-1][0] < min_len):
            out[-1][1] = sgm[1]
        else:
            out.append(sgm)
    return out


def blob_frames(im):
    """Frames found from the art itself: 4 row bands, then figures separated by empty columns (the sheets are not all
    on the same grid, so a fixed 129px cut takes pieces of the neighbours)."""
    a = np.array(im)[..., 3] > 0
    bands = _segments(a.any(axis=1), 3, 20)
    if len(bands) != 4:
        return None
    frames = {}
    for (d, r), (y0, y1) in zip(ROWS, bands):
        sub = a[y0:y1]
        cols = _segments(sub.any(axis=0), 4, 14)
        frames[d] = []
        for x0, x1 in cols:
            f = np.zeros((y1 - y0 + 8, x1 - x0 + 8, 4), np.uint8)
            f[4:-4, 4:-4] = np.array(im)[y0:y1, x0:x1]
            frames[d].append(f)
    n = min(len(v) for v in frames.values())
    if n < 2:
        return None
    return {d: v[:n] for d, v in frames.items()}


def _center(frames):
    """Pad every frame to one size with the figure's feet on the bottom row and its body centred."""
    boxes = {id(f): bbox(f) for fs in frames.values() for f in fs}
    w = max(b[2] - b[0] for b in boxes.values() if b) + 4
    h = max(b[3] - b[1] for b in boxes.values() if b) + 2
    out = {}
    for d, fs in frames.items():
        out[d] = []
        for f in fs:
            b = boxes[id(f)]
            g = np.zeros((h, w, 4), np.uint8)
            if b:
                piece = f[b[1]:b[3], b[0]:b[2]]
                ox = (w - piece.shape[1]) // 2
                g[h - 1 - piece.shape[0]:h - 1, ox:ox + piece.shape[1]] = piece
            out[d].append(g)
    return out, w, h


def build(stem):
    im = Image.open(os.path.join(SRC, stem + ".png")).convert("RGBA")
    bf = blob_frames(im)
    if bf is not None:
        frames, cw, ch = _center(bf)
        cw, ch = int(cw), int(ch)
        cols = len(frames["down"])
        sheet = Image.new("RGBA", (cw * cols, ch * 4), (0, 0, 0, 0))
        for d, r in ROWS:
            for c, f in enumerate(frames[d]):
                sheet.paste(Image.fromarray(f), (c * cw, r * ch))
        dst = os.path.join(OUT, stem.replace("/", "__"))
        os.makedirs(dst, exist_ok=True)
        sheet.save(os.path.join(dst, "field.png"))
        json.dump({"cell": [cw, ch], "foot": [cw // 2, ch - 1], "fps": 7,
                   "rows": {d: {"row": r, "n": cols - 1} for d, r in ROWS}}, open(os.path.join(dst, "field.json"), "w"))
        return
    cols = im.width // CELL
    frames = {}
    for d, r in ROWS:
        frames[d] = [clean(np.array(im.crop((c * CELL, r * CELL, (c + 1) * CELL, (r + 1) * CELL)))) for c in range(cols)]
    boxes = [bbox(f) for fs in frames.values() for f in fs if bbox(f)]
    x0 = min(b[0] for b in boxes) - 1
    x1 = max(b[2] for b in boxes) + 1
    y0 = min(b[1] for b in boxes) - 1
    feet = max(b[3] for b in boxes)
    x0, x1, y0, feet = int(x0), int(x1), int(y0), int(feet)
    cw, ch = x1 - x0, feet - y0 + 1
    sheet = Image.new("RGBA", (cw * cols, ch * 4), (0, 0, 0, 0))
    for d, r in ROWS:
        for c, f in enumerate(frames[d]):
            sheet.paste(Image.fromarray(f).crop((x0, y0, x1, feet + 1)), (c * cw, r * ch))
    dst = os.path.join(OUT, stem.replace("/", "__"))
    os.makedirs(dst, exist_ok=True)
    sheet.save(os.path.join(dst, "field.png"))
    json.dump({"cell": [cw, ch], "foot": [int(CELL / 2 - x0), ch - 1], "fps": 7,
               "rows": {d: {"row": r, "n": cols - 1} for d, r in ROWS}}, open(os.path.join(dst, "field.json"), "w"))


def main():
    os.makedirs(OUT, exist_ok=True)
    stems = sorted({s for v in MAP.values() for s in v})
    for s in stems:
        try:
            build(s)
        except Exception as ex:   # keep going; report
            print("FAIL", s, ex)
    json.dump({k: [s.replace("/", "__") for s in v] for k, v in MAP.items()}, open(os.path.join(OUT, "npc_map.json"), "w"), indent=1)
    print("npcs:", len(stems), "sheets,", len(MAP), "sprite keys")
    import cutclean
    for png, cells in cutclean.targets("npcs"):
        im, k = cutclean.clean_sheet(png, cells)
        if k:
            Image.fromarray(im).save(png)


if __name__ == "__main__":
    main()
