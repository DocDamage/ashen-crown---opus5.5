# World v2 — surface, underground, World of Ruin (expansion design, 2026-09-30)

Owner answers: `claude/ashen_crown_expansion_v2.md` and `claude/ashen_crown_expansion_v2_answers.md` (project docs).
This file is the working bible for the expansion. Names are Claude's (owner delegated naming).
Canon rules from `00_CANON_AND_SCOPE.md` and `02_STORY_BIBLE.md` still hold. Geography changes happen only along
the relay faults. Nobody is made disposable.

## 1. Scale

| Map | Old size (cells) | New size (cells) | Notes |
|---|---|---|---|
| Surface (pre-fault) `WORLD` | 96 x 72 | 176 x 132 | ~3.4x area; 9 regions |
| Surface (post-fault) `WORLD_POST` | 96 x 72 | 176 x 132 | same frame, reshaped (section 5) |
| Underground `DEEP` / `DEEP_POST` | — | 176 x 132 | same size as the surface; 3 realms |
| Sea floor `UNDERSEA` | — | 120 x 90 | submarine only, post-fault |

The world map is drawn with the Mode-7 renderer (section 7). It has one cell per 48 px ground texel, upright billboard
landmarks, and random encounters by region and terrain.

## 2. Surface regions (pre-fault)

The six canon regions keep their identity and move onto the larger map. Three new regions hold the new heroes'
homelands. Arrows give rough compass placement on the new map.

| Id | Region | Where | Look | Level band (normal) |
|---|---|---|---|---|
| R01 | Crown March | centre-south | river farms, quarry rail, capital | 1–12 |
| R02 | Cinder Reach | west | basalt ridges, pipe viaducts | 10–18 |
| R03 | Glass Coast | east coast | tidal libraries, bell towers | 14–22 |
| R04 | Skyspine | north-east | cliffs, cable ferries, wind shrines | 18–26 |
| R05 | Pale Basin | north | salt flats, mineral gardens | 22–30 |
| R06 | Ember Sea | south-east sea | reefs, islands (pre: fishing isles) | 20–30 |
| R07 | Vermilion Reach (new) | far east, across the strait | red maples, torii-like fox gates, lantern rivers | 24–32 |
| R08 | Mirewold (new) | south-west | fen, plague cities, quarantine walls, gibbet roads | 16–24 |
| R09 | Hoarfrost March (new) | far north | frozen tundra, dead forests, ice-bound citadel | 28–38 |
| SKY | Shattered Choir (new) | floating isles over Skyspine | fallen sky-host ruins, Arena isle | 30+ |

## 3. Places — surface (60)

Types: T town, V village, D dungeon, L landmark/shrine, S secret, A arena.
"Opens" is the earliest chapter the place can be reached. Q = questline hosted there (section 8).
Existing ids keep their numbers. New ids use N01–N43.

