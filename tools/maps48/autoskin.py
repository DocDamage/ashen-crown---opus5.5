"""Auto-skin: native 48px art for every map that has no hand-authored script, from its existing collision grid.

A Skin (skins/<tileset>.py, one per content tileset) says how each grid kind is drawn:
  ground   kind -> material (floors, paths, water ...)
  walls    kind -> WallStyle (cap texture + vertical face strip; faces appear where a wall meets open ground below)
  props    kind -> list of stamps (runs of the same kind are filled with the widest stamps that fit)
  trees    stamps for tree/tree2/forest cells (trunk on the cell, canopy overhanging)
  decals   flat stamps scattered on open floor; wall_decor: torches/banners mounted on wall faces
Collision never changes: art is drawn over the grid the game already uses.
Usage: python tools/maps48/autoskin.py [MAP_ID ...]   (default: every map without a hand-made script)
"""
import os, sys, json, importlib, glob
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kit
from kit import Map, C, sheet_img, EXT

REPO = kit.REPO


class WallStyle:
    def __init__(self, face, cap, face_h=1, rim=(0, 0, 0), cap_mat=None, top_edge=None):
        """face: (alias, sheet, x, y, w, h) texture strip (h = face_h*48) tiled horizontally.
        cap: material name for the wall top. top_edge: optional (alias, sheet, x, y, w, 12..24) strip drawn along
        the top of every face (a lit rim)."""
        self.face, self.cap, self.face_h, self.rim, self.top_edge = face, cap, face_h, rim, top_edge


class Skin:
    def __init__(self, mats, ground, default, walls=None, props=None, trees=None, decals=None, decal_density=0.05,
                 wall_decor=None, decor_every=6, void="void", water_anim=None, over_kinds=None,
                 dress_wall=None, dress_open=None, dress_target=0.0, dress_kind="crate"):
        self.mats, self.ground, self.default = mats, ground, default
        self.walls = walls or {}
        self.props = props or {}
        self.trees = trees or []
        self.decals = decals or []
        self.decal_density = decal_density
        self.wall_decor = wall_decor or []
        self.decor_every = decor_every
        self.void = void
        self.water_anim = water_anim or {}
        self.over_kinds = over_kinds or set()
        # auto-dressing (adds solid props where reachability allows): stamps against walls / in open floor,
        # target = share of open floor cells to fill (interiors 0.25-0.4, dungeons 0.06-0.12)
        self.dress_wall = dress_wall or []
        self.dress_open = dress_open or []
        self.dress_target = dress_target
        self.dress_kind = dress_kind


def load_skin(tileset):
    mod = importlib.import_module("skins." + tileset)
    return mod.SKIN


