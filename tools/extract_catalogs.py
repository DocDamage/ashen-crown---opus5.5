"""Reconstruct the design-package JSON catalogs from the combined handoff docs.

The original ZIP (data/*.json) was not present in the workspace; only the combined
Markdown handoff was supplied. This script derives the catalogs deterministically
from the Markdown tables and sections so the IDs and seed values stay traceable to
the authored design. Run: python tools/extract_catalogs.py
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
DATA = os.path.join(ROOT, "data")


def read(name):
    with open(os.path.join(DOCS, name), encoding="utf-8") as f:
        return f.read()


def tables_after(text, heading):
    """Return rows (list of dicts) of the first table after a heading line."""
    idx = text.find(heading)
    if idx < 0:
        raise KeyError(heading)
    lines = text[idx:].splitlines()[1:]
    rows, header = [], None
    started = False
    for ln in lines:
        if ln.startswith("|"):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if header is None:
                header = cells
            elif set("".join(cells)) <= set("-: "):
                continue
            else:
                rows.append(dict(zip(header, cells)))
            started = True
        elif started:
            break
    return rows


def num(v):
    try:
        f = float(v)
        return int(f) if abs(f - round(f)) < 1e-9 else round(f, 2)
    except ValueError:
        return v


def sections(text, pattern):
    """Split text into (id, title, body) for headings matching pattern."""
    out = []
    ms = list(re.finditer(pattern, text, re.M))
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        nxt = re.search(r"^## ", text[m.end():end], re.M)
        body = text[m.end(): m.end() + nxt.start()] if nxt else text[m.end():end]
        out.append((m.group(1), m.group(2).strip(), body.strip()))
    return out


def field(body, label):
    m = re.search(r"\*\*" + re.escape(label) + r":\*\*\s*(.+?)(?=\s\*\*[A-Z][^*]*:\*\*|\n|$)", body)
    return m.group(1).strip().rstrip(".") if m else None


def main():
    os.makedirs(DATA, exist_ok=True)
    out = {}
    # Characters
    chars = []
    t = read("03_CHARACTER_BIBLE.md")
    for cid, name, body in sections(t, r"^## (C\d\d) — (.+)$"):
        ident = re.search(r"\*\*Identity:\*\* (\d+), (.+?)\. \*\*Role:\*\* (.+?)\. \*\*First joins:\*\* (CH\d\d); \*\*returns:\*\* (CH\d\d)", body)
        pr = re.search(r"\*\*Personal resolution:\*\* (Q\d\d); weapon (W\d\d\d)", body)
        paras = [p for p in body.split("\n\n") if p and not p.startswith("**")]
        chars.append({
            "id": cid, "name": name, "age": int(ident.group(1)), "identity": ident.group(2),
            "role": ident.group(3), "joins": ident.group(4), "returns": ident.group(5),
            "summary": paras[0] if paras else "",
            "act": field(body, "What they actually did"), "arc": field(body, "Arc"),
            "visual": field(body, "Visual direction"), "voice": field(body, "Voice direction"),
            "quest": pr.group(1), "ultimate_weapon": pr.group(2),
        })
    out["characters"] = chars
    # Abilities
    t = read("08_ABILITIES_AND_EQUIPMENT.md")
    abil = []
    for sec, owner in [("### Dain Ashward", "C01"), ("### Tessa Vale", "C02"), ("### Corren Hale", "C03"),
                       ("### Ivo Quill", "C04"), ("### Nera Fen", "C05"), ("### Sister Oriel", "C06"),
                       ("### Sable Renn", "C07"), ("### Pip Marr", "C08")]:
        for r in tables_after(t, sec):
            pk = r["Power / kind"].split(" / ")
            unlock = r["Unlock"]
            abil.append({"id": r["ID"], "name": r["Ability"], "owner": owner,
                         "unlock_level": int(unlock.split()[1]) if unlock.startswith("Level") else None,
                         "unlock_quest": unlock if unlock.startswith("Q") else None,
                         "mp": int(r["MP"]), "power": int(pk[0]), "kind": pk[1], "target": r["Target"],
                         "effect": r["Effect"]})
    for r in tables_after(t, "### Accessory spells and Vestiges"):
        cost = r["MP / Concord"]
        abil.append({"id": r["ID"], "name": r["Name"], "owner": r["Access"],
                     "mp": int(cost.split()[0]) if "MP" in cost else 0,
                     "concord": int(cost.split()[0]) if "Concord" in cost else 0,
                     "kind": "summon" if r["Access"].startswith("V") else "accessory_spell",
                     "effect": r["Effect"]})
    out["abilities"] = abil
    out["weapons"] = [{"id": r["ID"], "name": r["Name"], "owner": r["Owner"], "tier": int(r["Tier"]),
                        "atk": num(r["ATK"]), "mag": num(r["MAG"]), "price": num(r["Price"]),
                        "acquisition": r["Acquisition / effect"]} for r in tables_after(t, "## Weapons")]
    out["armor"] = [{"id": r["ID"], "name": r["Name"], "slot": r["Slot"],
                      "allowed": [a.strip() for a in r["Allowed"].split(",")],
                      "def": num(r["DEF"]), "res": num(r["RES"]), "price": num(r["Price"]), "effect": r["Effect"]}
                     for r in tables_after(t, "## Armor, head and offhand")]
    out["accessories"] = [{"id": r["ID"], "name": r["Name"], "price": num(r["Price"]), "effect": r["Effect"]}
                          for r in tables_after(t, "## Accessories")]
    out["consumables"] = [{"id": r["ID"], "name": r["Name"], "price": num(r["Price"]), "effect": r["Effect"]}
                          for r in tables_after(t, "## Consumables")]
    out["statuses"] = [{"id": r["Status"].lower(), "name": r["Status"], "type": r["Type"],
                        "duration_text": r["Duration"], "effect": r["Effect"]}
                       for r in tables_after(t, "## Statuses")]
    # Enemies / bosses
    t = read("10_ENEMIES_AND_BOSSES.md")
    out["enemies"] = [{"id": r["ID"], "name": r["Name"], "home": r["Home"], "level": int(r["Level"]),
                       "hp": int(round(float(r["HP"]))), "weakness": r["Weakness"], "behavior": r["Behavior"]}
                      for r in tables_after(t, "## Ordinary enemies")]
    bosses = []
    for bid, name, body in sections(t, r"^### (B\d\d) — (.+)$"):
        m = re.search(r"\*\*Location:\*\* (D\d\d); \*\*chapter:\*\* (CH\d\d); \*\*optional:\*\* (\w+); \*\*seed HP:\*\* (\d+)", body)
        phases = re.findall(r"(\d+): ([^;.]+)", field(body, "Phases") or "")
        bosses.append({"id": bid, "name": name, "location": m.group(1), "chapter": m.group(2),
                       "optional": m.group(3) == "True", "hp": int(m.group(4)), "tell": field(body, "Tell"),
                       "counterplay": field(body, "Counterplay"),
                       "phases": [{"threshold": int(a), "name": b.strip()} for a, b in phases],
                       "victory": field(body, "Victory")})
    out["bosses"] = bosses
    # Dungeons
    t = read("05_DUNGEON_BIBLE.md")
    dungeons = []
    for did, name, body in sections(t, r"^## (D\d\d) — (.+)$"):
        m = re.search(r"\*\*Region:\*\* (R\d\d); \*\*first chapter:\*\* (CH\d\d); \*\*target levels:\*\* (\d+)–(\d+); \*\*optional:\*\* (\w+)", body)
        rooms = []
        for r in tables_after(body, "| Room ID"):
            pass
        # table begins directly with header line; parse manually
        for ln in body.splitlines():
            mm = re.match(r"\| (D\d\d_R\d\d) \| (.+?) \| (.+?) \| (\d+)×(\d+) \|", ln)
            if mm:
                rooms.append({"id": mm.group(1), "name": mm.group(2), "purpose": mm.group(3),
                              "w": int(mm.group(4)), "h": int(mm.group(5))})
        conns = re.findall(r"(D\d\d_R\d\d) ↔ (D\d\d_R\d\d)", body)
        dungeons.append({"id": did, "name": name, "region": m.group(1), "chapter": m.group(2),
                         "levels": [int(m.group(3)), int(m.group(4))], "optional": m.group(5) == "True",
                         "mechanic": field(body, "Spatial mechanic"), "rooms": rooms,
                         "connections": [list(c) for c in conns],
                         "boss": re.search(r"\*\*Primary boss:\*\* (B\d\d)", body).group(1),
                         "state_change": field(body, "State change"),
                         "secret_accessory": re.search(r"free accessory (A\d\d\d)", body).group(1)})
    out["dungeons"] = dungeons
    # World
    t = read("04_WORLD_BIBLE.md")
    regions = []
    for rid, name, body in sections(t, r"^## (R\d\d) — (.+)$"):
        regions.append({"id": rid, "name": name, "geography": field(body, "Geography"), "palette": field(body, "Palette")})
    out["regions"] = regions
    towns = []
    for tid, name, body in sections(t, r"^### (T\d\d) — (.+)$"):
        towns.append({"id": tid, "name": name, "region": field(body, "Region"), "function": field(body, "Function"),
                      "scene_maps": [s.strip() for s in (field(body, "Scene maps") or "").split(";")],
                      "before": field(body, "Before"), "after": field(body, "After"),
                      "human_detail": field(body, "Human detail"), "recurring": field(body, "Recurring person"),
                      "conversation": field(body, "Conversation")})
    out["towns"] = towns
    # Chapters
    t = read("02_STORY_BIBLE.md")
    chapters = []
    for cid, name, body in sections(t, r"^## (CH\d\d) — (.+)$"):
        m = re.search(r"\*\*Act (\d); prerequisites:\*\* (.+?)\. \*\*Status:\*\* (.+?)\.", body)
        pre = re.findall(r"CH\d\d", m.group(2))
        chapters.append({"id": cid, "name": name, "act": int(m.group(1)), "prerequisites": pre,
                         "status": m.group(3), "summary": body.split("\n\n")[1] if "\n\n" in body else "",
                         "turn": (re.search(r"\*\*Dramatic turn\.\*\* (.+)", body) or [None, None])[1],
                         "result": (re.search(r"\*\*Persistent result\.\*\* (.+)", body) or [None, None])[1]})
    out["chapters"] = chapters
    # Quests
    t = read("09_QUESTS_AND_EPILOGUES.md")
    quests = []
    for qid, name, body in sections(t, r"^## (Q\d\d) — (.+)$"):
        m = re.search(r"\*\*Start:\*\* (T\d\d)\. \*\*Location:\*\* (D\d\d)\. \*\*Character:\*\* (.+?)\.", body)
        quests.append({"id": qid, "name": name, "start": m.group(1), "location": m.group(2),
                       "character": m.group(3), "hook": field(body, "Hook"), "objectives": field(body, "Playable objectives"),
                       "decision": field(body, "Decision scene"), "result": field(body, "World and ending result"),
                       "reward": field(body, "Reward"), "boss": (re.search(r"\*\*Boss:\*\* (B\d\d)", body) or [None, None])[1]})
    out["quests"] = quests
    # Audio
    t = read("12_AUDIO_DIRECTION.md")
    out["music"] = [{"id": r["ID"], "name": r["Cue"], "use": r["Use"], "direction": r["Direction"]}
                    for r in tables_after(t, "## Track catalog")]
    out["sfx"] = [{"id": r["ID"], "name": r["Cue"], "slot": r["Runtime slot"]} for r in tables_after(t, "## SFX slots")]
    t = read("15_ACCEPTANCE_AND_RELEASE.md")
    out["acceptance"] = [{"id": r["ID"], "area": r["Area"], "test": r["Test"], "exercise": r["Exercise"],
                          "required": r["Required outcome"]} for r in tables_after(t, "## Acceptance matrix")]
    for k, v in out.items():
        with open(os.path.join(DATA, k + ".json"), "w", encoding="utf-8") as f:
            json.dump(v, f, indent=1, ensure_ascii=False)
        print(f"{k}: {len(v)}")


if __name__ == "__main__":
    main()
