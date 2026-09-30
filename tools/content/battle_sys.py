"""Expansion battle systems content (branch s1): blue magic (Lore), Capture/Morph, damage-limit breakers, level breaks
and superbosses' steal tables. Limit breaks live in limits.py, Vestiges V13-V24 in vestiges.py.

Blue magic ("Lore"). Four heroes learn enemy moves, each by one rule that fits their lore:
- Golem (C04), rune machinist: "hit". His runes record the force pattern of a move that strikes him.
- Corvus (C12), plague doctor: "hit". He studies an affliction in his own body before he can use it.
- Kitsune (C09), fox illusionist: "see". She copies any move she watches an enemy use.
- Lich King (C13), emperor of the dead: "see". His court remembers every death it witnessed.
The learner must be in the fight, and the move is kept when the battle is won with the learner still standing. The pool
is shared (Game.S.blue): any of the four can cast any learned move through the "Lore" command. A learned move reuses the
source enemy move's ops (copied from the compiled enemy table at build time), cast as magic by the hero.

Capture (Sak, C08, ability S201 learned at level 8; the Capture command appears in his command list): works on a non-boss
enemy at or below half HP; chance 35% at half HP rising to 95% near 0. The captured enemy leaves the battle (rewards
still count) and is added to Game.S.captured (Arena fighters later). 25% of captures also "morph" into a rare item
(MORPH by enemy level).
"""

MAGES = {"C04": "hit", "C12": "hit", "C09": "see", "C13": "see"}

# blue id -> (sources [(enemy id, move id)], mp, power scale, desc)
BLUE = {
    "S301": ([("E014", "burst"), ("B04", "sweep")], 8, 1.0, "Pressure fire on every enemy."),
    "S302": ([("E011", "pollen"), ("E056", "hex"), ("E064", "hex"), ("E114", "hex")], 6, 1.0, "Puts one enemy to sleep."),
    "S303": ([("E015", "blind"), ("E072", "hex"), ("E078", "hex"), ("E118", "hex")], 4, 1.0, "Blinds one enemy."),
    "S304": ([("E006", "silence")], 5, 1.0, "Silences one enemy."),
    "S305": ([("E067", "spit"), ("E058", "spit"), ("E096", "spit")], 5, 1.0, "Poison damage; poisons."),
    "S306": ([("E018", "drain"), ("E046", "drain"), ("E063", "drain"), ("E098", "drain"), ("E107", "drain")], 8, 1.1, "Damage that heals the caster."),
    "S307": ([("E030", "heal"), ("E071", "heal"), ("E079", "heal"), ("E087", "heal"), ("E099", "heal")], 6, 2.0, "Heals one ally."),
    "S308": ([("E028", "stun")], 10, 1.0, "Light damage; may stun."),
    "S309": ([("E024", "slow")], 6, 1.0, "Light damage; slows."),
    "S310": ([("E031", "bleed")], 6, 1.0, "Damage; causes Bleed."),
    "S311": ([("E026", "strip")], 8, 1.0, "Strips a boon, then damages."),
    "S312": ([("E039", "doom")], 14, 1.0, "Doom on one enemy (bosses are immune)."),
    "S313": ([("B03", "cage")], 10, 1.0, "Earth damage; slows."),
    "S314": ([("BX01", "tide")], 14, 1.0, "Water on every enemy; may slow."),
    "S315": ([("BX02", "meltdown")], 26, 1.0, "White-hot fire on every enemy."),
    "S316": ([("BX04", "screech")], 12, 1.0, "Silences every enemy."),
    "S317": ([("BX08", "blizzard")], 28, 1.0, "Whiteout on every enemy."),
    "S318": ([("BX15", "hollow")], 22, 1.0, "Heavy shadow on one enemy; may Doom."),
    "S319": ([("BX06", "plague")], 20, 1.0, "Poison cloud on every enemy."),
    "S320": ([("BX06", "sermon")], 12, 1.0, "Weakens every enemy."),
    "S321": ([("BX19", "gaze")], 16, 1.0, "Light on every enemy."),
    "S322": ([("BX07", "sentence")], 24, 1.0, "Heavy light on one enemy."),
    "S323": ([("SB01", "sig"), ("SB02", "sig"), ("SB03", "sig"), ("SB04", "sig")], 60, 0.7,
             "An ancient dragon's signature, in a smaller throat. Breaks the damage limit."),
    "S324": ([("SB12", "unmake")], 99, 0.6, "What the Unmade Crown did to you. Breaks the damage limit."),
}

CAPTURE = {"id": "S201", "owner": "C08", "level": 8, "hp_frac": 0.5, "base": 35, "slope": 120, "max": 95,
           "morph_chance": 25, "morph": [[0, "I006"], [20, "I020"], [35, "I024"]]}

