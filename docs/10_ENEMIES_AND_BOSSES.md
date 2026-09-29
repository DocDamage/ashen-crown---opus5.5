# Enemy and boss bible

## Ordinary enemies — 40 identities

| ID | Name | Home | Level | HP | Weakness | Behavior |
| --- | --- | --- | --- | --- | --- | --- |
| E001 | Rail Rat | D01 | 3 | 144.0 | fire | Bites the lowest current-HP front-row member; its tell is a short crouch. |
| E002 | Clamp Beetle | D01 | 3 | 194.4 | storm | Alternates a normal hit and one-action shell; attack another target during shell. |
| E003 | Quarry Wisp | D01 | 3 | 144.0 | ice | Charges a small fire bolt; interruptible by any direct hit during its announced charge. |
| E004 | Ministry Hound | D01 | 3 | 144.0 | earth | Marks one target before a lunge; cannot mark a fallen ally. |
| E005 | Canal Slime | D02 | 5 | 192.0 | fire | Splits once below 50% HP; child has no further split and no extra rare loot. |
| E006 | Seal Drone | D02 | 5 | 192.0 | storm | Applies short Silence, then a weak strike; cannot Silence the whole party at once. |
| E007 | Ledger Moth | D02 | 5 | 192.0 | ice | Steals at most 10 temporary battle gold; all stolen gold returns on victory. |
| E008 | Patrol Shell | D02 | 5 | 192.0 | storm | Guards the nearest ally for one action, then exposes its core. |
| E009 | Briar Wolf | D03 | 7 | 252.0 | fire | Coordinated bite gains 10% if another wolf lives; capped at two wolves. |
| E010 | Root Mite | D03 | 7 | 252.0 | ice | Applies Poison only after a one-action sap tell. |
| E011 | Pollen Bell | D03 | 7 | 252.0 | fire | Sleep pollen affects one target and cannot be reapplied before that target acts. |
| E012 | Bog Lantern | D03 | 7 | 252.0 | storm | Alternates water damage and a harmless lure animation that reveals its next target. |
| E013 | Rivet Imp | D04 | 10 | 365.0 | ice | Throws a ranged rivet, then reloads for one opportunity. |
| E014 | Boiler Crab | D04 | 10 | 492.75000000000006 | ice | Pressure grows for two actions, then a small area burst; cold reduces pressure. |
| E015 | Soot Sprite | D04 | 10 | 365.0 | light | Uses Blind, then weak shadow damage; healing items remain usable. |
| E016 | Furnace Hand | D04 | 10 | 365.0 | storm | Raises a fist before a strong single-target strike; defense halves it. |
| E017 | Tide Page | D05 | 12 | 455.0 | fire | Copies the element of the last incoming spell at reduced power. |
| E018 | Salt Leech | D05 | 12 | 455.0 | storm | Drain heals only actual HP damage dealt. |
| E019 | Bell Diver | D05 | 12 | 455.0 | light | Alternates melee and a water spell; explicit undead tag permits hostile healing. |
| E020 | Archive Eye | D05 | 12 | 455.0 | shadow | Reveals and then targets the highest-MP ally; never drains more than 15 MP. |
| E021 | Chain Kite | D06 | 14 | 557.0 | ice | Two light hits are one source action for counter limits. |
| E022 | Gust Viper | D06 | 14 | 557.0 | earth | Dodges melee slightly; ranged and magical counters remain reliable. |
| E023 | Ballast Golem | D06 | 14 | 751.95 | storm | High DEF, low RES; attacks slowly with a visible windup. |
| E024 | Sky Tick | D06 | 14 | 557.0 | fire | Applies Slow to one target, then rests. |
| E025 | Ivory Sentinel | D07 | 16 | 671.0 | shadow | Alternates physical guard and magic guard, visibly changing sigils. |
| E026 | Seal Leech | D07 | 16 | 671.0 | light | Removes one party buff; never steals permanent learned abilities. |
| E027 | Frost Runner | D07 | 16 | 671.0 | fire | Fast ice bite, low HP; no unavoidable opening burst. |
| E028 | Binding Hound | D07 | 16 | 671.0 | storm | Brief one-target Stun; respects hard-control recovery protection. |
| E029 | Memory Shard | D08 | 19 | 864.0 | shadow | Echoes a normal Attack once, using its own stats. |
| E030 | Pale Singer | D08 | 19 | 864.0 | physical | Heals one enemy at 50% power before repeating a weak light spell. |
| E031 | Glass Widow | D08 | 19 | 864.0 | earth | Telegraphed Bleed; cleanse or switch to magic/Item to reduce its cost. |
| E032 | Absent Knight | D08 | 19 | 864.0 | light | Strong front-row melee; low accuracy and explicit undead affinity. |
| E033 | Crown Relay | D09 | 22 | 1085.0 | storm | Empowers one ally by 10%; duplicate relays do not stack buffs. |
| E034 | Ash Lancer | D09 | 22 | 1085.0 | ice | Charges for one full opportunity, then strikes a marked row. |
| E035 | Threshold Wisp | D09 | 22 | 1085.0 | water | Fire spell followed by a self-exposing recovery period. |
| E036 | Edict Shell | D09 | 22 | 1464.75 | shadow | Weaken seal on one target, then slow physical strike. |
| E037 | Broken Seraph | D10 | 35 | 2352.0 | shadow | Warns before light area damage; physically fragile. |
| E038 | Cinder Automaton | D10 | 35 | 2352.0 | ice | Rotates defense and pressure without invulnerable phases. |
| E039 | Hollow Choirling | D10 | 35 | 2352.0 | physical | Schedules a two-action Doom warning; player has cleanse and damage options. |
| E040 | Crown Remnant | D10 | 35 | 2352.0 | light | Cycles attack families to teach the final boss; no unique stolen keys. |

