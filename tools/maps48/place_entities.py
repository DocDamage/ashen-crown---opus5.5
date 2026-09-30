"""Places overhaul entities (new recruits, Vestiges, the Namer) into map sources.

Each spec names a map, an entity template with {x} {y}, and a preferred cell. The tool finds the nearest free floor
cell whose occupation keeps every walkable cell connected (and keeps clear of exits, doors, spawns and other
entities), then writes the line - tagged `#! ov:<key>` so re-runs replace it - into every map file that defines that
map (the original source and the z48 skin that wins at compile time). Run from the repo root; then compile and
run tools/check_reach.py.
"""
import glob, os, re, sys
from collections import deque

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import compile_content as CC  # noqa: E402

SPECS = [
    # key, map, template, preferred (x, y) or None (centre)
    ("namer_t01", "T01_PLATFORM", 'npc ov_namer {x} {y} down sprite=scholar talk=OV_NAMER name="Name-Keeper"', None),
    ("namer_t07", "T07_HEARTH", 'npc ov_namer {x} {y} down sprite=scholar talk=OV_NAMER name="Name-Keeper"', None),
    ("lich", "D11_R05", "npc ov_lich {x} {y} down sprite=C13 talk=OV_LICH if=q:Q09,!recruited:C13", None),
    ("maldrath", "T01_POST", "npc ov_maldrath {x} {y} down sprite=C14 talk=OV_MALDRATH if=ch:CH20,!recruited:C14", None),
    ("velkhar", "D07P_R03", "npc ov_velkhar {x} {y} down sprite=C15 talk=OV_VELKHAR if=ch:CH19,!recruited:C15", None),
    ("kael", "D08P_R01", "npc ov_kael {x} {y} down sprite=C16 talk=OV_KAEL if=ch:CH16,!recruited:C16", None),
    ("rider", "D04P_R01", "npc ov_rider {x} {y} left sprite=C17 talk=OV_RIDER if=ch:CH16,!recruited:C17", None),
    ("v09", "D03P_R03", "npc ov_v09 {x} {y} down sprite=vestige:V09 talk=OV_V09 if=ch:CH14,!flag:ov_v09", None),
    ("v10", "D03P_R02", "npc ov_v10 {x} {y} down sprite=vestige:V10 talk=OV_V10 if=ch:CH14,!flag:ov_v10", None),
    ("v11", "D10_ALCOVE", "npc ov_v11 {x} {y} down sprite=vestige:V11 talk=OV_V11 if=!flag:ov_v11", None),
    ("v12", "D11_R04", "npc ov_v12 {x} {y} down sprite=vestige:V12 talk=OV_V12 if=!flag:ov_v12", None),
]

AVOID = {"bridge", "stairs", "shallow", "door", "doorway", "ice"}
BLOCKING = {"npc", "chest", "save", "switch", "shop", "inn", "heal", "prop", "sign", "read"}


def compiled_maps():
    CC.ERRORS.clear() if hasattr(CC, "ERRORS") else None
    return CC.parse_maps()


def walkable(m):
    W, H = m["w"], m["h"]
    kinds = [[m["legend"].get(m["grid"][y][x], "void") for x in range(W)] for y in range(H)]
    ok = [[kinds[y][x] not in CC.SOLID and kinds[y][x] != "void" for x in range(W)] for y in range(H)]
    m["_kinds"] = kinds
    for e in m["entities"]:
        if e["type"] in BLOCKING and "x" in e and not str(e.get("id", "")).startswith("ov_"):
            if 0 <= e["y"] < H and 0 <= e["x"] < W:
                ok[e["y"]][e["x"]] = False
        if e["type"] == "block" and not e["cond"]:
            for y in range(e["y1"], e["y2"] + 1):
                for x in range(e["x1"], e["x2"] + 1):
                    ok[y][x] = False
    return ok


def reserved(m):
    r = set()
    for e in m["entities"]:
        if str(e.get("id", "")).startswith("ov_"):
            continue
        if "x1" in e and e["type"] in ("exit", "door", "trigger", "landing"):
            for y in range(e["y1"] - 2, e["y2"] + 3):
                for x in range(e["x1"] - 2, e["x2"] + 3):
                    r.add((x, y))
        elif "x" in e:
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    r.add((e["x"] + dx, e["y"] + dy))
    return r


def components(ok, skip=None):
    H, W = len(ok), len(ok[0])
    seen, n = set(), 0
    for y in range(H):
        for x in range(W):
            if ok[y][x] and (x, y) != skip and (x, y) not in seen:
                n += 1
                q = deque([(x, y)])
                seen.add((x, y))
                while q:
                    cx, cy = q.popleft()
                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if 0 <= nx < W and 0 <= ny < H and ok[ny][nx] and (nx, ny) != skip and (nx, ny) not in seen:
                            seen.add((nx, ny))
                            q.append((nx, ny))
    return n


def choose(m, pref):
    ok = walkable(m)
    res = reserved(m)
    H, W = m["h"], m["w"]
    px, py = pref if pref else (W // 2, H // 2)
    base = components(ok)
    cands = sorted(((abs(x - px) + abs(y - py), x, y) for y in range(1, H - 1) for x in range(1, W - 1)
                    if ok[y][x] and (x, y) not in res))
    for _, x, y in cands:
        # talk cell below must be walkable (the player faces up to talk), and a wall/solid above looks deliberate
        if not ok[y + 1][x] or m["_kinds"][y][x] in AVOID or m["_kinds"][y + 1][x] in AVOID:
            continue
        if components(ok, skip=(x, y)) != base:
            continue
        return x, y
    raise SystemExit("no cell for %s" % m["id"])


def write(map_id, key, line):
    tag = "#! ov:%s" % key
    files = sorted(glob.glob(os.path.join(ROOT, "content_src", "maps", "*.map")))
    n = 0
    for fp in files:
        s = open(fp, encoding="utf-8").read()
        if not re.search(r"(?m)^=== %s\s*$" % re.escape(map_id), s):
            continue
        s = "\n".join(l for l in s.split("\n") if not l.endswith(tag))
        parts = re.split(r"(?m)^(?==== )", s)
        for i, b in enumerate(parts):
            if b.split("\n", 1)[0].strip() == "=== " + map_id:
                trail = len(b) - len(b.rstrip("\n"))
                parts[i] = b.rstrip("\n") + "\n" + line + " " + tag + "\n" * max(1, trail)
        open(fp, "w", encoding="utf-8").write("".join(parts))
        n += 1
    return n


def main():
    maps = compiled_maps()
    for key, mid, tpl, pref in SPECS:
        m = maps[mid]
        x, y = choose(m, pref)
        n = write(mid, key, tpl.format(x=x, y=y))
        print("%-10s %-14s (%d,%d)  %d file(s)" % (key, mid, x, y, n))


if __name__ == "__main__":
    main()
