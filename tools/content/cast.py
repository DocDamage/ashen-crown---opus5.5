"""Overhaul cast (owner-approved mapping, 2026-09-29; brief decisions 29-39, 54, 61).

The eight original party roles keep their ids (C01-C08), stats, kits and story functions; they take the new heroes'
names and identities. Nine heroes are added: four story members (C09-C12) and five secret recruits (C13-C17), each
with a new kit of eight abilities (seven learned by level, an ultimate at level 40) and a signature command.
New heroes use an original hero's equipment class (EQUIP_AS).
"""

RENAME = {
    "C01": dict(name="Raven, the Executioner", short="Raven", identity="man", role="Executioner",
                summary="The crown's executioner, who refuses the order he was sent to carry out."),
    "C02": dict(name="Morwen, Witch of the Eclipse", short="Morwen", identity="woman", role="Eclipse witch",
                summary="A brilliant fugitive witch who treats every warning as an attempt to control her."),
    "C03": dict(name="Vespera, Moonhare Warrior", short="Vespera", identity="woman", role="Moonhare dragoon",
                summary="A celebrated aerial guard of the moonhare folk, trained to make dying look noble."),
    "C04": dict(name="Rune Golem", short="Golem", identity="construct (he)", role="Rune machinist",
                summary="A working golem who kept the relays running and now wants to choose his own work."),
    "C05": dict(name="Elowen, Guardian of the Moonlit Grove", short="Elowen", identity="woman", role="Grove ranger",
                summary="The Moonlit Grove's displaced guardian, who trusts routes more than institutions."),
    "C06": dict(name="Aurex, Dragonblood Champion", short="Aurex", identity="man", role="Dragonblood oracle",
                summary="A champion whose dragon blood carries memory and visions his order mistook for divine law."),
    "C07": dict(name="Crimson Oni", short="Oni", identity="man", role="Oni spellblade",
                summary="A former binding officer, an oni soldier who broke rank and wants one act to cancel his record."),
    "C08": dict(name="Sak, Guardian of the Cat Kingdom", short="Sak", identity="man", role="Cat rogue",
                summary="A guardian of the Cat Kingdom who saves people by making the authorities believe they are dead."),
}
COMMAND = {"C04": "Runeworks", "C06": "Dragonsong", "C07": "Bladecraft"}

EQUIP_AS = {"C09": "C07", "C10": "C01", "C11": "C03", "C12": "C06", "C13": "C02", "C14": "C01", "C15": "C02",
            "C16": "C08", "C17": "C04"}

