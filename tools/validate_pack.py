"""Design-package validator (structural consistency only; NOT proof the game works).

Reconstructed for this workspace because the original tools/ folder was not supplied.
Checks catalog counts against docs/00_CANON_AND_SCOPE.md, unique IDs, references,
dungeon connectivity and chapter-prerequisite acyclicity.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPECTED = {"characters": 8, "regions": 6, "towns": 7, "dungeons": 12, "enemies": 40, "bosses": 16,
            "abilities": 80, "weapons": 48, "armor": 32, "accessories": 24, "consumables": 24,
            "statuses": 16, "quests": 12, "chapters": 24, "music": 30, "sfx": 32, "acceptance": 68}


def load(data_dir):
    return {k: json.load(open(os.path.join(data_dir, k + ".json"), encoding="utf-8")) for k in EXPECTED}


def validate(d):
    errors = []
    for k, n in EXPECTED.items():
        if len(d[k]) != n:
            errors.append(f"{k}: expected {n}, found {len(d[k])}")
        ids = [r["id"] for r in d[k]]
        if len(ids) != len(set(ids)):
            errors.append(f"{k}: duplicate ids")
    ids = {k: {r["id"] for r in d[k]} for k in EXPECTED}
    for c in d["characters"]:
        if c["quest"] not in ids["quests"]: errors.append(f"{c['id']} quest ref")
        if c["ultimate_weapon"] not in ids["weapons"]: errors.append(f"{c['id']} weapon ref")
    for w in d["weapons"]:
        if w["owner"] not in ids["characters"]: errors.append(f"{w['id']} owner")
    for a in d["abilities"]:
        own = a["owner"]
        if not (own in ids["characters"] or own in ids["accessories"] or (own.startswith("V") and len(own) == 3)):
            errors.append(f"{a['id']} owner {own}")
    for b in d["bosses"]:
        if b["location"] not in ids["dungeons"]: errors.append(f"{b['id']} location")
        if not b["phases"]: errors.append(f"{b['id']} phases")
    bosses_used = set()
    for dg in d["dungeons"]:
        rooms = {r["id"] for r in dg["rooms"]}
        if len(rooms) != 6: errors.append(f"{dg['id']} rooms != 6")
        adj = {r: set() for r in rooms}
        for a, b in dg["connections"]:
            if a not in rooms or b not in rooms: errors.append(f"{dg['id']} bad edge {a}-{b}")
            else: adj[a].add(b); adj[b].add(a)
        start = sorted(rooms)[0]; seen = {start}; st = [start]
        while st:
            for n in adj[st.pop()]:
                if n not in seen: seen.add(n); st.append(n)
        if seen != rooms: errors.append(f"{dg['id']} disconnected")
        if dg["boss"] not in ids["bosses"]: errors.append(f"{dg['id']} boss ref")
        if dg["secret_accessory"] not in ids["accessories"]: errors.append(f"{dg['id']} secret ref")
        bosses_used.add(dg["boss"])
    chmap = {c["id"]: c for c in d["chapters"]}
    state = {}
    def visit(c):
        if state.get(c) == 1: errors.append(f"cycle at {c}"); return
        if state.get(c) == 2: return
        state[c] = 1
        for p in chmap[c]["prerequisites"]:
            if p not in chmap: errors.append(f"{c} bad prereq {p}")
            else: visit(p)
        state[c] = 2
    for c in chmap: visit(c)
    for q in d["quests"]:
        if q["start"] not in ids["towns"] or q["location"] not in ids["dungeons"]: errors.append(f"{q['id']} refs")
    return errors


def main():
    d = load(os.path.join(ROOT, "data"))
    errs = validate(d)
    for e in errs: print("ERROR:", e)
    print("validate_pack:", "PASS (design data only)" if not errs else f"FAIL ({len(errs)})")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