| Id | Name | Type | Region | Opens | Notes / Q |
|---|---|---|---|---|---|
| T01 | Brackenford | T | R01 | CH01 | Q01, Q05 |
| T02 | Veyr | T | R01 | CH02 | capital |
| T03 | Cinderwake | T | R02 | CH04 | Q04 |
| T04 | Bellharbor | T | R03 | CH05 | Q08 |
| T05 | High Aerie | T | R04 | CH07 | Q03 |
| T06 | Nacre | T | R05 | CH09 | Q06, Q09 hook |
| D01 | Crown Quarry | D | R01 | CH01 | deepened; CH07 descent to the Deep (section 4) |
| D02 | Veyr Underways | D | R01 | CH02 | |
| D03 | Rootward | D | R01 | CH03 | |
| D04 | Furnace Spine | D | R02 | CH04 | |
| D05 | Drowned Archive | D | R03 | CH05 | |
| D06 | Skychain Viaduct | D | R04 | CH07 | |
| D07 | Whitebone Redoubt | D | R05 | CH08 | Q07 |
| D08 | Memory Vault | D | R05 | CH09 | |
| D09 | Sable Conduit | D | R01 | CH11 | |
| N01 | Hollins Mill | V | R01 | CH01 | millers, first crafter, fishing pond (tutorial) |
| N02 | Gallowgate Toll | L | R01 | CH02 | Crown toll fort; bounty board; waystone |
| N03 | Wren's Orchard | V | R01 | CH03 | cider farm; night-only ghost orchard event |
| N04 | The Sunken Chapel | D | R01 | CH03 | optional dungeon; drowned oath-knights |
| N05 | Ashward Barrows | S | R01 | CH06 | hidden barrow; Maldrath foreshadowing |
| N06 | Kettle Row | V | R02 | CH04 | slag-miners' village; mining node tutorial |
| N07 | The Slagfalls | D | R02 | CH04 | optional; molten terraces |
| N08 | Anvil Cairn | L | R02 | CH04 | smith shrine; forge crafter |
| N09 | Pipewright's Rest | V | R02 | CH05 | pipe-inn over a viaduct |
| N10 | Cindermaw Caldera | S | R02 | CH10 | caldera crater; later the Surface Wyrm's lair |
| N11 | Tidewrack | V | R03 | CH05 | wreck-salvager village; salvage node tutorial |
| N12 | Belltower Point | L | R03 | CH05 | lighthouse; ferry hub |
| N13 | The Brine Stair | D | R03 | CH06 | optional sea-cave dungeon |
| N14 | Saltwhistle Isle | V | R06 | CH06 | fishing guild HQ; fishing tournament |
| N15 | Gullrock | S | R06 | CH06 | smugglers' hidden cove |
| N16 | Windrest | V | R04 | CH07 | shepherd hamlet on the cliffs; Brackhorn stables |
| N17 | The Ninefold Shrine | L | R04 | CH07 | wind shrine; sky cable to the Arena (pre-fault) |
| N18 | Eyrie Hollow | D | R04 | CH08 | optional; roc nests |
| N19 | Lilac Seep | V | R05 | CH09 | mineral farmers; herbalist |
| N20 | The Glass Orchard | L | R05 | CH09 | crystal trees; Vestige lore |
| N21 | Sorrowmere | D | R05 | CH09 | optional; memory-drowning lake |
| N22 | Harrowfen | T | R08 | CH06 | quarantined plague city; Corvus's home; Q-C12 |
| N23 | The Gibbet Road | L | R08 | CH06 | road of cages; night event |
| N24 | Sickle Hamlet | V | R08 | CH06 | fen reapers; poison herbs |
| N25 | The Leech Cathedral | D | R08 | CH10 | optional; plague-order stronghold |
| N26 | Moth Hollow | S | R08 | CH10 | secret glade; Vestige foreshadowing |
| N27 | Kaminari Ford | V | R07 | CH10 | river-lantern village; ferry over the strait |
| N28 | Akagane, the Fox Court | T | R07 | CH10 | Kitsune's court city; Q-C09 |
| N29 | Thousand Gates | D | R07 | CH10 | optional; illusion maze of fox gates |
| N30 | The Whispering Maples | S | R07 | CH10 | forest maze; night-only fox wedding |
| N31 | Shiroyama Watch | L | R07 | CH11 | ruined castle keep; view over the strait |
| N32 | Rimeholt | V | R09 | CH10 | last tundra village; fur traders |
| N33 | The Ice Road | L | R09 | CH10 | frozen lake crossing; weather set piece |
| N34 | Glacier Spire | D | R09 | CH11 | optional; frozen ascent |
| N35 | Coldharbour Citadel | D | R09 | CH11 | the Lich King's frozen seat (pre-fault: sealed) |
| N36 | The Aurora Pit | S | R09 | CH11 | Great Pit to the Deep (airship descent point, post) |
| N37 | Choir Anchorage | L | SKY | CH07 | sky-cable landing (pre); airship field (post) |
| N38 | The Crucible Isle (Arena) | A | SKY | CH08 | Arena: ladder, solo, betting, gauntlet |
| N39 | Seraphel, Fallen Host | D | SKY | CH12 (post) | Archangel's ruined sky host; Q-C10 |
| N40 | The Broken Organ | S | SKY | post | floating wreck of the host's great organ |
| N41 | Oathstone Crossroads | L | R01 | CH02 | milestone hub; waystone; travelling merchant |
| N42 | The Weeping Dam | D | R02 | CH05 | optional; failing dam over Kettle Row |
| N43 | Lanternfall | V | R03 | CH06 | cliff village of lamp makers; night market |

