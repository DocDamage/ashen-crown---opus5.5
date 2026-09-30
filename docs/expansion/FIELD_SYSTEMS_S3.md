# Field and world systems (expansion pass s3)

How the field systems added in pass s3 work, and how to author content for them. Code: `game/src/field/field_sys.gd`
(rules), `field_cmds.gd` (scene commands), `wyrms.gd`, `weather_fx.gd`, `game/src/story/arena.gd`,
`game/src/ui/travel_menu.gd`; hooks in `field.gd`. Data: `tools/content/field_s3.py` (content `travel`, `arena`,
item `ZW01`), `tools/world2/wgen.py` (waystones, sky isles, the auger shaft, UNDERSEA), `content_src/maps/x_s3.map`,
`content_src/scenes/x_s3.scn`. Tests: `game/tests/unit/test_expansion_field.gd`. Screens: `--qa-gallery-set sys_s3`.

## 1. Time of day

- The world clock is `Game.S.clock` (minutes, 0-1440; new games start at 08:00) and `Game.S.day` (days passed). It
  runs only while the party can move, about 20 real minutes per day.
- Night is 20:00-05:00.
- Conditions, usable in any `if=` or scene `if`:
  - `night` / `!night`;
  - `day` (not night);
  - `hour:a-b`, from hour a up to hour b. It wraps past midnight, so `hour:22-4` is 22:00 to 04:00. Decimals work
    (`hour:6.5-9`).
- **NPC schedules.** Put `if=night` or `if=!night` on an `npc` line. The field refreshes NPCs when night falls or
  ends, when a menu or scene closes, and on every map load. Two lines with the same position and opposite conditions
  give a day NPC and a night NPC (use different ids).
- **Inns** offer three stays:
  - Rest: heals, and the hour does not change;
  - Sleep until morning: heals and wakes at 06:00;
  - Sleep until evening: heals and wakes at 18:00.
  Sleeping past midnight counts a day. From a scene, use `travel sleep morning|evening`.
- **Outdoor light.** World maps tint their ground plane by the hour. Outdoor town tilesets (`town_r0x`, `vermilion`,
  `fen`, `harbor`, `capital`, `sky`) get a dusk and night overlay.

## 2. Encounters

- **Map headers:**
  - `encounters_post: GROUP` replaces `encounters:` after the fault.
  - `rate_post: 0.8` replaces `rate:` after the fault.
  Without these headers, a map keeps its pre-fault group and rate.
- **Zones** honour their `if=` conditions. A zone whose condition is false is ignored, and the last matching zone
  wins. Example:

  ```
  zone 10..20 5..9 enc=W_NIGHT if=night
  ```

- **Night encounters.** At night, on the surface world maps (not the Deep, not the sea floor), about 30% of random
  fights come from `W_NIGHT` (pre-fault) or `WP_NIGHT` (post-fault).
  - Only night formations whose strongest enemy is at most 3 levels above the party's average are used. A weak party
    never meets the night rares.
  - QA route bots never get night mixing.

## 3. Waystones and fast travel

- **The entity:**

  ```
  waystone WS_ID x y name="Display Name" region=R01 [layer=deep] [if=cond]
  ```

  It needs a matching arrival spawn, `spawn ws_id x y dir` (the id in lower case). Stones are walkable billboards
  (a monolith with a rune).
- **Attuning.** Stepping onto a stone attunes it (`Game.S.waystones`).
- **The travel menu.** Press Confirm on a stone, or facing one, to open it.
  - It has two tabs, Surface and The Deep; Left and Right switch between them.
  - Attuned stones are grouped by region.
  - The stone you stand at is marked "here".
- **After the fault** the stones are dark until the Last Beacon's stone (`WS_P09`, at P09) is attuned. From then on
  every attuned stone answers again.
- **Placement.** wgen.py writes the stones on the world maps: N02, N41, T03, T04, T05, T06, N22, N27, N32, T07 (post),
  P09 (post), and U02 and U17 in the Deep. Each sits 3 to 7 cells from its place, south of the landmark, off roads.
  To add a stone, add a row to `WAYSTONES` in wgen.py and regenerate. For a stone inside a town map, write the two
  lines in that map.
- **The Wayfarer's Sigil** (`ZW01`, a consumable, sellable, 400 crowns) opens the same menu from the Items menu.
  - It works on world maps and in towns.
  - It does not work in dungeons (maps with encounters, zones, or a dungeon id prefix), in scenes, on the airship,
    or on the sea floor.
  - It is consumed only when the party travels.
  - Two are in a chest in the Hall of Wagers (N38_ARENA). No shop sells it yet.
