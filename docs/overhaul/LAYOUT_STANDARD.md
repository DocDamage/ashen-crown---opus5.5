Ashen Crown — Map Layout and Set-Dressing Standard
 · 
Every map from the pilot onward is scored against this standard; a map ships only when it passes every hard rule in the checklist and meets the density target for its class.
How a map is judged
A map passes when it clears every hard rule in the checklist at the end and reaches the detail-coverage floor for its class. Hard rules catch the four errors you named: wrong prop, too few props, wrong ground, wrong scale.
Detail coverage is the one number. Render the map, cut it into 48px cells, find the 16 most repeated cells (plain floor, grass, water), and count the share of cells that are not one of them. Plain ground scores low; walls, roofs, edges, props and varied ground score high.
I measured the same number on all 71 FF6 location rips in the Video Game Atlas (16px cells, both worlds). FF6 towns sit at a median of 78% (range 67–90%), and no FF6 town falls below 66%. The targets in section 3 come from those figures.
The number is a floor, not the goal. The rips include NPC sprites, and a map can hit 78% with the wrong props. The checklist decides; the number stops thin maps from reaching review at all.
The build will compute detail coverage and the countable rules (bare wall runs, empty rectangles, door dressing, edge straightness) from each Tiled map and print a pass/fail sheet per map.
Scale and pixel density
Everything is sized in H, the height of a standing hero. FF6 draws people about 1.5 tiles tall and its houses 4 to 5½ H from ground to roof peak; that ratio, not the tile count, is what makes FF6 towns feel full-sized.
Measure

FF6

Ashen Crown rule


Hero height (H)

about 24px on 16px tiles

62px on 48px tiles (decided: the native height of 15 heroes; Kitsune and Oni shrunk to match, Rune Golem enlarged to 75px)


Screen

16 × 14 tiles

20 × 15 tiles at 960 × 720


Cottage, shed, stall

about 4 H

at least 3 H (192px): CuteSCKR whole houses fit here


House, shop, inn

4–5½ H

at least 4 H (about 5 tiles) including roof


Hall, church, manor, castle keep

6 H and up

at least 6 H; built from pieces if no whole sprite is that large


Door opening

about 1.3 H

1.2–1.5 H


Barrel, crate, sack

about 0.6 H

0.5–0.7 H


Fence, low wall

about 0.6 H

0.5–0.8 H


Street tree

2–3 H

2–3.5 H


Scale finding. The CuteSCKR whole houses are 4 × 4 tiles, about 3.1 H beside our heroes. That is the wrong-scale look you saw. They stay as cottages and outbuildings; main buildings are composed larger from the wall, window and roof pieces in the same packs.
One pixel density per map. Every field sprite is drawn at 1 art pixel = 1 screen pixel (CuteSCKR, SakPix, the heroes all measure this way). Art made for 16px tiles and blown up 3× (the Seabed and Undead object packs, Time Fantasy) has pixels three times as coarse and clashes beside native art. It may be used only for a whole map set of its own (the Drowned Undercity seabed) or for distant backdrops, never mixed into a native map.
No free scaling. Sprites are placed at 1× or an exact whole multiple; the engine never scales pixel art by a fraction. Any fractional resize is done once, at the source, in Aseprite with rotsprite and a clean-up pass (as done for Kitsune, Oni, the Rune Golem, the GandalfHardcore NPCs and the giant bosses, halved to about 5 H tall), and the result is used at 1×. Backdrops are the one 2× layer: the pixelated battle arenas and the parallax skies are drawn 360px tall and shown doubled, and the weather and starfield shaders snap to the same 2× grid.
Density targets by map class
Towns must reach 70% detail coverage, with 78% (the FF6 town median) as the aim. The floors sit at or just above the lowest FF6 map in each class, so a map below its floor is thinner than anything FF6 shipped.
Map class

FF6 maps measured

FF6 median

FF6 range

Our floor

Largest empty walkable area

Dressed objects per 20 × 15 screen


Town or city

18 (both worlds)

78%

67–90%

70%

5 × 4 tiles, unless a plaza with a centrepiece