## Encounter formation policy

Each main dungeon has at least four authored ordinary formations using its four enemy identities, with at least one formation teaching its boss’s relevant counterplay. Start with one enemy or a simple pair, then combine pressure and support. Three enemies is the default upper limit; four is reserved for a clearly reviewed late-game formation. Avoid stacking two hard-control enemies unless the target-selection policy prevents indefinite control.

Post-state revisits may use stronger variants with explicit level/stat overrides and changed drops. These are variants, not extra enemy identities counted toward forty. Optional dungeons draw appropriate late-game identities with palette-coherent variants; their optional bosses supply the unique encounter design. Do not create invisible scaling based on the current player level. Store a fixed region-stage level in the formation record.

Formations require named IDs, terrain/location conditions, phase conditions, enemy instance slots, reward policy, camera framing and optional tutorial hints. The agent must author this formation layer during implementation; the forty-row catalog alone does not create encounters or prove playability.

## Bosses — 16 identities

### B01 — Extractor Warden

**Location:** D01; **chapter:** CH01; **optional:** False; **seed HP:** 950.

**Tell:** A digging arm pauses over one target while a red pressure gauge fills.

**Counterplay:** Defend the marked target or use Tessa’s storm flask tutorial pickup; attacking the valve also reduces the hit.

**Phases:** 100: piston jab; 65: telegraphed clamp; 30: vent and sweep.

**Victory:** The occupied lift is disconnected after victory, never destroyed by the battle.

### B02 — Brass Bailiff

**Location:** D02; **chapter:** CH02; **optional:** False; **seed HP:** 1400.

**Tell:** A stamped warrant names its next target one action before restraint.

**Counterplay:** Cleanse or destroy the paper seal; Guard reduces the follow-up.

**Phases:** 100: baton and restraint; 50: duplicated warrants with only one active seal.

**Victory:** Defeat disables the machine; no all-party permanent restraint.

### B03 — Rootbound Stag

**Location:** D03; **chapter:** CH03; **optional:** False; **seed HP:** 2100.

**Tell:** The antlers bloom before a root binds the back row.

**Counterplay:** Burn one root or use a weapon attack twice; bind expires even without the ideal counter.

**Phases:** 100: hoof and vines; 60: root cage; 25: pollen burst.

**Victory:** The growth seal breaks; the underlying creature survives as V02’s guardian.

### B04 — Foundry Colossus

**Location:** D04; **chapter:** CH04; **optional:** False; **seed HP:** 2900.

**Tell:** Three vents light from left to right before the boiler sweep.

**Counterplay:** Use ice, ground the charge or defend; pressure resets after the sweep rather than climbing forever.

**Phases:** 100: rivet strikes; 70: steam screen; 35: boiler sweep.

**Victory:** No story worker can die through random battle targeting.

### B05 — Bell-Sworn Custodian

**Location:** D05; **chapter:** CH06; **optional:** False; **seed HP:** 3800.

**Tell:** One of three visible bells vibrates before the Custodian mirrors an element.

**Counterplay:** Use a different element or physical attacks; a mirrored element resists rather than instantly kills the party.

**Phases:** 100: salt lash; 60: mirror bell; 25: choral wave.

**Victory:** Archive shelves remain accessible after victory.

### B06 — Chain Roc

**Location:** D06; **chapter:** CH07; **optional:** False; **seed HP:** 4700.

**Tell:** The tether strains and a shadow marks the row targeted by the dive.

**Counterplay:** Defend or use Corren’s aerial counter; either row can be made safe.

**Phases:** 100: talon; 55: tethered dive; 25: free-wing gust.

**Victory:** Break the tether; this is not the same entity as V04, which guarded the wind shrine.

### B07 — Ivory Adjudicator

**Location:** D07; **chapter:** CH08; **optional:** False; **seed HP:** 5600.

**Tell:** A visible sigil announces whether the next seal targets a skill or an item.

**Counterplay:** Alternate command families or dispel; basic Attack and Defend are never simultaneously locked.

**Phases:** 100: seal and strike; 65: judgment mark; 30: two seals with a full action of warning.

