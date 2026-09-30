"""Encounter formations, groups, shops, speakers and locations (authored layer; docs/10 formation policy)."""

def F(enemies, bg, music="M025", boss=False, hint="", **kw):
    d = {"enemies": enemies, "bg": bg, "music": music, "boss": boss, "hint": hint}
    d.update(kw)
    return d

def v(eid, level):
    return {"id": eid, "level": level}

FORMATIONS = {
    # D01 Crown Quarry (L2-4)
    "D01_1": F(["E001", "E001"], "quarry", hint="Attack and Defend are always available."),
    "D01_2": F(["E002"], "quarry", hint="The beetle shells up every other action - hit it while it is open."),
    "D01_3": F(["E003", "E001"], "quarry", hint="Any direct hit interrupts the wisp's announced charge."),
    "D01_4": F(["E004", "E002"], "quarry", hint="The hound marks its target before lunging. Defend the marked ally."),
    "D01_5": F(["E004", "E001", "E001"], "quarry"),
    "D01_T": F([v("E001", 1)], "quarry", tutorial=True, scripted_start=True, hint="Choose Attack, then pick the rat."),
    # D02 Veyr Underways (L4-6)
    "D02_1": F(["E005"], "underways", hint="Canal slimes split once when badly hurt."),
    "D02_2": F(["E006", "E008"], "underways"),
    "D02_3": F(["E007", "E007"], "underways", hint="Ledger moths return what they steal when defeated."),
    "D02_4": F(["E008", "E005"], "underways"),
    "D02_5": F(["E006", "E007", "E005"], "underways"),
    # D03 Rootward (L6-8)
    "D03_1": F(["E009", "E009"], "grove"),
    "D03_2": F(["E010", "E011"], "grove"),
    "D03_3": F(["E012", "E009"], "grove"),
    "D03_4": F(["E011", "E010", "E010"], "grove", hint="Burn or cleanse: fire is strong against the grove."),
    # D04 Furnace Spine (L8-11)
    "D04_1": F(["E013", "E013"], "furnace"),
    "D04_2": F(["E014"], "furnace", hint="Hit the crab while pressure builds to weaken its burst."),
    "D04_3": F(["E015", "E016"], "furnace"),
    "D04_4": F(["E016", "E013"], "furnace", hint="Defend when the fist rises."),
    "D04_5": F(["E014", "E015"], "furnace"),
    # D05 Drowned Archive (L10-13)
    "D05_1": F(["E017", "E018"], "archive"),
    "D05_2": F(["E019"], "archive", hint="Bell Divers are undead: healing magic hurts them."),
    "D05_3": F(["E020", "E017"], "archive"),
    "D05_4": F(["E018", "E019", "E017"], "archive"),
    # D06 Skychain (L12-15)
    "D06_1": F(["E021", "E021"], "sky"),
    "D06_2": F(["E022"], "sky"),
    "D06_3": F(["E023"], "sky", hint="The golem winds up slowly: Defend or finish it first."),
    "D06_4": F(["E024", "E021"], "sky"),
    "D06_5": F(["E022", "E024"], "sky"),
    # D07 Whitebone (L14-17)
    "D07_1": F(["E025"], "whitebone"),
    "D07_2": F(["E026", "E027"], "whitebone"),
    "D07_3": F(["E028", "E027"], "whitebone"),
    "D07_4": F(["E025", "E026"], "whitebone"),
    "D07_5": F(["E027", "E027", "E028"], "whitebone"),
    # D08 Memory Vault (L17-20)
    "D08_1": F(["E029", "E029"], "vault"),
    "D08_2": F(["E030", "E031"], "vault"),
    "D08_3": F(["E032"], "vault"),
    "D08_4": F(["E030", "E029", "E031"], "vault"),
    # D09 Sable Conduit (L20-24)
    "D09_1": F(["E033", "E034"], "conduit"),
    "D09_2": F(["E035", "E035"], "conduit"),
    "D09_3": F(["E036"], "conduit"),
    "D09_4": F(["E033", "E036", "E035"], "conduit"),
    "D09_5": F(["E034", "E034"], "conduit"),
    # D10 Crown Heart (L34-42)
    "D10_1": F(["E037"], "crown"),
    "D10_2": F(["E038", "E037"], "crown"),
    "D10_3": F(["E039", "E040"], "crown"),
    "D10_4": F(["E040", "E038"], "crown"),
    "D10_5": F(["E037", "E039", "E038"], "crown"),
    # D11 Cradle of Winter (optional, L30-35)
    "D11_1": F([v("E027", 32), v("E027", 32)], "winter"),
    "D11_2": F([v("E039", 32)], "winter"),
    "D11_3": F([v("E025", 32), v("E024", 32)], "winter"),
    "D11_4": F([v("E011", 33), v("E027", 33)], "winter"),
    # D12 Starless Reef (optional, L34-39)
    "D12_1": F([v("E019", 36), v("E018", 36)], "reef"),
    "D12_2": F([v("E029", 36), v("E035", 36)], "reef"),
    "D12_3": F([v("E037", 37)], "reef"),
    "D12_4": F([v("E012", 37), v("E019", 37)], "reef"),
    # Post-state revisits (explicit variants, not new identities)
    "D03P_1": F([v("E009", 22), v("E009", 22)], "grove_flood"),
    "D03P_2": F([v("E012", 22), v("E010", 22)], "grove_flood"),
    "D03P_3": F([v("E011", 23), v("E009", 23)], "grove_flood"),
    "D05P_1": F([v("E017", 24), v("E018", 24)], "archive"),
    "D05P_2": F([v("E019", 24), v("E020", 24)], "archive"),
    "D04P_1": F([v("E013", 25), v("E016", 25)], "furnace"),
    "D04P_2": F([v("E014", 25), v("E015", 25)], "furnace"),
    "D06P_1": F([v("E021", 27), v("E023", 27)], "sky"),
    "D06P_2": F([v("E022", 27), v("E024", 27)], "sky"),
    "D02P_1": F([v("E005", 28), v("E006", 28)], "underways"),
    "D02P_2": F([v("E007", 28), v("E008", 28)], "underways"),
    "D07P_1": F([v("E026", 28), v("E028", 28)], "whitebone"),
    # Overworld
    "OW1_1": F(["E001", "E004"], "field_r01"),
    "OW1_2": F([v("E009", 5)], "field_r01"),
    "OW2_1": F(["E013", "E016"], "field_r02"),
    "OW2_2": F([v("E015", 9), v("E013", 9)], "field_r02"),
    "OW3_1": F(["E017", v("E012", 11)], "field_r03"),
    "OW3_2": F([v("E018", 11), v("E018", 11)], "field_r03"),
    "OW4_1": F(["E021", "E022"], "field_r04"),
    "OW5_1": F(["E027", "E030"], "field_r05"),
    "OW5_2": F([v("E026", 17), v("E029", 17)], "field_r05"),
    "OWP_1": F([v("E034", 27), v("E027", 27)], "field_post"),
    "OWP_2": F([v("E038", 28)], "field_post"),
    "OWP_3": F([v("E022", 27), v("E024", 27)], "field_post"),
    # Bosses
    "B01": F(["B01"], "quarry", "M026", True, hint="Watch the red gauge: Defend the marked ally, strike the valve, or use the Storm Flask."),
    "B02": F(["B02"], "underways", "M026", True, hint="The warrant names its target before the restraint."),
    "B03": F(["B03"], "grove", "M026", True, hint="Burn the root before it binds the back row."),
    "B04": F(["B04"], "furnace", "M026", True, hint="Ice and Defend blunt the boiler sweep."),
    "B05": F(["B05"], "archive", "M026", True, hint="The vibrating bell mirrors the last element used."),
    "B06": F(["B06"], "sky", "M026", True, hint="The shadow marks which row the dive will strike."),
    "B07": F(["B07"], "whitebone", "M026", True, hint="The sigil tells you whether skills or strength will be sealed."),
    "B08": F(["B08"], "vault", "M026", True, hint="Vary your commands; Defend through the echo."),
    "B09": F(["B09"], "conduit", "M026", True, hint="Voss points at a protector before his orders."),
    "B10": F(["B10"], "dais", "M026", True, hint="Break an active relay or Defend when three lights show."),
    "B11": F(["B11"], "grove_flood", "M026", True, hint="Strike the current valve before the surge notch."),
    "B12": F(["B12"], "crown_core", "M028", True, hint="Phase 1 separate targets; Phase 2 vary commands; Phase 3 Defend during the release."),
    "B13": F(["B13"], "winter", "M026", True, hint="Relight the dark lantern with fire to weaken its choice."),
    "B14": F(["B14"], "reef", "M026", True, hint="Beacons flash before the tide returns to the front row."),
    "B15": F(["B15"], "underways", "M026", True, hint="The screen names the edict - Defend or dispel."),
    "B16": F(["B16"], "crown", "M026", True, hint="Defend through silence; act through response."),
}