NEW = {
    "C09": dict(name="Crimson Kitsune Empress", short="Kitsune", identity="woman", role="Fox spellblade", secret=False,
                command="Foxfire", base=dict(hp=96, mp=20, str=10, mag=11, df=7, res=9, spd=15), growth=(46, 4, 2, 2),
                summary="The exiled empress of the fox court, who fights with illusions and fox fire.",
                arc="Stop ruling through what others believe she is; let the court see her as she is."),
    "C10": dict(name="Archangel Commander", short="Archangel", identity="man", role="Seraph knight", secret=False,
                command="Judgment", base=dict(hp=118, mp=18, str=12, mag=9, df=10, res=9, spd=9), growth=(52, 4, 2, 1),
                summary="A commander of a sky host that stopped answering, still keeping its last order.",
                arc="Judge by what he sees, not by the order he was given."),
    "C11": dict(name="Inferna, Abyssal Valkyrie", short="Inferna", identity="woman", role="Abyssal valkyrie", secret=False,
                command="Hellbrand", base=dict(hp=104, mp=14, str=13, mag=8, df=8, res=6, spd=12), growth=(50, 3, 2, 1),
                summary="A valkyrie bound to carry souls into the abyss, who now carries the living out of it.",
                arc="Redemption: undo the bargains she enforced, one name at a time."),
    "C12": dict(name="Corvus, Harbinger of Pestilence", short="Corvus", identity="man", role="Plague doctor", secret=False,
                command="Physic", base=dict(hp=86, mp=24, str=6, mag=12, df=6, res=10, spd=10), growth=(42, 6, 1, 2),
                summary="A plague doctor once sent to spread sickness, now the party's healer.",
                arc="Heal without owning the cure; teach others to do it."),
    "C13": dict(name="Frost Lich King Emperor", short="Lich King", identity="man", role="Lich emperor", secret=True,
                command="Dominion", base=dict(hp=100, mp=28, str=8, mag=15, df=8, res=12, spd=8), growth=(46, 7, 1, 3),
                summary="A frozen emperor of the old north who rules a court of the dead beneath the Skyspine.",
                arc="Release the dead he kept; give up a crown that outlived its people."),
    "C14": dict(name="Maldrath, the Fallen King", short="Maldrath", identity="man", role="Fallen king", secret=True,
                command="Kingsblade", base=dict(hp=130, mp=14, str=15, mag=7, df=11, res=7, spd=7), growth=(58, 3, 3, 1),
                summary="A king who fell with the old Crown and walks the Crown March's graveyards.",
                arc="Answer for the crown he wore, then help break the one that remains."),
    "C15": dict(name="Velkhar, Lord of the Dead", short="Velkhar", identity="man", role="Necromancer", secret=True,
                command="Necromancy", base=dict(hp=92, mp=26, str=7, mag=14, df=6, res=11, spd=9), growth=(44, 6, 1, 3),
                summary="A lord of the dead who raised the fallen to hold the fault's crypts shut.",
                arc="Let the dead rest; keep the living from needing him."),
    "C16": dict(name="Kael-09, Neon Blade Operative", short="Kael-09", identity="man", role="Builder operative", secret=True,
                command="Overdrive", base=dict(hp=98, mp=18, str=12, mag=9, df=8, res=8, spd=16), growth=(46, 4, 2, 1),
                summary="An operative from the builders' era, woken in a sealed vault with orders nobody can cancel.",
                arc="Choose a mission of his own in a world his makers left."),
    "C17": dict(name="Night Rider", short="Night Rider", identity="man", role="Builder rider", secret=True,
                command="Throttle", base=dict(hp=102, mp=14, str=13, mag=6, df=9, res=6, spd=15), growth=(48, 3, 2, 1),
                summary="A rider from the builders' era who still patrols roads that no longer exist.",
                arc="Find a road worth riding now."),
}

LEVELS = [1, 2, 6, 10, 15, 21, 28]
ULT_LEVEL = 40


def dmg(power, typ="physical", element=None, **kw):
    d = {"op": "damage", "power": power, "type": typ}
    if element:
        d["element"] = element
    d.update(kw)
    return d


def st(sid, chance=100, dur=None, **kw):
    d = {"op": "status", "id": sid, "chance": chance}
    if dur is not None:
        d["dur"] = dur
    d.update(kw)
    return d


NEG = ["poison", "burn", "bleed", "silence", "sleep", "stun", "slow", "mark", "guardbreak", "blind", "doom", "weaken"]