**Victory:** Sable removes the remaining cell locks in the following scene.

### B08 — Pale Choir

**Location:** D08; **chapter:** CH09; **optional:** False; **seed HP:** 6500.

**Tell:** Three masks highlight the next repeated command it will echo.

**Counterplay:** Vary actions or defend the repeat; players are not punished for merely opening menus.

**Phases:** 100: memory needle; 60: echo command; 25: shared refrain.

**Victory:** All contradictory testimony remains; defeating it does not delete a culture’s history.

### B09 — Marshal Voss

**Location:** D09; **chapter:** CH11; **optional:** False; **seed HP:** 7800.

**Tell:** Voss raises the command baton and points to a protector.

**Counterplay:** Change targets, dispel the order or defend; counterattacks have a per-action recursion guard.

**Phases:** 100: sword command; 55: forced guard; 25: command barrage.

**Victory:** Voss retreats into the apparatus. The player wins the encounter normally.

### B10 — Elian Rook, Threshold Maker

**Location:** D09; **chapter:** CH12; **optional:** False; **seed HP:** 8800.

**Tell:** Three relay lights announce a full-party synchronization pulse.

**Counterplay:** Break either active relay or defend; relay destruction reduces rather than cancels the required story event.

**Phases:** 100: relay arc; 60: synchronization; 30: accelerated pulse with visible recovery.

**Victory:** Rook is defeated. His previously established secondary route triggers the catastrophe in the subsequent scene.

### B11 — Ash-Tide Warden

**Location:** D03; **chapter:** CH14; **optional:** False; **seed HP:** 4600.

**Tell:** A flood marker rises one step per action; a clear notch indicates the surge threshold.

**Counterplay:** Strike a current valve, defend or use Nera’s Snare on the channel add.

**Phases:** 100: water claw; 55: rising surge; 20: exposed core.

**Victory:** Balanced for Dain, Oriel and Nera, not a full four-person party.

### B12 — Crown Vessel

**Location:** D10; **chapter:** CH22; **optional:** False; **seed HP:** 26000.

**Tell:** Phase 1: shield tether; phase 2: named command; phase 3: three illuminated pressure rings.

**Counterplay:** Phase 1: separate targets. Phase 2: alternate commands and dispel. Phase 3: stagger attacks and defend during the visible release. All counters also have accessible consumable equivalents.

**Phases:** 100: Voss controls the shell; 65: coercion network exposed; 30: overloaded crown. Three phases share one boss record and reward transaction.

**Victory:** One final battle, no unannounced new antagonist. Story release follows the victory.

### B13 — Lantern Eater

**Location:** D11; **chapter:** CH21; **optional:** True; **seed HP:** 15500.

**Tell:** A lantern extinguishes and its shadow selects the next sleeper.

**Counterplay:** Relight it with fire or a reusable arena interaction; immunity is not required.

**Phases:** 100: chill bite; 60: sleep lantern; 25: long-night pulse.

**Victory:** V07 pact offered after victory.

### B14 — Heartless Leviathan

**Location:** D12; **chapter:** CH21; **optional:** True; **seed HP:** 19000.

**Tell:** Wave bands and beacon flashes show the next current direction.

**Counterplay:** Ground the charge or defend the marked row; audio and visual timing match.

**Phases:** 100: reef bite; 60: returning tide; 25: wreck memory.

**Victory:** V08 pact offered after the coercive loop is broken.

### B15 — Regent’s Echo

**Location:** D02; **chapter:** CH21; **optional:** True; **seed HP:** 18000.

**Tell:** The old command screen names the action that will be taxed next.

**Counterplay:** Choose a different action, dispel or accept a bounded penalty. It never steals unique gear or deletes saves.

**Phases:** 100: levy; 65: duplicate orders; 30: final edict.

**Victory:** Reward A023 exactly once; source records retained.

### B16 — Null Cantor

**Location:** D10; **chapter:** CH21; **optional:** True; **seed HP:** 23500.

**Tell:** A visible four-beat ring marks a silence window, then a response window.

**Counterplay:** Defend through silence; act through response; Wait mode preserves the same simulation beats.

**Phases:** 100: mute refrain; 60: two-part canon; 25: open chorus.

**Victory:** Reward A024 and music variation, not a mandatory finale key.

## Boss acceptance rules

The first occurrence of a large attack must have a readable tell and a survivable generic response. Do not assume a particular accessory, rare drop or optional ultimate. Retry preserves learning without permanent item loss. A phase threshold crosses once and queues its transition after the current action’s complete reaction chain. Simultaneous multi-hit damage must not start the same phase twice. A boss may resist an element without becoming invulnerable to every command available to a legal party.

Final-boss phases are one encounter with one reward identity. The two-party dungeon challenges must use formations tuned for the weakest legal team, not only a favorite composition. Give a preparation warning when one team has no healing skill, but never falsely prohibit it when items and shared recovery make it viable.
