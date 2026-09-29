# Dungeon and room construction bible

Each location has six authored room records. These are minimum functional rooms, not permission to stamp twelve identical six-room corridors. Scene dimensions in the JSON are initial layout envelopes, not final tiled artwork. Edges are undirected traversal links; puzzles may temporarily gate them only under the safety rules below.

## D01 — Crown Quarry

**Region:** R01; **first chapter:** CH01; **target levels:** 2–4; **optional:** False.

**Spatial mechanic:** Drain routes, then release the rail brake without opening the occupied lift.

| Room ID | Name | Purpose | Initial tiles |
| --- | --- | --- | --- |
| D01_R01 | Gatehouse | Arrival and rescue briefing | 40×28 |
| D01_R02 | Lunch Gallery | Meet Tessa under guard; find the worker list | 32×32 |
| D01_R03 | Flooded Spur | Shallow-water path and first enemies | 40×24 |
| D01_R04 | Pump Loft | Two linked pumps; preview the safe lift route | 32×28 |
| D01_R05 | Heartglass Face | Hear Ilyr; extraction boss arena | 40×32 |
| D01_R06 | Lift Yard | Evacuate workers; departure scene | 32×24 |

**Connections:** D01_R01 ↔ D01_R02, D01_R02 ↔ D01_R03, D01_R03 ↔ D01_R04, D01_R04 ↔ D01_R05, D01_R05 ↔ D01_R06, D01_R04 ↔ D01_R02.

**Primary boss:** B01. **State change:** After the catastrophe, the entrance is a memorial and supply cache; the underground section is sealed, with all unique missed rewards moved to Mara.

**Secret:** one clue-led route with free accessory A001; later shop availability prevents permanent loss. An optional viewpoint or document may provide a second reward without inflating the unique-content count.

## D02 — Veyr Underways

**Region:** R01; **first chapter:** CH02; **target levels:** 4–6; **optional:** False.

**Spatial mechanic:** Reroute a signal bell to move patrols; no real-time stealth failure.

| Room ID | Name | Purpose | Initial tiles |
| --- | --- | --- | --- |
| D02_R01 | Intake Hall | Arrest escape | 40×28 |
| D02_R02 | Ledger Stacks | Oriel finds living names marked deceased | 32×32 |
| D02_R03 | Bell Junction | Ring decoy bell and inspect patrol route | 40×24 |
| D02_R04 | Cistern Walk | Optional chest and one-way drop with return ladder | 32×28 |
| D02_R05 | Seal Chamber | Brass Bailiff arena | 40×32 |
| D02_R06 | Canal Exit | Boat exit and recovery point | 32×24 |

**Connections:** D02_R01 ↔ D02_R02, D02_R02 ↔ D02_R03, D02_R03 ↔ D02_R04, D02_R04 ↔ D02_R05, D02_R05 ↔ D02_R06, D02_R03 ↔ D02_R05.

**Primary boss:** B02. **State change:** Post-state removes the arrest route, adds Pip’s registry rescue and a sealed optional echo chamber for B15; preserve opened chest IDs.

**Secret:** one clue-led route with free accessory A002; later shop availability prevents permanent loss. An optional viewpoint or document may provide a second reward without inflating the unique-content count.

## D03 — Rootward

**Region:** R01; **first chapter:** CH03; **target levels:** 6–8; **optional:** False.

**Spatial mechanic:** Route irrigation through roots to reveal bridges; always leave a walking return path.

| Room ID | Name | Purpose | Initial tiles |
| --- | --- | --- | --- |
| D03_R01 | Wagon Hollow | Nera’s displaced caravan | 40×28 |
| D03_R02 | Root Ford | First water-level demonstration | 32×32 |
| D03_R03 | Three Sluices | Three valves with a visible correct-order mural | 40×24 |
| D03_R04 | Canopy Rise | Optional lookout and bow cache | 32×28 |
| D03_R05 | Hollow Grove | Rootbound Stag arena | 40×32 |
| D03_R06 | North Verge | Climb to the northern road | 32×24 |

**Connections:** D03_R01 ↔ D03_R02, D03_R02 ↔ D03_R03, D03_R03 ↔ D03_R04, D03_R04 ↔ D03_R05, D03_R05 ↔ D03_R06, D03_R02 ↔ D03_R05.

**Primary boss:** B03. **State change:** Post-state is flooded; existing trees become stepping bridges. B11 guards a new rescue channel during Nera’s reunion.

**Secret:** one clue-led route with free accessory A003; later shop availability prevents permanent loss. An optional viewpoint or document may provide a second reward without inflating the unique-content count.

## D04 — Furnace Spine

