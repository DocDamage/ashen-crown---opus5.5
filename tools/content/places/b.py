"""Group b places: Glass Coast (N11 Tidewrack, N12 Belltower Point, N13 The Brine Stair, N43 Lanternfall),
Ember Sea (N14 Saltwhistle Isle, N15 Gullrock), Skyspine (N16 Windrest, N17 The Ninefold Shrine, N18 Eyrie Hollow),
Pale Basin (N19 Lilac Seep, N20 The Glass Orchard, N21 Sorrowmere) and the Shattered Choir (N37 Choir Anchorage,
N39 Seraphel, N40 The Broken Organ). Maps: content_src/maps/x_b.map; scenes: content_src/scenes/x_b.scn.
Questlines: QW7 Old Bellharbor, QW2 The Ridge Road, QC10 The Host That Stopped Answering."""

SHOPS = {
    "SHOP_N11": {"name": "Salvage Exchange", "kinds": ["items", "weapons", "armor"], "town": "N11"},
    "SHOP_N14": {"name": "Guild Tackle and Stores", "kinds": ["items", "armor", "accessories"], "town": "N14"},
    "SHOP_N16": {"name": "Windrest Wool and Iron", "kinds": ["items", "weapons", "armor"], "town": "N16"},
    "SHOP_N19": {"name": "Seep Herbalist", "kinds": ["items", "armor", "accessories"], "town": "N19"},
    "SHOP_N43": {"name": "Tallow and Wick", "kinds": ["items", "accessories"], "town": "N43"},
}

# speaker key -> [display name, portrait key]
SPEAKERS = {
    # generic townsfolk keys used by these scenes (portraits reuse the generic set)
    "scholar": ["Scholar", "clerk"], "noble": ["Noble", "clerk"], "monk": ["Monk", "elder"], "farmer": ["Farmer", "worker"],
    # N11 Tidewrack
    "tam": ["Tam Drift", "sailor"], "wenna": ["Wenna Coyle", "sailor"], "marl": ["Marl", "baker"],
    "pruett": ["Old Pruett", "keeper"], "hesk": ["Hesk the Riveter", "worker"],
    # N12 Belltower Point
    "ossery": ["Keeper Ossery", "elder"], "coll": ["Coll the Boatman", "sailor"], "brisa": ["Brisa", "sailor"],
    # N13 The Brine Stair
    "matriarch": ["The Brine Matriarch", ""],
    # N43 Lanternfall
    "oda": ["Oda Galloway", "worker"], "brannock": ["Mother Brannock", "baker"], "wick": ["Wick", "keeper"],
    "ysa": ["Ysa", "keeper"],
    # N14 Saltwhistle / N15 Gullrock
    "vane": ["Guildmaster Vane", "elder"], "fishing_master": ["Tourney Master Oyle", "sailor"],
    "gullrock": ["Captain Nell Rask", "survivor"], "pearl": ["Pearl", "baker"], "gorse": ["Gorse", "keeper"],
    "ama": ["Net-Wright Ama", "worker"],
    # N16 Windrest (QW2)
    "maddoc": ["Maddoc Harl", "elder"], "ysolde": ["Ysolde Harl", "volunteer"], "crook": ["Old Crook", ""],
    "gwin": ["Gwin", "baker"], "brannagh": ["Brannagh", "keeper"], "tolly": ["Tolly the Hornsmith", "worker"],
    # N17 Ninefold Shrine
    "windkeeper": ["Windkeeper Aun", "elder"],
    # N18 Eyrie Hollow
    "aurelle": ["Aurelle", ""],
    # N19 Lilac Seep / N20 Glass Orchard / N21 Sorrowmere
    "herbalist": ["Sorrel the Herbalist", "apprentice"], "orchardist": ["Pellam, the Last Orchardist", "elder"],
    "meremother": ["The Mere-Mother", ""],
    "hanne": ["Hanne", "baker"], "aldous": ["Aldous Brine", "worker"], "temperance": ["Chair Temperance", "elder"], "drowned": ["A Drowned Voice", ""],
    # the sky: N37, N39, N40 (QC10)
    "anchormaster": ["Anchormaster Cleave", "pilot"], "seraph": ["The Hollow Seraph", ""],
    "hostsoldier": ["Host Sentinel", "guard"], "organ": ["The Broken Organ", ""],
}

