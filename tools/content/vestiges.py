"""Vestiges (brief decision 55): twelve summons that teach magic like FF6 Espers.

A Vestige linked to a hero (one each) gives, after every won battle, learning progress on each spell it teaches
(progress += rate x battle AP; AP 1, bosses 3); at 100 the hero knows the spell for good. When the linked hero levels
up, the Vestige's level-up bonus is added permanently. V03 is now Tide Serpent (was Bell Whale) and V04 Sky Griffon
(was Sky Manta); V09-V12 are new (art in Assets/_processed/vestiges).
"""

VESTIGES = {
    "V01": dict(name="Ember Moth", summon="S073", source="CH01", element="fire", art="V01_ember_moth",
                teach=[["S065", 10], ["S009", 5]], bonus={"mag": 1}, bonus_text="Magic +1"),
    "V02": dict(name="Rootstag", summon="S074", source="CH03", element="earth", art="V02_rootstag",
                teach=[["S069", 10], ["S012", 5], ["S036", 3]], bonus={"hp": 12}, bonus_text="Max HP +12"),
    "V03": dict(name="Tide Serpent", summon="S075", source="CH06", element="water", art="V03_tide_serpent",
                teach=[["S068", 10], ["S047", 5], ["S042", 4]], bonus={"res": 1}, bonus_text="Resistance +1"),
    "V04": dict(name="Sky Griffon", summon="S076", source="CH07", element="storm", art="V04_sky_griffon",
                teach=[["S067", 10], ["S011", 5], ["S027", 4]], bonus={"spd": 1}, bonus_text="Speed +1"),
    "V05": dict(name="Lumen Fox", summon="S077", source="CH09", element="light", art="V05_lumen_fox",
                teach=[["S041", 8], ["S072", 6], ["S043", 3]], bonus={"mag": 1}, bonus_text="Magic +1"),
    "V06": dict(name="Iron Tortoise", summon="S078", source="CH16", element="none", art="V06_iron_tortoise",
                teach=[["S055", 5], ["S046", 3], ["S110", 6]], bonus={"def": 1}, bonus_text="Defense +1"),
    "V07": dict(name="Winter Hind", summon="S079", source="Q09", element="ice", art="V07_winter_hind",
                teach=[["S066", 10], ["S010", 5], ["S135", 2]], bonus={"res": 1}, bonus_text="Resistance +1"),
    "V08": dict(name="Night Leviathan", summon="S080", source="Q10", element="shadow", art="V08_night_leviathan",
                teach=[["S071", 10], ["S014", 2], ["S151", 3]], bonus={"mp": 4}, bonus_text="Max MP +4"),
    "V09": dict(name="Grove Colossus", summon="S081", source="SIDE:grove", element="earth", art="V09_grove_colossus",
                teach=[["S130", 3], ["S026", 8], ["S044", 2]], bonus={"hp": 15}, bonus_text="Max HP +15"),
    "V10": dict(name="Thorn Queen", summon="S082", source="SIDE:thorn", element="poison", art="V10_thorn_queen",
                teach=[["S125", 8], ["S070", 6], ["S129", 2]], bonus={"str": 1}, bonus_text="Strength +1"),
    "V11": dict(name="Ash Wyrm", summon="S083", source="SIDE:ember", element="fire", art="V11_ash_wyrm",
                teach=[["S121", 4], ["S123", 2], ["S016", 1]], bonus={"str": 1}, bonus_text="Strength +1"),
    "V12": dict(name="Winter Wraith", summon="S084", source="SIDE:winter", element="shadow", art="V12_winter_wraith",
                teach=[["S137", 2], ["S139", 2], ["S048", 1]], bonus={"mag": 1}, bonus_text="Magic +1"),
}


def dmg(power, typ, element, **kw):
    d = {"op": "damage", "power": power, "type": typ, "element": element}
    d.update(kw)
    return d


NEW_SUMMONS = {
    "S081": ("Grove Colossus", "earth", [dmg(200, "magical", "earth", to="enemies", aoe=True), {"op": "heal", "pct": 0.12, "to": "allies"}],
             "Earth on every enemy; heals the party 12%."),
    "S082": ("Thorn Queen", "none", [dmg(160, "magical", "none", to="enemies", aoe=True),
                                     {"op": "status", "id": "poison", "chance": 80, "to": "enemies"},
                                     {"op": "status", "id": "weaken", "chance": 50, "dur": 3, "to": "enemies"}],
             "Thorns on every enemy; 80% Poison, 50% Weaken."),
    "S083": ("Ash Wyrm", "fire", [dmg(260, "magical", "fire", to="enemies", aoe=True)], "Fire on every enemy."),
    "S084": ("Winter Wraith", "ice", [dmg(230, "magical", "ice", to="enemies", aoe=True),
                                      {"op": "status", "id": "slow", "chance": 60, "to": "enemies"}],
             "Ice on every enemy; 60% Slow."),
}


def apply(content, check=None):
    ab = content["abilities"]
    for aid, (name, elem, ops, desc) in NEW_SUMMONS.items():
        if check:
            check(aid, ops)
        ab[aid] = {"id": aid, "name": name, "owner": "", "mp": 0, "power": 0, "kind": "summon", "target": "enemy_all",
                   "desc": desc, "ops": ops, "family": "summon", "anim": "cast", "element": elem, "elemental_spell": False,
                   "revive": False, "field": False, "concord": True}
    # the renamed summons follow their Vestiges
    ab["S075"]["name"] = "Tide Serpent"
    ab["S076"]["name"] = "Sky Griffon"
    for v in VESTIGES.values():
        for aid, _ in v["teach"]:
            assert aid in ab, aid
    content["vestiges"] = {k: dict(v) for k, v in VESTIGES.items()}
    return content