Post-fault additions and changes are in section 5. With the post-only sites the surface count is 60.

## 4. The Deep (underground, same size as the surface)

The Deep opens **before the fault**. In **CH07b "The Quarry Remembers"** the party returns to Crown Quarry (D01). Three
things are happening at once:
- the lower quarry has collapsed into a vast cavern, trapping workers below;
- Ilyr feels dragon fragments far beneath;
- a Crown detachment is already below, mining.

Only the dragon realm opens at CH07b. The builder Lattice opens in CH11, when the Conduit's drill-lift comes free. The
Hollow Throne opens post-fault, through the Aurora Pit airship descent and the Lanternwake drill.

| Realm | Id | Look | People | Level band |
|---|---|---|---|---|
| Emberdeep (dragon under-realm) | U1 | magma rivers, dragon-bone vaults, geode forests | dragonborn enclaves; the delvers | 18–30 |
| The Lattice (builder cities) | U2 | buried chrome and glass cities, rails, dead lights | builder machines, keepers | 28–40 |
| The Hollow Throne (realm of the dead) | U3 | black lakes, grave-cities, bone bridges | the dead; Velkhar's rival | 36–50 |

**Rulers and powers:**
- **Delver king:** King **Horrach Stonebeard** of Karag Dun, the delver forge-city and the Deep's main hub. He is proud, in
  debt to the Crown, and his miners are dying.
- **The Lattice:** its heart is **the Prime Relay**, the builder machine the Crown copied. It is run by a sleeping builder
  mind, **CURATOR**, which still issues orders. Kael-09's standing order came from CURATOR.
- **The Hollow Throne:** ruled by **Mother Sepulchre**, Velkhar's rival. She was once his teacher. She hoards the dead as
  currency and wants the living to come down.

### Places — Deep (40)

