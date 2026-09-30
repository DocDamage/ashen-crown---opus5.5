# Authoring the expansion places (maps, NPCs, scenes, questlines)

This is the brief for building the ~90 new places of the expansion (surface N01–N43, post-fault P01/P02/P05/P09, the Deep
U01–U40). The design bible is `docs/expansion/WORLD_V2.md`; read its place tables (sections 2–4), questlines (section 8)
and tone notes before writing. Every map is authored by hand: a real layout that fits the place's story, not a template.

## 1. Where things go (one author group = its own files)

- Maps: `content_src/maps/x_<group>.map` (one file per author group, many `=== MAP_ID` sections).
- Scenes (dialogue, events, boss fights, quest logic): `content_src/scenes/x_<group>.scn`.
- Shops, speakers, location names, quest records: `tools/content/places/<group>.py` defining any of
  `SHOPS`, `SPEAKERS`, `LOCATIONS`, `QUESTS` (see `tools/content/places/__init__.py`).
- Never edit other files. Never edit `world2.map` (the world is generated) or existing towns/dungeons.
- Validate with `python3 tools/compile_content.py` (must print `compile_content: OK`; `PENDING` lines about other
  groups' places not being built yet are fine). Also run `python3 tools/check_reach.py` (0 problems) and
  `python3 tools/check_entities_reach.py` (only the 14 known T02_SHOP/other pre-existing hits are allowed; nothing
  in your maps).

## 2. Map format (read examples first)

Read these real maps before writing: `content_src/maps/t04.map` (a town quay, lane, interiors),
`content_src/maps/d05_archive.map` (a 6-room dungeon with switches, blocks, boss), `content_src/maps/optional.map`
(post-state optional rooms), `content_src/maps/t01_brackenford.map`. The parser is `tools/compile_content.py`
(`parse_maps` / entity types around lines 330–420); the legend characters are `LEGEND_BASE` (line ~226) and the solid
kinds are `SOLID`. A section:

```
=== N01_R01
name: Hollins Mill
tileset: town_r01
music: M012
zone: N01
region: R01
location: L_N01
encounters: none          # or a group id, see 5.
save: true                # world-save allowed on this map (towns and landmarks)
grid:
<rows of legend characters, all the same width>
entities:
spawn world 20 28 up
spawn default 20 28 up
exit 18..22 29 WORLD l_n01
...
```

- **IDs.** The entry map of place `Nxx` is `Nxx_R01` (the world location's destination; it must contain spawn `world`
  and spawn `default`). Further outdoor areas `Nxx_R02`…, dungeon rooms `Nxx_R02..R05`, interiors `Nxx_INN`,
  `Nxx_SHOP`, `Nxx_HOUSE1`, `Nxx_HALL` and so on. P-places: `Pxx_R01`. Deep places: `Uxx_R01`.
- **Back to the world.** Surface places: `exit <x1..x2> <y> WORLD l_<id lowercase>` (for example `WORLD l_n01`).
  The game swaps in WORLD_POST automatically after the fault, so always write `WORLD`. Deep places use
  `DEEP l_u07` (swapped to DEEP_POST after the fault). The spawn names `l_n01`, `l_u07`… already exist on the world maps.
- **Room links.** `exit x1..x2 y DEST spawnname` (edge exits) and `door x y DEST spawnname sfx=FX008` (building doors).
  Every destination spawn must exist in the destination map.
- **Size.** Outdoor towns 36–48 wide x 26–34 tall; villages 30–40 x 22–30; dungeon rooms 20–40 x 16–30; interiors
  12–20 x 9–14. Surround playable space with walls/cliffs/trees/water; exits on the edges.
- **Legend.** Use `LEGEND_BASE` characters (`#` wall, `.` floor, `:` path, `~` water, `w` shallow, `=` bridge, `T` tree,
  `R` roof, `W` house wall, `D` door, `Q` window, `c` crate, `r` barrel, `l` lamp, `n` counter, `t` table, `B` bed,
  `k` shelf, `u` pillar, `y` statue, `*` crystal, `f` fence, `h` hedge, `g` garden, `1` flower, `O` well, `S` sign,
  `a` awning, `d` dock, `6` boat, `x` rubble, `^` cliff, `s` stairs, `@` altar, `!` brazier, `?` book, `9` pool,
  `0` hole, `%` vine, `` ` `` moss, `'` puddle, `;` roots, `z` sand, `q` snow, `i` ice, `e` ember, `]` tent,
  `[` shelter, `8` mural, `2` cart, `3` laundry, `4` chimney, `5` anvil, `(` arch …). A map may add its own
  `legend: x=kind` line for extra kinds (kinds from `SOLID`/`ENCOUNTER_TERRAIN` or the existing ones).
  Buildings in outdoor maps are drawn the town way: roof rows `R` above a wall row `W`/`Q` with a `D` door, as in t04.
- **Tilesets** (the art skin; pick by place): `town_r01` farmland village, `town_r02` ash/industrial town, `town_r03`
  harbour/coast town, `town_r04` cliff/wind town, `town_r05` salt/desert town, `capital`, `harbor`, `interior` (wood
  rooms), `interior_stone` (stone halls, chapels), `grove` forest, `grove_flood` flooded forest/swamp, `quarry` mine/
  cave, `furnace` lava/industrial, `archive` drowned ruins, `underways` canals/sewers, `sky` cliffs/sky bridges,
  `whitebone` bone/crypt, `vault` builder vault/crystal, `conduit` machine halls, `crown` palace/builder, `reef` sea
  caves, `winter` snow/ice, `ship`. New names you may use (skins are being added): `vermilion` (red-maple fox-court
  town, torii gates), `fen` (plague marsh village on stilts), `emberdeep` (dragon-realm caverns, lava and old scales),
  `lattice` (half-lit builder city), `hollow` (necropolis of the honoured dead).
- **Music** ids are in `data/music.json` (`M0xx`; towns/dungeons/tension/boss). Reuse them sensibly.

### Entities (one per line, `key=value` options at the end, `if=` conditions)

`spawn name x y dir` · `exit x1..x2 y1..y2 DEST spawn` · `door x y DEST spawn sfx=FX008` ·
`npc id x y dir sprite=<key> talk=<SCENE> [name="Display"] [wander=1] [if=cond]` ·
`chest id x y ITEM [count] [gold=N] [hidden=1]` · `sign x y "text"` · `read x y "text" scene=SCENE` ·
`save x y` · `heal x y` · `shop x y SHOP_ID` (the cell behind a counter `n`) · `inn x y scene=SCENE` (the scene
says a line then `inn <price>`, e.g. `inn 40`; see `T01P_INN` in ch14.scn) ·
`switch id x y scene=SCENE [flag=f] [sprite=lever] [toggle=1]` · `block x1..x2 y1..y2 tile=rubble if=cond msg="..."`
(conditional wall) · `trigger x1..x2 y1..y2 scene=SCENE [touch=1|0]` · `zone x1..x2 y1..y2 enc=GROUP` ·
`prop x y spritename`.
Conditions (`if=`) are comma lists: `ch:CH07` (chapter done), `!ch:CH07`, `flag:name`, `!flag:x`, `event:SCENE`,
`recruited:C09`, `party:C09`, `q:QID:ACTIVE`, `qs:QID:stage`, `phase:post`, `item:I001` … (see `Game.eval_cond` in
`game/src/autoload/game.gd`).
- **NPC sprites:** `worker elder survivor guard soldier child keeper monk pilot farmer baker sailor scholar patient
  noble clerk apprentice volunteer` (townsfolk art), hero ids `C01`–`C17` for heroes, or the named story NPCs
  `mara inspector pell jori edda sen ansel rook`. Give every NPC a unique id and a `name="..."` when they matter.
- **Chest items:** real ids only (`game/content/content.json` → `items`; consumables `I0xx`, weapons `W0xx`, armour
  `A0xx`, accessories `S0xx`). Match the reward to the place's level band; one or two better finds per dungeon.

## 3. Scenes (`.scn`)

Read `content_src/scenes/t04` scenes inside `ch05.scn`/`ch06.scn`, `quests.scn` and `overhaul.scn` for the house
style, and `game/src/story/director.gd` for every command (`_exec`). Basics:

```
@scene N01_MILLER
say elder | The wheel turns whether there's grain or not. That's the thing about wheels.
choice | Ask about the pond -> pond | Leave -> bye
label pond
say elder | Fish bite at dusk. Take the spare rod.
give I0xx 1
label bye
@end

@scene N04_BOSS once
say narr | The water in the nave stands up and becomes a knight.
battle BX01 noflee
set n04_cleared
give S0xx 1
say narr | The bells stop.
@end
```

- `say <speaker> | text` — speakers are keys of `SPEAKERS` (`tools/content/formations.py`): heroes are keyed by
  their OLD ids: `dain`=Raven (C01), `tessa`=Morwen (C02), `corren`=Vespera (C03), `ivo`=Golem (C04),
  `nera`=Elowen (C05), `oriel`=Aurex (C06), `sable`=Oni (C07), `pip`=Sak (C08); new heroes `kitsune archangel inferna
  corvus lich maldrath velkhar kael rider`; `ilyr` (the dragon inside Raven); `narr` (narration); generic `elder
  worker guard child sailor keeper baker clerk survivor apprentice patient officer volunteer pilot`. Add your own named
  recurring NPCs to `SPEAKERS` in your places module (`"hollin": ["Hollin", "elder"]` = display name, portrait key;
  reuse a generic portrait key).
- `once` scenes run a single time (quest beats, bosses). Flags: `set flag` / `unset flag`; variables `setvar`/`addvar`.
- `if <cond> label` jumps; `goto label`; `end`; `choice | text -> label | text -> label`.
- `battle <FORMATION> [noflee]` — bosses are formations named after the boss id (see 5).
- Rewards: `give ITEM n`, `gold n`, `xp n`, `vestige Vxx` (only where the design says), `quest QID STATE [stage]`
  (states NOT_STARTED/ACTIVE/RESOLUTION_READY/COMPLETED), `journal | text`, `rumor | text`, `discover L_xxx`.
- Staging: `move <npc> dir n`, `face`, `emote`, `wait`, `fade`, `sfx FXnnn`, `music Mnnn`, `shake`, `flash`, `tint`.

## 4. Tone and writing

Read `docs/overhaul/STORY_GUIDE.md`, `docs/overhaul/LAYOUT_STANDARD.md` (layout and density) and
`docs/overhaul/TOWN_GUIDE.md` (region moods) first. Grim but not gratuitous. People are tired, poor, grieving, stubborn and funny in a dry way; the Crown's rule has cost
everyone something. Short lines (FF6-length, one or two sentences per `say`). Every NPC says something specific to
this place — its trade, its fear, a rumour about a nearby place, a hint about a secret or a quest. No filler
("Nice weather!"). Each village or town gets **15–25 NPCs** across its maps; landmarks and secrets 3–8; dungeons a few
(survivors, ghosts, notes/`read` entries). Recurring NPCs (a travelling merchant, a courier, a bounty-board keeper, a
wandering scholar…) are welcome: reuse their speaker key and ids with different suffixes across places.
Places have a pre-fault and a post-fault life: add a few `if=phase:post` / `if=!phase:post` NPCs and lines so the
World of Ruin feels changed (places marked destroyed in WORLD_V2 section 5 only exist pre-fault).

## 5. Content per place type

- **V village:** 1 outdoor map + 2–3 interiors (inn with `inn`, a crafter/shop with `shop`, one home or hall).
  A save point outside or in the inn. Its own shop in `SHOPS` (`{"SHOP_N01": {"name": "...", "kinds":
  ["items", "weapons", "armor", "accessories"], "town": "N01"}}`; kinds may be a subset). A crafter NPC (the crafting
  system will hook the NPC with id `crafter_<place lower>`; give them lines about materials). Inns use an `inn` entity
  and an inn scene (pattern: `T01P_INN` in content_src/scenes/ch14.scn; a `shop` command in a scene also opens a shop).
- **T town:** 2–3 outdoor districts + 4–6 interiors, 20–25 NPCs, shop(s), inn, crafter, a save point.
- **D dungeon:** 4–6 rooms: entry, 2–4 puzzle/combat rooms (switches that open `block`s, keys via flags, a hidden
  chest, a shortcut back), a save point before the boss, the boss room with a `trigger` or `npc`/`read` that runs a
  `once` boss scene with `battle BXnn noflee`, and a reward. Rooms use `encounters: <group>` and `rate: 0.6..1.0`.
- **L landmark:** 1 map (sometimes 2), 3–8 NPCs or readable objects, a small reward or quest beat, maybe a save.
- **S secret:** 1 map, hidden reward, lore, often a condition (night, item, flag). Sparse NPCs.
- **Encounter groups:** dungeons `W_<PID>` pre-fault (for example `W_N04`) and `WP_<PID>` for post-fault rooms if the
  dungeon has post versions; region fields `W_R01`…`W_R09`, `W_SKY`, `W_SEA`; the Deep `W_U1`, `W_U2`, `W_U3` (pre)
  and `WP_U1`… (post). Villages/landmarks `none`.
- **Bosses** (formation = boss id, levels set): BX01 N04 Sunken Chapel · BX02 N07 Slagfalls · BX03 N13 Brine Stair ·
  BX04 N18 Eyrie Hollow · BX05 N21 Sorrowmere · BX06 N25 Leech Cathedral · BX07 N29 Thousand Gates · BX08 N34 Glacier
  Spire · BX09 N35 Coldharbour Citadel · BX10 N39 Seraphel · BX11 N42 Weeping Dam · BX12 P01 Spine of Ilyrath ·
  BX13 P02 Tessellate · BX14 U04 Geode Wood · BX15 U05 Ossuary of Wings · BX16 U08 Crown Dig · BX17 U12 Deepforge ·
  BX18 U18 Assembly Floors · BX19 U20 Datum Archive · BX20 U23 Vault Omega · BX21 U30 Bone Bridges · BX22 U31
  Sepulchre Court (Mother Sepulchre) · BX23 U32 Abyss Gate · BX24 U33 First Crown's Tomb · BX25 U35 Lich Stair ·
  BX26 U36 Crypt-Gate. Superbosses (SB01–SB12) are placed by the lead, not by you; you may leave a sealed door or an
  ominous `read` where the design puts one (Cindermaw at N10, CURATOR at U24, Mother Sepulchre's true form in U31,
  the Choir in U38, the Hollow Heart U39).
  Boss names, lore and mechanics are in `tools/content/bosses2.py` (read it: write intros that match the tells).
- **Questlines** (WORLD_V2 section 8) that live in your places: write them fully as scenes + `QUESTS` records
  (`{"id": "QC12", "name": "The Cure That Was Sold", "start": "N22", "location": "N25", "character": "C12", "hook":
  "...", "objectives": "...", "decision": "...", "result": "...", "reward": "...", "boss": "BX06"}`). Quest ids:
  hero questlines `QC09`…`QC17`, underground `QUP1`…`QUP4`, builder `QBM1`…`QBM3`, World of Ruin `QW1`…`QW7`.
  A questline has 3–6 beats across maps: a hook NPC (`quest QID ACTIVE`), steps with stages (`quest QID ACTIVE stage`
  and `qs:QID:stage` conditions), a decision (`choice`), a climax (often the place's boss) and a resolution with a
  reward (`quest QID COMPLETED`). Hero questlines need the hero in the party: gate the hook with `if=recruited:C12`
  and use their speaker. Read the hero's bio in `data/characters.json` (and `docs/overhaul/` if present) first.

## 6. Checklist per map before you finish

Spawn `world`+`default` on the entry map · every exit/door leads to an existing map+spawn · the player can walk from
each spawn to every exit and NPC (check_reach/check_entities_reach) · rows equal width · no NPC on a solid tile ·
scenes referenced by `talk=`/`scene=` exist · compile OK.