GROUPS = {
    "D01": ["D01_1", "D01_2", "D01_3", "D01_4", "D01_5"],
    "D01E": ["D01_1", "D01_2"],
    "D02": ["D02_1", "D02_2", "D02_3", "D02_4", "D02_5"],
    "D03": ["D03_1", "D03_2", "D03_3", "D03_4"],
    "D04": ["D04_1", "D04_2", "D04_3", "D04_4", "D04_5"],
    "D05": ["D05_1", "D05_2", "D05_3", "D05_4"],
    "D06": ["D06_1", "D06_2", "D06_3", "D06_4", "D06_5"],
    "D07": ["D07_1", "D07_2", "D07_3", "D07_4", "D07_5"],
    "D08": ["D08_1", "D08_2", "D08_3", "D08_4"],
    "D09": ["D09_1", "D09_2", "D09_3", "D09_4", "D09_5"],
    "D10": ["D10_1", "D10_2", "D10_3", "D10_4", "D10_5"],
    "D11": ["D11_1", "D11_2", "D11_3", "D11_4"],
    "D12": ["D12_1", "D12_2", "D12_3", "D12_4"],
    "D03P": ["D03P_1", "D03P_2", "D03P_3"],
    "D05P": ["D05P_1", "D05P_2"],
    "D04P": ["D04P_1", "D04P_2"],
    "D06P": ["D06P_1", "D06P_2"],
    "D02P": ["D02P_1", "D02P_2"],
    "D07P": ["D07P_1"],
    "OW1": ["OW1_1", "OW1_2"], "OW2": ["OW2_1", "OW2_2"], "OW3": ["OW3_1", "OW3_2"], "OW4": ["OW4_1"],
    "OW5": ["OW5_1", "OW5_2"], "OWP": ["OWP_1", "OWP_2", "OWP_3"],
}

