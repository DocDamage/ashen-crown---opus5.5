# World and persistence bible

## R01 — Crown March

**Geography:** River farms, quarry rail, a fortified capital. **Palette:** green-black masonry, faded wheat, red pennants.

The fertile heartland discovers that its prosperity has a hidden human cost.

## R02 — Cinder Reach

**Geography:** Basalt ridges, pipe viaducts, furnace terraces. **Palette:** umber, copper, orange light, smoke-blue shadows.

Extraction workers need a survivable transition, not a lecture about destroying their livelihoods.

## R03 — Glass Coast

**Geography:** Tidal libraries, bell towers, salt-bright docks. **Palette:** teal shallows, cream stone, oxidized bronze.

The sea returns testimony that the state tried to drown.

## R04 — Skyspine

**Geography:** Cliff settlements, cable ferries, wind shrines. **Palette:** pale granite, indigo cloud shadows, worn ochre cloth.

A society built around glorious sacrifice must learn the value of returning alive.

## R05 — Pale Basin

**Geography:** Salt flats, mineral gardens, memory vaults. **Palette:** lilac salt, moon-white boneglass, dark plum.

People confront inherited memories without surrendering their own identities.

## R06 — Ember Sea

**Geography:** Broken islands, refugee pontoons, exposed crown relay. **Palette:** charcoal reefs, coral-red lanterns, deep cobalt.

The catastrophe makes room for a new compact, but does not repair its damage.

## Towns

Each town has three authored scene maps, connected interiors where required, a minimum of six purposeful NPC interactions, a basic shop, an inn or recovery service, a rumor source and an exit that remains readable on the world map. T07 exists only in the post-state. Shop categories can share code, but not every town’s conversations or composition.

### T01 — Brackenford

**Region:** R01. **Function:** Quarry workers’ river town. **Scene maps:** Rail platform; shared bakery; miners’ bunkhouse.

**Before:** Low roofs, laundry lines, wheeled lunch carts, rails cutting through vegetable gardens.

**After:** Flood divides the town. The bakery becomes a footbridge depot; the bunkhouse is a shelter.

**Human detail:** A forewoman counts workers by name rather than production number.

**Recurring person:** Mara Pell. **Conversation:** Wages unpaid for three months; a storekeeper quietly extends credit.

### T02 — Veyr

**Region:** R01. **Function:** Fortified capital. **Scene maps:** South market; oath square; lower records hall.

**Before:** Heavy arches, red banners repaired with mismatched cloth, public heartglass lamps.

**After:** Outer walls fall into the river. The throne square becomes a distribution point; the records survive below ground.

**Human detail:** A palace clerk refuses a false death certificate even before the rebellion.

**Recurring person:** Clerk Ansel. **Conversation:** Two guards disagree about whether their families can eat loyalty.

### T03 — Cinderwake

**Region:** R02. **Function:** Industrial terrace settlement. **Scene maps:** Shift canteen; regulator shop; old cooling garden.

**Before:** Visible repair patches, copper pipe shadows, rich orange furnace interiors.

**After:** Power fails unevenly. Workers rig waterwheels and rotate heat between workshops.

**Human detail:** A worker asks how stopping extraction will keep the clinic heated.

**Recurring person:** Pell Quill. **Conversation:** A canteen wall keeps a tally of workplace injuries that no official ledger records.

### T04 — Bellharbor

**Region:** R03. **Function:** Port and archive town. **Scene maps:** Bell quay; chartmaker lane; tide chapel.

**Before:** Dense awnings, rope bundles, cream and teal stone, bells of uneven sizes.

**After:** Lower streets flood. Ropewalks become upper-level roads; the tide chapel is an evacuation station.

**Human detail:** A child rings an alarm using a cooking pot after the state removes the bell.

**Recurring person:** Jori Marr. **Conversation:** Shipping manifests contain passenger names disguised as cargo.

### T05 — High Aerie

**Region:** R04. **Function:** Cliffside cable settlement. **Scene maps:** Cable court; returners’ hall; wind stair.

**Before:** Ochre streamers, anchored baskets, horizontal architecture clinging to cliffs.

**After:** A broken chain links two new islands. Windmills replace the suspended extraction engines.

**Human detail:** The memorial lists those who died but has no wall for those who brought others home.

