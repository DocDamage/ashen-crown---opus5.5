"""Runtime behaviour for the 40 ordinary enemies and 16 bosses (docs/10).

Stats are derived from catalog level/HP with archetype multipliers (initial tuning, unverified).
Each enemy gets explicit moves (ops, targeting rule, optional charge 'tell') and a deterministic cycle.
Target choice is the only random element at commit time; Omen can therefore show the next move name.
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

def mv(name, ops, target="random", charge=0.0, tell="", anim="attack", element="physical", **kw):
    d = {"name": name, "ops": ops, "target": target, "anim": anim, "element": element}
    if charge:
        d["charge"] = charge
        d["tell"] = tell or name
    d.update(kw)
    return d

ATTACK = mv("Attack", [dmg(100)])

# id: (shape, archetype mods, affinities extra, tags, moves, cycle, extras)
E = {}

def enemy(eid, shape, moves, cycle, mods=None, aff=None, tags=None, **extra):
    E[eid] = dict(shape=shape, moves=moves, cycle=cycle, mods=mods or {}, aff=aff or {}, tags=tags or [], **extra)

# ---------- D01 Crown Quarry ----------
enemy("E001", "rat", {"bite": mv("Crouch-Bite", [dmg(105)], target="front_lowest", anim="attack")}, ["bite"], mods={"spd": 1.3, "def": 0.8})
enemy("E002", "beetle", {"hit": mv("Clamp", [dmg(100)]), "shell": mv("Shell Up", [{"op": "guard_self", "mult": 0.25, "label": "shell"}], target="self", anim="guard")},
      ["hit", "shell"], mods={"def": 1.4, "spd": 0.8})
enemy("E003", "wisp", {"bolt": mv("Fire Bolt", [dmg(120, "magical", "fire")], charge=2.0, tell="Gathering a small flame", anim="cast", element="fire", interruptible=True),
                       "touch": mv("Flicker", [dmg(80, "magical", "fire")], anim="cast", element="fire")},
      ["touch", "bolt"], mods={"hp": 1.0, "def": 0.7, "res": 1.3}, aff={"fire": "absorb"}, tags=["flying"])
enemy("E004", "hound", {"mark": mv("Sniff Out", [{"op": "msg", "text": "The hound fixes on its prey."}], target="random", anim="step"),
                        "lunge": mv("Lunge", [dmg(135)], target="marked")}, ["mark", "lunge"], mods={"spd": 1.2})
# ---------- D02 Veyr Underways ----------
enemy("E005", "slime", {"slap": mv("Slap", [dmg(95)])}, ["slap"], split=True, mods={"def": 0.6, "res": 1.2})
enemy("E006", "drone", {"silence": mv("Seal Pulse", [st("silence", 80, 2)], anim="cast", element="none"), "strike": mv("Stamp", [dmg(85)])},
      ["silence", "strike", "strike"], tags=["flying"], aff={"earth": "resist"})
enemy("E007", "moth", {"filch": mv("Filch", [{"op": "steal_gold"}, dmg(60)]), "dust": mv("Dust Wing", [dmg(90, "magical", "none")], anim="cast")},
      ["filch", "dust"], tags=["flying"])
enemy("E008", "shell", {"guard": mv("Brace Ally", [{"op": "guard_self", "mult": 0.5, "label": "braced"}], target="ally_random", anim="guard"),
                        "core": mv("Core Slam", [dmg(115)])}, ["guard", "core"], mods={"def": 1.5})
# ---------- D03 Rootward ----------
enemy("E009", "wolf", {"bite": mv("Pack Bite", [dmg(110)])}, ["bite"], mods={"spd": 1.25})
enemy("E010", "mite", {"sap": mv("Sap Tell", [{"op": "msg", "text": "The mite swells with sap."}], target="self", anim="step"),
                       "poison": mv("Sap Sting", [dmg(70), st("poison", 90, 3)])}, ["sap", "poison", "poison"])
enemy("E011", "flower", {"pollen": mv("Sleep Pollen", [st("sleep", 75, 1)], anim="cast", element="none"), "lash": mv("Petal Lash", [dmg(95)])},
      ["lash", "pollen", "lash"])
enemy("E012", "lantern", {"water": mv("Bog Spray", [dmg(115, "magical", "water")], anim="cast", element="water"),
                          "lure": mv("Lure Glow", [{"op": "msg", "text": "The lantern's glow drifts toward its next target."}], target="random", anim="step")},
      ["water", "lure"], tags=["flying"])
# ---------- D04 Furnace Spine ----------
enemy("E013", "imp", {"rivet": mv("Rivet Throw", [dmg(115, ranged=True)]), "reload": mv("Reload", [{"op": "msg", "text": "The imp reloads."}], target="self", anim="step")},
      ["rivet", "reload"])
enemy("E014", "crab", {"build": mv("Pressure Builds", [{"op": "msg", "text": "Pressure hisses inside the crab."}], target="self", anim="step"),
                       "burst": mv("Pressure Burst", [dmg(95, "magical", "fire", aoe=True)], target="all", anim="cast", element="fire", weaker_if_hit=True)},
      ["build", "build", "burst"], mods={"hp": 1.0, "def": 1.3})
enemy("E015", "sprite", {"blind": mv("Soot Cloud", [st("blind", 80, 2)], anim="cast", element="none"),
                         "shade": mv("Soot Bolt", [dmg(85, "magical", "shadow")], anim="cast", element="shadow")}, ["blind", "shade", "shade"], tags=["flying"])
enemy("E016", "hand", {"raise": mv("Fist Raised", [dmg(190)], charge=2.2, tell="The fist rises — Defend halves the blow"),
                       "jab": mv("Knuckle Jab", [dmg(90)])}, ["jab", "raise"], mods={"atk": 1.1})
# ---------- D05 Drowned Archive ----------
enemy("E017", "page", {"copy": mv("Copied Verse", [dmg(95, "magical", "water", copy=True)], anim="cast", element="water"), "cut": mv("Paper Cut", [dmg(90)])},
      ["cut", "copy"], copy_element=True)
enemy("E018", "leech", {"drain": mv("Drain", [dmg(100, drain=True)])}, ["drain"], mods={"hp": 1.0})
enemy("E019", "diver", {"melee": mv("Hook", [dmg(105)]), "spell": mv("Undertow", [dmg(110, "magical", "water")], anim="cast", element="water")},
      ["melee", "spell"], tags=["undead"], aff={"light": "weak", "shadow": "absorb"})
enemy("E020", "eye", {"stare": mv("Appraise", [{"op": "msg", "text": "The eye studies the strongest mind."}], target="highest_mp", anim="step"),
                      "drain": mv("Mind Siphon", [{"op": "mp_drain", "amount": 15}, dmg(80, "magical", "none")], target="marked", anim="cast")},
      ["stare", "drain"], tags=["flying"])
# ---------- D06 Skychain ----------
enemy("E021", "kite", {"double": mv("Twin Cut", [dmg(60), dmg(60)])}, ["double"], tags=["flying"], mods={"spd": 1.3})
enemy("E022", "viper", {"bite": mv("Gust Bite", [dmg(105)]), "coil": mv("Coil", [dmg(120)])}, ["bite", "coil"], melee_dodge=15)
enemy("E023", "golem", {"windup": mv("Ballast Slam", [dmg(210)], charge=2.6, tell="The golem winds up a slow slam"), "push": mv("Shove", [dmg(90)])},
      ["push", "windup"], mods={"def": 1.8, "res": 0.6, "spd": 0.6})
enemy("E024", "tick", {"slow": mv("Numbing Bite", [dmg(60), st("slow", 80, 3)]), "rest": mv("Rest", [{"op": "msg", "text": "The tick rests."}], target="self", anim="step")},
      ["slow", "rest"])
# ---------- D07 Whitebone ----------
enemy("E025", "sentinel", {"pguard": mv("Physical Sigil", [{"op": "guard_self", "mult": 0.5, "label": "phys sigil"}], target="self", anim="guard"),
                           "mguard": mv("Magic Sigil", [{"op": "msg", "text": "Its sigil turns to face magic."}], target="self", anim="guard"),
                           "strike": mv("Halberd", [dmg(110)])}, ["pguard", "strike", "mguard", "strike"], mods={"def": 1.3, "res": 1.3})
enemy("E026", "leech", {"strip": mv("Seal Siphon", [{"op": "dispel_positive", "count": 1}, dmg(80)])}, ["strip"], sprite_variant="seal")
enemy("E027", "wolf", {"bite": mv("Frost Bite", [dmg(105, element="ice")])}, ["bite"], mods={"hp": 0.8, "spd": 1.4}, sprite_variant="frost", aff={"ice": "absorb"})
enemy("E028", "hound", {"stun": mv("Binding Snap", [dmg(70), st("stun", 60, 1)]), "bite": mv("Bite", [dmg(105)])}, ["bite", "stun", "bite"], sprite_variant="binding")
# ---------- D08 Memory Vault ----------
enemy("E029", "shard", {"echo": mv("Echo Strike", [dmg(100), dmg(60)])}, ["echo"], tags=["flying"])
enemy("E030", "singer", {"heal": mv("Mending Note", [{"op": "heal", "power": 50}], target="ally_lowest", anim="cast"),
                         "light": mv("Pale Note", [dmg(85, "magical", "light")], anim="cast", element="light")}, ["light", "heal", "light"],
      aff={"physical": "weak"}, weak_is_physical=True)
enemy("E031", "widow", {"bleed": mv("Glass Fang", [dmg(90), st("bleed", 85, 3)], charge=1.6, tell="Glass fangs glint"), "bite": mv("Bite", [dmg(100)])},
      ["bite", "bleed"])
enemy("E032", "knight", {"cleave": mv("Hollow Cleave", [dmg(150)], target="row_front")}, ["cleave"], tags=["undead"],
      aff={"light": "weak", "shadow": "absorb"}, acc_penalty=15)
# ---------- D09 Sable Conduit ----------
enemy("E033", "relay", {"boost": mv("Empower Relay", [{"op": "buff_ally"}], target="ally_random", anim="cast"), "arc": mv("Arc", [dmg(100, "magical", "storm")], anim="cast", element="storm")},
      ["boost", "arc", "arc"])
enemy("E034", "lancer", {"charge": mv("Row Lance", [dmg(170)], target="row_front", charge=2.4, tell="Lance lowered at the front row"), "jab": mv("Jab", [dmg(95)])},
      ["jab", "charge"])
enemy("E035", "wisp", {"fire": mv("Threshold Flame", [dmg(125, "magical", "fire")], anim="cast", element="fire"),
                       "recover": mv("Exposed", [{"op": "msg", "text": "The wisp's core is exposed."}], target="self", anim="step")},
      ["fire", "recover"], sprite_variant="threshold", tags=["flying"], aff={"fire": "absorb"})
enemy("E036", "shell", {"weaken": mv("Edict Seal", [st("weaken", 80, 3)], anim="cast", element="none"), "strike": mv("Edict Hammer", [dmg(135)])},
      ["weaken", "strike"], mods={"def": 1.5, "spd": 0.7}, sprite_variant="edict")
# ---------- D10 Crown Heart ----------
enemy("E037", "seraph", {"warn": mv("Radiant Fall", [dmg(115, "magical", "light", aoe=True)], target="all", charge=2.2, tell="Wings flare — light gathers overhead", element="light"),
                         "slash": mv("Slash", [dmg(105)])}, ["slash", "warn"], mods={"def": 0.6}, tags=["flying"])
enemy("E038", "automaton", {"press": mv("Press", [dmg(115)]), "guard": mv("Rotate Plating", [{"op": "guard_self", "mult": 0.5, "label": "plating"}], target="self", anim="guard"),
                            "vent": mv("Vent", [dmg(90, "magical", "fire", aoe=True)], target="all", element="fire")}, ["press", "guard", "vent"])
enemy("E039", "choirling", {"doom": mv("Doom Chant", [st("doom", 70, 3)], charge=2.0, tell="A two-action doom warning begins", anim="cast", element="none"),
                            "note": mv("Hollow Note", [dmg(95, "magical", "shadow")], anim="cast", element="shadow")}, ["note", "doom", "note"],
      aff={"physical": "weak"}, weak_is_physical=True)
enemy("E040", "remnant", {"shield": mv("Tether Shield", [{"op": "guard_self", "mult": 0.5, "label": "tether"}], target="self", anim="guard"),
                          "order": mv("Named Order", [dmg(110), st("silence", 50, 2)]),
                          "ring": mv("Pressure Ring", [dmg(100, "magical", "none", aoe=True)], target="all", charge=2.0, tell="Pressure rings brighten")},
      ["shield", "order", "ring"])

# ---------- Bosses ----------
B = {}

def boss(bid, shape, phases, moves, aff=None, tags=None, parts=None, **extra):
    B[bid] = dict(shape=shape, phases=phases, moves=moves, aff=aff or {}, tags=["boss"] + (tags or []), parts=parts or [], **extra)

boss("B01", "extractor", [
    {"at": 100, "cycle": ["jab", "jab", "clamp"], "enter": ""},
    {"at": 65, "cycle": ["jab", "clamp", "jab", "clamp"], "enter": "The Warden's pressure gauge redlines."},
    {"at": 30, "cycle": ["vent", "jab", "clamp"], "enter": "Steam bursts from every seam — the Warden vents."}],
    {"jab": mv("Piston Jab", [dmg(115)]),
     "clamp": mv("Pressure Clamp", [dmg(230)], charge=3.0, tell="The digging arm hovers; the red gauge fills", weakened_by_part="valve"),
     "vent": mv("Vent and Sweep", [dmg(95, aoe=True)], target="all", charge=2.4, tell="Vents hiss open for a sweep")},
    aff={"storm": "weak", "fire": "resist"}, parts=[{"id": "E_VALVE", "name": "Pressure Valve", "hp_frac": 0.18}])
boss("B02", "bailiff", [
    {"at": 100, "cycle": ["baton", "warrant", "restrain"]},
    {"at": 50, "cycle": ["baton", "warrants", "restrain", "baton"], "enter": "The Bailiff stamps duplicate warrants — only one seal is live."}],
    {"baton": mv("Baton", [dmg(115)]),
     "warrant": mv("Stamp Warrant", [{"op": "msg", "text": "A warrant names its next target."}], target="random", anim="cast"),
     "warrants": mv("Duplicate Warrants", [{"op": "msg", "text": "Three warrants flutter; one seal glows."}], target="random", anim="cast"),
     "restrain": mv("Restraint", [dmg(90), st("stun", 100, 1)], target="marked", charge=1.8, tell="The warrant's seal glows — restraint incoming")})
boss("B03", "stag", [
    {"at": 100, "cycle": ["hoof", "vines", "hoof"]},
    {"at": 60, "cycle": ["bloom", "cage", "hoof"], "enter": "Roots split the floor around the back row."},
    {"at": 25, "cycle": ["pollen", "hoof", "cage"], "enter": "The antlers shed a cloud of pollen."}],
    {"hoof": mv("Hoof", [dmg(120)]), "vines": mv("Vines", [dmg(85, "magical", "earth"), st("poison", 40, 3)], anim="cast", element="earth"),
     "bloom": mv("Antler Bloom", [{"op": "msg", "text": "The antlers bloom."}], target="self", anim="cast"),
     "cage": mv("Root Cage", [dmg(110, "magical", "earth"), st("slow", 70, 2)], target="row_back", charge=2.4, tell="Antlers bloom — roots coil toward the back row", element="earth", weakened_by_part="root"),
     "pollen": mv("Pollen Burst", [dmg(80, "magical", "none", aoe=True), st("sleep", 30, 1)], target="all", charge=2.0, tell="A pollen cloud swells")},
    aff={"fire": "weak", "earth": "resist"}, parts=[{"id": "E_ROOT", "name": "Binding Root", "hp_frac": 0.12, "aff": {"fire": "weak"}}])
boss("B04", "colossus", [
    {"at": 100, "cycle": ["rivet", "rivet", "stomp"]},
    {"at": 70, "cycle": ["screen", "rivet", "stomp"], "enter": "Steam screens the Colossus's joints."},
    {"at": 35, "cycle": ["vents", "sweep", "rivet"], "enter": "Three vents glow along its back."}],
    {"rivet": mv("Rivet Strike", [dmg(120, ranged=True)]), "stomp": mv("Stomp", [dmg(105, aoe=True)], target="all"),
     "screen": mv("Steam Screen", [{"op": "guard_self", "mult": 0.6, "label": "steam"}], target="self", anim="guard"),
     "vents": mv("Vents Light", [{"op": "msg", "text": "Vents light left to right..."}], target="self", anim="cast"),
     "sweep": mv("Boiler Sweep", [dmg(150, "magical", "fire", aoe=True)], target="all", charge=2.6, tell="All three vents blaze — boiler sweep", element="fire", weaker_if_hit=True)},
    aff={"ice": "weak", "fire": "absorb"})
boss("B05", "custodian", [
    {"at": 100, "cycle": ["lash", "lash", "bell"]},
    {"at": 60, "cycle": ["bell", "lash", "mirror"], "enter": "One of three bells begins to vibrate."},
    {"at": 25, "cycle": ["wave", "lash", "mirror"], "enter": "The Custodian draws breath for a choral wave."}],
    {"lash": mv("Salt Lash", [dmg(120)]), "bell": mv("Bell Toll", [dmg(100, "magical", "water")], anim="cast", element="water"),
     "mirror": mv("Mirror Bell", [dmg(130, "magical", "water", copy=True)], charge=1.8, tell="A bell vibrates — it will mirror the last element", anim="cast"),
     "wave": mv("Choral Wave", [dmg(115, "magical", "water", aoe=True)], target="all", charge=2.4, tell="The choir swells", element="water")},
    aff={"storm": "weak", "water": "absorb"}, copy_element=True)
boss("B06", "roc", [
    {"at": 100, "cycle": ["talon", "talon", "gust"]},
    {"at": 55, "cycle": ["dive", "talon", "gust"], "enter": "The tether strains; a shadow sweeps a row."},
    {"at": 25, "cycle": ["freegust", "dive", "talon"], "enter": "The Roc pulls against its chain with free wings."}],
    {"talon": mv("Talon", [dmg(125)]), "gust": mv("Gust", [dmg(85, "magical", "storm", aoe=True)], target="all", element="storm"),
     "dive": mv("Tethered Dive", [dmg(190)], target="row_front", charge=2.4, tell="A shadow marks the front row"),
     "freegust": mv("Free-Wing Gust", [dmg(110, "magical", "storm", aoe=True), {"op": "atb", "amount": -100}], target="all", charge=2.0, tell="Wings spread wide", element="storm")},
    aff={"ice": "weak", "earth": "immune"}, tags=["flying"])
boss("B07", "adjudicator", [
    {"at": 100, "cycle": ["seal", "strike", "strike"]},
    {"at": 65, "cycle": ["judge", "strike", "seal"], "enter": "A judgment mark hangs over the party."},
    {"at": 30, "cycle": ["seal", "seal2", "strike"], "enter": "Two sigils rotate, a full action of warning apart."}],
    {"seal": mv("Skill Seal", [st("silence", 90, 2)], charge=1.6, tell="A sigil turns toward skills", anim="cast", element="none"),
     "seal2": mv("Item Seal", [st("weaken", 90, 2)], charge=1.6, tell="A sigil turns toward strength", anim="cast", element="none"),
     "strike": mv("Ivory Strike", [dmg(130)]), "judge": mv("Judgment", [dmg(140, "magical", "light")], target="lowest_hp", anim="cast", element="light")},
    aff={"shadow": "weak", "light": "resist"})
boss("B08", "choir", [
    {"at": 100, "cycle": ["needle", "needle", "echo"]},
    {"at": 60, "cycle": ["echo", "needle", "refrain"], "enter": "Three masks light, naming the command they will echo."},
    {"at": 25, "cycle": ["refrain", "echo", "needle"], "enter": "The Choir tries to sing with one voice."}],
    {"needle": mv("Memory Needle", [dmg(125, "magical", "none")], anim="cast"),
     "echo": mv("Echo Command", [dmg(150)], charge=1.8, tell="Masks light — the echo targets the repeated command"),
     "refrain": mv("Shared Refrain", [dmg(120, "magical", "light", aoe=True), st("silence", 30, 2)], target="all", charge=2.4, tell="The masks harmonize", element="light")},
    aff={"physical": "weak", "shadow": "resist"})
boss("B09", "voss", [
    {"at": 100, "cycle": ["sword", "order", "sword"]},
    {"at": 55, "cycle": ["guard", "sword", "order"], "enter": "Voss raises the baton and points at a protector."},
    {"at": 25, "cycle": ["barrage", "sword", "order"], "enter": "'Hold the line,' Voss says, to no one who can refuse."}],
    {"sword": mv("Marshal's Blade", [dmg(140)]), "order": mv("Command: Kneel", [st("weaken", 70, 2), dmg(90)], target="protector"),
     "guard": mv("Forced Guard", [{"op": "guard_self", "mult": 0.5, "label": "forced guard"}], target="self", anim="guard"),
     "barrage": mv("Command Barrage", [dmg(115, aoe=True)], target="all", charge=2.4, tell="The baton points at every protector")},
    aff={"storm": "weak"})
boss("B10", "rook", [
    {"at": 100, "cycle": ["arc", "arc", "pulse"]},
    {"at": 60, "cycle": ["sync", "arc", "pulse"], "enter": "Relay lights climb toward synchronization."},
    {"at": 30, "cycle": ["pulse", "arc", "recover"], "enter": "Rook accelerates the pulse; his recovery shows."}],
    {"arc": mv("Relay Arc", [dmg(130, "magical", "storm")], anim="cast", element="storm"),
     "sync": mv("Synchronize", [st("slow", 60, 2)], target="all", anim="cast"),
     "pulse": mv("Synchronization Pulse", [dmg(145, "magical", "none", aoe=True)], target="all", charge=2.6, tell="Three relay lights announce a pulse", weakened_by_part="relay"),
     "recover": mv("Recovering", [{"op": "msg", "text": "Rook steadies himself, exposed."}], target="self", anim="step")},
    aff={"earth": "weak"}, parts=[{"id": "E_RELAY", "name": "Active Relay", "hp_frac": 0.08}, {"id": "E_RELAY", "name": "Active Relay", "hp_frac": 0.08}])
boss("B11", "tidewarden", [
    {"at": 100, "cycle": ["claw", "rise", "claw"]},
    {"at": 55, "cycle": ["rise", "surge", "claw"], "enter": "The flood marker climbs toward the surge notch."},
    {"at": 20, "cycle": ["claw", "claw", "surge"], "enter": "The Warden's core is exposed."}],
    {"claw": mv("Water Claw", [dmg(125, element="water")]), "rise": mv("Rising Water", [{"op": "msg", "text": "The flood marker rises a notch."}], target="self", anim="cast"),
     "surge": mv("Surge", [dmg(140, "magical", "water", aoe=True)], target="all", charge=2.6, tell="The marker reaches the notch — surge coming", element="water", weakened_by_part="valve")},
    aff={"storm": "weak", "water": "absorb"}, parts=[{"id": "E_VALVE", "name": "Current Valve", "hp_frac": 0.1}],
    mods={"atk": 0.72, "mag": 0.72})   # fought by the two-person recovery party (Dain, Oriel)
boss("B12", "vessel", [
    {"at": 100, "cycle": ["tether", "crush", "crush", "order"], "enter": ""},
    {"at": 65, "cycle": ["named", "crush", "order", "crush"], "enter": "The shell cracks; the coercion network shows through.", "affinities": {"light": "weak", "shadow": "resist"}},
    {"at": 30, "cycle": ["rings", "crush", "release", "named"], "enter": "The crown overloads — three pressure rings illuminate.", "affinities": {"storm": "weak", "light": "neutral"}}],
    {"tether": mv("Shield Tether", [{"op": "guard_self", "mult": 0.5, "label": "tether"}], target="self", anim="guard"),
     "crush": mv("Crown Crush", [dmg(150)]), "order": mv("Obey", [dmg(100, "magical", "shadow"), st("silence", 50, 2)], anim="cast", element="shadow"),
     "named": mv("Named Command", [dmg(210, "magical", "shadow")], target="random", charge=2.2, tell="Voss names a command — vary your actions", element="shadow"),
     "rings": mv("Pressure Rings", [dmg(170, "magical", "none", aoe=True)], target="all", charge=2.8, tell="Three rings blaze — Defend through the release", weaker_if_hit=True),
     "release": mv("Venting", [{"op": "msg", "text": "The crown vents; its core is visible."}], target="self", anim="step")},
    aff={"storm": "weak"})
boss("B13", "lanterneater", [
    {"at": 100, "cycle": ["bite", "bite", "douse"]},
    {"at": 60, "cycle": ["douse", "sleep", "bite"], "enter": "A lantern gutters; its shadow picks a sleeper."},
    {"at": 25, "cycle": ["night", "bite", "douse"], "enter": "The long night pulses."}],
    {"bite": mv("Chill Bite", [dmg(150, element="ice")]), "douse": mv("Douse Lantern", [{"op": "msg", "text": "A lantern goes out."}], target="random", anim="cast"),
     "sleep": mv("Sleep Lantern", [st("sleep", 70, 1), dmg(100, "magical", "ice")], target="marked", charge=2.0, tell="The dark lantern chooses a sleeper", weakened_by_part="lantern"),
     "night": mv("Long-Night Pulse", [dmg(160, "magical", "ice", aoe=True)], target="all", charge=2.6, tell="Every lantern dims", element="ice")},
    aff={"fire": "weak", "ice": "absorb"}, parts=[{"id": "E_LANTERN", "name": "Dark Lantern", "hp_frac": 0.06, "aff": {"fire": "weak"}}])
boss("B14", "leviathan", [
    {"at": 100, "cycle": ["bite", "current", "bite"]},
    {"at": 60, "cycle": ["tide", "bite", "current"], "enter": "Wave bands pulse toward one row."},
    {"at": 25, "cycle": ["wreck", "bite", "tide"], "enter": "The wreck's last instant repeats."}],
    {"bite": mv("Reef Bite", [dmg(160)]), "current": mv("Current", [dmg(120, "magical", "water", aoe=True)], target="all", element="water"),
     "tide": mv("Returning Tide", [dmg(200, "magical", "water")], target="row_front", charge=2.4, tell="Beacons flash — the tide returns to the front row", element="water"),
     "wreck": mv("Wreck Memory", [dmg(180, "magical", "shadow", aoe=True)], target="all", charge=2.8, tell="The bell of the lost ship rings", element="shadow")},
    aff={"storm": "weak", "water": "absorb"})
boss("B15", "echo", [
    {"at": 100, "cycle": ["levy", "strike", "levy"]},
    {"at": 65, "cycle": ["orders", "strike", "levy"], "enter": "The command screen duplicates its orders."},
    {"at": 30, "cycle": ["edict", "strike", "orders"], "enter": "FINAL EDICT is printed on the screen."}],
    {"levy": mv("Levy", [{"op": "mp_drain", "amount": 20}, dmg(110, "magical", "none")], anim="cast"),
     "strike": mv("Stamp", [dmg(150)]),
     "orders": mv("Duplicate Orders", [st("weaken", 60, 2)], target="all", anim="cast"),
     "edict": mv("Final Edict", [dmg(190, "magical", "none", aoe=True)], target="all", charge=2.6, tell="The screen names the edict — Defend or dispel")},
    aff={"storm": "weak"})
boss("B16", "cantor", [
    {"at": 100, "cycle": ["silence", "response", "refrain"]},
    {"at": 60, "cycle": ["silence", "canon", "response"], "enter": "A four-beat ring marks the canon."},
    {"at": 25, "cycle": ["chorus", "response", "silence"], "enter": "The Cantor opens its chorus."}],
    {"silence": mv("Mute Refrain", [st("silence", 80, 2)], target="all", charge=2.0, tell="A four-beat ring: silence window — Defend", anim="cast"),
     "response": mv("Response", [dmg(170, "magical", "none")], anim="cast"),
     "refrain": mv("Refrain", [dmg(120, "magical", "shadow", aoe=True)], target="all", element="shadow"),
     "canon": mv("Two-Part Canon", [dmg(110, "magical", "light"), dmg(110, "magical", "shadow")], anim="cast"),
     "chorus": mv("Open Chorus", [dmg(200, "magical", "none", aoe=True)], target="all", charge=2.8, tell="The ring opens: response window after this")},
    aff={"physical": "neutral"})