- **Travel networks.** A network is content `travel` in `field_s3.py`. Each stop has a map, a spawn and an `if`. The
  scene command `travel menu <net>` shows every stop whose condition holds.

  | Network | What it is | Stops |
  |---|---|---|
  | `rail_u1` | Delver mine-rail | Vaultmouth U11, Karag Dun U02, Deepforge U12 |
  | `mag_u2` | Lattice mag-rail | Terminus U26, Railhead Nine U19, Meridian U17 (post), Prime Relay spur U24 (post) |
  | `lava_u1` | Magma skiffs | Magma Ferry U06, Cinderlake Isles U07 (pre only), Fungal Terraces U15 (post only) |
  | `lake_u2` | Glasswater barge | U21, U26 |
  | `lake_u3` | Black-lake boat | Styx Landing U28, Cenotaph U29 |

  The ferry and rail NPCs (U11_RAIL, U26_RAIL, U06_FERRY, U21_BARGE, U28_OARSMAN) keep their own lines and choices,
  and gain a first "board" option that opens the menu.

## 4. Vehicles

### Brackhorn variants

A variant is unlocked when the party has the mount (`vehicle mount true`) and the variant's flag is set.

| Variant | Flag | Rides | Crosses (solid on foot) |
|---|---|---|---|
| Bramble (base) | — | open ground: plains, grass, sand, salt, snow, ash, olive, roads, bridges, ice, forest | — |
| Ridgehorn | `brackhorn_ridgehorn` | + hills, rocky | — |
| Fenwader | `brackhorn_fenwader` | + swamp, shallow | water cells that touch walkable land (shore shallows, narrow rivers) |
| Deepstrider | `qup1_deepstrider` | the Deep's floors (cave, crystal, bone, ruin, road) | lava crust (the Deep only) |
| Gilded | `brackhorn_gilded` | open ground + hills, rocky, swamp; fastest (x1.8) | — |

- On terrain the current variant cannot ride, the party leads it on foot. They move at walking speed and random
  encounters happen as usual. There is no trap: they can always walk.
- In the Deep only the Deepstrider is ridden. Before this pass the base Brackhorn was ridden there too.
- **Switching.** On a world map, standing still, press Page L or Page R (Q / E) to cycle the owned variants. A toast
  names the variant.
- Each variant is drawn with its own tint of the Brackhorn sprite.

### Lanternwake upgrades (post-fault ship)

| Upgrade | Flag | Effect |
|---|---|---|
| Gale Vanes | `gale_vanes` | x1.5 flying speed |
| Grapnel Keel | `lanternwake_grapnel` | land anywhere there is standing room, not only on landing fields |
| Diving Hull | `lanternwake_diving` | over open ocean (`deep` cells of WORLD_POST), the Run key dives to UNDERSEA at the matching cell |
| Delver Auger | `lanternwake_auger` | post-fault: hovering within 2 cells of the Aurora Pit (L_N36), the Run key lowers the party to DEEP_POST spawn `auger` |

- **Diving Hull, surfacing.** On the sea floor the party is always in the submarine. The Run key (or Confirm, then
  "Surface") comes up aloft over the matching cell of WORLD_POST.
- **Delver Auger, return.** The ship stays over the pit. The Auger Winch NPC beside the arrival spawn (scene
  AUGER_WINCH) takes the party back up to the ship.
- **The key hint.** A hint window at the bottom of the screen shows the current Run-key action, for example
  "Shift: Dive".

### Sky isles

- A `location ... land=1` is never entered on foot, only by landing the airship next to it. The ship parks there,
  and the party arrives at the isle map's `dock` spawn (if it has one).
- The Crucible Isle (L_N38) is the only land-only location.
- Before the fault the Crucible Isle is reached by the sky cable. CABLE_CHOIR at the Ninefold Shrine goes to
  N38_R01 after CH07.

## 5. The sea floor (UNDERSEA)

- **The map.** A 96 x 72 world-kind map, generated by wgen.py as the last section of world2.map. It is post-fault
  and reached only by submarine. One sea-floor cell is 176/96 surface cells.
- **Terrain:**
  - open ocean above → sand seabed;
  - coastal water above → algae shelf (olive);
  - the sunken rim of the land → dunes (hills);
  - deeper under the land → continental rock (mountain, solid);
  - kelp forests (forest);
  - scree (rocky);
  - vent fields (lava, solid);
  - the abyssal trench (deep, passable).

  Every place has a channel to the open basin.
- **Places:**

  | Id | Place | Map |
  |---|---|---|
  | L_S01 | Old Bellharbor | S3_OLDBELL + S3_OLDBELL_HALL |
  | L_S02 | The Drowned Crown | S3_DROWNED |
  | L_S03 | The Wreck of the Tithe, dungeon mouth (WP_SEA) | S3_TITHE |
  | L_S04 | The Reef Temple, dungeon mouth (WP_SEA) | S3_REEF |
  | L_S05 | The Abyssal Cradle, Thalassar's lair (inner gate sealed) | S3_CRADLE |
  | L_S06 | The Throat, sea end | U40_R01 spawn `from_sea` |

  From the Deep side, U40_THROAT_END (the open lock, with the Diving Hull) now offers to take the diving hull down
  (`travel undersea throat`).
