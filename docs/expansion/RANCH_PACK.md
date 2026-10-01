# Super Retro Ranch (premium v32, by Gif) - what is in the pack and how the ranches use it

The owner's pack lives at `Assets/Ranching/SuperRetroRanch` (on the owner's PC: `F:\Ashen Crown\The Ashen Crown\Assets\Ranching\SuperRetroRanch`).
Store page: https://farm-animal.itch.io/farm. It is a **16x16 pixel-art farming kit** (Stardew-like farm life): crops with growth
animations, farmers working with hoe / watering can / shovel, farm animals in 4 directions, seasonal tiles and autotiles,
a farmhouse with an animated door, ~70 objects, weather overlays, UI frames, music and icons.

This file is the readme for it: read it before touching `tools/art/install_ranch.py`, `tools/maps48/maps/ranch.py`,
`tools/maps48/ranchkit.py` or the drawing code in `game/src/meta/ranch.gd`.

## 0. Scale and the game

- The pack is native 16 px. The game's logical screen is 320x240 units with 16-unit map cells, drawn x3 (960x720). So
  **one pack pixel = one logical unit**, and a 16x16 tile is exactly one map cell (48 screen pixels). Nothing is rescaled
  except x3 nearest; the `engines/RPG_Maker_MV_MZ` 48 px re-exports are **not** used.
- `weathers/rays/*_320x240.png` are exactly the logical screen: drawn 1:1 as a screen overlay.
- Animals: 16x20 frames (dove, coney, cat, fox, mouse, egg, nest) stand on one cell; 32x32 frames (cows, pigs, farmers)
  are about two cells wide and overhang one cell upwards, feet on their cell.

## 1. Folder layout (`assets/`)

| folder | what | frame format |
|---|---|---|
| `animals/` | birds (dove: idle L/R, fly 4 dirs, dead; nest), bunnies, cats (+ sleep), cows (36 colours), egg (idle, move = wobble, opened), fireflies, foxes, mouses (+ dead, cheese), pigs (6 colours, adult + baby + grow) | file names give `WxH` and `Nframes`; one row per file |
| `characters/` | `males/male_01`, `females/female_01`, each with and without a hat (`_hat_`): idle, walk, hoe, water, shovel | 32x32 frames; **columns = frames, rows = directions down, left, right, up** (idle: 32x128 = 1 frame x 4 rows; others 96x128 = 3 frames x 4 rows) |
| `crops/<crop>/` | 19 crops: `growth_basic` strip (+ corn `growth_smooth`, `frozen`, `on_fire`, `shake`, `tempest`) and `icon` | strips left to right; 16x16, 16x32 or 18x32 per frame |
| `tiles/` | 256x256 sheets on a 16 px grid: ground_01..03, snow_01, cliff_01..03, cliff_snow_01..03, fence_01, tree_01..02; water_01..05 (80x16 = 5 animated frames) | see section 3 |
| `autotiles/` | 16x96 six-tile strips (grass, fence, snow, leaf, field, animated water) in the pack's own layout, `template_SuperRetroRanch.png` shows it | we use the Godot re-exports instead (section 2) |
| `buildings/` | `building_01_16x16.png` (the farmhouse) and `doors/door_01` (closed, opened, opening 4 frames) | |
| `objects/` | `objects_01/02_16x16.png` (256x256 prop sheets), campfires, chests, coins (8 frames), ice blocks, the rail kart (`kart/`: idle / chest / move / chest opening in 4 dirs, `rails_16x16.png`), the sickle (closed / opening / slicing 8 frames, 48x48) | |
| `visual_effects/` | droplets (5 frames 16x16), fires (4 kinds, 3 frames of 16x26) | |
| `weathers/` | rain_01 (136x80 tile), rays ray_01/02 in white / blue / red (320x240), snow_01 (64x64 tile), wind_01 (272x160 tile) | screen overlays |
| `icons/` | coin, gems 1-6, hearts 1-6, helmet, potions 1-3, shield, sword (16x16) | heart_01 full, 02 half, 03 empty, 04 small, 05 green, 06 grey |
| `user_interfaces/` | 9-split themes basic / cute / default (48x48 = 3x3 of 16) and the Roboto font | |
| `musics/` | themes `field`, `town`, `village` (loopable WAV), ambients `night_01`, `rain_01`, melodies fanfare / gameover / inn | |

