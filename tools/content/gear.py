"""Regional gear lines (expansion Phase 2, owner-approved design doc 2026-09-29).

Six lines, one per region. Each piece sits between two existing tiers (a sidegrade with a passive rather than a
straight upgrade): stats = lerp(tier a, tier b, f) of the matching existing item, rounded. Prices follow the same lerp.
IDs: weapons W101-W148, armor G101-G124, accessories A101-A118, upgrade ore M001-M003.
"""

CHARS = ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08"]
FIRST_WEAPON = {"C01": 1, "C02": 7, "C03": 13, "C04": 19, "C05": 25, "C06": 31, "C07": 37, "C08": 43}  # W001.. per owner

# line id -> region, shop town, chapter whose completion stocks it, weapon lerp (tier a, tier b, f), armor lerp, element, passives
LINES = {
    "oathguard": dict(region="R01", town="T02", chapter="CH01", w=(1, 2, 0.45), a=(1, 2, 0.45), element="",
                      wp={"lowhp_guard": 0.25}, ap={"lowhp_guard": 0.2}),
    "furnace":   dict(region="R02", town="T03", chapter="CH03", w=(1, 2, 0.9), a=(1, 2, 0.8), element="fire",
                      wp={}, ap={"elem_resist": {"fire": True}}),
    "tideglass": dict(region="R03", town="T04", chapter="CH04", w=(2, 3, 0.45), a=(2, 3, 0.2), element="water",
                      wp={"mp_regen": 2}, ap={"mp_regen": 2}),
    "returner":  dict(region="R04", town="T05", chapter="CH06", w=(2, 3, 0.75), a=(2, 3, 0.35), element="",
                      wp={"atb_mult": 1.08}, ap={"atb_mult": 1.05}),
    "boneglass": dict(region="R05", town="T06", chapter="CH07", w=(2, 3, 0.95), a=(2, 3, 0.55), element="",
                      wp={"immune": ["blind", "silence"], "mag_bonus": 0.12}, ap={"immune": ["poison", "sleep"]}),
    "salvage":   dict(region="R06", town="T07", chapter="CH12", w=(3, 4, 0.55), a=(3, 4, 0.2), element="",
                      wp={"reserve_scale": 0.02}, ap={"reserve_scale": 0.015}),
}
LINE_ORDER = ["oathguard", "furnace", "tideglass", "returner", "boneglass", "salvage"]

WEAPON_NAMES = {
    "oathguard": ["Oathguard Sword", "Pennant Rod", "Gatewatch Spear", "Quarry Maul", "Millrace Bow", "Wheatsheaf Staff", "Oathbound Blade", "Cutpurse Knife"],
    "furnace":   ["Forgebrand", "Ember Wand", "Flue Pike", "Slag Hammer", "Cinder Recurve", "Hearth Crook", "Smelted Edge", "Tongs Dagger"],
    "tideglass": ["Tidecutter", "Brine Wand", "Bell Harpoon", "Anchor Wrench", "Gullwing Bow", "Bellstaff", "Tidal Rune", "Rope Fang"],
    "returner":  ["Homeward Saber", "Windcord Rod", "Cable Lance", "Pulley Hammer", "Updraft Bow", "Cairn Staff", "Summit Edge", "Kite Knife"],
    "boneglass": ["Boneglass Sword", "Salt Prism Rod", "Glass Lance", "Kiln Hammer", "Lilac Bow", "Memory Staff", "Glass Rune", "Shard Dagger"],
    "salvage":   ["Salvaged Blade", "Lantern Rod", "Mooring Spear", "Scrap Engine", "Pontoon Bow", "Driftwood Crook", "Sign-Iron Blade", "Driftknife"],
}
# armor per line: heavy body (C01 C03 C04 C07), robe (C02 C06), leather (C05 C08), head (all)
ARMOR_NAMES = {
    "oathguard": ["Oathguard Plate", "Pennant Robe", "Mill Leathers", "Gatewatch Helm"],
    "furnace":   ["Furnace Mail", "Ember Apron", "Stoker's Jerkin", "Smoke Goggles"],
    "tideglass": ["Tideglass Mail", "Tidewoven Mantle", "Chartmaker's Coat", "Bell Cap"],
    "returner":  ["Returner's Harness", "Windcord Robe", "Ferryman's Jacket", "Cloud Hood"],
    "boneglass": ["Boneglass Plate", "Listening Robe", "Salt-Road Hide", "Listening Veil"],
    "salvage":   ["Salvage Mail", "Hearth Shawl", "Pontoon Oilskin", "Lantern Hood"],
}
ARMOR_BASE = [("body", ["G013", "G014", "G015", "G016"], ["C01", "C03", "C04", "C07"]),
              ("body", ["G001", "G002", "G003", "G004"], ["C02", "C06"]),
              ("body", ["G005", "G006", "G007", "G008"], ["C05", "C08"]),
              ("head", ["G017", "G019", "G021", "G023"], CHARS)]