25–45


Dungeon, cave, forest, tower

40

76%

33–94% (quarter below 67%)

65%

6 × 5 tiles, unless a set-piece room

12–25


Castle or palace

6

68%

47–77%

60%

a courtyard or throne axis only

20–40


Lone house or outpost in the field

6

53%

40–58%

50%

the approach and yard only

8–15


Interior room

inside the composites above

—

—

wall rules in section 6

40% of the floor

every wall run dressed


FF6 references by class: towns — Narshe, South Figaro, Jidoor, Kohlingen, Mobliz, Thamasa, Albrook, Tzen, Maranda, Nikeah, Zozo, Vector; dungeons — Mt. Kolts, Phantom Forest, Magitek Factory, Cave to the Sealed Gate, Phoenix Cave, Kefka's Tower; castles — Figaro, Doma, the Imperial Palace, the Opera House; lone houses — Sabin's cabin, Duncan's house, the Chocobo stable.
The object counts are my starting calibration from the rips and will be checked on the pilot maps before rollout. They count placed objects (props, signs, plants, lamps), not ground or wall tiles.
Town shapes
Every FF6 town is shaped by one terrain idea, and the streets are what the buildings and terrain leave over. None is a grid of houses on an open lawn.
Shape

FF6 example

What makes it work

Fits in Ashen Crown


Valley spine

Narshe

Cliffs take half the map; one main street climbs the valley; houses on stilts, scaffold walkways and ladders up the rock; mine machinery on the slopes

Skyspine, quarry and mining towns


Walled block

South Figaro

Buildings share walls and form blocks; 2–3 tile streets; a canal and a lower level cut through; forest bands on both sides, docks at the bottom

Crown March market towns, the capital


Terraced axis

Jidoor

Entrance at the bottom, terraces joined by stairs, the mansion at the top framed by trees; symmetric plots with hedges and flower beds

Wealthy towns, seats of nobles


Vertical city

Zozo

Tall buildings with outside staircases; the town is climbed like a dungeon; rain and dark palette

Cinder Reach industrial towns, fallen cities


Clearing village

Mobliz, Thamasa

Loose houses with yards, fields and paths of worn dirt; a well or tree at the centre; forest and shore frame it

Hamlets such as Millrace Hamlet, Rootward


Port

Albrook, Nikeah

The town runs down to piers; ships and crates on the docks; a warehouse row along the water

Glass Coast, Ember Sea


Imperial capital

Vector

Stacked industrial blocks, pipes, a palace as the end goal of the map

Late-game seat of power