`engines/Godot/autotiles/2x2` and `3x3` hold Godot terrain-ready copies of every autotile with templates; `engines/Unity`
the same for Unity; `info/ChangeLog.txt` the version history (v32, July 2026: field autotiles, more signposts, engine
exports, melodies; v30: 36 cow colours; v29: sun rays, fireflies, night/rain ambients; v28: piglets and pig colours).

## 2. Autotiles: the Godot "3x3 minimal" sheets (what the game uses)

`engines/Godot/autotiles/3x3/**/_RANCH_AUTOTILE_<name>.png` are 192x64 = **12x4 tiles of 16 px**, the standard 47-tile blob
layout; animated water sheets are 768x64 = 4 frames of 192x64 side by side. `template_Godot_3x3.png` marks each tile's
bits: a tile is split in 3x3 zones (pixels 1-5, 6-10, 11-15); a red zone means "terrain there" (centre, the four edges,
the four corners). `ranchkit.blob_table()` (Python) and `Ranch._blob_cell()` (GDScript) decode it directly, so a cell's
8-neighbour mask (corners only counted when both edges are set) picks its tile. The install copies them flat to
`ext/ranch/autotiles/<name>.png` (prefix dropped).

What "terrain" and "outside" are in each sheet (all opaque except fences and leaf):

| sheet | terrain (red) | outside |
|---|---|---|
| grass_01 | grass | grass (plain fill) |
| grass_on_dirt_01 / 02 | pale sand dirt (244,205,162) / orange dirt (238,161,96) | grass (113,171,49) with a grass lip |
| grass_on_rock_01 / 02 | grey / pale cobbles | grass |
| grass_on_snow_01 | snow | grass |
| snow_on_grass_01 | grass | snow |
| snow_01 | snow | snow |
| field_01 | orange dirt | brown soil (181,109,86) |
| field_02 | tilled soil (181,109,86) | orange dirt |
| field_03 | brown soil | dark soil (134,73,75) |
| field_04 | dark furrowed soil (134,73,75) | brown soil |
| water_on_grass_01 / 02 | light / deep blue water (4 frames) | grass |
| water_on_dirt_01 / 02 | green / purple murky water (4 frames) | orange dirt |
| fence_01..04, light_fence_01 | fence posts and rails (grey, brown, grey-purple, ice; light rails) | transparent |
| leaf_01 | leaf piles | transparent |

So the colours chain: grass -> orange dirt (grass_on_dirt_02) -> tilled (field_02) -> watered. The install derives
`field_wet.png` (field_02 with the tilled soil turned to field_04's darker colours) and `field_04_wet.png` (field_04 darkened
again) for watered beds.

## 3. The 256x256 tile sheets (16 px grid, (col,row))

**Terrain blocks** (ground_01, snow_01, cliff_*): RPG-Maker-like **3 columns x 5 rows** blocks: rows 0-1 cols 0-1 are a 2x2
of inner-corner tiles (notches at their outer corners), col 2 row 0 the terrain fill, col 2 row 1 the outside fill, rows 2-4
a 3x3 patch (corners, edges, centre). `ranchkit.block_tile` composes them per 8x8 quarter; cliffs use whole tiles
(`slice9`) because the rock face is a full tile row.

- `ground_01`: block (0,1) orange dirt on light grass; (3,1) brown dirt on dark grass; (0,6) dark grass on light grass;
  (3,6) light grass on dark grass; (8,0) a light-grass rim round a transparent hole (grass patches on any ground: holes
  everywhere else); (8,5) orange on brown; (11,5) brown on orange; (8,10) dark soil on brown; (11,10) brown on dark.
  Rows 11-14 cols 0-6: raked bed strips (row 11-12 orange with brown furrows, rows 13-14 brown with dark furrows;
  per row: col 0 left end, 1 middle, 2 right end, 3 single; cols 4-6 vertical pieces). Fills: (2,1) orange, (2,2) light
  grass, (5,1) brown, (5,2) dark grass.
