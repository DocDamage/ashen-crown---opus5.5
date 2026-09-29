# Authored decisions and recorded deviations

The handoff references files that were not present in the workspace (package ZIP contents: `CLAUDE.md`,
`CURRENT_STATE.json`, `data/*.json`, `tools/validate_pack.py`, `tools/doctor.py`). Only the combined Markdown
handoff and the kickoff prompt were supplied. Everything below was decided during implementation and is traceable.

## Environment
- Godot 4.7.2-stable (official, `ed1daf0bf`) Linux x86_64 editor downloaded from the official GitHub release
  (user-authorized; 77,860,424 bytes, sha256 `cadd3204…29e4`). Windows export template: to be range-fetched from
  the official template pack (user-authorized "Windows template only").
- Build/test host: Linux cloud sandbox with Xvfb + Mesa llvmpipe (Compatibility renderer). Windows runtime launch
  must be verified on the owner's PC; cross-export alone is not a Windows pass (docs/15 AC065).

## Data reconstruction
- `data/*.json` rebuilt from the handoff's Markdown tables by `tools/extract_catalogs.py`; validator/doctor rewritten.
- Body armour DEF/RES floats (e.g. 3.25) are rounded to integers in the compiler.
- Head items: even-index styles +2 DEF, odd-index +2 RES, applied once in the compiler (as specified).

## Numbers not given in the handoff (initial tuning, unverified balance)
- Level-1 base stats per character (`tools/content/tables.py`, CHAR_BASE). Growth values are the handoff's.
- Dain starts at level 3 (a 34-year-old veteran officer); early level-1 encounters were measured as unwinnable coin
  flips by the route bot (reports/evidence). Recruits use the handoff's join rule (median - 1).
- Enemy derived stats: ATK/MAG = (5 + 2.5 L) x archetype, DEF/RES = (3 + 1.6 L), SPD = 8 + L/2; bosses x1.15 ATK, x1.2 DEF/RES.
  XP = 8 + 5 L, gold = 10 + 6 L; boss XP = 6 x 2.5 x ordinary.
- Post-state enemy variants are compiled records (`E009@22`) with HP scaled by (L/L0)^1.3; not new identities.
- Encounter meter: 55-95 eligible steps per encounter (about 15-26 s of walking at 3.75 tiles/s), 8-step grace after
  map entry, 6-step grace after battles, suppressed within 3 tiles of save lamps.

## Mechanics interpretations
- Boss "parts" (valve, root, relays, lantern) are targetable, never-destroyed battlers: hitting one during a telegraphed
  charge halves that charged move. This implements the catalog counterplay ("attacking the valve also reduces the hit").
- B01 is weak to storm and resists fire (catalog counterplay names the storm flask tutorial).
- Ember Moth's "Burn immunity for 2 actions" is modelled as a 2-action fire ward.
- Save lamps also fully restore HP/MP; separate recovery springs sit before mandatory bosses.
- Tests run inside a normal game process (`--qa-tests`) because Godot's `--script` mode does not register autoloads;
  `tests/run_all.gd` relays that process for the templated command.
- Encounter meter persists across room transitions (reset only after a battle); each arrival grants an 8-step grace. Found in seg2 traces: short rooms reset the meter so encounters almost never occurred.

## Session 2 decisions (CH11-CH24, post-state, release)
- D09 has three visible synchronization relays (south, north-lift, bridge); CH10 foreshadows the fourth (hidden) relay in Ivo's line, CH06 via the pasted-over archive diagram. SC08 reveals it.
- Protected backups: `backup_pre_dais` (D09_R04 warning) and `backup_pre_finale` (D10 Accord Dock). They are written by the story, never by slot saves, and appear read-only in Load as "Protected: ...".
- The catastrophe transaction (phase post) is followed by an automatic atomic save to the slot the run last used (if any); the pre-transition state is kept in `backup_pre_catastrophe`.
- The CH12 escape is a short playable collapse corridor (D09_ESC) whose falling-stone hazards push the player back one tile (local retry, no damage).
- Pre-state overworld gating is done at location entrances (authored "not yet" scenes) because the continent is open country; blocks remain as flavour/secondary gates.
- Pre-state dungeons revisited after the catastrophe exit to WORLD_POST (Game.world_for_phase). Post-state towns use dedicated post maps (T01_POST, T02_SQUARE_POST, T03_POST, T04_UPPER, T05_POST, T06_POST); quest dungeons at old locations use small post rooms (D04P, D05P, D08P, D07P_R03, D02P_*).
- Wayfarer: board by facing the parked ship; land only inside/next to a marked landing field (failure leaves the ship flying with a visible reason); recall on foot from any landing field; the berth tender at Hearthward brings the ship home. The deck (W_DECK) holds formation, stores, rest and the CH21 crew board.
- CH21 is a window, not a chapter gate: the crew board and NPC hooks surface all twelve quests after CH20.
- Final dungeon: split into Team A (west) / Team B (east); locks alternate W1 -> E1 -> W2 -> E2; each lung has an unconditional swap bell so neither team can be shut in; formation is locked while split.
- Post-clear: "Continue from Before the Final Descent" loads the pre-finale backup and re-applies completed quests, quest flags and epilogue flags (the clear state), labelled honestly as a snapshot.
- Creature speakers (Vestiges, B15 echo, B16 cantor) use portraits derived from the project's own generated Vestige/boss art (tools/art/creatures.py).
- Encounter meter persists across rooms (reset only by a battle); arrival grace 8 steps.
- Save lamps were added before every boss room that lacked one (D03P_R02, D04_R03/R04, D08_R03/R04, D09_R05).
- B11 Ash-Tide Warden is fought by the two-person recovery party: no escort add, attack/magic x0.72 (seed HP kept). Found by seg6 trace: three consecutive defeats at Lv24 with two members.
- Catch-up XP: after each story level floor, members below floor+4 earn up to x3 battle XP (1 + 0.25 per level below). Direct-route traces reached CH16 at Lv24 against a Lv28 floor and the Lv34-42 final dungeon band.
- Catch-up XP tuned to +35% per level below band, cap x4 (seg8 trace: Lv25 party in starter gear could not hold the Lv35 final-dungeon groups).