# (id, name, mp, power, kind, target, family, anim, element, ops, desc)
K = {
 "C09": [
  ("S101", "Scarlet Moon Slash", 4, 120, "physical", "enemy_one", "skill", "attack", "fire", [dmg(120, element="fire")], "A fire-edged slash."),
  ("S102", "Foxfire", 5, 100, "magical", "enemy_one", "spell", "cast", "fire", [dmg(100, "magical", "fire"), st("burn", 30)], "Fox fire; 30% Burn."),
  ("S103", "Mirror Veil", 6, 0, "utility", "self", "skill", "guard", "none", [{"op": "evasion", "pct": 40, "count": 2}], "Illusions: the next two attacks have -40% accuracy."),
  ("S104", "Crimson Blossom Dance", 10, 85, "physical", "enemy_all", "skill", "attack", "physical", [dmg(85, aoe=True)], "Strikes every enemy."),
  ("S105", "Nine Lanterns", 12, 120, "magical", "enemy_all", "spell", "cast", "fire", [dmg(120, "magical", "fire", aoe=True), st("burn", 25)], "Fire on all enemies; 25% Burn."),
  ("S106", "Fox Mirror Counter", 8, 0, "utility", "self", "skill", "guard", "none", [{"op": "mirror", "to": "self"}, {"op": "guard_self", "mult": 0.6, "label": "counter"}], "Guard stance that reflects the next spell's force."),
  ("S107", "Empress's Grace", 14, 0, "utility", "ally_all", "spell", "cast", "none", [st("haste", 100, 3)], "Haste on the party."),
  ("S108", "Nine-Tailed Judgment", 30, 250, "physical", "enemy_all", "skill", "ult", "fire", [dmg(250, element="fire", aoe=True)], "Ultimate: nine tails of fire over every enemy."),
 ],
 "C10": [
  ("S109", "Seraph Strike", 4, 120, "physical", "enemy_one", "skill", "attack", "light", [dmg(120, element="light")], "A holy strike."),
  ("S110", "Divine Guard", 5, 0, "utility", "ally_one", "spell", "guard", "none", [st("barrier", 100, 3)], "Barrier on one ally."),
  ("S111", "Heavenly Rebirth", 14, 35, "revive", "ally_one", "spell", "cast", "light", [{"op": "revive", "pct": 0.35}], "Revives an ally at 35% HP."),
  ("S112", "Judgment Cleave", 10, 150, "physical", "enemy_one", "skill", "attack", "light", [dmg(150, element="light"), st("guardbreak", 50, 3)], "Heavy holy cleave; 50% Guardbreak."),
  ("S113", "Wings of Judgment", 16, 110, "magical", "enemy_all", "spell", "cast", "light", [dmg(110, "magical", "light", aoe=True)], "Light on every enemy."),
  ("S114", "Aegis Wings", 18, 0, "utility", "ally_all", "spell", "guard", "none", [st("barrier", 100, 2)], "Barrier on the party."),
  ("S115", "Celestial Rush", 12, 170, "physical", "enemy_one", "skill", "attack", "physical", [dmg(170, ignore_def=0.3)], "Ignores 30% of defense."),
  ("S116", "Final Judgment", 32, 240, "magical", "enemy_all", "spell", "ult", "light", [dmg(240, "magical", "light", aoe=True, to="enemies"), {"op": "heal", "power": 80, "to": "allies"}], "Ultimate: judgment on every enemy, healing for the party."),
 ],
 "C11": [
  ("S117", "Abyssal Thrust", 4, 125, "physical", "enemy_one", "skill", "attack", "shadow", [dmg(125, element="shadow")], "A shadow-edged thrust."),
  ("S118", "Hellbrand", 0, 0, "utility", "self", "skill", "cast", "none", [{"op": "self_hp", "pct": 0.15}, {"op": "buff_ally"}, st("focus", 100, 3)], "Burns 15% of max HP: Empowered and Focus."),
  ("S119", "Valkyrie Dive", 8, 150, "physical", "enemy_one", "skill", "leap", "physical", [{"op": "leap", "time": 1.2}, dmg(150, melee=True)], "Leaps out of reach, then dives."),
  ("S120", "Soul Harvest", 8, 110, "physical", "enemy_one", "skill", "attack", "shadow", [dmg(110, element="shadow", drain=0.5)], "Heals her for half the damage."),
  ("S121", "Infernal Wings", 12, 100, "magical", "enemy_all", "spell", "cast", "fire", [dmg(100, "magical", "fire", aoe=True)], "Fire on every enemy."),
  ("S122", "Blood Pact", 10, 140, "heal", "ally_one", "skill", "cast", "none", [{"op": "self_hp", "pct": 0.2}, {"op": "heal", "power": 140}], "Gives 20% of her max HP to heal an ally."),
  ("S123", "Hellfire Ring", 18, 150, "magical", "enemy_all", "spell", "cast", "fire", [dmg(150, "magical", "fire", aoe=True), st("burn", 40)], "Fire on every enemy; 40% Burn."),
  ("S124", "Abyssal Descent", 30, 260, "physical", "enemy_one", "skill", "ult", "shadow", [dmg(260, element="shadow", drain=0.5)], "Ultimate: a draining dive into the abyss."),
 ],
 "C12": [
  ("S125", "Poison Flask", 3, 70, "magical", "enemy_one", "skill", "attack", "none", [dmg(70, "magical", ranged=True), st("poison", 80)], "Thrown flask; 80% Poison."),
  ("S126", "Tonic", 4, 110, "heal", "ally_one", "spell", "cast", "none", [{"op": "heal", "power": 110}], "Heals one ally."),
  ("S127", "Purge", 6, 0, "utility", "ally_one", "spell", "cast", "none", [{"op": "cleanse", "ids": NEG}], "Removes every harmful status."),
  ("S128", "Raven Swarm", 10, 90, "magical", "enemy_all", "spell", "cast", "shadow", [dmg(90, "magical", "shadow", aoe=True), st("blind", 30)], "Ravens on every enemy; 30% Blind."),
  ("S129", "Pestilence Wave", 14, 0, "utility", "enemy_all", "spell", "cast", "none", [st("poison", 90), st("weaken", 50, 3)], "Poison and Weaken on every enemy."),
  ("S130", "Remedy Mist", 16, 90, "heal", "ally_all", "spell", "cast", "none", [{"op": "heal", "power": 90}, st("regen", 100, 3)], "Heals the party and grants Regen."),
  ("S131", "Plague Ward", 12, 0, "utility", "ally_all", "spell", "guard", "none", [{"op": "status_ward", "to": "allies"}], "Wards the party against the next harmful status."),
  ("S132", "Black Death Ritual", 30, 180, "magical", "enemy_all", "spell", "ult", "shadow", [dmg(180, "magical", "shadow", aoe=True), st("poison", 100), st("weaken", 100, 3)], "Ultimate: plague on every enemy."),
 ],
 "C13": [
  ("S133", "Frost Bite", 4, 110, "magical", "enemy_one", "spell", "cast", "ice", [dmg(110, "magical", "ice"), st("slow", 25)], "Ice; 25% Slow."),
  ("S134", "Royal Cleave", 5, 120, "physical", "enemy_one", "skill", "attack", "ice", [dmg(120, element="ice")], "An ice-edged cleave."),
  ("S135", "Frost Nova", 12, 100, "magical", "enemy_all", "spell", "cast", "ice", [dmg(100, "magical", "ice", aoe=True), st("slow", 30)], "Ice on every enemy; 30% Slow."),
  ("S136", "Soul Reaper", 10, 120, "magical", "enemy_one", "spell", "attack", "shadow", [dmg(120, "magical", "shadow", drain=0.5)], "Heals him for half the damage."),
  ("S137", "Frozen Judgment", 16, 180, "magical", "enemy_one", "spell", "cast", "ice", [dmg(180, "magical", "ice"), st("stun", 30)], "Heavy ice; 30% Stun."),
  ("S138", "Crown of Rime", 14, 0, "utility", "ally_all", "spell", "guard", "none", [st("barrier", 100, 2), {"op": "resist", "elem": "fire", "mult": 0.5, "dur": 3}], "Barrier and fire resistance for the party."),
  ("S139", "Throne of the Damned", 20, 0, "utility", "enemy_all", "spell", "cast", "shadow", [st("doom", 25), st("slow", 60)], "25% Doom and 60% Slow on every enemy."),
  ("S140", "Army of the Dead", 32, 250, "magical", "enemy_all", "spell", "ult", "shadow", [dmg(250, "magical", "shadow", aoe=True)], "Ultimate: the frozen dead rise against every enemy."),
 ],
 "C14": [
  ("S141", "Greatsword Slash", 4, 130, "physical", "enemy_one", "skill", "attack", "physical", [dmg(130)], "A heavy slash."),
  ("S142", "Abyssal Roar", 6, 0, "utility", "enemy_all", "skill", "cast", "none", [st("weaken", 60, 3)], "60% Weaken on every enemy."),
  ("S143", "Heavy Cleave", 10, 160, "physical", "enemy_one", "skill", "attack", "physical", [dmg(160), st("guardbreak", 80, 3)], "80% Guardbreak."),
  ("S144", "Shadow Dash", 8, 140, "physical", "enemy_one", "skill", "attack", "shadow", [dmg(140, element="shadow", ignore_def=0.2)], "Ignores 20% of defense."),
  ("S145", "Fallen Crown", 12, 0, "utility", "self", "skill", "guard", "none", [{"op": "guard_self", "mult": 0.5, "label": "fallen crown"}, {"op": "buff_ally"}], "Guards and becomes Empowered."),
  ("S146", "Soul Nova", 18, 140, "magical", "enemy_all", "spell", "cast", "shadow", [dmg(140, "magical", "shadow", aoe=True)], "Shadow on every enemy."),
  ("S147", "Kingsbane", 16, 200, "physical", "enemy_one", "skill", "attack", "physical", [dmg(200, bonus_vs={"weaken": 1.3, "guardbreak": 1.3})], "x1.3 against weakened or broken foes."),
  ("S148", "Execution Strike", 30, 300, "physical", "enemy_one", "skill", "ult", "shadow", [dmg(300, element="shadow")], "Ultimate: the fallen king's execution."),
 ],
 "C15": [
  ("S149", "Bone Spear", 4, 110, "physical", "enemy_one", "skill", "attack", "physical", [dmg(110, ranged=True)], "A thrown spear of bone."),
  ("S150", "Shadow Bolt", 5, 120, "magical", "enemy_one", "spell", "cast", "shadow", [dmg(120, "magical", "shadow")], "Shadow on one enemy."),
  ("S151", "Soul Drain", 8, 100, "magical", "enemy_one", "spell", "cast", "shadow", [dmg(100, "magical", "shadow", drain=True), {"op": "mp_drain", "amount": 10}], "Drains HP and MP."),
  ("S152", "Raise Skeleton", 12, 0, "utility", "self", "spell", "cast", "none", [{"op": "decoy"}], "A skeleton draws the next two attacks."),
  ("S153", "Death Nova", 16, 130, "magical", "enemy_all", "spell", "cast", "shadow", [dmg(130, "magical", "shadow", aoe=True)], "Shadow on every enemy."),
  ("S154", "Grave Chill", 10, 0, "utility", "enemy_one", "spell", "cast", "none", [st("slow", 90), st("blind", 50)], "90% Slow and 50% Blind."),
  ("S155", "Unlife", 14, 0, "utility", "ally_one", "spell", "cast", "none", [st("regen", 100, 3), {"op": "protect"}], "Regen, and the next lethal hit leaves 1 HP."),
  ("S156", "Legion of Bone", 32, 240, "magical", "enemy_all", "spell", "ult", "shadow", [dmg(240, "magical", "shadow", aoe=True, to="enemies"), {"op": "decoy", "to": "self"}], "Ultimate: the dead rise; a skeleton guards the party."),
 ],
 "C16": [
  ("S157", "Energy Slash", 4, 120, "physical", "enemy_one", "skill", "attack", "storm", [dmg(120, element="storm")], "A charged slash."),
  ("S158", "EMP Burst", 8, 90, "magical", "enemy_all", "spell", "cast", "storm", [dmg(90, "magical", "storm", aoe=True), st("stun", 20)], "Storm on every enemy; 20% Stun."),
  ("S159", "Hologram Strike", 10, 140, "physical", "enemy_one", "skill", "attack", "physical", [dmg(140), {"op": "evasion", "pct": 30, "count": 1, "to": "self"}], "Leaves a decoy image: the next attack on him has -30% accuracy."),
  ("S160", "Dash Boost", 6, 0, "utility", "self", "skill", "step", "none", [{"op": "atb", "amount": 300}], "Fills his readiness gauge by 30%."),
  ("S161", "Plasma Combo", 14, 180, "physical", "enemy_one", "skill", "attack", "storm", [dmg(180, element="storm")], "A heavy storm combo."),
  ("S162", "Cyber Teleport", 8, 0, "utility", "self", "skill", "step", "none", [{"op": "row_back"}, {"op": "evasion", "pct": 50, "count": 1}], "Back row; the next attack has -50% accuracy."),
  ("S163", "System Scan", 3, 0, "utility", "enemy_one", "skill", "cast", "none", [{"op": "reveal", "what": "affinity"}, st("mark", 100, 4)], "Reveals weaknesses and Marks the target."),
  ("S164", "Overdrive Mode", 30, 0, "utility", "self", "skill", "ult", "none", [{"op": "once_per_battle"}, st("haste", 100, 4), st("focus", 100, 4), {"op": "buff_ally"}, {"op": "mp", "amount": 20}], "Ultimate: Haste, Focus and Empowered; restores 20 MP."),
 ],
 "C17": [
  ("S165", "Rev Strike", 4, 125, "physical", "enemy_one", "skill", "attack", "physical", [dmg(125)], "A revved strike."),
  ("S166", "Burnout", 8, 100, "physical", "enemy_all", "skill", "attack", "fire", [dmg(100, element="fire", aoe=True)], "Fire on every enemy."),
  ("S167", "Headlight", 5, 0, "utility", "enemy_all", "skill", "cast", "none", [st("blind", 50)], "50% Blind on every enemy."),
  ("S168", "Wheelie Smash", 10, 160, "physical", "enemy_one", "skill", "attack", "physical", [dmg(160), st("stun", 25)], "25% Stun."),
  ("S169", "Nitro", 8, 0, "utility", "ally_one", "skill", "cast", "none", [st("haste", 100, 3)], "Haste on one ally."),
  ("S170", "Road Flare", 12, 140, "magical", "enemy_one", "skill", "cast", "fire", [dmg(140, "magical", "fire"), st("mark", 100, 4)], "Fire and Mark."),
  ("S171", "Slipstream", 12, 0, "utility", "ally_all", "skill", "cast", "none", [{"op": "atb", "amount": 150}], "Fills the party's readiness by 15%."),
  ("S172", "Midnight Run", 30, 260, "physical", "enemy_all", "skill", "ult", "physical", [dmg(260, aoe=True)], "Ultimate: a full-throttle run through every enemy."),
 ],
}


