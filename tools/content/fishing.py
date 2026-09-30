"""Fishing (sys s4): fish, regional tables, reward items, tournament thresholds, and the `fish` map entity.

Fish icons are cells of the Mana Seed Fishing Gear 2.0 sheet (assets/ext/fishing/icons.png, 16x16, 8 per row;
the numbering follows the pack's "Fishing Gear icon reference.txt").
Weight (kg) = K * (size_cm / 10) ** 3 (K per body shape), so a size roll reads naturally in the log and the scales.
Tables: river (Crown March), coast (Glass Coast), ember (Ember Sea, Saltwhistle), fen (Mirewold), frost (Hoarfrost
March), fox (Vermilion Reach), salt (Pale Basin brine), deep (black lakes of the Deep).
Map entity:  fish X Y [table=<id>] [if=...]   X,Y is a walkable cell next to water (the player stands on or beside it
and faces the water). The table defaults to the map's region (REGION_TABLE).
"""

# id: (name, icon, tables, rarity 1-4, night, size cm [min, max], shape K, strength 1-10, reward item, value crowns, note)
FISH = {
    "F01": ("Mill Carp", 3, ["river", "fen"], 1, False, (25, 70), 0.016, 3, "Y01", 12, "Fat on the grain that falls from the mill races."),
    "F02": ("Bluegill", 12, ["river", "fox"], 1, False, (10, 24), 0.018, 2, "Y01", 6, "Every child's first fish, and most men's last."),
    "F03": ("Stripe Perch", 13, ["river", "fen"], 1, False, (15, 35), 0.014, 3, "Y01", 9, "Schools under bridges. Bites anything shiny."),
    "F04": ("Whiskered Catfish", 4, ["river", "fen", "deep"], 2, True, (40, 120), 0.011, 6, "Y01", 30, "Comes up from the silt after dark to eat what drowned."),
    "F05": ("River Chub", 11, ["river"], 1, False, (15, 40), 0.013, 2, "Y01", 7, "Bony and plentiful. The quarry cooks boil it with turnips."),
    "F06": ("Rainbow Trout", 25, ["river", "frost"], 2, False, (25, 70), 0.012, 5, "Y01", 24, "Runs the cold streams off the Skyspine."),
    "F07": ("Pike of the Weir", 18, ["river", "fen"], 3, False, (60, 130), 0.007, 7, "Y03", 70, "Waits under the weir gates like a toll-keeper."),
    "F08": ("Mudsnap Turtle", 33, ["fen", "river"], 3, False, (25, 50), 0.05, 6, "Y03", 60, "Bites the line, the hook and the hand, in that order."),
    "F09": ("Bog Frog", 32, ["fen"], 1, True, (8, 20), 0.03, 1, "Y02", 5, "Not a fish. The guild counts it anyway."),
    "F10": ("Crayfish", 41, ["fen", "river", "deep"], 1, False, (8, 18), 0.02, 1, "Y01", 6, "Plague-town children sell them by the bucket."),
    "F11": ("Gibbet Eel", 24, ["fen", "coast"], 2, True, (50, 140), 0.003, 6, "Y02", 28, "Feeds under the gibbet roads. Nobody asks on what."),
    "F12": ("Sturgeon Elder", 17, ["fen", "deep", "frost"], 4, False, (120, 260), 0.006, 9, "Y05", 320, "Older than the quarantine walls. Its roe buys a house."),
    "F13": ("Sea Bass", 5, ["coast", "ember"], 1, False, (30, 80), 0.014, 4, "Y01", 18, "The Bellharbor staple, grilled on bell-tower coals."),
    "F14": ("Red Snapper", 6, ["coast", "ember"], 2, False, (30, 90), 0.016, 5, "Y01", 30, "Red as a Crown tax notice, and more welcome."),
    "F15": ("Garfish", 10, ["coast", "ember"], 1, False, (40, 90), 0.002, 3, "Y03", 10, "All teeth and no meat."),
    "F16": ("Mackerel", 23, ["coast", "ember"], 1, False, (20, 45), 0.01, 3, "Y01", 8, "They come in thousands, or not at all."),
    "F17": ("Anchovy", 22, ["coast", "ember", "salt"], 1, False, (8, 18), 0.008, 1, "Y02", 3, "Salted by the barrel for the capital's poor."),
    "F18": ("Pufferfish", 21, ["coast", "ember"], 2, False, (15, 40), 0.04, 3, "Y03", 26, "Cooked right, a delicacy. Cooked wrong, a funeral."),
    "F19": ("Clownfish", 27, ["ember"], 2, False, (6, 12), 0.02, 1, "Y03", 20, "Lives in the reef's poison and laughs about it."),
    "F20": ("Lionfish", 28, ["ember", "coast"], 3, False, (20, 45), 0.02, 5, "Y03", 55, "Its spines sting for a week. Sailors keep them as warnings."),
    "F21": ("Mahi-Mahi", 9, ["ember"], 2, False, (60, 150), 0.006, 7, "Y01", 60, "Chases the boats in the Ember Sea's warm lanes."),
    "F22": ("Bluefin Tuna", 7, ["ember", "coast"], 3, False, (100, 220), 0.012, 8, "Y01", 150, "The guild's pride. The Crown taxes it twice."),
    "F23": ("Ember Marlin", 8, ["ember"], 4, False, (180, 330), 0.004, 10, "Y04", 400, "The Saltwhistle legend. Fights for an hour, forgives nothing."),
    "F24": ("Manta Ray", 20, ["ember", "coast"], 3, True, (120, 300), 0.004, 8, "Y03", 180, "Glides under the pontoons at night like a second shadow."),
    "F25": ("Mako Shark", 19, ["ember"], 4, True, (150, 320), 0.005, 10, "Y04", 360, "Takes the catch, the line, and sometimes the fisher."),
    "F26": ("Seahorse", 30, ["coast", "fox"], 2, False, (6, 15), 0.02, 1, "Y03", 22, "Glass Coast scholars keep them in reading-room jars."),
    "F27": ("Starfish", 31, ["coast", "salt"], 1, False, (10, 30), 0.01, 1, "Y03", 5, "It comes up holding the hook like a gift."),
    "F28": ("Hermit Crab", 34, ["coast", "salt"], 1, False, (5, 15), 0.03, 1, "Y01", 6, "Moves house more often than a debtor."),
    "F29": ("Tide Lobster", 40, ["coast", "ember"], 2, True, (25, 60), 0.02, 4, "Y01", 45, "Walks the tide shelf at night. Worth a week's wages."),
    "F30": ("Reef Octopus", 44, ["ember", "coast"], 3, True, (40, 120), 0.004, 6, "Y02", 90, "Opens the bait tin, eats the bait, closes the tin."),
    "F31": ("Glass Squid", 45, ["coast", "deep"], 2, True, (30, 80), 0.004, 4, "Y02", 35, "You can read the tide tables through it."),
    "F32": ("Bell Jellyfish", 46, ["coast", "ember"], 2, False, (20, 50), 0.004, 2, "Y02", 18, "Rings, faintly, if you hold it to your ear. Don't."),
    "F33": ("Lantern Koi", 0, ["fox"], 2, False, (30, 80), 0.014, 4, "Y03", 50, "The fox court breeds them to swim under the lantern rivers."),
    "F34": ("Court Goldfish", 1, ["fox"], 1, False, (8, 25), 0.02, 1, "Y01", 15, "Escaped from a noble's pond. Proud about it."),
    "F35": ("Shrine Betta", 2, ["fox"], 3, True, (6, 12), 0.02, 3, "Y03", 70, "Fights its own reflection in the shrine basins."),
    "F36": ("Maple Salmon", 16, ["fox", "frost"], 2, False, (50, 100), 0.01, 6, "Y01", 40, "Runs red up the maple rivers every autumn."),
    "F37": ("Angelfish", 15, ["fox", "coast"], 2, False, (10, 25), 0.03, 2, "Y03", 25, "Too pretty to eat. People eat it anyway."),
    "F38": ("Brine Tilapia", 14, ["salt"], 1, False, (15, 40), 0.016, 2, "Y01", 9, "Lives in the salt pools where nothing should."),
    "F39": ("Salt Shrimp", 42, ["salt", "coast"], 1, False, (4, 10), 0.02, 1, "Y02", 4, "Pink and crunchy. The basin cooks fry them whole."),
    "F40": ("Mineral Clam", 38, ["salt", "coast"], 2, False, (6, 14), 0.06, 1, "Y05", 40, "Sometimes a pearl. Usually a grain of salt."),
    "F41": ("Frost Bream", 26, ["frost"], 1, False, (20, 45), 0.018, 3, "Y01", 12, "Caught through the ice. Tastes of the cold."),
    "F42": ("Blind Angler", 29, ["deep"], 3, False, (20, 60), 0.02, 6, "Y03", 90, "Its lamp is the only light in the black lakes."),
    "F43": ("Deep Sea Slug", 47, ["deep", "coast"], 1, True, (5, 20), 0.01, 1, "Y02", 8, "Glows faintly, then stops. Nobody knows which is worse."),
    "F44": ("Sepulchre Pearl Oyster", 37, ["deep", "salt"], 4, True, (8, 18), 0.08, 2, "Y05", 250, "The dead's lake grows pearls in the dark."),
}

