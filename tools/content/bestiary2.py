"""Expansion bestiary: 80 new regular enemies (E041-E120) for the new regions, the Deep, the undersea and night.

Each row: id, name, home (region/realm group, see docs/expansion/WORLD_V2.md), level, weakness, art code
(tools/art/enemy_roster.py codes), size class, flip, archetype, element, tags, behaviour line, bestiary lore.
`apply(content_catalog, EN)` adds the catalog rows and runtime behaviours; `ROSTER` feeds the art pipeline;
`GROUPS` holds encounter groups by region, terrain and time of day (world maps pick them up by zone).
"""

S, M, L = 34, 46, 60

# id, name, home, lv, weak, art, size, flip, arch, elem, tags, behaviour, lore
ROWS = [
    # ---- R01 Crown March (surface, early; Sunken Chapel N04; night) ----
    ("E041", "Mill Rat Swarm", "R01", 4, "fire", "F:Trash_Rat", S, 0, "swarm", "physical", [], "Three quick nibbles on random targets.",
     "Fat on Crown grain. Where they nest, the tithe was never paid."),
    ("E042", "Toll Hound", "R01", 5, "fire", "M1:101", M, 1, "hunter", "physical", [], "Marks, then lunges; weak to fire.",
     "Bred at Gallowgate to sniff out undeclared cargo. Some of the cargo was children."),
    ("E043", "Orchard Wisp", "R01", 6, "shadow", "b1", M, 0, "caster", "light", ["flying"], "Blinding flare, then a soft light bolt.",
     "The pickers say the wisps are last year's harvest workers, still counting apples."),
    ("E044", "Drowned Oathknight", "N04", 9, "storm", "M:075", L, 0, "brute", "water", ["undead"], "Heavy blade; telegraphs a cleave.",
     "Knights who swore to hold the chapel against the flood. They kept the oath."),
    ("E045", "Chapel Mimic", "N04", 10, "light", "M:022", M, 0, "brute", "shadow", [], "Snaps shut for massive damage, then rests.",
     "The offering chest learned to feed itself."),
    ("E046", "Barrow Wight", "R01", 12, "light", "M:055", M, 0, "drainer", "shadow", ["undead"], "Drains HP; appears at night.",
     "Buried with a crown of tin. It remembers being told it was gold."),
    # ---- R02 Cinder Reach (Slagfalls N07, Weeping Dam N42) ----
    ("E047", "Slag Crawler", "R02", 11, "ice", "F:Rust_Slug", S, 0, "tank", "fire", [], "Hardens; burns on contact.",
     "Ate the slag heaps behind Kettle Row and kept growing."),
    ("E048", "Pipe Viper", "R02", 12, "ice", "b79", M, 1, "skirmisher", "fire", [], "Two fast burning bites.",
     "Nests in warm pipe. The fitters leave it milk and a spanner."),
    ("E049", "Scrap Bandit", "R02", 13, "storm", "F:Scrap_Bandit", M, 0, "thief", "physical", [], "Steals, then flees at low HP.",
     "Lost a shift, then a house, then a name. Took up the only trade that was hiring."),
    ("E050", "Cinder Imp", "N07", 14, "water", "M:120", S, 0, "caster", "fire", ["flying"], "Fire bolts; absorbs fire.",
     "It laughs in the voice of whichever worker it burned last."),
    ("E051", "Magma Golem", "N07", 16, "water", "M:041", L, 0, "brute", "fire", [], "Slow molten punch; weak to water.",
     "Poured into a mould shaped like a man, and it never cooled."),
    ("E052", "Dam Leech", "N42", 15, "storm", "b64", S, 0, "drainer", "water", [], "Latches on and drains.",
     "The dam wept for years. These are what it wept."),
    # ---- R03 Glass Coast (Brine Stair N13) + R06 Ember Sea isles ----
    ("E053", "Wreck Crab", "R03", 15, "storm", "M:141", M, 0, "tank", "water", [], "Shell up, then a pincer crush.",
     "Its shell is a customs lockbox. Nobody has the key."),
    ("E054", "Gull Harpy", "R03", 16, "storm", "M:093", M, 1, "skirmisher", "physical", ["flying"], "Swoops twice at the back row.",
     "Steals shining things from the drowned. Sometimes rings; sometimes teeth."),
    ("E055", "Brine Naga", "N13", 18, "storm", "M:035", L, 0, "caster", "water", [], "Tidal wave on a row; slow gaze.",
     "Keeper of the sea-caves. She lets the tide decide who leaves."),
    ("E056", "Siren of the Stair", "N13", 19, "storm", "M:252", M, 0, "charmer", "water", [], "Sleep song, then a drowning strike.",
     "Sings the names of sailors in their mothers' voices."),
    ("E057", "Reef Shark", "R06", 20, "storm", "M:262", M, 1, "hunter", "water", [], "Circles and bites the wounded.",
     "Follows the ferry lanes. It has learned what a capsized hull means."),
    ("E058", "Isle Toad", "R06", 18, "fire", "b72", S, 0, "poisoner", "poison", [], "Poison spit.",
     "Its croak rings like a bell. Smugglers use it to time the watch."),
    # ---- R04 Skyspine (Eyrie Hollow N18) ----
    ("E059", "Cliff Griffon", "R04", 20, "storm", "M:241", L, 1, "skirmisher", "physical", ["flying"], "Dive attack; hard to hit.",
     "The aerie guard once rode them. Now they ride the wind alone."),
    ("E060", "Roc Chick", "N18", 21, "storm", "M:172", M, 0, "swarm", "physical", ["flying"], "Pecks; calls its parent.",
     "Big as a cart and still hungry."),
    ("E061", "Frost Yeti", "R04", 22, "fire", "M:077", L, 0, "brute", "ice", [], "Ice slam on the front row.",
     "Shepherds leave it one ewe each winter. It leaves the rest."),
    ("E062", "Wind Sprite", "R04", 21, "earth", "M:042", S, 0, "caster", "storm", ["flying"], "Gust knocks targets back a row.",
     "Born in the ninefold shrine's cloths, it chases prayers down the cliff."),
    # ---- R05 Pale Basin (Sorrowmere N21) ----
    ("E063", "Salt Wraith", "R05", 24, "light", "M:286", M, 0, "drainer", "shadow", ["undead"], "Drains MP; fades in and out.",
     "The salt keeps what the water forgets. It kept her."),
    ("E064", "Memory Moth", "N21", 25, "fire", "M:216", S, 0, "charmer", "light", ["flying"], "Confusing dust; steals a buff.",
     "Drinks the lake's drowned memories and leaves the drinkers empty."),
    ("E065", "Mere Maw", "N21", 27, "storm", "M:237", L, 0, "brute", "water", [], "Tentacle sweep on a row.",
     "The lake's mouth. Sorrowmere's villagers called it Grandmother."),
    ("E066", "Crystal Stalker", "R05", 26, "earth", "M:212", M, 0, "hunter", "light", [], "Marks, then a refracted strike.",
     "Hunts by reflection. Stand still and it sees a hundred of you."),
    # ---- R08 Mirewold (Harrowfen N22, Leech Cathedral N25, Gibbet Road N23) ----
    ("E067", "Blight Grub", "R08", 17, "fire", "b0", M, 0, "poisoner", "poison", [], "Poison spit; slow.",
     "Fattened on the quarantine pits. The fen folk say it hums the plague bell's note."),
    ("E068", "Fen Lurker", "R08", 18, "fire", "b25", M, 0, "hunter", "water", [], "Drags a target into the water (stun).",
     "It waits under the causeway boards for the quarantine carts."),
    ("E069", "Gibbet Crow", "N23", 18, "storm", "M:173", S, 0, "swarm", "shadow", ["flying"], "Pecks the lowest HP ally.",
     "They learned the gallows bell means supper."),
    ("E070", "Quarantine Warden", "N22", 20, "storm", "b30", L, 0, "tank", "physical", [], "Shields allies; seals exits.",
     "An empty suit of plague armour still walking its post. The order was never lifted."),
    ("E071", "Leech Acolyte", "N25", 21, "fire", "b92", M, 0, "healer", "shadow", [], "Heals allies with stolen blood.",
     "The Order sold the cure by the pint. Its acolytes kept the change."),
    ("E072", "Bog Hag", "R08", 22, "light", "b16", M, 0, "charmer", "poison", [], "Curses: weaken and poison.",
     "She sold charms against the plague. Some of them worked, which was worse."),
    ("E073", "Rotting Reaper", "N25", 23, "fire", "M:054", L, 0, "brute", "shadow", ["undead"], "Scythe sweep; doom on a crit.",
     "Cathedral's gravedigger. It stopped waiting for the bodies to arrive."),
    # ---- R07 Vermilion Reach (Akagane N28, Thousand Gates N29, Whispering Maples N30) ----
    ("E074", "Lantern Tanuki", "R07", 24, "water", "b2", M, 0, "thief", "fire", [], "Steals, then disguises itself (evasion).",
     "Brings its own lantern to a fight. Takes yours when it leaves."),
    ("E075", "Masked Ronin", "R07", 25, "storm", "b23", M, 1, "duelist", "physical", [], "Counter stance, then a quick draw.",
     "Served the fox court before the exile. Now he serves whoever pays in rice."),
    ("E076", "Foxfire Kit", "N30", 26, "water", "M:158", S, 0, "caster", "fire", [], "Illusory fire on a random target.",
     "The fox wedding's lanterns, walking home without the bride."),
    ("E077", "Gate Oni", "N29", 27, "light", "M:015", L, 0, "brute", "fire", [], "Club smash; enrages below half HP.",
     "Each of the thousand gates has a keeper. This one has forgotten which gate."),
    ("E078", "Paper Spirit", "N29", 26, "fire", "b27", M, 0, "charmer", "shadow", ["flying"], "Silence and confusion.",
     "A petition folded into a man. It keeps asking the court to read it."),
    ("E079", "Moss Monk", "R07", 25, "fire", "b20", M, 0, "healer", "earth", [], "Regen on allies; root grip.",
     "Sat in meditation so long the forest took him for a stone."),
    ("E080", "Maple Serpent", "N30", 28, "ice", "M:169", L, 1, "hunter", "earth", [], "Coils (stun), then crushes.",
     "Red as autumn and patient as winter."),
    # ---- R09 Hoarfrost March (Glacier Spire N34, Coldharbour N35) ----
    ("E081", "Frost Wolf", "R09", 28, "fire", "M:166", M, 1, "hunter", "ice", [], "Pack bite; stronger in pairs.",
     "The tundra's last hunters. They follow the Lich King's cold like a shepherd."),
    ("E082", "Rime Bear", "R09", 29, "fire", "M:081", L, 0, "brute", "ice", [], "Ice claw; roars (weaken all).",
     "Sleeps a hundred days and wakes angry about all of them."),
    ("E083", "Ice Maiden", "N34", 30, "fire", "M:084", M, 0, "caster", "ice", [], "Blizzard on all; freezes (slow).",
     "The spire's first climber. She reached the top."),
    ("E084", "Frozen Legionary", "N35", 31, "fire", "M:083", L, 0, "tank", "ice", ["undead"], "Shield wall; guards allies.",
     "Part of a court that died of cold. Still in rank, still waiting for orders."),
    ("E085", "Glacier Drake", "N34", 32, "fire", "M:080", L, 1, "brute", "ice", ["flying"], "Frost breath on a row.",
     "Wings of cracked ice. It sheds a small glacier every spring."),
    ("E086", "Hoarfrost Wisp", "R09", 29, "fire", "M:086", S, 0, "caster", "ice", ["flying"], "Freezing touch.",
     "The breath of someone who died on the Ice Road."),
    # ---- SKY Shattered Choir (Seraphel N39) ----
    ("E087", "Choir Seraph", "SKY", 33, "shadow", "M:185", M, 0, "healer", "light", ["flying"], "Heals, then a hymn of light.",
     "Sings the last order the host received. It no longer knows what it means."),
    ("E088", "Fallen Cherub", "SKY", 32, "shadow", "M:246", S, 0, "swarm", "light", ["flying"], "Arrow volley.",
     "Too small to fall far. It fell anyway."),
    ("E089", "Host Sentinel", "N39", 35, "shadow", "M:188", L, 0, "tank", "light", [], "Judgement: damages attackers.",
     "Guards a throne that stopped answering thirty years ago."),
    ("E090", "Sky Wyvern", "SKY", 34, "ice", "M:143", L, 1, "skirmisher", "storm", ["flying"], "Tail sting (poison), dive.",
     "Nests in the host's broken organ pipes. Its cry is a flat note."),
    # ---- U1 Emberdeep (dragon under-realm) ----
    ("E091", "Geode Scuttler", "U1", 20, "earth", "M:236", S, 0, "tank", "earth", [], "Crystal shell; reflects magic once.",
     "Grows jewels on its back. The delvers farm them, carefully."),
    ("E092", "Delver Deserter", "U1", 21, "storm", "M:067", M, 0, "thief", "physical", [], "Steals ore; throws a pick.",
     "Ran from King Horrach's debt. Now he owes the dark instead."),
    ("E093", "Magma Salamander", "U1", 22, "water", "M:092", M, 0, "skirmisher", "fire", [], "Burning tail lash.",
     "Swims the lava rivers. The magma ferrymen tip it in copper."),
    ("E094", "Bone Drakeling", "U1", 24, "light", "M:091", M, 0, "brute", "fire", ["undead"], "Ashen breath on a row.",
     "Hatched from an egg left in a dragon's ossuary. It thinks the bones are its mother."),
    ("E095", "Crown Digger", "U1", 23, "storm", "b34", L, 0, "brute", "physical", [], "Drill charge (telegraphed).",
     "The Crown's mining suits, still digging after their crews ran."),
    ("E096", "Fungal Shambler", "U1", 22, "fire", "M:287", M, 0, "poisoner", "poison", [], "Spore cloud: poison and sleep.",
     "The fungal terraces grow their own farmhands."),
    ("E097", "Ember Bat", "U1", 21, "ice", "M:048", S, 0, "swarm", "fire", ["flying"], "Diving bites.",
     "Roosts in the heat above the magma and drops like sparks."),
    ("E098", "Scale Wraith", "U1", 26, "light", "M:217", M, 0, "drainer", "shadow", ["undead"], "Drains; curses a dragonborn ally.",
     "A dragonborn who died unbound. Its fragment never found a home."),
    # ---- U2 The Lattice (builder cities) ----
    ("E099", "Keeper Drone", "U2", 29, "storm", "b56", M, 0, "healer", "none", [], "Repairs machine allies.",
     "Still maintains a city nobody lives in."),
    ("E100", "Sawblade Skitterer", "U2", 30, "storm", "F:Sawblade_Skitterer", M, 0, "skirmisher", "physical", [], "Bleeding cuts.",
     "A floor cleaner that found out what else it could cut."),
    ("E101", "Volt Turret", "U2", 31, "earth", "F:Defective_Turret", M, 0, "caster", "storm", [], "Charged beam (interruptible).",
     "Its target list was last updated when the builders were alive."),
    ("E102", "Assembly Walker", "U2", 32, "storm", "b39", L, 0, "tank", "physical", [], "Braces allies; stomps a row.",
     "Built to carry the builders. It still waits at the stops."),
    ("E103", "Junk Golem", "U2", 30, "storm", "F:Junk_Bot", M, 0, "brute", "physical", [], "Scrap fling; self-repairs.",
     "Assembled itself from the parts of its friends."),
    ("E104", "Magnet Maw", "U2", 33, "earth", "F:Magnet_Maw", L, 0, "charmer", "storm", [], "Pulls weapons (weaken), then bites.",
     "Eats anything iron. It has a taste for Crown steel."),
    ("E105", "Datum Ghost", "U2", 34, "light", "b84", M, 0, "caster", "shadow", ["flying"], "Scan, then a targeted curse.",
     "A builder's record that kept running after its person stopped."),
    ("E106", "Chrome Hound", "U2", 32, "storm", "b62", M, 0, "hunter", "physical", [], "Locks on (mark) and pounces.",
     "The Lattice's watchdogs. CURATOR taught them what an intruder smells like."),
    # ---- U3 The Hollow Throne (realm of the dead) ----
    ("E107", "Mourning Shade", "U3", 36, "light", "M:291", M, 0, "drainer", "shadow", ["undead"], "Drains; weeps (slow).",
     "Carries its own grave-candle. It will not say whose."),
    ("E108", "Bone Knight", "U3", 38, "light", "M:073", L, 0, "tank", "physical", ["undead"], "Shield wall; counter.",
     "Mother Sepulchre pays her soldiers in the dead. They are always paid."),
    ("E109", "Grave Lich", "U3", 40, "light", "M:057", M, 0, "caster", "shadow", ["undead"], "Doom on one target; dark wave.",
     "A priest who bargained for one more year. Then one more."),
    ("E110", "Ferryman's Hound", "U3", 38, "light", "M:167", M, 1, "hunter", "shadow", ["undead"], "Three-headed bite on random targets.",
     "Guards Styx Landing. It lets the living in. It is the leaving it minds."),
    ("E111", "Abyss Valkyrie", "U3", 41, "light", "b87", M, 0, "duelist", "shadow", [], "Spear dive; brands a soul (mark).",
     "Inferna's former sisters. They still collect."),
    ("E112", "Coffin Mimic", "U3", 39, "light", "M:025", M, 0, "brute", "shadow", [], "Swallow (stun) and chew.",
     "In Cenotaph even the coffins are hungry."),
    ("E113", "Weeping Miner", "U3", 37, "light", "M:072", M, 0, "swarm", "earth", ["undead"], "Pick strikes.",
     "Still digging. The seam they want is their own names."),
    # ---- SEA undersea (post) ----
    ("E114", "Abyss Angler", "SEA", 36, "storm", "M:222", M, 0, "charmer", "water", [], "Lure light (blind), then bite.",
     "Its lantern is a drowned lighthouse keeper's lamp."),
    ("E115", "Drowned Citizen", "SEA", 35, "storm", "M:268", M, 0, "swarm", "water", ["undead"], "Grasping hands.",
     "Old Bellharbor never evacuated its lower streets."),
    ("E116", "Reef Titan", "SEA", 38, "storm", "M:090", L, 0, "tank", "water", [], "Shell up; tidal slam.",
     "The reef grew on its back while it slept. It woke up an island."),
    ("E117", "Kraken Spawn", "SEA", 37, "storm", "M:270", L, 0, "brute", "water", [], "Tentacle sweep; ink (blind).",
     "Young, which is to say only the size of a ferry."),
    # ---- NIGHT rares (surface, any region at night) ----
    ("E118", "Night Mare", "NIGHT", 20, "light", "M:249", L, 0, "charmer", "shadow", ["rare"], "Nightmare: sleep and doom.",
     "Runs only on moonless roads. Travellers who see it never finish the journey the same."),
    ("E119", "Gilded Tanuki", "NIGHT", 25, "water", "b2", M, 0, "thief", "light", ["rare"], "Flees quickly; drops treasure.",
     "Its coins turn to leaves at dawn. Spend them fast."),
    ("E120", "Wandering Armor", "NIGHT", 30, "storm", "b31", L, 0, "tank", "physical", ["rare", "undead"], "Walks between regions at night.",
     "A suit of the old Crown's armour that forgot which war it was in."),
]

