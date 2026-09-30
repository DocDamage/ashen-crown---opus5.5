"""Group a places: Crown March (N01 Hollins Mill, N02 Gallowgate Toll, N03 Wren's Orchard, N04 The Sunken Chapel,
N05 Ashward Barrows, N41 Oathstone Crossroads), Cinder Reach (N06 Kettle Row, N07 The Slagfalls, N08 Anvil Cairn,
N09 Pipewright's Rest, N10 Cindermaw Caldera, N42 The Weeping Dam) and the post-fault additions (P01 Spine of Ilyrath,
P02 The Tessellate, P05 Refuge Rock, P09 The Last Beacon).
Maps: content_src/maps/x_a.map. Scenes: content_src/scenes/x_a.scn.
Recurring NPC: Tobiah Wend, pack-merchant (speaker 'wend', shop SHOP_WEND) at N41, N02, N08, P05, P09.
Sergeant Kell (speaker 'kell') runs the Gallowgate bounty board pre-fault and leads the deserters in QW1 post-fault."""

SHOPS = {
    "SHOP_N01": {"name": "Linden's Store", "kinds": ["items", "weapons", "armor"], "town": "N01"},
    "SHOP_N02": {"name": "Gallowgate Canteen", "kinds": ["items"], "town": "N02"},
    "SHOP_N03": {"name": "Cellarman Duro's", "kinds": ["items", "weapons", "armor"], "town": "N03"},
    "SHOP_N06": {"name": "Guild Smithy", "kinds": ["items", "weapons", "armor"], "town": "N06"},
    "SHOP_N08": {"name": "Forge-Mother's Anvil", "kinds": ["weapons", "armor"], "town": "N08"},
    "SHOP_N09": {"name": "Wend's Agent", "kinds": ["items", "armor", "accessories"], "town": "N09"},
    "SHOP_P05": {"name": "Salvager Quill's", "kinds": ["items", "weapons", "armor", "accessories"], "town": "P05"},
    "SHOP_WEND": {"name": "Wend's Pack", "kinds": ["items", "accessories"], "town": "N41"},
}

SPEAKERS = {
    # recurring
    "wend": ["Tobiah Wend", "keeper"],
    "kell": ["Sergeant Kell", "guard"],
    # N01 Hollins Mill
    "hollin": ["Old Hollin", "elder"],
    "brannock": ["Brannock", "worker"],
    "oda": ["Oda", "sailor"],
    "assessor": ["Grain Assessor", "clerk"],
    "juniper": ["Juniper", "apprentice"],
    "nell": ["Nell Hollin", "baker"],
    # N03 Wren's Orchard
    "wren": ["Wren Tamsey", "baker"],
    "harl": ["Harl Wren", "survivor"],
    "duro": ["Cellarman Duro", "keeper"],
    "mab": ["Cooper Mab", "apprentice"],
    "buyer": ["Veyr Buyer", "clerk"],
    # N04 The Sunken Chapel
    "hallam": ["Ser Hallam", "guard"],
    "aubel": ["Squire Aubel", "survivor"],
    # N05 Ashward Barrows
    "edrin": ["Barrow-Warden Edrin", "elder"],
    # N06 Kettle Row
    "grete": ["Forewoman Grete", "worker"],
    "pickett": ["Tam Pickett", "worker"],
    "sallow": ["Old Sallow", "elder"],
    "ivy": ["Ember-hand Ivy", "worker"],
    # N08 Anvil Cairn
    "seo": ["Anvil-Mother Seo", "elder"],
    "cairnkeeper": ["Cairn Keeper", "elder"],
    # N09 Pipewright's Rest
    "dunmore": ["Dunmore Pipewright", "keeper"],
    "olen": ["Brasswife Olen", "apprentice"],
    "hesta": ["Master Hesta", "elder"],
    "ambrose": ["Old Ambrose", "elder"],
    # N10 Cindermaw Caldera
    "imre": ["Fire-Reader Imre", "clerk"],
    # N42 The Weeping Dam
    "sluicewife": ["The Sluicewife", "patient"],
    "orrin": ["Keeper Orrin", "survivor"],
    # P02 The Tessellate
    "tessellate": ["The Tessellate Engine", "clerk"],
    "lanne": ["Surveyor Lanne", "clerk"],
    # P05 Refuge Rock
    "marit": ["Warden Marit", "elder"],
    "ansa": ["Ansa", "sailor"],
    "dov": ["Dov", "worker"],
    "tamm": ["Tamm", "worker"],
    "nan": ["Wreckwright Nan", "worker"],
    "librarian": ["Tide-Librarian", "clerk"],
    # P09 The Last Beacon
    "hesk": ["Signalwoman Hesk", "worker"],
}

