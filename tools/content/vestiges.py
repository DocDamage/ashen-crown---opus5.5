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


# V13-V24: rewards of the superbosses (WORLD_V2.md section 9; bosses2.VESTIGE_OF). Names by Claude. Granted on the
# superboss victory (Game.expansion_victory) and also by the `vestige Vxx` scene command, so a scene may gate them by
# flag (`sb_sb01_down` etc.). Art: assets/ext/vestiges/<Vxx>.png + .json like V01-V12 (supplied by the lead); until it is
# installed the summon plays with the element rune only (battle_scene._summon_fx fallback), never a crash.
LATE_VESTIGES = {
    "V13": dict(name="Cinder Sovereign", summon="S085", source="SB01", element="fire", art="V13_cinder_sovereign",
                teach=[["S123", 4], ["S121", 6], ["S016", 2]], bonus={"str": 2}, bonus_text="Strength +2"),
    "V14": dict(name="Undertow Queen", summon="S086", source="SB02", element="water", art="V14_undertow_queen",
                teach=[["S130", 5], ["S047", 6], ["S048", 2]], bonus={"mp": 6}, bonus_text="Max MP +6"),
    "V15": dict(name="Stormcrest", summon="S087", source="SB03", element="storm", art="V15_stormcrest",
                teach=[["S158", 6], ["S107", 3], ["S011", 8]], bonus={"spd": 1}, bonus_text="Speed +1"),
    "V16": dict(name="Deepcoil", summon="S088", source="SB04", element="earth", art="V16_deepcoil",
                teach=[["S012", 10], ["S114", 3], ["S055", 4]], bonus={"hp": 30}, bonus_text="Max HP +30"),
    "V17": dict(name="Curator's Echo", summon="S089", source="SB05", element="none", art="V17_curators_echo",
                teach=[["S039", 5], ["S131", 4], ["S138", 3]], bonus={"mag": 2}, bonus_text="Magic +2"),
    "V18": dict(name="Veiled Mother", summon="S090", source="SB06", element="shadow", art="V18_veiled_mother",
                teach=[["S151", 6], ["S153", 3], ["S140", 1]], bonus={"res": 2}, bonus_text="Resistance +2"),
    "V19": dict(name="Crucible Lion", summon="S091", source="SB07", element="none", art="V19_crucible_lion",
                teach=[["S110", 8], ["S114", 4], ["S111", 3]], bonus={"str": 2}, bonus_text="Strength +2"),
    "V20": dict(name="Scale of Taking", summon="S092", source="SB09", element="fire", art="V20_scale_of_taking",
                teach=[["S105", 5], ["S123", 3], ["S116", 1]], bonus={"mag": 2}, bonus_text="Magic +2"),
    "V21": dict(name="Scale of Giving", summon="S093", source="SB10", element="ice", art="V21_scale_of_giving",
                teach=[["S135", 5], ["S137", 3], ["S048", 2]], bonus={"hp": 40}, bonus_text="Max HP +40"),
    "V22": dict(name="The Remaining Choir", summon="S094", source="SB08", element="light", art="V22_remaining_choir",
                teach=[["S043", 8], ["S113", 4], ["S111", 3]], bonus={"res": 2}, bonus_text="Resistance +2"),
    "V23": dict(name="Last Verdict", summon="S095", source="SB11", element="shadow", art="V23_last_verdict",
                teach=[["S146", 4], ["S156", 1], ["S132", 1]], bonus={"def": 2}, bonus_text="Defense +2"),
    "V24": dict(name="The Crown Unmade", summon="S096", source="SB12", element="none", art="V24_crown_unmade",
                teach=[["S016", 3], ["S116", 2], ["S140", 2]], bonus={"str": 1, "mag": 1, "def": 1, "res": 1},
                bonus_text="All stats +1"),
}
VESTIGES.update(LATE_VESTIGES)


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
    # ---- V13-V24 (superboss rewards)
    "S085": ("Cinder Sovereign", "fire", [dmg(300, "magical", "fire", to="enemies", aoe=True),
                                          {"op": "status", "id": "burn", "chance": 60, "to": "enemies"}],
             "Caldera fire on every enemy; 60% Burn."),
    "S086": ("Undertow Queen", "water", [dmg(280, "magical", "water", to="enemies", aoe=True), {"op": "heal", "pct": 0.15, "to": "allies"}],
             "Water on every enemy; heals the party 15%."),
    "S087": ("Stormcrest", "storm", [dmg(290, "magical", "storm", to="enemies", aoe=True), {"op": "status", "id": "haste", "chance": 100, "dur": 3, "to": "allies"}],
             "Storm on every enemy; Haste on the party."),
    "S088": ("Deepcoil", "earth", [dmg(310, "magical", "earth", to="enemies", aoe=True), {"op": "status", "id": "barrier", "chance": 100, "dur": 3, "to": "allies"}],
             "Earth on every enemy; Barrier on the party."),
    "S089": ("Curator's Echo", "none", [dmg(260, "magical", "none", to="enemies", aoe=True), {"op": "dispel_positive", "count": 99, "to": "enemies"},
                                        {"op": "atb", "amount": 300, "to": "allies"}],
             "Strips every enemy's boons; the party's readiness jumps."),
    "S090": ("Veiled Mother", "shadow", [dmg(320, "magical", "shadow", to="enemies", aoe=True, drain=0.2),
                                         {"op": "status", "id": "doom", "chance": 30, "dur": 4, "to": "enemies"}],
             "Shadow on every enemy; 30% Doom."),
    "S091": ("Crucible Lion", "none", [dmg(340, "physical", "physical", to="enemies", aoe=True, no_crit=True),
                                       {"op": "status", "id": "weaken", "chance": 70, "dur": 3, "to": "enemies"}],
             "A champion's charge through every enemy; 70% Weaken."),
    "S092": ("Scale of Taking", "fire", [dmg(360, "magical", "fire", to="enemies", aoe=True), {"op": "mp", "amount": 30, "to": "allies"}],
             "Fire on every enemy; the party regains 30 MP."),
    "S093": ("Scale of Giving", "ice", [dmg(330, "magical", "ice", to="enemies", aoe=True), {"op": "heal", "pct": 0.25, "to": "allies"}],
             "Ice on every enemy; heals the party 25%."),
    "S094": ("The Remaining Choir", "light", [{"op": "heal", "power": 220, "to": "allies"},
                                              {"op": "cleanse", "ids": ["poison", "burn", "bleed", "silence", "sleep", "blind", "doom", "slow", "weaken"], "to": "allies"},
                                              dmg(240, "magical", "light", to="enemies", aoe=True)],
             "Heals and cures the party; light on every enemy."),
    "S095": ("Last Verdict", "shadow", [dmg(380, "magical", "shadow", to="enemies", aoe=True), {"op": "status", "id": "guardbreak", "chance": 100, "dur": 3, "to": "enemies"}],
             "Shadow on every enemy; Guardbreak."),
    "S096": ("The Crown Unmade", "none", [dmg(480, "magical", "none", to="enemies", aoe=True, uncapped=True)],
             "The unmaking itself, on every enemy. Breaks the damage limit."),
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