HP_PER_LEVEL = 36.0


def _moves(arch, elem, mv, dmg, st):
    e = None if elem in ("physical", "none") else elem
    typ = "magical" if arch in ("caster", "charmer", "healer") else "physical"
    A = {}
    if arch == "swarm":
        A = {"a": mv("Flurry", [dmg(55), dmg(55)], element=elem)}
        return A, ["a"]
    if arch == "hunter":
        A = {"mark": mv("Mark Prey", [st("mark", 100, 2)], anim="step", element="none"),
             "lunge": mv("Lunge", [dmg(140, "physical", e)], target="marked", element=elem)}
        return A, ["mark", "lunge", "lunge"]
    if arch == "brute":
        A = {"hit": mv("Heavy Blow", [dmg(115, "physical", e)], element=elem),
             "smash": mv("Crushing Smash", [dmg(190, "physical", e)], charge=2.0, tell="Winding up a crushing blow", element=elem)}
        return A, ["hit", "hit", "smash"]
    if arch == "caster":
        A = {"bolt": mv("Bolt", [dmg(125, "magical", e)], anim="cast", element=elem),
             "wave": mv("Wave", [dmg(80, "magical", e)], target="all", anim="cast", element=elem, charge=1.5, tell="Gathering power")}
        return A, ["bolt", "bolt", "wave"]
    if arch == "tank":
        A = {"guard": mv("Brace", [{"op": "guard_self", "mult": 0.5, "label": "braced"}], target="self", anim="guard"),
             "slam": mv("Slam", [dmg(120, "physical", e)], element=elem)}
        return A, ["slam", "guard", "slam"]
    if arch == "drainer":
        A = {"drain": mv("Drain", [dmg(100, typ, e, drain=True)], element=elem),
             "sap": mv("Sap Will", [{"op": "mp_drain", "amount": 12}], anim="cast", element="none")}
        return A, ["drain", "sap", "drain"]
    if arch == "healer":
        A = {"heal": mv("Mend", [{"op": "heal", "power": 55}], target="ally_lowest", anim="cast"),
             "hit": mv("Smite", [dmg(105, "magical", e)], anim="cast", element=elem)}
        return A, ["hit", "heal", "hit"]
    if arch == "poisoner":
        A = {"spit": mv("Toxic Spit", [dmg(70, "physical", e), st("poison", 85, 3)], element=elem),
             "bite": mv("Bite", [dmg(100)])}
        return A, ["spit", "bite"]
    if arch == "charmer":
        A = {"hex": mv("Hex", [st("sleep" if elem in ("water", "light") else "blind", 70, 2)], anim="cast", element="none"),
             "hit": mv("Strike", [dmg(115, "magical", e)], anim="cast", element=elem)}
        return A, ["hex", "hit", "hit"]
    if arch == "thief":
        A = {"steal": mv("Pilfer", [{"op": "steal_gold"}, dmg(70)]),
             "hit": mv("Stab", [dmg(105)])}
        return A, ["steal", "hit"]
    if arch == "skirmisher":
        A = {"a": mv("Double Strike", [dmg(75, "physical", e), dmg(75, "physical", e)], element=elem)}
        return A, ["a"]
    if arch == "duelist":
        A = {"stance": mv("Counter Stance", [{"op": "guard_self", "mult": 0.4, "label": "stance"}], target="self", anim="guard"),
             "draw": mv("Quick Draw", [dmg(165, "physical", e)], target="lowest_hp", element=elem)}
        return A, ["stance", "draw"]
    raise ValueError(arch)


