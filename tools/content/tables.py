"""Authored numeric/table decisions not present in the supplied handoff (recorded in reports/decisions.md)."""

# Level-1 base stats (hp1/mp1 etc. were referenced to missing JSON; authored here).
CHAR_BASE = {
    "C01": dict(hp=120, mp=12, str=12, mag=5, df=10, res=5, spd=8),
    "C02": dict(hp=80, mp=24, str=5, mag=13, df=5, res=10, spd=11),
    "C03": dict(hp=105, mp=12, str=12, mag=5, df=8, res=6, spd=12),
    "C04": dict(hp=110, mp=16, str=9, mag=10, df=8, res=8, spd=7),
    "C05": dict(hp=95, mp=14, str=11, mag=6, df=7, res=7, spd=14),
    "C06": dict(hp=85, mp=26, str=5, mag=12, df=6, res=11, spd=9),
    "C07": dict(hp=100, mp=18, str=10, mag=10, df=8, res=8, spd=10),
    "C08": dict(hp=90, mp=14, str=10, mag=6, df=6, res=6, spd=16),
}
# From docs/07 (hp growth, mp growth, STR/MAG growth).
HP_G = dict(C01=54, C02=40, C03=49, C04=51, C05=45, C06=42, C07=48, C08=43)
MP_G = dict(C01=3, C02=6, C03=3, C04=4, C05=3, C06=6, C07=4, C08=3)
SM_G = dict(C01=(2, 1), C02=(1, 2), C03=(2, 1), C04=(1, 2), C05=(2, 1), C06=(1, 2), C07=(2, 2), C08=(2, 1))

STARTER = {  # tier-1 weapon + ordinary initial equipment
    "C01": dict(weapon="W001", offhand="G025", head="G017", body="G013"),
    "C02": dict(weapon="W007", head="G018", body="G001"),
    "C03": dict(weapon="W013", head="G017", body="G009"),
    "C04": dict(weapon="W019", head="G019", body="G009"),
    "C05": dict(weapon="W025", head="G018", body="G005"),
    "C06": dict(weapon="W031", head="G018", body="G001"),
    "C07": dict(weapon="W037", head="G017", body="G009"),
    "C08": dict(weapon="W043", head="G018", body="G005"),
}
TWO_HANDED_OWNERS = {"C03", "C04", "C05", "C06"}
RANGED_OWNERS = {"C05"}
WEAPON_ELEMENT = {}

ULTIMATE_PASSIVES = {
    "W006": {"oath_guard_10": True}, "W012": {"overcast_5": True}, "W018": {"landing_heal": True},
    "W024": {"patch_burn": True}, "W030": {"mark_plus1": True}, "W036": {"cleanse_doom": True},
    "W042": {"infusion_plus2": True}, "W048": {"pilfer_refund": True},
}
ACCESSORY = {
    "A001": {"grants": "S065"}, "A002": {"grants": "S066"}, "A003": {"grants": "S067"}, "A004": {"grants": "S068"},
    "A005": {"grants": "S069"}, "A006": {"grants": "S070"}, "A007": {"grants": "S071"}, "A008": {"grants": "S072"},
    "A009": {"passives": {"phys_reduce": 0.1}}, "A010": {"passives": {"reveal_affinity": True}},
    "A011": {"passives": {"immune": ["silence"]}}, "A012": {"passives": {"immune": ["blind", "sleep"]}},
    "A013": {"passives": {"immune": ["poison", "burn"]}}, "A014": {"passives": {"acc_bonus": 10}},
    "A015": {"passives": {"heal_mult": 1.15}}, "A016": {"passives": {"mmp_mult": 1.15}},
    "A017": {"passives": {"mhp_mult": 1.15}}, "A018": {"passives": {"counter": 0.5}},
    "A019": {"passives": {"twohand_mult": 1.15}}, "A020": {"passives": {"mercy_barrier": True}},
    "A021": {"passives": {"start_atb": 100}}, "A022": {"passives": {"encounter_mult": 0.75}},
    "A023": {"passives": {"dispel_ward": True}}, "A024": {"passives": {"concord_bonus": 2}},
}
# Accessory shop availability: chapter after which it is stocked (None = quest/secret only first).
ACCESSORY_SHOP = {"A001": "CH01", "A002": "CH02", "A003": "CH03", "A004": "CH04", "A005": "CH06", "A006": "CH07",
                  "A007": "CH08", "A008": "CH09", "A009": "CH06", "A010": "CH06", "A011": "CH08", "A012": "CH08",
                  "A013": "CH08", "A014": "CH08", "A015": "CH16", "A016": "CH16", "A017": "CH16", "A018": "CH16",
                  "A019": "CH20", "A020": "CH20", "A021": "CH20", "A022": "CH16"}
ARMOR_TIER = {}
for base, ids in [(0, ["G001", "G002", "G003", "G004"]), (0, ["G005", "G006", "G007", "G008"]),
                  (0, ["G009", "G010", "G011", "G012"]), (0, ["G013", "G014", "G015", "G016"])]:
    for i, x in enumerate(ids):
        ARMOR_TIER[x] = i + 1
for i, x in enumerate(["G017", "G018", "G019", "G020", "G021", "G022", "G023", "G024"]):
    ARMOR_TIER[x] = i // 2 + 1
ARMOR_TIER.update({"G025": 1, "G026": 2, "G027": 3, "G028": 4, "G029": 2, "G030": 4, "G031": 3, "G032": 4})
TIER_CHAPTER_WEAPON = {1: "CH01", 2: "CH04", 3: "CH08", 4: "CH16", 5: "CH20"}
TIER_CHAPTER_ARMOR = {1: "CH01", 2: "CH06", 3: "CH16", 4: "CH20"}