- `snow_01`: the same layout in snow: block (0,1) orange dirt on snow, (2,2) snow fill, (8,0) snow rim round a hole.
- `ground_02`: (0..1,1..2) textured grass tiles; (0..3,3..4) cobbles (orange, grey, red, dark; ring stones); (8..10,0)
  flowers, (11,0) stump, (12,0) tiny mushrooms; (8..12,1) mushrooms (orange, red, green, purple, the dark brown one used
  as the truffle icon); (8..11,2..5) pebbles in 4 colours.
- `ground_03`: grass clumps and bushes. Columns 8-9 / 10-11 hold round bushes (32x32) and col 12 tufts (16x16), each 32 px
  row band one shade from pale (row band 0) to near black (band 6).
- `tree_02`: pairs of trees by season, small 32x32 at (+0,+16) and big 48x48 at (+32,+0) from each origin: (0,0) spring
  green, (0,48) summer dark green, (0,96) blossom pink, (128,0) autumn yellow, (128,48) fall orange, (128,96) snow. Trunk:
  bottom centre; the game stands the trunk on its cell (big: anchor -16,-32; small: -8,-16). `tree_01` = the spring pair.
- `cliff_01/02/03` (grey, brown, red rock) and `cliff_snow_01..03`: block (0,1) a raised ledge (grass / snow top, rock
  sides, a one-tile rock face on the bottom row); (3,1) the same with a white outline; cols 8-13 rows 0-4 pits with water;
  cols 8-13 rows 5-14 holes and edges; (0,12) stairs. Ledges are low (one face row): stack plateaus for terraces.
- `fence_01`: loose fence pieces (posts, rails, diagonals) for hand placement; the game uses the fence autotiles.
- `building_01`: the farmhouse at (0,1)-(3,3) (4x3 cells: two roof rows, the wall row with the door at (1,3) and windows).
  The game cuts (0,15,65,50) so the corners stay transparent, and tints the roof (and walls) for barns and longhouses.