SHAPE = {"swarm": "rat", "hunter": "hound", "brute": "golem", "caster": "wisp", "tank": "shell", "drainer": "leech",
         "healer": "singer", "poisoner": "mite", "charmer": "moth", "thief": "imp", "skirmisher": "viper", "duelist": "knight"}
MODS = {"swarm": {"spd": 1.3, "hp": 0.8}, "hunter": {"spd": 1.2}, "brute": {"hp": 1.3, "spd": 0.8, "def": 1.2},
        "caster": {"res": 1.3, "def": 0.8}, "tank": {"def": 1.6, "hp": 1.2, "spd": 0.8}, "drainer": {}, "healer": {"res": 1.2},
        "poisoner": {}, "charmer": {"res": 1.2}, "thief": {"spd": 1.4, "hp": 0.8}, "skirmisher": {"spd": 1.3},
        "duelist": {"spd": 1.1, "def": 1.1}}

ROSTER = {r[0]: (r[5], r[6], r[7]) for r in ROWS}
LORE = {r[0]: r[12] for r in ROWS}


def catalog_rows():
    return [{"id": r[0], "name": r[1], "home": r[2], "level": r[3], "hp": int(round(HP_PER_LEVEL * r[3] + 60)),
             "weakness": r[4], "behavior": r[11]} for r in ROWS]


