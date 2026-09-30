"""Limit breaks (expansion battle systems, WORLD_V2 section 9 era): four per hero, 17 heroes, 68 in all.

Rules (runtime: BattleModel + Game):
- Each hero has a limit gauge (0-100) that fills from damage taken (75 points per max HP lost) and dealt (+2.5 per
  hit landed on an enemy). It persists between battles. When full, the command list offers "Limit".
- Using a limit empties the gauge. Limits are learned by use: tier 1 at the start; tier k+1 once the hero has used
  tier k USES[k] times and reached LEVELS[k].
- Tier 4 limits break the damage limit (op `uncapped`).
Ids S401-S468 (hero order C01..C17, four each). Ops use the existing op vocabulary only.
"""

LEVELS = [1, 15, 30, 50]      # level floor per tier
USES = [0, 3, 5, 8]           # uses of the previous tier needed per tier
FILL_TAKEN = 75.0             # gauge points per 100% max HP lost
FILL_DEALT = 2.5              # gauge points per damaging hit on an enemy


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


def heal(power, **kw):
    d = {"op": "heal", "power": power}
    d.update(kw)
    return d


LEAP = {"op": "leap", "time": 1.0}
NEG = ["poison", "burn", "bleed", "silence", "sleep", "stun", "slow", "mark", "guardbreak", "blind", "doom", "weaken"]