# 3 accessories per line: (name, passives, price)
ACCESSORIES = {
    "oathguard": [("Oath Pennant", {"lowhp_guard": 0.3}, 600), ("Baker's Mitts", {"heal_mult": 1.1}, 520),
                  ("Shift Bell", {"start_atb": 100}, 900)],
    "furnace":   [("Vent-Iron Gauntlets", {"elem_resist": {"fire": True}, "phys_reduce": 0.05}, 1100),
                  ("Coal Heart", {"weapon_element": "fire"}, 1300), ("Stoker's Band", {"mhp_mult": 1.08}, 1000)],
    "tideglass": [("Tide Charm", {"mp_regen": 3}, 1400), ("Brine Pearl", {"elem_resist": {"water": True}}, 1250),
                  ("Chart Lens", {"acc_bonus": 12}, 1200)],
    "returner":  [("Returner's Cord", {"auto_revive": True}, 2200), ("Windcord Knot", {"atb_mult": 1.1}, 1900),
                  ("Ferryman's Boots", {"encounter_mult": 0.8}, 1500)],
    "boneglass": [("Scholar's Monocle", {"reveal_affinity": True, "mag_bonus": 0.08}, 2400),
                  ("Kiln Ring", {"immune": ["burn", "poison", "bleed"]}, 2300), ("Salt Rosary", {"mmp_mult": 1.12}, 2100)],
    "salvage":   [("Rehung Sign", {"reserve_scale": 0.03}, 3000), ("Lantern Charm", {"heal_mult": 1.12, "mp_regen": 2}, 3200),
                  ("Driftglass Ring", {"lowhp_guard": 0.2, "atb_mult": 1.05}, 3400)],
}

MATERIALS = {
    "M001": dict(name="Iron Ore", price=60, desc="Plain ore. A smith uses it for a first upgrade."),
    "M002": dict(name="Heartsteel Ore", price=240, desc="Dense ore for a second upgrade."),
    "M003": dict(name="Starmetal Ore", price=900, desc="Rare ore for a final upgrade."),
}
# smith upgrade: level -> (ore id, ore count, crowns as a fraction of the item's price, min 80)
UPGRADE = {1: ("M001", 2, 0.30), 2: ("M002", 2, 0.45), 3: ("M003", 1, 0.60)}
UPGRADE_STEP = 0.08          # +8% of the main stat per level
SMITH_SHOPS = ["SHOP_T01", "SHOP_T03", "SHOP_T07"]
ORE_STOCK = {"M001": "CH01", "M002": "CH05", "M003": "CH15"}  # stocked once this chapter is done (CH01: from the start)

PASSIVE_TEXT = {
    "lowhp_guard": "Takes {pct}% less damage below 40% HP", "mp_regen": "Restores {v} MP after each action",
    "atb_mult": "Readiness fills {pct}% faster", "mag_bonus": "+{pct}% magic power", "reserve_scale": "+{pct}% ATK/DEF per member in reserve",
    "auto_revive": "Once per battle, survives a fatal blow at 1 HP", "elem_resist": "Resists {elems}",
    "immune": "Immune to {elems}", "weapon_element": "Weapon attacks deal {v} damage", "heal_mult": "Healing received +{pct}%",
    "start_atb": "Starts battles ready", "mhp_mult": "Max HP +{pct}%", "mmp_mult": "Max MP +{pct}%", "acc_bonus": "Accuracy +{v}",
    "phys_reduce": "Physical damage -{pct}%", "encounter_mult": "Fewer random encounters", "reveal_affinity": "Shows enemy weaknesses",
}