def apply(cat_enemies, EN):
    have = {e["id"] for e in cat_enemies}
    for row in catalog_rows():
        if row["id"] not in have:
            cat_enemies.append(row)
    for r in ROWS:
        moves, cycle = _moves(r[8], r[9], EN.mv, EN.dmg, EN.st)
        aff = {}
        if r[9] not in ("physical", "none"):
            aff[r[9]] = "absorb" if r[8] == "caster" else "resist"
        EN.E[r[0]] = dict(shape=SHAPE[r[8]], moves=moves, cycle=cycle, mods=MODS[r[8]], aff=aff, tags=list(r[10]))


# Encounter groups by home. Formations are built per group: 1-3 enemies of the home, levels from the rows.
def groups():
    by = {}
    for r in ROWS:
        by.setdefault(r[2], []).append(r[0])
    return by


def apply_formations(FM):
    """Adds encounter formations OWX_<home>_<n> and groups OWX_<home> (world zones and dungeons use these)."""
    import itertools
    bg = {"R01": "field_r01", "N04": "grove_flood", "R02": "furnace", "N07": "furnace", "N42": "underways", "R03": "reef",
          "N13": "reef", "R06": "reef", "R04": "sky", "N18": "sky", "R05": "field_r05", "N21": "vault", "R08": "grove_flood",
          "N22": "field_post", "N23": "field_post", "N25": "whitebone", "R07": "grove", "N29": "crown", "N30": "grove",
          "R09": "winter", "N34": "winter", "N35": "winter", "SKY": "sky", "N39": "crown_core", "U1": "furnace",
          "U2": "vault", "U3": "whitebone", "SEA": "reef", "NIGHT": "field_post"}
    by = groups()
    lv = {r[0]: r[3] for r in ROWS}
    size = {r[0]: r[6] for r in ROWS}
    for home, ids in by.items():
        forms = []
        for i, a in enumerate(ids):
            n = 1 if size[a] >= L else (2 if size[a] >= M else 3)
            forms.append([a] * n)
        for a, b in itertools.combinations(ids, 2):
            if size[a] + size[b] <= M + L:
                forms.append([a, b])
        names = []
        for k, f in enumerate(forms[:8]):
            fid = "OWX_%s_%d" % (home, k + 1)
            FM.FORMATIONS[fid] = FM.F([FM.v(e, lv[e]) for e in f], bg.get(home, "field_r01"))
            names.append(fid)
        FM.GROUPS["OWX_" + home] = names


