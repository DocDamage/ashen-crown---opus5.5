"""Bellharbor (T04, Glass Coast): hand-made maps for Bell Quay, Chartmaker Lane, the Back Alleys and the post-fault
Upper Town. Art in tools/maps48/lib_bell.py.

Shape: port (layout standard section 4). The town runs down from the rampart and its sea gate to a stone quay, and
from the quay out along three piers; the Ministry ferry lies moored at the end of the main axis (gate -> stairs ->
central pier). Two levels on every exterior: rampart / upper street / quay / piers on Bell Quay, the raised shop
pavement over the lane and the inner-harbour walk on Chartmaker Lane, the terraces of the alleys, and the ropewalks
over the flood in the Upper Town. Entities, sizes and headers are read unchanged from the original map sources."""
import sys, os
from collections import deque
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
from kit import Map, write_group, REPO, C
import compile_content as CC
import lib_bell as B

SOLID = set(CC.SOLID)


# ------------------------------------------------------------------------------------------------ helpers
def orig(fname, mid):
    """Header, size and entity lines of `mid` from its original map file (kept verbatim)."""
    lines = open(os.path.join(REPO, "content_src", "maps", fname), encoding="utf-8").read().split("\n")
    i = lines.index("=== " + mid)
    hdr, grid, ents, mode = {}, [], [], "hdr"
    for ln in lines[i + 1:]:
        if ln.startswith("=== "):
            break
        if mode == "hdr":
            if ln.strip() == "grid:":
                mode = "grid"
            elif ":" in ln and ln.strip() and not ln.startswith("legend"):
                k, v = ln.split(":", 1)
                hdr[k.strip()] = v.strip()
        elif mode == "grid":
            if ln.strip() == "entities:":
                mode = "ent"
            elif ln.strip():
                grid.append(ln)
        elif ln.strip():
            ents.append(ln)
    return hdr, len(grid[0]), len(grid), ents


def new_map(fname, mid, seed=7):
    hdr, w, h, ents = orig(fname, mid)
    base = {k: hdr.pop(k, "") for k in ("name", "tileset", "music", "zone", "location", "region")}
    m = Map(mid, w, h, base["name"], base["tileset"], music=base["music"], zone=base["zone"], location=base["location"],
            region=base["region"], group="bell", seed=seed, **hdr)
    m.use(**B.MATS)
    m.orig_ents = ents
    return m


def ent_points(m):
    """(type, x, y, x2, y2) of every positioned entity of the map."""
    out = []
    for ln in m.orig_ents:
        a = ln.split()
        t = a[0]
        try:
            if t in ("door", "exit", "trigger"):
                xs, ys = a[1], a[2]
                x1, x2 = (int(xs.split("..")[0]), int(xs.split("..")[1])) if ".." in xs else (int(xs), int(xs))
                y1, y2 = (int(ys.split("..")[0]), int(ys.split("..")[1])) if ".." in ys else (int(ys), int(ys))
                out.append((t, x1, y1, x2, y2))
            elif t == "spawn":
                out.append((t, int(a[2]), int(a[3]), int(a[2]), int(a[3])))
            elif t in ("npc",):
                out.append((t, int(a[2]), int(a[3]), int(a[2]), int(a[3])))
            elif t in ("sign", "shop", "inn", "save", "chest", "switch", "read"):
                out.append((t, int(a[1]), int(a[2]), int(a[1]), int(a[2])))
        except (ValueError, IndexError):
            pass
    return out


def entity_cells(m, pad=0):
    cells = set()
    for (t, x1, y1, x2, y2) in ent_points(m):
        for y in range(y1 - pad, y2 + pad + 1):
            for x in range(x1 - pad, x2 + pad + 1):
                cells.add((x, y))
    return cells


def verify(m):
    """Own reachability check (mirrors tools/check_reach.py, plus: everything reachable from the first spawn, door
    entities on door cells, spawns and exits walkable)."""
    W, H = m.w, m.h
    pts = ent_points(m)
    block = {(x, y) for (t, x, y, _, _) in pts if t in ("npc", "sign", "shop", "inn", "save", "chest", "switch")}

    def walk(x, y):
        return 0 <= x < W and 0 <= y < H and m.kind[y][x] not in SOLID and m.kind[y][x] is not None and (x, y) not in block
    probs = []
    sp = [(x, y) for (t, x, y, _, _) in pts if t == "spawn"]
    seen = {sp[0]}
    q = deque([sp[0]])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in seen and walk(*n):
                seen.add(n)
                q.append(n)
    for (t, x1, y1, x2, y2) in pts:
        cells = [(x, y) for x in range(x1, x2 + 1) for y in range(y1, y2 + 1)]
        if t in ("spawn", "door", "exit", "trigger"):
            ok = any(c in seen for c in cells)
        else:
            x, y = x1, y1
            rng = ((1, 0), (-1, 0), (0, 1), (0, -1)) + (((2, 0), (-2, 0), (0, 2), (0, -2)) if t in ("shop", "inn", "npc") else ())
            ok = any((x + dx, y + dy) in seen for dx, dy in rng)
        if t == "door" and m.kind[y1][x1] != "door":
            probs.append("door %d,%d is on %s" % (x1, y1, m.kind[y1][x1]))
        if not ok:
            probs.append("unreachable %s @ %d,%d" % (t, x1, y1))
    for p in probs:
        print(m.id, p)
    return probs


def put(m, s, x, ybase, **kw):
    """Place stamp s with its bottom row on row ybase."""
    return m.place(s, x, ybase - s.h + 1, **kw)


def solid_rect(m, x0, y0, x1, y1, kind="house"):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            m.solid(x, y, kind)


