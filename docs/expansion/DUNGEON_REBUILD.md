# Hand-made rebuild of the 12 story dungeons (and their post-fault rooms)

The owner asked for every dungeon and interior to be hand-made. The story dungeons D01-D12 still use the grids the old
generator wrote (`tools/maps/d*.py`): big rectangles, one line of props, empty floors. Your job is to redraw those
rooms by hand as real FF6-style dungeon rooms, while keeping the game working exactly as before.

You work in your own git worktree. Commit there with
`git -c user.name=Claude -c user.email=noreply@anthropic.com commit`. Edit only the room sections you were given, in
their source file under `content_src/maps/`. Do not touch any other file except `content_src/maps/z48_auto.map`, and
only through `tools/maps/undress.py`. The lead merges the worktrees.

## Read first

- `docs/05_DUNGEON_BIBLE.md` gives each dungeon's theme, rooms, puzzle and boss. Your rooms must tell that story.
- `docs/overhaul/LAYOUT_STANDARD.md` covers FF6 layout and density rules.
- The glyph legend is `LEGEND_BASE` in `tools/compile_content.py`, plus per-map `legend: x=kind` overrides. Solid
  kinds are listed in `SOLID` there.
- Your rooms' current sections and entities, and the scenes they call (`content_src/scenes/*.scn`: grep the scene
  ids), so you know what each switch, read, NPC or trigger is for.
- The tileset's skin, `tools/maps48/skins/<tileset>.py`, shows which kinds get good art. Prefer kinds the skin draws
  (props, walls, trees). Others fall back to generic art.

## Hard rules (the checker enforces 1-4)

1. **Entities stay the same.** Every line under `entities:` stays identical: same coordinates, same conditions, same order.
   The QA story bot, the scenes and the save data all use these coordinates.
2. **Size stays the same.** Keep each room's width and height. Every grid row must be the same width.
3. **Route cells stay walkable.** A cell that a QA route walks to (`["go", x, y]` or `["tile", x, y]` in
   `game/src/qa/routes.gd`) must stay walkable if it was walkable before. The checker checks every route cell on
   every room, which is stricter than needed; accept it.
4. **Standing spots stay walkable.** Spawns stay on walkable cells. Exits, triggers and hazards keep at least one
   walkable cell, and every interactable keeps a walkable neighbour.
5. **Paths stay open.** Everything stays reachable: from every spawn to every exit, NPC, chest, switch, read and
   trigger (`tools/check_entities_reach.py`, `tools/check_reach.py`).
   - Keep the main path at least 2 cells wide where the old room had open floor.
   - Keep hazard lanes (`hazard x1..x2 y1..y2`) as floor: they are timed falling-stone or steam lanes the player
     crosses.
   - Leave 1 free cell in front of every exit.
6. **Puzzles still read.** Puzzle rooms (switch orders, seals, levers, water levels, `tileset_over` entities that
   change tiles) must still read clearly. Keep the cells that `tileset_over` changes the same kind they were, because
   the overlay swaps them.

## What "hand-made" means here

- **Irregular outlines.** No perfect rectangles: bite the walls in and out, add alcoves, corners, collapsed sections,
  ledges, broken pillars and rubble spills. Draw the room as a place with a history, as in the bible.
- **Setpieces that say what the room is.**
  - A redoubt has cells, racks, a muster yard and a gatehouse.
  - An archive has stacks, reading tables, flooded aisles and fallen shelves.
  - A quarry has cart rails, timber props, spoil heaps and tool racks.
  - Aim for 2-4 setpiece clusters per room, placed against walls, not scattered.
- **Varied floor.** Use `floor2`, `path`, `puddle`, `moss`, `roots`, `grate` or `carpet` (via a legend override) to make
  walkways, worn paths, water damage and runners, so no big single-kind floor areas remain.
- **Readable routes.** The main path, side pockets with treasure (existing chests only), and dead ends that reward a
  look. Guide the eye to exits and interactables.
- **Density.** Dungeons are about 8-15% props on open floor (see LAYOUT_STANDARD), heavier along walls, and lighter
  in rooms with hazards or battles.

## Workflow per dungeon

1. **Undress.** `python3 tools/maps/undress.py <ROOM IDS>` removes the rooms' dressed copies, so the compiler uses your
   sources. The lead re-dresses them on the owner's PC afterwards.
2. **Redraw** each room grid in its source section (e.g. `content_src/maps/d07_whitebone.map`). Keep the header and
   entity lines untouched.
3. **Check.**
   - `python3 tools/maps/rebuild_check.py <ROOM IDS>` must say `rebuild problems: 0`.
   - `python3 tools/compile_content.py` must end `compile_content: OK`.
   - `python3 tools/check_reach.py` must report `reachability problems: 0`.
   - `python3 tools/check_entities_reach.py <ROOM IDS>` must report no problems for your rooms. Some known problems in
     other maps are by design, so pass your ids.
4. **Preview.** Print each room's grid and look at it: does it read as the place in the bible? Revise until it does.
5. **Commit** with a message naming the dungeon.

Report back: the rooms you rebuilt, one line per room on what the room now is, and anything you could not do.