- `objects_01`: row 1 pots; row 2 crates and small chests; (0,3) sack, (1,3) bowl; (2..3,3..4) bench/table; (3..4,5..6)
  lamp posts (red, blue double); (0..2,6) mailboxes; rows 7-10 **signposts**: (0,7) blank, (1,7) lined, (0,8) planks, then one
  per crop icon: tomato (7,8), berry (3,7), eggplant (5,7), pumpkin (6,7), beetroot (7,7), leek (4,8), grape (6,8), bamboo
  (0,9), carrot (1,9), pepper (3,9), celery (4,7), cauliflower (5,9), broccoli (6,9), lettuce (7,9), radish (1,10), onion
  (2,10), wheat (3,10), potato (4,10), corn (5,10) (the game's seed icons are these signposts).
- `objects_02`: (8,1) bucket, (9..12,0..1) barrels 16x24 (orange lid, empty, low water, full); (8..9,2) buckets; (8..15,3..4)
  four stone rings 32x32 by water level (troughs / well heads); (8..15,5..7) four roofed wells 32x48; (8..11,8..11)
  **irrigation pipes** (a horizontal run at (9,10), a vertical one at (10,10) with a cap below, a loop, junctions), (12,8)
  gauge, (12..13,9) arrow pads, (14..15,8..10) valve wheels.

## 4. Sprites: frames, directions, anchors (feet)

| sprite | file | frames | anchor used by ranch.gd (cell top-left = 0,0) |
|---|---|---|---|
| farmer idle | `characters/*/idle/*_idle_32x32.png` | 1 x 4 rows (down, left, right, up) | drawn at (-8,-9): feet (16,24) on the cell's bottom centre |
| farmer walk / hoe / water / shovel | `*_<task>_32x32_3frames.png` | 3 x 4 rows; walk played 0-1-2-1, work loops 0-1-2 at 4 fps | (-8,-9) |
| cow | `cows/cow_01/<colour>/idle/*_idle_<dir>_32x32.png`, `move/*_move_<dir>_32x32_4frames.png` | idle 1, move 4 | (-8,-11) |
| pig adult / baby | `pigs/pig_01/<colour>/[baby/]idle|move/...` ; `baby/grow/*_grow_32x32_6frames.png` | idle 1, move 4, grow 6 | adult (-8,-11), baby (-8,-8) |
| dove | `birds/bird_01/idle/*_idle_left|right_16x20.png`, `fly/*_fly_<dir>_16x20_4frames.png` | idle 1 (left/right only), fly 4 | idle (0,-1), flying (0,-8) |
| coney, cat, fox, mouse | `<kind>/<kind>_01/idle|move/...16x20[_4frames].png`; cat `sleep_16x20_2frames`; mouse `dead_16x20` | idle 1, move 4 | (0,-4) |
| nest / egg | `birds/nest_16x20.png`; `egg/idle`, `egg/move` (4-frame wobble), `egg/opened` | | (0,-4); eggs offset on the nest |
| kart | `objects/kart/idle/[chest_closed_|chest_opened_]idle_<dir>_22x25.png`, `move/chest_move_<dir>_22x25_3frames.png` | | (-3,-10): wheels on the rails of its cell |
| rails | `objects/kart/rails_16x16.png` (80x32): turntable (1,1,30,30); horizontal track at x 39-75, y 0-15 (ties every 8 px; the game repeats x 41-57 and uses the ends at 39 and 59); vertical tracks in the lower right | | flat |
| sickle slicing | `objects/sickle/sickle_slicing/*_48x48_8frames.png` | 8 | centred on the cell (-16,-24) |
| droplets | `visual_effects/droplets/droplet_01_16x16_5frames.png` | 5 | on the cell |
| fires | `visual_effects/fires/fire_0N_16x16_3frames.png` (frames 16x26) | 3 | over a scorched crop |
| campfire | `objects/campfires/campfire_05_16x32_3frames.png` (lit, 3 frames); 01-04 still variants | 3 | (0,-16) |
| door | `buildings/doors/door_01/opening/*_16x16_4frames.png` | 4 | on the door cell |
| coins | `objects/coins/coin_01/coin_01_16x16_8frames.png` | 8 (spin) | over the kart |
| firefly | `animals/fireflies/firefly_01/idle/*_16x16_4frames.png` | 4 (pulse) | screen point |

Crops: frame 0 is the seed, the last frames are the harvested / withered plant. The game's `stages` (tools/content/ranch.py)
are the frames from seed to ripe: 7-frame crops `0..5` (eggplant and bamboo ripen at 4), tomato `0,2,4,6,8,10,13,16` of 23,
pepper `0,2,4,5,6,7,8,9` of 11, wheat `0..5` of 8, corn the 29-frame growth_smooth `0,3,6,10,14,18,19`. Corn's `frozen`,
`on_fire` and `shake` strips have 8 frames matching growth_basic; `tempest` is a 12-frame loop of the ripe plant.
Crop sprites are bottom-aligned on their cell (feet at y 15), 18-px-wide crops centred.

## 5. How the game uses it

- `tools/art/install_ranch.py` copies the `assets/` tree as is into `game/assets/ext/ranch/pack/`, the Godot 3x3 sheets into
  `ext/ranch/autotiles/` (+ the wet bed sheets), builds `ext/ranch/icons.png` (item icons) and copies the music into
  `ext/ranch/music/`.
- `tools/maps48/maps/ranch.py` lays out the eight farms (a cell plan per ranch) and `ranchkit.py` composes their ground at
  16 px (fills, terrain blocks, blob autotiles, cliffs, rails, pipes, raked bed strips, the hands' tilled beds, water
  frame 0), saves it x3 as `ext/maps48/<MAP>_ground.png`, writes the upright stamps (houses, barns, trees, bushes,
  fences, wells, signposts, barrels, lamps, ice) on x3 copies of the sheets in `ext/ranch/x3/`, and puts the runtime
  extras in `<MAP>.json` under `"ranch"` (water cells, doors, campfires, gates, fireflies, the hands' crops, rails, the
  bed sheets). It also writes `content_src/maps/ranch.map` from the same plan (collision = art).
- `game/src/meta/ranch.gd` draws what changes: hoed / watered beds and animated water as flat quads on the (HD-2D) ground,
  crops, gates, doors, campfires, effects, animals, farmers, the nest and the kart as y-sorted uprights, fireflies,
  sun rays and wind over the view, and plays the pack's field / village themes and night / rain ambients.