def building(m, s, x, y, kind="house"):
    """Whole building: every cell of the sprite blocks (the area behind is rampart or roof), door cell kept."""
    m.place(s, x, y, solid=s.h, kind=kind)


def sea_anims(m, mats=("sea",), foam=True, name="glint_teal"):
    """Animated ripples (transparent glint frames) over the baked swell texture on every water cell, surf foam
    below every quay or bank edge."""
    for y in range(m.h):
        for x in range(m.w):
            if m.mat[y][x] in mats:
                m.anim(name, x, y, h=48, flat=True)
                if foam and y > 0 and m.mat[y - 1][x] not in mats:
                    m.anim("shore_foam_top", x, y, h=1)


def smoke(m, x, y, dx=0, dy=0):
    m.anim("chimney_smoke", x, y, dx=dx, dy=dy, h=96)


def scatter_flat(m, stamps, x0, y0, x1, y1, n, on):
    """Flat decals on free, unreserved cells of the given materials (never on entities)."""
    ents = entity_cells(m)
    placed = tries = 0
    while placed < n and tries < n * 30:
        tries += 1
        x, y = m.rng.randint(x0, x1), m.rng.randint(y0, y1)
        if m.mat[y][x] in on and m.free(x, y) and (x, y) not in ents:
            m.place(m.rng.choice(stamps), x, y)
            placed += 1


