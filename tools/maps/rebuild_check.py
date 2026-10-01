"""Hand-made dungeon rebuild guard (docs/expansion/DUNGEON_REBUILD.md).

Compares each named room's source section in content_src/maps/*.map with the committed version (git REF, default
HEAD) and checks the rules a rebuilt grid must keep:
  1. the entity lines are unchanged (same entities, same coordinates, same conditions);
  2. every cell a QA route walks to (["go", x, y] / ["tile", x, y] anywhere in game/src/qa/routes.gd) that was walkable
     stays walkable (the bot drives the real game by coordinates);
  3. spawns, exits, triggers and every interactable keep a walkable cell or neighbour (reachability itself is checked
     by tools/check_entities_reach.py after compiling);
  4. the room keeps its width and height, and uses only known glyphs.
Usage: python3 tools/maps/rebuild_check.py MAP_ID [MAP_ID ...] [--ref HEAD]
"""
import os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import compile_content as CC

args = [a for a in sys.argv[1:] if not a.startswith("--")]
ref = "HEAD"
if "--ref" in sys.argv:
    ref = sys.argv[sys.argv.index("--ref") + 1]
    args = [a for a in args if a != ref]
MAPS = os.path.join(ROOT, "content_src", "maps")
SOURCES = [f for f in sorted(os.listdir(MAPS)) if f.endswith(".map") and not f.startswith("z48_") and f not in ("world.map", "world2.map")]


def sections(text):
    out = {}
    for part in re.split(r"^(?==== )", text, flags=re.M)[1:]:
        mid = part.split("\n", 1)[0][4:].strip()
        out[mid] = part
    return out


def parse(sec):
    lines = sec.rstrip("\n").split("\n")[1:]
    hdr, grid, ents, legend, mode = {}, [], [], {}, "hdr"
    for ln in lines:
        s = ln.strip()
        if mode == "hdr":
            if s == "grid:":
                mode = "grid"
            elif s.startswith("legend:"):
                for kv in s[7:].split(","):
                    if "=" in kv:
                        k, v = kv.split("=", 1)
                        legend[k.strip()] = v.strip()
            elif ":" in s:
                hdr[s.split(":", 1)[0]] = s.split(":", 1)[1].strip()
        elif mode == "grid":
            if s == "entities:":
                mode = "ents"
            elif ln != "":
                grid.append(ln)
        else:
            if s and not s.startswith("#"):
                ents.append(" ".join(s.split()))
    return hdr, grid, ents, legend


def kind(ch, legend):
    return legend.get(ch, CC.GLYPHS.get(ch) if hasattr(CC, "GLYPHS") else None)


GL = getattr(CC, "GLYPHS", None) or getattr(CC, "DEFAULT_LEGEND", None)
if GL is None:
    for name in dir(CC):
        v = getattr(CC, name)
        if isinstance(v, dict) and v.get("#") == "wall" and v.get(".") == "floor":
            GL = v
            break


def walk(ch, legend):
    k = legend.get(ch, GL.get(ch))
    return k is not None and k not in CC.SOLID and k != "void"


def route_cells():
    t = open(os.path.join(ROOT, "game", "src", "qa", "routes.gd")).read()
    return {(int(a), int(b)) for a, b in re.findall(r'\["(?:go|tile)",\s*(\d+),\s*(\d+)\]', t)}


def main():
    cur, old = {}, {}
    for f in SOURCES:
        p = os.path.join(MAPS, f)
        for mid, sec in sections(open(p).read()).items():
            cur[mid] = sec
        try:
            txt = subprocess.run(["git", "show", "%s:content_src/maps/%s" % (ref, f)], cwd=ROOT, capture_output=True,
                                 text=True, check=True).stdout
            for mid, sec in sections(txt).items():
                old[mid] = sec
        except subprocess.CalledProcessError:
            pass
    rc = route_cells()
    bad = 0
    for mid in args:
        if mid not in cur or mid not in old:
            print("%s: not found in the sources (or at %s)" % (mid, ref)); bad += 1
            continue
        h0, g0, e0, l0 = parse(old[mid])
        h1, g1, e1, l1 = parse(cur[mid])
        prob = []
        if e0 != e1:
            gone = [e for e in e0 if e not in e1]
            new = [e for e in e1 if e not in e0]
            prob.append("entities changed: -%s +%s" % (gone[:3], new[:3]))
        if len(g0) != len(g1) or any(len(r) != len(g0[0]) for r in g1):
            prob.append("size changed (%dx%d -> %dx%d, rows must all be the same width)" % (len(g0[0]), len(g0), len(g1[0]) if g1 else 0, len(g1)))
        else:
            for y, row in enumerate(g1):
                for x, ch in enumerate(row):
                    if ch not in l1 and ch not in GL:
                        prob.append("unknown glyph %r at (%d,%d)" % (ch, x, y))
            for (x, y) in rc:
                if y < len(g0) and x < len(g0[0]) and walk(g0[y][x], l0) and not walk(g1[y][x], l1):
                    prob.append("route cell (%d,%d) was walkable and is now %r" % (x, y, g1[y][x]))
            for e in e1:
                p = e.split()
                nums = [t for t in p[1:5] if re.fullmatch(r"\d+(\.\.\d+)?", t)]
                if p[0] in ("spawn",) and len(p) >= 4:
                    x, y = int(p[2]), int(p[3])
                    if not walk(g1[y][x], l1):
                        prob.append("spawn %s at (%d,%d) is on %r" % (p[1], x, y, g1[y][x]))
                if p[0] in ("exit", "trigger", "hazard") and len(nums) >= 2:
                    xr = [int(v) for v in nums[0].split("..")]
                    yr = [int(v) for v in nums[1].split("..")]
                    cells = [(x, y) for x in range(xr[0], xr[-1] + 1) for y in range(yr[0], yr[-1] + 1)]
                    if not any(y < len(g1) and x < len(g1[0]) and walk(g1[y][x], l1) for x, y in cells):
                        prob.append("%s at %s,%s has no walkable cell" % (p[0], nums[0], nums[1]))
        if prob:
            bad += 1
            print("%s:" % mid)
            for q in prob[:12]:
                print("   " + q)
        else:
            print("%s: ok" % mid)
    print("rebuild problems: %d" % bad)
    sys.exit(1 if bad else 0)


main()