**Region:** R02; **first chapter:** CH04; **target levels:** 8–11; **optional:** False.

**Spatial mechanic:** Balance three pressure lines, venting into empty chambers rather than occupied workshops.

| Room ID | Name | Purpose | Initial tiles |
| --- | --- | --- | --- |
| D04_R01 | Shift Gate | Ivo joins the party | 40×28 |
| D04_R02 | Boiler Walk | Observe burst rhythm before crossing | 32×32 |
| D04_R03 | Red Valve | First valve and optional workers | 40×24 |
| D04_R04 | Blue Valve | Second valve; bridge to regulator | 32×28 |
| D04_R05 | Regulator Crown | Foundry Colossus arena | 40×32 |
| D04_R06 | Cooling Garden | Manual shutdown and workers’ argument | 32×24 |

**Connections:** D04_R01 ↔ D04_R02, D04_R02 ↔ D04_R03, D04_R02 ↔ D04_R04, D04_R03 ↔ D04_R05, D04_R04 ↔ D04_R05, D04_R05 ↔ D04_R06.

**Primary boss:** B04. **State change:** Post-state repurposes pressure puzzle into a waterwheel start sequence; recovering Ivo activates V06 and the airship’s ordinary engine.

**Secret:** one clue-led route with free accessory A004; later shop availability prevents permanent loss. An optional viewpoint or document may provide a second reward without inflating the unique-content count.

## D05 — Drowned Archive

**Region:** R03; **first chapter:** CH06; **target levels:** 10–13; **optional:** False.

**Spatial mechanic:** Match three bell tones to archive shelves; clues remain visible and can be replayed.

| Room ID | Name | Purpose | Initial tiles |
| --- | --- | --- | --- |
| D05_R01 | Tide Door | Enter at low water | 40×28 |
| D05_R02 | Bell Nave | Three reproducible bell clues | 32×32 |
| D05_R03 | Dry Gallery | Records of extraction contracts | 40×24 |
| D05_R04 | Wet Gallery | Submerged route above safe stepping blocks | 32×28 |
| D05_R05 | Witness Vault | Custodian arena and Rook’s evidence | 40×32 |
| D05_R06 | Roof Pier | Open the coastal ferry route | 32×24 |

**Connections:** D05_R01 ↔ D05_R02, D05_R02 ↔ D05_R03, D05_R02 ↔ D05_R04, D05_R03 ↔ D05_R05, D05_R04 ↔ D05_R05, D05_R05 ↔ D05_R06.

**Primary boss:** B05. **State change:** Post-state swaps low-water paths for upper shelves. Tessa is maintaining a failing shield; releasing it safely opens the same exit.

**Secret:** one clue-led route with free accessory A005; later shop availability prevents permanent loss. An optional viewpoint or document may provide a second reward without inflating the unique-content count.

## D06 — Skychain Viaduct

**Region:** R04; **first chapter:** CH07; **target levels:** 12–15; **optional:** False.

**Spatial mechanic:** Use ballast anchors to change wind channels; falls reset locally without losing rewards.

| Room ID | Name | Purpose | Initial tiles |
| --- | --- | --- | --- |
| D06_R01 | Cable Foot | Corren introduction | 40×28 |
| D06_R02 | Ballast Yard | Two ballast locks | 32×32 |
| D06_R03 | Crosswind Span | Readable gust cycle with generous movement windows | 40×24 |
| D06_R04 | Pilots’ Niche | Optional rescue gear and rest point | 32×28 |
| D06_R05 | Chain Nest | Chain Roc arena | 40×32 |
| D06_R06 | High Landing | High Aerie cable system unlocked | 32×24 |

**Connections:** D06_R01 ↔ D06_R02, D06_R02 ↔ D06_R03, D06_R03 ↔ D06_R04, D06_R04 ↔ D06_R05, D06_R05 ↔ D06_R06, D06_R02 ↔ D06_R04.

**Primary boss:** B06. **State change:** Post-state changes the chain into an island link. Corren’s reunion restores safe moorings, not a mandatory movement skill.

**Secret:** one clue-led route with free accessory A006; later shop availability prevents permanent loss. An optional viewpoint or document may provide a second reward without inflating the unique-content count.

## D07 — Whitebone Redoubt

**Region:** R05; **first chapter:** CH08; **target levels:** 14–17; **optional:** False.

**Spatial mechanic:** Replace binding sigils with consent keys recorded from actual occupants.

