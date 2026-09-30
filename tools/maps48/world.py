"""World maps at native 48px from the Winlu Fantasy Overworld set (RPG Maker MV autotiles: A1 liquids, A2 terrain).

The collision grid (content maps WORLD / WORLD_POST) is kept; this bakes the look: every cell gets a ground autotile,
forests/hills/mountains are autotiles laid over the ground, water uses shore-aware liquid autotiles, and each location
entity gets an overworld landmark sprite (village, castle, tower, cave, ruin).
Usage: python tools/maps48/world.py [WORLD WORLD_POST]"""
import os, sys, json
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kit

REPO = kit.REPO
W48 = os.path.join(kit.ASSETS, "Winlu Fantasy Overworld")
Q = 24


def load(name):
    return Image.open(os.path.join(W48, "tilesets", name)).convert("RGBA")


A1 = load("Fantasy_World_A1.png")
A2 = load("Fantasy_World_A2.png")

# autotile blocks (column, row of the block's top-left cell, 48px cells)
GROUND = {"plains": (A2, 0, 0), "grass2": (A2, 12, 0), "sand": (A2, 0, 3), "salt": (A2, 2, 9), "snow": (A2, 0, 9),
          "ash": (A2, 4, 9), "dirt": (A2, 6, 0), "red": (A2, 4, 0), "olive": (A2, 6, 3), "rocky": (A2, 0, 6),
          "dark": (A2, 4, 6), "grey": (A2, 6, 9), "purple": (A2, 10, 9)}
OVER = {"forest": (A2, 8, 0), "forest_autumn": (A2, 10, 0), "jungle": (A2, 8, 3), "forest_snow": (A2, 8, 9),
        "forest_magic": (A2, 8, 6), "rocks": (A2, 10, 3), "hills": (A2, 12, 9), "hills_green": (A2, 12, 6),
        "mountain": (A2, 12, 6), "mountain_brown": (A2, 14, 6), "mountain_snow": (A2, 14, 9), "mountain_desert": (A2, 14, 3)}
LIQUID = {"sea_sand": (A1, 0, 0), "sea_grass": (A1, 8, 0), "deep": (A1, 0, 3), "sea_snow": (A1, 0, 9), "lava": (A1, 8, 3),
          "ice_sea": (A1, 0, 6)}


def quarters(block, n, s, w, e, nw, ne, sw, se):
    img, bc, br = block
    bx, by = bc * 48, br * 48
    out = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
    for (qx, qy) in ((0, 0), (1, 0), (0, 1), (1, 1)):
        v = n if qy == 0 else s
        h = w if qx == 0 else e
        d = (nw if qx == 0 else ne) if qy == 0 else (sw if qx == 0 else se)
        if v and h and d:
            sx, sy = 2 - qx, 4 - qy
        elif v and h:
            sx, sy = 2 + qx, qy
        elif v:
            sx, sy = (0 if qx == 0 else 3), 4 - qy
        elif h:
            sx, sy = 2 - qx, (2 if qy == 0 else 5)
        else:
            sx, sy = (0 if qx == 0 else 3), (2 if qy == 0 else 5)
        out.alpha_composite(img.crop((bx + sx * Q, by + sy * Q, bx + sx * Q + Q, by + sy * Q + Q)), (qx * Q, qy * Q))
    return out


def autolayer(canvas, cells, W, H, block_of, group_of):
    """Draw an autotile layer: cells = {(x,y): block}; neighbours join when group_of is equal."""
    for (x, y), blk in cells.items():
        g = group_of(x, y)

        def same(xx, yy):
            if not (0 <= xx < W and 0 <= yy < H):
                return True
            return group_of(xx, yy) == g
        t = quarters(blk, same(x, y - 1), same(x, y + 1), same(x - 1, y), same(x + 1, y), same(x - 1, y - 1),
                     same(x + 1, y - 1), same(x - 1, y + 1), same(x + 1, y + 1))
        canvas.alpha_composite(t, (x * 48, y * 48))