# cid -> 4 x (name, kind, target, element, anim, ops, desc); kind is the ability kind (physical|magical|heal|revive|utility)
L = {
 "C01": [  # Raven, the Executioner (oath knight; shares his body with Ilyr)
  ("Refused Sentence", "physical", "enemy_one", "physical", "attack", [dmg(230), st("guardbreak", 100, 3)],
   "The axe falls on the order, not the prisoner. Guardbreak."),
  ("Ilyr's Wing", "utility", "ally_all", "none", "guard", [st("barrier", 100, 3), heal(0, pct=0.15)],
   "The dragon opens a wing over everyone. Barrier; heals 15%."),
  ("Commuted", "physical", "enemy_one", "fire", "attack", [dmg(330, element="fire", ignore_def=0.4), {"op": "protect", "to": "lowest_ally"}],
   "A burning cut through armour; the weakest ally is protected."),
  ("By Agreement", "magical", "enemy_all", "fire", "ult", [dmg(470, "magical", "fire", aoe=True, uncapped=True), st("haste", 100, 3, to="allies")],
   "Raven and Ilyr, together by choice. Dragonfire on all; party Haste. Breaks the damage limit."),
 ],
 "C02": [  # Morwen, Witch of the Eclipse
  ("Penumbra", "magical", "enemy_all", "shadow", "cast", [dmg(220, "magical", "shadow", aoe=True)],
   "The edge of the eclipse crosses every enemy."),
  ("Corona", "magical", "enemy_all", "fire", "cast", [dmg(290, "magical", "fire", aoe=True), st("burn", 40)],
   "The ring of fire around the dark. 40% Burn."),
  ("Totality", "magical", "enemy_all", "shadow", "cast", [dmg(360, "magical", "shadow", aoe=True), {"op": "dispel_positive", "count": 1}, st("slow", 40)],
   "Full eclipse. Strips a boon; 40% Slow."),
  ("The Sun Returns", "magical", "enemy_all", "light", "ult", [dmg(480, "magical", "light", aoe=True, uncapped=True), {"op": "mp", "amount": 30, "to": "allies"}],
   "She lets the light back on her own terms. The party regains 30 MP. Breaks the damage limit."),
 ],
 "C03": [  # Vespera, Moonhare Warrior (dragoon; rescue without martyrs)
  ("Moonfall", "physical", "enemy_one", "physical", "leap", [LEAP, dmg(250, melee=True)],
   "Leaps past the clouds and lands like the moon."),
  ("No One Falls", "revive", "ally_all", "none", "cast", [{"op": "revive", "pct": 0.30}, heal(80)],
   "She goes back for everyone. Revives the fallen at 30%; heals the party."),
  ("Crescent Harrow", "physical", "enemy_all", "physical", "leap", [LEAP, dmg(190, aoe=True), dmg(130, aoe=True)],
   "Two diving passes over the whole field."),
  ("Testimony", "physical", "enemy_one", "physical", "ult", [LEAP, dmg(520, melee=True, uncapped=True), st("barrier", 100, 3, to="allies")],
   "The truth, from the highest point. Party Barrier. Breaks the damage limit."),
 ],
 "C04": [  # Rune Golem (machinist construct)
  ("Overclock", "utility", "ally_all", "none", "cast", [st("haste", 100, 3), {"op": "atb", "amount": 200}],
   "Pushes every rune past spec. Party Haste; readiness up."),
  ("Relay Surge", "magical", "enemy_all", "storm", "cast", [dmg(280, "magical", "storm", aoe=True)],
   "Routes a relay's full load through the enemy."),
  ("Distributed Grid", "utility", "ally_all", "none", "cast", [st("barrier", 100, 3), st("regen", 100, 3), {"op": "mp", "amount": 20}],
   "Power anyone can maintain. Barrier, Regen, 20 MP."),
  ("Engine Nobody Owns", "magical", "enemy_all", "none", "ult", [dmg(470, "magical", "none", aoe=True, uncapped=True)],
   "His own work, at full output. Breaks the damage limit."),
 ],
 "C05": [  # Elowen, Guardian of the Moonlit Grove (ranger)
  ("Moonlit Volley", "physical", "enemy_all", "physical", "shoot", [dmg(120, ranged=True, aoe=True), dmg(120, ranged=True, aoe=True)],
   "Two volleys under the grove's moon."),
  ("The Grove Remembers", "heal", "ally_all", "light", "cast", [heal(150), {"op": "cleanse", "ids": ["poison", "blind", "slow", "weaken"]}],
   "Old roots heal the party and draw out poison, blindness, slow and weakness."),
  ("Every Path at Once", "physical", "enemy_all", "physical", "shoot", [dmg(330, ranged=True, aoe=True), st("mark", 100, 4)],
   "An arrow down every route. Marks every enemy."),
  ("Guardian's Last Arrow", "physical", "enemy_one", "physical", "ult", [dmg(540, ranged=True, uncapped=True, bonus_vs={"mark": 1.2})],
   "The one she kept for the grove. Breaks the damage limit."),
 ],
 "C06": [  # Aurex, Dragonblood Champion (oracle / healer)
  ("Blood Memory", "heal", "ally_all", "light", "cast", [heal(170)],
   "His blood remembers every wound healed. Heals the party."),
  ("Foresight", "utility", "ally_all", "none", "cast", [st("barrier", 100, 3), {"op": "evasion", "pct": 30, "count": 1}, {"op": "reveal", "what": "intent", "to": "enemies"}],
   "He tells you what comes next, and lets you choose. Barrier, evasion; reveals intents."),
  ("Dragon's Dawn", "revive", "ally_all", "light", "cast", [{"op": "revive", "pct": 0.5}, heal(200)],
   "Revives the fallen at 50% and heals everyone."),
  ("Unwritten Future", "revive", "ally_all", "light", "ult", [{"op": "revive", "pct": 1.0}, {"op": "full_restore"}, dmg(400, "magical", "light", to="enemies", aoe=True, uncapped=True)],
   "No vision holds. Revives and fully restores the party; light on every enemy. Breaks the damage limit."),
 ],
 "C07": [  # Crimson Oni (spellblade; burning his own record)
  ("Red Ledger", "physical", "enemy_one", "fire", "attack", [dmg(240, element="fire"), st("burn", 60)],
   "Every name he bound, cut into the blade. 60% Burn."),
  ("Broken Rank", "physical", "enemy_all", "physical", "attack", [dmg(150, aoe=True), dmg(150, aoe=True)],
   "He steps out of line twice through the whole enemy line."),
  ("Unbinding", "physical", "enemy_all", "light", "attack", [{"op": "dispel_positive", "count": 99}, dmg(290, element="light", aoe=True)],
   "Cuts every seal and boon off the enemy."),
  ("Record Burned", "physical", "enemy_one", "fire", "ult", [dmg(520, element="fire", ignore_def=0.5, uncapped=True)],
   "One act to cancel the rest. Ignores half of defense. Breaks the damage limit."),
 ],
 "C08": [  # Sak, Guardian of the Cat Kingdom (rogue; fakes deaths)
  ("Cutpurse Flurry", "physical", "enemy_one", "physical", "attack", [dmg(95), dmg(95), dmg(95), {"op": "steal"}],
   "Three quick cuts and a lighter purse."),
  ("Nine Lives", "utility", "ally_all", "none", "cast", [{"op": "protect"}, {"op": "evasion", "pct": 40, "count": 1}],
   "Everyone gets one of his spare lives. Survives a fatal blow once."),
  ("Paperwork Death", "utility", "enemy_one", "none", "cast", [st("doom", 80, 3), st("weaken", 100, 3), st("guardbreak", 100, 3)],
   "The records now say it died. 80% Doom; Weaken; Guardbreak."),
  ("Royal Pardon", "physical", "enemy_one", "physical", "ult", [dmg(480, uncapped=True), {"op": "steal"}, st("haste", 100, 3, to="allies")],
   "The Cat Kingdom's highest mercy. Steals; party Haste. Breaks the damage limit."),
 ],
 "C09": [  # Crimson Kitsune Empress (illusions, fox fire)
  ("Foxfire Procession", "magical", "enemy_all", "fire", "cast", [dmg(230, "magical", "fire", aoe=True)],
   "A wedding of fox lights walks through the enemy."),
  ("Thousand Masks", "utility", "ally_all", "none", "cast", [{"op": "evasion", "pct": 50, "count": 2}, st("blind", 60, to="enemies")],
   "Which one is real? The party dodges; 60% Blind on enemies."),
  ("Court Unmasked", "magical", "enemy_all", "fire", "cast", [{"op": "dispel_positive", "count": 99}, dmg(340, "magical", "fire", aoe=True)],
   "She tears the masks off everyone, and the lies burn."),
  ("Empress Unveiled", "magical", "enemy_all", "fire", "ult", [dmg(480, "magical", "fire", aoe=True, uncapped=True), st("haste", 100, 3, to="allies")],
   "The court sees her as she is. Party Haste. Breaks the damage limit."),
 ],
 "C10": [  # Archangel Commander (seraph knight; the last order)
  ("Last Order", "physical", "enemy_one", "light", "attack", [dmg(250, element="light")],
   "The last command the host gave, carried out well."),
  ("Host Formation", "utility", "ally_all", "none", "guard", [st("barrier", 100, 3), {"op": "protect"}],
   "The party stands in the host's old ranks. Barrier; survives a fatal blow once."),
  ("Seraph's Descent", "physical", "enemy_all", "light", "leap", [LEAP, dmg(320, element="light", aoe=True)],
   "He falls on the field like judgment."),
  ("Judged by Sight", "magical", "enemy_all", "light", "ult", [dmg(480, "magical", "light", aoe=True, uncapped=True), heal(120, to="allies")],
   "He judges what he sees. Heals the party. Breaks the damage limit."),
 ],
 "C11": [  # Inferna, Abyssal Valkyrie (carries the living out)
  ("Soul Ferry", "physical", "enemy_one", "shadow", "attack", [dmg(240, element="shadow", drain=0.5)],
   "Takes a soul's worth and gives half back to her."),
  ("Ledger Torn", "utility", "enemy_all", "none", "cast", [st("weaken", 90, 3), st("slow", 70), st("focus", 100, 3, to="self")],
   "She rips up the abyss's accounts. Weaken, 70% Slow; she gains Focus."),
  ("Carried Out Alive", "revive", "ally_all", "none", "cast", [{"op": "revive", "pct": 0.4}, heal(120)],
   "She brings everyone back up. Revives at 40%; heals the party."),
  ("Abyss Unbargained", "magical", "enemy_all", "fire", "ult", [{"op": "self_hp", "pct": 0.2}, dmg(520, "magical", "fire", aoe=True, uncapped=True)],
   "Pays in her own blood, owes nothing after. Breaks the damage limit."),
 ],
 "C12": [  # Corvus, Harbinger of Pestilence (plague doctor / healer)
  ("Quarantine Lifted", "heal", "ally_all", "none", "cast", [{"op": "cleanse", "ids": NEG}, heal(140)],
   "Cures every ailment on the party and heals."),
  ("Murder of Crows", "magical", "enemy_all", "shadow", "cast", [dmg(150, "magical", "shadow", aoe=True), dmg(150, "magical", "shadow", aoe=True)],
   "His birds come home twice."),
  ("The Cure, Given Away", "heal", "ally_all", "none", "cast", [heal(200), st("regen", 100, 4), st("barrier", 100, 3)],
   "The recipe, free to all. Heals; Regen; Barrier."),
  ("Pestilence Unmade", "magical", "enemy_all", "shadow", "ult", [st("poison", 90), st("weaken", 90, 3), dmg(460, "magical", "shadow", aoe=True, uncapped=True)],
   "The sickness he was sent to spread, turned on its senders. Breaks the damage limit."),
 ],
 "C13": [  # Frost Lich King Emperor (court of the dead)
  ("Rime Edict", "magical", "enemy_all", "ice", "cast", [dmg(240, "magical", "ice", aoe=True), st("slow", 30)],
   "A decree of the old north. 30% Slow."),
  ("Court Dismissed", "utility", "ally_all", "none", "cast", [{"op": "cleanse", "ids": ["doom", "slow", "sleep"]}, st("barrier", 100, 3), {"op": "mp", "amount": 20}],
   "He lets his courtiers go, and they guard you on the way out."),
  ("Absolute Winter", "magical", "enemy_all", "ice", "cast", [dmg(360, "magical", "ice", aoe=True), st("slow", 60)],
   "The cold that froze an empire. 60% Slow."),
  ("Abdication", "magical", "enemy_all", "ice", "ult", [dmg(500, "magical", "ice", aoe=True, uncapped=True), heal(120, to="allies")],
   "He sets down the crown, and the winter with it. Breaks the damage limit."),
 ],
 "C14": [  # Maldrath, the Fallen King
  ("Graveyard March", "physical", "enemy_one", "shadow", "attack", [dmg(260, element="shadow")],
   "Every soldier he buried marches behind the stroke."),
  ("The Crown Answers", "physical", "enemy_all", "physical", "attack", [dmg(160, aoe=True), st("weaken", 80, 3), st("guardbreak", 80, 3)],
   "He answers for the crown, loudly. Weaken and Guardbreak."),
  ("Kingsfall", "physical", "enemy_one", "physical", "attack", [dmg(380, ignore_def=0.3)],
   "How he fell, taught the hard way."),
  ("Break the Last Crown", "physical", "enemy_all", "shadow", "ult", [dmg(520, element="shadow", aoe=True, uncapped=True)],
   "What he came back for. Breaks the damage limit."),
 ],
 "C15": [  # Velkhar, Lord of the Dead (necromancer)
  ("Ossuary Rain", "physical", "enemy_all", "physical", "cast", [dmg(130, aoe=True, ranged=True), dmg(130, aoe=True, ranged=True)],
   "The crypt's bones come down twice."),
  ("Borrowed Breath", "magical", "enemy_one", "shadow", "cast", [dmg(290, "magical", "shadow", drain=True)],
   "Takes the breath from one enemy and keeps it."),
  ("Let Them Rest", "revive", "ally_all", "none", "cast", [{"op": "revive", "pct": 0.35}, {"op": "cleanse", "ids": ["doom", "poison"]}, heal(100)],
   "Nobody here needs him to raise them. Revives at 35%; cures Doom and Poison."),
  ("Crypts Shut", "magical", "enemy_all", "shadow", "ult", [dmg(490, "magical", "shadow", aoe=True, uncapped=True), st("doom", 30, 4)],
   "Every gate closed, the enemy inside. 30% Doom. Breaks the damage limit."),
 ],
 "C16": [  # Kael-09, Neon Blade Operative
  ("Standing Orders", "physical", "enemy_one", "storm", "attack", [dmg(140, element="storm"), dmg(140, element="storm")],
   "Two cuts by the manual."),
  ("Tactical Link", "utility", "ally_all", "none", "cast", [st("haste", 100, 3), st("focus", 100, 3)],
   "Links the party to his targeting. Haste and Focus."),
  ("Orbital Correction", "magical", "enemy_all", "storm", "cast", [dmg(360, "magical", "storm", aoe=True)],
   "Something old in orbit still answers his code."),
  ("Mission of My Own", "physical", "enemy_one", "storm", "ult", [dmg(520, element="storm", uncapped=True), {"op": "atb", "amount": 300, "to": "allies"}],
   "Orders he wrote himself. Party readiness up. Breaks the damage limit."),
 ],
 "C17": [  # Night Rider
  ("High Beam", "physical", "enemy_one", "physical", "attack", [dmg(230), st("blind", 60)],
   "Full lights in the eyes. 60% Blind."),
  ("Convoy", "utility", "ally_all", "none", "cast", [st("haste", 100, 3), {"op": "atb", "amount": 250}],
   "Everyone rides in his slipstream. Haste; readiness up."),
  ("Dead Man's Curve", "physical", "enemy_all", "fire", "attack", [dmg(330, element="fire", aoe=True)],
   "The bend nobody took at speed, taken."),
  ("The Road That Was", "physical", "enemy_all", "physical", "ult", [dmg(520, aoe=True, uncapped=True)],
   "He rides the whole old highway through them. Breaks the damage limit."),
 ],
}

