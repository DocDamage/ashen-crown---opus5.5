# Combat specification

## Battle contract

Use a side-view, four-character active party with visible readiness gauges. Combat is an authored deterministic simulation with a presentation layer, not damage implemented directly inside animation callbacks. The default is Wait mode; Active mode is an optional setting. Both use exactly the same actions, enemy intents, costs and damage rules. No competitive fairness or internet clock is needed.

Every battler has a stable encounter-local ID, current/max HP and MP, derived stats, readiness, action state, statuses, row, affinities and an immutable content definition reference. Encounter state owns RNG streams, enemy spawns, rewards, flee progress, Concord and once-per-battle flags. UI widgets hold no authoritative HP or inventory counts.

## Readiness and action states

Simulation runs at a fixed 60 Hz with an accumulated fixed-point gauge. Gauge range is 0–1000. Fill rate per simulation second is `100 + 5 × clamp(SPD, 1, 99)`, modified by Haste/Slow and a user battle-speed factor of 0.75, 1.0 or 1.25. Clamp readiness to 1000; never create multiple turns from overflow.

Actor states are FILLING, READY, SELECTING, COMMITTED, CASTING, RESOLVING, RECOVERING and KO, with AIRBORNE as an explicit temporary state for leap skills. Only FILLING advances readiness. Committed actions do not keep charging. A successful resolution resets readiness to zero, then applies explicit refunds bounded to 500 unless the action specification says otherwise. A canceled selection consumes nothing. Queue ties resolve by ready tick, then stable battler ID. Do not sort by the order nodes happen to appear in the scene tree.

Wait mode pauses readiness, cast timers, leap timers and scheduled battle timers while any player command/target menu is open. Cosmetic animation and menu movement continue. Active mode keeps simulation timers advancing during ordinary command selection. The full pause menu, loss of application focus under the default setting, and a modal accessibility/help screen pause both modes. During an action’s presentation lock, simulation does not advance until the authoritative action has been presented; skipping the animation shortens wall-clock presentation, not the action’s simulated power or timing.

## Commit, validation and resource use

Selection creates a proposed command; commit validates actor life, learned/granted ability, target eligibility, silence, MP, item availability and once-per-battle rules. Reserve costs at commit. At resolution, revalidate target existence and life. Offensive single-target actions retarget the lowest stable ID living eligible enemy if the original target fell. Healing retargets the lowest HP-percentage living eligible ally. Revive cancels with a full cost refund when no eligible fallen ally remains. An actor KO before resolution loses the turn but receives reserved MP/item costs back. Once-per-battle flags are consumed only by a valid resolution; the exception is a prevented crash replay, which must replay the already committed transaction exactly once.

Never subtract an item on button press and again on animation completion. Costs are an idempotent transaction keyed to the committed action. The command log records the selected target and any lawful retarget so a failed replay is diagnosable.

## Base commands

Attack uses the current weapon and 100 physical power. Defend consumes an action and reduces direct damage by 50% until the actor’s next resolved action, including the next command’s casting interval. Item uses one shared inventory item through the same transaction path as abilities. Row changes consume an action in battle and are free at safe formation screens. Escape accumulates a shared flee meter in normal encounters: each completed Escape action adds 250, plus any explicitly permitted skill/item bonus, and succeeds at 1000. Bosses visibly disable Escape before item consumption. No random flee failure can repeatedly waste ten turns.

Each character exposes Attack, their role command, Item and Defend; equipped accessory magic and linked summons appear as optional subcommands. Show unavailable commands with a specific reason rather than silently removing them. Use a remembered cursor per character, but never automatically reuse an invalid target or spend a rare item after the encounter changes.

## Damage, healing and affinities

All following constants are initial tuning values, not verified balance. Round only at the final result except where a cost explicitly says round up.

Physical raw damage = `(2 × ATK + 3 × level) × power / 100`.
Magical raw damage = `(2 × MAG + 3 × level) × power / 100`.
Defense multiplier = `100 / (100 + max(0, effective DEF or RES))`.
Healing = `(2 × MAG + 2 × level) × power / 100 + 0.06 × target max HP`.

For damage, apply defense, elemental affinity, row/range, guard and status modifiers, a seeded variance in [0.95, 1.05], and critical factor when eligible; floor once. Damage that is not explicitly immune is at least 1. Healing is at least 1 and capped by missing HP. Healing does not crit. Standard physical critical chance is 5%, capped at 35%, with multiplier 1.5. Standard physical accuracy is 95% before modifiers; spells default to 100% unless explicitly specified. Show MISS, RESIST, IMMUNE and damage as distinct outcomes.