def apply(content, check=None):
    ch = content["characters"]
    for cid, r in RENAME.items():
        ch[cid].update(r)
        if cid in COMMAND:
            ch[cid]["role_command"] = COMMAND[cid]
    for cid in ch:
        ch[cid].setdefault("secret", False)
        ch[cid].setdefault("art", cid)
    ab = content["abilities"]
    for cid, d in NEW.items():
        kit = K[cid]
        tmpl = ch[EQUIP_AS[cid]]
        learn = [{"id": kit[i][0], "level": LEVELS[i]} for i in range(7)] + [{"id": kit[7][0], "level": ULT_LEVEL}]
        ch[cid] = {"id": cid, "name": d["name"], "short": d["short"], "role": d["role"], "age": "", "identity": d["identity"],
                   "base": {"hp": d["base"]["hp"], "mp": d["base"]["mp"], "str": d["base"]["str"], "mag": d["base"]["mag"],
                            "def": d["base"]["df"], "res": d["base"]["res"], "spd": d["base"]["spd"]},
                   "growth": {"hp": d["growth"][0], "mp": d["growth"][1], "str": d["growth"][2], "mag": d["growth"][3]},
                   "learn": learn, "ultimate": None, "quest": "", "ultimate_weapon": "",
                   "starter": dict(tmpl["starter"]), "role_command": d["command"], "summary": d["summary"], "arc": d["arc"],
                   "secret": d["secret"], "art": cid, "equip_as": EQUIP_AS[cid]}
        for (aid, name, mp, power, kind, target, family, anim, elem, ops, desc) in kit:
            if check:
                check(aid, ops)
            ab[aid] = {"id": aid, "name": name, "owner": cid, "mp": mp, "power": power, "kind": kind, "target": target,
                       "desc": desc, "ops": ops, "family": family, "anim": anim, "element": elem,
                       "elemental_spell": family == "spell" and elem not in ("none", "physical"),
                       "revive": kind == "revive", "field": kind in ("heal", "revive"), "concord": True,
                       "unlock_level": [l["level"] for l in learn if l["id"] == aid][0]}
    # equipment: new heroes share their template's gear
    for it in content["items"].values():
        al = it.get("allowed")
        if not al:
            continue
        for cid, t in EQUIP_AS.items():
            if t in al and cid not in al:
                al.append(cid)
    return content
