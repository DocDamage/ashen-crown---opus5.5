"""Overworld audit: which locations are reachable on foot from a start spawn (blocks treated as open or closed),
and whether every airship landing zone has a walkable tile within 3 steps (the runtime landing rule)."""
import json, os, sys
from collections import deque
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = json.load(open(os.path.join(ROOT, "game", "content", "content.json"), encoding="utf-8"))
SOLID = set(C["tile_rules"]["solid"])

def audit(mid, start, blocks_closed):
    m = C["maps"][mid]
    g = [[m["legend"].get(ch, "void") for ch in row] for row in m["grid"]]
    closed = set()
    if blocks_closed:
        for e in m["entities"]:
            if e["type"] == "block":
                for y in range(e["y1"], e["y2"] + 1):
                    for x in range(e["x1"], e["x2"] + 1):
                        closed.add((x, y))
    locs = {(e["x"], e["y"]): e["id"] for e in m["entities"] if e["type"] == "location"}
    sp = [e for e in m["entities"] if e["type"] == "spawn" and e["name"] == start][0]
    seen = {(sp["x"], sp["y"])}; q = deque(seen)
    while q:
        x, y = q.popleft()
        if (x, y) in locs and (x, y) != (sp["x"], sp["y"]):
            continue   # entering a location leaves the map
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < m["w"] and 0 <= n[1] < m["h"] and n not in seen and g[n[1]][n[0]] not in SOLID and n not in closed:
                seen.add(n); q.append(n)
    reach = sorted(v for k, v in locs.items() if k in seen)
    print(f"{mid} from {start} ({'blocks closed' if blocks_closed else 'blocks open'}): {reach}")
    bad = []
    for e in m["entities"]:
        if e["type"] == "landing":
            ok = any(g[y][x] not in SOLID and (x, y) not in locs
                     for y in range(max(0, e["y1"] - 3), min(m["h"], e["y2"] + 4))
                     for x in range(max(0, e["x1"] - 3), min(m["w"], e["x2"] + 4)))
            if not ok:
                bad.append(e["name"])
    if any(e["type"] == "landing" for e in m["entities"]):
        print("  landing zones without walkable ground:", bad or "none")

audit("WORLD", "default", True)
audit("WORLD_POST", "l_t07", True)
audit("WORLD_POST", "l_t07", False)


def post_access():
    """Every post-state location must be reachable on foot from Hearthward or from some landing field."""
    m = C["maps"]["WORLD_POST"]
    g = [[m["legend"].get(ch, "void") for ch in row] for row in m["grid"]]
    locs = {(e["x"], e["y"]): e["id"] for e in m["entities"] if e["type"] == "location"}
    def flood(starts):
        seen = set(starts); q = deque(starts)
        while q:
            x, y = q.popleft()
            if (x, y) in locs:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if 0 <= n[0] < m["w"] and 0 <= n[1] < m["h"] and n not in seen and g[n[1]][n[0]] not in SOLID:
                    seen.add(n); q.append(n)
        return {locs[p] for p in seen if p in locs}
    got = set()
    for e in m["entities"]:
        if e["type"] == "landing" or (e["type"] == "spawn" and e["name"] == "l_t07"):
            xs = range(e.get("x1", e.get("x")) - 3, e.get("x2", e.get("x")) + 4)
            ys = range(e.get("y1", e.get("y")) - 3, e.get("y2", e.get("y")) + 4)
            starts = [(x, y) for x in xs for y in ys if 0 <= x < m["w"] and 0 <= y < m["h"] and g[y][x] not in SOLID and (x, y) not in locs]
            got |= flood(starts)
    missing = sorted(set(locs.values()) - got)
    print("post locations unreachable from any landing/Hearthward:", missing or "none")
    return missing

post_access()