Affinities are weak x1.5, neutral x1.0, resistant x0.5, immune x0.0 and absorb as a separately tagged conversion to healing. Do not encode absorb with negative damage. Resist and weakness do not multiply repeatedly when two items grant the same affinity; use the strongest applicable final category. Elements are physical, fire, ice, storm, earth, water, light, shadow and none. “Phase-specific” is a boss design instruction; the importer must expand it to concrete phase affinities before runtime.

Back-row actors receive half melee physical damage and deal half melee physical damage. Ranged weapons and ranged skills ignore the outgoing row penalty. Magic ignores rows. Incoming ranged physical damage ignores the defensive row reduction. Combine ordinary reduction sources multiplicatively but cap total direct-damage reduction at 80%, excluding an explicit immunity. This prevents an oath, Defend, accessory and Barrier from creating accidental permanent invulnerability.

A level/stat formula must be shared by runtime and preview UI. A test implementation must call the actual runtime formula, not maintain a second conveniently different model.

## Status engine

Use the sixteen status records in `data/statuses.json`. Reapplication refreshes to the larger remaining duration; it does not stack magnitudes. Haste and Slow replace one another. At an actor’s action opportunity, process hard-control skipping consistently; a skipped action consumes the relevant status duration so Stun cannot preserve itself forever. After an actual resolved action, process damage-over-time/healing-over-time, decrement action-based durations, then evaluate KO. Repeated source hits in one action count as one status duration event.

Bosses are immune to Sleep, Stun and Doom unless a named encounter explicitly replaces immunity with a bounded response. Boss Slow is weaker and total ATB delay is capped at 200 between boss actions. Every boss has at least one counter available through generic Attack, Defend or guaranteed consumables. No particular active-party member is a mandatory puzzle key inside a boss battle.

Outside battle, statuses clear except KO; exploration is not a poison-step punishment system. Story seals are progression conditions, not ordinary dispellable combat statuses. Do not let Unwritten Law delete a story gate because both use the word “seal.”

## Character-specific state

Oaths are mutually exclusive Dain-only battle stances; change costs an action. Overcast is one armed spell, nonrandom and nonlethal in self-damage. Corren’s airborne absence advances through simulation time and cannot softlock when all other allies fall. An all-airborne living party is not a defeat. Ivo has one mine per enemy and one team decoy. Nera reveals data and marks targets but does not multiply every mark bonus indefinitely. Oriel exposes already committed intents, not future random draws. Sable has one infusion. Pip’s steal limits are per enemy instance and battle rewards are reconciled once.

A single source action may produce one counter, one interception and its documented triggered effect per eligible recipient. Triggered attacks cannot trigger another counter or reflection. Every reactive effect carries an origin action ID and a recursion depth limit. Test simultaneous damage to a protected ally, Dain’s lethal threshold, and enemy death during a counter.

## Vestiges and Concord

Each character may link one owned Vestige outside battle; a Vestige cannot be linked to two characters simultaneously. Linking does not permanently alter level-up stats. Concord is shared, ranges 0–100, starts at 0 each battle, and is reset on ending the encounter. A successful eligible player action gains 6 Concord, with accessory bonuses capped so a single action can grant at most 10. Defend grants 3 once per completed readiness cycle. Item grants 0 except a Concord Seed. Multi-hit and area attacks count as one action. Summons grant no Concord and each Vestige may be summoned once per battle at a cost of 100.

Silence blocks summoning. A dead or unavailable linked character cannot use its Vestige, but links can be reassigned at the next safe screen. No mandatory overworld route needs a specific summon equipped. Summon animations have normal, short and reduced-flash variants, all resolving the same effects.

## Rewards, defeat and retry

Resolve KO and simultaneous reactions before determining the result. If all living/airborne player actors are gone, defeat takes precedence over a simultaneous enemy wipe. Victory grants XP, gold, drops and unique acquisition IDs in one transaction. It then clears temporary battle statuses and restores exploration at a valid location. Fallen characters remain KO until revived or recovered at a safe service; give a clear prompt if the leader changes.

A defeat offers Retry from Checkpoint and Load Save. Retry restores the checkpoint snapshot, seed and resources; it neither keeps stolen loot nor consumes the supplies from the failed attempt. The player may change formation at the retry preparation screen. Defeat does not quietly advance story flags, create another boss reward, or erase a manual save.