# ------------------------------------------------------------------------------------------------ Bell Quay
def quay():
    m = new_map("t04.map", "T04_QUAY")
    W, H = m.w, m.h                                            # 44 x 30
    m.fill("cobble")
    # rampart walk (top) and the arcade wall under it; sea gate at 19-22
    m.rect("flags", 0, 0, W - 1, 1, kind="wall")
    m.rect("stonewall", 0, 2, W - 1, 3, kind="wall")
    m.rect("cobble", 20, 0, 21, 3)
    for x in list(range(0, 16, 4)) + [15] + list(range(23, 40, 4)) + [40]:
        m.place(B.ARCHES, x, 2, solid=2)
    m.place(B.TOWN_GATE, 19, 0, solid=0)
    for y in range(0, 4):
        m.solid(19, y, "wall")
        m.solid(22, y, "wall")
    for x in (2, 9, 13, 27, 31, 35):
        m.place(B.LAMP_STAND[x % 2], x, 0, solid=0)
    for (x, s) in ((5, B.B7_CRATES[0]), (6, B.B7_BARRELS[2]), (25, B.B7_CRATES[3]), (38, B.B7_BARRELS[0]), (39, B.B7_CRATES[2]),
                   (11, B.SACKS), (29, B.CANNONBALLS), (42, B.BARRELS[2])):
        m.place(s, x, 0, solid=0)
    m.anim("flag_blue", 17, 0, dy=-40, h=96)
    m.anim("flag_blue", 24, 0, dy=-40, h=96)

    # upper street; a paved square under the sea gate with its fountain
    m.rect("slabs", 18, 4, 23, 10)
    m.rect("flags", 3, 8, 11, 10)                            # the customs forecourt

    # north row of buildings (rows 4-7, chapel 5-8), backs against the arcade
    building(m, B.RTOWER, 0, 4, "wall")
    m.place(B.CRATE_PILE, 2, 4, solid=2)
    m.place(B.B7_CRATES[4], 4, 4, solid=2)
    m.place(B.CART, 2, 6, solid=2)
    m.place(B.BARREL_W, 4, 6, solid=2)
    building(m, B.GATEHOUSE, 5, 4)                            # Customs House, door (7,7)
    m.anim("flag_blue", 5, 3, dx=6, dy=-30, h=96)
    m.place(B.WALL_LOW, 9, 4, solid=2)
    building(m, B.HUT_TEAL, 9, 6)
    m.place(B.B7_CRATES[1], 11, 6, solid=2)
    m.place(B.BARREL_T[0], 12, 6, solid=2)
    building(m, B.H_TIMBER, 13, 4)
    smoke(m, 15, 3, dx=40, dy=-60)
    building(m, B.TOWER, 17, 4, "wall")
    building(m, B.TOWER, 23, 4, "wall")
    building(m, B.H_SHED, 25, 4)
    smoke(m, 26, 3, dx=30, dy=-50)
    m.place(B.WALL_LOW, 29, 4, solid=2)
    building(m, B.SHOP_TEAL, 29, 6)
    building(m, B.SHOP_A, 31, 6)
    building(m, B.CABIN, 33, 5)
    solid_rect(m, 33, 4, 35, 4, "wall")
    m.place(B.NET_RACK, 35, 7, solid=1)
    building(m, B.CHURCH, 37, 5)                              # Tide Chapel, door (38,8)
    solid_rect(m, 37, 4, 38, 4, "wall")
    m.place(B.PALMS[1], 38, 3, solid=0)
    m.solid(39, 6, "tree")
    m.place(B.WALL_LOW, 39, 7, solid=2)                       # the families' bells along the chapel wall
    for i, x in enumerate((39, 40, 41, 42)):
        m.place(B.BELLS[(i * 2) % 3], x, 6, dy=14 + (i % 2) * 4, over=True)
    solid_rect(m, 39, 4, 41, 6, "wall")
    building(m, B.RTOWER, 42, 3, "wall")
    solid_rect(m, 42, 7, 43, 7, "wall")
    m.place(B.LANTERN, 43, 7, solid=1)
    for (x, y) in ((15, 7), (27, 7), (34, 7)):                # houses without interiors: shut
        m.solid(x, y, "house")

    # street dressing: against the fronts (row 8) and along the terrace edge (row 10)
    for (s, x, y) in ((B.BARRELS[0], 0, 8), (B.CRATE_STACK, 0, 10), (B.WELL, 1, 10), (B.SACKS, 2, 8), (B.BARRELS[5], 3, 8),
                      (B.LAMP_STAND[0], 9, 8), (B.BARRELS[2], 10, 8), (B.B7_BARRELS[1], 13, 8), (B.CRATES[0], 16, 8),
                      (B.STALL_JARS, 14, 10), (B.STALL_BW, 16, 10),              # the fishwife's stalls (shop 16,10)
                      (B.LAMP_STAND[1], 18, 8), (B.LAMP_STAND[0], 23, 8), (B.FOUNTAIN, 20, 7),
                      (B.NOTICE, 24, 10), (B.CRATES[1], 28, 8), (B.BARRELS[3], 26, 8), (B.BENCH, 29, 8),
                      (B.POTS[1], 31, 8), (B.BIG_BARREL, 32, 8), (B.LAMP_STAND[1], 36, 8), (B.BENCH2, 27, 10),
                      (B.POTS[0], 30, 10), (B.SACKS_T, 32, 10), (B.BARRELS[4], 34, 10), (B.BARRELS[1], 3, 10),
                      (B.BENCH, 7, 10), (B.POTS[2], 9, 10), (B.CRATES[2], 11, 10), (B.BUCKETS[0], 12, 10),
                      (B.CHESTS[3], 35, 10), (B.FISHBOX[1], 40, 10), (B.CRATES[0], 41, 10)):
        put(m, s, x, y)

    # terrace face (row 11) with two stairs down to the quay
    m.rect("seawall", 0, 11, W - 1, 11)
    m.rect("steps", 14, 11, 25, 11)
    m.rect("steps", 37, 11, 40, 11)

    # quay (rows 12-17), stone edge (row 18), piers and the sea
    m.rect("slabs", 0, 12, W - 1, 17)
    m.blob("sand", 1, 15, 2.2, 2.6, rough=0.3)
    m.rect("quayedge", 0, 18, W - 1, 18)
    m.rect("sea", 0, 19, W - 1, H - 1)
    for (x0, x1) in ((4, 9), (19, 24), (37, 42)):              # wharf decking at the pier heads
        m.rect("planks", x0, 16, x1, 17)
    m.rect("planks", 5, 18, 8, 26)
    m.rect("planks", 20, 18, 23, 24)
    m.rect("planks", 38, 18, 41, 21)
    # breakwater and harbour light (south-west)
    m.rect("quayedge", 0, 28, 15, 29)
    m.rect("slabs", 0, 28, 15, 28, kind="wall")

    # quay dressing: against the terrace face
    for (s, x, y) in ((B.ROCKS_S[1], 0, 12), (B.B7_BARRELS[3], 4, 12), (B.CRATES[2], 5, 12), (B.FISH_RACK, 7, 12),
                      (B.SACKS, 9, 12), (B.NET_RACK, 11, 12), (B.BARRELS[1], 13, 12),
                      (B.SIGNPOST, 19, 12), (B.FLAGPOST, 21, 12), (B.POTS[2], 24, 12),   # the empty bell post (sign 19,12)
                      (B.WINCH, 26, 12), (B.CRATES[0], 28, 12), (B.CHESTS[1], 29, 12), (B.B7_BARRELS[4], 30, 12),
                      (B.BENCH_P[0], 32, 12), (B.LANTERN, 34, 12), (B.ANCHOR, 35, 12)):
        put(m, s, x, y)
    put(m, B.ROWBOAT_V, 1, 16, solid=2, kind="boat")
    building(m, B.CABIN, 41, 12)                                # net loft closing the east quay
    solid_rect(m, 41, 11, 43, 11, "wall")
    # mid-quay clusters (1-tile lanes stay open; the axis x 19-24 stays clear)
    for (s, x, y) in ((B.CRATES[1], 42, 15), (B.BARRELS[5], 43, 15), (B.B7_CRATES[2], 43, 17), (B.FISH_HANG, 41, 17),
                      (B.CAPSTAN, 12, 15), (B.FISHBOX[0], 8, 14), (B.BUCKETS[1], 11, 14), (B.CLOTH[0], 7, 14),
                      (B.FISH_RACK2, 15, 15), (B.BUCKETS[2], 17, 15), (B.BARRELS[0], 14, 14),
                      (B.BIG_BARREL, 25, 15), (B.HANDCART, 28, 15), (B.FISHBOX[1], 31, 14), (B.BARRELS[2], 32, 14),
                      (B.SACKS_T, 36, 14), (B.CART, 38, 15), (B.CHESTS[0], 40, 14),
                      (B.CRATES[2], 33, 17), (B.B7_CRATES[1], 34, 17), (B.ROPES[1], 36, 17), (B.RINGS[0], 9, 17),
                      (B.LANTERN, 12, 17), (B.LANTERN2, 25, 17)):
        put(m, s, x, y)
    for x in (3, 15, 18, 27, 30):                              # bollards on the quay edge
        put(m, B.BOLLARD[x % 2], x, 17)
    # piers
    for (s, x, y) in ((B.CRATES[0], 8, 19), (B.BARRELS[0], 5, 20), (B.BOLLARD[0], 5, 24), (B.BOLLARD[1], 8, 23),
                      (B.LANTERN_S, 8, 26), (B.ROPES[0], 6, 26), (B.FISHBOX[0], 5, 22),
                      (B.BARRELS[4], 23, 19), (B.BOLLARD[0], 20, 22), (B.BOLLARD[1], 23, 22), (B.LANTERN_S, 20, 24),
                      (B.ROPES[2], 23, 24), (B.CRATES[1], 38, 19), (B.FISHBOX[0], 41, 20), (B.BOLLARD[0], 38, 21),
                      (B.BARRELS[3], 41, 18)):
        put(m, s, x, y)
    # breakwater: stones, a bollard, the harbour light at its end
    for (s, x, y) in ((B.BIG_ROCKS[0], 0, 29), (B.ROCKS_S[0], 2, 28), (B.BOLLARD[1], 4, 28), (B.ROCKS_S[3], 6, 29),
                      (B.LANTERN_S, 8, 28), (B.BIG_ROCKS[1], 10, 29), (B.ROCKS_S[5], 12, 28), (B.ROPES[1], 13, 28)):
        put(m, s, x, y, solid=0)
    building(m, B.TOWER, 14, 25, "wall")
    m.anim("brazier", 14, 23, dx=24, dy=40, h=96)
    for (s, x, y) in ((B.BIG_ROCKS[0], 16, 29), (B.ROCKS_S[4], 18, 29), (B.ROCKS_S[2], 42, 27), (B.BIG_ROCKS[1], 40, 29),
                      (B.ROCKS_S[1], 43, 25)):
        put(m, s, x, y, kind="rock")
    # boats and the ferry
    for (s, x, y) in ((B.ROWBOAT_V, 4, 23), (B.SKIFF_V, 9, 21), (B.LONGBOAT[0], 9, 25), (B.ROWBOAT_H, 1, 21),
                      (B.LONGBOAT[1], 13, 21), (B.ROWBOAT_H, 17, 26), (B.SKIFF_V, 42, 21), (B.ROWBOAT_H, 1, 25),
                      (B.SKIFF_V, 11, 27), (B.FLOTSAM[0], 17, 20), (B.PLANK_V[1], 42, 24),
                      (B.PLANK_V[0], 4, 20), (B.PLANK_V[1], 9, 19), (B.PLANK_V[0], 4, 26), (B.PLANK_V[1], 19, 20),
                      (B.PLANK_V[0], 24, 20), (B.PLANK_V[1], 37, 20), (B.PLANK_V[0], 19, 24), (B.BUOYS[0], 15, 24),
                      (B.BUOYS[1], 30, 20), (B.FLOTSAM[1], 36, 28), (B.ROWBOAT_H, 40, 23)):
        put(m, s, x, y)
    m.place(B.SHIP, 24, 17, solid=0)
    sea_anims(m)
    # flat dressing: rope coils, shells, stones
    scatter_flat(m, B.DECALS_Q + B.PEBBLES, 0, 12, W - 1, 17, 24, on=("slabs",))
    scatter_flat(m, B.SHELLS + B.PEBBLES, 0, 12, 4, 17, 6, on=("sand",))
    scatter_flat(m, B.DECALS_Q, 0, 18, W - 1, 26, 6, on=("planks",))
    scatter_flat(m, B.PEBBLES, 0, 4, W - 1, 10, 10, on=("slabs", "cobble", "flags"))
    for ln in m.orig_ents:
        m.ent(ln)
    return m