POST_LEVEL = {"R01": 28, "R02": 30, "R03": 32, "R04": 34, "R05": 36, "R06": 32, "R07": 34, "R08": 30, "R09": 38, "SKY": 38,
              "U1": 32, "U2": 36, "U3": 42, "SEA": 38, "NIGHT": 34}
OLD_GROUPS = {"R01": ["OW1"], "R02": ["OW2"], "R03": ["OW3"], "R04": ["OW4"], "R05": ["OW5"]}


def apply_world_groups(FM):
    """World zone groups: W_<region> (pre-fault) mixes the canon overworld group with the region's new enemies;
    WP_<region> (post-fault) uses the region's enemies re-levelled to the post band plus the canon post group."""
    lv = {r[0]: r[3] for r in ROWS}
    for home in list(groups().keys()) + ["R01", "R02", "R03", "R04", "R05"]:
        pre = []
        for g in OLD_GROUPS.get(home, []):
            pre += FM.GROUPS.get(g, [])
        pre += FM.GROUPS.get("OWX_" + home, [])
        if pre:
            FM.GROUPS["W_" + home] = pre
        post = list(FM.GROUPS.get("OWP", []))
        for fid in FM.GROUPS.get("OWX_" + home, []):
            f = FM.FORMATIONS[fid]
            pf = dict(f)
            pf["enemies"] = [FM.v(e["id"] if isinstance(e, dict) else e, max(POST_LEVEL.get(home, 30), lv.get(e["id"] if isinstance(e, dict) else e, 1)))
                             for e in f["enemies"]]
            FM.FORMATIONS["P" + fid] = pf
            post.append("P" + fid)
        FM.GROUPS["WP_" + home] = post
