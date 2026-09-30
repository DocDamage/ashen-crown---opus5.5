"""Group c: Mirewold (R08: N22-N26), Vermilion Reach (R07: N27-N31), Hoarfrost March (R09: N32-N36).
Maps in content_src/maps/x_c.map, scenes in content_src/scenes/x_c.scn.
Questlines: QC09 Kitsune, QC12 Corvus, QC13 Lich King (citadel half; finished at U35 by another group),
QW3 Harrowfen Burning, QW4 The Mire Ferry, QW5 The Fox Court in Exile."""

SHOPS = {
    "SHOP_N22": {"name": "Gall & Daughter, Apothecary", "kinds": ["items", "accessories"], "town": "N22"},
    "SHOP_N22_ROW": {"name": "Rookery Row Outfitter", "kinds": ["weapons", "armor"], "town": "N22"},
    "SHOP_N24": {"name": "Granny Sedge's Herb House", "kinds": ["items", "accessories"], "town": "N24"},
    "SHOP_N27": {"name": "Sayo's Lantern Shop", "kinds": ["items", "weapons"], "town": "N27"},
    "SHOP_N28": {"name": "Kageyama Masks", "kinds": ["armor", "accessories"], "town": "N28"},
    "SHOP_N28_MKT": {"name": "Lantern Market Stall", "kinds": ["items", "weapons"], "town": "N28"},
    "SHOP_N32": {"name": "Rimeholt Trading Post", "kinds": ["items", "weapons", "armor"], "town": "N32"},
}

# speaker key -> [display name, portrait key]
SPEAKERS = {
    # recurring
    "sallow": ["Brother Sallow", "monk"],          # ex-order scribe walking the Mirewold
    "tully": ["Tully the Pedlar", "keeper"],       # pedlar on the fen roads
    "ume": ["Ume", "apprentice"],                  # lantern courier of the Reach
    "brisk": ["Brisk", "keeper"],                  # fur trader of the north
    # Harrowfen
    "idony": ["Idony", "apprentice"], "gall": ["Gall", "keeper"], "marl": ["Marl", "keeper"],
    "brannock": ["Mother Brannock", "elder"], "ostrey": ["Warden-Captain Ostrey", "guard"],
    "boardmaster": ["Master of Quarantine", "noble"], "lamprey": ["Abbot Lamprey", "monk"],
    # Gibbet Road / Sickle Hamlet
    "hask": ["Hask", "survivor"], "hangman": ["The Last Hangman", "monk"], "sedge": ["Granny Sedge", "elder"],
    "holloway": ["Reeve Holloway", "elder"], "pike": ["Old Pike", "elder"], "nettle": ["Nettle", "child"],
    "meg": ["Meg Tansy", "keeper"], "rue": ["Rue", "apprentice"],
    # Vermilion Reach
    "tokichi": ["Tokichi", "sailor"], "sayo": ["Sayo", "keeper"], "oharu": ["Oharu", "keeper"],
    "hanzo": ["Hanzo", "worker"], "kiku": ["Old Kiku", "elder"], "tsubaki": ["Tsubaki", "noble"],
    "shirogane": ["Regent Shirogane", "noble"], "hotaru": ["Lady Hotaru", "noble"], "genba": ["Old Genba", "soldier"],
    "kageyama": ["Kageyama", "keeper"], "kasumi": ["Madam Kasumi", "keeper"], "oyuki": ["Oyuki", "baker"],
    "bailiff": ["Paper Bailiff", "clerk"], "magistrate": ["The Nine-Tailed Magistrate", "noble"],
    "hina": ["Hina", "apprentice"], "tae": ["Tae", "keeper"], "foxfather": ["The Bride's Father", "elder"], "foxbride": ["The Veiled Bride", "noble"],
    # Hoarfrost March
    "hild": ["Reeve Hild", "elder"], "aud": ["Hearthwife Aud", "keeper"], "torvald": ["Old Torvald", "keeper"],
    "sigrun": ["Sigrun", "worker"], "olle": ["Olle", "keeper"], "egil": ["Egil", "soldier"],
    "vesk": ["Chancellor Vesk", "noble"], "ormund": ["Captain Ormund", "soldier"], "ysolde": ["Ysolde", "noble"],
    "warden": ["The Frosthorn Warden", "guard"],
    # generic townsfolk portraits used by these places
    "monk": ["Monk", "monk"], "scholar": ["Scholar", "scholar"], "farmer": ["Farmer", "farmer"], "noble": ["Noble", "noble"],
    "soldier": ["Soldier", "soldier"],
}

LOCATIONS = {
    "L_N22": {"name": "Harrowfen", "map": "N22_R01", "spawn": "world"},
    "L_N23": {"name": "The Gibbet Road", "map": "N23_R01", "spawn": "world"},
    "L_N24": {"name": "Sickle Hamlet", "map": "N24_R01", "spawn": "world"},
    "L_N25": {"name": "The Leech Cathedral", "map": "N25_R01", "spawn": "world"},
    "L_N26": {"name": "Moth Hollow", "map": "N26_R01", "spawn": "world"},
    "L_N27": {"name": "Kaminari Ford", "map": "N27_R01", "spawn": "world"},
    "L_N28": {"name": "Akagane, the Fox Court", "map": "N28_R01", "spawn": "world"},
    "L_N29": {"name": "Thousand Gates", "map": "N29_R01", "spawn": "world"},
    "L_N30": {"name": "The Whispering Maples", "map": "N30_R01", "spawn": "world"},
    "L_N31": {"name": "Shiroyama Watch", "map": "N31_R01", "spawn": "world"},
    "L_N32": {"name": "Rimeholt", "map": "N32_R01", "spawn": "world"},
    "L_N33": {"name": "The Ice Road", "map": "N33_R01", "spawn": "world"},
    "L_N34": {"name": "Glacier Spire", "map": "N34_R01", "spawn": "world"},
    "L_N35": {"name": "Coldharbour Citadel", "map": "N35_R01", "spawn": "world"},
    "L_N36": {"name": "The Aurora Pit", "map": "N36_R01", "spawn": "world"},
}