# ------------------------------------------------------------------------------------------------ Chartmaker Lane
def lane():
    m = new_map("t04.map", "T04_LANE", seed=11)
    W, H = m.w, m.h                                            # 36 x 22
    m.fill("cobble")
    # old sea wall of the upper town behind the shops
    m.rect("flags", 0, 0, W - 1, 1, kind="wall")
    for i, x in enumerate(range(0, W, 4)):
        m.place((B.WALL, B.ARCHES, B.WALL_MOSS)[i % 3], x, 0, solid=2)
    # north shops (rows 2-5): Jori's office is the timber house, door (16,5)
    building(m, B.TOWER, 0, 2, "wall")
    building(m, B.H_SHED, 2, 2)
    building(m, B.CABIN, 6, 3)
    solid_rect(m, 6, 2, 9, 2, "wall")
    m.place(B.LAMP_STAND[0], 9, 4, solid=2)
    solid_rect(m, 9, 2, 9, 3, "wall")
    building(m, B.H_STONE, 10, 2)
    building(m, B.H_TIMBER, 14, 2)                             # Jori's office
    smoke(m, 16, 1, dx=40, dy=-60)
    building(m, B.TOWER, 18, 2, "wall")
    building(m, B.H_THATCH, 20, 2)
    building(m, B.WATCH, 24, 2)
    m.place(B.WALL_LOW, 26, 2, solid=2)
    building(m, B.SHOP_TEAL, 26, 4)
    building(m, B.SHOP_PURPLE, 28, 4)
    building(m, B.H_SHED, 30, 2)
    smoke(m, 31, 1, dx=30, dy=-50)
    building(m, B.RTOWER, 34, 2, "wall")
    for (x, y) in ((4, 5), (7, 5), (11, 5), (21, 5), (32, 5)):   # shop doors without interiors stay shut
        m.solid(x, y, "house")
    m.anim("flag_blue", 18, 1, dy=-44, h=96)
    # raised pavement (row 6) and its kerb (row 7) with three flights of steps down to the lane
    m.rect("slabs", 0, 6, W - 1, 6)
    m.rect("seawall", 0, 7, W - 1, 7)
    m.rect("steps", 3, 7, 4, 7)
    m.rect("steps", 14, 7, 18, 7)
    m.rect("steps", 26, 7, 27, 7)
    for (s, x, y) in ((B.B7_BARRELS[0], 1, 6), (B.CRATES[1], 5, 6), (B.MAP_STALLS[0], 7, 6), (B.SCROLLS[0], 9, 6),
                      (B.MAP_STALLS[2], 12, 6), (B.LAMP_STAND[1], 18, 6), (B.SCROLLS[1], 19, 6), (B.MAP_STALLS[3], 22, 6),
                      (B.CHESTS[0], 24, 6), (B.BARRELS[3], 25, 6), (B.POTS[1], 28, 6), (B.B7_CRATES[4], 29, 6),
                      (B.BUCKETS[3], 31, 6), (B.LAMP_STAND[0], 33, 6), (B.BARRELS[0], 35, 6)):
        put(m, s, x, y)
    # the lane (rows 8-13): a slab gutter down the middle, stalls and lamps along the harbour parapet
    m.rect("slabs", 0, 11, 33, 11)
    for (s, x, y) in ((B.BARRELS[5], 5, 8), (B.LAMP_STAND[0], 8, 8), (B.WELL, 11, 9), (B.MAP_STALLS[1], 20, 9),
                      (B.CHART_BOARD[0], 24, 9), (B.MAP_STALLS[2], 28, 9), (B.LAMP_STAND[1], 31, 8), (B.B7_CRATES[2], 34, 9),
                      (B.BARRELS[4], 35, 9), (B.CRATES[2], 35, 8), (B.BARRELS[2], 13, 8), (B.SACKS, 23, 8),
                      (B.CRATES[1], 1, 13), (B.BARRELS[1], 2, 13), (B.LAMP_STAND[1], 4, 13), (B.BENCH, 6, 13),
                      (B.SACKS_T, 11, 13), (B.CHART_BOARD[1], 13, 13), (B.LAMP_STAND[0], 15, 13), (B.STALL_JARS, 16, 13),
                      (B.BARRELS[3], 19, 13), (B.CRATES[0], 20, 13), (B.BENCH2, 22, 13), (B.HANDCART, 25, 13),
                      (B.BUCKETS[0], 28, 13), (B.LAMP_STAND[1], 29, 13), (B.BENCH, 31, 13), (B.CHESTS[2], 33, 13),
                      (B.CRATES[2], 2, 8), (B.BENCH2, 6, 9), (B.SACKS, 15, 9), (B.BARRELS[0], 18, 9), (B.CRATES[1], 19, 9),
                      (B.B7_BARRELS[3], 32, 9), (B.BARRELS[2], 33, 8), (B.CRATES[0], 3, 12), (B.POTS[0], 12, 12),
                      (B.BUCKETS[2], 21, 12), (B.FISHBOX[0], 27, 12), (B.CRATES[2], 34, 13), (B.BARRELS[5], 24, 12),
                      (B.BUSH[0], 0, 6), (B.BUSH[3], 34, 6), (B.BUSH[4], 13, 6)):
        put(m, s, x, y)
    building(m, B.WATCH, 34, 10)                               # lookout closing the lane's east end
    # inner harbour: parapet, water, the far bank's houses
    m.rect("seawall", 0, 14, W - 1, 14)
    m.rect("sea", 0, 15, W - 1, 18)
    m.rect("steps", 9, 14, 10, 14)                            # water steps and a boat landing
    m.rect("planks", 8, 15, 11, 15)
    m.rect("slabs", 0, 19, W - 1, H - 1, kind="house")
    for (s, x, y) in ((B.H_THATCH, 0, 19), (B.CABIN, 4, 19), (B.H_STONE, 7, 19), (B.TOWER, 11, 19),
                      (B.H_TIMBER, 13, 19), (B.WALL, 17, 20), (B.GATEHOUSE, 21, 19), (B.SHOP_A, 25, 20),
                      (B.SHOP_HERB, 27, 20), (B.H_STONE, 29, 19), (B.RTOWER, 33, 19)):
        m.place(s, x, y, solid=0)
    m.place(B.PALMS[3], 17, 17, dy=8, solid=0)
    for (s, x, y) in ((B.BOLLARD[0], 8, 15), (B.ROPES[0], 11, 15), (B.ROWBOAT_H, 3, 16), (B.LONGBOAT[0], 9, 17), (B.SKIFF_V, 16, 16), (B.ROWBOAT_H, 22, 15),
                      (B.LONGBOAT[1], 28, 16), (B.PLANK_V[0], 34, 17), (B.FLOTSAM[1], 13, 15), (B.ROWBOAT_V, 1, 18),
                      (B.SKIFF_V, 32, 16), (B.FLOTSAM[0], 19, 18)):
        put(m, s, x, y)
    sea_anims(m)
    scatter_flat(m, B.DECALS_Q + B.PEBBLES, 0, 8, W - 1, 13, 18, on=("cobble",))
    scatter_flat(m, B.PEBBLES, 0, 6, W - 1, 6, 4, on=("slabs",))
    for ln in m.orig_ents:
        m.ent(ln)
    return m