REGION_STYLE = {
    # region hints by location of ash/salt/snow masses are in the grid itself; these pick forest/mountain variants
    "ash": ("mountain_brown", "forest_autumn"), "snow": ("mountain_snow", "forest_snow"), "salt": ("mountain_desert", "forest"),
    "sand": ("mountain_desert", "jungle"), "plains": ("mountain", "forest"),
}

LANDMARKS = {
    "town": "!$Overworld_Village1.png", "port": "!$Overworld_village_sea.png", "city": "!$Overworld_Castle1.png",
    "castle": "!$Overworld_Castle2.png", "tower": "!Overworld_towers.png", "cave": None,
}


sys.path.insert(0, os.path.dirname(HERE))
from compile_content import SOLID as GSOLID, LEGEND_BASE
import autoskin
import random
from collections import deque

LANDK = ("plains", "hills", "forest", "sand", "ash", "salt", "snow")


def _reach(grid, W, H, starts, closed, locs):
    seen = set(starts)
    q = deque(starts)
    while q:
        x, y = q.popleft()
        if (x, y) in locs and (x, y) not in starts:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < W and 0 <= n[1] < H and n not in seen and grid[n[1]][n[0]] not in GSOLID and n not in closed:
                seen.add(n)
                q.append(n)
    return seen