| Room ID | Name | Purpose | Initial tiles |
| --- | --- | --- | --- |
| D07_R01 | White Gate | Sable requests a temporary truce | 40×28 |
| D07_R02 | Barracks | Inspect identical uniforms and different personal effects | 32×32 |
| D07_R03 | Names Hall | Read individual seals | 40×24 |
| D07_R04 | Binding Cells | Release captives; Sable’s equipment teaching | 32×28 |
| D07_R05 | Tribunal Ring | Ivory Adjudicator arena | 40×32 |
| D07_R06 | Snow Exit | Sable becomes a permanent party member | 32×24 |

**Connections:** D07_R01 ↔ D07_R02, D07_R02 ↔ D07_R03, D07_R03 ↔ D07_R04, D07_R04 ↔ D07_R05, D07_R05 ↔ D07_R06, D07_R02 ↔ D07_R04.

**Primary boss:** B07. **State change:** Post-state becomes a prisoner sanctuary. Sable returns voluntarily; the player removes distributed seals through a noncombat room sequence.

**Secret:** one clue-led route with free accessory A007; later shop availability prevents permanent loss. An optional viewpoint or document may provide a second reward without inflating the unique-content count.

## D08 — Memory Vault

**Region:** R05; **first chapter:** CH09; **target levels:** 17–20; **optional:** False.

**Spatial mechanic:** Arrange testimony in chronology; conflicting accounts must both remain in the record.

| Room ID | Name | Purpose | Initial tiles |
| --- | --- | --- | --- |
| D08_R01 | Listening Gate | Consent warning and opt-out that changes staging, not progression | 40×28 |
| D08_R02 | Voluntary Accord | Original shared-body pact | 32×32 |
| D08_R03 | First Industry | Industrial conversion of the pact | 40×24 |
| D08_R04 | Quiet Nursery | Dain sees records without entering a named child’s memory | 32×28 |
| D08_R05 | Choir Chamber | Pale Choir arena | 40×32 |
| D08_R06 | Still Pool | Ilyr speaks with Dain instead of through him | 32×24 |

**Connections:** D08_R01 ↔ D08_R02, D08_R02 ↔ D08_R03, D08_R02 ↔ D08_R04, D08_R03 ↔ D08_R05, D08_R04 ↔ D08_R05, D08_R05 ↔ D08_R06.

**Primary boss:** B08. **State change:** Post-state preserves the evidence rooms and adds Oriel’s restitution scene. No new false history overrides the first visit.

**Secret:** one clue-led route with free accessory A008; later shop availability prevents permanent loss. An optional viewpoint or document may provide a second reward without inflating the unique-content count.

## D09 — Sable Conduit

**Region:** R01; **first chapter:** CH11; **target levels:** 20–24; **optional:** False.

**Spatial mechanic:** Disable three synchronization relays while keeping evacuation transport powered.

| Room ID | Name | Purpose | Initial tiles |
| --- | --- | --- | --- |
| D09_R01 | Old Aqueduct | All eight travel together; select active four | 40×28 |
| D09_R02 | South Relay | Release local relay | 32×32 |
| D09_R03 | North Relay | Reroute occupied lift | 40×24 |
| D09_R04 | Soldiers’ Walk | Optional rescue; final warning and protected backup save | 32×28 |
| D09_R05 | Marshal Bridge | Voss human-form boss | 40×32 |
| D09_R06 | Crown Dais | Rook boss B10 and irreversible world transition | 32×24 |

**Connections:** D09_R01 ↔ D09_R02, D09_R01 ↔ D09_R03, D09_R02 ↔ D09_R04, D09_R03 ↔ D09_R04, D09_R04 ↔ D09_R05, D09_R05 ↔ D09_R06.

**Primary boss:** B09. **State change:** Destroyed after the catastrophe. Unique loot is forwarded to Hearthward’s salvage chest. No quest requires returning here.

**Secret:** one clue-led route with free accessory A009; later shop availability prevents permanent loss. An optional viewpoint or document may provide a second reward without inflating the unique-content count.

## D10 — Crown Heart

**Region:** R06; **first chapter:** CH22; **target levels:** 34–42; **optional:** False.

**Spatial mechanic:** Two four-person parties release alternating locks; neither party can trap the other.

| Room ID | Name | Purpose | Initial tiles |
| --- | --- | --- | --- |
| D10_R01 | Accord Dock | Reversible final warning; recovery and formation screen | 40×28 |
| D10_R02 | West Lung | Party A pressure sequence | 32×32 |
| D10_R03 | East Lung | Party B name-release sequence | 40×24 |
| D10_R04 | Concord Bridge | Reunite; rest point; optional B16 alcove | 32×28 |
| D10_R05 | Crown Vessel | Three-phase final boss, one encounter identity | 40×32 |
| D10_R06 | Open Sky | Release ritual and ending transition | 32×24 |