# ------------------------------------------------------------------------------------------------ Back Alleys (chase)
def chase():
    m = new_map("t04.map", "T04_CHASE", seed=5)
    W, H = m.w, m.h                                            # 30 x 20
    m.fill("cobble")
    m.rect("stonewall", 0, 0, W - 1, 0, kind="wall")
    m.rect("stonewall", 0, 0, 0, 15, kind="wall")
    m.rect("stonewall", W - 1, 4, W - 1, H - 1, kind="wall")
    m.rect("stonewall", 0, H - 1, W - 1, H - 1, kind="wall")
    m.rect("steps", 28, 1, 29, 3)
    for y in (6, 12):
        for x in (6, 15, 24):
            m.set(x, y, "steps")
    for y in (5, 11, 17):                                       # worn slab runs along the alleys
        m.rect("slabs", 1, y, 28, y)

    def fillwall(x0, y0, x1, y1):
        m.rect("stonewall", x0, y0, x1, y1, kind="wall")

    # top terrace: houses on rows 0-3, alley rows 4-5, the way out at the east end
    building(m, B.H_THATCH, 1, 0)
    fillwall(5, 0, 6, 1)
    building(m, B.SHOP_HERB, 5, 2)
    building(m, B.H_STONE, 7, 0)
    building(m, B.TOWER, 11, 0, "wall")
    building(m, B.H_TIMBER, 13, 0)
    fillwall(17, 0, 18, 1)
    building(m, B.SHED, 17, 2)
    building(m, B.STILT_HUT, 19, 0)
    fillwall(21, 0, 23, 0)
    building(m, B.CABIN, 21, 1)
    m.place(B.WALL_LOW, 24, -1, solid=0)
    put(m, B.CRATE_PILE, 24, 2)
    put(m, B.BARRELS[2], 25, 5)
    put(m, B.LANTERN, 28, 5)
    # middle terrace: houses rows 6-9 with stair lanes at x 6, 15, 24; alley rows 10-11
    building(m, B.CABIN, 1, 7)
    fillwall(1, 6, 3, 6)
    fillwall(4, 6, 5, 7)
    building(m, B.HUT_TEAL, 4, 8)
    building(m, B.H_SHED, 7, 6)
    m.place(B.WALL_LOW, 11, 6, solid=2)
    building(m, B.SHOP_A, 11, 8)
    building(m, B.TANNERY, 13, 8)
    building(m, B.H_STONE, 16, 6)
    m.place(B.WALL, 20, 6, solid=2)
    building(m, B.SMITHY, 20, 8)
    building(m, B.SHED, 22, 8)
    building(m, B.H_TIMBER, 25, 6)
    # bottom terrace: houses rows 12-15, alley rows 16-18 (the chase starts at its west mouth)
    fillwall(1, 12, 3, 13)
    building(m, B.HUT, 1, 14)
    put(m, B.BARREL_W, 3, 15)
    building(m, B.TOWER, 4, 12, "wall")
    building(m, B.H_THATCH, 7, 12)
    m.place(B.WALL_MOSS, 11, 12, solid=2)
    building(m, B.SHOP_PURPLE, 11, 14)
    building(m, B.HUT_TEAL, 13, 14)
    building(m, B.H_SHED, 16, 12)
    fillwall(20, 12, 23, 12)
    building(m, B.CABIN, 20, 13)
    put(m, B.B7_BARRELS[3], 23, 15)
    building(m, B.H_STONE, 25, 12)
    # every house door here is shut (back alleys)
    for y in range(H):
        for x in range(W):
            if m.kind[y][x] == "door":
                m.solid(x, y, "house")
    # lamps at the stair heads (stair lanes x 6, 15, 24)
    for (x, y) in ((5, 7), (12, 7), (14, 13), (23, 12)):       # torches on the yard walls by the stair lanes
        m.anim("torch_wall", x, y, dy=-40, h=96)
    smoke(m, 27, 5, dx=40, dy=-60)
    for (x0, y0, x1, y1, mat) in ((7, 16, 13, 18, "cobble2"), (17, 10, 22, 11, "cobble2"), (1, 4, 4, 5, "cobble2"),
                                  (25, 1, 27, 5, "cobble2"), (9, 4, 13, 4, "flags"), (1, 10, 5, 10, "flags"),
                                  (21, 16, 27, 16, "flags"), (16, 4, 21, 4, "cobble2"), (25, 10, 28, 11, "flags"),
                                  (1, 18, 5, 18, "cobble2")):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if m.mat[y][x] in ("cobble", "slabs"):
                    m.mat[y][x] = mat
    # alley clutter against the house fronts; the walking line stays open
    for (s, x, y) in ((B.BARRELS[0], 1, 4), (B.CRATES[0], 3, 4), (B.LAUNDRY, 9, 4), (B.CHESTS[1], 12, 4),
                      (B.B7_CRATES[0], 16, 4), (B.SACKS, 17, 4), (B.BUCKETS[2], 20, 4), (B.BARRELS[5], 22, 4),
                      (B.POTS[0], 4, 4), (B.CRATES[2], 11, 4), (B.FISHBOX[0], 19, 4), (B.BUCKETS[1], 23, 4),
                      (B.BARREL_T[1], 2, 10), (B.CRATES[1], 4, 10), (B.LAUNDRY2, 8, 10), (B.POTS[2], 11, 10),
                      (B.CRATES[2], 13, 10), (B.FISH_RACK2, 17, 10), (B.BARRELS[3], 21, 10), (B.CLOTH[1], 22, 10),
                      (B.B7_BARRELS[1], 26, 10), (B.CRATES[0], 28, 10), (B.BARRELS[1], 12, 10), (B.SACKS, 23, 10),
                      (B.CRATE_STACK, 2, 16), (B.BARRELS[1], 4, 16), (B.NET_RACK, 8, 16), (B.CHESTS[2], 12, 16),
                      (B.B7_CRATES[3], 14, 16), (B.LAUNDRY, 18, 16), (B.BARRELS[4], 21, 16), (B.SACKS_T, 26, 16),
                      (B.BUCKETS[0], 3, 18), (B.CRATES[1], 9, 18), (B.BARRELS[2], 10, 18), (B.ROCKS_S[2], 16, 18),
                      (B.B7_BARRELS[4], 20, 18), (B.CRATES[2], 27, 18), (B.BARRELS[0], 28, 18), (B.POTS[1], 13, 18),
                      (B.CRATES[0], 22, 16), (B.FISHBOX[1], 5, 18), (B.BARRELS[4], 27, 10), (B.CHESTS[3], 5, 10),
                      (B.BUCKETS[3], 10, 16), (B.CRATES[1], 25, 18), (B.SACKS, 18, 18), (B.POTS[0], 27, 16),
                      (B.BARRELS[2], 20, 10), (B.CLOTH[0], 10, 4), (B.BUCKETS[0], 27, 4)):
        if (x, y) not in entity_cells(m):
            put(m, s, x, y)
    scatter_flat(m, B.PEBBLES * 3 + B.DECALS_Q[:1], 1, 1, W - 2, H - 2, 40, on=("cobble", "slabs", "cobble2", "flags"))
    for ln in m.orig_ents:
        m.ent(ln)
    return m


