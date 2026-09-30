"""Stricter reachability: solid NPCs, switches, chests, save points and counters block movement (as in the game);
every interactable must have a reachable neighbour cell and every exit/door/trigger a reachable cell, from the map's
spawns, with conditional tileset_over applied and not applied. Usage: python3 tools/check_entities_reach.py [MAP ...]"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import compile_content as CC

c = json.load(open(os.path.join(ROOT, "game", "content", "content.json")))
ids = sys.argv[1:] or sorted(c["maps"])
bad = 0
for mid in ids:
    m = c["maps"][mid]
    if m.get("kind") == "world":
        continue
    W, H, L = m["w"], m["h"], m["legend"]
    ents = m["entities"]
    blk = {(e["x"], e["y"]) for e in ents if "x" in e and (e["type"] in ("switch", "chest", "save", "shop", "inn", "heal", "node") or (e["type"] == "npc" and e.get("solid", True)))}
    for variant in (False, True):
        kinds = [[L[m["grid"][y][x]] for x in range(W)] for y in range(H)]
        if variant:
            for e in ents:
                if e["type"] == "tileset_over":
                    for y in range(e["y1"], e["y2"] + 1):
                        for x in range(e["x1"], e["x2"] + 1):
                            kinds[y][x] = e["tile"]
        ok = lambda x, y: 0 <= x < W and 0 <= y < H and kinds[y][x] not in CC.SOLID and kinds[y][x] != "void" and (x, y) not in blk
        starts = [(e["x"], e["y"]) for e in ents if e["type"] == "spawn"]
        seen = set(s for s in starts if ok(*s))
        st = list(seen)
        while st:
            x, y = st.pop()
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if (nx, ny) not in seen and ok(nx, ny):
                    seen.add((nx, ny)); st.append((nx, ny))
        for e in ents:
            if e["type"] in ("npc", "switch", "chest", "save", "shop", "inn", "heal", "sign", "read", "node", "fish"):
                x, y = e["x"], e["y"]
                if not any(n in seen for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1), (x, y))):
                    print("%s%s: %s %s at (%d,%d) unreachable" % (mid, " [overs]" if variant else "", e["type"], e.get("id", ""), x, y)); bad += 1
            elif e["type"] in ("exit", "door"):
                cells = [(x, y) for y in range(e["y1"], e["y2"] + 1) for x in range(e["x1"], e["x2"] + 1)]
                if not any(cc in seen for cc in cells):
                    print("%s%s: %s -> %s unreachable" % (mid, " [overs]" if variant else "", e["type"], e["dest"])); bad += 1
print("entity reach problems:", bad)
