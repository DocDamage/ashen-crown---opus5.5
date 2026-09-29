"""Runtime operation lists for all 80 ability records (docs/08).

Each entry expands the catalog's prose effect into supported BattleModel ops.
family: skill (physical/utility, usable while Silenced) | spell (blocked by Silence) | summon.
"""

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

NEG_REMOVABLE = ["poison", "burn", "bleed", "silence", "sleep", "stun", "slow", "mark", "guardbreak", "blind", "doom", "weaken"]

ABILITY_OPS = {
    # --- Dain ---
    "S001": dict(family="skill", anim="guard", ops=[{"op": "oath", "oath": "shelter"}]),
    "S002": dict(family="skill", anim="attack", element="physical", ops=[dmg(120), st("guardbreak", 100, 3)]),
    "S003": dict(family="skill", anim="guard", ops=[{"op": "oath", "oath": "wrath"}]),
    "S004": dict(family="skill", anim="attack", element="fire", ops=[dmg(155, element="fire")]),
    "S005": dict(family="skill", anim="guard", ops=[{"op": "oath", "oath": "sacrifice"}]),
    "S006": dict(family="skill", anim="cast", ops=[{"op": "cleanse", "ids": ["weaken"]}, st("barrier", 100, 2)]),
    "S007": dict(family="skill", anim="guard", ops=[{"op": "witness"}]),
    "S008": dict(family="spell", anim="cast", element="light",
                 ops=[{"op": "cleanse", "ids": NEG_REMOVABLE}, st("barrier", 100, 3), {"op": "lethal_guard"}]),
    # --- Tessa ---
    "S009": dict(family="spell", anim="cast", element="fire", elemental_spell=True, ops=[dmg(110, "magical", "fire"), st("burn", 20)]),
    "S010": dict(family="spell", anim="cast", element="ice", elemental_spell=True, ops=[dmg(110, "magical", "ice"), st("slow", 25)]),
    "S011": dict(family="spell", anim="cast", element="storm", elemental_spell=True, ops=[dmg(90, "magical", "storm", aoe=True)]),
    "S012": dict(family="spell", anim="cast", element="earth", elemental_spell=True, ops=[dmg(130, "magical", "earth"), st("guardbreak", 40)]),
    "S013": dict(family="skill", anim="cast", concord=False, ops=[{"op": "arm_overcast"}]),
    "S014": dict(family="spell", anim="cast", element="shadow", elemental_spell=True, ops=[dmg(170, "magical", "shadow", aoe=True)]),
    "S015": dict(family="skill", anim="cast", concord=False, ops=[{"op": "heat_exchange"}]),
    "S016": dict(family="spell", anim="cast", element="light", elemental_spell=True,
                 ops=[dmg(225, "magical", "light", aoe=True), {"op": "dispel_positive", "count": 1}]),
    # --- Corren ---
    "S017": dict(family="skill", anim="leap", element="physical", ops=[{"op": "leap", "time": 1.2}, dmg(145, melee=True)]),
    "S018": dict(family="skill", anim="leap", element="physical", ops=[{"op": "leap", "time": 1.2}, dmg(160, bonus_vs={"mark": 1.3})]),
    "S019": dict(family="skill", anim="attack", ops=[dmg(130), {"op": "ground", "dur": 2}]),
    "S020": dict(family="skill", anim="attack", ops=[dmg(160, ignore_def=0.35)]),
    "S021": dict(family="skill", anim="guard", ops=[{"op": "feather"}]),
    "S022": dict(family="skill", anim="leap", ops=[{"op": "leap", "time": 1.2}, dmg(145, aoe=True)]),
    "S023": dict(family="skill", anim="cast", ops=[{"op": "wingbeat"}, {"op": "atb", "amount": 120, "to": "allies_except_self"}]),
    "S024": dict(family="skill", anim="leap", ops=[{"op": "leap", "time": 1.2}, dmg(240), st("barrier", 100, 2, to="lowest_ally")]),
    # --- Ivo ---
    "S025": dict(family="skill", anim="shoot", ops=[dmg(110, ranged=True)]),
    "S026": dict(family="spell", anim="item", field=True, ops=[{"op": "heal", "power": 105}]),
    "S027": dict(family="spell", anim="cast", ops=[{"op": "resist", "elem": "storm", "mult": 0.5, "dur": 3}]),
    "S028": dict(family="skill", anim="cast", ops=[st("barrier", 100, 2), {"op": "evasion", "pct": 20, "count": 1}]),
    "S029": dict(family="skill", anim="shoot", ops=[{"op": "mine", "power": 170}]),
    "S030": dict(family="skill", anim="cast", ops=[{"op": "cleanse", "ids": ["burn"]}, st("regen", 100, 3)]),
    "S031": dict(family="skill", anim="cast", ops=[{"op": "decoy"}]),
    "S032": dict(family="skill", anim="cast", ops=[{"op": "once_per_battle"}, st("haste", 100, 3), {"op": "mp", "amount": 15}]),
    # --- Nera ---
    "S033": dict(family="skill", anim="shoot", ops=[st("mark", 100, 4), {"op": "reveal", "what": "affinity"}]),
    "S034": dict(family="skill", anim="shoot", ops=[dmg(80, ranged=True, aoe=True)]),
    "S035": dict(family="skill", anim="shoot", ops=[st("slow", 90), {"op": "atb", "amount": -150}]),
    "S036": dict(family="spell", anim="cast", ops=[st("barrier", 100, 3), {"op": "bramble"}]),
    "S037": dict(family="skill", anim="cast", ops=[{"op": "reveal", "what": "drops"}, {"op": "omen"}]),
    "S038": dict(family="skill", anim="shoot", ops=[dmg(175, ranged=True, bonus_vs={"guardbreak": 1.25, "mark": 1.25})]),
    "S039": dict(family="spell", anim="cast", ops=[{"op": "cleanse", "ids": ["blind"]}, st("focus", 100, 3)]),
    "S040": dict(family="skill", anim="shoot", ops=[dmg(180, ranged=True, aoe=True), st("mark", 100, 4), {"op": "flee", "amount": 500, "to": "self"}]),
    # --- Oriel ---
    "S041": dict(family="spell", anim="cast", element="light", field=True, ops=[{"op": "heal", "power": 125}]),
    "S042": dict(family="spell", anim="cast", field=True, ops=[{"op": "cleanse", "ids": ["poison", "burn", "bleed", "blind", "silence", "sleep"]}]),
    "S043": dict(family="spell", anim="cast", element="light", field=True, ops=[{"op": "heal", "power": 95}]),
    "S044": dict(family="spell", anim="cast", revive=True, field=True, ops=[{"op": "revive", "pct": 0.25}]),
    "S045": dict(family="spell", anim="cast", ops=[{"op": "omen"}]),
    "S046": dict(family="spell", anim="cast", ops=[{"op": "protect"}]),
    "S047": dict(family="spell", anim="cast", ops=[{"op": "cleanse", "ids": ["slow", "doom"]}, st("regen", 100, 3)]),
    "S048": dict(family="spell", anim="cast", revive=True, ops=[{"op": "once_per_battle"}, {"op": "revive", "pct": 0.20}, {"op": "heal", "power": 180}]),
    # --- Sable ---
    "S049": dict(family="skill", anim="cast", ops=[{"op": "infuse", "elem": "fire", "dur": 4}]),
    "S050": dict(family="skill", anim="cast", ops=[{"op": "infuse", "elem": "ice", "dur": 4}]),
    "S051": dict(family="skill", anim="cast", ops=[{"op": "infuse", "elem": "storm", "dur": 4}]),
    "S052": dict(family="spell", anim="cast", ops=[{"op": "dispel_positive", "count": 1, "else_damage": 60}]),
    "S053": dict(family="skill", anim="attack", ops=[dmg(140, infused=True), {"op": "mirror", "to": "self"}]),
    "S054": dict(family="skill", anim="attack", element="light", ops=[dmg(165, element="light"), st("silence", 50)]),
    "S055": dict(family="spell", anim="cast", ops=[st("barrier", 100, 3), {"op": "resist", "elem": "light", "mult": 0.75, "dur": 3}, {"op": "resist", "elem": "shadow", "mult": 0.75, "dur": 3}]),
    "S056": dict(family="skill", anim="attack", element="light", ops=[{"op": "dispel_positive", "count": 99}, dmg(230, infused=True), {"op": "status_ward", "to": "allies"}]),
    # --- Pip ---
    "S057": dict(family="skill", anim="attack", concord=True, ops=[{"op": "steal"}]),
    "S058": dict(family="skill", anim="attack", ops=[dmg(95, melee=True), st("blind", 50)]),
    "S059": dict(family="skill", anim="cast", ops=[{"op": "flee", "amount": 500, "else_evasion": 15}]),
    "S060": dict(family="skill", anim="cast", concord=False, ops=[{"op": "quick_hands"}]),
    "S061": dict(family="skill", anim="attack", ops=[dmg(100), {"op": "atb", "amount": -150}]),
    "S062": dict(family="skill", anim="attack", ops=[dmg(130), st("weaken", 100, 3)]),
    "S063": dict(family="skill", anim="cast", ops=[{"op": "remove_hard"}, {"op": "row_back"}, st("barrier", 100, 2)]),
    "S064": dict(family="skill", anim="cast", ops=[st("weaken", 100, 3), st("guardbreak", 100, 3), {"op": "cancel_charge"}]),
    # --- accessory spells ---
    "S065": dict(family="spell", anim="cast", element="fire", ops=[dmg(100, "magical", "fire")]),
    "S066": dict(family="spell", anim="cast", element="ice", ops=[dmg(100, "magical", "ice")]),
    "S067": dict(family="spell", anim="cast", element="storm", ops=[dmg(100, "magical", "storm")]),
    "S068": dict(family="spell", anim="cast", element="water", ops=[dmg(100, "magical", "water")]),
    "S069": dict(family="spell", anim="cast", element="light", field=True, ops=[{"op": "heal", "power": 90}]),
    "S070": dict(family="spell", anim="cast", ops=[st("slow", 75, 2)]),
    "S071": dict(family="spell", anim="cast", element="shadow", ops=[dmg(100, "magical", "shadow")]),
    "S072": dict(family="spell", anim="cast", element="light", ops=[dmg(100, "magical", "light")]),
    # --- summons (Vestiges) ---
    "S073": dict(family="summon", element="fire", ops=[dmg(180, "magical", "fire", to="enemies", aoe=True), {"op": "resist", "elem": "fire", "mult": 0.5, "dur": 2, "to": "allies"}]),
    "S074": dict(family="summon", element="earth", ops=[dmg(170, "magical", "earth", to="enemies", aoe=True), {"op": "heal", "pct": 0.08, "to": "allies"}]),
    "S075": dict(family="summon", element="water", ops=[dmg(170, "magical", "water", to="enemies", aoe=True), {"op": "cleanse", "ids": ["silence", "sleep"], "to": "allies"}]),
    "S076": dict(family="summon", element="storm", ops=[dmg(180, "magical", "storm", to="enemies", aoe=True), {"op": "atb", "amount": 100, "to": "allies"}]),
    "S077": dict(family="summon", element="light", ops=[{"op": "heal", "power": 140, "to": "allies"}, {"op": "reveal", "what": "intent", "to": "enemies"}]),
    "S078": dict(family="summon", element="none", ops=[st("barrier", 100, 3, to="allies"), st("regen", 100, 3, to="allies")]),
    "S079": dict(family="summon", element="ice", ops=[dmg(210, "magical", "ice", to="enemies", aoe=True), {"op": "cleanse", "ids": ["doom"], "to": "allies"}]),
    "S080": dict(family="summon", element="shadow", ops=[dmg(220, "magical", "shadow", to="enemies", aoe=True), {"op": "dispel_positive", "count": 1, "to": "enemies"}]),
}

# Burn immunity from Ember Moth is modelled as a 2-action fire ward (S073) - recorded deviation.
SUMMON_TARGET = "enemy_all"