# ------------------------------------------------------------------------------------------------ Upper Town (post-fault)
def upper():
    m = new_map("post_r03.map", "T04_UPPER", seed=23)
    W, H = m.w, m.h                                            # 46 x 32
    m.fill("silt_sea")
    # north strip (rows 5-8, houses on 2-5) and the causeway up to the gallery (x 40-43)
    m.rect("cobble", 2, 5, 43, 8)
    m.rect("planks", 40, 0, 43, 4)
    # south strip (rows 20-25), the world road leaves west
    m.rect("cobble", 0, 20, 43, 25)
    m.rect("sand", 0, 25, 43, 25)
    for x in range(2, 44):                                      # silt left by the flood along both waterlines
        if not 20 <= x <= 23:
            m.set(x, 8, "silt")
            m.set(x, 20, "silt")
    # the ropewalk (x 20-23) across the flood, a broken one to the west
    m.rect("planks", 20, 8, 23, 20)
    m.rect("planks2", 8, 9, 9, 12)
    # north buildings: two standing, one broken open, one gone to rubble
    building(m, B.H_TIMBER, 4, 2)
    smoke(m, 6, 1, dx=40, dy=-60)
    m.place(B.ROOF_TOWER, 2, 3, solid=0)
    solid_rect(m, 2, 3, 3, 4, "house")
    building(m, B.SHOP_TEAL, 8, 4)
    put(m, B.RUIN_WALLS[1], 13, 5)
    put(m, B.RUIN_WALLS[3], 16, 5)
    building(m, B.H_STONE, 28, 2)
    building(m, B.CABIN, 33, 3)
    put(m, B.RUIN_WALLS[0], 36, 5)
    for (x, y) in ((6, 5), (29, 5), (34, 5)):
        m.solid(x, y, "house")
    # north strip: Jori's names board, the pot, a shelter camp, crates brought up from below
    for (s, x, y) in ((B.NOTICE, 25, 5), (B.BUCKETS[3], 23, 6), (B.POTS[2], 27, 7), (B.LAUNDRY, 10, 7),
                      (B.CRATES[0], 18, 7), (B.B7_CRATES[2], 19, 6), (B.BARRELS[3], 30, 7), (B.CRATES[1], 36, 7),
                      (B.LAUNDRY2, 41, 7), (B.LAMP_STAND[0], 12, 5), (B.LAMP_STAND[1], 38, 5), (B.SACKS, 3, 8),
                      (B.BARRELS[1], 32, 8), (B.B7_BARRELS[2], 43, 6), (B.LANTERN_S, 43, 2), (B.BOLLARD[0], 40, 1),
                      (B.TENTS[0], 38, 8), (B.BEDROLLS[0], 37, 6), (B.CAMPFIRE, 34, 8), (B.SACKS_T, 14, 8),
                      (B.BUCKETS[1], 11, 5), (B.ROCKS_S[3], 2, 7), (B.BARRELS[0], 26, 5),
                      (B.CHESTS[0], 31, 5), (B.FISHBOX[1], 42, 8), (B.RUIN_BITS[0], 6, 7), (B.BARRELS[2], 8, 6),
                      (B.BIG_ROCKS[1], 24, 8), (B.CRATES[0], 37, 8), (B.ROPES[1], 29, 7), (B.BUCKETS[0], 33, 6)):
        put(m, s, x, y)
    # ropewalk rails: posts both sides, lamps, rope coils
    for y in (9, 12, 15, 18):
        put(m, B.BOLLARD[y % 2], 20, y)
        put(m, B.BOLLARD[(y + 1) % 2], 23, y)
    put(m, B.LANTERN_S, 23, 10)
    put(m, B.LANTERN_S, 20, 16)
    put(m, B.ROPES[0], 8, 12, solid=1)
    put(m, B.BARRELS[4], 9, 11)
    # south: the tide chapel (door 12,21; inn 13,21), the chart stall, the ropemaker's yard
    building(m, B.CHURCH, 11, 18)
    put(m, B.MAP_STALLS[3], 8, 23)                              # chart seller (npc 10,23)
    building(m, B.H_THATCH, 3, 17)
    m.solid(4, 20, "house")
    building(m, B.H_SHED, 30, 17)
    m.solid(32, 20, "house")
    for (s, x, y) in ((B.BENCH_P[1], 14, 23), (B.LANTERN, 16, 21), (B.RUIN_WALLS[2], 25, 21), (B.SPOOL, 33, 22),
                      (B.WINCH, 38, 22), (B.ROPES[1], 35, 22), (B.ROPES[2], 37, 24), (B.LAUNDRY, 34, 25),
                      (B.NET_RACK, 40, 25), (B.FISH_RACK, 18, 25), (B.CRATES[2], 28, 23), (B.BARRELS[4], 27, 24),
                      (B.B7_CRATES[1], 42, 21), (B.BARRELS[5], 43, 22), (B.LAMP_STAND[0], 24, 21), (B.LAMP_STAND[1], 7, 21),
                      (B.TENTS[1], 14, 21), (B.TENTS[2], 8, 21), (B.BEDROLLS[1], 16, 24), (B.WINCH, 18, 23),
                      (B.BUCKETS[0], 20, 23), (B.SACKS_T, 26, 21), (B.CHESTS[3], 29, 21), (B.BARRELS[2], 2, 21),
                      (B.CRATES[0], 3, 24), (B.ROCKS_S[1], 1, 25), (B.BUCKETS[2], 41, 23), (B.CRATES[1], 22, 25),
                      (B.BIG_BARREL, 34, 21), (B.RUIN_BITS[1], 36, 25), (B.CRATES[2], 6, 22), (B.BARRELS[0], 26, 25),
                      (B.ROCKS_S[2], 12, 25), (B.SACKS, 31, 22), (B.BARRELS[1], 39, 21),
                      (B.CHESTS[1], 23, 23), (B.FISHBOX[0], 1, 23)):
        put(m, s, x, y)
    # the drowned lower town: roofs, broken walls and the sunk ferry in the flood
    roofs = ((B.ROOF_TIMBER, 4, 11), (B.ROOF_THATCH, 12, 14), (B.ROOF_TOWER, 17, 12), (B.ROOF_SHED, 1, 14),
             (B.ROOF_TIMBER, 14, 9), (B.ROOF_SHED, 2, 27), (B.ROOF_TOWER, 26, 29), (B.ROOF_THATCH, 38, 27),
             (B.ROOF_TIMBER, 9, 28), (B.ROOF_SHED, 30, 28), (B.ROOF_THATCH, 16, 27), (B.ROOF_TOWER, 44, 12),
             (B.ROOF_TIMBER, 16, 1), (B.ROOF_THATCH, 24, 0), (B.ROOF_TOWER, 36, 0), (B.ROOF_SHED, 5, 16))
    for (s, x, y) in roofs:
        m.place(s, x, y, solid=0)
        for dx in range(s.w):
            if 0 <= y + s.h < H:
                m.anim("shore_foam_top", x + dx, y + s.h, h=1)
    m.place(B.WRECK, 25, 9, solid=0)
    for x in range(0, W, 4):                                    # the old harbour arcade, drowned to its arches
        m.place(B.ARCHES, x, 30, solid=0)
    for (s, x, y) in ((B.ARCHES_TOP, 0, 12), (B.ARCHES_TOP, 9, 18), (B.ARCHES_TOP, 41, 9), (B.ROOF_SHED, 14, 16)):
        m.place(s, x, y, solid=0)
    for (s, x, y) in ((B.RUIN_WALLS[0], 7, 16), (B.RUIN_WALLS[2], 22, 27), (B.RUIN_WALLS[3], 33, 29), (B.RUIN_BITS[0], 42, 17),
                      (B.RUIN_BITS[1], 0, 10), (B.RUIN_WALLS[1], 12, 1), (B.RUIN_BITS[0], 30, 0), (B.RUIN_WALLS[0], 43, 29)):
        put(m, s, x, y + s.h - 1, solid=0)
    for (s, x, y) in ((B.ROWBOAT_V, 17, 16), (B.PLANK_V[0], 10, 17), (B.PLANK_V[1], 43, 15), (B.ROWBOAT_H, 1, 18),
                      (B.LONGBOAT[0], 13, 30), (B.SKIFF_V, 44, 23), (B.PLANK_V[0], 20, 29), (B.ROWBOAT_H, 1, 1),
                      (B.FLOTSAM[0], 6, 19), (B.FLOTSAM[1], 36, 19), (B.FLOTSAM[0], 27, 26), (B.BIG_ROCKS[0], 0, 29),
                      (B.BIG_ROCKS[1], 44, 30), (B.ROCKS_S[2], 19, 1), (B.FLOTSAM[1], 34, 1), (B.SKIFF_V, 43, 18),
                      (B.BARRELS[0], 10, 19), (B.CRATES[1], 29, 18), (B.ROCKS_S[4], 16, 30), (B.FLOTSAM[0], 40, 30),
                      (B.BARRELS[2], 3, 10), (B.FLOTSAM[1], 11, 11), (B.CRATES[2], 18, 17), (B.PLANK_V[1], 7, 13),
                      (B.ROWBOAT_H, 26, 18), (B.BARRELS[5], 42, 13), (B.FLOTSAM[0], 33, 18), (B.ROCKS_S[0], 44, 5),
                      (B.BIG_ROCKS[1], 0, 3), (B.FLOTSAM[1], 26, 3), (B.CRATES[0], 38, 3), (B.PLANK_V[0], 12, 26),
                      (B.BARRELS[3], 33, 27), (B.ROWBOAT_V, 42, 26)):
        put(m, s, x, y, solid=0)
    sea_anims(m, mats=("silt_sea",), name="glint_silt")
    scatter_flat(m, B.DECALS_Q + B.PEBBLES, 0, 3, W - 1, 25, 20, on=("cobble", "planks"))
    scatter_flat(m, B.STONES + B.SHELLS, 0, 8, W - 1, 25, 14, on=("silt", "sand"))
    for ln in m.orig_ents:
        m.ent(ln)
    return m


MAPS = [quay, lane, chase, upper]

if __name__ == "__main__":
    built = [f() for f in MAPS]
    bad = 0
    for m in built:
        bad += len(verify(m))
    print(write_group("bell", [m.save() for m in built]))
    print("bell: own check problems:", bad)