# damage-limit breakers: late accessories (passive break_damage), found as superbosses' rare steals
BREAKERS = {
    "A201": ("Wyrmscale Brand", {"break_damage": True, "atb_mult": 1.05}, "Breaks the damage limit; readiness +5%.", ["SB01", "SB02", "SB03", "SB04"]),
    "A202": ("Champion's Laurel", {"break_damage": True, "counter": 0.5}, "Breaks the damage limit; counters physical hits.", ["SB07"]),
    "A203": ("Crown of Nothing", {"break_damage": True, "mag_bonus": 0.1}, "Breaks the damage limit; +10% magic power.", ["SB09", "SB10", "SB11", "SB12"]),
}
# other superbosses: rare steal is a Megalixir-grade Elixir, common a High Ether (unchanged)

LEVEL_BREAKS = {"default": 99, "levelbreak_1": 120, "levelbreak_2": 150, "levelbreak_3": 200}
WYRMS = ["SB01", "SB02", "SB03", "SB04"]
FINALE = "SB12"


def _blue_kind(ops):
    if any(o["op"] == "damage" for o in ops):
        return "magical"
    if any(o["op"] == "heal" for o in ops):
        return "heal"
    return "utility"


def _blue_target(mv, ops):
    t = mv.get("target", "random")
    if any(o["op"] == "heal" for o in ops):
        return "ally_all" if t in ("allies", "all") else "ally_one"
    if t in ("all", "row_front", "row_back"):
        return "enemy_all"
    if t == "self":
        return "self"
    return "enemy_one"


def apply(content, check=None):
    ab = content["abilities"]
    en = content["enemies"]
    chars = sorted(content["characters"])
    src = {}
    for bid, (sources, mp, scale, desc) in BLUE.items():
        eid, mid = sources[0]
        mv = en[eid]["moves"][mid]
        ops = []
        for o in mv["ops"]:
            o = dict(o)
            if o["op"] == "damage":
                o["type"] = "magical"
                o["power"] = int(round(float(o["power"]) * scale))
                o.pop("copy", None)
            elif o["op"] == "heal" and "power" in o:
                o["power"] = int(round(float(o["power"]) * scale))
            ops.append(o)
        if check:
            check(bid, ops)
        elem = mv.get("element") or next((o.get("element") for o in ops if o["op"] == "damage" and o.get("element")), "none")
        if elem in ("physical", None):
            elem = "none"
        ab[bid] = {"id": bid, "name": mv.get("name", mid), "owner": "", "mp": mp,
                   "power": max([o.get("power", 0) for o in ops if o["op"] == "damage"] or [0]),
                   "kind": _blue_kind(ops), "target": _blue_target(mv, ops), "desc": desc, "ops": ops, "family": "blue",
                   "anim": "cast", "element": elem, "elemental_spell": False, "revive": False, "field": False, "concord": True,
                   "blue": True}
        for eid, mid in sources:
            assert mid in en[eid]["moves"], (bid, eid, mid)
            src["%s:%s" % (eid, mid)] = bid
    content["blue"] = {"mages": MAGES, "src": src, "order": sorted(BLUE)}
    # Capture (Sak)
    c = CAPTURE
    ab[c["id"]] = {"id": c["id"], "name": "Capture", "owner": c["owner"], "mp": 0, "power": 0, "kind": "utility",
                   "target": "enemy_one", "desc": "Captures a weakened enemy (half HP or less; not bosses). Sometimes it morphs into a rare item.",
                   "ops": [{"op": "capture"}], "family": "skill", "anim": "attack", "element": "none", "elemental_spell": False,
                   "revive": False, "field": False, "concord": True, "unlock_level": c["level"], "command": "capture"}
    learn = content["characters"][c["owner"]]["learn"]
    if not any(x["id"] == c["id"] for x in learn):
        learn.append({"id": c["id"], "level": c["level"]})
    content["capture"] = {k: c[k] for k in ("id", "hp_frac", "base", "slope", "max", "morph_chance", "morph")}
    # damage-limit breakers and the superbosses' rare steals
    nxt = max(int(it.get("icon", -1)) for it in content["items"].values()) + 1
    for aid, (name, passives, desc, bosses) in BREAKERS.items():
        content["items"][aid] = {"id": aid, "name": name, "kind": "accessory", "slot": "accessory", "price": 0,
                                 "allowed": list(chars), "sellable": False, "passives": dict(passives), "desc": desc,
                                 "icon": nxt}
        nxt += 1
        for b in bosses:
            en[b].setdefault("steal", {})
            en[b]["steal"]["rare"] = aid
    content["level_breaks"] = {"caps": LEVEL_BREAKS, "wyrms": WYRMS, "finale": FINALE}
    return content
