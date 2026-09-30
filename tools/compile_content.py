"""Build-time content compiler: design catalogs (data/*.json) + authored runtime tables
(tools/content/*.py, content_src/maps/*.map, content_src/scenes/*.scn) -> game/content/content.json

Fails loudly on unknown operations, unresolved references, bad map geometry or scene commands.
Usage: python tools/compile_content.py [--check]
"""
import glob, hashlib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from content import abilities as AB, enemies as EN, tables as TB  # noqa: E402
from content import formations as FM  # noqa: E402
from content import gear as GR  # noqa: E402
from content import cast as CAST  # noqa: E402
from content import vestiges as VES  # noqa: E402
from content import bestiary2 as BX  # noqa: E402
from content import bosses2 as BS  # noqa: E402
from content import places as PL  # noqa: E402

SUPPORTED_OPS = {"self_hp", "damage", "heal", "mp", "full_restore", "revive", "status", "cleanse", "dispel_positive", "atb", "oath",
                 "arm_overcast", "heat_exchange", "leap", "ground", "mine", "decoy", "steal", "protect", "lethal_guard",
                 "bramble", "flee", "evasion", "infuse", "resist", "reveal", "omen", "mirror", "feather", "quick_hands",
                 "witness", "status_ward", "row_back", "remove_hard", "cancel_charge", "concord", "steal_gold",
                 "buff_ally", "guard_self", "mp_drain", "once_per_battle", "wingbeat", "msg"}
TARGET_RULES = {"random", "all", "self", "ally_lowest", "ally_random", "row_front", "row_back", "front_lowest",
                "highest_mp", "marked", "lowest_hp", "protector", "allies"}
SCENE_CMDS = {"say", "choice", "label", "goto", "if", "set", "unset", "give", "take", "gold", "key", "unkey", "join",
              "leave", "avail", "chapter", "objective", "battle", "move", "face", "show", "hide", "fade", "wait",
              "music", "sfx", "shake", "flash", "warp", "doc", "heal", "phase", "vestige", "quest", "emote", "credits",
              "title", "rumor", "discover", "shop", "inn", "formation", "save_prompt", "event", "xp", "level_floor",
              "vehicle", "tint", "end", "split_party", "setvar", "addvar", "equip", "portrait", "lights", "salvage",
              "call", "clear_save", "epilogue", "ship_travel", "sprite", "row", "note", "lock_party", "unlock_party",
              "ending", "journal", "backup", "airship", "team", "name", "rename"}

errors = []
pending = []


def err(msg):
    errors.append(msg)


def load(name):
    with open(os.path.join(ROOT, "data", name + ".json"), encoding="utf-8") as f:
        return json.load(f)


def check_ops(owner, ops):
    for op in ops:
        if op.get("op") not in SUPPORTED_OPS:
            err(f"{owner}: unsupported op {op.get('op')!r}")
        if op.get("op") == "status" and op["id"] not in TB.STATUS_DURATION:
            err(f"{owner}: unknown status {op['id']}")


def plain(s):
    return (s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
             .replace("—", "-").replace("–", "-").replace("…", "...").replace("×", "x"))


def build_characters(cat):
    out = {}
    abil = load("abilities")
    for c in cat:
        cid = c["id"]
        b = TB.CHAR_BASE[cid]
        learn = [{"id": a["id"], "level": a["unlock_level"]} for a in abil if a["owner"] == cid and a["unlock_level"]]
        ult = [a["id"] for a in abil if a["owner"] == cid and a.get("unlock_quest")]
        out[cid] = {"id": cid, "name": c["name"], "short": c["name"].split()[0] if cid != "C06" else "Oriel",
                    "role": c["role"], "age": c["age"], "identity": c["identity"],
                    "base": {"hp": b["hp"], "mp": b["mp"], "str": b["str"], "mag": b["mag"], "def": b["df"], "res": b["res"], "spd": b["spd"]},
                    "growth": {"hp": TB.HP_G[cid], "mp": TB.MP_G[cid], "str": TB.SM_G[cid][0], "mag": TB.SM_G[cid][1]},
                    "learn": learn, "ultimate": ult[0] if ult else None, "quest": c["quest"], "ultimate_weapon": c["ultimate_weapon"],
                    "starter": TB.STARTER[cid], "role_command": {"C01": "Oath", "C02": "Magic", "C03": "Aerial", "C04": "Tools",
                    "C05": "Hunt", "C06": "Prayer", "C07": "Runes", "C08": "Tricks"}[cid],
                    "summary": plain(c["summary"]), "arc": plain(c["arc"] or "")}
    return out