def _tile(img_src, W, H):
    th, tw = img_src.shape[:2]
    reps = (H // th + 1, W // tw + 1, 1)
    return np.tile(img_src, reps)[:H, :W]


def build(mid, content, raw=None):
    cm = content["maps"][mid]
    skin = load_skin(cm["tileset"])
    W, H = int(cm["w"]), int(cm["h"])
    legend = cm["legend"]
    grid = [[legend.get(ch, "void") for ch in row] for row in cm["grid"]]
    if raw is not None and raw[2]:
        # always start from the original layout (auto-dressing is re-applied, never stacked)
        sys.path.insert(0, os.path.dirname(HERE))
        from compile_content import LEGEND_BASE
        lg = dict(LEGEND_BASE)
        lg.update(raw[3])
        w0 = max(len(r) for r in raw[2])
        grid = [[lg.get(ch, "void") for ch in r.ljust(w0, "_")] for r in raw[2]]
    m = Map(mid, W, H, cm["name"], cm["tileset"])
    mats = dict(skin.mats)
    mats.setdefault("void", kit.Mat([], "void"))
    m.use(**mats)
    reserved = set()
    for e in cm["entities"]:
        if "x" in e and "y" in e:
            reserved.add((int(e["x"]), int(e["y"])))
        for k in ("x1",):
            if k in e:
                for yy in range(e["y1"], e["y2"] + 1):
                    for xx in range(e["x1"], e["x2"] + 1):
                        reserved.add((xx, yy))
    # ---- ground materials (props and walls stand on the nearest ground)
    def ground_of(x, y):
        for r in range(1, 4):
            cnt = {}
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < W and 0 <= yy < H and grid[yy][xx] in skin.ground:
                        g = skin.ground[grid[yy][xx]]
                        if not mats[g].solid and grid[yy][xx] not in ("water", "deep", "void"):
                            cnt[g] = cnt.get(g, 0) + 1
            if cnt:
                return max(cnt, key=cnt.get)
        return skin.default
    for y in range(H):
        for x in range(W):
            k = grid[y][x]
            if k == "void":
                m.mat[y][x] = "void"
            elif k in skin.ground:
                m.mat[y][x] = skin.ground[k]
            elif k in skin.walls:
                m.mat[y][x] = skin.walls[k].cap
            else:
                m.mat[y][x] = ground_of(x, y)
            m.kind[y][x] = k
    # ---- walls: faces where a wall cell has open ground below
    faces = []
    for y in range(H):
        for x in range(W):
            k = grid[y][x]
            if k in skin.walls:
                below = grid[y + 1][x] if y + 1 < H else "void"
                if below not in skin.walls and below != "void":
                    faces.append((x, y, skin.walls[k]))
    # ---- props: runs of the same kind, left to right, widest stamp that fits
    done = set()
    for y in range(H):
        x = 0
        while x < W:
            k = grid[y][x]
            if k in skin.props and (x, y) not in done:
                run = 1
                while x + run < W and grid[y][x + run] == k and (x + run, y) not in done:
                    run += 1
                # vertical extent of the block (same kind directly below for the whole run)
                hgt = 1
                while y + hgt < H and all(grid[y + hgt][xx] == k for xx in range(x, x + run)):
                    hgt += 1
                opts = skin.props[k]
                xx = x
                while xx < x + run:
                    fit = [s for s in opts if s.w <= x + run - xx and (s.hgrid if hasattr(s, "hgrid") else 1) <= hgt]
                    if not fit:
                        fit = [min(opts, key=lambda s: s.w)]
                    best = max(s.w for s in fit)
                    cand = [s for s in fit if s.w == best]
                    s = cand[(xx * 31 + y * 17) % len(cand)]
                    hg = getattr(s, "hgrid", 1)
                    m.place(s, xx, y + hg - s.h, solid=0)
                    for dx in range(s.w):
                        for dy in range(hg):
                            done.add((xx + dx, y + dy))
                    xx += s.w
                x += run
            else:
                x += 1
    # ---- auto-dressing: solid props along walls (and a few in the open) that never cut a route
    added = dress(m, grid, skin, reserved, cm)
    # ---- trees
    if skin.trees:
        for y in range(H):
            for x in range(W):
                if grid[y][x] in ("tree", "tree2", "forest") and (x + y * 3) % 1 == 0:
                    s = skin.trees[(x * 7 + y * 13) % len(skin.trees)]
                    tc = (s.cols[0] if s.cols else s.w // 2)
                    m.place(s, x - tc, y + 1 - s.h, solid=0)
    # ---- water animation
    for k, name in skin.water_anim.items():
        for y in range(H):
            for x in range(W):
                if grid[y][x] == k:
                    m.anim(name, x, y, h=48, flat=True)
    # ---- decals on open floor
    rng = m.rng
    if skin.decals:
        for y in range(H):
            for x in range(W):
                if (x, y) in reserved:
                    continue
                k = grid[y][x]
                if k in skin.ground and not kit.Map._solid_kind(k) and k not in ("water", "deep", "void", "bridge", "stairs"):
                    if rng.random() < skin.decal_density:
                        m.place(rng.choice(skin.decals), x, y, solid=0)
    # ---- wall decor on faces
    n = 0
    for (x, y, ws) in faces:
        n += 1
        if skin.wall_decor and n % skin.decor_every == 0 and grid[y + 1][x] not in skin.props:
            d = skin.wall_decor[(x + y) % len(skin.wall_decor)]
            if isinstance(d, str):
                m.anim(d, x, y - 1, h=96)
            else:
                m.place(d, x, y + 1 - d.h, solid=0)
    return m, faces, skin


PASS_EXTRA = {"door", "doorway", "stairs", "bridge", "ladder", "dock", "carpet", "grate", "lift"}


sys.path.insert(0, os.path.dirname(HERE))
from compile_content import SOLID as _GAME_SOLID


def passable(k):
    return k not in _GAME_SOLID and k not in kit.SOLID_KINDS and k != "void"


_BLOCKED = set()


def _reach(grid, W, H, start):
    seen = {start}
    st = [start]
    while st:
        x, y = st.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in seen and (nx, ny) not in _BLOCKED and passable(grid[ny][nx]):
                seen.add((nx, ny))
                st.append((nx, ny))
    return seen


def dress(m, grid, skin, reserved, cm):
    if skin.dress_target <= 0 or not (skin.dress_wall or skin.dress_open):
        return 0
    W, H = m.w, m.h
    ents = cm["entities"]
    keep = set()
    starts = []
    for e in ents:
        if e["type"] == "spawn":
            starts.append((e["x"], e["y"]))
        if "x" in e:
            x, y = int(e["x"]), int(e["y"])
            keep.add((x, y))
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                keep.add((x + dx, y + dy))
            if e["type"] in ("npc", "shop", "inn"):
                for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
                    keep.add((x + dx, y + dy))
        if "x1" in e:
            for yy in range(e["y1"] - 1, e["y2"] + 2):
                for xx in range(e["x1"] - 1, e["x2"] + 2):
                    keep.add((xx, yy))
    if not starts:
        return 0
    # entities that block movement (solid NPCs, chests, save points, counters' shops ...) are obstacles here too
    _BLOCKED.clear()
    for e in ents:
        if "x" in e and (e["type"] in ("chest", "save", "switch", "shop", "inn", "heal") or (e["type"] == "npc" and e.get("solid", True)) or (e["type"] == "prop" and e.get("solid", True))):
            _BLOCKED.add((int(e["x"]), int(e["y"])))
    # per spawn: what each spawn reaches now must stay reachable from that same spawn (a union over spawns lets a
    # prop cut a map in two when each half has its own spawn)
    starts = [sp for sp in dict.fromkeys(starts) if 0 <= sp[0] < W and 0 <= sp[1] < H]
    must_by = {}
    for sp in starts:
        r = _reach(grid, W, H, sp)
        must_by[sp] = {c for c in keep if c in r}
    opens = [(x, y) for y in range(H) for x in range(W) if passable(grid[y][x]) and grid[y][x] not in PASS_EXTRA]
    target = int(len(opens) * skin.dress_target)
    walls = set(skin.walls)
    cand_wall = [c for c in opens if c[1] > 0 and grid[c[1] - 1][c[0]] in walls]
    cand_side = [c for c in opens if (c[0] > 0 and grid[c[1]][c[0] - 1] in walls) or (c[0] < W - 1 and grid[c[1]][c[0] + 1] in walls)]
    cand_open = [c for c in opens if c not in cand_wall and c not in cand_side]
    rng = m.rng
    rng.shuffle(cand_wall)
    rng.shuffle(cand_side)
    rng.shuffle(cand_open)
    order = [(c, skin.dress_wall) for c in cand_wall] + [(c, skin.dress_wall) for c in cand_side] + \
            [(c, skin.dress_open) for c in cand_open[:max(0, target // 3)]]
    n = 0
    for (x, y), pool in order:
        if n >= target or not pool:
            continue
        if (x, y) in keep or not passable(grid[y][x]):
            continue
        s = rng.choice(pool)
        grid[y][x] = skin.dress_kind
        ok = True
        for sp in starts:
            if not passable(grid[sp[1]][sp[0]]) or not must_by[sp] <= _reach(grid, W, H, sp):
                ok = False
                break
        if not ok:
            grid[y][x] = m.kind[y][x]
            continue
        m.kind[y][x] = skin.dress_kind
        hg = getattr(s, "hgrid", 1)
        m.place(s, x, y + 1 - s.h, solid=0)
        n += 1
    m.dressed = n
    return n


def render(m, faces, skin):
    img = m._ground()
    a = np.array(img)
    Wp, Hp = a.shape[1], a.shape[0]
    for (x, y, ws) in faces:
        al, sh, fx, fy, fw, fh = ws.face
        src = np.array(sheet_img(al, sh).crop((fx, fy, fx + fw, fy + fh)).convert("RGBA"))
        # face occupies this cell (and the one above for 2-cell faces), tiled across x
        hh = C * ws.face_h
        y0 = (y + 1) * C - hh
        ox = (x * C) % fw
        strip = np.concatenate([src, src], axis=1)[:, ox:ox + C]
        strip = strip[fh - hh:] if fh >= hh else strip
        for yy in range(hh):
            py = y0 + yy
            if 0 <= py < Hp:
                row = strip[min(yy, strip.shape[0] - 1)]
                al_ = row[:, 3:4].astype(np.float32) / 255.0
                a[py, x * C:(x + 1) * C, :3] = (a[py, x * C:(x + 1) * C, :3] * (1 - al_) + row[:, :3] * al_).astype(np.uint8)
        # dark rim where the cap meets the face
        ry = y0 - 2
        if ry >= 0:
            a[ry:ry + 2, x * C:(x + 1) * C, :3] = (a[ry:ry + 2, x * C:(x + 1) * C, :3] * 0.45).astype(np.uint8)
        # contact shadow on the floor below
        sy = (y + 1) * C
        if sy + 6 <= Hp:
            for i in range(6):
                a[sy + i, x * C:(x + 1) * C, :3] = (a[sy + i, x * C:(x + 1) * C, :3] * (0.62 + i * 0.06)).astype(np.uint8)
    return Image.fromarray(a)


def save(m, faces, skin):
    img = render(m, faces, skin)
    m.flat = []   # already baked
    base_save_ground = m._ground
    m._ground = lambda: img
    m.save()
    m._ground = base_save_ground


def raw_sections():
    """Original .map sections (not z48_*): id -> (header lines, entity lines)."""
    out = {}
    import re
    for p in sorted(glob.glob(os.path.join(REPO, "content_src", "maps", "*.map"))):
        if os.path.basename(p).startswith("z48_"):
            continue
        text = open(p, encoding="utf-8").read()
        for block in re.split(r"^=== ", text, flags=re.M)[1:]:
            lines = block.split("\n")
            mid = lines[0].strip()
            hdr, ents, mode, grid, legend = [], [], "hdr", [], {}
            for ln in lines[1:]:
                st_ = ln.strip()
                if mode == "hdr":
                    if st_ == "grid:":
                        mode = "grid"
                    elif st_.startswith("legend:"):
                        for pair in st_[7:].split():
                            k_, v_ = pair.split("=", 1)
                            legend[k_] = v_
                    elif st_ and not st_.startswith("#!"):
                        hdr.append(st_)
                elif mode == "grid":
                    if st_.startswith("entities:"):
                        mode = "ent"
                    elif ln.rstrip("\n") != "":
                        grid.append(ln.rstrip("\n"))
                else:
                    if st_:
                        ents.append(ln.rstrip())
            out[mid] = (hdr, ents, grid, legend)
    return out


def map_text(m, raw):
    hdr, ents = raw[0], raw[1]
    kinds = sorted({k for row in m.kind for k in row if k})
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    legend = {k: chars[i] for i, k in enumerate(kinds)}
    lines = ["=== " + m.id] + hdr
    lines.append("legend: " + " ".join("%s=%s" % (legend[k], k) for k in kinds))
    lines.append("grid:")
    for row in m.kind:
        lines.append("".join(legend[k] if k else "_" for k in row))
    lines.append("entities:")
    lines.extend(ents)
    return "\n".join(lines) + "\n"


def hand_made():
    ids = set()
    for p in glob.glob(os.path.join(REPO, "content_src", "maps", "z48_*.map")):
        if os.path.basename(p) == "z48_auto.map":
            continue
        for ln in open(p, encoding="utf-8"):
            if ln.startswith("=== "):
                ids.add(ln[4:].strip())
    return ids


def main():
    content = json.load(open(os.path.join(REPO, "game", "content", "content.json"), encoding="utf-8"))
    ids = [a for a in sys.argv[1:] if not a.startswith("--")] or sorted(set(content["maps"]) - hand_made())
    done, missing = 0, set()
    raw = raw_sections()
    auto_path = os.path.join(REPO, "content_src", "maps", "z48_auto.map")
    texts = {}
    if os.path.exists(auto_path):
        import re
        for block in re.split(r"^=== ", open(auto_path, encoding="utf-8").read(), flags=re.M)[1:]:
            texts[block.split("\n")[0].strip()] = "=== " + block
    for mid in ids:
        ts = content["maps"][mid]["tileset"]
        try:
            importlib.import_module("skins." + ts)
        except ModuleNotFoundError:
            missing.add(ts)
            continue
        m, faces, skin = build(mid, content, raw.get(mid))
        save(m, faces, skin)
        if getattr(m, "dressed", 0) > 0 and mid in raw:
            texts[mid] = map_text(m, raw[mid])
        elif mid in texts:
            del texts[mid]
        done += 1
        print("skinned", mid, "dressed", getattr(m, "dressed", 0))
    if "--preview" in sys.argv:
        print("done", done, "(preview only: z48_auto.map not written)", "missing skins:", sorted(missing))
        return
    with open(auto_path, "w", encoding="utf-8") as f:
        f.write("#! Generated by tools/maps48/autoskin.py: original layouts with auto-dressing (collision grid only).\n")
        for k in sorted(texts):
            f.write(texts[k] if texts[k].endswith("\n") else texts[k] + "\n")
    print("done", done, "missing skins:", sorted(missing))


if __name__ == "__main__":
    main()