CONSUMABLE = {
    "I001": dict(target="ally_one", ops=[{"op": "heal", "flat": 250}], field=True),
    "I002": dict(target="ally_one", ops=[{"op": "heal", "flat": 900}], field=True),
    "I003": dict(target="ally_one", ops=[{"op": "heal", "flat": 1800}], field=True),
    "I004": dict(target="ally_one", ops=[{"op": "mp", "amount": 40}], field=True),
    "I005": dict(target="ally_one", ops=[{"op": "mp", "amount": 100}], field=True),
    "I006": dict(target="ally_one", revive=True, ops=[{"op": "revive", "pct": 0.25}], field=True),
    "I007": dict(target="ally_one", ops=[{"op": "cleanse", "ids": ["poison", "burn", "bleed", "blind", "sleep", "silence"]}]),
    "I008": dict(target="ally_one", ops=[{"op": "cleanse", "ids": ["blind"]}]),
    "I009": dict(target="ally_one", ops=[{"op": "cleanse", "ids": ["poison"]}]),
    "I010": dict(target="ally_one", ops=[{"op": "cleanse", "ids": ["sleep"]}]),
    "I011": dict(target="ally_one", ops=[{"op": "cleanse", "ids": ["burn"]}]),
    "I012": dict(target="ally_one", ops=[{"op": "cleanse", "ids": ["silence"]}]),
    "I013": dict(target="party", ops=[], battle=False, field=True, special="tent"),
    "I014": dict(target="self", ops=[{"op": "flee", "amount": 600}]),
    "I015": dict(target="enemy_one", ops=[{"op": "damage", "power": 120, "type": "magical", "element": "fire", "fixed_mag": 30}]),
    "I016": dict(target="enemy_one", ops=[{"op": "damage", "power": 120, "type": "magical", "element": "ice", "fixed_mag": 30}]),
    "I017": dict(target="enemy_one", ops=[{"op": "damage", "power": 120, "type": "magical", "element": "storm", "fixed_mag": 30}]),
    "I018": dict(target="ally_one", ops=[{"op": "status", "id": "barrier", "chance": 100, "dur": 3}]),
    "I019": dict(target="enemy_one", ops=[{"op": "status", "id": "slow", "chance": 85}]),
    "I020": dict(target="self", ops=[]),
    "I021": dict(target="ally_all", ops=[{"op": "heal", "flat": 200}], field=True),
    "I022": dict(target="party", ops=[], battle=False, field=True, special="waystone"),
    "I023": dict(target="ally_one", ops=[{"op": "cleanse", "ids": ["doom", "bleed"]}]),
    "I024": dict(target="ally_one", ops=[{"op": "full_restore"}], field=True),
}
BASIC_STOCK = ["I001", "I004", "I006", "I007", "I008", "I009", "I010", "I011", "I012", "I013"]
EXPANDED_STOCK = ["I002", "I005", "I014", "I015", "I016", "I017", "I018", "I019", "I020", "I021", "I022", "I023"]
LATE_STOCK = ["I003"]  # CH16

STATUS_DURATION = {"poison": 3, "burn": 3, "bleed": 3, "silence": 2, "sleep": 1, "stun": 1, "slow": 3, "haste": 3,
                   "barrier": 3, "regen": 3, "mark": 4, "guardbreak": 3, "blind": 2, "doom": 3, "weaken": 3, "focus": 3}

VESTIGES = {
    "V01": dict(name="Ember Moth", summon="S073", source="CH01"), "V02": dict(name="Rootstag", summon="S074", source="CH03"),
    "V03": dict(name="Bell Whale", summon="S075", source="CH06"), "V04": dict(name="Sky Manta", summon="S076", source="CH07"),
    "V05": dict(name="Lumen Fox", summon="S077", source="CH09"), "V06": dict(name="Iron Tortoise", summon="S078", source="CH16"),
    "V07": dict(name="Winter Hind", summon="S079", source="Q09"), "V08": dict(name="Night Leviathan", summon="S080", source="Q10"),
}

BOSS_LEVEL = dict(B01=4, B02=6, B03=8, B04=11, B05=13, B06=15, B07=17, B08=20, B09=23, B10=24, B11=24, B12=40,
                  B13=35, B14=38, B15=36, B16=40)

KEY_ITEMS = {
    "K_WORKER_LIST": "Worker List", "K_LEDGER": "Ministry Ledger", "K_MANIFEST": "Shipping Manifest",
    "K_CONFISCATED": "Confiscated Ledger", "K_ROOK_EVIDENCE": "Rook's Evidence", "K_RELEASE_KEYS": "Consent Keys",
    "K_TESTIMONY": "Vault Testimony", "K_ACCORD_NOTES": "Local Release Notes", "K_MANUAL": "Maintenance Manual",
    "K_ROUTE_DIAGRAMS": "Hidden Route Diagrams", "K_MEMORIAL_RECORDS": "Named Records", "K_LOW_CIRCUIT": "Low-Power Circuit",
    "K_FLIGHT_RECORDER": "Flight Recorder", "K_REVISED_MANUAL": "Revised Manual", "K_ROUTE_SCHEDULE": "Shared Schedule",
    "K_AUTHORIZATION": "Original Authorization", "K_SEAL_DESIGN": "Seal Design Record", "K_OFFICIAL_SEAL": "Assembly Seal",
    "K_LISTENING_PHRASE": "Listening Phrase", "K_PASSENGER_REGISTER": "Passenger Register", "K_COMMAND_LEDGER": "Command Ledger",
    "K_FERRY_PASS": "Ferry Pass", "K_CABLE_PASS": "Cable Pass",
}
