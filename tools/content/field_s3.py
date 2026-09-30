"""Field and world systems (expansion pass s3): data tables compiled into content.json.

  travel   travel networks (Deep mine-rail, mag-rail, magma skiffs, lake barges): stops with a destination map,
           spawn and condition; field_sys.gd opens them as travel menus (`travel menu <net>` in a scene).
  arena    the Crucible Isle (N38): the ranked ladder, solo challenges, the item-betting table and the
           superboss gauntlet (arena.gd runs them; `arena <op>` in a scene).
  items    ZW01 Wayfarer's Sigil: a consumable that opens the waystone menu anywhere outside battle and dungeons.
Waystones themselves are map entities (`waystone ID x y name=".." region=R01 [layer=deep]`, written by
tools/world2/wgen.py on the world maps).
"""

WARP_ITEM = "ZW01"   # sorts after every other item id, so its icon cell (sorted order) is the next free one

TRAVEL = {
    "rail_u1": {"name": "Delver Mine-Rail", "sfx": "FX010", "line": "The cart jolts off down the dark rails.", "stops": [
        {"id": "U11", "name": "Vaultmouth Rail", "map": "U11_R01", "spawn": "from_rail", "if": []},
        {"id": "U02", "name": "Karag Dun", "map": "U02_R01", "spawn": "from_rail", "if": []},
        {"id": "U12", "name": "Deepforge Mines", "map": "U12_R01", "spawn": "from_rail", "if": []},
    ]},
    "mag_u2": {"name": "Lattice Mag-Rail", "sfx": "FX010", "line": "The mag-car lifts off its rail and runs without a sound.", "stops": [
        {"id": "U26", "name": "Mag-rail Terminus", "map": "U26_R01", "spawn": "from_rail", "if": []},
        {"id": "U19", "name": "Railhead Nine", "map": "U19_R01", "spawn": "from_rail", "if": []},
        {"id": "U17", "name": "Meridian", "map": "DEEP_POST", "spawn": "l_u17", "if": ["phase:post"]},
        {"id": "U24", "name": "Prime Relay spur", "map": "DEEP_POST", "spawn": "l_u24", "if": ["phase:post"]},
    ]},
    "lava_u1": {"name": "Magma Skiffs", "sfx": "FX031", "line": "The skiff noses out onto the crust. Nobody touches the sides.", "stops": [
        {"id": "U06", "name": "Magma Ferry", "map": "U06_R01", "spawn": "from_ferry", "if": []},
        {"id": "U07", "name": "Cinderlake Isles", "map": "U07_R01", "spawn": "from_ferry", "if": ["!phase:post"]},
        {"id": "U15", "name": "Fungal Terraces", "map": "U15_R01", "spawn": "from_ferry", "if": ["phase:post"]},
    ]},
    "lake_u2": {"name": "Glasswater Barge", "sfx": "FX031", "line": "The barge slides over water too clear to trust.", "stops": [
        {"id": "U21", "name": "Glasswater Reservoir", "map": "U21_R01", "spawn": "from_barge", "if": []},
        {"id": "U26", "name": "Mag-rail Terminus", "map": "U26_R01", "spawn": "from_barge", "if": []},
    ]},
    "lake_u3": {"name": "Black-Lake Boat", "sfx": "FX031", "line": "The boat moves without a sound over water that shows no reflection.", "stops": [
        {"id": "U28", "name": "Styx Landing", "map": "U28_R01", "spawn": "from_boat", "if": []},
        {"id": "U29", "name": "Cenotaph", "map": "U29_R01", "spawn": "from_boat", "if": []},
    ]},
}