LOCATIONS = {
    "L_N11": {"name": "Tidewrack", "map": "N11_R01", "spawn": "world"},
    "L_N12": {"name": "Belltower Point", "map": "N12_R01", "spawn": "world"},
    "L_N13": {"name": "The Brine Stair", "map": "N13_R01", "spawn": "world"},
    "L_N14": {"name": "Saltwhistle Isle", "map": "N14_R01", "spawn": "world"},
    "L_N15": {"name": "Gullrock", "map": "N15_R01", "spawn": "world"},
    "L_N16": {"name": "Windrest", "map": "N16_R01", "spawn": "world"},
    "L_N17": {"name": "The Ninefold Shrine", "map": "N17_R01", "spawn": "world"},
    "L_N18": {"name": "Eyrie Hollow", "map": "N18_R01", "spawn": "world"},
    "L_N19": {"name": "Lilac Seep", "map": "N19_R01", "spawn": "world"},
    "L_N20": {"name": "The Glass Orchard", "map": "N20_R01", "spawn": "world"},
    "L_N21": {"name": "Sorrowmere", "map": "N21_R01", "spawn": "world"},
    "L_N37": {"name": "Choir Anchorage", "map": "N37_R01", "spawn": "world"},
    "L_N39": {"name": "Seraphel, Fallen Host", "map": "N39_R01", "spawn": "world"},
    "L_N40": {"name": "The Broken Organ", "map": "N40_R01", "spawn": "default"},
    "L_N43": {"name": "Lanternfall", "map": "N43_R01", "spawn": "world"},
}

QUESTS = [
    {"id": "QW7", "name": "Old Bellharbor", "start": "N11", "location": "N12", "character": None,
     "hook": "After the fault, Wenna Coyle of Tidewrack hears that Keeper Ossery at Belltower Point has been hearing "
             "knocking through the lamp-glass at low tide: people alive under the sea in drowned Old Bellharbor",
     "objectives": "Speak to Keeper Ossery; recover the smugglers' sea-glass helmet from the Brine Stair's contraband "
                   "hold; fit it to the lighthouse's old diving bell; descend the sea-stair into Old Bellharbor",
     "decision": "Eleven people are trapped in the drowned customs vault and the bell carries six a trip: choose who "
                 "goes first, or ask them to decide among themselves",
     "result": "Everyone comes up. Wenna and Ossery draft a pressure hull from the bell's design and fit it to the "
               "Lanternwake: the Diving Hull (the airship can become a submarine)",
     "reward": "Diving Hull (flag lanternwake_diving); A118 Driftglass Ring; 2000 crowns", "boss": None},
    {"id": "QW2", "name": "The Ridge Road", "start": "N16", "location": "N16", "character": None,
     "hook": "After the fault, Windrest's stablemaster Maddoc Harl asks for help: his daughter Ysolde took the flock "
             "up the ridge the morning the cliff road fell, and has not come down",
     "objectives": "Climb the broken ridge road above Windrest; reach the stranded shepherds' camp; bring them down",
     "decision": "Carry the injured shepherd down the short way at once and leave the flock, or follow Old Crook, the "
                 "ridgehorn ram, down the goat paths with everyone and every animal",
     "result": "The shepherds come home. Maddoc shoes Bramble with ridgehorn iron and teaches her the high paths: "
               "the Ridgehorn can cross mountains",
     "reward": "Ridgehorn (flag brackhorn_ridgehorn); A111 Windcord Knot", "boss": None},
    {"id": "QC10", "name": "The Host That Stopped Answering", "start": "N39", "location": "N39", "character": "C10",
     "hook": "In the ruins of Seraphel, the Archangel Commander recognises his own host, which stopped answering him "
             "thirty years ago, and its last standing order: hold the sky until relieved",
     "objectives": "Read the host's muster roll; find the sentinels still holding their posts; reach the choir loft "
                   "where the choirmaster conducts a song nobody sings",
     "decision": "Order the sentinels to stand down, or tell them what he has seen below and let each of them choose",
     "result": "The Hollow Seraph is silenced; the Archangel declares himself relieved, by his own judgment rather "
               "than anyone's order",
     "reward": "W004 Witness Edge; A020 Mercy Thread", "boss": "BX10"},
]