| Id | Name | Type | Realm | Opens | Notes / Q |
|---|---|---|---|---|---|
| U01 | The Breach (quarry floor) | L | U1 | CH07b | descent; trapped workers |
| U02 | Karag Dun | T | U1 | CH07b | delver capital, King Horrach; master forge |
| U03 | Emberwell | V | U1 | CH07b | dragonborn enclave; Q-UP1 |
| U04 | The Geode Wood | D | U1 | CH07b | crystal forest; gathering |
| U05 | Ossuary of Wings | D | U1 | CH07b | dragon-bone vault; Ilyr memory scene |
| U06 | Magma Ferry | L | U1 | CH07b | lava-boat landing |
| U07 | Cinderlake Isles | V | U1 | CH08 | lava-boat village |
| U08 | The Crown Dig | D | U1 | CH07b | Crown mining camp dungeon; boss |
| U09 | Hearthroot Shrine | L | U1 | CH08 | Vestige shrine (V13) |
| U10 | Drakesleep Hollow | S | U1 | CH08 | sleeping dragon fragment; secret |
| U11 | Vaultmouth Rail | L | U1 | CH08 | mine-rail hub (fast travel) |
| U12 | Deepforge Mines | D | U1 | CH08 | optional; ore; delver quest |
| U13 | Scaleward | V | U1 | CH09 | hidden dragonborn refuge; Q-UP2 |
| U14 | The Singing Chasm | L | U1 | CH09 | echo set piece |
| U15 | Fungal Terraces | V | U1 | CH09 | mushroom farmers; herbalism |
| U16 | Lattice Gate | L | U2 | CH11 | Conduit drill-lift arrival |
| U17 | Meridian | T | U2 | CH11 | half-lit builder city; keepers' market |
| U18 | The Assembly Floors | D | U2 | CH11 | automaton factory; Kael-09 lore |
| U19 | Railhead Nine | V | U2 | CH11 | keepers' settlement on the mag-rail |
| U20 | The Datum Archive | D | U2 | post | builder records; Q-BM1 |
| U21 | Glasswater Reservoir | L | U2 | post | lake-boat dock; undersea link tunnel |
| U22 | The Highway That Was | L | U2 | post | Night Rider's patrol road; Q-C17 |
| U23 | Vault Omega | D | U2 | post | Kael-09's origin vault; Q-C16 |
| U24 | Prime Relay | D | U2 | post | CURATOR's heart; Q-BM3 climax |
| U25 | Shutdown Town | S | U2 | post | secret city of switched-off machines |
| U26 | Mag-rail Terminus | L | U2 | post | rail hub |
| U27 | The Sunless Garden | S | U2 | post | builder arboretum; rare herbs |
| U28 | Styx Landing | L | U3 | post | black-lake boat landing |
| U29 | Cenotaph | T | U3 | post | city of the honoured dead; Q-UP4 |
| U30 | The Bone Bridges | D | U3 | post | span dungeon |
| U31 | Sepulchre Court | D | U3 | post | Mother Sepulchre's palace |
| U32 | Abyss Gate | D | U3 | post | Inferna's origin; Q-C11 |
| U33 | The First Crown's Tomb | D | U3 | post | Maldrath recruit site (moved); Q-C14 |
| U34 | Mourner's Vale | V | U3 | post | living pilgrims who came down |
| U35 | The Lich Stair | D | U3 | post | Lich King's under-court; Q-C13 |
| U36 | Velkhar's Crypt-Gate | D | U3 | post | Velkhar recruit site (moved); Q-C15 |
| U37 | Weeping Mines | V | U3 | post | dead miners still digging |
| U38 | The Silent Choir | S | U3 | post | secret; Vestige V22 |
| U39 | Hollow Heart | D | U3 | post | bonus dungeon (post-game arc) |
| U40 | Undersea Throat | L | U3 | post | submarine link to the sea floor |

## 5. World of Ruin (post-fault surface)

The fault tears the surface along the relay lines. Canon logic applies: damage follows the fault lines only.

- **The continent splits into four landmasses and an archipelago.**
  - Crown March is cut from Cinder Reach by the **Veyr Rift**, a new inland sea.
  - The Glass Coast becomes islands.
  - The Pale Basin and Skyspine stay joined.
  - Vermilion Reach drifts behind a storm strait.
  - Hoarfrost March cracks open over the Aurora Pit.
- **Destroyed places.** Some are gone for good:
  - Kettle Row (N06), under the burst Weeping Dam;
  - Pipewright's Rest (N09);
  - Lanternfall (N43) — its lamp makers move to Hearthward.

  Others survive as ruins, with survivors:
  - Harrowfen (N22), burned by its own quarantine order;
  - Akagane (N28), the fox court in exile.
- **Risen land.** Dragon structures and builder ruins rise from the sea and the plains:
  - **P01** the Spine of Ilyrath, a dragon skeleton ridge and dungeon;
  - **P02** the Tessellate, a builder tower risen from the plains;
  - **P03** Hearthward (T07, existing);
  - **P04** the Drowned Crown, a sunken Veyr district reached by submarine;
  - **P05** Refuge Rock, a new survivors' village;
  - **P06** the Starless Reef (D12, existing);
  - **P07** the Crown Heart (D10, existing);
  - **P08** the Cradle of Winter (D11, existing);
  - **P09** the Last Beacon, a signal tower that gives the fast-travel network.
