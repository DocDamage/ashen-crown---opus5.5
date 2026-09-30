# Writing an auto-skin (tools/maps48/skins/<tileset>.py)

Every map in the game has a collision grid of named *kinds* (floor, wall, water, crate, shelf ...). An auto-skin says
how each kind is drawn with the owner's native 48px art (1 art pixel = 1 screen pixel; one grid cell = 48x48 px).
`tools/maps48/autoskin.py` builds the art for every map of that tileset; collision never changes except where the skin's
auto-dressing adds props (it checks that every spawn, exit, NPC, chest and trigger stays reachable).

Read first: `tools/maps48/kit.py` (Stamp `st(alias, sheet, col, row, w, h, ...)`, Mat), `tools/maps48/autoskin.py`
(Skin, WallStyle), `tools/maps48/skins/common.py` (shared stamps/materials you may import) and the working example
`tools/maps48/skins/interior.py`.

## The art
Packs (aliases in kit.PACKS) live in `F:\Ashen Crown\The Ashen Crown\Assets\CuteSCKR\...` (768x768 sheets, 16x16 cells
of 48px, objects laid out on the cell grid). To look at a sheet with cell coordinates:
    python3 tools/maps48/gridsheet.py "<pack folder name>" [sheet ...]
writes `Claude outputs/tmp/grid/<slug>_<sheet>.png` (column numbers on top, row numbers on the left). Stage it with
device_stage_files (F:\Ashen Crown\The Ashen Crown\Claude outputs\tmp\grid\<file>) and Read the staged copy.
A stamp is a cell rectangle: `st("town", "6", 9, 2, 1, 2)` = sheet 6 of the Medieval Town pack, column 9, row 2, 1 wide,
2 tall. `hgrid` = how many grid rows the stamp stands on (default 1: the bottom row sits on the grid cell and the rest
overhangs upwards, which is right for shelves against a back wall, trees, statues). `cols=(c0, c1)` marks which columns
hold the trunk/base for trees. Materials: `Mat([(alias, sheet, x_px, y_px, w_px, h_px), ...], kind, organic=bool,
prio=int)` - a seamless swatch tiled across the floor (pick big uniform swatches); `organic=True` gives ragged natural
edges against other organic materials; `("color", (r, g, b))` is a flat colour.

## Skin fields
- `ground`: kind -> material name for every walkable/flat kind of the tileset (floor, floor2, path, grass, water, shallow,
  deep, bridge, dock, stairs, door, doorway, snow, ice, ember, sand, salt, ash, moss, roots, puddle, lift, grate ...).
- `walls`: kind -> WallStyle(face=(alias, sheet, x, y, w, h), cap=<material>, face_h=1 or 2). The face is a horizontal
  strip (w px wide, face_h*48 tall) tiled along every wall that has open ground below it; cap is drawn on wall tops.
  Use it for `wall` and usually `cliff`.
- `props`: kind -> list of stamps. Runs of the same kind are filled left to right with the widest stamps that fit.
- `trees`: stamps for `tree`/`tree2` cells. `decals`: flat stamps scattered on open floor (`decal_density` 0.02-0.08).
- `wall_decor`: stamps or field animation names ("torch_wall", "banner_wall_red", "banner_wall_blue") mounted on faces.
- `water_anim`: kind -> field animation ("water_deep", "water_shallow") for animated water.
- `dress_wall`, `dress_open`, `dress_target` (share of open floor to fill: interiors 0.2-0.35, dungeons 0.06-0.12,
  outdoor 0.04-0.08), `dress_kind` (a solid kind, e.g. "crate" or "rock"): extra solid props that raise density.
Every kind used by the tileset's maps must be covered (ground, walls, props or trees); anything else is drawn as the
nearest ground and looks bare.

## Look and rules (from the owner's layout standard)
- One colour mood per region: Crown March warm stone, slate roofs, green verges; Cinder Reach soot brown, brass, ember
  orange, grey steam; Glass Coast sea teal, bleached wood, sand; Skyspine cold blue, white, dark pine, timber; Pale Basin
  ochre sandstone; Ember Sea deep red, black rock, lava glow. Dungeons follow their theme.
- Props must fit the place (mines: carts, timber, tools, ore; archives: books, shelves, water damage; vaults: builder-era
  tech allowed; nothing modern or sci-fi outside builder ruins and the industrial Cinder Reach).
- Props come in clusters and stand against walls; no single-colour floors over big areas (use swatches with texture).
- Never scale art; use cell rectangles exactly.

## Test
    python3 tools/maps48/autoskin.py --preview MAP_ID [MAP_ID ...]
    python3 tools/maps48/preview.py MAP_ID [...] --half --out "<Claude outputs>/tmp/prev_<you>"
then stage and Read the PNGs. Iterate until the maps read clearly as their place. Always pass --preview (never let
autoskin write z48_auto.map), do not run Godot, compile_content or git, and only create/edit files under
tools/maps48/skins/ (skins/<tileset>.py, optionally skins/lib_<yourname>.py for shared pieces).