# junk (any table, small chance)
JUNK = {"J01": ("Old Boot", 60, "Y06"), "J02": ("Message in a Bottle", 61, "Y07")}

REGION_TABLE = {"R01": "river", "R02": "river", "R03": "coast", "R04": "river", "R05": "salt", "R06": "ember",
                "R07": "fox", "R08": "fen", "R09": "frost", "SKY": "coast"}
TABLES = ["river", "coast", "ember", "fen", "frost", "fox", "salt", "deep"]

RARITY_WEIGHT = {1: 60, 2: 26, 3: 10, 4: 3}

# Saltwhistle Open: rank by the weight (kg) of a single catch taken at Saltwhistle during the tournament
TOURNEY = {"map_zone": "N14", "gold": 18.0, "silver": 8.0, "bronze": 3.0}

# reward items (ids sort after every existing item, so the icon sheet indices of older items never move)
ITEMS = {
    "Y01": {"name": "Fish Fillet", "kind": "consumable", "price": 40, "desc": "Fresh-caught and grilled. Restores 180 HP to one ally.",
            "target": "ally_one", "ops": [{"op": "heal", "flat": 180}], "battle": True, "field": True, "icon_fish": 48},
    "Y02": {"name": "Silver Roe", "kind": "consumable", "price": 90, "desc": "Salted roe. Restores 30 MP to one ally.",
            "target": "ally_one", "ops": [{"op": "mp", "amount": 30}], "battle": True, "field": True, "icon_fish": 53},
    "Y03": {"name": "Fish Scales", "kind": "material", "price": 60, "desc": "Hard, bright scales. Smiths and crafters pay for them.", "icon_fish": 50},
    "Y04": {"name": "Shark Tooth", "kind": "material", "price": 300, "desc": "A tooth as long as a finger. Worth a great deal to a crafter.", "icon_fish": 51},
    "Y05": {"name": "Pearl", "kind": "material", "price": 800, "desc": "A pearl from the deep water. Sells for a fortune.", "icon_fish": 39},
    "Y06": {"name": "Old Boot", "kind": "material", "price": 2, "desc": "Somebody's. Once.", "icon_fish": 60},
    "Y07": {"name": "Bottled Message", "kind": "material", "price": 100, "desc": "A letter nobody answered. The ink has run.", "icon_fish": 61},
    "Y08": {"name": "Waylamp", "kind": "consumable", "price": 400,
            "desc": "A shuttered lamp lit from a save lamp's flame. Opens the save ledger anywhere outside battle and boss rooms.",
            "target": "party", "ops": [], "battle": False, "field": True, "special": "save_lantern", "icon_fish": 58},
}
# the portable save item in 3 shops
LANTERN_SHOPS = ["SHOP_T02", "SHOP_N14", "SHOP_N43"]