**Connections:** D10_R01 ↔ D10_R02, D10_R01 ↔ D10_R03, D10_R02 ↔ D10_R04, D10_R03 ↔ D10_R04, D10_R04 ↔ D10_R05, D10_R05 ↔ D10_R06.

**Primary boss:** B12. **State change:** Post only. Clear-save returns to Accord Dock before the final commitment while preserving clear flags and optional completion.

**Secret:** one clue-led route with free accessory A010; later shop availability prevents permanent loss. An optional viewpoint or document may provide a second reward without inflating the unique-content count.

## D11 — Cradle of Winter

**Region:** R05; **first chapter:** CH21; **target levels:** 30–35; **optional:** True.

**Spatial mechanic:** Warm occupied shelters before thawing the route to the frozen sanctum.

| Room ID | Name | Purpose | Initial tiles |
| --- | --- | --- | --- |
| D11_R01 | White Causeway | Quest Q09 starts here | 40×28 |
| D11_R02 | Sleeping House | Identify living sleepers | 32×32 |
| D11_R03 | Warmth Channels | Three reusable heat sources with no consumable lock | 40×24 |
| D11_R04 | Rime Gallery | Optional equipment cache | 32×28 |
| D11_R05 | Lantern Cradle | Lantern Eater optional boss | 40×32 |
| D11_R06 | Dawn Window | Winter Hind offers a pact | 32×24 |

**Connections:** D11_R01 ↔ D11_R02, D11_R02 ↔ D11_R03, D11_R03 ↔ D11_R04, D11_R04 ↔ D11_R05, D11_R05 ↔ D11_R06, D11_R02 ↔ D11_R04.

**Primary boss:** B13. **State change:** Post-only island visible from Nacre; airship landing is permanent after discovery.

**Secret:** one clue-led route with free accessory A011; later shop availability prevents permanent loss. An optional viewpoint or document may provide a second reward without inflating the unique-content count.

## D12 — Starless Reef

**Region:** R06; **first chapter:** CH21; **target levels:** 34–39; **optional:** True.

**Spatial mechanic:** Follow audible beacons through a dark reef; provide equal visual signals.

| Room ID | Name | Purpose | Initial tiles |
| --- | --- | --- | --- |
| D12_R01 | Blackwater Mooring | Quest Q10 start | 40×28 |
| D12_R02 | First Beacon | Teach signal rhythm | 32×32 |
| D12_R03 | Second Beacon | Move reflector without extinguishing return beacon | 40×24 |
| D12_R04 | Wreck Library | Recovered passenger names | 32×28 |
| D12_R05 | Night Trench | Heartless Leviathan optional boss | 40×32 |
| D12_R06 | Open Current | Night Leviathan offers a pact | 32×24 |

**Connections:** D12_R01 ↔ D12_R02, D12_R02 ↔ D12_R03, D12_R03 ↔ D12_R04, D12_R04 ↔ D12_R05, D12_R05 ↔ D12_R06, D12_R02 ↔ D12_R04.

**Primary boss:** B14. **State change:** Post only. Return beacon is unconditionally lit after boss victory; audio is never the sole navigation channel.

**Secret:** one clue-led route with free accessory A012; later shop availability prevents permanent loss. An optional viewpoint or document may provide a second reward without inflating the unique-content count.

## Construction and softlock rules

Entrance, decision point, payoff and exit should be identifiable from silhouettes before the player reads a label. Reuse tiles; do not reuse the exact composition. Furnace rooms have vertical pressure lines and visible occupied spaces; the archive has parallel dry/wet routes; Skychain emphasizes lateral silhouettes and foreground cables; the vault uses concentric testimony rooms; the final dungeon visibly separates two routes and then reunites them.

All switches show an observable result. Required puzzle clues remain accessible after an incorrect operation. Include a local reset handle for any movable-object puzzle. No required switch consumes a finite item. A one-way drop must have a return ladder or connect to a permanent unlocked exit. Save points sit before bosses, not behind them. Defeat reloads the checkpoint with the same baseline resources and no duplicated loot.

D02 has a post-state B15 alcove, and D10 has a B16 alcove. These are subareas of an existing room or an attached small arena, not additional unique dungeons. D09 has B09 and B10 in adjacent final rooms. D03’s post rescue has B11. Do not count a repeated normal encounter as a new boss.

Record a doorway-spawn contract for every edge: source trigger, destination scene, spawn marker, approach direction, conditions and return behavior. Test collision and reachability in the actual map geometry. The included graph check confirms connected metadata only; it does not prove that tiled walls, collision shapes or cutscene blocking allow a player through.