- **The Deep changes too.**
  - The fault floods part of Emberdeep: Magma Ferry routes change and Cinderlake Isles is lost.
  - The Lattice's lights come back on as CURATOR wakes.
  - The Hollow Throne opens.
- **The undersea (post, submarine):**
  - sunken towns — Old Bellharbor and the Drowned Crown;
  - undersea dungeons — the Wreck of the Tithe, and the Reef Temple;
  - the leviathan lair — the Abyssal Cradle, home of the Sea Wyrm superboss;
  - the Undersea Throat, which links to the Deep.

## 6. Vehicles (names by Claude)

| Vehicle | When | What |
|---|---|---|
| Brackhorn (Bramble) | CH03 | Mount. Faster, no encounters, world map. |
| Brackhorn variants | quests | **Ridgehorn** crosses mountains (Q-W2). **Fenwader** crosses shallows and marsh (Q-W4). **Deepstrider** runs in the Deep without encounters (Q-UP1). **Gilded Brackhorn** flies short hops (post-game). |
| Sky cable | CH07 | High Aerie ↔ Ninefold Shrine ↔ Crucible Isle (pre-fault Arena route). |
| Wayfarer | CH10–CH12 | Pre-fault airship; lost at the Dais. |
| Lanternwake | CH16 | Post-fault airship. |
| Lanternwake upgrades | quests | **Gale Vanes** (speed, Q-BM1). **Grapnel Keel** (land anywhere, Q-W6). **Diving Hull** (becomes a submarine, Q-W7). **Delver Auger** (drills into the Deep through Great Pits, Q-UP3). |
| Magma skiffs | CH07b | Lava boats in Emberdeep (Magma Ferry routes). |
| Lake barges | post | Black-lake boats in the Hollow Throne; Glasswater barges in the Lattice. |
| Mag-rail | CH11 / post | The Lattice's rail network: fast travel between rail hubs. Emberdeep has delver mine carts (Vaultmouth Rail). |

## 7. World-map presentation (Mode-7)

- The ground is a baked texture: Winlu 48 px terrain plus hand-painted coastlines, rivers and roads.
- It is drawn as a perspective plane. The camera tilt depends on the vehicle:
  - on foot: gentle;
  - on the Brackhorn: stronger;
  - on the airship: full FF6 tilt, with horizon fog and a sky band.
- The camera rotates only on the airship.
- Landmarks are upright billboards: towns, dungeons, trees, peaks, mills, lighthouses and bridges.
- Roads wind with the terrain: worn dirt paths, paved Crown highways near Veyr, bridges, signposts, milestones and forks.
- Day/night runs on a real-time clock (about 20 minutes per day). Weather is visual only.
- UI: minimap, full map screen with fog of war, quest markers, waystones.

## 8. Questlines (25+)

**Hero questlines (17).** Q01–Q08 keep their canon plots, deepened. These are new:
- Q-C09 Kitsune, *The Court of Masks*: Akagane / Thousand Gates.
- Q-C10 Archangel, *The Host That Stopped Answering*: Seraphel.
- Q-C11 Inferna, *Ledger of the Damned*: Abyss Gate.
- Q-C12 Corvus, *The Cure That Was Sold*: Harrowfen / Leech Cathedral.
- Q-C13 Lich King, *A Court Too Long in Mourning*: Coldharbour / Lich Stair.
- Q-C14 Maldrath, *The First Crown*: Ashward Barrows → First Crown's Tomb.
- Q-C15 Velkhar, *The Teacher Below*: Crypt-Gate → Sepulchre Court.
- Q-C16 Kael-09, *Standing Orders*: Vault Omega → Prime Relay.
- Q-C17 Night Rider, *The Highway That Was*: The Highway That Was / Tessellate.