def apply(content, err):
    fish = {}
    for fid, r in FISH.items():
        name, icon, tables, rar, night, size, k, strength, reward, value, note = r
        for t in tables:
            if t not in TABLES:
                err(f"fish {fid}: unknown table {t}")
        if reward not in ITEMS:
            err(f"fish {fid}: unknown reward {reward}")
        fish[fid] = {"id": fid, "name": name, "icon": icon, "tables": tables, "rarity": rar, "night": night,
                     "size": list(size), "k": k, "strength": strength, "reward": reward, "value": value, "note": note}
    junk = {jid: {"id": jid, "name": n, "icon": ic, "reward": rw} for jid, (n, ic, rw) in JUNK.items()}
    for t in TABLES:
        if not any(t in f["tables"] for f in fish.values()):
            err(f"fishing table {t} has no fish")
    content["fishing"] = {"fish": fish, "junk": junk, "tables": TABLES, "region_table": REGION_TABLE,
                          "rarity_weight": {str(k): v for k, v in RARITY_WEIGHT.items()}, "tourney": TOURNEY}
    nxt = max(int(i.get("icon", -1)) for i in content["items"].values()) + 1
    for iid, it in sorted(ITEMS.items()):
        d = {"id": iid, "sellable": True, "revive": False, "special": "", "allowed": []}
        d.update(it)
        if iid not in content["items"]:
            d["icon"] = nxt          # atlas cell after every existing item (drawn from the fishing sheet when installed)
            nxt += 1
        content["items"][iid] = d
    for sid in LANTERN_SHOPS:
        if sid in content["shops"]:
            content["shops"][sid].setdefault("extra", [])
            if "Y08" not in content["shops"][sid]["extra"]:
                content["shops"][sid]["extra"].append("Y08")
        else:
            err(f"lantern shop {sid} missing")
    # fish spots: resolve default tables, check the cell is next to water
    water = {"water", "shallow", "deep", "pool", "lava", "reef", "puddle"}
    for mid, m in content["maps"].items():
        for e in m["entities"]:
            if e["type"] != "fish":
                continue
            if not e.get("table"):
                e["table"] = REGION_TABLE.get(m.get("region", ""), "river")
            if e["table"] not in TABLES:
                err(f"{mid}: fish spot table {e['table']} unknown")
            wet = [(dx, dy) for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0))
                   if 0 <= e["x"] + dx < m["w"] and 0 <= e["y"] + dy < m["h"]
                   and m["legend"].get(m["grid"][e["y"] + dy][e["x"] + dx], "") in water]
            if not wet:
                err(f"{mid}: fish spot ({e['x']},{e['y']}) has no water beside it")
            else:
                e["water"] = list(wet[0])
    return content


def boss_rooms(content):
    """Maps where a boss fight waits (a trigger/talk scene fights a boss formation): the Waylamp does not burn there."""
    forms = content["formations"]["formations"]
    boss_scenes = set()
    for sid, sc in content["scenes"].items():
        for c in sc["cmds"]:
            if c["c"] == "battle" and c["a"] and forms.get(c["a"][0], {}).get("boss", False):
                boss_scenes.add(sid)
    for mid, m in content["maps"].items():
        if any(e.get("scene") in boss_scenes or e.get("talk") in boss_scenes for e in m["entities"]):
            m["boss_room"] = True