**Recurring person:** Captain Edda Hale. **Conversation:** An old pilot admits the ceremonial uniforms make safe landings harder.

### T06 — Nacre

**Region:** R05. **Function:** Mineral garden and sanctuary. **Scene maps:** Salt market; quiet cloister; listening pool.

**Before:** Layered lilac minerals, low domes, water carried in cloth-lined jars.

**After:** The pool projects conflicting dragon memories. Residents establish a consent-based listening house.

**Human detail:** A gardener tends plants without asking whether they count as sacred.

**Recurring person:** Archivist Sen. **Conversation:** A family disagrees openly about a vision rather than receiving a single authoritative answer.

### T07 — Hearthward

**Region:** R06. **Function:** Post-catastrophe refugee harbor. **Scene maps:** Ponton market; communal hearth; Wayfarer berth.

**Before:** Tents become cabins across a visible sequence; reused signs retain old town names.

**After:** Post-only town. Services grow through reunions and the Ash Accord; no construction minigame.

**Human detail:** Residents preserve signs from lost businesses, not just relics of rulers.

**Recurring person:** Mara Pell. **Conversation:** Residents argue over practical rebuilding priorities; decisions appear in later scenery.

## World graph

Pre-state critical route: Brackenford/quarry → Veyr/Underways → Rootward → Cinderwake/Furnace → Bellharbor/Archive → coastal ferry → Skychain/High Aerie → Whitebone/Nacre → Memory Vault → regional accord visits → Sable Conduit. Walking and vehicle edges are authored, not inferred from geographic distance. Place the capital near the river, the coast east, the cliffs northeast, the basin north and the future Ember Sea across the central relay fault.

Post-state critical route: Hearthward → flooded Rootward/Brackenford → upper Bellharbor/Archive → Cinderwake/Furnace → Wayfarer. Then expose High Aerie, Veyr and Whitebone as three independent reunion destinations. All three lead to the Ash Accord at Nacre, which opens the final route. Cradle of Winter and Starless Reef are optional airship landings. A rumor reveals each without adding a mandatory minimap arrow.

Use two authored overworld map resources with shared stable location IDs. Changed coastlines must be visually legible in both the region map and in movement collision. Location destinations are records with explicit valid spawn points, not arbitrary coordinates copied from the earlier state.

## Traversal

Walking is four-directional grid-aware movement with smooth animation, forgiving corner correction and collision at the feet. Running is a held/toggled option, not stamina. The ferry follows authored routes after CH06. The cable ferry opens after CH07. Wayfarer opens after CH16 and has a deck, common room, formation screen, destination map and normal repair-based travel fiction. It does not require fuel grinding.

Airship landing checks a marked landing region and a valid walkable spawn. A failed landing leaves the ship in flight with a visible reason. On foot, the player can recall the ship at any discovered landing zone. Entering a dungeon must not despawn or lose its parked location. No companion-specific field skill may permanently block a main route; Corren is not a mandatory Jump key and Sable is not a mandatory lockpick in the active party.

## Catastrophe transaction

One committed transition changes `world.phase` from `pre` to `post`, marks CH12 complete, sets the valid arrival spawn at Hearthward, updates companion availability, switches world resources and appends the event ID to the applied-event ledger. Save a separate pre-transition backup first. Commit the new payload atomically. On a process crash, load either the complete pre-state or complete post-state; never a mixture.

Inventory is owned by the save, not by the currently instantiated party scene. Equipment remains assigned to its character while they are absent. Their XP continues under the reserve rule. Rejoining does not duplicate equipment or reset personal progress. Missed unique rewards from sealed pre-state maps are forwarded to one stable salvage ledger. The transfer checks acquisition IDs, not whether the item is currently equipped or was sold.

Each chest uses a stable ID. A chest intentionally replaced by a post-state chest uses a new ID; unchanged chests retain their ID and opened state. NPCs, doors, rumors and shops read explicit phase and quest conditions. The renderer must not mutate progression just because a map loaded.

## After the ending

The clear-save offers return to the pre-finale post-world snapshot, preserving the clear flag and completed optional content. This is not a claim that every NPC has a simulated post-ending schedule. Label the menu choice honestly. Do not overwrite the only pre-finale manual save with the credits scene.