def _lerp(a, b, f):
    return a + (b - a) * f


def passive_line(p):
    out = []
    for k, v in p.items():
        t = PASSIVE_TEXT.get(k)
        if not t:
            continue
        if k == "atb_mult" or k.endswith("_mult"):
            pct = int(round((float(v) - 1) * 100)) if k != "encounter_mult" else 0
        else:
            pct = int(round(float(v) * 100)) if isinstance(v, (int, float)) and not isinstance(v, bool) else 0
        elems = ", ".join(sorted(v)) if isinstance(v, (list, dict)) else ""
        out.append(t.format(pct=pct, v=v, elems=elems))
    return "; ".join(out)


def build(items):
    """Add the regional gear + ore to `items` (the compiled item table). Returns the added ids."""
    added = []
    for li, line in enumerate(LINE_ORDER):
        L = LINES[line]
        ta, tb, f = L["w"]
        for ci, cid in enumerate(CHARS):
            base = FIRST_WEAPON[cid]
            wa, wb = items["W%03d" % (base + ta - 1)], items["W%03d" % (base + tb - 1)]
            wid = "W%03d" % (101 + li * 8 + ci)
            p = dict(L["wp"])
            it = {"id": wid, "name": WEAPON_NAMES[line][ci], "kind": "weapon", "owner": cid, "tier": ta,
                  "atk": int(round(_lerp(wa["atk"], wb["atk"], f))), "mag": int(round(_lerp(wa["mag"], wb["mag"], f))),
                  "price": int(round(_lerp(wa["price"], wb["price"], f) / 10.0)) * 10 + 40,
                  "two_handed": wa["two_handed"], "ranged": wa["ranged"], "allowed": [cid], "sellable": True,
                  "line": line, "region": L["region"], "shop_town": L["town"], "chapter": L["chapter"]}
            if L["element"]:
                p["weapon_element"] = L["element"]
            if p:
                it["passives"] = p
            it["desc"] = passive_line(p) or "A regional make."
            items[wid] = it
            added.append(wid)
        ta, tb, f = L["a"]
        for ai, (slot, bases, allowed) in enumerate(ARMOR_BASE):
            ga, gb = items[bases[ta - 1]], items[bases[tb - 1]]
            gid = "G%03d" % (101 + li * 4 + ai)
            p = dict(L["ap"])
            it = {"id": gid, "name": ARMOR_NAMES[line][ai], "kind": "armor", "slot": slot, "allowed": list(allowed),
                  "def": int(round(_lerp(ga["def"], gb["def"], f))), "res": int(round(_lerp(ga["res"], gb["res"], f))),
                  "price": int(round(_lerp(ga["price"], gb["price"], f) / 10.0)) * 10 + 30, "tier": ta, "sellable": True,
                  "passives": p, "desc": passive_line(p), "line": line, "region": L["region"], "shop_town": L["town"],
                  "chapter": L["chapter"]}
            items[gid] = it
            added.append(gid)
        for k, (name, p, price) in enumerate(ACCESSORIES[line]):
            aid = "A%03d" % (101 + li * 3 + k)
            it = {"id": aid, "name": name, "kind": "accessory", "slot": "accessory", "price": price, "allowed": list(CHARS),
                  "sellable": True, "passives": dict(p), "desc": passive_line(p), "line": line, "region": L["region"],
                  "shop_town": L["town"], "chapter": L["chapter"]}
            items[aid] = it
            added.append(aid)
    for mid, m in MATERIALS.items():
        items[mid] = {"id": mid, "name": m["name"], "kind": "material", "price": m["price"], "desc": m["desc"], "sellable": True}
        added.append(mid)
    return added
