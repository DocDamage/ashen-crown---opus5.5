"""Offline reachability check over compiled maps (authoring aid for AC010/AC011).
Two passes per map: 'open' (all tileset_overs applied, conditional blocks removed) must reach every
exit, NPC, chest, switch and trigger from every spawn's component; reports unreachable entities.
Runtime collision is verified separately by the route bots in the real engine."""
import json, os, sys
from collections import deque

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = json.load(open(os.path.join(ROOT, "game", "content", "content.json"), encoding="utf-8"))
SOLID = set(C["tile_rules"]["solid"])


def grid_kinds(m):
    g = [[m["legend"].get(ch, "void") for ch in row] for row in m["grid"]]
    for e in m["entities"]:
        if e["type"] == "tileset_over":
            for y in range(e["y1"], e["y2"] + 1):
                for x in range(e["x1"], e["x2"] + 1):
                    g[y][x] = e["tile"]
    return g


def blocked(m, g, x, y):
    if not (0 <= x < m["w"] and 0 <= y < m["h"]):
        return True
    if g[y][x] in SOLID:
        return True
    for e in m["entities"]:
        if e["type"] in ("chest", "save", "switch", "shop", "inn", "heal", "prop") and e.get("x") == x and e.get("y") == y:
            if e["type"] == "prop" and not e.get("solid", True):
                continue
            return True
        if e["type"] == "npc" and e["x"] == x and e["y"] == y and e.get("solid", True):
            return True
    return False


def reach(m, g, sx, sy):
    seen = {(sx, sy)}
    q = deque([(sx, sy)])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in seen and not blocked(m, g, *n):
                seen.add(n)
                q.append(n)
    return seen


def main(only=None):
    problems = 0
    for mid, m in sorted(C["maps"].items()):
        if only and not mid.startswith(only):
            continue
        if m.get("kind") == "world":
            continue
        g = grid_kinds(m)
        spawns = [e for e in m["entities"] if e["type"] == "spawn"]
        if not spawns:
            print(f"{mid}: no spawns")
            problems += 1
            continue
        area = set()
        for s in spawns:
            area |= reach(m, g, s["x"], s["y"])
        for e in m["entities"]:
            t = e["type"]
            pts = []
            if t in ("door", "exit", "trigger"):
                pts = [(x, y) for x in range(e["x1"], e["x2"] + 1) for y in range(e["y1"], e["y2"] + 1)]
                ok = any(p in area for p in pts)
                if t == "trigger" and not e.get("touch", True):
                    ok = any((p[0] + dx, p[1] + dy) in area for p in pts for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            elif t in ("npc", "chest", "switch", "save", "shop", "inn", "heal", "sign", "read"):
                x, y = e["x"], e["y"]
                ok = any((x + dx, y + dy) in area for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if t in ("shop", "inn") and not ok:
                    ok = any((x + dx, y + dy) in area for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)))
                if t == "npc" and not ok:
                    ok = any((x + dx, y + dy) in area for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)))
            else:
                continue
            if not ok:
                problems += 1
                label = e.get("id") or e.get("dest") or e.get("scene") or e.get("text", "")[:30]
                print(f"{mid}: unreachable {t} {label} @ {e.get('x', e.get('x1'))},{e.get('y', e.get('y1'))}")
    # strict pass: every arrival spawn (named by some door/exit elsewhere) must reach every exit of its room
    arrivals = {}
    for mid, m in C["maps"].items():
        for e in m["entities"]:
            if e["type"] in ("door", "exit"):
                arrivals.setdefault(e["dest"], set()).add(e["spawn"])
    for mid, m in sorted(C["maps"].items()):
        if (only and not mid.startswith(only)) or m.get("kind") == "world":
            continue
        g = grid_kinds(m)
        exits = [e for e in m["entities"] if e["type"] in ("door", "exit")]
        for s in m["entities"]:
            if s["type"] != "spawn" or s["name"] not in arrivals.get(mid, ()):
                continue
            area = reach(m, g, s["x"], s["y"])
            for e in exits:
                pts = [(x, y) for x in range(e["x1"], e["x2"] + 1) for y in range(e["y1"], e["y2"] + 1)]
                if not any(p in area for p in pts):
                    problems += 1
                    print(f"{mid}: from spawn {s['name']} cannot reach exit to {e['dest']}")
    print("reachability problems:", problems)
    return problems


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1] if len(sys.argv) > 1 else None) else 0)
