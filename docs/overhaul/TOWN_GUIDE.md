# Hand-made town maps (maps48)

Goal: replace the flat auto-skinned town exteriors with hand-composed maps at the quality of the pilot
`tools/maps48/maps/t01_brackenford.py` (Brackenford, T01_PLATFORM). Read these first:
- `docs/overhaul/LAYOUT_STANDARD.md` - the owner's layout and set-dressing standard (scale in hero heights H,
  density targets, the checklist). Towns target FF6-like density (detail coverage ~70-80%).
- `tools/maps48/maps/t01_brackenford.py` - the pilot; copy its structure.
- `tools/maps48/kit.py` (Map API: use/fill/rect/blob/path/place/anim/water_anims/rails_h/scatter/reserve/ent/save,
  Stamp `st()`, Mat), `tools/maps48/lib_r01.py` (Crown March stamps: houses with door offsets, props, trees),
  `tools/maps48/SKIN_GUIDE.md` (how to look at art sheets with gridsheet.py and stage/Read the PNGs), and the region
  skins in `tools/maps48/skins/` (town_r01..r05, capital, harbor, furnace, underways, lib_d.py, lib_cold.py,
  common.py ...) whose stamps and materials you can import and reuse.

## Hard rules
1. Keep each map's id, size (w x h), header (name, tileset, music, zone, location, region, save, encounters) and
   EVERY entity line exactly as it is now - same coordinates, same text. Copy them from the map's current section in
   the winning map file (for most towns `content_src/maps/z48_auto.map`; T01_POST lives in `content_src/maps/t01.map`).
   Lines ending in `#! ov:<key>` must be kept verbatim too (they are placed by tools/maps48/place_entities.py).
   QA routes walk to these coordinates, so do not move anything.
2. Build the town AROUND the fixed points: door entities must sit on a building's door cell (use the house stamps'
   door offsets, see lib_r01 H_* comments; `m.place()` marks the door cell kind "door"); shops/inns sit at counters or
   stalls; exits stay open at the map edge; NPC cells stay walkable; every spawn, exit, door, npc, chest, sign, save,
   trigger and switch must stay reachable from every other one.
3. Pre- and post-fault variants of a town (e.g. T03_TOWN and T03_POST) must read as the same place: same street
   plan and buildings where the entities allow, the post version damaged/flooded/repaired as its name and story say.
4. Region moods (LAYOUT_STANDARD): Crown March warm stone/slate/green; Cinder Reach soot brown, brass, ember orange,
   steam (industrial allowed); Glass Coast sea teal, bleached wood, sand; Skyspine cold blue, white, dark pine,
   timber; Pale Basin ochre sandstone; Ember Sea (Hearthward) deep red, black rock, lava glow, pontoons.
5. Main buildings at least 4 H tall (compose larger buildings from wall/roof pieces when a whole-house stamp is too
   small); props clustered against walls; no big empty single-material areas; never scale art.

## Workflow
- Write `tools/maps48/maps/<group>.py` with one function per map (like `platform()` in the pilot) and a
  `__main__` that calls `write_group("<group>", [m.save() for m in ...])`. It writes `content_src/maps/z48_<group>.map`
  (which overrides the auto-skin) and the art into `game/assets/ext/maps48/`.
- Put new shared stamps in `tools/maps48/lib_<group>.py`. Do not edit kit.py, lib_r01.py, autoskin.py or other
  people's files.
- Check: `python3 tools/maps48/maps/<group>.py && python3 tools/compile_content.py && python3 tools/check_reach.py`
  (compile must print OK; check_reach must report 0 problems), then
  `python3 tools/maps48/preview.py MAP_ID --half --out "../Claude outputs/tmp/prev_<group>"` and stage + Read the PNG
  (device path `F:\Ashen Crown\The Ashen Crown\Claude outputs\tmp\prev_<group>\<file>`; staged copies can be cached,
  so write each iteration under a new file name). Iterate until each map reads clearly as its place.
- Do not run Godot or git. Other agents work on other towns at the same time; compile_content writes
  game/content/content.json, so if compile fails in a file that is not yours, wait a few seconds and rerun.
