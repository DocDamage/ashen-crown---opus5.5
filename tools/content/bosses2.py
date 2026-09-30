"""Expansion bosses (BX01-BX26: one per optional dungeon / questline climax) and superbosses (SB01-SB12).

Each row keeps the house style of tools/content/enemies.py bosses: phases at HP thresholds with their own cycles, a
charged signature move with a tell the player can read, affinities that change between phases, and a counterplay line.
apply() registers them with the enemy/boss tables, the boss catalogue, levels and formations (formation id = boss id).
Art: ROSTER (id -> source code, height, flip) through the Aseprite enemy pipeline (tools/art/enemy_job.py).
Superbosses (tag "superboss") have damage caps lifted and drop a Vestige key (see WORLD_V2.md section 9).
"""


def hp_for(lv, mult=1.0):
    return int(round((200 * lv + 9 * lv * lv) * mult / 50.0)) * 50


# id, name, where, chapter, level, art, height, flip, bg, music, lore
ROWS = [
    ("BX01", "Ser Hallam, the Oath-Drowned", "N04", "CH03", 12, "M:13", 104, 0, "grove_flood", "M026",
     "Knight-commander of the chapel order. He swore to hold the chapel until relieved. Nobody came."),
    ("BX02", "The Slag Colossus", "N07", "CH04", 18, "M:4", 110, 0, "furnace", "M026",
     "Built from the overflow of a hundred furnaces. It walks the terraces because nobody told the slag to stop."),
    ("BX03", "The Brine Matriarch", "N13", "CH06", 21, "M:34", 106, 0, "reef", "M026",
     "Mother of the sea-cave broods. The smugglers paid her in drowned men; she kept the receipts."),
    ("BX04", "Aurelle, Roc Queen", "N18", "CH08", 24, "M:175", 112, 0, "sky", "M026",
     "The last roc queen of the Skyspine. Her eggs are worth a fortune; her mood is not."),
    ("BX05", "The Mere-Mother", "N21", "CH09", 29, "R:04", 118, 0, "vault", "M026",
     "Each head remembers a different drowned village. Kill one and the lake forgets it."),
    ("BX06", "Abbot Lamprey", "N25", "CH10", 25, "G:3/Boss (10)", 118, 0, "whitebone", "M026",
     "The plague order's abbot, who sold the cure and kept the disease. He has been feeding for years."),
    ("BX07", "The Nine-Tailed Magistrate", "N29", "CH10", 30, "M:159", 108, 1, "crown", "M026",
     "Judge of the Fox Court's lower gates. Every tail is a verdict it has never overturned."),
    ("BX08", "The Rimebound Behemoth", "N34", "CH11", 34, "R:09", 120, 0, "winter", "M026",
     "Frozen into the spire's heart before the Crown was a crown. The thaw woke it hungry."),
    ("BX09", "The Frosthorn Warden", "N35", "CH11", 35, "R:10", 120, 0, "winter", "M026",
     "Guardian of the Lich King's frozen seat. It has not let anyone in for three hundred winters."),
    ("BX10", "The Hollow Seraph", "N39", "CH16", 38, "M:300", 112, 1, "sky", "M026",
     "What is left of the host's choirmaster when the song stops. It still conducts."),
    ("BX11", "The Sluicewife", "N42", "CH05", 17, "M:255", 104, 0, "underways", "M026",
     "The dam keeper's widow, now the dam. Every crack is a grievance she never filed."),
    ("BX12", "Marrow Tyrant", "P01", "CH16", 38, "M:199", 116, 0, "field_post", "M026",
     "A scavenger dragon that made its nest in Ilyrath's ribs and grew fat on the fault."),
    ("BX13", "The Tessellate Engine", "P02", "CH16", 38, "M:6", 112, 0, "crown_core", "M026",
     "The builder tower's governor. It rose with the tower and resumed a construction schedule nobody alive remembers."),
    ("BX14", "The Geode Hydra", "U04", "CH07", 24, "M:79", 108, 0, "vault", "M026",
     "Crystal grown around a living heart. Every shard it sheds becomes another mouth."),
    ("BX15", "The Wingless Remnant", "U05", "CH07", 26, "M:177", 112, 0, "whitebone", "M026",
     "A dragon that lost its fragment and kept living. Ilyr knows its name and will not say it."),
    ("BX16", "Foreman Grisk's Excavator", "U08", "CH07", 27, "M:123", 110, 0, "quarry", "M026",
     "The Crown's deep-dig machine with its foreman welded into the cab. He calls it overtime."),
    ("BX17", "The Forge-Wurm", "U12", "CH08", 28, "M:128", 110, 0, "furnace", "M026",
     "It eats ore and excretes ingots. The delvers mine it more than the rock."),
    ("BX18", "Assembler Prime", "U18", "CH11", 34, "M:9", 112, 0, "conduit", "M026",
     "The factory floor's first automaton. It has built ten thousand soldiers for a war that ended an age ago."),
    ("BX19", "The Index", "U20", "CH16", 36, "M:207", 106, 0, "archive", "M026",
     "The archive's cataloguing eye. It files every visitor under 'pending deletion'."),
    ("BX20", "Kael-00", "U23", "CH17", 37, "M:111", 108, 0, "vault", "M026",
     "The prototype Kael-09 was copied from. It never received its standing orders and has been waiting."),
    ("BX21", "Ossuan, Keeper of the Bridges", "U30", "CH18", 42, "M:74", 110, 0, "whitebone", "M026",
     "It collects a toll of one bone per crossing. The bridges are the tolls."),
    ("BX22", "Mother Sepulchre", "U31", "CH19", 44, "M:282", 112, 1, "whitebone", "M028",
     "Queen of the Hollow Throne and Velkhar's old rival. She does not raise the dead. She adopts them."),
    ("BX23", "The Warden of Debts", "U32", "CH18", 43, "G:3/Boss (3)", 120, 0, "crown", "M026",
     "Keeper of the Abyss Gate's ledger. It remembers what Inferna owes, to the soul."),
    ("BX24", "The First Crown", "U33", "CH19", 45, "M:1", 112, 0, "crown_core", "M028",
     "The first wearer of the Ashen Crown, entombed with it. The crown was copied; the king was not."),
    ("BX25", "The Mourning Court", "U35", "CH19", 45, "M:219", 110, 0, "winter", "M026",
     "The Lich King's under-court, a single body of every courtier who grieved too long."),
    ("BX26", "Gatewarden Sorrow", "U36", "CH18", 44, "M:221", 108, 0, "whitebone", "M026",
     "Velkhar's first student, who stayed behind to hold the gate when he left. She is still angry."),
    ("BX27", "The Bell That Rang Wrong", "EP4", "CH24", 92, "M:150", 124, 0, "crown_core", "M028",
     "The Crown's great bell, sunk with Veyr. It rang once at the fault and has been trying to ring the right note since."),
    # ---- superbosses
    ("SB01", "Cindermaw, the Surface Wyrm", "N10", "CH16", 60, "R:05", 150, 0, "furnace", "M028",
     "The oldest dragon that never gave up its fragment. It sleeps in the caldera and wakes to feed on towns."),
    ("SB02", "Thalassar, the Sea Wyrm", "SEA", "CH17", 66, "M:266", 150, 0, "reef", "M028",
     "It coils under the Ember Sea. Sailors call the tide by its breathing."),
    ("SB03", "Aerith-Vael, the Sky Wyrm", "SKY", "CH18", 72, "M:197", 150, 1, "sky", "M028",
     "It flies the airship lanes and has never once landed. The storms are its wake."),
    ("SB04", "Ossathrax, the Deep Wyrm", "U1", "CH19", 78, "M:194", 150, 0, "furnace", "M028",
     "Ruler of Emberdeep before the delvers came. It remembers the world when it was still hot."),
    ("SB05", "CURATOR", "U24", "CH20", 80, "M:156", 150, 0, "crown_core", "M028",
     "The builder mind that sleeps at the Lattice's heart. The Crown's machine is a copy of it, badly made."),
    ("SB06", "Mother Sepulchre, Unveiled", "U31", "CH20", 84, "M:281", 140, 1, "whitebone", "M028",
     "Her true face, under the veil she wears for the living."),
    ("SB07", "Varro the Unbeaten", "N38", "CH16", 70, "M:210", 130, 0, "sky", "M028",
     "Champion of the Crucible Isle for forty years. He has never lost, and he has never been happy."),
    ("SB08", "The Choir That Remains", "U38", "CH20", 88, "M:254", 150, 0, "whitebone", "M028",
     "Every voice the Pale Choir silenced, still singing, under the Hollow Throne."),
    ("SB09", "Hollow Heart: the Ledger", "U39", "CH23", 95, "M:180", 150, 0, "crown_core", "M028",
     "The first of the Hollow Heart's keepers. It counts everything the Crown ever took."),
    ("SB10", "Hollow Heart: the Tally", "U39", "CH23", 102, "M:181", 150, 0, "crown_core", "M028",
     "The second keeper. It counts what the Crown ever gave back. The number is small."),
    ("SB11", "Hollow Heart: the Verdict", "U39", "CH23", 110, "M:187", 150, 0, "crown_core", "M028",
     "The third keeper. It weighs the two sums and says what they mean."),
    ("SB12", "The Unmade Crown", "U39", "CH23", 130, "M:102", 150, 0, "crown_core", "M028",
     "What the Ashen Crown would have become if nobody had ever worn it. It wants a head."),
]