HEROES = sorted(L)


def ids_for(cid):
    base = 401 + HEROES.index(cid) * 4
    return ["S%03d" % (base + k) for k in range(4)]


def apply(content, check=None):
    ab = content["abilities"]
    table = {}
    for cid in HEROES:
        assert cid in content["characters"], cid
        assert len(L[cid]) == 4, cid
        ids = ids_for(cid)
        for tier, (aid, row) in enumerate(zip(ids, L[cid]), start=1):
            name, kind, target, elem, anim, ops, desc = row
            if check:
                check(aid, ops)
            assert aid not in ab, aid
            rec = {"id": aid, "name": name, "owner": cid, "mp": 0, "power": max([o.get("power", 0) for o in ops if o["op"] == "damage"] or [0]),
                   "kind": kind, "target": target, "desc": desc, "ops": ops, "family": "limit", "anim": anim,
                   "element": elem, "elemental_spell": False, "revive": kind == "revive", "field": False, "concord": True,
                   "limit_tier": tier}
            if any(o["op"] == "leap" for o in ops):
                rec["anim"] = "leap"
            ab[aid] = rec
        table[cid] = ids
    content["limits"] = {"heroes": table, "levels": LEVELS, "uses": USES, "fill_taken": FILL_TAKEN, "fill_dealt": FILL_DEALT}
    return content