SHOPS = {
    "SHOP_T01": {"name": "Brackenford Store", "kinds": ["items", "weapons", "armor"], "town": "T01"},
    "SHOP_T02": {"name": "South Market", "kinds": ["items", "weapons", "armor", "accessories"], "town": "T02"},
    "SHOP_T03": {"name": "Canteen Counter", "kinds": ["items", "weapons", "armor"], "town": "T03"},
    "SHOP_T04": {"name": "Chartmaker Stalls", "kinds": ["items", "weapons", "armor", "accessories"], "town": "T04"},
    "SHOP_T05": {"name": "Cable Court Traders", "kinds": ["items", "weapons", "armor", "accessories"], "town": "T05"},
    "SHOP_T06": {"name": "Salt Market", "kinds": ["items", "weapons", "armor", "accessories"], "town": "T06"},
    "SHOP_T07": {"name": "Ponton Market", "kinds": ["items", "weapons", "armor", "accessories"], "town": "T07"},
    "SHOP_SHIP": {"name": "Wayfarer Stores", "kinds": ["items"], "town": "SHIP"},
}

# speaker id -> display name, portrait key (character id or npc sprite)
SPEAKERS = {
    "dain": ["Dain", "C01"], "tessa": ["Tessa", "C02"], "corren": ["Corren", "C03"], "ivo": ["Ivo", "C04"],
    "nera": ["Nera", "C05"], "oriel": ["Oriel", "C06"], "sable": ["Sable", "C07"], "pip": ["Pip", "C08"],
    "ilyr": ["Ilyr", "ilyr"], "mara": ["Mara", "mara"], "inspector": ["Inspector Holt", "inspector"],
    "rook": ["Rook", "rook"], "voss": ["Voss", "voss"], "pell": ["Pell", "pell"], "jori": ["Jori", "jori"],
    "edda": ["Edda", "edda"], "sen": ["Sen", "sen"], "ansel": ["Ansel", "ansel"], "guard": ["Guard", "guard"],
    "worker": ["Worker", "worker"], "narr": ["", ""], "clerk": ["Clerk", "clerk"], "volunteer": ["Volunteer", "volunteer"],
    "survivor": ["Survivor", "survivor"], "child": ["Child", "child"], "elder": ["Elder", "elder"], "pilot": ["Old Pilot", "elder"],
    "sign": ["", ""], "apprentice": ["Apprentice", "apprentice"], "patient": ["Patient", "patient"], "officer": ["Officer", "guard"],
    "hind": ["Winter Hind", "hind"], "leviathan": ["Night Leviathan", "leviathan"], "cantor": ["Null Cantor", "cantor"],
    "echo": ["Regent's Echo", "echo"], "stag": ["Rootstag", "stag"], "moth": ["Ember Moth", "moth"],
    "whale": ["Tide Serpent", "whale"], "manta": ["Sky Griffon", "manta"], "fox": ["Lumen Fox", "fox"], "tortoise": ["Iron Tortoise", "tortoise"],
    "baker": ["Baker", "baker"], "keeper": ["Storekeeper", "keeper"], "sailor": ["Sailor", "sailor"],
    # overhaul: new Vestiges and heroes (portraits: assets/portraits/<key>.png, heroes/<cid>/portrait.png)
    "colossus": ["Grove Colossus", "colossus"], "thorn": ["Thorn Queen", "thorn"], "wyrm": ["Ash Wyrm", "wyrm"],
    "wraith": ["Winter Wraith", "wraith"],
    "kitsune": ["Kitsune", "C09"], "archangel": ["Archangel", "C10"], "inferna": ["Inferna", "C11"], "corvus": ["Corvus", "C12"],
    "lich": ["Lich King", "C13"], "maldrath": ["Maldrath", "C14"], "velkhar": ["Velkhar", "C15"], "kael": ["Kael-09", "C16"],
    "rider": ["Night Rider", "C17"], "namer": ["Name-Keeper", "namer"],
}