ROSTER = {r[0]: (r[5], r[6], r[7]) for r in ROWS}
LORE = {r[0]: r[10] for r in ROWS}
SUPER = {r[0] for r in ROWS if r[0].startswith("SB")}
VESTIGE_OF = {"SB01": "V13", "SB02": "V14", "SB03": "V15", "SB04": "V16", "SB05": "V17", "SB06": "V18", "SB07": "V19",
              "SB09": "V20", "SB10": "V21", "SB08": "V22", "SB11": "V23", "SB12": "V24"}


def specs(mv, dmg, st):
    """id -> (shape, phases, moves, aff, parts, tell, counterplay, hint)"""
    S = {}
    S["BX01"] = ("knight", [
        {"at": 100, "cycle": ["cleave", "oath", "cleave"]},
        {"at": 50, "cycle": ["tide", "cleave", "oath", "cleave"], "enter": "Water pours from Hallam's visor. The chapel floods to the knee."}],
        {"cleave": mv("Drowned Cleave", [dmg(125)]),
         "oath": mv("Oath of Holding", [{"op": "guard_self", "mult": 0.45, "label": "oath"}], target="self", anim="guard"),
         "tide": mv("Chapel Tide", [dmg(95, "magical", "water", aoe=True), st("slow", 60, 2)], target="all", charge=2.4,
                    tell="The bells ring underwater", element="water")},
        {"storm": "weak", "water": "absorb"}, [], "Hallam raises his shield before every swing he cannot land",
        "Break the Oath guard with storm, or wait it out and Defend through the tide.", "Storm cracks his oath; Defend when the bells ring.")
    S["BX02"] = ("golem", [
        {"at": 100, "cycle": ["fist", "fist", "pour"]},
        {"at": 60, "cycle": ["fist", "pour", "crust", "fist"], "enter": "The colossus's crust hardens as it cools.", "affinities": {"ice": "weak", "fire": "absorb"}},
        {"at": 25, "cycle": ["meltdown", "fist", "pour"], "enter": "Its core glows white. The terraces start to run."}],
        {"fist": mv("Slag Fist", [dmg(130, element="fire")], element="fire"),
         "pour": mv("Molten Pour", [dmg(90, "magical", "fire"), st("burn", 70, 3)], target="row_front", element="fire"),
         "crust": mv("Cool Crust", [{"op": "guard_self", "mult": 0.5, "label": "crust"}], target="self", anim="guard"),
         "meltdown": mv("Meltdown", [dmg(175, "magical", "fire", aoe=True)], target="all", charge=2.8, tell="The core whitens and the air shakes", element="fire")},
        {"ice": "weak", "fire": "absorb"}, [], "The core brightens before the meltdown",
        "Ice cracks the crust; spread out the burn with cleanses.", "Ice and water crack the slag; cleanse burns.")
    S["BX03"] = ("naga", [
        {"at": 100, "cycle": ["lash", "song", "lash"]},
        {"at": 55, "cycle": ["brood", "lash", "song", "undertow"], "enter": "The Matriarch calls her brood from the pools."}],
        {"lash": mv("Tail Lash", [dmg(120)]), "song": mv("Siren Hymn", [st("sleep", 65, 2)], target="random", anim="cast", element="none"),
         "brood": mv("Call the Brood", [{"op": "heal", "power": 60}], target="self", anim="cast"),
         "undertow": mv("Undertow", [dmg(150, "magical", "water", aoe=True)], target="all", charge=2.6, tell="The pools drain toward her", element="water")},
        {"storm": "weak", "water": "absorb", "fire": "resist"}, [], "The pools drain toward her before the undertow",
        "Keep a waker ready for the hymn; storm stops her healing.", "Storm is strong; wake sleepers fast.")
    S["BX04"] = ("bird", [
        {"at": 100, "cycle": ["talon", "gust", "talon"]},
        {"at": 50, "cycle": ["dive", "talon", "gust", "screech"], "enter": "Aurelle takes to the air over the nest."}],
        {"talon": mv("Talon Rake", [dmg(125)]), "gust": mv("Wing Gust", [dmg(80, "magical", "storm", aoe=True)], target="all", element="storm"),
         "screech": mv("Queen's Screech", [st("silence", 60, 2)], target="all", anim="cast", element="none"),
         "dive": mv("Stoop", [dmg(210)], target="row_back", charge=2.4, tell="Her shadow crosses the back row", element="physical")},
        {"earth": "weak", "storm": "resist"}, [], "Her shadow marks the row she will dive on",
        "Move the back row forward when the shadow crosses it; earth grounds her.", "Earth grounds her; watch her shadow.")
    S["BX05"] = ("hydra", [
        {"at": 100, "cycle": ["bite", "bite", "drown"]},
        {"at": 66, "cycle": ["bite", "memory", "bite", "drown"], "enter": "A second head surfaces, weeping."},
        {"at": 33, "cycle": ["memory", "flood", "bite"], "enter": "All the heads rise. The mere remembers everything at once.", "affinities": {"fire": "weak", "ice": "neutral"}}],
        {"bite": mv("Many Bites", [dmg(70), dmg(70)]), "drown": mv("Drowning Hold", [dmg(140, "magical", "water"), st("slow", 70, 2)], target="lowest_hp", element="water"),
         "memory": mv("Drowned Memory", [dmg(110, "magical", "shadow"), st("doom", 30, 4)], target="random", anim="cast", element="shadow"),
         "flood": mv("The Mere Rises", [dmg(170, "magical", "water", aoe=True)], target="all", charge=2.8, tell="The lake climbs the shore", element="water")},
        {"ice": "weak", "water": "absorb"}, [{"id": "E_HEAD", "name": "Weeping Head", "hp_frac": 0.1, "aff": {"light": "weak"}}],
        "The lake climbs the shore before it rises", "Light on the weeping head stops the memories; ice early, fire late.",
        "Ice first, fire when all heads rise; light the weeping head.")
    S["BX06"] = ("ghoul", [
        {"at": 100, "cycle": ["claw", "leech", "claw"]},
        {"at": 50, "cycle": ["plague", "leech", "claw", "sermon"], "enter": "Lamprey sheds his robes. The cathedral's leeches answer."}],
        {"claw": mv("Rotting Claw", [dmg(120), st("poison", 60, 3)]), "leech": mv("Bloodletting", [dmg(110, drain=True)], target="lowest_hp"),
         "sermon": mv("Sermon of Rot", [st("weaken", 70, 3)], target="all", anim="cast", element="none"),
         "plague": mv("Plague Censer", [dmg(120, "magical", "poison", aoe=True), st("poison", 80, 4)], target="all", charge=2.6, tell="The censer swings wide", element="poison")},
        {"fire": "weak", "light": "weak", "poison": "absorb"}, [], "The censer swings wide before the plague",
        "Fire and light burn him; carry antidotes and cure the party after the censer.", "Fire and light; cure poison after the censer.")
    S["BX07"] = ("fox", [
        {"at": 100, "cycle": ["verdict", "illusion", "verdict"]},
        {"at": 60, "cycle": ["tails", "verdict", "illusion"], "enter": "Three more tails ignite. The court is in session."},
        {"at": 25, "cycle": ["sentence", "tails", "verdict"], "enter": "Every tail burns. The Magistrate reads the sentence."}],
        {"verdict": mv("Verdict", [dmg(130, "magical", "fire")], target="marked", anim="cast", element="fire"),
         "illusion": mv("Court of Masks", [st("blind", 70, 2), st("mark", 100, 2)], target="random", anim="cast", element="none"),
         "tails": mv("Foxfire Tails", [dmg(85, "magical", "fire", aoe=True)], target="all", element="fire"),
         "sentence": mv("Final Sentence", [dmg(230, "magical", "light")], target="marked", charge=2.6, tell="The marked one is named aloud", element="light")},
        {"water": "weak", "fire": "absorb"}, [], "The marked one is named aloud",
        "Guard or cover the marked ally before the sentence; water douses the tails.", "Water douses foxfire; protect the marked one.")
    S["BX08"] = ("beast", [
        {"at": 100, "cycle": ["tusk", "stomp", "tusk"]},
        {"at": 50, "cycle": ["blizzard", "tusk", "stomp", "shell"], "enter": "Ice closes over the Behemoth's wounds."}],
        {"tusk": mv("Glacier Tusk", [dmg(150, element="ice")], element="ice"), "stomp": mv("Avalanche Stomp", [dmg(95, aoe=True), st("stun", 30, 1)], target="all"),
         "shell": mv("Rime Shell", [{"op": "guard_self", "mult": 0.4, "label": "rime"}], target="self", anim="guard"),
         "blizzard": mv("Whiteout", [dmg(180, "magical", "ice", aoe=True)], target="all", charge=3.0, tell="The wind drops to nothing", element="ice")},
        {"fire": "weak", "ice": "absorb"}, [], "The wind drops to nothing before the whiteout",
        "Fire breaks the rime shell; Defend in the silence before the whiteout.", "Fire, and Defend in the silence.")
    S["BX09"] = ("titan", [
        {"at": 100, "cycle": ["horn", "seal", "horn"]},
        {"at": 55, "cycle": ["horn", "court", "seal", "horn"], "enter": "The Warden calls the court's cold down on the hall.", "affinities": {"light": "weak"}}],
        {"horn": mv("Frosthorn Gore", [dmg(160, element="ice")], element="ice"),
         "seal": mv("Seal the Seat", [st("silence", 70, 2), st("slow", 60, 2)], target="all", anim="cast", element="none"),
         "court": mv("Cold of the Court", [dmg(190, "magical", "ice", aoe=True)], target="all", charge=2.8, tell="Frost crawls up the pillars", element="ice")},
        {"fire": "weak", "ice": "absorb"}, [], "Frost crawls up the pillars", "Keep silence cures; fire, then light when the court comes.",
        "Fire, then light; cure silence.")
    S["BX10"] = ("angel", [
        {"at": 100, "cycle": ["baton", "hymn", "baton"]},
        {"at": 60, "cycle": ["hymn", "discord", "baton"], "enter": "The Seraph raises its baton. The broken organ answers."},
        {"at": 25, "cycle": ["finale", "baton", "discord"], "enter": "The last movement begins."}],
        {"baton": mv("Conductor's Strike", [dmg(140, "magical", "light")], anim="cast", element="light"),
         "hymn": mv("Hollow Hymn", [{"op": "heal", "power": 70}], target="self", anim="cast"),
         "discord": mv("Discord", [dmg(110, "magical", "shadow", aoe=True), st("silence", 50, 2)], target="all", anim="cast", element="shadow"),
         "finale": mv("Finale", [dmg(240, "magical", "light", aoe=True)], target="all", charge=3.2, tell="The organ holds a single chord", element="light")},
        {"shadow": "weak", "light": "absorb"}, [], "The organ holds one chord before the finale",
        "Silence it to stop the hymn; shadow cuts through; Defend in the chord.", "Shadow; stop its hymn; Defend on the chord.")
    S["BX11"] = ("serpent", [
        {"at": 100, "cycle": ["spray", "crack", "spray"]},
        {"at": 45, "cycle": ["breach", "spray", "crack"], "enter": "The dam groans. Water bursts through her."}],
        {"spray": mv("Pressure Spray", [dmg(115, "magical", "water")], anim="cast", element="water"),
         "crack": mv("Grievance", [st("weaken", 60, 3)], target="random", anim="cast", element="none"),
         "breach": mv("Breach", [dmg(150, "magical", "water", aoe=True)], target="all", charge=2.6, tell="The sluice gates shudder", element="water")},
        {"storm": "weak", "water": "absorb"}, [], "The sluice gates shudder", "Storm is strong; Defend through the breach.", "Storm; Defend on the breach.")
    S["BX12"] = ("dragon", [
        {"at": 100, "cycle": ["bite", "marrow", "bite"]},
        {"at": 50, "cycle": ["breath", "bite", "marrow", "tail"], "enter": "The Tyrant cracks a rib of Ilyrath and swallows the marrow."}],
        {"bite": mv("Marrow Bite", [dmg(150)]), "tail": mv("Tail Sweep", [dmg(100, aoe=True)], target="row_front"),
         "marrow": mv("Feast", [{"op": "heal", "power": 90}], target="self", anim="cast"),
         "breath": mv("Bone-Dust Breath", [dmg(190, "magical", "earth", aoe=True), st("blind", 50, 2)], target="all", charge=2.8, tell="It drags in a long breath of dust", element="earth")},
        {"storm": "weak", "earth": "absorb"}, [], "It drags in a long breath of dust", "Stop its feasting with pressure; storm; cure blind.", "Storm; keep pressure on.")
    S["BX13"] = ("machine", [
        {"at": 100, "cycle": ["laser", "schedule", "laser"]},
        {"at": 60, "cycle": ["build", "laser", "schedule"], "enter": "The Engine lays another course of the tower around itself.", "affinities": {"storm": "weak"}},
        {"at": 25, "cycle": ["demolish", "laser", "build"], "enter": "DEMOLITION SCHEDULED."}],
        {"laser": mv("Survey Beam", [dmg(140, "magical", "light")], target="random", anim="cast", element="light"),
         "schedule": mv("Schedule", [st("slow", 70, 2)], target="all", anim="cast", element="none"),
         "build": mv("Lay a Course", [{"op": "guard_self", "mult": 0.45, "label": "masonry"}], target="self", anim="guard"),
         "demolish": mv("Demolition", [dmg(230, "physical", None, aoe=True)], target="all", charge=3.0, tell="DEMOLITION SCHEDULED", element="physical")},
        {"water": "weak"}, [{"id": "E_GOVERNOR", "name": "Governor Core", "hp_frac": 0.12, "aff": {"storm": "weak"}}],
        "It announces demolition", "Strike the governor core to slow its schedule; Defend on demolition.", "Hit the core; Defend on demolition.")
    S["BX14"] = ("hydra", [
        {"at": 100, "cycle": ["shard", "shard", "refract"]},
        {"at": 50, "cycle": ["shatter", "shard", "refract"], "enter": "The hydra splits along its fault lines.", "affinities": {"earth": "weak"}}],
        {"shard": mv("Shard Bite", [dmg(120)]), "refract": mv("Refract", [{"op": "guard_self", "mult": 0.5, "label": "prism"}], target="self", anim="guard"),
         "shatter": mv("Geode Burst", [dmg(160, "magical", "earth", aoe=True)], target="all", charge=2.6, tell="Its crystals ring like bells", element="earth")},
        {"fire": "weak", "ice": "resist", "light": "resist"}, [], "Its crystals ring", "Fire cracks the prism; earth once it splits.", "Fire, then earth.")
    S["BX15"] = ("dragon", [
        {"at": 100, "cycle": ["claw", "grief", "claw"]},
        {"at": 50, "cycle": ["grief", "hollow", "claw"], "enter": "Ilyr stirs in Raven. The Remnant hears him."}],
        {"claw": mv("Old Claws", [dmg(140)]), "grief": mv("Unbound Grief", [dmg(90, "magical", "shadow", aoe=True)], target="all", element="shadow"),
         "hollow": mv("Hollow Roar", [dmg(200, "magical", "shadow"), st("doom", 40, 4)], target="random", charge=2.6, tell="It turns its empty eyes on one of you", element="shadow")},
        {"light": "weak", "shadow": "absorb"}, [], "It turns its empty eyes on one of you", "Light hurts; cure doom quickly.", "Light; cure doom.")
    S["BX16"] = ("machine", [
        {"at": 100, "cycle": ["drill", "scoop", "drill"]},
        {"at": 55, "cycle": ["overtime", "drill", "scoop", "blast"], "enter": "Grisk: 'Overtime! Nobody leaves till the seam's dry!'"}],
        {"drill": mv("Drill Arm", [dmg(135)]), "scoop": mv("Scoop", [dmg(90), st("guardbreak", 60, 2)], target="row_front"),
         "overtime": mv("Overtime", [{"op": "guard_self", "mult": 0.6, "label": "overtime"}], target="self", anim="guard"),
         "blast": mv("Seam Blast", [dmg(170, "physical", "earth", aoe=True)], target="all", charge=2.8, tell="Grisk lights a fuse", element="earth")},
        {"storm": "weak", "water": "weak"}, [{"id": "E_CAB", "name": "Foreman's Cab", "hp_frac": 0.15}],
        "Grisk lights a fuse before the blast", "Break the cab to stop the overtime; storm and water short it out.", "Storm or water; break the cab.")
    S["BX17"] = ("worm", [
        {"at": 100, "cycle": ["gulp", "slag", "gulp"]},
        {"at": 45, "cycle": ["molt", "gulp", "slag"], "enter": "The wurm sheds a skin of iron."}],
        {"gulp": mv("Gulp", [dmg(145)], target="lowest_hp"), "slag": mv("Spit Slag", [dmg(90, "magical", "fire"), st("burn", 60, 3)], target="random", element="fire"),
         "molt": mv("Iron Molt", [dmg(170, "physical", "earth", aoe=True)], target="all", charge=2.4, tell="Its plates start to lift", element="earth")},
        {"ice": "weak", "fire": "absorb"}, [], "Its plates lift before the molt", "Ice; keep the weakest ally topped up.", "Ice; protect the weakest.")
    S["BX18"] = ("machine", [
        {"at": 100, "cycle": ["rivet", "assemble", "rivet"]},
        {"at": 60, "cycle": ["rivet", "line", "assemble"], "enter": "The production line starts again."},
        {"at": 25, "cycle": ["recall", "rivet", "line"], "enter": "Assembler Prime recalls every unit on the floor."}],
        {"rivet": mv("Rivet Gun", [dmg(75), dmg(75)]), "assemble": mv("Assemble", [{"op": "heal", "power": 60}], target="self", anim="cast"),
         "line": mv("Production Line", [dmg(110, "magical", "storm", aoe=True)], target="all", element="storm"),
         "recall": mv("Recall All Units", [dmg(220, "physical", None, aoe=True)], target="all", charge=3.0, tell="Every machine on the floor turns toward you")},
        {"water": "weak", "storm": "resist"}, [], "Every machine turns toward you", "Water shorts it; Defend on the recall.", "Water; Defend on the recall.")
    S["BX19"] = ("eye", [
        {"at": 100, "cycle": ["file", "gaze", "file"]},
        {"at": 50, "cycle": ["delete", "gaze", "file"], "enter": "PENDING DELETION: APPROVED."}],
        {"file": mv("File Under", [st("mark", 100, 2), dmg(80, "magical", "light")], target="random", anim="cast", element="light"),
         "gaze": mv("Indexing Gaze", [dmg(120, "magical", "light", aoe=True)], target="all", anim="cast", element="light"),
         "delete": mv("Delete Record", [dmg(260, "magical", "none")], target="marked", charge=2.6, tell="A record is highlighted", element="none")},
        {"shadow": "weak", "light": "absorb"}, [], "A record is highlighted", "Protect the marked ally; shadow blinds the eye.", "Shadow; protect the marked.")
    S["BX20"] = ("machine", [
        {"at": 100, "cycle": ["shot", "await", "shot"]},
        {"at": 50, "cycle": ["orders", "shot", "shot"], "enter": "Kael-00: 'Orders received. Correction: orders invented.'"}],
        {"shot": mv("Rail Shot", [dmg(160)], target="lowest_hp"), "await": mv("Await Orders", [{"op": "guard_self", "mult": 0.3, "label": "standby"}], target="self", anim="guard"),
         "orders": mv("Self-Issued Order", [dmg(210, "magical", "storm", aoe=True)], target="all", charge=2.6, tell="Its lights cycle through every colour", element="storm")},
        {"water": "weak", "storm": "absorb"}, [], "Its lights cycle", "Hit hard between standbys; water.", "Water; strike between standbys.")
    S["BX21"] = ("skeleton", [
        {"at": 100, "cycle": ["toll", "club", "club"]},
        {"at": 50, "cycle": ["collapse", "club", "toll"], "enter": "Ossuan pulls a bone from the bridge. The span sags."}],
        {"club": mv("Femur Club", [dmg(170)]), "toll": mv("Take the Toll", [dmg(90, drain=True), st("bleed", 60, 3)], target="random"),
         "collapse": mv("Collapse the Span", [dmg(220, "physical", "earth", aoe=True)], target="all", charge=2.8, tell="The bridge cracks under your feet", element="earth")},
        {"light": "weak", "fire": "weak", "shadow": "absorb"}, [], "The bridge cracks under your feet", "Light and fire; heal bleeds.", "Light or fire; heal bleeds.")
    S["BX22"] = ("queen", [
        {"at": 100, "cycle": ["kiss", "adopt", "kiss"]},
        {"at": 60, "cycle": ["lullaby", "kiss", "adopt"], "enter": "Mother Sepulchre: 'Hush now. You're home.'"},
        {"at": 25, "cycle": ["embrace", "kiss", "lullaby"], "enter": "Her veil lifts an inch."}],
        {"kiss": mv("Cold Kiss", [dmg(150, "magical", "shadow", drain=True)], target="random", anim="cast", element="shadow"),
         "adopt": mv("Adopt", [st("doom", 50, 4)], target="lowest_hp", anim="cast", element="none"),
         "lullaby": mv("Grave Lullaby", [st("sleep", 70, 2)], target="all", anim="cast", element="none"),
         "embrace": mv("Mother's Embrace", [dmg(260, "magical", "shadow", aoe=True)], target="all", charge=3.0, tell="She opens her arms", element="shadow")},
        {"light": "weak", "shadow": "absorb"}, [], "She opens her arms", "Light; cure doom and sleep; Defend when she opens her arms.", "Light; cure doom; Defend on the embrace.")
    S["BX23"] = ("demon", [
        {"at": 100, "cycle": ["gore", "ledger", "gore"]},
        {"at": 50, "cycle": ["collect", "gore", "ledger"], "enter": "The Warden opens the ledger to Inferna's page."}],
        {"gore": mv("Gore", [dmg(175)]), "ledger": mv("Read the Ledger", [st("weaken", 70, 3), st("slow", 50, 2)], target="all", anim="cast", element="none"),
         "collect": mv("Collect", [dmg(240, "magical", "fire", aoe=True)], target="all", charge=2.8, tell="The ledger's page burns", element="fire")},
        {"ice": "weak", "water": "weak", "fire": "absorb"}, [], "The ledger's page burns", "Ice and water; cleanse the ledger's curse.", "Ice or water; cleanse.")
    S["BX24"] = ("king", [
        {"at": 100, "cycle": ["sword", "decree", "sword"]},
        {"at": 66, "cycle": ["decree", "sword", "crown"], "enter": "The First Crown remembers being worn."},
        {"at": 33, "cycle": ["ash", "sword", "decree"], "enter": "The crown ignites. It was ash before it was gold.", "affinities": {"water": "weak", "light": "weak"}}],
        {"sword": mv("Regal Blade", [dmg(180)]), "decree": mv("First Decree", [st("silence", 60, 2), dmg(100, "magical", "shadow")], target="all", anim="cast", element="shadow"),
         "crown": mv("Crown's Weight", [dmg(230, "magical", "shadow")], target="protector", anim="cast", element="shadow"),
         "ash": mv("The First Ash", [dmg(280, "magical", "fire", aoe=True)], target="all", charge=3.2, tell="Ash falls like snow in the tomb", element="fire")},
        {"light": "weak", "shadow": "resist"}, [], "Ash falls like snow before the first ash",
        "Light; later water; keep silence cures ready.", "Light, then water; cure silence.")
    S["BX25"] = ("wraith", [
        {"at": 100, "cycle": ["scythe", "mourn", "scythe"]},
        {"at": 50, "cycle": ["procession", "scythe", "mourn"], "enter": "The courtiers step out of the body one by one."}],
        {"scythe": mv("Grieving Scythe", [dmg(170, "magical", "ice")], anim="cast", element="ice"),
         "mourn": mv("Mourn", [st("doom", 40, 4), st("slow", 60, 2)], target="random", anim="cast", element="none"),
         "procession": mv("Funeral Procession", [dmg(230, "magical", "shadow", aoe=True)], target="all", charge=2.8, tell="Bells toll once for each of you", element="shadow")},
        {"fire": "weak", "light": "weak", "ice": "absorb"}, [], "Bells toll once for each of you", "Fire and light; cure doom.", "Fire or light; cure doom.")
    S["BX26"] = ("wraith", [
        {"at": 100, "cycle": ["lash", "lesson", "lash"]},
        {"at": 50, "cycle": ["lesson", "gate", "lash"], "enter": "Sorrow: 'He taught you too? Then he taught you wrong.'"}],
        {"lash": mv("Grave Lash", [dmg(165)]), "lesson": mv("Old Lesson", [dmg(120, "magical", "shadow"), st("blind", 60, 2)], target="random", anim="cast", element="shadow"),
         "gate": mv("Shut the Gate", [dmg(240, "magical", "shadow", aoe=True)], target="all", charge=2.8, tell="The crypt-gate grinds closed behind you", element="shadow")},
        {"light": "weak", "shadow": "absorb"}, [], "The gate grinds closed", "Light; cure blind.", "Light; cure blind.")
    S["BX27"] = ("golem", [
        {"at": 100, "cycle": ["toll", "peal", "toll"]},
        {"at": 66, "cycle": ["peal", "toll", "wrong", "toll"], "enter": "The bell swings on no rope. The water shivers."},
        {"at": 33, "cycle": ["wrong", "toll", "knell", "peal"], "enter": "It remembers the note it rang at the fault."}],
        {"toll": mv("Toll", [dmg(240)]), "peal": mv("Peal", [dmg(170, "magical", "storm", aoe=True), st("stun", 35, 1)], target="all", element="storm"),
         "wrong": mv("The Wrong Note", [st("doom", 45, 4), st("silence", 55, 2)], target="all", anim="cast", element="none"),
         "knell": mv("Knell of Veyr", [dmg(380, "magical", "shadow", aoe=True, uncapped=True)], target="all", charge=3.2,
                     tell="Every bell in the drowned city answers at once", element="shadow")},
        {"earth": "weak", "storm": "absorb", "shadow": "resist"}, [], "Every bell in the city answers before the knell",
        "Earth muffles it; cure doom before it counts out; Defend through the knell.", "Earth dulls it; cure doom; Defend on the knell.")
    # ---- superbosses: longer phase chains, heavier charged moves, damage above the 9,999 line
    def wyrm(elem, weak, sig, sig_tell, roar):
        return ("dragon", [
            {"at": 100, "cycle": ["claw", "breath", "claw", "tail"]},
            {"at": 70, "cycle": ["breath", "claw", "roar", "tail"], "enter": roar},
            {"at": 40, "cycle": ["sig", "claw", "breath", "roar"], "enter": "The ancient dragon's fragment blazes through its scales."},
            {"at": 15, "cycle": ["sig", "breath", "sig", "claw"], "enter": "It will not stop. It never has."}],
            {"claw": mv("Ancient Claw", [dmg(260)]), "tail": mv("Tail Quake", [dmg(170, aoe=True)], target="row_front"),
             "breath": mv("Breath", [dmg(210, "magical", elem, aoe=True)], target="all", element=elem),
             "roar": mv("Roar", [st("weaken", 60, 3), st("slow", 50, 2)], target="all", anim="cast", element="none"),
             "sig": mv(sig, [dmg(420, "magical", elem, aoe=True, uncapped=True)], target="all", charge=3.4, tell=sig_tell, element=elem)},
            {weak: "weak", elem: "absorb"}, [], sig_tell, "Defend through the signature; exploit the weakness; bring revives.", "Defend on the signature; " + weak + " is weak.")
    S["SB01"] = wyrm("fire", "ice", "Caldera Heart", "The caldera's glow drains into its mouth", "Cindermaw's roar sets the ash alight.")
    S["SB02"] = wyrm("water", "storm", "Tidefall", "The sea pulls away from the shore", "Thalassar's roar lifts the waves.")
    S["SB03"] = wyrm("storm", "earth", "Skybreak", "The clouds split open above you", "Aerith-Vael's roar is thunder.")
    S["SB04"] = wyrm("earth", "water", "World When Hot", "The rock underfoot turns red", "Ossathrax's roar shakes Emberdeep.")
    S["SB05"] = ("machine", [
        {"at": 100, "cycle": ["hand", "index", "hand"]},
        {"at": 70, "cycle": ["copy", "hand", "index"], "enter": "CURATOR: 'You are running an old version. Updating.'"},
        {"at": 40, "cycle": ["purge", "copy", "hand"], "enter": "The Lattice powers down around you. All of it is going into CURATOR."},
        {"at": 15, "cycle": ["purge", "purge", "hand"], "enter": "CURATOR: 'Curation complete. Beginning deletion.'"}],
        {"hand": mv("Builder's Hand", [dmg(250)]), "index": mv("Reindex", [{"op": "heal", "power": 120}], target="self", anim="cast"),
         "copy": mv("Copy Technique", [dmg(230, "magical", "light", aoe=True)], target="all", anim="cast", element="light"),
         "purge": mv("Purge", [dmg(450, "magical", "none", aoe=True, uncapped=True)], target="all", charge=3.4, tell="Every light in the Lattice goes out", element="none")},
        {"water": "weak", "storm": "weak"}, [{"id": "E_LHAND", "name": "Left Hand", "hp_frac": 0.08}, {"id": "E_RHAND", "name": "Right Hand", "hp_frac": 0.08}],
        "Every light in the Lattice goes out", "Break both hands to slow its reindexing; Defend on the purge.", "Break the hands; Defend on the purge.")
    S["SB06"] = ("queen", [
        {"at": 100, "cycle": ["kiss", "brood", "kiss"]},
        {"at": 60, "cycle": ["unveil", "kiss", "brood"], "enter": "The veil falls. Nobody should see this face and live. You will have to try."},
        {"at": 25, "cycle": ["unveil", "grave", "kiss"], "enter": "Every grave in the Hollow Throne opens."}],
        {"kiss": mv("Deathly Kiss", [dmg(280, "magical", "shadow", drain=True)], target="random", anim="cast", element="shadow"),
         "brood": mv("Call the Brood", [{"op": "heal", "power": 110}], target="self", anim="cast"),
         "unveil": mv("Unveiling", [st("doom", 60, 3), st("sleep", 50, 2)], target="all", anim="cast", element="none"),
         "grave": mv("Every Grave", [dmg(460, "magical", "shadow", aoe=True, uncapped=True)], target="all", charge=3.4, tell="The ground breathes", element="shadow")},
        {"light": "weak", "shadow": "absorb"}, [], "The ground breathes", "Light; doom and sleep cures; Defend on the grave.", "Light; cure doom; Defend.")
    S["SB07"] = ("beast", [
        {"at": 100, "cycle": ["maul", "taunt", "maul"]},
        {"at": 60, "cycle": ["crowd", "maul", "maul", "taunt"], "enter": "Varro: 'Louder! They paid for louder!'"},
        {"at": 20, "cycle": ["unbeaten", "maul", "crowd"], "enter": "The crowd goes silent. Varro smiles for the first time in forty years."}],
        {"maul": mv("Champion's Maul", [dmg(240)], target="lowest_hp"), "taunt": mv("Taunt", [st("mark", 100, 2), st("weaken", 50, 2)], target="random", anim="step", element="none"),
         "crowd": mv("Play to the Crowd", [dmg(190, "physical", None, aoe=True)], target="all"),
         "unbeaten": mv("Unbeaten", [dmg(520, "physical", None, uncapped=True)], target="marked", charge=3.0, tell="Varro points at one of you", element="physical")},
        {}, [], "Varro points at one of you", "Cover the pointed-at ally; no weakness, only skill.", "No weakness; protect the marked.")
    S["SB08"] = ("choir", [
        {"at": 100, "cycle": ["verse", "chorus", "verse"]},
        {"at": 66, "cycle": ["silence", "verse", "chorus"], "enter": "The Choir finds a voice it silenced long ago: yours."},
        {"at": 33, "cycle": ["requiem", "silence", "chorus"], "enter": "It sings the requiem for everyone the Pale Choir took."}],
        {"verse": mv("Verse", [dmg(230, "magical", "shadow")], anim="cast", element="shadow"),
         "chorus": mv("Chorus", [dmg(200, "magical", "light", aoe=True)], target="all", anim="cast", element="light"),
         "silence": mv("Unsung", [st("silence", 80, 3)], target="all", anim="cast", element="none"),
         "requiem": mv("Requiem", [dmg(480, "magical", "shadow", aoe=True, uncapped=True)], target="all", charge=3.6, tell="Every voice stops at once", element="shadow")},
        {"storm": "weak"}, [], "Every voice stops at once", "Silence cures; storm; Defend in the pause.", "Storm; cure silence; Defend in the pause.")
    def keeper(elem, weak, sig, tell):
        return ("keeper", [
            {"at": 100, "cycle": ["strike", "count", "strike"]},
            {"at": 60, "cycle": ["sum", "strike", "count"], "enter": "The keeper reaches the end of a column."},
            {"at": 25, "cycle": ["sig", "sum", "strike"], "enter": "The keeper totals the book."}],
            {"strike": mv("Keeper's Strike", [dmg(300)]), "count": mv("Count", [st("weaken", 70, 3), st("slow", 60, 2)], target="all", anim="cast", element="none"),
             "sum": mv("Sum", [dmg(280, "magical", elem, aoe=True)], target="all", anim="cast", element=elem),
             "sig": mv(sig, [dmg(560, "magical", elem, aoe=True, uncapped=True)], target="all", charge=3.6, tell=tell, element=elem)},
            {weak: "weak", elem: "absorb"}, [], tell, "Defend on the total; " + weak + " is weak.", weak + " is weak; Defend on the total.")
    S["SB09"] = keeper("fire", "water", "What Was Taken", "The ledger's pages turn by themselves")
    S["SB10"] = keeper("ice", "fire", "What Was Returned", "The tally is very short")
    S["SB11"] = keeper("shadow", "light", "The Verdict", "The two books close together")
    S["SB12"] = ("crown", [
        {"at": 100, "cycle": ["claim", "weight", "claim"]},
        {"at": 75, "cycle": ["claim", "orders", "weight", "claim"], "enter": "The Unmade Crown looks for a head. It looks at each of you."},
        {"at": 50, "cycle": ["crown_all", "claim", "orders"], "enter": "It tries all of you on at once."},
        {"at": 20, "cycle": ["unmake", "claim", "crown_all"], "enter": "It remembers it was never meant to be made."}],
        {"claim": mv("Claim", [dmg(320, "magical", "shadow")], target="random", anim="cast", element="shadow"),
         "weight": mv("The Weight", [st("slow", 70, 3), st("guardbreak", 60, 2)], target="all", anim="cast", element="none"),
         "orders": mv("Orders Nobody Gave", [dmg(260, "magical", "none", aoe=True), st("silence", 50, 2)], target="all", anim="cast", element="none"),
         "crown_all": mv("Crown Them All", [dmg(380, "magical", "fire", aoe=True)], target="all", charge=3.0, tell="It widens", element="fire"),
         "unmake": mv("Unmake", [dmg(700, "magical", "none", aoe=True, uncapped=True)], target="all", charge=3.8, tell="The world goes quiet enough to hear your own names", element="none")},
        {"light": "weak"}, [{"id": "E_ASH", "name": "Ash Circlet", "hp_frac": 0.06, "aff": {"water": "weak"}}],
        "The world goes quiet", "Break the circlet with water; light; Defend on the unmaking.", "Light; break the circlet; Defend on the unmaking.")
    return S


def apply(cat_bosses, EN, TB, FM):
    have = {b["id"] for b in cat_bosses}
    sp = specs(EN.mv, EN.dmg, EN.st)
    for r in ROWS:
        bid, name, where, ch, lv = r[0], r[1], r[2], r[3], r[4]
        shape, phases, moves, aff, parts, tell, counter, hint = sp[bid]
        superb = bid in SUPER
        hp = hp_for(lv, 3.0 if superb else 1.0)
        if bid not in have:
            cat_bosses.append({"id": bid, "name": name, "location": where, "chapter": ch, "optional": True, "hp": hp,
                               "tell": tell, "counterplay": counter,
                               "phases": [{"threshold": ph["at"], "name": ph["cycle"][0]} for ph in phases],
                               "victory": "", "lore": r[10]})
        EN.boss(bid, shape, phases, moves, aff=aff, tags=["superboss"] if superb else [], parts=parts,
                mods={"spd": 1.2, "atk": 1.1} if superb else {})
        TB.BOSS_LEVEL[bid] = lv
        FM.FORMATIONS[bid] = FM.F([bid], r[8], r[9], True, hint=hint)