def refine(mid, grid, ents, W, H, seed=11):
    """FF6-style shapes without changing where anyone can walk to: diagonal river steps become continuous water,
    region borders (plains/forest/hills/sand/ash/salt/snow) get ragged, and coasts get bays - each change is kept
    only if the set of reachable locations, landings and exits stays exactly the same."""
    rng = random.Random(seed + len(mid))
    locs = {(e["x"], e["y"]) for e in ents if e["type"] == "location"}
    starts = [(e["x"], e["y"]) for e in ents if e["type"] == "spawn"]
    special = set(locs)
    for e in ents:
        for k in ("x",):
            if k in e:
                special.add((e["x"], e["y"]))
        if "x1" in e and e["type"] not in ("zone", "tileset_over"):
            for yy in range(e["y1"] - 1, e["y2"] + 2):
                for xx in range(e["x1"] - 1, e["x2"] + 2):
                    special.add((xx, yy))
    closed_sets = [set(), set()]
    for e in ents:
        if e["type"] == "block":
            for yy in range(e["y1"], e["y2"] + 1):
                for xx in range(e["x1"], e["x2"] + 1):
                    closed_sets[1].add((xx, yy))

    def signature():
        out = []
        for cl in closed_sets:
            r = set()
            for st in starts:
                r |= _reach(grid, W, H, [st], cl, locs)
            out.append(frozenset(c for c in r if c in special))
        return out
    def per_start():
        out = []
        for cl in closed_sets:
            for st in starts:
                out.append(frozenset(c for c in _reach(grid, W, H, [st], cl, locs) if c in special))
        return out
    snapshot = [row[:] for row in grid]
    base_sig = per_start()

    def walk(xx, yy):
        return 0 <= xx < W and 0 <= yy < H and grid[yy][xx] not in GSOLID and (xx, yy) not in closed_sets[1]

    def simple(x, y):
        """Removing (x, y) from the walkable set keeps its walkable 4-neighbours connected through the 3x3 ring."""
        ring = [(-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)]
        cells = [(dx, dy) for dx, dy in ring if walk(x + dx, y + dy)]
        four = [(dx, dy) for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)) if walk(x + dx, y + dy)]
        if len(four) <= 1:
            return True
        comp = {four[0]}
        st = [four[0]]
        cs = set(cells)
        while st:
            a = st.pop()
            for b in cs:
                if b not in comp and abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1:
                    comp.add(b)
                    st.append(b)
        return all(f in comp for f in four)

    def try_set(x, y, k):
        old = grid[y][x]
        if old not in GSOLID and k in GSOLID and not simple(x, y):
            return False
        grid[y][x] = k
        return True

    def nearpath(x, y):
        return any(0 <= x + dx < W and 0 <= y + dy < H and grid[y + dy][x + dx] in ("path", "bridge")
                   for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    n_river = n_edge = n_coast = 0
    # A) diagonal river steps
    for y in range(H - 1):
        for x in range(W - 1):
            for (ax, ay, bx, by, cx, cy, dx_, dy_) in ((x, y, x + 1, y + 1, x + 1, y, x, y + 1), (x + 1, y, x, y + 1, x, y, x + 1, y + 1)):
                if grid[ay][ax] == "water" and grid[by][bx] == "water" and grid[cy][cx] != "water" and grid[dy_][dx_] != "water":
                    for (px, py) in ((cx, cy), (dx_, dy_)):
                        if grid[py][px] in LANDK and (px, py) not in special and not nearpath(px, py):
                            if try_set(px, py, "water"):
                                n_river += 1
                                break
    # B) ragged region borders (all walkable kinds: no reachability change)
    import numpy as np
    noise = kit._value_noise(H, W, 3, seed)
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            k = grid[y][x]
            if k not in LANDK or (x, y) in special:
                continue
            nb = [grid[y + dy][x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            other = [n for n in nb if n in LANDK and n != k]
            if other and noise[y, x] > 0.62:
                grid[y][x] = rng.choice(other)
                n_edge += 1
    # C) coastal bays: plains next to the sea turn to water where nothing depends on them
    noise2 = kit._value_noise(H, W, 4, seed + 5)
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if grid[y][x] not in ("plains", "sand", "hills") or (x, y) in special or nearpath(x, y):
                continue
            water_n = sum(1 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if grid[y + dy][x + dx] == "water")
            if water_n >= 1 and noise2[y, x] > 0.6 + 0.08 * (2 - water_n):
                if try_set(x, y, "water"):
                    n_coast += 1
    if per_start() != base_sig:
        print(mid, "refinement changed reachability: reverted")
        for y in range(H):
            grid[y] = snapshot[y][:]
        return grid
    print(mid, "refined: river", n_river, "borders", n_edge, "coast", n_coast)
    return grid


def build(mid, grid_override=None):
    content = json.load(open(os.path.join(REPO, "game", "content", "content.json"), encoding="utf-8"))
    cm = dict(content["maps"][mid])
    W, H = int(cm["w"]), int(cm["h"])
    lg = cm["legend"]
    grid = grid_override if grid_override is not None else [[lg.get(ch, "water") for ch in row] for row in cm["grid"]]
    canvas = Image.new("RGBA", (W * 48, H * 48), (20, 40, 90, 255))
    land_base = {"plains": "plains", "hills": "plains", "forest": "plains", "mountain": "plains", "path": "plains",
                 "sand": "sand", "salt": "salt", "snow": "snow", "ash": "ash", "dungeon_mark": "plains",
                 "town_mark": "plains", "city": "plains", "ruin": "plains", "bridge": "plains", "island": "sand", "cave": "plains"}

    # the ground a mountain/forest/hill cell stands on = most common neighbouring ground
    def base_of(x, y):
        k = grid[y][x]
        if k in ("sand", "salt", "snow", "ash", "plains"):
            return k
        cnt = {}
        for r in (1, 2, 3):
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < W and 0 <= yy < H and grid[yy][xx] in ("sand", "salt", "snow", "ash", "plains"):
                        cnt[grid[yy][xx]] = cnt.get(grid[yy][xx], 0) + 1
            if cnt:
                return max(cnt, key=cnt.get)
        return "plains"
    base = [[None if grid[y][x] in ("water", "deep", "reef") else base_of(x, y) for x in range(W)] for y in range(H)]
    # 1) liquids: water everywhere under land edges; shore style from the nearest land
    def shore(x, y):
        cnt = {}
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                xx, yy = x + dx, y + dy
                if 0 <= xx < W and 0 <= yy < H and base[yy][xx]:
                    cnt[base[yy][xx]] = cnt.get(base[yy][xx], 0) + 1
        b = max(cnt, key=cnt.get) if cnt else "sand"
        return {"plains": "sea_grass", "snow": "sea_snow", "salt": "sea_sand", "sand": "sea_sand", "ash": "sea_sand"}.get(b, "sea_sand")
    liq = {}
    for y in range(H):
        for x in range(W):
            if grid[y][x] in ("water", "reef", "deep"):
                liq[(x, y)] = LIQUID[shore(x, y)]
    autolayer(canvas, liq, W, H, None, lambda x, y: "w" if grid[y][x] in ("water", "reef", "deep") else "l")
    deep = {(x, y): LIQUID["deep"] for y in range(H) for x in range(W) if grid[y][x] == "deep"}
    autolayer(canvas, deep, W, H, None, lambda x, y: "d" if grid[y][x] == "deep" else "o")
    # 2) ground: each base kind is its own autotile group (edges blend over the plains below)
    plains_all = {(x, y): GROUND["plains"] for y in range(H) for x in range(W) if base[y][x]}
    autolayer(canvas, plains_all, W, H, None, lambda x, y: "g" if base[y][x] else "w")
    for kind in ("sand", "salt", "snow", "ash"):
        cells = {(x, y): GROUND[kind] for y in range(H) for x in range(W) if base[y][x] == kind}
        autolayer(canvas, cells, W, H, None, lambda x, y, k=kind: base[y][x] == k)
    paths = {(x, y): GROUND["dirt"] for y in range(H) for x in range(W) if grid[y][x] in ("path", "bridge")}
    autolayer(canvas, paths, W, H, None, lambda x, y: grid[y][x] in ("path", "bridge", "dungeon_mark", "town_mark", "city", "ruin"))
    # 3) overlays: hills, forests, mountains (variant by the ground they stand on)
    def variant(kind, x, y):
        b = base[y][x] or "plains"
        mnt, fst = REGION_STYLE.get(b, REGION_STYLE["plains"])
        return {"mountain": mnt, "forest": fst, "hills": "hills"}[kind]
    for kind in ("hills", "forest"):
        cells = {(x, y): OVER[variant(kind, x, y)] for y in range(H) for x in range(W) if grid[y][x] == kind}
        autolayer(canvas, cells, W, H, None, lambda x, y, k=kind: grid[y][x] == k)
    # mountains: overlapping peak sprites (Fantasy_World_Mountains.png, 2x2 cells each), bottom on the cell
    MT = Image.open(os.path.join(W48, "tilesets", "Fantasy_World_Mountains.png")).convert("RGBA")
    peaks = {"mountain": [(0, 0), (2, 0), (4, 0), (0, 2), (2, 2), (4, 2)], "mountain_brown": [(0, 4), (2, 4), (4, 4)],
             "mountain_snow": [(6, 0), (6, 4)], "mountain_desert": [(0, 4), (4, 4)]}
    import random
    rng = random.Random(7)
    for y in range(H):
        for x in range(W):
            if grid[y][x] == "mountain":
                v = variant("mountain", x, y)
                c, r = rng.choice(peaks.get(v, peaks["mountain"]))
                spr = MT.crop((c * 48, r * 48, c * 48 + 96, r * 48 + 96))
                canvas.alpha_composite(spr, (x * 48 - 24 + rng.randint(-4, 4), y * 48 - 44))
    return canvas, cm


LANDMARK_FILES = {"town_mark": "!$Overworld_Village1.png", "city": "!$Overworld_Castle1.png",
                  "dungeon_mark": "!$Overworld_Castle_Mountain.png", "ruin": "!$Overworld_Castle3.png"}


LOC_SPRITES = {
    "L_T01": ("!$Overworld_Village1.png", None), "L_T02": ("!$Overworld_Castle1.png", None),
    "L_T03": ("!$Overworld_Castle3.png", None), "L_T04": ("!$Overworld_village_sea.png", None),
    "L_T05": ("!$Overworld_Castle2.png", None), "L_T06": ("!$Overworld_Castle1_desert.png", None),
    "L_T07": ("!$Overworld_village_sea.png", None), "L_D01": ("!$Overworld_Mountain2.png", None),
    "L_D03": ("!$Overworld_BigTree.png", None), "L_D04": ("!Overworld_towers.png", 1),
    "L_D05": ("!Overworld_towers.png", 2), "L_D06": ("!Overworld_towers.png", 5), "L_D07": ("!$Overworld_Castle2.png", None),
    "L_D08": ("!$Overworld_Castle_magic.png", None), "L_D09": ("!Overworld_towers.png", 0),
    "L_D10": ("!$Overworld_magicshield.png", None), "L_D11": ("!Overworld_towers.png", 6),
    "L_D12": ("!Overworld_towers.png", 3),
}


def landmarks(canvas, cm, grid):
    """Location markers: each location's landmark sprite (RPG Maker character sheets: '$' = one 3x4 sheet, else
    4x2 characters of 3x4 frames; the middle frame of the first row faces the camera)."""
    objs = []
    placed = set()
    for e in cm["entities"]:
        if e["type"] != "location" or e["id"] not in LOC_SPRITES or (e["x"], e["y"]) in placed:
            continue
        placed.add((e["x"], e["y"]))
        f, k = LOC_SPRITES[e["id"]]
        sheet = Image.open(os.path.join(W48, "characters", f)).convert("RGBA")
        if k is None:
            fw, fh = sheet.width // 3, sheet.height // 4
            spr = sheet.crop((fw, 0, 2 * fw, fh))
        else:
            fw, fh = sheet.width // 12, sheet.height // 8
            bx, by = (k % 4) * 3 * fw, (k // 4) * 4 * fh
            spr = sheet.crop((bx + fw, by, bx + 2 * fw, by + fh))
        x, y = e["x"], e["y"]
        if True:
            bb = spr.getbbox()
            if not bb:
                continue
            spr = spr.crop((0, 0, fw, bb[3]))
            px = x * 48 + 24 - fw // 2
            py = (y + 1) * 48 - spr.height + 4
            canvas.alpha_composite(spr, (max(0, px), max(0, py)))
    return objs


def save(mid, texts):
    raw = autoskin.raw_sections()[mid]
    lg = dict(LEGEND_BASE)
    lg.update(raw[3])
    w0 = max(len(r) for r in raw[2])
    grid = [[lg.get(ch, "water") for ch in r.ljust(w0, "~")] for r in raw[2]]
    content = json.load(open(os.path.join(REPO, "game", "content", "content.json"), encoding="utf-8"))
    ents = content["maps"][mid]["entities"]
    grid = refine(mid, grid, ents, w0, len(grid))
    canvas, cm = build(mid, grid)
    landmarks(canvas, cm, grid)
    m = kit.Map(mid, w0, len(grid), cm["name"], cm["tileset"])
    m.kind = grid
    texts.append(autoskin.map_text(m, raw))
    os.makedirs(os.path.join(kit.EXT, "maps48"), exist_ok=True)
    canvas.convert("RGB").save(os.path.join(kit.EXT, "maps48", mid + "_ground.png"), optimize=True)
    json.dump({"id": mid, "w": cm["w"], "h": cm["h"], "ground": mid + "_ground.png", "over": "", "sheets": [], "objects": [], "anims": []},
              open(os.path.join(kit.EXT, "maps48", mid + ".json"), "w"))
    print("world", mid)


if __name__ == "__main__":
    texts = []
    for mid in (sys.argv[1:] or ["WORLD", "WORLD_POST"]):
        save(mid, texts)
    if len(texts) == 2 or "--write" in sys.argv:
        print(kit.write_group("world", texts))