def build_abilities(cat):
    out = {}
    for a in cat:
        aid = a["id"]
        if aid not in AB.ABILITY_OPS:
            err(f"ability {aid} has no runtime ops")
            continue
        spec = AB.ABILITY_OPS[aid]
        check_ops(aid, spec["ops"])
        r = {"id": aid, "name": plain(a["name"]), "owner": a["owner"], "mp": a.get("mp", 0), "power": a.get("power", 0),
             "kind": a["kind"], "target": a.get("target", AB.SUMMON_TARGET if a["kind"] == "summon" else "enemy_one"),
             "desc": plain(a["effect"]), "ops": spec["ops"], "family": spec.get("family", "skill"),
             "anim": spec.get("anim", "cast"), "element": spec.get("element", "none"),
             "elemental_spell": spec.get("elemental_spell", False), "revive": spec.get("revive", False),
             "field": spec.get("field", False), "concord": spec.get("concord", True)}
        if a["kind"] == "accessory_spell":
            r["target"] = "ally_one" if aid == "S069" else "enemy_one"
        if a["kind"] == "summon":
            r["target"] = "enemy_all"
        if a.get("unlock_level"):
            r["unlock_level"] = a["unlock_level"]
        if a.get("unlock_quest"):
            r["unlock_quest"] = a["unlock_quest"]
        out[aid] = r
    return out