**Underground peoples (4):**
- Q-UP1 *Emberwell's Debt* (dragonborn enclave vs the Crown dig).
- Q-UP2 *Scaleward* (hidden refuge; a choice about who is let in).
- Q-UP3 *The King Under the Mountain* (Horrach's debt; the Delver Auger).
- Q-UP4 *Cenotaph* (a living child trapped among the honoured dead).

**Builder mysteries (3):**
- Q-BM1 *The Datum Archive*.
- Q-BM2 *Shutdown Town*.
- Q-BM3 *CURATOR*, the Prime Relay climax, with a superboss tier.

**World of Ruin rescues (7):**
- Q-W1 *Refuge Rock*.
- Q-W2 *The Ridge Road* (Ridgehorn).
- Q-W3 *Harrowfen Burning*.
- Q-W4 *The Mire Ferry* (Fenwader).
- Q-W5 *The Fox Court in Exile*.
- Q-W6 *The Last Beacon* (Grapnel Keel).
- Q-W7 *Old Bellharbor* (Diving Hull).

**Existing optional (4):** Q09 winter, Q10 sea, Q11 no more crowns, Q12 song.

**Post-game arc (1):** *The Hollow Heart*, a bonus dungeon with the hardest superbosses.

Total: 36 questlines.

## 9. Superbosses and Vestiges V13–V24

**Roaming ancient dragons.** They roam late in the game, FFVII Weapon style. Each gives a Vestige and a level break.

| Superboss | Roams | Reward |
|---|---|---|
| Surface Wyrm **Cindermaw** | surface | V13 |
| Sea Wyrm **Thalassar** | undersea and coast | V14 |
| Sky Wyrm **Aerith-Vael** | airship lanes | V15 |
| Deep Wyrm **Ossathrax** | the Deep | V16 |

**Level breaks** come in tiers:
- 99 → 120 after the first ancient dragon;
- 150 after all four;
- 200 after the Hollow Heart finale.

**Other superbosses:**

| Superboss | Where | Reward / note |
|---|---|---|
| CURATOR | Prime Relay | V17 |
| Mother Sepulchre (true form) | Sepulchre Court | V18 |
| The Arena Gauntlet champion | Crucible Isle | V19 |
| the Choir That Remains | the Silent Choir | V22 |
| three Hollow Heart bosses | Hollow Heart | V20, V21, V23 |
| the Omega-tier **Unmade Crown** | Hollow Heart | V24 |

The soul-bound party (section 10) unlocks after the first ancient dragon falls.

## 10. The CH12 rescue and the soul-bound five

- **Choosing the five.** During the escape from the Crown Dais the player picks 5 of the 8 heroes who can be present:
  Morwen, Vespera, Golem, Elowen, Oni, Sak, Kitsune and Archangel. Raven and Aurex wake at Hearthward.
- **The mission.** The five go back for the prisoners still bound in the relays.
- **The timer.** It is hidden, with hints: Ilyr, the others' dialogue and the collapse sounds. If the player waits long
  enough, the whole team makes it out at the last second.
- **Leaving early.** Any hero still inside dies and returns changed. The type is chosen by the hero's nature:
  - undead, raised by Mother Sepulchre's court;
  - builder-rebuilt, remade by CURATOR's machines;
  - fragment-bound, sharing a body with a dragon fragment, as Raven shares his with Ilyr.
- **Soul-binding.** The survivors are soul-bound to the changed ones out of gratitude.
- **The locked party.** The five form a fixed party that can only be used as-is. It is fully playable, and nobody else can
  join it. It unlocks and merges back into the whole team after the first ancient dragon falls.
- **Reunion chapters** CH14–CH19 still play for these heroes, adapted: a reunion with the soul-bound team, or a changed
  hero coming back.

## 11. Enemy roster target

- **About 120 regular enemies.** 40 exist; about 80 are new, spread over:
  - surface regions: 9 regions x ~5;
  - the Deep: 3 realms x ~8;
  - the undersea: ~6;
  - night-only and rare: ~8;
  - post-fault variants, which are recolor tiers where marked.
- **New bosses: about 20**, one per optional dungeon or questline climax. Superbosses are in section 9.
- **All enemies are animated:** idle, attack, cast and hurt frames, built in Aseprite.
- **Art:** the owner's packs, pixelated in Aseprite where painted; AI art also runs through Aseprite.

## 12. As built (implementation notes)

- **CH12 rescue.**
  - Code in `game/src/story/rescue.gd` (class `Rescue`); map `D09_LIFT` (`content_src/maps/x_lead.map`); scenes in `content_src/scenes/ch12_rescue.scn`.
  - `CH12_FALL` starts it with `rescue begin` / `rescue pick`. Route bots and skipped scenes go straight to `CH12_FALL_BODY`.
  - Timer: T = 100 s. Arrival slots are 32/50/66/81/96 s (a smaller team takes the last slots). There are six hints; `CH12_LIFT_CRUSH` retries from the lift.
  - The forms are fixed by hero, as in section 10. Tints and passives are applied in `Game.stats_for` and `HeroArt`.
  - Survivors start at Bond 3 with each changed hero.
  - The Bound party: `Game.S.bound`, swapped by `bound swap` (menu **Switch**), with its camp at `BOUND_CAMP` (the Rootwell). Chapter scenes (`CH*`) do not run while the Bound are in control.
  - A reunion `join` for a bound hero plays `BOUND_MEET_<cid>`, and the hero stays with the Bound.
  - The Bound merge on the first wyrm (`levelbreak_1`), or at the finale team split.
  - Conditions: `changed:<cid>[:form]`, `bound`, `bound_on`, `bound_member:<cid>`, `qa`.
- **Bonds.** Code in `game/src/meta/bonds.gd`. Every shared victory adds +1 per pair. Levels come at 10/30/60/100/160 points, and each level gives +1% atk/matk/def/res, capped at 8%. The 36 pair scenes (`content_src/scenes/bonds.scn`) play after an inn rest at bond 2 and 4.
- **Stills.**
  - The `still <id> [seconds]` command shows `res://assets/stills/<id>.png` and is skipped when the file is missing.
  - The title screen uses `stills/title.png` when present.
  - The image brief is in `docs/expansion/STILLS.md`; processing is `tools/art/stills_job.py` with `tools/aseprite/stills.lua`.
- **Post-game.**
  - The QEPI Belfry Below (`x_epi.map`, `x_epi.scn`, `tools/content/epilogue.py`, `places/f_epi.py`), with boss BX27 and gear AN40, GN40, GN41 and WN40.
  - Enhanced epilogues for C09-C17 and for the rescue outcome, in `CH23_EPILOGUES`.
  - Completion tracking (`game/src/meta/completion.gd`, Records > Stats); achievements ST13-ST16.
- **World fix.** A mountain pass joins the Aerie cable station to the Skyspine foothills (`MOUNTAIN_PASSES` in `wgen.py`). Write the world with `python3 wgen.py ../../content_src/maps/world2.map`.
- **Ranches.** One per major kingdom, off the main town (both world phases): Fallowmere (T01_RANCH, Brackenford), Soot Paddock
  (T03_RANCH, Cinderwake), Gullbank Croft (T04_RANCH, Bellharbor), Windbreak Fold (T05_RANCH, High Aerie), Brinewell Steading
  (T06_RANCH, Nacre), Maple Gate Farm (N28_RANCH, Akagane), Lazar Fields (N22_RANCH, Harrowfen), Rimefold (N32_RANCH, Rimeholt).
  Code `game/src/meta/ranch.gd`, data `tools/content/ranch.py`, maps `content_src/maps/ranch.map`, scenes `ranch.scn`, art
  `tools/art/install_ranch.py` (Super Retro Ranch pack). Livestock is bought once per kind per ranch and fills the produce crate
  over in-game days; crop plots take seed from the rancher's seed box; goods eat, sell and cook (recipes RF01-RF06, RA01).
  Records > Ranches; achievements RN01-RN03.