- **Sealed ways on, for later passes:** the Tithe's hold (`flag:s3_tithe_hold`), the Reef sanctum
  (`flag:s3_reef_sanctum`), the Drowned Crown's Oath Gate (`flag:s3_drowned_gate`) and the Cradle's rib-gate (no flag).
- **Mode 7** draws the sea floor with a murky blue sky and haze.
  - The baked art comes from bake.py's seabed style.
  - Until that bake has run, the game falls back to the collision grid in flat colours for the ground plane and the
    minimap. Mode-7 fallback: `Mode7.make_grid`; minimap fallback: `WorldHud.make_grid`.

## 6. Weather (visual only)

- **Kinds:** rain, snow, ash, fog, sandstorm. They are drawn with `shaders/weather.gdshader` (particles) plus
  `shaders/haze.gdshader` (drifting haze) over the field, under the minimap and the UI.
- **Rolls.** Weather rolls per region, every six in-game hours, and is deterministic by day, slot and region. Tables
  are in field_sys.gd:
  - `REGION_WEATHER`: Cinder Reach ash, Hoarfrost snow, Mirewold fog, Pale Basin sandstorms, rain on the coasts and
    the Crown March;
  - `REGION_WEATHER_POST`: more ash after the fault.
- **Where it applies:**
  - world maps use the region of the zone under the party;
  - outdoor town tilesets use the map's `region:`;
  - the Deep, the sea floor and interiors never have weather.
- **Map header:** `weather: rain|snow|ash|fog|sandstorm` fixes the weather, `weather: none` turns it off, and
  `weather: region` forces the region roll.
- **Setting:** Settings > "Weather effects" (on by default).

## 7. Roaming ancient wyrms

The wyrms roam only post-fault, after CH16.

| Id | Name | Map and range | Meets |
|---|---|---|---|
| SB01 | Cindermaw | WORLD_POST, Cinder Reach around N10 | the party on the ground |
| SB03 | Aerith-Vael | WORLD_POST, the whole sky, drawn aloft with a shadow | only the airship |
| SB02 | Thalassar | WORLD_POST coastal water (ground or airship); UNDERSEA (the submarine) | as listed |
| SB04 | Ossathrax | DEEP_POST, the Hollow Throne | the party on the ground |

- Contact runs scene `WYRM_<id>`: narration, `battle <id> noflee`, `set sb_<id>_down`. A beaten wyrm no longer
  appears.
- Vestige and level-break rewards are left to the superboss pass. Add them to the WYRM_ scenes after the battle line.
- **Sprites.** Frame 0 of `assets/ext/enemies/<sprite>.png` (the enemy's `sprite`, SB0x), scaled as a billboard.
  With a `<sprite>.json` that has `cell`, only the first cell is used. Without the art, a tinted silhouette is drawn.

## 8. The Crucible Isle arena (N38)

- **Maps:**
  - N38_R01, the sky dock: the cable winch west (pre-fault exit), the airship field east (post-fault exit to
    WORLD_POST `l_n38`);
  - N38_ARENA, the Hall of Wagers: Registrar (ladder), Bookmaker (bets), Solo Master, Pen-Keeper (beasts);
  - N38_PIT, the ring: the Herald (gauntlet); the champion's gate opens with `flag:arena_champion`.
- **Data:** content `arena` (field_s3.py). **State:** `Game.S.arena` = {rank, solo, gauntlet, bets, beasts}.
- **Ladder.**
  - Ten ranks on existing formations of rising level (D04_5 ... D12_4).
  - Fight the next rank only. Each rank pays its reward (items and crowns) once.
  - Rank 6 needs CH09. Ranks 7-10 need the World of Ruin.
- **Solo bouts.**
  - Three bouts, opening at ranks 2, 5 and 8.
  - The player picks the fight, then one active hero. The party is restored after the bout.
- **Bets.** FF6-style table: wager one owned item, fight the house's pick, win the prize or lose the wager.
- **Gauntlet.**
  - Opens with the ladder done, after the fault and CH16.
  - BX10, BX12, BX21, BX24, then SB07 Varro, one after another with no rest.
  - Winning sets `arena_champion` and `sb_SB07_down`, and gives A018.
- **Beast bouts.** If `Game.S.captured` holds monsters (an Array of enemy ids or {id} dicts, or a Dictionary keyed
  by id), the Pen-Keeper runs a watched bout for a crown stake. The higher level wins more often; the result is
  seeded.
- **Losing.** Arena battles never end the game: a loss restores the party and the loss stands
  (`run_battle(..., {"arena": true})`).