def build_items(cat_w, cat_a, cat_acc, cat_c):
    items = {}
    for w in cat_w:
        it = {"id": w["id"], "name": plain(w["name"]), "kind": "weapon", "owner": w["owner"], "tier": w["tier"],
              "atk": w["atk"], "mag": w["mag"], "price": w["price"], "desc": plain(w["acquisition"]),
              "two_handed": w["owner"] in TB.TWO_HANDED_OWNERS, "ranged": w["owner"] in TB.RANGED_OWNERS,
              "allowed": [w["owner"]], "sellable": w["tier"] < 6}
        if w["id"] in TB.ULTIMATE_PASSIVES:
            it["passives"] = TB.ULTIMATE_PASSIVES[w["id"]]
            it["unique"] = True
        items[w["id"]] = it
    heads = [a["id"] for a in cat_a if a["slot"] == "head"]
    for a in cat_a:
        d, r = int(round(float(a["def"]))), int(round(float(a["res"])))
        if a["slot"] == "head":
            if heads.index(a["id"]) % 2 == 0:
                d += 2
            else:
                r += 2
        items[a["id"]] = {"id": a["id"], "name": plain(a["name"]), "kind": "armor", "slot": a["slot"], "allowed": a["allowed"],
                          "def": d, "res": r, "price": a["price"], "tier": TB.ARMOR_TIER[a["id"]], "desc": plain(a["effect"]), "sellable": True}
    for a in cat_acc:
        spec = TB.ACCESSORY[a["id"]]
        it = {"id": a["id"], "name": plain(a["name"]), "kind": "accessory", "slot": "accessory", "price": a["price"],
              "desc": plain(a["effect"]), "allowed": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08"], "sellable": a["price"] > 0}
        it.update(spec)
        if a["price"] == 0:
            it["unique"] = True
        items[a["id"]] = it
    for c in cat_c:
        spec = TB.CONSUMABLE[c["id"]]
        check_ops(c["id"], spec["ops"])
        it = {"id": c["id"], "name": plain(c["name"]), "kind": "consumable", "price": c["price"], "desc": plain(c["effect"]),
              "target": spec["target"], "ops": spec["ops"], "battle": spec.get("battle", True), "field": spec.get("field", False),
              "revive": spec.get("revive", False), "special": spec.get("special", ""), "sellable": c["id"] != "I024"}
        items[c["id"]] = it
    for kid, name in TB.KEY_ITEMS.items():
        items[kid] = {"id": kid, "name": name, "kind": "key", "price": 0, "desc": "A key item.", "sellable": False}
    return items


def enemy_stats(level, mods, boss=False):
    m = lambda k: mods.get(k, 1.0)
    bm = 1.15 if boss else 1.0
    return {"atk": round((5 + 2.5 * level) * m("atk") * bm, 1), "mag": round((5 + 2.5 * level) * m("mag") * bm, 1),
            "def": round((3 + 1.6 * level) * m("def") * (1.2 if boss else 1.0), 1),
            "res": round((3 + 1.6 * level) * m("res") * (1.2 if boss else 1.0), 1),
            "spd": int(min(60, (8 + level * 0.5) * m("spd")))}


DROP_TABLE = [(0, "I001", "I004"), (8, "I001", "I004"), (14, "I002", "I004"), (20, "I002", "I005"), (30, "I003", "I005")]


def tier_drops(level):
    row = [r for r in DROP_TABLE if level >= r[0]][-1]
    return row[1], row[2]


def build_enemies(cat_e, cat_b):
    out = {}
    for e in cat_e:
        spec = EN.E.get(e["id"])
        if spec is None:
            err(f"enemy {e['id']} has no behaviour")
            continue
        lv = e["level"]
        common, rare = tier_drops(lv)
        aff = {e["weakness"]: "weak"}
        aff.update(spec["aff"])
        r = {"id": e["id"], "name": plain(e["name"]), "level": lv, "hp": int(round(e["hp"] * spec["mods"].get("hp", 1.0))),
             **enemy_stats(lv, spec["mods"]), "affinities": aff, "tags": spec["tags"], "moves": spec["moves"], "cycle": spec["cycle"],
             "xp": 8 + 5 * lv, "gold": 10 + 6 * lv, "drops": [{"item": common, "chance": 20}, {"item": "I009" if lv < 10 else "I007", "chance": 8}],
             "steal": {"common": common, "rare": rare}, "shape": spec["shape"], "variant": spec.get("sprite_variant", ""),
             "home": e["home"], "behavior": plain(e["behavior"]), "sprite": e["id"]}
        for k in ("split", "melee_dodge", "copy_element", "acc_penalty"):
            if k in spec:
                r[k] = spec[k]
        for mid, mv in spec["moves"].items():
            check_ops(f"{e['id']}.{mid}", mv["ops"])
            if mv["target"] not in TARGET_RULES:
                err(f"{e['id']}.{mid} bad target {mv['target']}")
        for mid in spec["cycle"]:
            if mid not in spec["moves"]:
                err(f"{e['id']} cycle references {mid}")
        out[e["id"]] = r
    for b in cat_b:
        spec = EN.B.get(b["id"])
        if spec is None:
            err(f"boss {b['id']} has no behaviour")
            continue
        lv = TB.BOSS_LEVEL[b["id"]]
        if len(spec["phases"]) != len(b["phases"]):
            err(f"{b['id']} phase count mismatch catalog={len(b['phases'])} runtime={len(spec['phases'])}")
        for i, ph in enumerate(spec["phases"]):
            if i < len(b["phases"]) and ph["at"] != b["phases"][i]["threshold"]:
                err(f"{b['id']} phase {i} threshold mismatch")
            for mid in ph["cycle"]:
                if mid not in spec["moves"]:
                    err(f"{b['id']} phase cycle references {mid}")
        for mid, mv in spec["moves"].items():
            check_ops(f"{b['id']}.{mid}", mv["ops"])
            if mv["target"] not in TARGET_RULES:
                err(f"{b['id']}.{mid} bad target {mv['target']}")
        r = {"id": b["id"], "name": plain(b["name"]), "level": lv, "hp": b["hp"], **enemy_stats(lv, spec.get("mods", {}), boss=True),
             "affinities": spec["aff"], "tags": spec["tags"], "moves": spec["moves"], "phases": spec["phases"],
             "xp": int(6 * 2.5 * (8 + 5 * lv)), "gold": 60 * lv, "drops": [], "steal": {"common": tier_drops(lv)[1], "rare": "I024" if lv >= 30 else tier_drops(lv)[0]},
             "shape": spec["shape"], "tell": plain(b["tell"]), "counterplay": plain(b["counterplay"]), "optional": b["optional"],
             "status_immune": ["sleep", "stun", "doom"], "sprite": b["id"], "parts": []}
        if spec.get("copy_element"):
            r["copy_element"] = True
        for i, p in enumerate(spec["parts"]):
            pid = f"{b['id']}_P{i + 1}"
            out[pid] = {"id": pid, "name": p["name"], "level": lv, "hp": max(1, int(b["hp"] * p["hp_frac"])), **enemy_stats(lv, {"def": 0.5, "res": 0.5}),
                        "affinities": p.get("aff", {}), "tags": ["part"], "moves": {}, "cycle": [], "xp": 0, "gold": 0, "drops": [], "steal": {},
                        "shape": "part_" + p["id"].split("_")[1].lower(), "sprite": pid}
            r["parts"].append(pid)
        out[b["id"]] = r
    return out


# ---------------------------------------------------------------- maps
LEGEND_BASE = {
    "#": "wall", ".": "floor", ",": "floor2", ":": "path", "~": "water", "w": "shallow", "=": "bridge", "T": "tree",
    "o": "rock", '"': "grass", "R": "roof", "W": "house", "D": "door", "+": "doorway", "_": "void", "^": "cliff",
    "|": "rail", "b": "bench", "c": "crate", "r": "barrel", "l": "lamp", "k": "shelf", "m": "machine", "t": "table",
    "p": "pipe", "B": "bed", "s": "stairs", "x": "rubble", "*": "crystal", "f": "fence", "h": "hedge", "g": "garden",
    "n": "counter", "u": "pillar", "j": "bell", "v": "vent", "y": "statue", "z": "sand", "q": "snow", "i": "ice",
    "e": "ember", "a": "awning", "d": "dock", "L": "ladder", "S": "sign", "O": "well", "M": "mountain", "F": "forest",
    "H": "hills", "P": "plains", "C": "city", "X": "dungeon_mark", "Y": "town_mark", "K": "deep", "A": "ash",
    "N": "salt", "Z": "reef", "V": "cave", "I": "island", "U": "ruin", "E": "lift", "G": "gate", "Q": "window",
    "1": "flower", "2": "cart", "3": "laundry", "4": "chimney", "5": "anvil", "6": "boat", "7": "cable", "8": "mural", "9": "pool",
    "0": "hole", "&": "sluice", "%": "vine", "$": "chest_deco", "@": "altar", "!": "brazier", "?": "book", "<": "wheel",
    ">": "gear", "{": "grate", "}": "chain", "[": "shelter", "]": "tent", "/": "stair_l", "\\": "stair_r", "(": "arch",
    ")": "lever_deco", "`": "moss", "'": "puddle", ";": "roots",
}
SOLID = {"block", "tree2", "banner", "crystal_tall", "pipe_tall", "mast", "totem", "lantern_post", "roof_block", "wall", "water", "tree", "rock", "roof", "house", "void", "cliff", "rail", "crate", "barrel", "lamp", "shelf",
         "machine", "table", "pipe", "bed", "rubble", "crystal", "fence", "hedge", "counter", "pillar", "bell", "vent",
         "statue", "mountain", "deep", "reef", "window", "cart", "chimney", "anvil", "boat", "cable", "mural", "pool",
         "hole", "sluice", "altar", "brazier", "wheel", "gear", "chain", "shelter", "tent", "lever_deco", "well", "sign",
         "bench", "island_block", "garden", "laundry", "chest_deco", "book", "awning_solid", "gate", "wall_rock", "lava"}
ENCOUNTER_TERRAIN = {"floor", "floor2", "path", "shallow", "grass", "sand", "snow", "ice", "ash", "salt", "moss",
                     "roots", "plains", "forest", "hills", "puddle", "ember", "bridge", "stairs", "road", "rocky", "grass2",
                     "olive", "swamp", "cave_floor", "ruin_floor", "bone", "crystal_floor"}


def parse_cond(s):
    if not s:
        return []
    return [c.strip() for c in s.split(",") if c.strip()]


def tokenize(line):
    toks, cur, q = [], "", False
    for ch in line:
        if ch == '"':
            q = not q
            continue
        if ch == " " and not q:
            if cur:
                toks.append(cur)
            cur = ""
        else:
            cur += ch
    if cur:
        toks.append(cur)
    return toks


def parse_maps():
    maps = {}
    files = sorted(glob.glob(os.path.join(ROOT, "content_src", "maps", "*.map")))
    for fp in files:
        text = open(fp, encoding="utf-8").read()
        for block in re.split(r"^=== ", text, flags=re.M)[1:]:
            lines = block.split("\n")
            mid = lines[0].strip()
            m = {"id": mid, "props": {}, "entities": [], "legend": {}}
            mode = "hdr"
            grid = []
            for ln in lines[1:]:
                if mode == "grid":
                    if ln.strip() == "entities:" or ln.startswith("entities:"):
                        mode = "ent"
                        continue
                    if ln.strip() == "" and grid:
                        continue
                    grid.append(ln.rstrip("\n"))
                    continue
                if mode == "ent":
                    s = ln.split("#!")[0].strip()
                    if not s:
                        continue
                    toks = tokenize(s)
                    ent = {"type": toks[0], "args": [], "kv": {}}
                    for t in toks[1:]:
                        if "=" in t and not t.startswith("="):
                            k, v = t.split("=", 1)
                            ent["kv"][k] = v
                        else:
                            ent["args"].append(t)
                    m["entities"].append(ent)
                    continue
                s = ln.strip()
                if not s or s.startswith("#!"):
                    continue
                if s == "grid:":
                    mode = "grid"
                    continue
                if s.startswith("legend:"):
                    for pair in s[7:].split():
                        k, v = pair.split("=", 1)
                        m["legend"][k] = v
                    continue
                k, _, v = s.partition(":")
                m["props"][k.strip()] = v.strip()
            while grid and grid[-1].strip() == "":
                grid.pop()
            if len(set(len(r) for r in grid)) > 1:
                err(f"{mid}: ragged grid rows {sorted(set(len(r) for r in grid))}")
            w = max(len(r) for r in grid) if grid else 0
            grid = [r.ljust(w, "_") for r in grid]
            m["w"], m["h"], m["grid"] = w, len(grid), grid
            maps[mid] = compile_map(m, fp)
    return maps


def compile_map(m, fp):
    legend = dict(LEGEND_BASE)
    legend.update(m["legend"])
    out = {"id": m["id"], "name": plain(m["props"].get("name", m["id"])), "tileset": m["props"].get("tileset", "town_r01"),
           "music": m["props"].get("music", ""), "zone": m["props"].get("zone", ""), "region": m["props"].get("region", ""),
           "encounters": m["props"].get("encounters", ""), "rate": float(m["props"].get("rate", "1.0")),
           "dark": m["props"].get("dark", "false") == "true", "kind": m["props"].get("kind", "room"),
           "phase": m["props"].get("phase", ""), "w": m["w"], "h": m["h"], "grid": m["grid"], "legend": {},
           "entities": [], "save_ok": m["props"].get("save", "false") == "true", "bg": m["props"].get("battlebg", ""),
           "location": m["props"].get("location", "")}
    used = set("".join(m["grid"]))
    for ch in used:
        if ch not in legend:
            err(f"{m['id']}: unknown tile char {ch!r} ({os.path.basename(fp)})")
            continue
        out["legend"][ch] = legend[ch]
    for e in m["entities"]:
        t, a, kv = e["type"], e["args"], e["kv"]
        ent = {"type": t, "cond": parse_cond(kv.get("if", ""))}
        try:
            if t == "spawn":
                ent.update(name=a[0], x=int(a[1]), y=int(a[2]), dir=a[3] if len(a) > 3 else "down")
            elif t in ("door", "exit"):
                # door x y DEST_MAP spawn [dir]  |  exit x1..x2 y1..y2 DEST spawn
                xs, ys = a[0], a[1]
                x1, x2 = (int(xs.split("..")[0]), int(xs.split("..")[1])) if ".." in xs else (int(xs), int(xs))
                y1, y2 = (int(ys.split("..")[0]), int(ys.split("..")[1])) if ".." in ys else (int(ys), int(ys))
                ent.update(x1=x1, x2=x2, y1=y1, y2=y2, dest=a[2], spawn=a[3], sfx=kv.get("sfx", ""), msg=plain(kv.get("msg", "")),
                           locked_msg=plain(kv.get("locked", "")))
            elif t == "npc":
                ent.update(id=a[0], x=int(a[1]), y=int(a[2]), dir=a[3] if len(a) > 3 else "down", sprite=kv.get("sprite", a[0]),
                           talk=kv.get("talk", ""), wander=kv.get("wander", "0") == "1", name=plain(kv.get("name", "")),
                           solid=kv.get("solid", "1") == "1")
            elif t == "chest":
                ent.update(id=a[0], x=int(a[1]), y=int(a[2]), item=a[3], count=int(a[4]) if len(a) > 4 else 1,
                           gold=int(kv.get("gold", "0")), acq=kv.get("acq", ""), hidden=kv.get("hidden", "0") == "1")
            elif t in ("sign", "read"):
                ent.update(x=int(a[0]), y=int(a[1]), text=plain(" ".join(a[2:])), scene=kv.get("scene", ""))
            elif t == "trigger":
                xs, ys = a[0], a[1]
                x1, x2 = (int(xs.split("..")[0]), int(xs.split("..")[1])) if ".." in xs else (int(xs), int(xs))
                y1, y2 = (int(ys.split("..")[0]), int(ys.split("..")[1])) if ".." in ys else (int(ys), int(ys))
                ent.update(x1=x1, x2=x2, y1=y1, y2=y2, scene=kv["scene"], touch=kv.get("touch", "1") == "1")
            elif t == "save":
                ent.update(x=int(a[0]), y=int(a[1]))
            elif t in ("inn", "shop", "heal"):
                ent.update(x=int(a[0]), y=int(a[1]), id=a[2] if len(a) > 2 else "", scene=kv.get("scene", ""))
            elif t == "switch":
                ent.update(id=a[0], x=int(a[1]), y=int(a[2]), scene=kv.get("scene", ""), flag=kv.get("flag", ""),
                           sprite=kv.get("sprite", "lever"), toggle=kv.get("toggle", "0") == "1")
            elif t == "block":
                # conditional collision block: block x1..x2 y1..y2 [char] if=...
                xs, ys = a[0], a[1]
                x1, x2 = (int(xs.split("..")[0]), int(xs.split("..")[1])) if ".." in xs else (int(xs), int(xs))
                y1, y2 = (int(ys.split("..")[0]), int(ys.split("..")[1])) if ".." in ys else (int(ys), int(ys))
                ent.update(x1=x1, x2=x2, y1=y1, y2=y2, tile=kv.get("tile", "rubble"), msg=plain(kv.get("msg", "")))
            elif t == "tileset_over":
                xs, ys = a[0], a[1]
                x1, x2 = (int(xs.split("..")[0]), int(xs.split("..")[1])) if ".." in xs else (int(xs), int(xs))
                y1, y2 = (int(ys.split("..")[0]), int(ys.split("..")[1])) if ".." in ys else (int(ys), int(ys))
                ent.update(x1=x1, x2=x2, y1=y1, y2=y2, tile=a[2])
            elif t == "prop":
                ent.update(x=int(a[0]), y=int(a[1]), sprite=a[2], solid=kv.get("solid", "1") == "1")
            elif t == "location":
                ent.update(id=a[0], x=int(a[1]), y=int(a[2]), dest=kv.get("dest", ""), spawn=kv.get("spawn", "default"),
                           name=plain(kv.get("name", "")), land=kv.get("land", "0") == "1")
            elif t == "landing":
                xs, ys = a[0], a[1]
                x1, x2 = (int(xs.split("..")[0]), int(xs.split("..")[1])) if ".." in xs else (int(xs), int(xs))
                y1, y2 = (int(ys.split("..")[0]), int(ys.split("..")[1])) if ".." in ys else (int(ys), int(ys))
                ent.update(x1=x1, x2=x2, y1=y1, y2=y2, name=kv.get("name", ""))
            elif t == "hazard":
                xs, ys = a[0], a[1]
                x1, x2 = (int(xs.split("..")[0]), int(xs.split("..")[1])) if ".." in xs else (int(xs), int(xs))
                y1, y2 = (int(ys.split("..")[0]), int(ys.split("..")[1])) if ".." in ys else (int(ys), int(ys))
                ent.update(x1=x1, x2=x2, y1=y1, y2=y2, period=float(kv.get("period", "3")), on=float(kv.get("on", "1")),
                           phase=float(kv.get("phase", "0")))
            elif t == "vehicle":
                ent.update(kind=a[0], x=int(a[1]), y=int(a[2]))
            elif t == "zone":
                xs, ys = a[0], a[1]
                x1, x2 = (int(xs.split("..")[0]), int(xs.split("..")[1])) if ".." in xs else (int(xs), int(xs))
                y1, y2 = (int(ys.split("..")[0]), int(ys.split("..")[1])) if ".." in ys else (int(ys), int(ys))
                ent.update(x1=x1, x2=x2, y1=y1, y2=y2, encounters=kv.get("enc", ""))
            else:
                err(f"{m['id']}: unknown entity type {t}")
                continue
        except (IndexError, ValueError, KeyError) as ex:
            err(f"{m['id']}: bad entity line {t} {a} {kv}: {ex}")
            continue
        out["entities"].append(ent)
    return out


def check_maps(maps, scenes, items, forms):
    for mid, m in maps.items():
        spawns = {e["name"]: e for e in m["entities"] if e["type"] == "spawn"}
        for e in m["entities"]:
            if e["type"] in ("door", "exit"):
                dest = maps.get(e["dest"])
                if dest is None:
                    err(f"{mid}: door to unknown map {e['dest']}")
                    continue
                if e["spawn"] not in {x["name"] for x in dest["entities"] if x["type"] == "spawn"}:
                    err(f"{mid}: door to {e['dest']} unknown spawn {e['spawn']}")
            if e["type"] == "spawn":
                if not (0 <= e["x"] < m["w"] and 0 <= e["y"] < m["h"]):
                    err(f"{mid}: spawn {e['name']} out of bounds")
                else:
                    kind = m["legend"].get(m["grid"][e["y"]][e["x"]], "?")
                    if kind in SOLID:
                        err(f"{mid}: spawn {e['name']} on solid tile {kind}")
            for key in ("talk", "scene"):
                if e.get(key) and e[key] not in scenes:
                    err(f"{mid}: {e['type']} references missing scene {e[key]}")
            if e["type"] == "chest" and e["item"] not in items and e["item"] != "gold":
                err(f"{mid}: chest {e['id']} unknown item {e['item']}")
        for e in m["entities"]:
            if e["type"] == "location" and e["dest"] not in maps:
                pending.append(f"{mid}: location {e['id']} -> {e['dest']} (map not built yet)")
        enc = m.get("encounters", "")
        if enc and enc != "none" and enc not in forms["groups"]:
            err(f"{mid}: unknown encounter group {enc}")


# ---------------------------------------------------------------- scenes
def parse_scenes():
    scenes = {}
    for fp in sorted(glob.glob(os.path.join(ROOT, "content_src", "scenes", "*.scn"))):
        cur = None
        for n, raw in enumerate(open(fp, encoding="utf-8").read().split("\n"), 1):
            ln = raw.strip()
            if not ln or ln.startswith("#"):
                continue
            if ln.startswith("@scene"):
                parts = ln.split()
                cur = {"id": parts[1], "once": "once" in parts[2:], "cmds": [], "file": os.path.basename(fp)}
                if cur["id"] in scenes:
                    err(f"duplicate scene {cur['id']}")
                scenes[cur["id"]] = cur
                continue
            if ln == "@end":
                cur = None
                continue
            if cur is None:
                err(f"{os.path.basename(fp)}:{n}: command outside scene")
                continue
            if "|" in ln and ln.split()[0] in ("say", "doc", "choice", "objective", "rumor", "note", "journal"):
                head, _, text = ln.partition("|")
                ht = head.split()
                cmd = {"c": ht[0], "a": ht[1:], "text": plain(text.strip())}
                if ht[0] == "choice":
                    opts = [o.strip() for o in ln.split("|")[1:]]
                    cmd["options"] = []
                    for o in opts:
                        lab, _, tgt = o.partition("->")
                        cmd["options"].append({"text": plain(lab.strip()), "goto": tgt.strip()})
                    del cmd["text"]
            else:
                t = tokenize(ln)
                cmd = {"c": t[0], "a": t[1:]}
            if cmd["c"] not in SCENE_CMDS:
                err(f"{os.path.basename(fp)}:{n}: unknown scene command {cmd['c']}")
            cmd["line"] = n
            cur["cmds"].append(cmd)
    # label checks
    for sid, s in scenes.items():
        labels = {c["a"][0] for c in s["cmds"] if c["c"] == "label"}
        for c in s["cmds"]:
            if c["c"] == "goto" and c["a"][0] not in labels:
                err(f"{sid}: goto missing label {c['a'][0]}")
            if c["c"] == "if" and c["a"][-1] not in labels:
                err(f"{sid}: if-goto missing label {c['a'][-1]}")
            if c["c"] == "choice":
                for o in c["options"]:
                    if o["goto"] and o["goto"] not in labels:
                        err(f"{sid}: choice missing label {o['goto']}")
            if c["c"] == "call" and c["a"][0] not in scenes:
                err(f"{sid}: call missing scene {c['a'][0]}")
    return scenes


def check_scene_refs(scenes, maps, items, forms, chars):
    for sid, s in scenes.items():
        for c in s["cmds"]:
            a = c["a"]
            if c["c"] in ("give", "take") and a and a[0] not in items:
                err(f"{sid}: unknown item {a[0]}")
            if c["c"] in ("key", "unkey") and a[0] not in items:
                err(f"{sid}: unknown key item {a[0]}")
            if c["c"] == "battle" and a[0] not in forms["formations"]:
                err(f"{sid}: unknown formation {a[0]}")
            if c["c"] == "warp" and a[0] not in maps:
                err(f"{sid}: warp to unknown map {a[0]}")
            if c["c"] in ("join", "leave") and a[0] not in chars:
                err(f"{sid}: unknown character {a[0]}")


def make_variant(enemies, eid, level):
    vid = f"{eid}@{level}"
    if vid in enemies:
        return vid
    base = enemies[eid]
    spec = EN.E.get(eid)
    r = json.loads(json.dumps(base))
    r["id"] = vid
    r["level"] = level
    r["hp"] = int(round(base["hp"] * (level / base["level"]) ** 1.3))
    r.update(enemy_stats(level, spec["mods"] if spec else {}))
    r["xp"], r["gold"] = 8 + 5 * level, 10 + 6 * level
    common, rare = tier_drops(level)
    r["drops"] = [{"item": common, "chance": 20}, {"item": "I007", "chance": 8}]
    r["steal"] = {"common": common, "rare": rare}
    r["variant_of"] = eid
    enemies[vid] = r
    return vid


def build_formations(enemies):
    forms = {"formations": {}, "groups": {}}
    for fid, f in FM.FORMATIONS.items():
        ff = dict(f)
        ff["id"] = fid
        slots = []
        for slot in f["enemies"]:
            eid = slot if isinstance(slot, str) else slot["id"]
            if eid not in enemies:
                err(f"formation {fid}: unknown enemy {eid}")
                continue
            if isinstance(slot, dict) and "level" in slot:
                eid = make_variant(enemies, eid, slot["level"])
            slots.append(eid)
            for pid in enemies[eid].get("parts", []):
                slots.append({"id": pid, "part_of": "E1"})
        ff["enemies"] = slots
        forms["formations"][fid] = ff
    for gid, g in FM.GROUPS.items():
        for fid in g:
            if fid not in forms["formations"]:
                err(f"group {gid}: unknown formation {fid}")
        forms["groups"][gid] = g
    return forms


def build_shops(items):
    shops = {}
    for sid, spec in FM.SHOPS.items():
        shops[sid] = spec
    return shops


def main():
    cat = {k: load(k) for k in ["characters", "abilities", "weapons", "armor", "accessories", "consumables", "statuses",
                                  "enemies", "bosses", "dungeons", "regions", "towns", "chapters", "quests", "music", "sfx"]}
    content = {"schema": 1}
    PL.apply(cat, FM)
    content["characters"] = build_characters(cat["characters"])
    content["abilities"] = build_abilities(cat["abilities"])
    content["items"] = build_items(cat["weapons"], cat["armor"], cat["accessories"], cat["consumables"])
    GR.build(content["items"])
    for i, iid in enumerate(sorted(content["items"])):
        content["items"][iid]["icon"] = i          # cell in assets/ext/sprites/icons_*.png (tools/art/icons.py)
    content["gear"] = {"upgrade": {str(k): list(v) for k, v in GR.UPGRADE.items()}, "step": GR.UPGRADE_STEP,
                       "smith_shops": GR.SMITH_SHOPS, "ore_stock": GR.ORE_STOCK, "lines": GR.LINE_ORDER}
    content["statuses"] = {s["id"]: {"id": s["id"], "name": s["name"], "type": s["type"], "duration": TB.STATUS_DURATION[s["id"]],
                                     "desc": plain(s["effect"])} for s in cat["statuses"]}
    BX.apply(cat["enemies"], EN)
    BX.apply_formations(FM)
    BX.apply_world_groups(FM)
    BS.apply(cat["bosses"], EN, TB, FM)
    content["enemies"] = build_enemies(cat["enemies"], cat["bosses"])
    for eid, e in content["enemies"].items():
        e["lore"] = BX.LORE.get(eid, BS.LORE.get(eid, e.get("lore", "")))
    content["vestiges"] = TB.VESTIGES
    content["formations"] = build_formations(content["enemies"])
    content["shops"] = build_shops(content["items"])
    content["shop_rules"] = {"basic": TB.BASIC_STOCK, "expanded": TB.EXPANDED_STOCK, "late": TB.LATE_STOCK,
                             "weapon_tier_chapter": {str(k): v for k, v in TB.TIER_CHAPTER_WEAPON.items()},
                             "armor_tier_chapter": {str(k): v for k, v in TB.TIER_CHAPTER_ARMOR.items()},
                             "accessory_chapter": TB.ACCESSORY_SHOP}
    content["chapters"] = {c["id"]: {"id": c["id"], "name": plain(c["name"]), "act": c["act"], "prerequisites": c["prerequisites"],
                                     "status": c["status"]} for c in cat["chapters"]}
    content["quests"] = {q["id"]: {k: (plain(v) if isinstance(v, str) else v) for k, v in q.items()} for q in cat["quests"]}
    content["dungeons"] = {d["id"]: {"id": d["id"], "name": plain(d["name"]), "region": d["region"], "rooms": [r["id"] for r in d["rooms"]],
                                     "levels": d["levels"], "optional": d["optional"]} for d in cat["dungeons"]}
    content["towns"] = {t["id"]: {"id": t["id"], "name": t["name"], "region": t["region"]} for t in cat["towns"]}
    content["regions"] = {r["id"]: {"id": r["id"], "name": r["name"]} for r in cat["regions"]}
    content["music"] = {m["id"]: {"id": m["id"], "name": plain(m["name"]), "use": m["use"]} for m in cat["music"]}
    content["sfx"] = {s["id"]: {"id": s["id"], "name": s["name"], "slot": s["slot"]} for s in cat["sfx"]}
    content["speakers"] = FM.SPEAKERS
    content["locations"] = FM.LOCATIONS
    content["tile_rules"] = {"solid": sorted(SOLID), "enc": sorted(ENCOUNTER_TERRAIN),
                             "tall": ["tree", "tree2", "lamp", "pillar", "statue", "shelf", "banner", "crystal_tall", "pipe_tall", "mast", "totem", "lantern_post"],
                             "passable_extra": ["door", "doorway", "stairs", "bridge", "ladder", "dock", "carpet", "grate"]}
    CAST.apply(content, check_ops)
    VES.apply(content, check_ops)
    content["scenes"] = parse_scenes()
    content["maps"] = parse_maps()
    check_maps(content["maps"], content["scenes"], content["items"], content["formations"])
    check_scene_refs(content["scenes"], content["maps"], content["items"], content["formations"], content["characters"])
    dumped = json.dumps(content, ensure_ascii=False).replace("“", '\\"').replace("”", '\\"')
    content = json.loads(plain(dumped))   # every display string uses the Ashen8 glyph set
    fnt = open(os.path.join(ROOT, "game", "assets", "fonts", "ashen8.fnt"), encoding="utf-8").read()
    glyphs = {int(x) for x in re.findall(r"char id=(\d+)", fnt)}
    missing = sorted({ch for ch in json.dumps(content, ensure_ascii=False) if ord(ch) >= 32 and ord(ch) not in glyphs and ch not in '{}\\'})
    if missing:
        err("characters without a font glyph: " + "".join(missing))
    blob = json.dumps(content, sort_keys=True, ensure_ascii=False)
    content["content_hash"] = hashlib.sha256(blob.encode()).hexdigest()[:16]
    stats = {k: len(v) for k, v in content.items() if isinstance(v, dict)}
    for p_ in pending:
        print("PENDING:", p_)
    if pending and "--strict" in sys.argv:
        errors.append(f"{len(pending)} pending references in strict mode")
    content["pending"] = pending
    if errors:
        for e in errors:
            print("ERROR:", e)
        print(f"compile_content: FAIL ({len(errors)} errors)")
        return 1
    if "--check" not in sys.argv:
        os.makedirs(os.path.join(ROOT, "game", "content"), exist_ok=True)
        with open(os.path.join(ROOT, "game", "content", "content.json"), "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, separators=(",", ":"))
    print("compile_content: OK", content["content_hash"], stats)
    return 0


if __name__ == "__main__":
    sys.exit(main())