QUESTS = [
    {"id": "QC09", "name": "The Court of Masks", "start": "N28", "location": "N29", "character": "C09",
     "hook": "Old Kiku, Kitsune's nursemaid, tells her that Tsubaki - the handmaid who wore the Empress's face for the court "
             "after the exile - is to be tried by the Nine-Tailed Magistrate at the Thousand Gates",
     "objectives": "Seek an audience with Regent Shirogane in the Court of Masks; take the summons to the Thousand Gates; "
                   "find the true gate through the illusion maze; stand for Tsubaki in the Magistrate's court; return to Kiku",
     "decision": "Before the court, Kitsune goes masked (as the court expects) or barefaced (as she is); afterwards she "
                 "either takes the throne back unmasked or names Tsubaki regent and leaves the court its own face",
     "result": "The court sees its Empress as she is, and Tsubaki is free of a face that was never hers",
     "reward": "Mirrorbrand (W040), Open-Eye Thread (A012) from the Mirror Walk", "boss": "BX07"},
    {"id": "QC12", "name": "The Cure That Was Sold", "start": "N22", "location": "N25", "character": "C12",
     "hook": "In burned Harrowfen, Corvus's old apprentice Idony says the Weeping Grey has come back with the smoke, and the "
             "only stock of the Mirewold Remedy sits in the Leech Cathedral under a Crown licence",
     "objectives": "Find the licence in the Board of Quarantine's ruined ledger; go to the Leech Cathedral; face Abbot Lamprey "
                   "in the reliquary (or, if he fled into the leech-well before the fault, below it); bring the formula back to Idony",
     "decision": "Publish the formula to every herbalist in the Mirewold, or leave it with Idony's physic house to brew "
                 "safely and teach from",
     "result": "Corvus heals without owning the cure; the fen learns to brew it without him",
     "reward": "Warm Lantern (A015); Salt Locket (A013) from the physic house", "boss": "BX06"},
    {"id": "QC13", "name": "A Court Too Long in Mourning", "start": "N35", "location": "U35", "character": "C13",
     "hook": "At Coldharbour's causeway the Lich King stops: the Frosthorn Warden still keeps his seat shut, and his court still waits inside",
     "objectives": "Pass the Frosthorn Warden; enter the sealed inner court; speak with Chancellor Vesk, Captain Ormund and "
                   "Ysolde; learn that most of the court went down the Lich Stair into the Deep; follow them below (U35)",
     "decision": "Release the three who stayed at Coldharbour, or ask them to keep the seat until the rest come home",
     "result": "(citadel half) The Lich King learns his mourning court did not stay; it followed Mother Sepulchre's call below",
     "reward": "continues at U35 The Lich Stair", "boss": "BX09"},
    {"id": "QW3", "name": "Harrowfen Burning", "start": "N22", "location": "N22", "character": None,
     "hook": "Mother Brannock, at the burned Plague Gate, says the Board's cleansing order is still being carried out in the "
             "Ward - by one warden-captain who will not stop",
     "objectives": "Enter the Burning Ward; find three trapped families; open the lazar-house; face Warden-Captain Ostrey",
     "decision": "Hand Ostrey to the survivors' judgment, or let him carry the sick out with his own hands",
     "result": "The last fire order in Harrowfen is ended by the people it was written against",
     "reward": "Grand Tonic x2, 1500 crowns, Elixir", "boss": None},
    {"id": "QW4", "name": "The Mire Ferry", "start": "N24", "location": "N24", "character": None,
     "hook": "The fault drowned Sickle Hamlet's causeway and sank Old Pike's ferry; Reeve Holloway wants to teach the "
             "party's brackhorn to wade the mire on reed pattens",
     "objectives": "Cut three bundles of ironreed on the Drowned Causeway; find Old Pike on his islet; drive off the mire-beast "
                   "that nests in the sunken road; bring the reed to Granny Sedge for the pattens",
     "decision": "Give Pike the first pair of pattens (he guides wading riders now) or rebuild his punt from the spare reed",
     "result": "Bramble learns to wade: the Fenwader crosses shallows and marsh",
     "reward": "Fenwader (brackhorn_fenwader), Salt-Road Hide", "boss": None},
    {"id": "QW5", "name": "The Fox Court in Exile", "start": "N27", "location": "N28", "character": None,
     "hook": "Lady Hotaru, chancellor of the court in exile at Kaminari Ford, says Regent Shirogane stayed in ruined Akagane "
             "and still holds the old city together with an illusion - and the people who stayed live inside it",
     "objectives": "Light the old beacon at Shiroyama Watch so the scattered court can find the Ford; walk ruined Akagane; "
                   "face the Regent in the broken Court of Masks",
     "decision": "Let the Regent keep the illusion for those who choose it, or ask him to let it fall so everyone sees the ruin",
     "result": "The court chooses what it will look at, for the first time",
     "reward": "Windcord Knot (A111), 2000 crowns", "boss": None},
]