# Stable location IDs shared by both overworld states.
LOCATIONS = {
    "L_T01": {"name": "Brackenford", "map": "T01_PLATFORM", "spawn": "world"},
    "L_D01": {"name": "Crown Quarry", "map": "D01_R01", "spawn": "world"},
    "L_T02": {"name": "Veyr", "map": "T02_MARKET", "spawn": "world"},
    "L_D03": {"name": "Rootward", "map": "D03_R01", "spawn": "world"},
    "L_T03": {"name": "Cinderwake", "map": "T03_CANTEEN", "spawn": "world"},
    "L_D04": {"name": "Furnace Spine", "map": "D04_R01", "spawn": "world"},
    "L_T04": {"name": "Bellharbor", "map": "T04_QUAY", "spawn": "world"},
    "L_D05": {"name": "Drowned Archive", "map": "D05_R01", "spawn": "world"},
    "L_D06": {"name": "Skychain Viaduct", "map": "D06_R01", "spawn": "world"},
    "L_T05": {"name": "High Aerie", "map": "T05_COURT", "spawn": "world"},
    "L_D07": {"name": "Whitebone Redoubt", "map": "D07_R01", "spawn": "world"},
    "L_T06": {"name": "Nacre", "map": "T06_MARKET", "spawn": "world"},
    "L_D08": {"name": "Memory Vault", "map": "D08_R01", "spawn": "world"},
    "L_D09": {"name": "Sable Conduit", "map": "D09_R01", "spawn": "world"},
    "L_T07": {"name": "Hearthward", "map": "T07_MARKET", "spawn": "world"},
    "L_D10": {"name": "Crown Heart", "map": "D10_R01", "spawn": "world"},
    "L_D11": {"name": "Cradle of Winter", "map": "D11_R01", "spawn": "world"},
    "L_D12": {"name": "Starless Reef", "map": "D12_R01", "spawn": "world"},
}