LOCATIONS = {
    "L_N01": {"name": "Hollins Mill", "map": "N01_R01", "spawn": "world"},
    "L_N02": {"name": "Gallowgate Toll", "map": "N02_R01", "spawn": "world"},
    "L_N03": {"name": "Wren's Orchard", "map": "N03_R01", "spawn": "world"},
    "L_N04": {"name": "The Sunken Chapel", "map": "N04_R01", "spawn": "world"},
    "L_N05": {"name": "Ashward Barrows", "map": "N05_R01", "spawn": "world"},
    "L_N06": {"name": "Kettle Row", "map": "N06_R01", "spawn": "world"},
    "L_N07": {"name": "The Slagfalls", "map": "N07_R01", "spawn": "world"},
    "L_N08": {"name": "Anvil Cairn", "map": "N08_R01", "spawn": "world"},
    "L_N09": {"name": "Pipewright's Rest", "map": "N09_R01", "spawn": "world"},
    "L_N10": {"name": "Cindermaw Caldera", "map": "N10_R01", "spawn": "world"},
    "L_N41": {"name": "Oathstone Crossroads", "map": "N41_R01", "spawn": "world"},
    "L_N42": {"name": "The Weeping Dam", "map": "N42_R01", "spawn": "world"},
    "L_P01": {"name": "Spine of Ilyrath", "map": "P01_R01", "spawn": "world"},
    "L_P02": {"name": "The Tessellate", "map": "P02_R01", "spawn": "world"},
    "L_P05": {"name": "Refuge Rock", "map": "P05_R01", "spawn": "world"},
    "L_P09": {"name": "The Last Beacon", "map": "P09_R01", "spawn": "world"},
}

QUESTS = [
    {"id": "QW1", "name": "Refuge Rock", "start": "P05", "location": "P05", "character": "",
     "hook": "Warden Marit Oakes of Refuge Rock: the spring is failing and four fishers (Ansa, Dov, Tamm and the girl Wynn) have not come back from the Tide Shelf wreck.",
     "objectives": "Open the shelf gate; save Ansa from the wreck crabs; splint Dov's leg on the north rocks; find Tamm and Wynn in the Crown supply hulk, sheltered by Sergeant Kell's deserters; survive the harpy ambush on the way home.",
     "decision": "At the council: let Kell's nine Crown deserters onto the Rock (qw1_kell_in) or keep them on the shelf with a share of the rations (qw1_kell_out).",
     "result": "The fishers are home and the deserters' salvaged still saves the spring. Kell and a deserter live on the Rock, or Kell's camp stays on the shelf and sends water up at dawn.",
     "reward": "A117 Lantern Charm, I003 x2, 2000 crowns", "boss": "", "stages": ["shelf", "wreck", "plead", "council", "done"],
     "scenes": ["QW1_MARIT", "QW1_CRABS", "QW1_DOV", "QW1_WRECK", "QW1_CHECK", "QW1_AMBUSH", "QW1_DECISION"]},
    {"id": "QW6", "name": "The Last Beacon", "start": "P09", "location": "P09", "character": "",
     "hook": "Signalwoman Hesk: the Last Beacon, master lamp of the old keepers' signal network, went dark in the fault; its keeper died on the cliff with the key.",
     "objectives": "Take Old Mattock's key from his cairn on the west ledge; climb to the lamp gallery and drive out the griffon roost; fill the empty fire-cup.",
     "decision": "Burn the Ministry's heartglass shard found in the lamp housing (qw6_heartglass) or burn the camp's winter oil and bury the heartglass under Mattock's cairn (qw6_oil).",
     "result": "The beacon burns (p09_beacon_lit): the waystone network wakes, and Hesk's crew fits the Lanternwake with the Grapnel Keel (lanternwake_grapnel).",
     "reward": "Grapnel Keel (land anywhere), A118 Driftglass Ring, 3000 crowns", "boss": "", "stages": ["key", "climb", "lamp", "lit"],
     "scenes": ["QW6_HESK", "QW6_CAIRN", "QW6_ROOST", "QW6_LAMP", "QW6_REWARD"]},
    {"id": "QC17", "name": "The Highway That Was", "start": "P02", "location": "U22", "character": "C17",
     "hook": "At the Tessellate the Night Rider finds Mile 0 of the Ring Highway he still patrols; the tower stands on its old interchange.",
     "objectives": "Surface half (P02): read the three final-night traffic logs in Traffic Control; reach the master dispatch console at the crown of the tower, past the Tessellate Engine; defeat the patrol drones. Deep half (U22): follow the highway's lower deck into the Lattice.",
     "decision": "At the dispatch console: end the patrol - unit relieved (qc17_ended) - or continue it on a new route, the ruin's broken roads (qc17_route).",
     "result": "Surface half ends with qc17_surface_done and stage 'deep': the lower deck to the Lattice still has its lights on. The Deep half continues at U22 The Highway That Was.",
     "reward": "Surface half: A111 Windcord Knot. Deep half: see U22.", "boss": "BX13", "stages": ["marker", "logs", "deep"],
     "scenes": ["QC17_MARKER", "QC17_LOG1", "QC17_LOG2", "QC17_LOG3", "QC17_CHECK", "QC17_CONSOLE"]},
]