# The Crucible Isle arena. Ladder ranks use existing formations of rising level; each rank pays once.
ARENA = {
    "ladder": [
        {"rank": 1, "name": "Sawdust Bout", "form": "D04_5", "reward": "I002", "n": 3, "gold": 300, "if": []},
        {"rank": 2, "name": "The Brass Pair", "form": "D05_4", "reward": "A103", "n": 1, "gold": 400, "if": []},
        {"rank": 3, "name": "Wind on the Ropes", "form": "D06_5", "reward": "I005", "n": 2, "gold": 600, "if": []},
        {"rank": 4, "name": "Ivory Seconds", "form": "D07_5", "reward": "A111", "n": 1, "gold": 800, "if": []},
        {"rank": 5, "name": "The Choir Box", "form": "D08_4", "reward": "I020", "n": 2, "gold": 1000, "if": []},
        {"rank": 6, "name": "Conduit Brawlers", "form": "D09_5", "reward": "A114", "n": 1, "gold": 1400, "if": ["ch:CH09"]},
        {"rank": 7, "name": "Returners' Grudge", "form": "D05P_2", "reward": "I003", "n": 3, "gold": 1800, "if": ["phase:post"]},
        {"rank": 8, "name": "Salt and Iron", "form": "D06P_2", "reward": "A117", "n": 1, "gold": 2400, "if": ["phase:post"]},
        {"rank": 9, "name": "Winter's Court", "form": "D11_3", "reward": "A118", "n": 1, "gold": 3200, "if": ["phase:post"]},
        {"rank": 10, "name": "The Starless Ring", "form": "D12_4", "reward": "I024", "n": 1, "gold": 5000, "if": ["phase:post"]},
    ],
    "solo": [
        {"id": "solo1", "name": "The Lonely Road", "form": "D06_5", "rank": 2, "reward": "A112", "n": 1},
        {"id": "solo2", "name": "One Against Three", "form": "D08_4", "rank": 5, "reward": "A116", "n": 1},
        {"id": "solo3", "name": "Last Lantern Standing", "form": "D11_3", "rank": 8, "reward": "A022", "n": 1},
    ],
    # FF6-style wager table: put up an item, fight the house's pick, win the better item or lose the wager
    "bets": [
        {"wager": "I001", "form": "D05_4", "prize": "I002"},
        {"wager": "I002", "form": "D08_4", "prize": "I003"},
        {"wager": "I004", "form": "D07_5", "prize": "I005"},
        {"wager": "I006", "form": "D09_5", "prize": "I020"},
        {"wager": "I013", "form": "D06_5", "prize": "I021"},
        {"wager": "A101", "form": "D06P_2", "prize": "A111"},
        {"wager": "A106", "form": "D11_3", "prize": "A114"},
        {"wager": "A112", "form": "D12_4", "prize": "A118"},
        {"wager": "I003", "form": "D12_4", "prize": "I024"},
    ],
    # the champion's gauntlet: one fight after another with no rest; Varro the Unbeaten at the top
    "gauntlet": ["BX10", "BX12", "BX21", "BX24", "SB07"],
    "gauntlet_if": ["phase:post", "ch:CH16"],
    "gauntlet_reward": "A018",
    # captured monsters (Game.S.captured, when another system provides it) can be entered in beast bouts
    "beast_stake": 200,
}


def apply(content, err):
    items = content["items"]
    icon = max([int(it.get("icon", -1)) for it in items.values()] + [-1]) + 1   # tools/art/icons.py fills this cell
    items[WARP_ITEM] = {"id": WARP_ITEM, "name": "Wayfarer's Sigil", "kind": "consumable", "price": 400,
                        "desc": "Opens the waystone roads from anywhere outside battle and dungeons. Consumed on travel.",
                        "target": "party", "ops": [], "battle": False, "field": True, "revive": False, "special": "warp",
                        "sellable": True, "icon": icon}
    content["travel"] = TRAVEL
    content["arena"] = ARENA
    errs = []
    forms = set()
    for r in ARENA["ladder"]:
        forms.add(r["form"])
        if r["reward"] not in items:
            errs.append("arena ladder reward %s" % r["reward"])
    for s in ARENA["solo"]:
        forms.add(s["form"])
        if s["reward"] not in items:
            errs.append("arena solo reward %s" % s["reward"])
    for b in ARENA["bets"]:
        forms.add(b["form"])
        for k in ("wager", "prize"):
            if b[k] not in items:
                errs.append("arena bet item %s" % b[k])
    forms |= set(ARENA["gauntlet"])
    for f in sorted(forms):
        if f not in content["formations"]["formations"]:
            errs.append("arena formation %s" % f)
    for e in errs:
        err("field_s3: unknown " + e)


def check_map(mid, m, forms, err):
    enc = m.get("encounters_post", "")
    if enc and enc != "none" and enc not in forms["groups"]:
        err(f"{mid}: unknown encounters_post group {enc}")
    for e in m["entities"]:
        if e["type"] == "zone" and e.get("encounters", "") not in ("", "none") and e["encounters"] not in forms["groups"]:
            err(f"{mid}: zone with unknown encounter group {e['encounters']}")


def check_travel(maps, err):
    for net, t in TRAVEL.items():
        for st in t["stops"]:
            m = maps.get(st["map"])
            if m is None:
                err(f"travel {net}: unknown map {st['map']}")
            elif st["spawn"] not in {e["name"] for e in m["entities"] if e["type"] == "spawn"}:
                err(f"travel {net}: {st['map']} has no spawn {st['spawn']}")