Rules taken from them:
One shape per town, picked from the table or argued for in the map's notes. The shape must be readable from the first screen.
A landmark at the end of the main axis (Jidoor's mansion, Narshe's mine entrance, Mobliz's well). The player sees it or its approach within two screens of the entrance.
At least two ground levels in every town, joined by stairs or ramps.
Terrain fills the rectangle. Cliffs, forest, water or walls run to every map edge; there is no leftover lawn between the town and the border.
Streets are 2–3 tiles wide, a main street up to 4, alleys 1. A street wider than 4 tiles is a plaza and needs a centrepiece.
Services read from outside: every inn, shop, smith and church has a hanging sign or display (FF6-style icons for bed, pot, sword, shield, ring) beside its door.
Cities pack, villages spread. City buildings touch or share walls; village buildings sit on plots with fences, yards, gardens or fields.
Buildings
A building is one whole sprite (or one composed block) that stands on the ground, not a stack of loose wall tiles. FF6 buildings are mostly roof: the roof is about half the height and overhangs the walls.
Whole sprites first. Use a whole-building sprite from CuteSCKR when one fits the region and the size class in section 2. Otherwise compose one from a single pack's wall, window, door and roof pieces, and save the result as a reusable building prefab so it is never rebuilt tile by tile on a map.
One pack per building. Walls, roof and trim on one building come from the same pack and palette.
Roof share 40–60% of the building's height, with eaves over the wall line. The player walks behind roofs and in front of walls.
Doors on the south face (the side the camera sees), with a step, stoop or threshold tile. Side and back doors only where a path leads to them.
Every building has a foundation line: a plinth, step or shadow where it meets the ground. No building floats on grass.
Chimneys smoke, windows glow at night, signs hang beside service doors.
Enterable by default. A building with a visible door has an interior. A building you cannot enter shows it: boarded door, rubble, a guard, or no door at all.
Variety along a street: no two identical buildings side by side; at most three copies of one sprite on a map, and copies differ in colour, signs or dressing.
Outdoor dressing at every door: within one tile of each door there is at least one object (sign, barrel, crate, lamp, plant pot, bench).
Interiors
FF6 interiors are small, cut-cornered rooms whose back walls are lined edge to edge with furniture and hangings. In the South Figaro rooms no stretch of back wall runs more than about three tiles without something on or against it.
Room outline. Rooms have bevelled (cut) corners and a back wall 2–3 tiles tall. The exit is a notch in the bottom edge, usually centred, with a mat or step. The black around the room is kept.
Size. A single room is 8–14 tiles wide and 6–10 tall. A room that fills the whole 20 × 15 screen is split with a counter, a partition or a second room.
Match the outside. The room's width follows the building's front; a two-storey house has stairs to an upper room.
Back wall rule. No bare run of back wall longer than 3 tiles: shelves, cupboards, windows, lamps, paintings, clocks, mounted weapons, banners.
Side walls get tall furniture (bookcases, wardrobes, barrels, beds against the wall) on at least half their length.
Furniture in groups: table with two to four chairs; bed with nightstand and rug; stove with pots, firewood and a basket; counter with the keeper behind it and goods on shelves behind the keeper. A single chair alone in a room is a defect.
Rugs anchor groups. Every seating or sleeping group sits on a rug or a floor change.
Floor open to 40% at most, but a clear walking line of at least 1 tile from the door to every NPC, chest and exit.
Light sources (hearth, lamp, candle, window) in every room, with a glow at night.
Room type decides the props:
Room

Must have


Inn

counter and keeper, at least 2 beds visible, a hearth or bar, stairs if two storeys


Item or weapon or armour shop

counter, keeper, stocked shelves or racks that show the goods type, a sign icon outside


Smithy

forge with fire, anvil, water trough, racks of tools and blades


Home

bed, table group, hearth or stove, storage, one personal item that tells who lives there


Church or shrine

altar or statue on the axis, pews or mats in rows, candles


Castle hall

carpet on the throne axis, pillars in pairs, guards, banners


Props and ground
Props go where people would put them, in the region's own style, on the right ground. Each rule below maps to one of the four errors you flagged.
Wrong prop (off-theme)
Each region has a prop list (its packs, from the interiors-per-region decision). A map uses only its region's list plus the shared neutral set (barrels, crates, sacks, rocks, grass tufts, flowers).
Builder-era, modern or sci-fi props appear only in builder ruins and the industrial areas you allowed.
Props say what the place does: Narshe has winches, rails, pipes and steam; a port has nets, crates, ropes, bollards; a farm has troughs, hay, tools.
Too few props
The per-screen counts and empty-area limits in section 3.
Every door (section 5), every back wall (section 6), every street corner and every stair head gets dressing.
Props come in clusters of 2–4 mixed items (barrel + crate + sack), not single items spaced evenly.
Wrong placement
Props stand against something: a wall, a fence, a tree, a building corner, a stall. Free-standing props in the open are limited to centrepieces (well, fountain, statue, tree, market stall, lamp post).
Every prop meets the ground: its base sits on a walkable or floor tile of the same level, with its shadow. Nothing overlaps a roof, hangs over a cliff edge or sits half on water.
Props never block the only route; a 1-tile walking line always stays open.
Wrong scale
Sizes follow the H table in section 2. A prop outside its size band is replaced, not scaled.
Wrong ground
Ground follows use: paving or cobbles in a town core and in front of public buildings; packed dirt on paths and around farms; grass in yards, verges and edges; wooden boards on docks and scaffolds; snow, sand, ash or mud by region.
Worn paths connect every door to the street: a dirt or stone path, never a door opening onto untouched grass.
Every change of ground has a transition (edge tiles, scattered stones, grass tufts). No hard straight seam between two ground types longer than 3 tiles.
Ground varies: no single ground tile repeated over more than a 4 × 4 block without a variant, crack, flower or stone.
Elevation and edges
FF6 maps are never flat: even Mobliz has banks and shore, and Narshe is almost all cliff. Height gives the map its shape and its routes.
Cliff faces are at least 2 tiles tall with a lit top edge and a shadowed base. A single-tile step is a ledge or bank, not a cliff.
Natural edges are ragged. A cliff, shore or forest edge never runs straight for more than 6 tiles; it steps in and out by 1–2 tiles.
Stairs, ramps, ladders and bridges join levels, and each one is dressed at its top and bottom (rail, post, lamp, rocks).
Map borders are closed by terrain: a band of 2–4 tiles of forest canopy, cliff, water, wall or roof at every edge the player cannot walk off. Exits are gaps in that band, marked by a path or gate.
Water has banks: shore tiles, reeds, rocks or piers along every edge, and animated surface.
Trees overlap. Forest bands use layered canopy with trunks visible only on the front row; no single-file lines of identical trees.
Walk-behind depth. Anything taller than 1 H (trees, buildings, cliffs, pillars) hides the player when they walk behind it.
Dungeon flow
A dungeon floor follows FF6's room-and-corridor pattern: the player sees a reward before they can reach it, a branch opens the way forward, and a shortcut returns them to the entrance before the boss.
Rooms and corridors, not open caves. A floor is 3–6 rooms of one or two screens joined by corridors 1–3 tiles wide.
At least two branches per floor, and every dead end pays off: a chest, a save point, a lore scene, a Vestige, or a view of what comes next.
Visible but unreachable: at least one reward or route per dungeon is seen before it can be reached (across a chasm, behind bars, on a ledge) and is reached later from another direction.
One mechanism per dungeon (switches, mine carts, rafts, moving platforms, a timer, a light puzzle), introduced safely, then used under pressure.
Save point and recovery spring before every boss, in a room with no random encounters.
The motif changes every 2–3 rooms (Magitek Factory goes conveyors, then vats, then a shaft), so no two adjacent rooms look alike.
Multi-party dungeons (the FF6 Phoenix Cave and Kefka's Tower pattern) give each party a lane; a switch in one lane opens a door in another, and the lanes are visibly parallel.
Relaid story dungeons keep every scene, switch and boss reachable in the original order (your decision 27); the build's reachability check must pass.
Colour, light and ambience
Each location has one colour mood that you could name from a thumbnail: Narshe is blue-grey snow and brown timber, Jidoor warm stone and blue roofs, Zozo near-black with rain. A map that could be swapped with its neighbour's palette fails.
Region

Mood (starting palette)

Music (your casting)

Sound bed


Crown March

warm stone, slate-blue roofs, green verges

Echoes Below; Crimson Nocturne for the Crown

market chatter, birds, bells


Cinder Reach

soot brown, brass, ember orange, grey steam

Echoes Below; Neon Reverie and Midnight Velocity in builder ruins

furnace hum, hammering, steam


Glass Coast

sea teal, bleached wood, sand

Dark Pirate Fantasy

surf, gulls, rigging creak


Skyspine

cold blue, white, dark pine, timber

Frozen Echoes

wind, creaking ice


Pale Basin

ochre, sandstone, pale sky

Sands of Eternity

dry wind, cicadas


Ember Sea

deep red, black rock, lava glow

Echoes Below; Astral Horizons as needed

lava bubbling, low rumble


Light direction is fixed (top-left) for every sprite shadow on a map.
Night, rain, snow and fog are map-wide overlays with lit windows, lamp glows and torch flicker, never darkened tiles.
Animated ambience on every exterior map: water, fire, smoke and flags move; at least one animated element per screen in towns.
Wandering NPCs: towns have 8–15 NPCs, at least a third of them walking set routes; each service has its keeper.
Sound beds: every map names a looping bed and up to three spot sounds (fountain, forge, surf) tied to objects. The library has no ambience or sound-effect audio yet; see the asset inventory.
Ruined variants and the world maps
FF6's World of Ruin keeps each town's footprint and changes everything that sits on it. Comparing the two Mobliz maps: the grass turns olive, the sea takes the lower third, most houses are gone or broken, the paths fade, and a new underground shelter is added.
Ruined variant of a map
Same footprint, same entrances, so the player recognises the place at once.
Palette shift per region (burned: ash grey and char; flooded: silt and green water; frozen: white and blue; blighted: olive and rust).
30–60% of buildings destroyed or damaged (roof holes, collapsed walls, rubble, scorch), with at least one landmark kept standing.
Terrain intrudes: water, ice, ash or lava cuts off old streets, so routes through the town change.
Something new appears: a shelter, a camp, a crack into a cave, a cult shrine. Every ruined town has at least one space the first version lacked.
Fewer NPCs, changed NPCs, different music, and ruin props (Cursed and Undead land objects, battlefield and apocalypse packs) replacing the town set.
Detail coverage stays at or above the class floor; rubble counts, empty ash does not.
World maps
Balance world: continents with mountain spines that gate progress, forests in pockets, deserts and snowfields as their own regions, water routes that later need the Wayfarer. Location positions stay where they are now.
Ruined world: the continent broken into islands and a long thin land bridge, regions flooded, burned or frozen, forests mostly gone, lost towns replaced by new areas.
Every location marker is readable at a glance (town, castle, cave, tower, ruin), sized to its importance.
Coasts, rivers and mountain edges are ragged, and no terrain block is a plain rectangle.
Landmarks between locations (a lone tower, a wreck, a crater) so no stretch of more than a screen is empty.
Review checklist
A map passes when every row below passes. Rows marked build are checked automatically from the Tiled map; rows marked eye are checked on the review screenshots.
#

Check

Checked by

Section


1

Detail coverage at or above the class floor

build

3


2

No empty walkable area larger than the class limit

build

3


3

Dressed-object count within the class range per screen

build

3


4

Heroes, NPCs, buildings and props within their H size bands; no non-integer scaling

build

2


5

One pixel density on the map

build

2


6

Town has one named shape, a landmark on the main axis and two or more ground levels

eye

4


7

Terrain closes every border; exits are marked gaps

build + eye

4, 8


8

Buildings from one pack each, roof share 40–60%, foundation line, south doors

eye

5


9

Every visible door is enterable or visibly closed; every door has dressing within 1 tile

build

5


10

No sprite copied more than three times; no identical neighbours

build

5


11

Interior back walls have no bare run over 3 tiles; furniture in groups on rugs

build + eye

6


12

Every prop from the region list or the neutral set; no builder-era props outside allowed areas

build

7


13

Every prop stands against something or is a centrepiece, sits on its own level, blocks no route

build + eye

7


14

Ground matches use; every door has a path; no straight ground seam over 3 tiles; no tile repeated over 4 × 4

build

7


15

Cliffs 2+ tiles, natural edges never straight over 6 tiles, stairs dressed

build + eye

8


16

Dungeon: two or more branches per floor, every dead end pays off, one seen-but-unreachable reward, save and spring before the boss

build + eye

9


17

Colour mood matches the region; animated ambience present; NPC count and sound bed set

eye

10


18

Ruined variant: same footprint, palette shift, damage share, at least one new space

eye

11


Review screenshots for each map: the full map at 1×, three gameplay screens at 960 × 720 (entrance, landmark, densest area), one night or weather shot, and each interior.
Sources
The Video Game Atlas — Super NES maps, Final Fantasy VI: 71 location rips (44 World of Balance, 27 World of Ruin) plus both world maps, measured and viewed on 2026-09-29. Maps by the Atlas contributors (FlyingArmor and others).
Detail-coverage figures: my measurement of those rips (16px cells, blank background excluded). Per-map numbers are saved with the build tools as ff6_metrics.csv.
Ashen Crown overhaul brief (your 64 decisions) and the asset inventory for pack names and sizes.

