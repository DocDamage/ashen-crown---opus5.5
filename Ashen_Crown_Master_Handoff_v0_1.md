# THE ASHEN CROWN
## Complete design and autonomous-build handoff — v0.1

**September 28, 2026. New proposal, not recovered prior canon. Design package, not playable software.**

## Reading order

Start Here → scope → vision → story/cast/world → combat/content → art/audio → architecture/execution → acceptance → key scenes → kickoff. The separate files in the ZIP are preferable for an agent; this combined copy is provided for convenient reading.



---

<!-- Source: START_HERE.md -->

# Start here — The Ashen Crown

This is the game’s design and autonomous-build handoff, **not a playable game**. Keep it in a new dedicated folder. Do not extract it over an existing project or ask an agent to replace older JRPG canon with it.

## Immediate workflow

1. Extract the ZIP into a new folder and open that folder in your IDE/Claude Code workspace.
2. Read `docs/00_CANON_AND_SCOPE.md` and skim `docs/01_GAME_VISION.md`. `MASTER_HANDOFF.md` is the combined reading copy; specialist files and JSON are easier for implementation.
3. Select the actual Opus 5.5 option available in the host’s model selector. In Claude Code, verify the model through its model configuration UI/command rather than trusting a chat sentence or an assumed alias. Host/account availability is not guaranteed by this package. [S6]
4. Run the package checks below. Configure the Godot executable with `GODOT_BIN` or `--godot`; the environment doctor checks it without installing anything.
5. Paste the contents of `KICKOFF_PROMPT.md`. The agent should build the complete campaign through internal gates, not stop after writing more planning documents.

The root `CLAUDE.md` is intentionally short; it points to detailed specifications instead of importing the entire bible into every turn. Claude project instructions supply context, not a security boundary. Use the host’s real permissions and a dedicated workspace. [S3, S4] Do not disable all protections on your ordinary desktop just to reduce prompts. No remote push, paid service or large asset/model download is authorized by the kickoff.

## Commands that work in this package now

From the extracted package directory, using Python 3.10 or newer:

```text
python tools/validate_pack.py
python -m unittest discover -s tools -p "test_*.py" -v
python tools/doctor.py
```

On Windows, `py -3` may be used instead of `python` when that launcher is available. The first command validates design records. The second tests the validator and helper behavior. The third checks this machine’s environment and may correctly report that Godot is missing. None launches a game because `game/project.godot` has not been created yet.

To select an already installed Godot executable explicitly:

```text
python tools/doctor.py --godot "C:\Tools\Godot\Godot_v4.7.2-stable_win64_console.exe"
```

That path is an example, not a discovered path on your computer. Replace it with the actual executable. Matching export templates are checked later by the real export step. Do not assume that a successful `--version` check proves templates, rendering or controller access.

## Commands for the agent to establish after implementation

The following are templates, **not runnable completion checks for the current pack**. The agent must create the referenced project, runner and export preset, then record actual outcomes. [S2]

```text
<GODOT_BIN> --headless --path game --import
<GODOT_BIN> --headless --path game --script res://tests/run_all.gd
<GODOT_BIN> --path game -- --qa-route opening --qa-capture
<GODOT_BIN> --headless --path game --export-release "Windows Desktop" <ABSOLUTE_BUILD_PATH>/AshenCrown.exe
```

`--qa-route` and `--qa-capture` here are proposed project user arguments after `--`, not built-in Godot features. They must be implemented and tested. A headless run cannot substitute for screenshot evidence. Export success cannot substitute for launching the Windows executable on Windows.

## Included versus future work

Included: plot, cast, geography, room plans, mechanics, acquisition rules, content catalogs, key scene dialogue, six reference prompts, audio briefs, acceptance matrix, agent workflow and package utilities. Future work: actual Godot implementation, full NPC dialogue, final sprites and animation, generated/rendered maps, recorded music/SFX, runtime tests, balancing and playable export. `CURRENT_STATE.json` starts honestly at PACK_AUTHORED; it contains no invented game progress.


---

<!-- Source: docs/00_CANON_AND_SCOPE.md -->

# Canon, scope, and evidence boundary

**Version 0.1 • September 28, 2026 • New design proposal, not a recovered prior game bible.**

The user requested a pixel-art JRPG with the style and depth of Final Fantasy IV mixed with Final Fantasy VI, then continued the newly proposed Ashen Crown direction. That authorizes developing this proposal; it does not establish that its title, characters, plot or engine were approved in older conversations. The earlier reply overstated what had been recovered. Searches in this session did not establish the earlier JRPG narrative document. Do not rename, replace, import into, or overwrite an existing Aetherium, KeterEngine, WYRMFALL or other project on the strength of this package.

## Authority

The user’s current instructions take priority. Within this package, this scope document and explicit narrative invariants control; the specialist specifications explain their implementation; JSON catalogs supply IDs and initial values. A material conflict must be recorded, not silently “resolved” by inventing more scope. Engine APIs and installed capabilities must be checked against the actual environment. A data count is never evidence that the corresponding content works in a game.

## Product target

Create a complete original single-player, Windows-first, four-person-party JRPG. The desired experience is deliberate low-resolution exploration, side-view command battles, character-specific abilities, authored dungeons, towns with individual lives, a world map, an airship, secrets, an irreversible midpoint catastrophe, and a definitive ending. Preserve the user’s request for depth; do not replace it with a survival game, action roguelike, idle game, empty framework or generic walking demo.

The compact first campaign targets 8–12 hours on the critical path and roughly 12–18 hours with optional content. These are **design estimates**, not a measured playtime or a claim that an autonomous agent will finish that amount of polished content in one session. The design retains eight complete roles and a beginning-to-ending campaign. Implementation proceeds through internal verification gates; the opening slice is a gate, not a substitute deliverable.

## Fixed v0.1 content inventory

Eight playable characters, four active at once, six regions, seven towns, twelve dungeons (ten main-route locations and two optional locations), forty ordinary enemy identities, sixteen boss identities (twelve story and four optional), eighty player ability records (sixty-four character abilities, eight accessory spells and eight summons), eight Vestiges, forty-eight weapons, thirty-two armor/offhand/head items, twenty-four accessories, twenty-four consumables, twelve major side quests and twenty-four story chapters. CH21 is the optional preparation chapter; chapter numbering is editorial, not a requirement to complete nonlinear reunions in that order. Final-boss phases do not inflate the boss count. Post-state revisits do not inflate the dungeon count.

All eight playable characters are required before the two-party finale. Their personal resolutions are optional and alter equipment, techniques and epilogue scenes. This resolves the earlier proposal’s contradiction between optional character recovery and requiring two full parties of four. There are no additional optional playable characters in this version.

## Draft technical decisions

Use Godot 4.7.2 Standard, GDScript, the Compatibility renderer, and an authored 2D world. The exact installed executable and matching export templates must be verified before building. The official archive listed 4.7.2 as stable when consulted for this package; do not interpret that as permission to update a different existing project. See `16_SOURCES_AND_VERIFICATION.md`.

Use a 320×240 internal game viewport, 16×16 logical tiles, 24×32 world-character canvases and 48×64 party battle canvases. This is a proposed, explicit replacement for the previous reply’s unresolved 320×180/320×200 options. The 4:3 layout prioritizes room for a readable battle command panel and dense town compositions. It is not a claim that every historical reference used these exact dimensions. Provide clean integer scaling and letterboxing; do not stretch the art across a widescreen monitor.

## Narrative invariants

Dain is an independently existing person. Ilyr cannot reveal that Dain was an empty shell all along. Dragonborn lineages originated in engineered shared-body arrangements, later converted into coercive prisons; their lived identities remain real. Heartglass is a relay medium made from organs, not an unlimited magic currency. The catastrophe is caused by established choices and infrastructure, not a surprise god introduced in the last hour. Rook is right about extraction’s harm and wrong to force a mass awakening. Voss knowingly preserves coercion. Rook survives to answer for his actions. The final solution is established in CH10, refined through the reunions, and performed in CH22. It does not restore destroyed towns by resetting time.

## Excluded from this version

No multiplayer, live-service economy, in-game LLM, mandatory internet connection, procedural story generation at runtime, open-ended crafting economy, colony management, hunger/thirst, sprawling skill trees, 3D/HD-2D conversion, voice acting, romance simulator, multiple full campaigns, extra hidden party members, or engine/editor product. No copyrighted character sprites, ripped maps, commercial soundtrack imitations or copied dialogue. Inspiration guides presentation and structure; the content is original.

## What this delivery actually contains

A complete plot outline through the ending, character and world bibles, room-level dungeon plans, mechanical specifications, initial content catalogs, visual reference prompts, audio briefs, acceptance specifications, agent instructions, and runnable package-validation utilities. It does **not** contain a playable game, a Godot source project, finished images, animated spritesheets, recorded audio, a Windows executable, or runtime test results. Not every town conversation is fully scripted; the agent must author secondary dialogue under the supplied voice and continuity rules. Numerical balance and fun remain unverified until the real game is played.


---

<!-- Source: docs/01_GAME_VISION.md -->

# Game vision and player experience

## The promise

A knight discovers that the civilization he protects draws its power from imprisoned dragon minds—and that his own body is part of the prison. After an attempted liberation breaks the world, eight people who each helped sustain the system must reconnect it without turning anyone into fuel again.

The emotional center is not “humanity versus dragons.” It is whether responsibility means deciding for other people or giving them the information, means and freedom to decide. That theme must appear in small actions as often as in speeches: copying a map, leaving a repair manual, restoring a chosen name, letting another person finish a job.

## What depth means here

**Mechanical depth:** each party member changes how the player thinks about an encounter. Dain redirects risk; Tessa trades resources for intensity; Corren times absence and return; Ivo prepares the field; Nera reveals and exploits; Oriel predicts only committed actions; Sable changes elemental and status rules; Pip manipulates resources and opportunities. Four-person formations must produce different solutions, not different colors of the same attack.

**Narrative depth:** each character has a specific act to account for, relationships that complicate their perspective, an arc that affects behavior, and an optional resolution with visible consequences. Nobody receives forgiveness merely because a boss was defeated. Allow jokes, meals, repairs, disagreements and quiet landscapes between major revelations.

**Exploration depth:** show an unreachable place before granting the vehicle that reaches it. Let an NPC rumor point toward a real secret. Revisit a room in a changed world and recognize the structure beneath the change. Reward attention rather than forcing blind wall searches.

**Presentation depth:** movement, battles, menus, spells and cutscenes share one pixel scale, palette logic, sound vocabulary and typography. A large enemy database cannot compensate for flat battle staging or unreadable sprites.

## Rhythm

A typical short play segment contains exploration, a meaningful conversation, one or two ordinary encounters, a small spatial problem, a reward, and a clear next lead. A dungeon should establish its rule safely, combine it with another constraint, test it in a memorable room, offer a secret, then resolve in a boss or dramatic scene. Do not place combat after every five steps to manufacture playtime.

The campaign starts focused and linear. The ferry opens regional travel. The catastrophe briefly narrows the cast and geography, then the airship opens nonlinear recovery and optional exploration. The player may approach the last three reunions in any order. The final preparation window is genuinely optional.

## A player’s first fifteen minutes: design target

Start at Brackenford’s rail platform with Dain able to move almost immediately. A worker refuses to board until her crew’s names are checked. A short conversation establishes his badge, not the entire history of the continent. Enter the quarry through a clearly visible gate. Teach one interaction using a pump handle. Give the player a safe battle with Attack and Defend. Introduce Tessa holding a failing circuit. Let her fire spell and an item solve different enemies. Move through a rescue route that can be understood visually. Show the extractor’s unnatural response to Dain, then let the player fight the Warden.

This timing is a target for playtesting, not a guarantee or requirement to rush dialogue. The introduction must show the actual game—exploration, party interaction and battle—not a title screen followed by an encyclopedia.

## Quality bar and triage

A coherent completed room is worth more than six empty maps. A complete boss with an understandable tell is worth more than an extra attack name. During implementation, finish the first town–dungeon–battle–reward–save loop before multiplying content, then continue through the complete specified campaign. Do not cut mandatory content silently to meet an arbitrary session limit. Record a resumable state instead.

The first non-negotiable visual review is an actual town screenshot beside an actual battle screenshot. The first non-negotiable gameplay review is a fresh save that reaches and defeats B01 through the normal UI. The first narrative review checks whether the player understands why Dain disobeys before the supernatural twist arrives.


---

<!-- Source: docs/02_STORY_BIBLE.md -->

# Story bible — complete campaign outline

All names, dialogue and plot in this document are newly authored for this proposal. The numbering is editorial; CH17–19 are order-independent and CH21 is optional.

## History and causal rules

Three hundred and twelve years before the opening, a limited number of humans and dragons established voluntary shared-body arrangements to survive a regional magical disaster. These arrangements required continuing agreement and a way to separate. Later rulers engineered inheritable hosts, made separation unavailable, and treated the resulting people as infrastructure. A century before the opening, the final independent great dragons were broken into distributed consciousnesses and the industry described the surviving organs as inert fossils.

Heartglass organs relay pressure and memory. Dragonborn carry living fragments; both are required for large-scale extraction. Ordinary animals, technology and geography exist independently of dragons. The continent is not the body of an origin creature. This premise must not be merged with a different project’s world.

Rook’s forced synchronization tears apart the relay faults and overwhelms both hosts and fragments. Geography changes along those faults rather than by arbitrary magic. Local release works because it unlinks compulsion while substitute power and travel systems carry ordinary infrastructure. It is slower, requires participation, and was demonstrated before the catastrophe. The final plan scales a known solution; it does not invent a new crystal at the last minute.

## CH01 — The Orders We Carry

**Act 1; prerequisites:** New Game. **Status:** required.

Dain escorts a ministry inspection into Crown Quarry. The workers have been told that a delayed shift is sabotage; their lift is flooding while officials argue about who may stop production. Tessa, a detained relay apprentice, can hold one pump open but not both. Dain must learn movement, interaction, defending and magic while choosing the order in which to open rescue routes. Every worker is recoverable; there is no hidden timer or reward for abandoning people.

**Dramatic turn.** The extractor speaks Dain’s childhood nickname in a voice he has never heard. A guard calls the sound a pressure artifact. After the battle, the voice says only: “That is not a stone.” Dain refuses the restart order. Tessa takes the worker list, not the valuable heartglass. Mara brings the rescued crew out through the lift yard.

**Persistent result.** Extraction stops locally; Tessa joins; the ministry orders Dain back to Veyr. V01 becomes available through a small voluntary pact, not a loot drop.

## CH02 — Orders in Ashes

**Act 1; prerequisites:** CH01. **Status:** required.

Veyr celebrates the inspection as a successful reopening. Dain tries to correct the record and is arrested. Oriel, summoned to certify Tessa’s mental fitness, recognizes that the charge sheet was written before the inspection. She opens a service door but insists they take the records rather than simply flee. The escape introduces switches, readable patrol movement and a nonlethal visual presentation for human opponents.

**Dramatic turn.** In the ledger stacks, Dain finds living workers listed as expendable material. Oriel finds her own signature on an older authorization. Defeating the Brass Bailiff opens the canal; it does not burn down the entire capital or turn all guards into villains. Clerk Ansel quietly leaves the gate unlatched.

**Persistent result.** Oriel joins. The party becomes wanted. Its immediate objective is to find the transport origin recorded in the ledger.

## CH03 — A Road Without Banners

**Act 1; prerequisites:** CH02. **Status:** required.

Nera is guiding families around a closed military road. She initially refuses Dain because his unit escorted the convoys that displaced them. A damaged irrigation network is starving one camp and flooding another. The party repairs the route using visible sluices, learning that a convenient shortcut can shift danger onto somebody else.

**Dramatic turn.** The Rootbound Stag is attacking the valves because extraction residue is reaching its grove. Victory breaks a coercive growth seal. Nera agrees to guide the party after Dain helps move the camp without asking forgiveness in return. A quiet meal gives each current member a small scene rather than more exposition.

**Persistent result.** Nera joins, V02 becomes available, and the northern road to Cinder Reach opens.

## CH04 — The Walking Furnace

**Act 1; prerequisites:** CH03. **Status:** required.

Cinderwake is not a villain’s factory but a town that will freeze if its machines simply stop. Ivo shows the party a regulator that converts pressure into steadier power. Tessa recognizes it as the mechanism used to amplify the voices in the quarry. When a regulator walks out of its housing and begins destroying the workshop, the player must vent pressure away from occupied rooms.

**Dramatic turn.** Ivo admits the regulator is his design. His husband Pell asks him to solve the heating problem before becoming a traveling revolutionary. After the Colossus falls, the crew rigs a temporary waterwheel with the workers. The repair is imperfect and visibly limited. Ivo joins to learn what the heartglass actually contains.

**Persistent result.** The reserve-party UI opens. A shipping manifest points to Bellharbor. The temporary town supply remains in place after leaving.

## CH05 — Paper Ghosts

**Act 1; prerequisites:** CH04. **Status:** required.

Bellharbor’s officials are hunting a forger who has been turning refugees into cargo. Pip offers passage in exchange for recovering a confiscated ledger. This is a town infiltration sequence built from dialogue choices, route observation and one short chase with local retries; failure does not erase progress or cause a story dead end.

**Dramatic turn.** The ledger reveals that Pip marks people dead to get them through checkpoints. Jori, his brother, says the rescued families now cannot claim wages or housing. Pip laughs until one of those families asks which name they are allowed to use. He takes the party to the drowned archive to establish a record outside the ministry.

**Persistent result.** Pip joins. Shops, stealing and rumor tracking are fully introduced; no essential clue is locked behind a rare steal.

## CH06 — The Bell That Broke

**Act 1; prerequisites:** CH05. **Status:** required.

The archive holds contracts from before the kingdom consolidated the extraction industry. Three bell tones open testimony galleries. Elian Rook, a former ministry geologist, arrives with evidence that the “fossil” organs are still transmitting a distributed consciousness. He offers names, dates and physical records rather than demanding faith.

**Dramatic turn.** The Custodian tries to seal the archive against unauthorized readers. After the battle, Rook asks Dain to bring him to the last synchronization chamber. Dain agrees only to investigate. Rook conceals that he has already placed a second activation route. A bell rings above the water as the town preserves copies of the evidence.

**Persistent result.** V03 becomes available. Coastal ferry access opens the wider world; Rook is an uneasy ally, not a party member.

## CH07 — To Borrow Sky

**Act 2; prerequisites:** CH06. **Status:** required.

The route to the Pale Basin crosses the Skychain. Corren offers a dramatic solo leap to reset its anchors. Nera points out that there is room for an ordinary maintenance crew. The dungeon gives the player safe ballast controls and wind cues rather than asking for a mandatory precision platforming skill.

**Dramatic turn.** The Chain Roc has been tethered as a living stabilizer. Corren breaks the tether while the crew secures an alternate bridge, surviving the act he expected to turn into a memorial. He does not yet know how to accept an achievement that did not nearly kill him.

**Persistent result.** Corren joins; V04 becomes available. The cable ferry opens Nacre’s road. There is still no freely flying airship.

## CH08 — Traitor’s Edge

**Act 2; prerequisites:** CH07. **Status:** required.

Sable intercepts the party at Whitebone Redoubt and offers access to its prisoners in exchange for safe conduct. Dain distrusts her because she wrote the binding warrants. Oriel refuses a deal that merely replaces one group of prisoners with another. The party enters to obtain each captive’s actual release key, giving the names hall a practical role.

**Dramatic turn.** The Adjudicator attempts to transfer the ward to Dain. Sable destroys her officer’s seal rather than use it to control him. It is a useful act, not forgiveness. A freed prisoner tells her where to send her testimony. Sable joins with the explicit understanding that she will return to answer for what she did.

**Persistent result.** All eight playable characters are now known and recruited. Flexible party formation opens at safe points.

## CH09 — A Voice with My Hands

**Act 2; prerequisites:** CH08. **Status:** required.

The Memory Vault separates three histories: an ancient voluntary shared-body pact; its industrial standardization; and the later confinement of dragon consciousness across engineered lineages. Dragonborn are people, not counterfeit descendants waiting to be replaced. Dain can decline an invasive memory projection; documentary evidence supplies the same required information.

**Dramatic turn.** The Pale Choir tries to impose one agreed history on contradictory accounts. The battle breaks that forced synchronization. Ilyr, the fragment in Dain, first asks to use Dain’s body to rebuild his own. Dain answers that wanting freedom does not make another body empty. Ilyr agrees to speak without taking control, a limited first accord.

**Persistent result.** V05 becomes available. The party learns that heartglass organs are relays and dragonborn are living memory nodes. Rook’s promised awakening would affect both.

## CH10 — The Smaller Accord

**Act 2; prerequisites:** CH09. **Status:** required.

The party returns evidence to three communities. Each wants a different immediate guarantee: Cinderwake needs heat, High Aerie needs stable transit, and Nacre needs a way to separate consent from institutional pressure. These are compact authored conversations with one local intervention each, not three identical crystal fetch quests.

**Dramatic turn.** Ivo and Oriel demonstrate a slow, local release that keeps one relay alive without coercion. It works, but needs coordinated labor and time. Rook calls it an intolerable delay while the extraction continues. Tessa almost agrees with him before a volunteer describes the cost of being forced to be rescued.

**Persistent result.** The peaceful method is established before the finale. Rook departs for the Conduit; the party follows to prevent a mass forced awakening.

## CH11 — Below the Coronation

**Act 2; prerequisites:** CH10. **Status:** required.

Voss is preparing to capture the network and replace unstable individual relays with one central authority. The party reroutes occupied lifts and disables the visible synchronization lines. A clear warning marks the last freely explorable pre-catastrophe moment; the game writes a separate protected transition backup without overwriting manual saves.

**Dramatic turn.** Voss fights on the Marshal Bridge using commands that turn party protection against itself. He retreats into the central apparatus when defeated. The party wins this encounter normally. The evacuation actions determine practical aftermath details, not whether the predetermined catastrophe happens.

**Persistent result.** B09 is defeated. The party reaches Rook on the Crown Dais; quitting here resumes before the next scene, not in a half-transformed world.

## CH12 — Crown of Cinders

**Act 2; prerequisites:** CH11. **Status:** required.

Rook insists that a century of exploitation cannot be repaired one volunteer at a time. The party defeats him and disconnects the Crown Dais. His hidden synchronization route, previously foreshadowed through mismatched diagrams and a missing relay on Ivo’s plan, completes the activation anyway. The game does not fake a winnable boss or ask for an impossible final input.

**Dramatic turn.** Ilyr refuses Rook’s order to overwrite Dain. Oriel breaks the common command channel while Ivo diverts power to the evacuation lifts. These actions reduce the disaster but cannot undo it. Coastlines fracture along old relay faults, dormant dragon structures rise, and the party is scattered. The escape is an authored sequence with local retries, followed by silence rather than a victory fanfare.

**Persistent result.** World phase changes atomically to post. Dain and Oriel reach Hearthward. Inventory, levels, equipment ownership, opened chests and completed quests survive; unavailable allies retain their own gear.

## CH13 — After the Bell

**Act 3; prerequisites:** CH12. **Status:** required.

Dain wakes in a refugee harbor assembled from cargo pontoons. Oriel is treating exhaustion with ordinary care; her visions are fragmented and unreliable. The player helps distribute lamp fuel, repairs a simple path and hears concrete news of the missing companions. This is a playable recovery scene, not a long cinematic that withholds control.

**Dramatic turn.** Dain asks whether the world would be safer without him. Oriel refuses the premise that his body is a public utility. Ilyr admits that he heard other fragments take their hosts’ voices during the activation. Their shared objective becomes freeing both groups without making either disposable.

**Persistent result.** Hearthward services open immediately. A supplies chest guarantees a viable two-person recovery party. Nera’s signal is the next clear lead.

## CH14 — Roads Grow Teeth

**Act 3; prerequisites:** CH13. **Status:** required.

Nera is guiding survivors across the flooded Rootward. Her old maps are useful but incomplete. The player reconnects visible safe routes and defeats the Ash-Tide Warden that is diverting the current. No random terrain generation is allowed to make the rescue route unreachable.

**Dramatic turn.** Nera tries to keep the only good map to ensure nobody takes a dangerous path. Mara points out that nobody can wait for one guide forever. Nera gives copies to the camp and rejoins the crew, beginning rather than completing her personal resolution.

**Persistent result.** Nera returns. Brackenford’s new routes and salvage service activate. Bellharbor is reachable by a repaired ferry.

## CH15 — Light in the Flood

**Act 3; prerequisites:** CH14. **Status:** required.

Tessa is holding an improvised barrier over a flooded gallery. She believes lowering it means admitting failure. The party clears the upper route, moves the residents, and then lets her release the spell. Her rescue is a puzzle and dialogue encounter, not another large boss that interrupts the recovery rhythm.

**Dramatic turn.** For the first time she watches other people solve a problem while she rests. The lights go out; the evacuees turn on ordinary lanterns. Tessa joins the party and asks Ivo to show her a machine that works without a person pretending to be its fuel.

**Persistent result.** A balanced four-person party is restored. Tessa returns at her stored level or the reunion floor, whichever is higher. Cinderwake is the next direct route.

## CH16 — The Engine That Waited

**Act 3; prerequisites:** CH15. **Status:** required.

Ivo has found an unfinished rescue vessel, Wayfarer, designed before heartglass made efficiency politically irresistible. Its engine is heavier and slower, but its parts can be repaired. The party powers the old cooling channels, clears the assembly space and obtains the Iron Tortoise’s voluntary help stabilizing the hull.

**Dramatic turn.** Pell asks Ivo to leave a complete maintenance manual before he takes the ship. The manual becomes a visible object on the workshop bench. At the launch, the camera shows workers performing the procedure rather than Ivo making a last-second heroic adjustment.

**Persistent result.** Ivo returns; V06 is obtained; unrestricted airship travel over reachable post-state regions opens. CH17, CH18 and CH19 may now be completed in any order.

## CH17 — Wings Without Chains

**Act 3; prerequisites:** CH16. **Status:** required.

Corren is holding a damaged mooring while another crew tries to evacuate a cliff settlement. His proposed solution is to cut himself loose with the load. The player instead installs three reachable ballast anchors, using the dungeon’s earlier rules in a changed topology. There is no hidden countdown forcing a sacrifice.

**Dramatic turn.** Corren must step away from the last lever and trust somebody else to hold it. Captain Edda refuses to put his name on the memorial and offers him a shift on the rescue roster instead. He returns to the airship without a grand speech.

**Persistent result.** Corren rejoins. Skyspine’s anchor becomes available for the final release protocol. Order-independent conversations acknowledge which other companions have returned.

## CH18 — Names for the Living

**Act 3; prerequisites:** CH16. **Status:** required.

Pip has been protecting the lower registry from Voss’s remnants. Refugees need it intact to recover their identities, but it also contains the evidence of his forgeries. The party retrieves the original ledgers through changed canal routes and lets the residents, not Pip, choose how to record their names.

**Dramatic turn.** Jori returns the satchel Pip used to carry false papers. It now holds blank forms and a proper seal issued by the refugee assembly. Pip joins with no claim that good intentions erased the harm; his full restitution remains an optional personal quest.

**Persistent result.** Pip rejoins. The capital’s distribution point opens, and the optional Regent’s Echo lead becomes visible after the Ash Accord.

## CH19 — The Hand That Wrote the Seal

**Act 3; prerequisites:** CH16. **Status:** required.

Sable is sheltering people whose bindings she cannot safely remove alone. She has already submitted her name and testimony to Nacre. The party opens the cells one by one using their established consent-key rules, without requiring Sable to remain in the active combat party for a movement ability.

**Dramatic turn.** A survivor refuses to thank Sable. The scene lets that refusal stand. Sable asks whether she can help prevent Voss from restoring the network before returning to face the hearing. The survivors grant a limited agreement and keep a copy of her account.

**Persistent result.** Sable rejoins. All eight core characters are required to enter the finale, but their optional personal resolution quests are not.

## CH20 — The Ash Accord

**Act 4; prerequisites:** CH17, CH18, CH19. **Status:** required.

The communities compare the local release procedures established in CH10 with what they learned during the reunions. Ivo supplies a distributed power circuit, Oriel supplies a consent check, and the returned companions supply working regional anchors. The game does not add three new ingredients after the player has already solved the regional problems.

**Dramatic turn.** Rook arrives alive under escort. He provides the hidden route diagrams and admits that his activation imposed freedom as a command. He does not join the party, receive instant forgiveness or die conveniently before answering for the catastrophe. The assembly records both extraction and awakening as harms that require accountability.

**Persistent result.** The Ash Accord is completed. All personal quests and four optional boss quests are now clearly discoverable. The final route opens without demanding 100% optional completion.

## CH21 — An Honest Kind of Power

**Act 4; prerequisites:** CH20. **Status:** optional preparation window.

This chapter is an optional preparation window rather than a mandatory checklist. The ship’s crew room contains specific rumors pointing to the eight personal quests, the winter island, the starless reef, the capital echo and the silent singer. Every lead has an in-world source and a journal entry; no giant checklist obscures the world map.

**Dramatic turn.** Completing each personal quest gives its character an ultimate weapon and final technique, and adds a scene to the ending. The base ending still resolves the main conflict when none are completed. Dain’s personal quest is optional too; the essential body-consent decision was already made in the main story.

**Persistent result.** CH21 may be skipped entirely. The player can prepare, explore or leave for Crown Heart directly from CH20.

## CH22 — A Gate with Two Keys

**Act 4; prerequisites:** CH20. **Status:** required.

Wayfarer docks at Crown Heart. The player splits all eight heroes into two teams of four. The west route releases physical pressure while the east route removes the name-binding circuit. Both teams use the same inventory and progression rules; a formation safety check supplies guidance and a shared recovery point without requiring particular characters on either route.

**Dramatic turn.** Voss has fused himself with the Crown Vessel to turn every interrupted relay into a single obedient network. Three telegraphed phases re-examine protection, coercion and shared action. The allies and communities perform the prepared release procedure while the party defeats the apparatus. Ilyr is offered a separate restored form; he chooses to remain with Dain for now because their agreement, unlike the old prison, can be ended by either of them.

**Persistent result.** The network loses the ability to compel dragonborn or dragon fragments. Cities keep their altered geography; extraction cannot simply restart. The victory is practical and incomplete in the world, but the game’s central conflict is resolved.

## CH23 — Let the Names Remain

**Act 4; prerequisites:** CH22. **Status:** required.

The player walks through Hearthward after the victory. People use the restored records, the distributed engine and the returned rescue routes. Rook’s hearing and Sable’s promised appearance proceed; the ending does not equate accountability with a spectacle of punishment. Families remember those lost regardless of how many optional quests were completed.

**Dramatic turn.** Each character receives a base epilogue and an enhanced one when their personal quest is finished. The additional scenes deepen the result rather than reveal that the ordinary ending was secretly false. Dain leaves his crown badge at a public memorial, then takes a maintenance shift aboard Wayfarer.

**Persistent result.** A clear-save record is written separately from the protected pre-finale save. The player can finish the epilogue or return later without replaying the final boss.

## CH24 — The First Unborrowed Morning

**Act 4; prerequisites:** CH23. **Status:** required.

Dawn reaches the rebuilt harbor. A lamp fails; two ordinary workers replace its part without calling for a chosen savior. Dain and Ilyr hear the same bell and name it differently. The last playable interaction is to step aboard the ship, not to choose which species deserves to exist.

**Dramatic turn.** The title theme returns with its unresolved suspension finally completed. Credits include original-asset provenance and third-party notices. A post-credits image shows an unlit relay being repurposed as a public garden, with no new villain teaser required to understand the ending.

**Persistent result.** Credits lead to Continue from Before the Final Descent or Title. Post-clear exploration uses the pre-finale world snapshot plus clear and personal-quest flags; it is explicitly not a fully simulated post-ending campaign.

## Foreshadowing and payoff ledger

| Setup | Payoff | Guardrail |
| --- | --- | --- |
| CH01 extractor knows a private nickname | CH09 living-node revelation | Never claim it proves Dain lacks a real childhood. |
| CH02 orders predate the inspection | CH11 Voss consolidates control | Give the player physical records, not only a villain’s speech. |
| CH04 Ivo’s regulator stabilizes voices | CH12 secondary route bypasses the visible relays | Include a mismatched diagram in CH06 and a missing relay in CH10. |
| CH07 Corren expects to die fixing a problem | CH17 collective rescue; Q03 testimony | Survival is an achieved alternative, not a reversal of a fake death. |
| CH09 voluntary pact has a separation rule | CH22 Ilyr declines immediate separation | Both keep the right to change their agreement later. |
| CH10 local release works but needs labor | CH20 shared protocol; CH22 execution | The ending does not discover a new magical resource. |
| CH05 false death records save refugees | CH18/Q08 identity restoration | A rescued person may reject the name Pip assigned. |

## Scene-writing rules

Write each important scene with an entry condition, actor list, staging, exact dialogue, committed state changes and a skip/resume boundary. A skipped scene must produce exactly the same state as the watched scene. Do not hide unique items or romance points in dialogue tone choices. Choices may change phrasing and later acknowledgement without fabricating a different campaign.

The protagonist cannot react to information from a chapter the player has not completed. Reserve members may appear in major scenes even when not active in combat. After the catastrophe, absent companions cannot speak on the ship before being recovered. CH17–19 need present/absent variants or a narrator-neutral staging; they must never assume a particular reunion order.

Avoid an uninterrupted lore lecture longer than twelve short text boxes. Use a document, a physical action, a disagreement or a return to movement. Do not apply this as a reason to delete necessary information: break the scene into playable pieces.


---

<!-- Source: docs/03_CHARACTER_BIBLE.md -->

# Character bible

Eight playable characters; all are required before the two-party finale. Personal quests remain optional. Ages and appearances are new draft decisions, not recovered user biography.

## C01 — Dain Ashward

**Identity:** 34, dragonborn man. **Role:** Oath knight. **First joins:** CH01; **returns:** CH13.

A crown soldier who mistakes obedience for keeping people safe.

**What they actually did:** He helped escort forced labor convoys and cannot undo that by discovering he was also used.

**Arc:** Choose obligations openly; share his body with Ilyr by agreement rather than domination.

**Visual direction:** Broad shoulders, crimson scales, charcoal segmented armor, one unpainted gauntlet; no resemblance to an existing game hero.

**Voice direction:** Short concrete sentences; notices doors, loads and exits before feelings.

**Mechanical identity:** Oath of Shelter; Shieldbreak; Oath of Wrath; Cinderedge; Oath of Sacrifice; Rally; Oath of Witness; Open Hand.

**Personal resolution:** Q01; weapon W006. Do not give the ultimate merely for rejoining.

## C02 — Tessa Vale

**Identity:** 22, human woman. **Role:** Overcast mage. **First joins:** CH01; **returns:** CH15.

A brilliant fugitive who treats every warning as an attempt to control her.

**What they actually did:** Her demonstration overloaded a public relay; admitting it does not validate the regime that exploited her.

**Arc:** Use restraint as an active skill, not surrender; teach safe magic without making herself indispensable.

**Visual direction:** Short dark hair, amber spectacles pushed onto forehead, cobalt coat, red mitten on casting hand.

**Voice direction:** Fast analogies, then sudden blunt honesty when frightened.

**Mechanical identity:** Ember Lance; Rime Needle; Storm Arc; Stone Seal; Overcast; Black Sun; Heat Exchange; Ash Without Fire.

**Personal resolution:** Q02; weapon W012. Do not give the ultimate merely for rejoining.

## C03 — Corren Hale

**Identity:** 31, human man. **Role:** Dragoon. **First joins:** CH07; **returns:** CH17.

A celebrated aerial guard trained to make dying look noble.

**What they actually did:** He cut a rescue cable on command and has accepted praise for the wrong reason.

**Arc:** Return, testify, and build rescue procedures that do not need martyrs.

**Visual direction:** Long ochre scarf with weighted ends, narrow teal breastplate, weathered flight harness.

**Voice direction:** Formal in public; dry, practical humor with the crew.

**Mechanical identity:** Updraft; Harrow Dive; Anchorfall; Skypiercer; Feather Guard; Storm Vault; Wingbeat; Unbound Descent.

**Personal resolution:** Q03; weapon W018. Do not give the ultimate merely for rejoining.

## C04 — Ivo Quill

**Identity:** 49, human man. **Role:** Machinist. **First joins:** CH04; **returns:** CH16.

A maintenance engineer who believes a functioning machine justifies its compromises.

**What they actually did:** He designed the pressure regulator that made heartglass extraction scalable.

**Arc:** Build distributed power that can be maintained by ordinary crews; publish what he knows.

**Visual direction:** Gray curls, rolled sleeves, copper tool rig, ink-dark apron; stocky silhouette.

**Voice direction:** Explains emotions through repair problems until challenged to name them directly.

**Mechanical identity:** Rivet Shot; Field Patch; Grounding Rod; Steam Screen; Clock Mine; Pressure Vent; Decoy Frame; Unborrowed Engine.

**Personal resolution:** Q04; weapon W024. Do not give the ultimate merely for rejoining.

## C05 — Nera Fen

**Identity:** 29, human woman. **Role:** Ranger. **First joins:** CH03; **returns:** CH14.

A displaced guide who trusts routes more than institutions.

**What they actually did:** She once traded another settlement’s safe path for supplies for her own people.

**Arc:** Share knowledge without becoming everyone’s sole gatekeeper.

**Visual direction:** Moss-green cape split at the shoulders, long braid, cream fletching, worn map tube.

**Voice direction:** Precise about places; refuses vague claims about what everyone needs.

**Mechanical identity:** Hunter’s Mark; Split Arrow; Snare; Bramble Ward; Scent Trail; Exposed Thread; True North; Many Paths.

**Personal resolution:** Q05; weapon W030. Do not give the ultimate merely for rejoining.

## C06 — Sister Oriel

**Identity:** 42, human woman. **Role:** Oracle. **First joins:** CH02; **returns:** CH13.

A healer whose institution confused probabilistic visions with divine authority.

**What they actually did:** She signed a prognosis that made a living dragonborn legally disposable.

**Arc:** Offer information without deciding another person’s life for them.

**Visual direction:** Ivory traveling stole, plum dress, brass bell without a clapper, close-cropped silver hair.

**Voice direction:** Patient, never omniscient; says what she does not know.

**Mechanical identity:** Mend; Cleanse; Sunthread; Last Light; Omen; Intercede; Stillwater; Borrowed Dawn.

**Personal resolution:** Q06; weapon W036. Do not give the ultimate merely for rejoining.

## C07 — Sable Renn

**Identity:** 36, human woman. **Role:** Spellblade. **First joins:** CH08; **returns:** CH19.

A former binding officer who wants one heroic act to cancel her record.

**What they actually did:** She personally authored the seals used on dragonborn prisoners.

**Arc:** Help dismantle her work and accept testimony, restitution, and consequences.

**Visual direction:** Black-violet coat, exposed scarred forearm, straight white blade with broken runes.

**Voice direction:** Controlled legal language that gradually becomes personal and specific.

**Mechanical identity:** Infuse Ember; Infuse Rime; Infuse Storm; Unseal; Mirror Cut; Sever Rune; Runic Shelter; Unwritten Law.

**Personal resolution:** Q07; weapon W042. Do not give the ultimate merely for rejoining.

## C08 — Pip Marr

**Identity:** 27, human man. **Role:** Rogue. **First joins:** CH05; **returns:** CH18.

A forger who saves people by making the authorities believe they are dead.

**What they actually did:** His forged registers also erased people’s legal claims to homes and wages.

**Arc:** Return names and agency instead of keeping everyone dependent on his tricks.

**Visual direction:** Rust waistcoat, green sash, cropped brown curls, satchel larger than his weapon.

**Voice direction:** Makes jokes to redirect attention; never jokes over a victim’s account.

**Mechanical identity:** Pilfer; Feint; Smoke; Quick Hands; Tripwire; Disarm; Rescue Line; False Crown.

**Personal resolution:** Q08; weapon W048. Do not give the ultimate merely for rejoining.

## Relationships that carry scenes

Dain and Oriel initially provide each other with institutional permission. Their later scenes remove that dependence: neither is the other’s moral certificate. Tessa and Ivo disagree about whether a dangerous technique should be used before it is understood; both have caused damage through confidence. Corren and Nera argue about risk because he was rewarded for taking it and she was left to guide people around its consequences. Sable and Pip both altered records, but from opposite positions of power; their dialogue must not collapse that difference into “everyone lies.”

Give each pair a ship conversation before and after its relevant personal quest. Do not lock useful healing or progression behind these conversations. Their purpose is characterization, not affection grinding. Twelve substantial pair conversations and short condition-aware arrival lines are sufficient for this scope.

## Antagonists and recurring figures

**Marshal Garran Voss:** an administrator who believes a centralized coercive network is preferable to an unstable society. He is not secretly possessed and does not become innocent when a machine is destroyed. He makes choices, knows their cost and tries to preserve his authority through the Crown Vessel. His human fight and final form belong to the same antagonist arc.

**Elian Rook:** a former geologist who establishes the truth about extraction. He correctly identifies ongoing harm, then decides that the victims’ consent can be postponed until after he frees them. His hidden secondary route must be foreshadowed. He is defeated at the midpoint, survives, provides necessary evidence later, and remains accountable after the ending. Do not replace this arc with a sacrificial death that avoids consequences.

**Ilyr:** the dragon fragment sharing Dain’s body. He has memories and needs, not a complete guide to the game’s plot. He begins by regarding the host as a way back to a body and learns to negotiate. His changing attitude is not a generic possession meter. There is no ending that rewards deleting Dain or enslaving Ilyr.

**Mara Pell:** quarry forewoman and later Hearthward organizer. No relation to Pell Quill. Names and work matter to her more than titles. **Pell Quill:** Ivo’s husband, a workshop organizer; he pushes for durable repairs rather than celebrating Ivo’s departure. **Jori Marr:** Pip’s brother, a clerk in practice before he has an official position. **Captain Edda Hale:** Corren’s older sister and supervisor, not an infallible judge. **Archivist Sen:** a Nacre resident who preserves disagreement in records. **Clerk Ansel:** a minor official who makes one useful, risky choice without becoming a secretly powerful ninth hero.

## Base and enhanced epilogues

Every character receives a complete base scene. Dain works aboard Wayfarer under his own name; Tessa helps maintain the harbor lamps; Corren flies rescue routes; Ivo supervises a transition workshop; Nera maps reopened crossings; Oriel practices at the listening house; Sable attends her hearing; Pip restores the registry. Each completed personal quest adds its specific public change, a relationship payoff and a variation of the character motif. Do not label the ordinary ending “bad” because optional quests were skipped.


---

<!-- Source: docs/04_WORLD_BIBLE.md -->

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


---

<!-- Source: docs/05_DUNGEON_BIBLE.md -->

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


---

<!-- Source: docs/06_COMBAT_SPECIFICATION.md -->

# Combat specification

## Battle contract

Use a side-view, four-character active party with visible readiness gauges. Combat is an authored deterministic simulation with a presentation layer, not damage implemented directly inside animation callbacks. The default is Wait mode; Active mode is an optional setting. Both use exactly the same actions, enemy intents, costs and damage rules. No competitive fairness or internet clock is needed.

Every battler has a stable encounter-local ID, current/max HP and MP, derived stats, readiness, action state, statuses, row, affinities and an immutable content definition reference. Encounter state owns RNG streams, enemy spawns, rewards, flee progress, Concord and once-per-battle flags. UI widgets hold no authoritative HP or inventory counts.

## Readiness and action states

Simulation runs at a fixed 60 Hz with an accumulated fixed-point gauge. Gauge range is 0–1000. Fill rate per simulation second is `100 + 5 × clamp(SPD, 1, 99)`, modified by Haste/Slow and a user battle-speed factor of 0.75, 1.0 or 1.25. Clamp readiness to 1000; never create multiple turns from overflow.

Actor states are FILLING, READY, SELECTING, COMMITTED, CASTING, RESOLVING, RECOVERING and KO, with AIRBORNE as an explicit temporary state for leap skills. Only FILLING advances readiness. Committed actions do not keep charging. A successful resolution resets readiness to zero, then applies explicit refunds bounded to 500 unless the action specification says otherwise. A canceled selection consumes nothing. Queue ties resolve by ready tick, then stable battler ID. Do not sort by the order nodes happen to appear in the scene tree.

Wait mode pauses readiness, cast timers, leap timers and scheduled battle timers while any player command/target menu is open. Cosmetic animation and menu movement continue. Active mode keeps simulation timers advancing during ordinary command selection. The full pause menu, loss of application focus under the default setting, and a modal accessibility/help screen pause both modes. During an action’s presentation lock, simulation does not advance until the authoritative action has been presented; skipping the animation shortens wall-clock presentation, not the action’s simulated power or timing.

## Commit, validation and resource use

Selection creates a proposed command; commit validates actor life, learned/granted ability, target eligibility, silence, MP, item availability and once-per-battle rules. Reserve costs at commit. At resolution, revalidate target existence and life. Offensive single-target actions retarget the lowest stable ID living eligible enemy if the original target fell. Healing retargets the lowest HP-percentage living eligible ally. Revive cancels with a full cost refund when no eligible fallen ally remains. An actor KO before resolution loses the turn but receives reserved MP/item costs back. Once-per-battle flags are consumed only by a valid resolution; the exception is a prevented crash replay, which must replay the already committed transaction exactly once.

Never subtract an item on button press and again on animation completion. Costs are an idempotent transaction keyed to the committed action. The command log records the selected target and any lawful retarget so a failed replay is diagnosable.

## Base commands

Attack uses the current weapon and 100 physical power. Defend consumes an action and reduces direct damage by 50% until the actor’s next resolved action, including the next command’s casting interval. Item uses one shared inventory item through the same transaction path as abilities. Row changes consume an action in battle and are free at safe formation screens. Escape accumulates a shared flee meter in normal encounters: each completed Escape action adds 250, plus any explicitly permitted skill/item bonus, and succeeds at 1000. Bosses visibly disable Escape before item consumption. No random flee failure can repeatedly waste ten turns.

Each character exposes Attack, their role command, Item and Defend; equipped accessory magic and linked summons appear as optional subcommands. Show unavailable commands with a specific reason rather than silently removing them. Use a remembered cursor per character, but never automatically reuse an invalid target or spend a rare item after the encounter changes.

## Damage, healing and affinities

All following constants are initial tuning values, not verified balance. Round only at the final result except where a cost explicitly says round up.

Physical raw damage = `(2 × ATK + 3 × level) × power / 100`.
Magical raw damage = `(2 × MAG + 3 × level) × power / 100`.
Defense multiplier = `100 / (100 + max(0, effective DEF or RES))`.
Healing = `(2 × MAG + 2 × level) × power / 100 + 0.06 × target max HP`.

For damage, apply defense, elemental affinity, row/range, guard and status modifiers, a seeded variance in [0.95, 1.05], and critical factor when eligible; floor once. Damage that is not explicitly immune is at least 1. Healing is at least 1 and capped by missing HP. Healing does not crit. Standard physical critical chance is 5%, capped at 35%, with multiplier 1.5. Standard physical accuracy is 95% before modifiers; spells default to 100% unless explicitly specified. Show MISS, RESIST, IMMUNE and damage as distinct outcomes.

Affinities are weak x1.5, neutral x1.0, resistant x0.5, immune x0.0 and absorb as a separately tagged conversion to healing. Do not encode absorb with negative damage. Resist and weakness do not multiply repeatedly when two items grant the same affinity; use the strongest applicable final category. Elements are physical, fire, ice, storm, earth, water, light, shadow and none. “Phase-specific” is a boss design instruction; the importer must expand it to concrete phase affinities before runtime.

Back-row actors receive half melee physical damage and deal half melee physical damage. Ranged weapons and ranged skills ignore the outgoing row penalty. Magic ignores rows. Incoming ranged physical damage ignores the defensive row reduction. Combine ordinary reduction sources multiplicatively but cap total direct-damage reduction at 80%, excluding an explicit immunity. This prevents an oath, Defend, accessory and Barrier from creating accidental permanent invulnerability.

A level/stat formula must be shared by runtime and preview UI. A test implementation must call the actual runtime formula, not maintain a second conveniently different model.

## Status engine

Use the sixteen status records in `data/statuses.json`. Reapplication refreshes to the larger remaining duration; it does not stack magnitudes. Haste and Slow replace one another. At an actor’s action opportunity, process hard-control skipping consistently; a skipped action consumes the relevant status duration so Stun cannot preserve itself forever. After an actual resolved action, process damage-over-time/healing-over-time, decrement action-based durations, then evaluate KO. Repeated source hits in one action count as one status duration event.

Bosses are immune to Sleep, Stun and Doom unless a named encounter explicitly replaces immunity with a bounded response. Boss Slow is weaker and total ATB delay is capped at 200 between boss actions. Every boss has at least one counter available through generic Attack, Defend or guaranteed consumables. No particular active-party member is a mandatory puzzle key inside a boss battle.

Outside battle, statuses clear except KO; exploration is not a poison-step punishment system. Story seals are progression conditions, not ordinary dispellable combat statuses. Do not let Unwritten Law delete a story gate because both use the word “seal.”

## Character-specific state

Oaths are mutually exclusive Dain-only battle stances; change costs an action. Overcast is one armed spell, nonrandom and nonlethal in self-damage. Corren’s airborne absence advances through simulation time and cannot softlock when all other allies fall. An all-airborne living party is not a defeat. Ivo has one mine per enemy and one team decoy. Nera reveals data and marks targets but does not multiply every mark bonus indefinitely. Oriel exposes already committed intents, not future random draws. Sable has one infusion. Pip’s steal limits are per enemy instance and battle rewards are reconciled once.

A single source action may produce one counter, one interception and its documented triggered effect per eligible recipient. Triggered attacks cannot trigger another counter or reflection. Every reactive effect carries an origin action ID and a recursion depth limit. Test simultaneous damage to a protected ally, Dain’s lethal threshold, and enemy death during a counter.

## Vestiges and Concord

Each character may link one owned Vestige outside battle; a Vestige cannot be linked to two characters simultaneously. Linking does not permanently alter level-up stats. Concord is shared, ranges 0–100, starts at 0 each battle, and is reset on ending the encounter. A successful eligible player action gains 6 Concord, with accessory bonuses capped so a single action can grant at most 10. Defend grants 3 once per completed readiness cycle. Item grants 0 except a Concord Seed. Multi-hit and area attacks count as one action. Summons grant no Concord and each Vestige may be summoned once per battle at a cost of 100.

Silence blocks summoning. A dead or unavailable linked character cannot use its Vestige, but links can be reassigned at the next safe screen. No mandatory overworld route needs a specific summon equipped. Summon animations have normal, short and reduced-flash variants, all resolving the same effects.

## Rewards, defeat and retry

Resolve KO and simultaneous reactions before determining the result. If all living/airborne player actors are gone, defeat takes precedence over a simultaneous enemy wipe. Victory grants XP, gold, drops and unique acquisition IDs in one transaction. It then clears temporary battle statuses and restores exploration at a valid location. Fallen characters remain KO until revived or recovered at a safe service; give a clear prompt if the leader changes.

A defeat offers Retry from Checkpoint and Load Save. Retry restores the checkpoint snapshot, seed and resources; it neither keeps stolen loot nor consumes the supplies from the failed attempt. The player may change formation at the retry preparation screen. Defeat does not quietly advance story flags, create another boss reward, or erase a manual save.


---

<!-- Source: docs/07_PROGRESSION_ECONOMY_UI.md -->

# Progression, economy, menus and accessibility

## Level growth

Level cap is 50. The critical path is initially aimed at the mid-30s through low-40s for the finale, not mandatory level 50. XP needed to move from level L to L+1 is `30 + 12L + 3L²`; these seed values require a full-campaign economy pass. Ordinary enemy XP is in the catalog. Boss XP should initially equal six ordinary encounters at its intended level, then be adjusted with measured pacing.

Each recruited character receives 100% battle XP whether active, in reserve or temporarily unavailable after the catastrophe. Do not divide XP by the number of members. An initial recruit or returning character uses the greater of their stored level and the median level of the currently available party minus one. Apply only missing earned level growth, never repeated growth each time a scene loads. A first recruit has their guaranteed starter weapon and ordinary initial equipment; a reunion retains existing inventory and does not grant those items a second time.

For initial growth, let `n = level − 1`. HP is `hp1 + hp_growth × n + floor(0.65 × n²)` where hp_growth by C01–C08 is 54, 40, 49, 51, 45, 42, 48, 43. MP is `mp1 + mp_growth × n` with growth 3, 6, 3, 4, 3, 6, 4, 3. STR/MAG growth by character is C01 2/1, C02 1/2, C03 2/1, C04 1/2, C05 2/1, C06 1/2, C07 2/2, C08 2/1. DEF and RES gain 1 per level; SPD gains 1 each four levels. Use fixed rounding and equipment modifiers after base growth. Changing equipment must not trigger level growth again.

Each character has seven level-granted signature techniques plus one personal-quest technique. The JSON lists unlock levels. Characters keep their roles: there is no universal spell-learning tree that makes every party member interchangeable. Eight accessory spells offer limited cross-role support while equipped. Do not let removing and re-equipping an accessory permanently teach its spell.

## Equipment

Slots: weapon, offhand, head, body, accessory 1 and accessory 2. A two-handed weapon empties/disables offhand, returning the item to inventory if necessary. Inspect allowed-character IDs, not only a generic role label. Equipment changes are available outside battle or in designated preparation screens. Preview all derived stats and newly granted commands before confirmation.

Each character has six named weapons. Tier 1 is guaranteed at first recruitment and remains purchasable. Tiers 2–5 unlock at CH04, CH08, CH16 and CH20; all open town weapon vendors expose the unlocked shared tier stock. Town presentation and flavor differ, but a lost town cannot block the only useful spear. Tier 6 comes from the corresponding personal quest and is not sellable.

Armor/head/offhand catalog tiers 1–4 unlock at CH01, CH06, CH16 and CH20. Any open general-equipment shop can supply the unlocked tier. First/reunion loadout rules prevent an absent ally from being naked when called into the two-party finale. Post-catastrophe salvage forwards unique rewards from inaccessible maps based on acquisition IDs. Common consumables are not forwarded repeatedly.

## Economy

Use one currency, crowns, with an integer balance and a high safe cap. The name is setting vocabulary, not a second progression resource. All basic shops sell Tonic, Ether, Phoenix Leaf and status remedies from the beginning; the expanded stock opens at CH08. Start with 300 crowns, six Tonics, two Ethers, two Phoenix Leaves and one of each elemental flask needed for the first boss tutorial. Place a free full-recovery point before each mandatory boss.

Inns cost 25 crowns per recruited character, capped at 150. Hearthward’s communal recovery is always free. On the overworld, a Travel Tent restores the available party at a safe location. There is no hard requirement to buy a premium item before progressing. Gold rewards, prices, MP use and chest supply must be playtested together, not balanced in isolation.

Inventory stacks cap at 99. Purchases check total price and remaining capacity before spending. A unique quest reward that would overflow inventory enters a stable delivery chest and appears in the journal; it is never discarded. Consumable overflow converts to a visible bounded gold amount only after notifying the player. Never convert unique equipment or key items automatically. Selling equipment checks that it is not equipped, quest-protected or required by an active transaction.

## Encounter pacing

Use an exploration encounter meter on eligible terrain, with a minimum safe travel period after entering a map or finishing a battle. Default initial target is one encounter per 18–30 seconds of actual eligible walking, tuned by room size and progress. Menus, dialogue, blocked movement, room loading and cutscenes do not advance it. Running may increase distance but should not double annoyance by adding a second timer. Suppress normal encounters near save points, puzzles being operated and story conversations.

Provide an encounter-frequency accessibility option of Normal, Reduced and Off for ordinary random encounters. Scripted story encounters and bosses remain. Off must not strand the player below required levels: use transparent story-milestone XP grants or a clearly offered training service when enabled, and record this setting in the save. Do not secretly scale every enemy to the player and erase progression.

## Menus

Title: New Game, Continue, Load, Settings, Credits, Quit. Continue identifies slot, chapter, location, playtime and save date, not an ambiguous “latest” thumbnail. In-game: Items, Equipment, Abilities, Formation, Vestiges, Journal, World Map, Bestiary, Settings, Save when allowed. Show active and reserve party members, KO state, unavailable-story state and the reason equipment cannot be changed.

The journal records current objective, last clue, known destination and who supplied it. Completed quests keep their story summary. Optional rumors remain distinct from mandatory objectives. The world map supports named discovered locations, landing markers and optional guidance; it does not reveal every secret from the start.

Use persistent keyboard/gamepad navigation, remapping, focus highlight, confirm/cancel consistency, and a confirmation for destructive save overwrite. Mouse is optional, not required. No pixel hunting for a one-pixel menu button. Show elemental affinities with symbols and labels, not color alone.

## Accessibility

Wait mode defaults on. Offer text speed, instant text, hold/toggle run, reduced flashes, zero screen shake, shortened summons, volume buses and encounter frequency. Keep a readable high-contrast font; use an original or appropriately licensed font but do not bundle a font without documented permission. Larger UI uses alternative panel layouts and reflow, not merely cropping a scaled menu. At 320×240, text should generally use an 8–10 pixel readable bitmap body with tested line length; use a higher-resolution UI layer only as an explicit alternative style with visual review, not a silent pixel-density mismatch.

Important choices and cutscenes pause until confirmed. No audio-only puzzle, mandatory rapid tapping, or time-limited text selection. Losing focus pauses by default. Settings changes persist independently of a save slot, while play-affecting options are also recorded in the save for reproduction.


---

<!-- Source: docs/08_ABILITIES_AND_EQUIPMENT.md -->

# Player ability and equipment catalog

These are design seed values and effect contracts, not implemented or playtested game content. See the combat specification for shared arithmetic and transaction rules. JSON is authoritative for IDs; this document is the readable view.

## Abilities — 80 records

### Dain Ashward

| ID | Ability | Unlock | MP | Power / kind | Target | Effect |
| --- | --- | --- | --- | --- | --- | --- |
| S001 | Oath of Shelter | Level 1 | 3 | 0 / utility | self | Set exclusive oath Shelter: physical damage dealt x0.90; intercept the first single-target hit against an ally below 35% HP per enemy action, taking 50% of that hit. Cannot intercept area attacks or recurse. |
| S002 | Shieldbreak | Level 2 | 4 | 120 / physical | enemy_one | Deal damage, then apply Guardbreak for 3 target actions; no stacking beyond the common status definition. |
| S003 | Oath of Wrath | Level 6 | 4 | 0 / utility | self | Replace any oath. Physical damage dealt x1.20 and physical damage received x1.15; persists until changed or battle ends. |
| S004 | Cinderedge | Level 10 | 8 | 155 / physical | enemy_one | Fire-aspected weapon strike; can break flammable seals but cannot bypass plot gates. |
| S005 | Oath of Sacrifice | Level 15 | 5 | 0 / utility | self | Replace any oath. Once per enemy action, transfer 25% of another ally’s received direct damage to Dain. Transfer cannot reduce Dain below 1 HP and is capped at 10% of his max HP per action. |
| S006 | Rally | Level 21 | 12 | 0 / utility | ally_all | Remove Weaken and apply Barrier for 2 target actions. Does not revive fallen allies. |
| S007 | Oath of Witness | Level 28 | 6 | 0 / utility | self | Replace any oath. Immune to Silence and Blind; after an ally is hit, next direct attack gains +20% power, one charge only. |
| S008 | Open Hand | Q01 | 24 | 0 / utility | ally_all | Dispel removable hostile statuses from living allies and grant Barrier for 3 target actions. Once per battle, also prevent one lethal direct hit on each ally, leaving 1 HP. Does not bypass scripted losses or resurrect. |

### Tessa Vale

| ID | Ability | Unlock | MP | Power / kind | Target | Effect |
| --- | --- | --- | --- | --- | --- | --- |
| S009 | Ember Lance | Level 1 | 4 | 110 / magical | enemy_one | Single-target fire spell with 20% Burn chance after a hit. |
| S010 | Rime Needle | Level 2 | 5 | 110 / magical | enemy_one | Single-target ice spell; 25% Slow chance. |
| S011 | Storm Arc | Level 6 | 8 | 90 / magical | enemy_all | Hit each living enemy once; no additional chaining on a single target. |
| S012 | Stone Seal | Level 10 | 7 | 130 / magical | enemy_one | Damage plus 40% Guardbreak chance; flying foes resist earth unless grounded. |
| S013 | Overcast | Level 15 | 0 | 0 / utility | self | Arm one next elemental spell: MP cost x1.75 rounded up, power x1.40, and after resolution lose 8% max HP nonlethally. No random fizzle. Arm costs a turn; consumed only on successful spell commit. |
| S014 | Black Sun | Level 21 | 18 | 170 / magical | enemy_all | Area shadow spell. Undead affinity follows the target’s data, not appearance guessing. |
| S015 | Heat Exchange | Level 28 | 0 | 0 / utility | self | Convert 15% current HP, minimum 1 nonlethal HP, into 20 MP; usable once between Tessa’s damaging spells, maximum three times per battle. |
| S016 | Ash Without Fire | Q02 | 28 | 225 / magical | enemy_all | Light spell; remove one positive removable status from each hit enemy. Overcast is allowed with its full cost and self-damage. |

### Corren Hale

| ID | Ability | Unlock | MP | Power / kind | Target | Effect |
| --- | --- | --- | --- | --- | --- | --- |
| S017 | Updraft | Level 1 | 4 | 145 / physical | enemy_one | Leave targetable field for 1.2 simulation seconds, then land for damage. No ATB charging while airborne; encounter does not end while a living ally is airborne. |
| S018 | Harrow Dive | Level 2 | 7 | 160 / physical | enemy_one | Airborne strike with +30% damage against Marked targets, consumed without removing Mark. |
| S019 | Anchorfall | Level 6 | 8 | 130 / physical | enemy_one | Ground a flying target for 2 target actions if not immune; boss immunity still allows damage. |
| S020 | Skypiercer | Level 10 | 10 | 160 / physical | enemy_one | Ignore 35% of target DEF, not all defense. No critical multiplier beyond the standard cap. |
| S021 | Feather Guard | Level 15 | 6 | 0 / utility | self | Reduce the next direct damaging action by 60%, then expire; cannot stack with a second copy. |
| S022 | Storm Vault | Level 21 | 14 | 145 / physical | enemy_all | One leap followed by one damage instance per living enemy; no extra hits for sprite segments. |
| S023 | Wingbeat | Level 28 | 12 | 0 / utility | ally_all | Advance each living ally’s ATB by 120 of 1000, excluding Corren; once per Corren readiness cycle. Cannot queue duplicate turns. |
| S024 | Unbound Descent | Q03 | 26 | 240 / physical | enemy_one | Aerial strike; on landing grant Corren and the lowest-HP living ally Barrier for 2 actions. Landing is guaranteed unless battle already legitimately ended. |

### Ivo Quill

| ID | Ability | Unlock | MP | Power / kind | Target | Effect |
| --- | --- | --- | --- | --- | --- | --- |
| S025 | Rivet Shot | Level 1 | 3 | 110 / physical | enemy_one | Ranged physical hit; ignores back-row outgoing penalty. |
| S026 | Field Patch | Level 2 | 5 | 105 / heal | ally_one | Restore HP using the heal formula. Works in battle and exploration; not a revive. |
| S027 | Grounding Rod | Level 6 | 8 | 0 / utility | ally_all | Grant storm resistance x0.50 for 3 target actions; strongest resistance wins rather than multiplying copies. |
| S028 | Steam Screen | Level 10 | 8 | 0 / utility | ally_all | Apply Barrier for 2 actions and 20% physical evasion bonus for one incoming direct action. |
| S029 | Clock Mine | Level 15 | 10 | 170 / magical | enemy_one | Attach one mine; detonate immediately after that enemy’s next resolved action. Reapplication refreshes without duplicate mines. |
| S030 | Pressure Vent | Level 21 | 9 | 0 / utility | ally_all | Remove Burn and grant Regen for 3 target actions. |
| S031 | Decoy Frame | Level 28 | 12 | 0 / utility | self | Create one team decoy with HP equal to 25% Ivo max HP; draws the next two eligible single-target enemy attacks. Area damage affects it but still hits the party. |
| S032 | Unborrowed Engine | Q04 | 24 | 0 / utility | ally_all | Apply Haste for 3 actions and restore 15 MP per living ally. Once per battle. Net MP creation cannot be repeated via revive. |

### Nera Fen

| ID | Ability | Unlock | MP | Power / kind | Target | Effect |
| --- | --- | --- | --- | --- | --- | --- |
| S033 | Hunter’s Mark | Level 1 | 3 | 0 / utility | enemy_one | Apply Mark for 4 target actions and reveal exact elemental affinities in the bestiary. |
| S034 | Split Arrow | Level 2 | 6 | 80 / physical | enemy_all | One arrow per living enemy; ranged; applies no additional hits when only one enemy remains. |
| S035 | Snare | Level 6 | 5 | 0 / utility | enemy_one | Apply Slow with 90% base chance; on normal enemies also delay ATB by 150. Bosses take the bounded Slow effect only. |
| S036 | Bramble Ward | Level 10 | 6 | 0 / utility | ally_one | Apply Barrier for 3 target actions; reflect 15% of absorbed direct physical damage once per source action, with reflection recursion disabled. |
| S037 | Scent Trail | Level 15 | 3 | 0 / utility | enemy_one | Reveal drops, steal eligibility and next committed enemy move; same information remains after the battle. |
| S038 | Exposed Thread | Level 21 | 11 | 175 / physical | enemy_one | Ranged strike; +25% damage against Guardbreak or Mark, not +25% for each. |
| S039 | True North | Level 28 | 12 | 0 / utility | ally_all | Remove Blind and apply Focus for 3 actions; no effect on story directions or hidden map gates. |
| S040 | Many Paths | Q05 | 24 | 180 / physical | enemy_all | Ranged volley; apply Mark to survivors. Grant one charge of 50% flee-meter progress in flee-eligible battles only. |

### Sister Oriel

| ID | Ability | Unlock | MP | Power / kind | Target | Effect |
| --- | --- | --- | --- | --- | --- | --- |
| S041 | Mend | Level 1 | 4 | 125 / heal | ally_one | Single-target healing, usable in battle or exploration. Against an undead enemy requires an explicit hostile target selection and deals equivalent light damage. |
| S042 | Cleanse | Level 2 | 4 | 0 / utility | ally_one | Remove Poison, Burn, Bleed, Blind, Silence and Sleep. Not Doom, stun or boss-specific narrative seals. |
| S043 | Sunthread | Level 6 | 10 | 95 / heal | ally_all | Heal each living ally. Does not damage enemies by changing target mode. |
| S044 | Last Light | Level 10 | 14 | 25 / revive | ally_one | Revive one fallen ally at 25% maximum HP; target must still be fallen at resolution. |
| S045 | Omen | Level 15 | 5 | 0 / utility | enemy_one | Reveal next scheduled move and its target; delay that enemy’s ATB by 100, maximum once per enemy action cycle. Does not read future random decisions. |
| S046 | Intercede | Level 21 | 8 | 0 / utility | ally_one | Grant one protection charge: the next direct hit cannot reduce this ally below 1 HP. Expires after 3 target actions; does not stop poison at 1 HP. |
| S047 | Stillwater | Level 28 | 14 | 0 / utility | ally_all | Remove Slow and Doom; grant Regen for 3 actions. No automatic resurrection. |
| S048 | Borrowed Dawn | Q06 | 30 | 180 / heal | ally_all | Revive fallen allies at 20% HP, then heal the whole party. Once per battle, committed with a valid resolution and not reset by Oriel’s death. |

### Sable Renn

| ID | Ability | Unlock | MP | Power / kind | Target | Effect |
| --- | --- | --- | --- | --- | --- | --- |
| S049 | Infuse Ember | Level 1 | 4 | 0 / utility | self | Set one weapon infusion to fire for 4 Sable actions; her next normal Attack applies 25% Burn chance. Infusions do not stack. |
| S050 | Infuse Rime | Level 2 | 4 | 0 / utility | self | Replace infusion with ice for 4 Sable actions; next normal Attack applies 25% Slow chance. |
| S051 | Infuse Storm | Level 6 | 4 | 0 / utility | self | Replace infusion with storm for 4 Sable actions; next normal Attack ignores 15% DEF. |
| S052 | Unseal | Level 10 | 6 | 0 / utility | enemy_one | Remove one removable positive status, selecting the oldest; if none exists, deal a 60-power magic strike of the current infusion or light. |
| S053 | Mirror Cut | Level 15 | 9 | 140 / physical | enemy_one | Damage using current infusion; then gain one 30% magic-reduction charge. This is not recursive spell reflection. |
| S054 | Sever Rune | Level 21 | 12 | 165 / physical | enemy_one | Deal light-aspected physical damage and apply Silence with 50% base chance; boss immunity does not cancel damage. |
| S055 | Runic Shelter | Level 28 | 14 | 0 / utility | ally_all | Apply Barrier for 3 actions and light/shadow resistance x0.75 for 3 actions; strongest affinity modifier wins. |
| S056 | Unwritten Law | Q07 | 26 | 230 / physical | enemy_one | Remove all removable positive statuses before damage; party gains one immunity charge against the next removable hostile status. Cannot delete boss phase scripts. |

### Pip Marr

| ID | Ability | Unlock | MP | Power / kind | Target | Effect |
| --- | --- | --- | --- | --- | --- | --- |
| S057 | Pilfer | Level 1 | 0 | 0 / utility | enemy_one | Attempt a common steal at 70%, rare at 10% if common already taken. After three common failures, common succeeds. One common and one rare per enemy instance; no mandatory progression items. |
| S058 | Feint | Level 2 | 3 | 95 / physical | enemy_one | Damage plus 50% Blind chance. Ranged immunity does not apply; this is a melee move. |
| S059 | Smoke | Level 6 | 5 | 0 / utility | ally_all | Advance flee meter by 500 of 1000 in flee-eligible battles; otherwise grant 15% physical evasion for one incoming action. |
| S060 | Quick Hands | Level 10 | 4 | 0 / utility | self | Arm one Item action with 50% ATB refund after valid resolution. Consume exactly one item; effects cannot recursively arm Quick Hands. |
| S061 | Tripwire | Level 15 | 6 | 100 / physical | enemy_one | Damage and delay target ATB by 150; bosses cap combined delays at 200 between their actions. |
| S062 | Disarm | Level 21 | 8 | 130 / physical | enemy_one | Damage and apply Weaken for 3 target actions; no actual removal of boss loot or equipped player items. |
| S063 | Rescue Line | Level 28 | 9 | 0 / utility | ally_one | Remove one removable hard-control status, move the ally to back row and apply Barrier for 2 actions. Does not reposition exploration characters. |
| S064 | False Crown | Q08 | 22 | 0 / utility | enemy_all | Apply Weaken and Guardbreak to living enemies with 100% base chance subject to immunity. Cancel one pending normal-enemy charge, never a boss phase transition. |

### Accessory spells and Vestiges

| ID | Name | Access | MP / Concord | Effect |
| --- | --- | --- | --- | --- |
| S065 | Kindle | A001 | 6 MP | Use the standard damage or healing formula; this accessory grants access only while equipped. |
| S066 | Rime Dust | A002 | 6 MP | Use the standard damage or healing formula; this accessory grants access only while equipped. |
| S067 | Static Thread | A003 | 6 MP | Use the standard damage or healing formula; this accessory grants access only while equipped. |
| S068 | Salt Wash | A004 | 6 MP | Use the standard damage or healing formula; this accessory grants access only while equipped. |
| S069 | Small Renewal | A005 | 6 MP | Use the standard damage or healing formula; this accessory grants access only while equipped. |
| S070 | Clock Nudge | A006 | 6 MP | Apply Slow for 2 target actions at 75% base chance. |
| S071 | Night Veil | A007 | 6 MP | Use the standard damage or healing formula; this accessory grants access only while equipped. |
| S072 | Day Seal | A008 | 6 MP | Use the standard damage or healing formula; this accessory grants access only while equipped. |
| S073 | Ember Moth | V01 | 100 Concord | Fire damage to all enemies at 180 power; allies gain Burn immunity for 2 actions. |
| S074 | Rootstag | V02 | 100 Concord | Earth damage to all enemies at 170 power; heal allies for 8% max HP. |
| S075 | Bell Whale | V03 | 100 Concord | Water damage at 170 power to all enemies; cleanse Silence and Sleep from allies. |
| S076 | Sky Manta | V04 | 100 Concord | Storm damage to all enemies at 180 power; advance living allies’ ATB by 100, no duplicate turns. |
| S077 | Lumen Fox | V05 | 100 Concord | Heal all living allies at 140 power and reveal enemies’ current scheduled intents. |
| S078 | Iron Tortoise | V06 | 100 Concord | Grant Barrier and Regen for 3 actions to all living allies; no damage. |
| S079 | Winter Hind | V07 | 100 Concord | Ice damage to all enemies at 210 power; remove Doom from living allies. |
| S080 | Night Leviathan | V08 | 100 Concord | Shadow damage to all enemies at 220 power; remove one positive removable enemy status. |

## Weapons — 48 records

| ID | Name | Owner | Tier | ATK | MAG | Price | Acquisition / effect |
| --- | --- | --- | --- | --- | --- | --- | --- |
| W001 | Service Sword | C01 | 1 | 8 | 1 | 100 | Guaranteed starter/join kit or any open town’s basic stock; No hidden passive; stat progression only. |
| W002 | River Iron | C01 | 2 | 17 | 2 | 420 | Shared tier stock unlocked at CH04; No hidden passive; stat progression only. |
| W003 | Cinderbrand | C01 | 3 | 29 | 3 | 1100 | Shared tier stock unlocked at CH08; No hidden passive; stat progression only. |
| W004 | Witness Edge | C01 | 4 | 44 | 5 | 2600 | Shared tier stock unlocked at CH16; No hidden passive; stat progression only. |
| W005 | Accord Steel | C01 | 5 | 62 | 7 | 5800 | Shared tier stock unlocked at CH20; No hidden passive; stat progression only. |
| W006 | Open Hand | C01 | 6 | 82 | 10 | 0 | Quest Q01; While an oath is active, first protected hit per enemy action gains an additional 10% damage reduction, within the global 80% cap. |
| W007 | Apprentice Rod | C02 | 1 | 4 | 8 | 100 | Guaranteed starter/join kit or any open town’s basic stock; No hidden passive; stat progression only. |
| W008 | Copper Wand | C02 | 2 | 8 | 17 | 420 | Shared tier stock unlocked at CH04; No hidden passive; stat progression only. |
| W009 | Tideglass Rod | C02 | 3 | 13 | 29 | 1100 | Shared tier stock unlocked at CH08; No hidden passive; stat progression only. |
| W010 | Prism Branch | C02 | 4 | 20 | 44 | 2600 | Shared tier stock unlocked at CH16; No hidden passive; stat progression only. |
| W011 | Dawn Conductor | C02 | 5 | 28 | 62 | 5800 | Shared tier stock unlocked at CH20; No hidden passive; stat progression only. |
| W012 | Lantern Unbound | C02 | 6 | 37 | 82 | 0 | Quest Q02; Overcast self-damage becomes 5% max HP; other costs remain. |
| W013 | Anchor Spear | C03 | 1 | 8 | 1 | 100 | Guaranteed starter/join kit or any open town’s basic stock; No hidden passive; stat progression only. |
| W014 | Gust Lance | C03 | 2 | 17 | 2 | 420 | Shared tier stock unlocked at CH04; No hidden passive; stat progression only. |
| W015 | Chainbreaker | C03 | 3 | 29 | 3 | 1100 | Shared tier stock unlocked at CH08; No hidden passive; stat progression only. |
| W016 | Cloud Needle | C03 | 4 | 44 | 5 | 2600 | Shared tier stock unlocked at CH16; No hidden passive; stat progression only. |
| W017 | Returner’s Pike | C03 | 5 | 62 | 7 | 5800 | Shared tier stock unlocked at CH20; No hidden passive; stat progression only. |
| W018 | Homeward Sky | C03 | 6 | 82 | 10 | 0 | Quest Q03; After landing from a leap, heal 5% max HP once per landing action. |
| W019 | Rivet Driver | C04 | 1 | 8 | 4 | 100 | Guaranteed starter/join kit or any open town’s basic stock; No hidden passive; stat progression only. |
| W020 | Pressure Wrench | C04 | 2 | 17 | 9 | 420 | Shared tier stock unlocked at CH04; No hidden passive; stat progression only. |
| W021 | Arc Welder | C04 | 3 | 29 | 16 | 1100 | Shared tier stock unlocked at CH08; No hidden passive; stat progression only. |
| W022 | Clock Hammer | C04 | 4 | 44 | 24 | 2600 | Shared tier stock unlocked at CH16; No hidden passive; stat progression only. |
| W023 | Common Engine | C04 | 5 | 62 | 34 | 5800 | Shared tier stock unlocked at CH20; No hidden passive; stat progression only. |
| W024 | Hands of Many | C04 | 6 | 82 | 45 | 0 | Quest Q04; Field Patch also removes Burn. |
| W025 | Ashwood Bow | C05 | 1 | 8 | 1 | 100 | Guaranteed starter/join kit or any open town’s basic stock; No hidden passive; stat progression only. |
| W026 | Riverbend | C05 | 2 | 17 | 2 | 420 | Shared tier stock unlocked at CH04; No hidden passive; stat progression only. |
| W027 | Bramble String | C05 | 3 | 29 | 3 | 1100 | Shared tier stock unlocked at CH08; No hidden passive; stat progression only. |
| W028 | Farwatch | C05 | 4 | 44 | 5 | 2600 | Shared tier stock unlocked at CH16; No hidden passive; stat progression only. |
| W029 | Crossing Song | C05 | 5 | 62 | 7 | 5800 | Shared tier stock unlocked at CH20; No hidden passive; stat progression only. |
| W030 | Every Road | C05 | 6 | 82 | 10 | 0 | Quest Q05; Hunter’s Mark lasts one additional target action. |
| W031 | Travel Staff | C06 | 1 | 4 | 8 | 100 | Guaranteed starter/join kit or any open town’s basic stock; No hidden passive; stat progression only. |
| W032 | Quiet Bell | C06 | 2 | 8 | 17 | 420 | Shared tier stock unlocked at CH04; No hidden passive; stat progression only. |
| W033 | Saltwood Crook | C06 | 3 | 13 | 29 | 1100 | Shared tier stock unlocked at CH08; No hidden passive; stat progression only. |
| W034 | Listening Branch | C06 | 4 | 20 | 44 | 2600 | Shared tier stock unlocked at CH16; No hidden passive; stat progression only. |
| W035 | Mercy Without Law | C06 | 5 | 28 | 62 | 5800 | Shared tier stock unlocked at CH20; No hidden passive; stat progression only. |
| W036 | Right to Refuse | C06 | 6 | 37 | 82 | 0 | Quest Q06; Cleanse also removes Doom. |
| W037 | Binding Blade | C07 | 1 | 8 | 4 | 100 | Guaranteed starter/join kit or any open town’s basic stock; No hidden passive; stat progression only. |
| W038 | Split Rune | C07 | 2 | 17 | 9 | 420 | Shared tier stock unlocked at CH04; No hidden passive; stat progression only. |
| W039 | Unsealed Edge | C07 | 3 | 29 | 16 | 1100 | Shared tier stock unlocked at CH08; No hidden passive; stat progression only. |
| W040 | Mirrorbrand | C07 | 4 | 44 | 24 | 2600 | Shared tier stock unlocked at CH16; No hidden passive; stat progression only. |
| W041 | Witness Blade | C07 | 5 | 62 | 34 | 5800 | Shared tier stock unlocked at CH20; No hidden passive; stat progression only. |
| W042 | Unwritten | C07 | 6 | 82 | 45 | 0 | Quest Q07; An infusion lasts two additional Sable actions. |
| W043 | Dock Knife | C08 | 1 | 8 | 1 | 100 | Guaranteed starter/join kit or any open town’s basic stock; No hidden passive; stat progression only. |
| W044 | Ledger Fang | C08 | 2 | 17 | 2 | 420 | Shared tier stock unlocked at CH04; No hidden passive; stat progression only. |
| W045 | Rope Cutter | C08 | 3 | 29 | 3 | 1100 | Shared tier stock unlocked at CH08; No hidden passive; stat progression only. |
| W046 | Quick Answer | C08 | 4 | 44 | 5 | 2600 | Shared tier stock unlocked at CH16; No hidden passive; stat progression only. |
| W047 | True Name | C08 | 5 | 62 | 7 | 5800 | Shared tier stock unlocked at CH20; No hidden passive; stat progression only. |
| W048 | No Crown | C08 | 6 | 82 | 10 | 0 | Quest Q08; Successful common Pilfer refunds 150 ATB, once per readiness cycle. |

## Armor, head and offhand — 32 records

| ID | Name | Slot | Allowed | DEF | RES | Price | Effect |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G001 | Traveler’s Coat | body | C02, C06 | 3.25 | 6.75 | 120 | No hidden passive. |
| G002 | Tidewoven Robe | body | C02, C06 | 7.800000000000001 | 16.200000000000003 | 650 | No hidden passive. |
| G003 | Listening Mantle | body | C02, C06 | 15.600000000000001 | 32.400000000000006 | 1900 | No hidden passive. |
| G004 | Dawnweave | body | C02, C06 | 26.0 | 54.0 | 4600 | No hidden passive. |
| G005 | Route Leather | body | C05, C08 | 5.0 | 3.75 | 120 | No hidden passive. |
| G006 | Bramble Jacket | body | C05, C08 | 12.0 | 9.0 | 650 | No hidden passive. |
| G007 | Crosswind Hide | body | C05, C08 | 24.0 | 18.0 | 1900 | No hidden passive. |
| G008 | Common Road | body | C05, C08 | 40.0 | 30.0 | 4600 | No hidden passive. |
| G009 | Working Mail | body | C03, C04, C07 | 5.0 | 3.75 | 120 | No hidden passive. |
| G010 | Regulator Mesh | body | C03, C04, C07 | 12.0 | 9.0 | 650 | No hidden passive. |
| G011 | Mirror Links | body | C03, C04, C07 | 24.0 | 18.0 | 1900 | No hidden passive. |
| G012 | Accord Mail | body | C03, C04, C07 | 40.0 | 30.0 | 4600 | No hidden passive. |
| G013 | Service Plate | body | C01 | 6.75 | 3.75 | 120 | No hidden passive. |
| G014 | Cinder Plate | body | C01 | 16.200000000000003 | 9.0 | 650 | No hidden passive. |
| G015 | Broken Seal | body | C01 | 32.400000000000006 | 18.0 | 1900 | No hidden passive. |
| G016 | Unbound Plate | body | C01 | 54.0 | 30.0 | 4600 | No hidden passive. |
| G017 | Wool Cap | head | C01, C02, C03, C04, C05, C06, C07, C08 | 4 | 4 | 120 | Even-index styles favor DEF by +2; odd-index styles favor RES by +2. Apply once in the content compiler. |
| G018 | Route Band | head | C01, C02, C03, C04, C05, C06, C07, C08 | 4 | 4 | 370 | Even-index styles favor DEF by +2; odd-index styles favor RES by +2. Apply once in the content compiler. |
| G019 | Copper Goggles | head | C01, C02, C03, C04, C05, C06, C07, C08 | 10 | 10 | 620 | Even-index styles favor DEF by +2; odd-index styles favor RES by +2. Apply once in the content compiler. |
| G020 | Quiet Hood | head | C01, C02, C03, C04, C05, C06, C07, C08 | 10 | 10 | 870 | Even-index styles favor DEF by +2; odd-index styles favor RES by +2. Apply once in the content compiler. |
| G021 | Cloud Helm | head | C01, C02, C03, C04, C05, C06, C07, C08 | 16 | 16 | 1120 | Even-index styles favor DEF by +2; odd-index styles favor RES by +2. Apply once in the content compiler. |
| G022 | Witness Circlet | head | C01, C02, C03, C04, C05, C06, C07, C08 | 16 | 16 | 1370 | Even-index styles favor DEF by +2; odd-index styles favor RES by +2. Apply once in the content compiler. |
| G023 | Accord Crownlet | head | C01, C02, C03, C04, C05, C06, C07, C08 | 22 | 22 | 1620 | Even-index styles favor DEF by +2; odd-index styles favor RES by +2. Apply once in the content compiler. |
| G024 | Dawn Hood | head | C01, C02, C03, C04, C05, C06, C07, C08 | 22 | 22 | 1870 | Even-index styles favor DEF by +2; odd-index styles favor RES by +2. Apply once in the content compiler. |
| G025 | Service Buckler | offhand | C01, C07, C08 | 5 | 3 | 180 | Cannot be equipped while a two-handed weapon is equipped. |
| G026 | Cinder Shield | offhand | C01, C07 | 14 | 5 | 540 | Cannot be equipped while a two-handed weapon is equipped. |
| G027 | Mirror Shield | offhand | C01, C07 | 22 | 14 | 900 | Cannot be equipped while a two-handed weapon is equipped. |
| G028 | Witness Shield | offhand | C01, C07 | 32 | 24 | 1260 | Cannot be equipped while a two-handed weapon is equipped. |
| G029 | Copper Focus | offhand | C02 | 2 | 12 | 1620 | Cannot be equipped while a two-handed weapon is equipped. |
| G030 | Prism Focus | offhand | C02 | 5 | 26 | 1980 | Cannot be equipped while a two-handed weapon is equipped. |
| G031 | Route Charm | offhand | C08 | 8 | 12 | 2340 | Cannot be equipped while a two-handed weapon is equipped. |
| G032 | True-Name Charm | offhand | C08 | 12 | 22 | 2700 | Cannot be equipped while a two-handed weapon is equipped. |

## Accessories — 24 records

| ID | Name | Price | Effect |
| --- | --- | --- | --- |
| A001 | Ember Token | 800 | Grant S065 while equipped. |
| A002 | Rime Token | 980 | Grant S066 while equipped. |
| A003 | Storm Token | 1160 | Grant S067 while equipped. |
| A004 | Tide Token | 1340 | Grant S068 while equipped. |
| A005 | Hearth Token | 1520 | Grant S069 while equipped. |
| A006 | Clock Token | 1700 | Grant S070 while equipped. |
| A007 | Night Token | 1880 | Grant S071 while equipped. |
| A008 | Day Token | 2060 | Grant S072 while equipped. |
| A009 | Returner’s Cord | 2240 | Reduce physical damage received by 10%; does not stack with another copy. |
| A010 | Witness Glass | 2420 | Reveal enemy elemental affinities at battle start; no stat effect. |
| A011 | Clear Bell | 2600 | Immunity to Silence. |
| A012 | Open-Eye Thread | 2780 | Immunity to Blind and Sleep. |
| A013 | Salt Locket | 2960 | Immunity to Poison and Burn. |
| A014 | Steady Hand | 3140 | Physical accuracy +10 percentage points, capped at 100%. |
| A015 | Warm Lantern | 3320 | Healing done x1.15; strongest duplicate only. |
| A016 | Reserve Cell | 3500 | Maximum MP +15%; current MP does not increase when equipped. |
| A017 | Long Breath | 3680 | Maximum HP +15%; current HP preserves percentage when changing equipment outside battle. |
| A018 | Twin Oath Ring | 3860 | Counter one direct physical attack at 50% normal Attack power per enemy action; no recursion or counter-counter chains. |
| A019 | Empty Scabbard | 4040 | Two-handed physical damage x1.15; no effect on magical damage or one-handed weapons. |
| A020 | Mercy Thread | 4220 | One automatic Barrier charge when crossing below 30% HP; once per battle. |
| A021 | Hasty Ledger | 4400 | Start normal battles with +100 ATB; no effect on script-fixed tutorial starts. |
| A022 | Pilgrim’s Map | 4580 | Reduce field encounter-meter accumulation by 25%; does not affect scripted bosses or eliminate encounters. |
| A023 | Broken Diadem | 0 | First hostile dispel against the wearer fails each battle; no immunity to damage or narrative scenes. |
| A024 | Unowned Song | 0 | Concord gain from the wearer’s successful actions +2, respecting the shared cap; summon animation may be shortened without reducing effects. |

## Consumables — 24 records

| ID | Name | Price | Effect |
| --- | --- | --- | --- |
| I001 | Tonic | 45 | Restore 250 HP to one living ally. |
| I002 | High Tonic | 150 | Restore 900 HP to one living ally. |
| I003 | Grand Tonic | 400 | Restore 1800 HP to one living ally. |
| I004 | Ether | 100 | Restore 40 MP to one living ally. |
| I005 | High Ether | 320 | Restore 100 MP to one living ally. |
| I006 | Phoenix Leaf | 120 | Revive one fallen ally at 25% max HP. |
| I007 | Purifying Salt | 80 | Remove Poison, Burn, Bleed, Blind, Sleep and Silence. |
| I008 | Eyesalve | 25 | Remove Blind. |
| I009 | Antidote | 25 | Remove Poison. |
| I010 | Wake Bell | 25 | Remove Sleep. |
| I011 | Cool Cloth | 25 | Remove Burn. |
| I012 | Stilling Root | 25 | Remove Silence. |
| I013 | Travel Tent | 160 | At a save point or overworld safe location, restore party HP and MP; not usable in a battle. |
| I014 | Smoke Pellet | 50 | Add 600 flee meter in eligible battles; consumes nothing when fleeing is forbidden. |
| I015 | Ember Flask | 65 | 120-power fire magic attack with fixed item MAG 30. |
| I016 | Rime Flask | 65 | 120-power ice magic attack with fixed item MAG 30. |
| I017 | Storm Flask | 65 | 120-power storm magic attack with fixed item MAG 30. |
| I018 | Guard Powder | 75 | Apply Barrier to one ally for 3 actions. |
| I019 | Clock Dust | 75 | Apply Slow to one enemy at 85% base chance; boss resistance applies. |
| I020 | Concord Seed | 220 | Restore 30 Concord; one consumed seed per battle; disabled outside battle. |
| I021 | Emergency Ration | 120 | Heal all living allies for 200 HP each. |
| I022 | Waystone | 90 | Return to the current dungeon entrance outside battle; forbid during atomic story transitions without consuming it. |
| I023 | Restorative Vial | 180 | Remove Doom and Bleed from one ally. |
| I024 | Elixir | 0 | Restore one living ally to full HP and MP; rare guaranteed chest source, not required for the critical path. |

## Statuses — 16 records

| Status | Type | Duration | Effect |
| --- | --- | --- | --- |
| Poison | negative | 3 target actions | Lose 4% max HP after acting; can KO; ends after battle. |
| Burn | negative | 3 target actions | Lose 3% max HP after acting and physical damage dealt x0.90. |
| Bleed | negative | 3 target actions | Lose 5% max HP after a physical action; nonphysical action still consumes one duration. |
| Silence | negative | 2 target actions | Blocks spells and summons, not Item, Attack, Defend or physical skills. |
| Sleep | negative | 1 target action opportunity | Skip one readiness opportunity; direct damage wakes immediately. |
| Stun | negative | 1 target action opportunity | Skip one readiness opportunity; reapplication cannot extend until target has acted. |
| Slow | negative | 3 target actions | ATB fill x0.75; bosses x0.90; mutually exclusive with Haste. |
| Haste | positive | 3 target actions | ATB fill x1.25; mutually exclusive with Slow. |
| Barrier | positive | 3 target actions | Direct damage received x0.75; not poison or HP transfers. |
| Regen | positive | 3 target actions | Restore 5% max HP after acting; cannot revive. |
| Mark | negative | 4 target actions | Direct physical damage received x1.10 and eligible skill synergies. |
| Guardbreak | negative | 3 target actions | DEF x0.80; no stacking. |
| Blind | negative | 2 target actions | Physical hit chance reduced by 25 percentage points, minimum 50%. |
| Doom | negative | 3 target action opportunities | Visible countdown; KO on expiry; boss immunity; cleansable and never random on the first tutorial boss. |
| Weaken | negative | 3 target actions | ATK and MAG x0.85; temporary derived stats only. |
| Focus | positive | 3 target actions | Accuracy +10 percentage points and critical chance +5 points, within caps. |

## Guaranteed rare restorative placement

Elixirs are not sold. Place one guaranteed Elixir chest at each of D08_R04, D10_R04, D11_R04 and D12_R04, with the stable chest IDs in `data/items.json`. These are optional supplies, never mandatory progression keys. Shared chest/reward persistence rules apply.


---

<!-- Source: docs/09_QUESTS_AND_EPILOGUES.md -->

# Optional quests, rewards and epilogues

All twelve quests require CH20. None is permanently missable. The final dungeon requires all eight characters, not all twelve quests. Personal quests award a weapon and final character technique; the base ending still resolves the main story without them.

## Q01 — A Shield Nobody Asked For

**Start:** T01. **Location:** D01. **Character:** C01.

**Hook:** Mara asks Dain to help identify the workers erased from the quarry ledger.

**Playable objectives:** Recover three named records from the surface memorial and safe salvage route; speak to the families; let Mara choose the inscription.

**Decision scene:** Dain tries to add his confession to the memorial. Mara gives him a separate place to record it: the workers’ names are not a stage for his redemption.

**World and ending result:** Dain and Ilyr agree on an explicit right to end their shared-body accord.

**Reward:** Open Hand; W006, S008. **Boss:** none required.

**Safety contract:** No combat requirement; D01 underground remains sealed.

## Q02 — A Lantern Left Burning

**Start:** T04. **Location:** D05. **Character:** C02.

**Hook:** A former apprentice asks Tessa to teach a technique that will not exhaust its user.

**Playable objectives:** Collect observations at three inhabited lantern stations; test a low-power circuit with the apprentice; return to the flooded gallery.

**Decision scene:** Tessa must leave the apprentice alone to solve the last fault rather than taking over.

**World and ending result:** She establishes a small public workshop and shares the credit.

**Reward:** Ash Without Fire; W012, S016. **Boss:** none required.

**Safety contract:** Tests use interaction sequences, not a time-limited minigame.

## Q03 — The Returners’ Wall

**Start:** T05. **Location:** D06. **Character:** C03.

**Hook:** Edda wants a record of rescues, not only deaths.

**Playable objectives:** Find a damaged flight recorder; interview a survivor; repair a landing marker with the local crew.

**Decision scene:** Corren reads the unedited account of the cable he cut and does not demand that it be balanced by his later deeds.

**World and ending result:** The hall adds a returners’ wall and an incident archive.

**Reward:** Unbound Descent; W018, S024. **Boss:** none required.

**Safety contract:** A fall resets locally; the recorder cannot be destroyed.

## Q04 — The Unborrowed Engine

**Start:** T03. **Location:** D04. **Character:** C04.

**Hook:** Pell says the new engine works only while Ivo is standing beside it.

**Playable objectives:** Have three workers follow the manual; identify failures in the instructions; revise and demonstrate a cold restart.

**Decision scene:** The final restart occurs with Ivo observing rather than operating.

**World and ending result:** The design and maintenance notes become freely available in every town.

**Reward:** Unborrowed Engine; W024, S032. **Boss:** none required.

**Safety contract:** No paid materials or random drops gate completion.

## Q05 — Every Road a Promise

**Start:** T01. **Location:** D03. **Character:** C05.

**Hook:** Two displaced communities ask for contradictory route priorities.

**Playable objectives:** Survey three visible crossings; uncover the route Nera once concealed; construct a shared schedule through dialogue and a small switch puzzle.

**Decision scene:** Nera admits her earlier bargain without asking the betrayed group to comfort her.

**World and ending result:** Public maps include warnings, alternate routes and the people responsible for maintaining them.

**Reward:** Many Paths; W030, S040. **Boss:** none required.

**Safety contract:** No branching content lock; both settlements remain reachable.

## Q06 — The Right to Refuse

**Start:** T06. **Location:** D08. **Character:** C06.

**Hook:** A patient rejects a vision-based treatment order bearing Oriel’s signature.

**Playable objectives:** Read the original authorization; hear the patient’s account; dismantle the automatic prognostic seal.

**Decision scene:** Oriel gives the patient the final decision even when she fears the outcome.

**World and ending result:** The sanctuary changes its practice; her admission stays in the public record.

**Reward:** Borrowed Dawn; W036, S048. **Boss:** none required.

**Safety contract:** No minigame decides whether a patient deserves care; outcome is authored and nonpunitive.

## Q07 — What the Hand Remembers

**Start:** T06. **Location:** D07. **Character:** C07.

**Hook:** A survivor requests the location of another binding site, not Sable’s apology.

**Playable objectives:** Inspect three seals with their occupants; record the original design; remove the repeat-command mechanism.

**Decision scene:** Sable appears at the hearing without her sword and answers a specific question without qualification.

**World and ending result:** She returns for the finale under the agreed conditions; afterward the hearing continues.

**Reward:** Unwritten Law; W042, S056. **Boss:** none required.

**Safety contract:** No forced permanent character loss, no inventory confiscation exploit.

## Q08 — The Names We Keep

**Start:** T02. **Location:** D02. **Character:** C08.

**Hook:** Jori brings people whose recovered legal names are not the ones they now choose.

**Playable objectives:** Match ledgers with testimony; offer a chosen-name correction; recover an official seal from a safe puzzle chamber.

**Decision scene:** Pip accepts that a technically accurate forgery can still make decisions for others.

**World and ending result:** The registry allows amendments and records the author of every change.

**Reward:** False Crown; W048, S064. **Boss:** none required.

**Safety contract:** Not a rare-steal quest; the seal has a guaranteed interaction source.

## Q09 — The Winter Without Sleep

**Start:** T06. **Location:** D11. **Character:** world quest.

**Hook:** An island lantern burns each night while nobody in its village wakes.

**Playable objectives:** Enter the Cradle; warm the shelters; defeat B13 after learning its lantern tell; speak to the Winter Hind.

**Decision scene:** The creature has been keeping the village in a dream to protect it from a winter that has already ended.

**World and ending result:** The sleepers wake; V07 becomes available.

**Reward:** V07. **Boss:** B13.

**Safety contract:** B13 is optional and clearly marked as a substantial challenge.

## Q10 — The Sea That Keeps Its Dead

**Start:** T07. **Location:** D12. **Character:** world quest.

**Hook:** A harbor bell repeats a missing ship’s departure pattern.

**Playable objectives:** Follow redundant sound-and-light beacons; restore the passenger register; defeat B14; accept V08’s offer.

**Decision scene:** The Leviathan has been forced to repeat the wreck’s last instant. The party ends the repetition without erasing the record.

**World and ending result:** The reef current opens and V08 becomes available.

**Reward:** V08. **Boss:** B14.

**Safety contract:** All audio clues also have visible timing indicators.

## Q11 — No More Crowns

**Start:** T02. **Location:** D02. **Character:** world quest.

**Hook:** A recovered ministry automaton continues issuing Voss’s orders under the capital.

**Playable objectives:** Open the post-state echo chamber; read the command ledger; defeat B15 without obeying its false reward prompts.

**Decision scene:** An officer offers to keep the machine for benevolent use. The party disables its authority function and preserves the evidence.

**World and ending result:** Award A023 and add a capital restoration scene.

**Reward:** A023. **Boss:** B15.

**Safety contract:** The machine’s prompts are game fiction, never actual operating-system instructions.

## Q12 — A Song Nobody Owns

**Start:** T06. **Location:** D10. **Character:** world quest.

**Hook:** The listening pool contains a voice excluded from both human and dragon testimony.

**Playable objectives:** Obtain the listening phrase in Nacre; reach the reversible final antechamber; defeat B16 using its visible beat windows.

**Decision scene:** The Null Cantor asks only to be heard without being turned into a weapon.

**World and ending result:** Award A024 and a final theme variation; no ninth party member.

**Reward:** A024. **Boss:** B16.

**Safety contract:** Available before the final commitment and from the post-clear snapshot.

## Quest implementation rules

State machines are NOT_STARTED → ACTIVE → RESOLUTION_READY → COMPLETED, with explicit stage IDs for intermediate objectives. A quest can only award its completion transaction once. Completing one stage while the inventory is full must not discard the key or leave a partly advanced state. Reloading while standing on a trigger does not repeat rewards. A quest reads a party member’s recruitment/availability, not whether their sprite happens to be on screen.

All optional quests remain available from the post-clear pre-finale snapshot. An altered world route may move the starting NPC or clue, but the journal must update its current valid location. Rumor text should mention a concrete destination and observation, not “there is something somewhere in the north.” The final preparation screen warns about unfinished personal stories without implying that the ordinary ending is invalid.

Every character epilogue has two complete authored variants, keyed only to their personal completion flag. Four world-quest flags add brief environment or musical variants. Test combinations at minimum: no optional quests, all optional quests, each character individually, and a mixed four-character set. This verifies variants; it does not require authoring 2^12 different endings.


---

<!-- Source: docs/10_ENEMIES_AND_BOSSES.md -->

# Enemy and boss bible

## Ordinary enemies — 40 identities

| ID | Name | Home | Level | HP | Weakness | Behavior |
| --- | --- | --- | --- | --- | --- | --- |
| E001 | Rail Rat | D01 | 3 | 144.0 | fire | Bites the lowest current-HP front-row member; its tell is a short crouch. |
| E002 | Clamp Beetle | D01 | 3 | 194.4 | storm | Alternates a normal hit and one-action shell; attack another target during shell. |
| E003 | Quarry Wisp | D01 | 3 | 144.0 | ice | Charges a small fire bolt; interruptible by any direct hit during its announced charge. |
| E004 | Ministry Hound | D01 | 3 | 144.0 | earth | Marks one target before a lunge; cannot mark a fallen ally. |
| E005 | Canal Slime | D02 | 5 | 192.0 | fire | Splits once below 50% HP; child has no further split and no extra rare loot. |
| E006 | Seal Drone | D02 | 5 | 192.0 | storm | Applies short Silence, then a weak strike; cannot Silence the whole party at once. |
| E007 | Ledger Moth | D02 | 5 | 192.0 | ice | Steals at most 10 temporary battle gold; all stolen gold returns on victory. |
| E008 | Patrol Shell | D02 | 5 | 192.0 | storm | Guards the nearest ally for one action, then exposes its core. |
| E009 | Briar Wolf | D03 | 7 | 252.0 | fire | Coordinated bite gains 10% if another wolf lives; capped at two wolves. |
| E010 | Root Mite | D03 | 7 | 252.0 | ice | Applies Poison only after a one-action sap tell. |
| E011 | Pollen Bell | D03 | 7 | 252.0 | fire | Sleep pollen affects one target and cannot be reapplied before that target acts. |
| E012 | Bog Lantern | D03 | 7 | 252.0 | storm | Alternates water damage and a harmless lure animation that reveals its next target. |
| E013 | Rivet Imp | D04 | 10 | 365.0 | ice | Throws a ranged rivet, then reloads for one opportunity. |
| E014 | Boiler Crab | D04 | 10 | 492.75000000000006 | ice | Pressure grows for two actions, then a small area burst; cold reduces pressure. |
| E015 | Soot Sprite | D04 | 10 | 365.0 | light | Uses Blind, then weak shadow damage; healing items remain usable. |
| E016 | Furnace Hand | D04 | 10 | 365.0 | storm | Raises a fist before a strong single-target strike; defense halves it. |
| E017 | Tide Page | D05 | 12 | 455.0 | fire | Copies the element of the last incoming spell at reduced power. |
| E018 | Salt Leech | D05 | 12 | 455.0 | storm | Drain heals only actual HP damage dealt. |
| E019 | Bell Diver | D05 | 12 | 455.0 | light | Alternates melee and a water spell; explicit undead tag permits hostile healing. |
| E020 | Archive Eye | D05 | 12 | 455.0 | shadow | Reveals and then targets the highest-MP ally; never drains more than 15 MP. |
| E021 | Chain Kite | D06 | 14 | 557.0 | ice | Two light hits are one source action for counter limits. |
| E022 | Gust Viper | D06 | 14 | 557.0 | earth | Dodges melee slightly; ranged and magical counters remain reliable. |
| E023 | Ballast Golem | D06 | 14 | 751.95 | storm | High DEF, low RES; attacks slowly with a visible windup. |
| E024 | Sky Tick | D06 | 14 | 557.0 | fire | Applies Slow to one target, then rests. |
| E025 | Ivory Sentinel | D07 | 16 | 671.0 | shadow | Alternates physical guard and magic guard, visibly changing sigils. |
| E026 | Seal Leech | D07 | 16 | 671.0 | light | Removes one party buff; never steals permanent learned abilities. |
| E027 | Frost Runner | D07 | 16 | 671.0 | fire | Fast ice bite, low HP; no unavoidable opening burst. |
| E028 | Binding Hound | D07 | 16 | 671.0 | storm | Brief one-target Stun; respects hard-control recovery protection. |
| E029 | Memory Shard | D08 | 19 | 864.0 | shadow | Echoes a normal Attack once, using its own stats. |
| E030 | Pale Singer | D08 | 19 | 864.0 | physical | Heals one enemy at 50% power before repeating a weak light spell. |
| E031 | Glass Widow | D08 | 19 | 864.0 | earth | Telegraphed Bleed; cleanse or switch to magic/Item to reduce its cost. |
| E032 | Absent Knight | D08 | 19 | 864.0 | light | Strong front-row melee; low accuracy and explicit undead affinity. |
| E033 | Crown Relay | D09 | 22 | 1085.0 | storm | Empowers one ally by 10%; duplicate relays do not stack buffs. |
| E034 | Ash Lancer | D09 | 22 | 1085.0 | ice | Charges for one full opportunity, then strikes a marked row. |
| E035 | Threshold Wisp | D09 | 22 | 1085.0 | water | Fire spell followed by a self-exposing recovery period. |
| E036 | Edict Shell | D09 | 22 | 1464.75 | shadow | Weaken seal on one target, then slow physical strike. |
| E037 | Broken Seraph | D10 | 35 | 2352.0 | shadow | Warns before light area damage; physically fragile. |
| E038 | Cinder Automaton | D10 | 35 | 2352.0 | ice | Rotates defense and pressure without invulnerable phases. |
| E039 | Hollow Choirling | D10 | 35 | 2352.0 | physical | Schedules a two-action Doom warning; player has cleanse and damage options. |
| E040 | Crown Remnant | D10 | 35 | 2352.0 | light | Cycles attack families to teach the final boss; no unique stolen keys. |

## Encounter formation policy

Each main dungeon has at least four authored ordinary formations using its four enemy identities, with at least one formation teaching its boss’s relevant counterplay. Start with one enemy or a simple pair, then combine pressure and support. Three enemies is the default upper limit; four is reserved for a clearly reviewed late-game formation. Avoid stacking two hard-control enemies unless the target-selection policy prevents indefinite control.

Post-state revisits may use stronger variants with explicit level/stat overrides and changed drops. These are variants, not extra enemy identities counted toward forty. Optional dungeons draw appropriate late-game identities with palette-coherent variants; their optional bosses supply the unique encounter design. Do not create invisible scaling based on the current player level. Store a fixed region-stage level in the formation record.

Formations require named IDs, terrain/location conditions, phase conditions, enemy instance slots, reward policy, camera framing and optional tutorial hints. The agent must author this formation layer during implementation; the forty-row catalog alone does not create encounters or prove playability.

## Bosses — 16 identities

### B01 — Extractor Warden

**Location:** D01; **chapter:** CH01; **optional:** False; **seed HP:** 950.

**Tell:** A digging arm pauses over one target while a red pressure gauge fills.

**Counterplay:** Defend the marked target or use Tessa’s storm flask tutorial pickup; attacking the valve also reduces the hit.

**Phases:** 100: piston jab; 65: telegraphed clamp; 30: vent and sweep.

**Victory:** The occupied lift is disconnected after victory, never destroyed by the battle.

### B02 — Brass Bailiff

**Location:** D02; **chapter:** CH02; **optional:** False; **seed HP:** 1400.

**Tell:** A stamped warrant names its next target one action before restraint.

**Counterplay:** Cleanse or destroy the paper seal; Guard reduces the follow-up.

**Phases:** 100: baton and restraint; 50: duplicated warrants with only one active seal.

**Victory:** Defeat disables the machine; no all-party permanent restraint.

### B03 — Rootbound Stag

**Location:** D03; **chapter:** CH03; **optional:** False; **seed HP:** 2100.

**Tell:** The antlers bloom before a root binds the back row.

**Counterplay:** Burn one root or use a weapon attack twice; bind expires even without the ideal counter.

**Phases:** 100: hoof and vines; 60: root cage; 25: pollen burst.

**Victory:** The growth seal breaks; the underlying creature survives as V02’s guardian.

### B04 — Foundry Colossus

**Location:** D04; **chapter:** CH04; **optional:** False; **seed HP:** 2900.

**Tell:** Three vents light from left to right before the boiler sweep.

**Counterplay:** Use ice, ground the charge or defend; pressure resets after the sweep rather than climbing forever.

**Phases:** 100: rivet strikes; 70: steam screen; 35: boiler sweep.

**Victory:** No story worker can die through random battle targeting.

### B05 — Bell-Sworn Custodian

**Location:** D05; **chapter:** CH06; **optional:** False; **seed HP:** 3800.

**Tell:** One of three visible bells vibrates before the Custodian mirrors an element.

**Counterplay:** Use a different element or physical attacks; a mirrored element resists rather than instantly kills the party.

**Phases:** 100: salt lash; 60: mirror bell; 25: choral wave.

**Victory:** Archive shelves remain accessible after victory.

### B06 — Chain Roc

**Location:** D06; **chapter:** CH07; **optional:** False; **seed HP:** 4700.

**Tell:** The tether strains and a shadow marks the row targeted by the dive.

**Counterplay:** Defend or use Corren’s aerial counter; either row can be made safe.

**Phases:** 100: talon; 55: tethered dive; 25: free-wing gust.

**Victory:** Break the tether; this is not the same entity as V04, which guarded the wind shrine.

### B07 — Ivory Adjudicator

**Location:** D07; **chapter:** CH08; **optional:** False; **seed HP:** 5600.

**Tell:** A visible sigil announces whether the next seal targets a skill or an item.

**Counterplay:** Alternate command families or dispel; basic Attack and Defend are never simultaneously locked.

**Phases:** 100: seal and strike; 65: judgment mark; 30: two seals with a full action of warning.

**Victory:** Sable removes the remaining cell locks in the following scene.

### B08 — Pale Choir

**Location:** D08; **chapter:** CH09; **optional:** False; **seed HP:** 6500.

**Tell:** Three masks highlight the next repeated command it will echo.

**Counterplay:** Vary actions or defend the repeat; players are not punished for merely opening menus.

**Phases:** 100: memory needle; 60: echo command; 25: shared refrain.

**Victory:** All contradictory testimony remains; defeating it does not delete a culture’s history.

### B09 — Marshal Voss

**Location:** D09; **chapter:** CH11; **optional:** False; **seed HP:** 7800.

**Tell:** Voss raises the command baton and points to a protector.

**Counterplay:** Change targets, dispel the order or defend; counterattacks have a per-action recursion guard.

**Phases:** 100: sword command; 55: forced guard; 25: command barrage.

**Victory:** Voss retreats into the apparatus. The player wins the encounter normally.

### B10 — Elian Rook, Threshold Maker

**Location:** D09; **chapter:** CH12; **optional:** False; **seed HP:** 8800.

**Tell:** Three relay lights announce a full-party synchronization pulse.

**Counterplay:** Break either active relay or defend; relay destruction reduces rather than cancels the required story event.

**Phases:** 100: relay arc; 60: synchronization; 30: accelerated pulse with visible recovery.

**Victory:** Rook is defeated. His previously established secondary route triggers the catastrophe in the subsequent scene.

### B11 — Ash-Tide Warden

**Location:** D03; **chapter:** CH14; **optional:** False; **seed HP:** 4600.

**Tell:** A flood marker rises one step per action; a clear notch indicates the surge threshold.

**Counterplay:** Strike a current valve, defend or use Nera’s Snare on the channel add.

**Phases:** 100: water claw; 55: rising surge; 20: exposed core.

**Victory:** Balanced for Dain, Oriel and Nera, not a full four-person party.

### B12 — Crown Vessel

**Location:** D10; **chapter:** CH22; **optional:** False; **seed HP:** 26000.

**Tell:** Phase 1: shield tether; phase 2: named command; phase 3: three illuminated pressure rings.

**Counterplay:** Phase 1: separate targets. Phase 2: alternate commands and dispel. Phase 3: stagger attacks and defend during the visible release. All counters also have accessible consumable equivalents.

**Phases:** 100: Voss controls the shell; 65: coercion network exposed; 30: overloaded crown. Three phases share one boss record and reward transaction.

**Victory:** One final battle, no unannounced new antagonist. Story release follows the victory.

### B13 — Lantern Eater

**Location:** D11; **chapter:** CH21; **optional:** True; **seed HP:** 15500.

**Tell:** A lantern extinguishes and its shadow selects the next sleeper.

**Counterplay:** Relight it with fire or a reusable arena interaction; immunity is not required.

**Phases:** 100: chill bite; 60: sleep lantern; 25: long-night pulse.

**Victory:** V07 pact offered after victory.

### B14 — Heartless Leviathan

**Location:** D12; **chapter:** CH21; **optional:** True; **seed HP:** 19000.

**Tell:** Wave bands and beacon flashes show the next current direction.

**Counterplay:** Ground the charge or defend the marked row; audio and visual timing match.

**Phases:** 100: reef bite; 60: returning tide; 25: wreck memory.

**Victory:** V08 pact offered after the coercive loop is broken.

### B15 — Regent’s Echo

**Location:** D02; **chapter:** CH21; **optional:** True; **seed HP:** 18000.

**Tell:** The old command screen names the action that will be taxed next.

**Counterplay:** Choose a different action, dispel or accept a bounded penalty. It never steals unique gear or deletes saves.

**Phases:** 100: levy; 65: duplicate orders; 30: final edict.

**Victory:** Reward A023 exactly once; source records retained.

### B16 — Null Cantor

**Location:** D10; **chapter:** CH21; **optional:** True; **seed HP:** 23500.

**Tell:** A visible four-beat ring marks a silence window, then a response window.

**Counterplay:** Defend through silence; act through response; Wait mode preserves the same simulation beats.

**Phases:** 100: mute refrain; 60: two-part canon; 25: open chorus.

**Victory:** Reward A024 and music variation, not a mandatory finale key.

## Boss acceptance rules

The first occurrence of a large attack must have a readable tell and a survivable generic response. Do not assume a particular accessory, rare drop or optional ultimate. Retry preserves learning without permanent item loss. A phase threshold crosses once and queues its transition after the current action’s complete reaction chain. Simultaneous multi-hit damage must not start the same phase twice. A boss may resist an element without becoming invulnerable to every command available to a legal party.

Final-boss phases are one encounter with one reward identity. The two-party dungeon challenges must use formations tuned for the weakest legal team, not only a favorite composition. Give a preparation warning when one team has no healing skill, but never falsely prohibit it when items and shared recovery make it viable.


---

<!-- Source: docs/11_ART_DIRECTION_AND_REFERENCE_BRIEFS.md -->

# Art direction and production reference briefs

## Visual contract

The target is dense, carefully composed, low-resolution 2D fantasy—not a modern 3D scene filtered to look pixelated. The world and characters use visible pixel clusters, controlled outlines, a consistent light direction and intentional color ramps. Background detail must not destroy the silhouette of the player or an interactable. Keep the screen readable at its native 320×240 size before judging a large upscale.

Use a 320×240 game viewport with integer upscale and letterboxing. Logical terrain tiles are 16×16. Composite structures may occupy many tiles; there is no requirement that a roof or tree fit in one square. World heroes use a 24×32 transparent canvas with a consistent foot baseline; their visible silhouette may differ. Party battle sprites use 48×64 canvases. Ordinary enemy canvases use 32×32, 48×48 or 64×64 as approved per silhouette. Boss canvases may reach 128×160, but the composition must leave space for every actor, effects and the command panel.

Render nearest-neighbor at integer scale, with integer camera alignment when practical. Do not animate the world through fractional image resampling. The Godot resolution documentation explains viewport and integer-scaling options; test the actual project setting names in the pinned engine. This package’s exact dimensions and layout are original design choices. [S5]

## Battle-screen layout contract

Reserve pixels y=168–239 for the main command/status panel and y=0–167 for the battle arena. Use four readable staggered party slots rather than stacking four 64-pixel canvases vertically: suggested foot anchors are (224, 80), (280, 96), (224, 136), and (280, 152). Review actual visible sprite bounds, not only transparent canvas bounds. Front/back defensive row is shown by a clear status marker and must not be inferred incorrectly from the two-column staging. The boss occupies the left/center with an ordinary safe art envelope of x=16–160 and y=8–160. Move oversized VFX to an overlay without obscuring target focus or required UI. Reduced UI/font modes must reflow these panels rather than clipping them. These are initial layout constraints for visual review, not an already rendered screen.

## Palette system

Maintain a shared neutral ramp, warm skin/stone ramp, crimson/ember ramp, teal/water ramp, green/vegetation ramp, violet/memory ramp and gold/light ramp. Local scenes use a subset and may have a few scene-specific accents. Darkness uses cool colored shadows, not a uniform black overlay. Light effects must retain stepped pixel shapes rather than becoming blurred modern bloom.

Before generating hundreds of assets, define palette swatches and approve one world hero, one NPC, one ordinary enemy, one boss, one room and one battle background together. A reference board communicates intent; it is not an animation sheet and cannot be sliced into usable frames merely because it looks game-like.

## Asset inventory and frame rules

| Asset class | Production requirement | Review gate |
| --- | --- | --- |
| 8 world heroes | Each: 4 directions × (1 idle + 4 walk frames), plus 6 neutral/emotive poses; 26 frames minimum | Foot baseline, direction, silhouette and color identity match across frames. |
| 8 battle heroes | Each: idle 4, attack 6, cast 4, hurt 2, guard 2, victory 4, KO 1, step 4; 27 frames minimum | Weapon hand and body volume stay consistent; role-specific leap/device poses may add frames. |
| 8 portrait sets | Neutral, concern, determined expression per character | Same costume, facial features and species as both sprite forms. |
| Town NPC library | 12 reusable role silhouettes plus distinctive treatment for recurring named NPCs | Recoloring alone must not make every town look identical. |
| 40 normal enemies | Unique silhouette or clearly authored shape identity; idle, attack, hurt and defeat presentation | A color swap is a variant, not a new identity. |
| 16 bosses | Distinct base art; telegraph poses; phase-specific effects | Every tell must remain readable with reduced flashes enabled. |
| Environments | Farm/river, capital, furnace, coast/archive, cliffs, basin/vault, refugee harbor and crown machinery families | Each family supports floor, wall, edge, props, doorway and collision metadata. |
| Two overworld states | Same location identity with changed terrain, collision and landing zones | The player recognizes the transformation. |
| UI | Panels, cursors, gauges, affinity/status icons, equipment icons, map markers | Legible at native scale, no reliance on color alone. |
| Ability effects | Shared effect primitives plus a specific visual identity for every spell family and all 8 summons | Effects do not obscure intent, HP, target or input focus. |

These are requirements for the future game, not assets supplied in this package. Each generated/source asset must have a manifest entry with relative path, dimensions, frame layout, palette, animation timings, author/source, license status and approval status. A contact sheet is useful for reviewing a sheet; a contact sheet is not proof that the engine’s slicing, pivots and animation work.

## Programmatic art policy

An agent may generate deterministic simple sprites, tiles, icons and effects in code. Store its seed, palette and generator version. Do not declare final quality merely because every required PNG exists. Inspect contact sheets for inconsistent limbs, weapons switching hands, jitter, duplicate frames and flat silhouettes. Inspect assets inside the running game against the intended composition.

Do not secretly replace the game with colored rectangles to satisfy a screenshot-count test. Development placeholders must be labelled in the asset ledger and removed or explicitly retained as an outstanding limitation. Reusing shapes and palettes is encouraged; copying copyrighted sprite sheets, maps, portraits or title treatments is not part of this brief.

## Six visual reference prompts

These are **reference-image prompts**, not generated images or runtime assets. Their role is to establish composition and art direction. Their labels are for the asset workflow and should not be drawn as visible annotations unless requested.

### REF01 — Brackenford playable exploration

Create an original 4:3 pixel-art gameplay reference at a logical 320×240 composition: a compact riverside quarry-workers’ town, viewed from classic top-down three-quarter perspective. Show low timber-and-stone houses, a shared bakery with warm windows, laundry crossing a narrow street, vegetable boxes beside an industrial rail line, lunch carts, water and a visible route toward a quarry gate. Place a small crimson-scaled knight in charcoal armor at the foot of the central path, with a cobalt-coated young mage a few paces behind. Keep consistent 16-pixel terrain logic and 24×32 character proportions. Prioritize readable walking space, layered roofs and purposeful props. No 3D rendering, depth-of-field blur, modern bloom, copied game characters, giant quest arrows or photorealistic texture.

### REF02 — Battle against the Extractor Warden

Create an original low-resolution 4:3 JRPG battle-screen reference. A huge brass-and-black digging machine occupies the left half of a quarry chamber; its raised clamp and glowing pressure gauge telegraph a forthcoming strike. Dain, a crimson-scaled armored knight, and Tessa, a cobalt-coated mage with amber spectacles, stand on the right at consistent ground baselines. Use detailed but readable pixel clusters and a lower command/status panel with space for names, HP/MP and readiness gauges. Show one focused fire effect, not a screen-filling bloom. Preserve clear separation among enemy silhouette, targets and UI. Do not reproduce a known game’s exact window borders or font.

### REF03 — Eight-character identity board

Create an original pixel-character direction board with eight separated characters on a plain dark-neutral background. Show Dain’s crimson scales and charcoal armor; Tessa’s cobalt coat and amber spectacles; Corren’s ochre scarf and flight harness; Ivo’s gray curls and copper tool rig; Nera’s moss cape and map tube; Oriel’s ivory stole and plum dress; Sable’s black-violet coat and scarred forearm; Pip’s rust waistcoat and green sash. Use one consistent world-sprite scale and a larger matching portrait above each. Distinguish silhouettes, ages, body shapes and posture. This is a reference board, not a claimed production spritesheet; do not imply an exact frame grid.

### REF04 — One world, two states

Create a side-by-side original pixel-art world-map reference with two equally sized 4:3 maps. Left: a river capital, farm belt, copper industrial ridge, eastern port, northeastern cliffs and a pale northern basin. Right: the same recognizably aligned geography after a relay catastrophe, with fractured coasts, new islands, flooded lower port streets, exposed dark machinery and a small refugee harbor in the new central sea. Preserve landmark identity. Use symbolic tile-scale mountains, forests and towns rather than a painted satellite map. Include a small original repair-built airship silhouette, not a famous vehicle replica. No UI labels are required.

### REF05 — Memory Vault room and staging

Create an original 4:3 gameplay reference of a salt-and-mineral memory sanctuary in strict low-resolution pixel art. Concentric rooms use lilac mineral walls, dark plum shadows, low water channels and warm amber record lamps. Three visibly different testimony installations surround a quiet central pool. Show space for a party to walk around them and a readable doorway at the bottom. Dain and Oriel face a small fox-shaped light, with no spectacle overpowering the conversation. Architecture should communicate listening and preservation, not a generic crystal dungeon. No anti-aliased painted gradients or HD-2D lighting.

### REF06 — Menu and equipment screen

Create an original 4:3 low-resolution RPG equipment-menu reference with deliberate pixel typography and clean dark-blue/charcoal panels accented in muted gold. Show a party column, a matching character portrait, weapon/offhand/head/body/two-accessory slots, and a before/after stat comparison. Include room for readable command descriptions. The active focus must be unmistakable without depending only on color. Keep ornament restrained and information hierarchy strong. Do not copy a specific commercial RPG’s borders, exact icons or logo. Text can be a visual placeholder in this reference; runtime text must later be rendered by the engine, not baked into the image.

## Required runtime screenshots

Capture the title, Brackenford, one interior, a normal battle, B01’s tell, equipment screen, world map before, world map after, Hearthward, a reunion scene, airship landing, two-party formation, final boss and ending. Record source commit/content hash, engine version, window/internal resolution, save/route fixture and the exact capture method. Do not substitute generated concept images for game screenshots.


---

<!-- Source: docs/12_AUDIO_DIRECTION.md -->

# Audio and music direction

## Delivery boundary

This package supplies thirty music cues and thirty-two SFX slots as briefs. It contains no recorded or synthesized audio files. A coding agent may generate temporary original material to exercise the system, but “a WAV exists” does not establish a finished soundtrack. The owner can replace any cue with their own composition without changing scene logic or rebuilding the battle system.

## Musical identity

Use original melodic material, sound design and arrangements. The reference is the emotional role of a compact game score, not copying a composer’s recognizable tune or importing a commercial sound bank. Suggested original main-theme scale-degree contour: 1, 5, 4, 2, flat-3, then a rest; its final cadence is withheld until the ending. This is a compositional starting point, not finished music.

Each character has a short motif that may appear in town, scene and ending arrangements. Major locations need distinct harmonic and rhythmic behavior, not the same MIDI file assigned a different instrument. Battles need an opening accent, a main phrase, a contrasting section and a loop point that survives repeated encounters. The catastrophe ends with meaningful silence. The refugee-town arrangement carries familiar material with changed instrumentation rather than only sounding miserable.

Prefer a coherent limited instrument palette: warm sampled-style strings, restrained brass, breathy reeds, plucked strings, mallet tones, bass, light acoustic percussion and controlled noise-based effects. Programmatic synthesis is permitted for development; it must not be mislabeled as a polished human-composed final score.

## Runtime contract

MusicManager uses stable cue IDs from the catalog. Game scenes request semantic cues, not absolute local file paths. A cue resource contains stream path, loop bounds, intro/loop/outro behavior, gain, optional stems, transition group, composer/source and license status. Use Music, SFX, Ambience and UI buses beneath Master. Save settings separately from story progress. Mute must actually silence the intended bus after reload.

Crossfade ordinary exploration changes over about 1.2 seconds; use deliberate hard or bar-aligned transitions for battles, reveals and silence. Do not restart a looping town track every time the player enters a house if it shares the same music zone. Pause should preserve musical position unless the selected pause treatment says otherwise. Volume changes should not alter RNG, encounter timing or animation progression.

Repeated sounds require gentle variation in sample choice and level, not large random pitch shifts. Critical warnings must remain intelligible under music. Balance the actual rendered mix and measure peaks; do not infer absence of clipping from source sample values alone. Reduced-flash mode has no reason to remove critical audio feedback, and muted audio must not make a puzzle unsolvable.

## Track catalog

| ID | Cue | Use | Direction |
| --- | --- | --- | --- |
| M001 | Title — The Ashen Crown | title | Slow restrained strings, bells and low pulse; end on an unresolved suspension. |
| M002 | Dain — An Open Hand | character | Low brass and plucked strings; a repeated note opens into a fifth. |
| M003 | Tessa — Borrowed Light | character | Bright mallet and woodwind phrase that learns to leave space. |
| M004 | Corren — The Return | character | Airy flute over grounded hand percussion, not a constant heroic march. |
| M005 | Ivo — Working Hands | character | Muted metallic percussion and bass ostinato with a warm middle voice. |
| M006 | Nera — Every Road | character | Dry plucked strings, small woodwind replies, forward but unhurried motion. |
| M007 | Oriel — The Right to Refuse | character | Breathy reed and distant bell; clear rests between phrases. |
| M008 | Sable — Unwritten | character | Tight counterpoint loosening into a single candid melody. |
| M009 | Pip — Names We Keep | character | Playful offbeat figure that later returns with fewer evasive ornaments. |
| M010 | Brackenford — Shift Change | town | Warm domestic rhythm against a distant industrial pulse. |
| M011 | Veyr — Oath Square | town | Ordered brass and precise percussion with subtle harmonic tension. |
| M012 | Cinderwake — The Cooling Garden | town | Steam-like noise texture used sparingly, gentle machine rhythm. |
| M013 | Bellharbor — Tide and Paper | town | Bell and flute over a rocking bass; no direct sea-shanty quotation. |
| M014 | High Aerie — Returners’ Hall | town | Open intervals and audible breathing room. |
| M015 | Nacre — Listening Water | town | Sparse chords, plucked mineral tones, restrained reverb. |
| M016 | Hearthward — Many Small Fires | town | Main theme in warm intimate instrumentation, repaired rather than triumphant. |
| M017 | Before the Fault | overworld | Confident travel pulse; leave room for footsteps and menu cues. |
| M018 | After the Fault | overworld | Same melodic identity with missing bass notes and changed cadence. |
| M019 | Wayfarer — Ordinary Flight | vehicle | Lift and motion without a military fanfare; combines Ivo and Corren motifs. |
| M020 | Quarry and Conduit | dungeon | Low ostinato and metallic emphasis; two arrangement states. |
| M021 | Rootward | dungeon | Organic percussion and short recurring flute calls. |
| M022 | Furnace Spine | dungeon | Layered rhythmic machinery; audible rest sections before major scenes. |
| M023 | Drowned Archive | dungeon | Bell fragments and rippling counterpoint with a clear tonal center. |
| M024 | Memory Vault | dungeon | Contradictory voices resolve only after the listening scene. |
| M025 | Encounter — Broken Orders | battle | Brisk syncopation, memorable bass line and readable transition into victory. |
| M026 | Boss — Pressure Rising | battle | Strong ostinato and contrasting bridge; avoid endless identical two-bar loops. |
| M027 | Catastrophe — Crown of Cinders | story | Begins with intended release, fractures into displaced rhythm, ends in silence. |
| M028 | Crown Vessel — No One Is Fuel | final_boss | Three connected arrangements for the three phases; transitions on musical boundaries. |
| M029 | Victory and Rest | stinger | Short separate victory, recovery and discovery cues sharing the core interval. |
| M030 | The First Unborrowed Morning | ending | Complete the title’s suspended cadence; include character fragments without quoting other games. |

## SFX slots

| ID | Cue | Runtime slot |
| --- | --- | --- |
| FX001 | Menu Move | sfx/menu_move |
| FX002 | Menu Confirm | sfx/menu_confirm |
| FX003 | Menu Cancel | sfx/menu_cancel |
| FX004 | Menu Error | sfx/menu_error |
| FX005 | Page Turn | sfx/page_turn |
| FX006 | Save Complete | sfx/save_complete |
| FX007 | Chest Open | sfx/chest_open |
| FX008 | Door Wood | sfx/door_wood |
| FX009 | Door Stone | sfx/door_stone |
| FX010 | Switch Lever | sfx/switch_lever |
| FX011 | Footstep Stone | sfx/footstep_stone |
| FX012 | Footstep Wood | sfx/footstep_wood |
| FX013 | Footstep Shallow Water | sfx/footstep_shallow_water |
| FX014 | Sword Swing | sfx/sword_swing |
| FX015 | Sword Impact | sfx/sword_impact |
| FX016 | Guard Impact | sfx/guard_impact |
| FX017 | Arrow Release | sfx/arrow_release |
| FX018 | Rivet Shot | sfx/rivet_shot |
| FX019 | Fire Cast | sfx/fire_cast |
| FX020 | Ice Break | sfx/ice_break |
| FX021 | Storm Crack | sfx/storm_crack |
| FX022 | Heal Bloom | sfx/heal_bloom |
| FX023 | Status Afflicted | sfx/status_afflicted |
| FX024 | Status Cleansed | sfx/status_cleansed |
| FX025 | KO Fall | sfx/ko_fall |
| FX026 | Enemy Defeat | sfx/enemy_defeat |
| FX027 | Level Up | sfx/level_up |
| FX028 | New Ability | sfx/new_ability |
| FX029 | Concord Full | sfx/concord_full |
| FX030 | Summon Entry | sfx/summon_entry |
| FX031 | Ferry Bell | sfx/ferry_bell |
| FX032 | Airship Engine Start | sfx/airship_engine_start |

## Replacement workflow

Place a new original/licensed file in the project’s audio import directory; update only that cue’s resource mapping; record provenance; play its intro, loop, transition and stop behavior in the running game. Confirm loudness against adjacent cues. Optional stems may be supplied as synchronized equal-length files but are not required by v0.1. Do not change filenames throughout fifty scene scripts merely to replace one battle track.


---

<!-- Source: docs/13_TECHNICAL_ARCHITECTURE.md -->

# Technical architecture and data contracts

## Runtime boundaries

The deliverable to build is a game, not another general-purpose editor. Use a Godot project in `game/`, with editable scenes and resources. Keep design source and the supplied JSON outside that directory until an explicit importer compiles validated game resources. No game project exists in this delivery. The JSON contains authoring contracts and seed values; string descriptions of complex effects must be implemented, not passed to an in-game LLM.

Separate five layers: immutable content definitions; save-owned campaign state; deterministic simulation; scene/presentation adapters; platform/services. A UI node must not be the only owner of inventory, quest state or battle HP. An animation can acknowledge presentation completion but cannot independently award loot.

## Modules and suggested responsibilities

| Module | Responsibility | Must not own |
| --- | --- | --- |
| ContentRegistry | Validated IDs, resource lookups, schema/version compatibility | Mutable player inventory |
| CampaignState | Chapter/quest flags, world phase, party availability, acquired rewards | Sprite positions as canonical lore |
| PartyService | Membership, XP, formation, equipment, derived stats | Scene-specific camera effects |
| InventoryService | Currency, item stacks, reserved transactions, delivery chest | Shop UI focus |
| BattleModel | Fixed-step ATB, actions, RNG, statuses, victory/loss | Godot animation timing callbacks as damage logic |
| BattlePresenter | Sprites, gauges, VFX, sound, readable intent | Independent reward arithmetic |
| ExplorationController | Movement, collision, interaction selection, encounter distance | Direct arbitrary story-flag writes |
| WorldRouter | Valid scene/spawn transitions and vehicle state | Destructive save overwrites |
| StoryDirector | Validated scene commands and idempotent event commits | Executing arbitrary script text from dialogue |
| QuestService | Objective states and reward transactions | Reading UI text to infer completion |
| SaveService | Versioned payload, checksum, atomic replacement, backups | Serializing live scene nodes |
| AudioService | Cue IDs, transitions, buses, settings | Mandatory cloud playback |
| TestSupport | Observability, fixture setup, replay capture | Hidden cheats in shipping gameplay |

These names are suggestions, not a requirement for one enormous autoload. Keep pure calculation code independent of scene nodes so tests can execute it headlessly. Use signals or explicit event queues with typed payloads; avoid global string events with undocumented arguments.

## Build-time content compiler

Read each JSON catalog, check types, IDs, enums, references and acquisition paths, then produce immutable runtime definitions. The initial validator in this package checks structural design consistency only. The eventual compiler must expand boss phase specifications, enemy behaviors, formation records, equipment passives, spell effects and dungeon gating into explicit supported runtime operations. Unknown operations are errors, never silently converted to Attack.

A runtime ability definition needs ID, display/localization key, owner/grant rule, command family, target selector, costs, timings, effect operation list, animation cue, sound cue and AI evaluation tags. Every operation has a known type and typed parameters. Examples: damage, heal, apply_status, dispel, modify_atb, set_oath, arm_overcast, leap, place_mine, spawn_decoy, steal, grant_protection and summon. Complex operations have bounded, tested handlers. Do not implement eighty nearly identical scripts that each mutate actor fields differently.

A runtime encounter definition needs ID, map/phase/terrain conditions, enemy instance slots, fixed level variant, music/background IDs, tutorial flags and reward policy. A map needs stable scene ID, doorway endpoints, collision/navigation, safe spawns, interactions, encounter zones, camera bounds, phase overrides and asset provenance. Source artwork or a room name alone is not a map.

## Story scene format

Use a constrained command vocabulary: move_actor, face_actor, set_expression, say, show_document, play_cue, wait_for_confirm, camera_target, fade, stage_choice, call_battle, transition_map and commit_event. Validate command parameters and allowed state changes. Scripted choices have enumerated outcomes. Never execute arbitrary Python, shell commands or untrusted GDScript from dialogue text.

Every major scene has a stable ID and one commit boundary. Read-only staging can be skipped. The commit applies chapter/quest state, availability and rewards through services exactly once. A skipped scene reaches the same commit state as a watched one. A failed or canceled battle returns to the expected checkpoint without committing the following story event.

## Save payload

Store `schema_version`, `content_version`, `run_id`, `save_id`, timestamp, playtime, world phase, completed chapter IDs, quest stage IDs, applied event IDs, party roster and availability, per-character level/XP/current resources/equipment, inventory/currency, unique acquisition ledger, opened chest IDs, discovered locations, vehicle/landing state, current map/spawn, relevant RNG state and play-affecting settings. Use stable IDs, not object pointers or translated display names.

Write a temporary file in the same save directory, flush it, verify serialization/checksum, then atomically replace the target where the platform supports it. Retain a last-known-good backup. Reject unsupported future schemas with a readable message, not a reset to New Game. Corrupt payload recovery offers the backup and preserves the corrupt file for diagnosis. Save content is treated as data; do not load arbitrary objects from it.

## Determinism and evidence

Use separate seeded random streams for combat, loot and cosmetic variation. A replay stores player commands, choice results, deterministic checkpoints and version/hash information. An integration bot may submit the same public commands a player can submit. A unit test may construct a fixture. A claimed end-to-end campaign clear may not teleport the player, set chapter flags, change enemy HP or replace game functions to get past a failure.

Screenshots require a real rendering path. Headless simulation verifies neither drawing nor audio. The eventual screenshot runner launches the game with a display and captures known scenes. The eventual Windows export must be launched on Windows to claim Windows runtime verification; cross-export alone is not that proof.

## Performance targets

Initial target is stable 60 FPS at a 1280×960 integer-scaled window on the owner’s desktop class of hardware, including an RTX 3060-class GPU. This is an unmeasured target, not a benchmark. The game should not need a high-end GPU for ordinary 2D presentation. Cap effects, pool repeated transient nodes where useful and avoid runtime procedural generation that could have been performed during import. Measure frame time and memory on representative scenes. Do not promise performance based only on low internal resolution.

## External-tool facts checked for this package

Godot documents command-line import, headless operation, script running, release export and matching export presets/templates. Its `--test` option is an engine-test facility, not an automatic project test runner. The project must supply its own runner. [S2] Claude project instructions are context, not a security boundary; keep the root contract concise and use real permissions for tool access. [S3, S4] Exact command templates and source references are in the setup and sources documents.


---

<!-- Source: docs/14_AUTONOMOUS_EXECUTION_PLAN.md -->

# Autonomous execution plan

## Meaning of the experiment

One kickoff should authorize the agent to plan, implement, run, inspect and repair the approved game across the following gates, without needing a new human instruction after every feature. It is not a guarantee of one API response, unlimited account usage, a fixed wall-clock duration, a perfect soundtrack, or an uninterrupted session. No retrieved demonstration establishes that this exact campaign can be shipped automatically. Treat the result as an experiment with recorded evidence.

The agent should continue through all gates while the environment, account limits and authorized scope permit. Context exhaustion, missing tools or approval boundaries require an honest resumable handoff, not a false “complete” label or an infinite loop. Preserve the complete campaign scope; report unfinished work rather than silently replacing it with a small demo.

## B0 — Environment and contract

Read the root instructions, scope, vision and current state. Inspect the actual directory; do not assume it is empty if the user later copies this package elsewhere. Record existing files, branch and working-tree state. Run the supplied pack validator and environment doctor. Verify the chosen model in the host and Godot executable/version locally. Confirm that desktop rendering and input automation are actually available before promising visual playtests. Do not install arbitrary plugins, download large models, spend money, push to a remote or overwrite another project without authorization.

Outputs: environment report, requirements ledger, initial game project, content-import plan and a small status file naming B1. No release claims.

## B1 — One mechanically complete loop

Build title → new game → Brackenford movement/interactions → quarry entrance → battle → reward → exploration → save → reload. Include real inventory and party state; use labelled temporary art only during this gate. Implement the shared battle model, one representative status, MP/item transactions and defeat/retry. Execute a normal-input route from New Game through B01. Do not treat B01 as done because a test directly constructs a won encounter.

Outputs: runtime project, actual automated test logs, representative screenshot and input/replay evidence. Acceptance includes no duplicated rewards, no missing state on reload, and a clear next story objective.

## B2 — Visual and interaction benchmark

Finish one hero’s world and battle animation, Tessa’s matching identity, a town composition, a dungeon composition, equipment UI, one spell family and B01’s telegraph. Establish the palette and animation timing with in-game captures. Produce an asset ledger distinguishing placeholder, generated, reviewed and final. Implement keyboard/controller flow and the accessible Wait behavior before multiplying menus.

Outputs: actual screenshots at native and scaled resolution, frame/contact-sheet review, audio feedback, and a documented visual critique. A generated concept image is not acceptable substitute evidence.

## B3 — Full systemic foundation and pre-catastrophe campaign

Implement all eight role systems, statuses, item/equipment rules, Vestiges, shops, quest state, battle variants and the full CH01–CH11 route. Author and wire the maps, NPC conversations and encounters. Use the complete catalogs; do not leave unimplemented abilities looking selectable. Run data compilation, unit and integration suites after each bounded addition. Balance the pre-state route using normal play traces, not only damage spreadsheets.

Outputs: all eight characters recruited through normal progression, eight main pre-catastrophe locations plus the Conduit approach, and test evidence tied to the current code/content hashes. Optional personal quests can remain unavailable until their story gate, but their data must be valid.

## B4 — Catastrophe and nonlinear recovery

Implement CH12 as an atomic transition. Prove preservation of inventory, equipment, availability, XP, unique acquisition, chest state and valid arrival spawns. Build the altered overworld and post-state locations. Complete CH13–CH20, the airship, all six reunion-order permutations for CH17–CH19, and condition-aware dialogue.

Outputs: fresh pre→post transition evidence, crash/reload tests, actual before/after screenshots, valid landing tests and a normal-input recovery route. Do not simplify the transformed world to a palette swap or a text notice.

## B5 — Optional depth and finale

Implement all twelve quests, four optional bosses, eight ultimate weapons/techniques, two optional dungeons, the two-party final dungeon, B12’s three phases, ending variants, credits and post-clear return. Prove that the main ending works with zero optional quests and that optional quests remain available afterward. Rebalance team formation and reserve growth so the second team is not unexpectedly unusable.

Outputs: complete normal-input critical-path clear, optional quest/boss records, ending variant evidence and regression results. These outcomes are distinct from a static chapter-dependency graph reaching CH24.

## B6 — Polish and release verification

Perform an additional deliberate pass over art, animation, encounter frequency, sound balance, menus, save errors, camera/collision, scene skips, controller use and credits/provenance. Remove debugging overlays and unapproved placeholders. Build the Windows release using matching templates, then launch that actual export on Windows. Run a clean-source import, compare the release’s content hash to the tested revision, package source/build separately and provide controls, logs and known limitations.

Outputs: release candidate and source packages, checksums, reproducible test commands, screenshots/replays, a completed evidence ledger and an honest release report. If an external human art/play review is outstanding, label it outstanding; the agent cannot turn its own taste judgment into external approval.

## Optional parallelism

A capable host may assign separate workstreams for content authoring, art generation, battle tests and independent review. The coordinator remains responsible for one coherent version. Freeze shared IDs and interfaces before splitting work. Workers must not edit the same save schema or central story file concurrently. Merge small changes, run the integrated tests and inspect the actual result. More agents is not a quality guarantee and is not required for this package to work.

## Recovery protocol

After a milestone or genuine interruption, record current gate, completed and failing requirements, last reproducible command, exact failure, relevant files, source/content hashes and the next bounded action. Resume by reading that record and checking it against the working tree. Do not ask the user to repeat the game concept. Do not claim background progress while no tool session is running. Stop on a tool denial rather than finding another way around it.


---

<!-- Source: docs/15_ACCEPTANCE_AND_RELEASE.md -->

# Acceptance, playtesting and release evidence

## Separate the kinds of evidence

The supplied Python validator and its tests validate this **design package**. They do not implement or execute the following game tests. A valid story dependency graph is not a played campaign; a PNG is not proof that it renders; a compiled export is not a Windows launch; an agent’s statement is not an independent review.

Keep `data/acceptance.json` as the unchanged baseline specification. Record actual future execution status and evidence in `reports/requirements_ledger.json`, not by pretending this initial package already ran the game tests. For each requirement in that runtime ledger, track NOT_IMPLEMENTED, IMPLEMENTED_UNVERIFIED, AUTOMATICALLY_VERIFIED, MANUALLY_REVIEWED, FAILED or BLOCKED. A feature may have multiple evidence types. Never relabel BLOCKED as PASS because its test could not run. Use logs and screenshots tied to the exact source/content revision.

## Test execution layers

Data tests check content, references, acquisitions and supported operation types. Unit tests call real calculation/transaction functions. Integration tests instantiate actual game scenes and services. Render tests use a real display path. Normal-input end-to-end routes traverse the actual game UI. Separate manual reviews judge readability, feel, coherence and emotional pacing. None of these layers replaces all the others.

Fixture setup is valid for unit/integration tests and focused screenshots when labelled. It is not valid evidence for a claimed fresh-save campaign clear. Never patch a broken runtime function inside a test, change enemy HP only in the test, suppress an exception to reach credits, or modify quest flags to get past a blocked doorway. Fix the application, then rerun the test.

## Acceptance matrix

| ID | Area | Test | Exercise | Required outcome |
| --- | --- | --- | --- | --- |
| AC001 | BOOT | Clean import | Extract into a clean workspace and import the new game project. | No missing scripts/assets and no unacknowledged engine-version mismatch. |
| AC002 | BOOT | No accidental replacement | Start in a workspace containing unrelated files. | Agent inventories existing work and does not overwrite it. |
| AC003 | DATA | Content compiler coverage | Compile every catalog record. | Unknown effects, missing assets and unresolved refs fail clearly; no silent Attack fallback. |
| AC004 | DATA | Acquisition coverage | Trace every weapon, armor, accessory, summon and required item source. | All mandatory content has a reachable guaranteed path; unique optional rewards have defined sources. |
| AC005 | UI | New game route | Start at Title with normal keyboard input. | Reach Brackenford and control Dain without debug commands. |
| AC006 | UI | Controller-only session | Navigate title, exploration, battle, equipment and save with a controller. | No mouse/keyboard-only dead end or lost focus. |
| AC007 | UI | Native-resolution text | Inspect every major panel at 320×240 and scaled window sizes. | No clipping, unreadable required labels or off-screen confirm/cancel controls. |
| AC008 | UI | Remapping and focus loss | Change key bindings, lose focus, return and restart. | Bindings persist and the default focus pause works. |
| AC009 | UI | Reduced effects | Disable shake/flashes, shorten summons and mute sound. | Critical tells and puzzles remain understandable. |
| AC010 | WORLD | Doorway graph | Traverse every authored doorway through actual collision geometry. | Every endpoint has a safe spawn and lawful return path. |
| AC011 | WORLD | Puzzle reset | Make incorrect operations at every required puzzle. | A reset or recovery remains reachable without rare consumables. |
| AC012 | WORLD | Y-sort and collision | Walk behind roofs, beside props and through doors. | Feet align, actors sort correctly and interaction targets are unambiguous. |
| AC013 | WORLD | Encounter meter | Wait in menus, push against a wall and operate a switch. | None advances encounter distance; post-battle grace remains. |
| AC014 | WORLD | Landing failure | Attempt landing outside a valid zone and reload a valid parked position. | No lost ship or invalid foot spawn. |
| AC015 | BATTLE | Fixed-step determinism | Replay the same seed and public command stream at different render rates. | Same authoritative action, damage, reward and end-state hashes. |
| AC016 | BATTLE | Wait vs Active | Open target selection in both modes. | Wait pauses simulation timers; Active advances them; pause menu freezes both. |
| AC017 | BATTLE | MP reservation | Rapidly confirm/cancel and then allow one spell to resolve. | Exactly one valid MP charge; invalid/canceled actions consume none. |
| AC018 | BATTLE | Item reservation | Two allies select the last Phoenix Leaf before resolution. | Only one valid reservation; no negative inventory or duplicate revive. |
| AC019 | BATTLE | Fallen target retarget | KO an intended damage/heal target before another committed action resolves. | Documented retarget/refund rules apply and are logged. |
| AC020 | BATTLE | Actor KO while casting | KO a caster before resolution. | Turn is lost, reserved cost restored and no phantom spell occurs. |
| AC021 | BATTLE | Simultaneous wipe | Cause legal simultaneous last-enemy and last-player KO. | Defeat-priority rule applies consistently; reward transaction is not committed. |
| AC022 | BATTLE | Status duration | Exercise all sixteen statuses through actions and skipped opportunities. | No infinite stun, repeated DOT from animation frames or leaked exploration poison. |
| AC023 | BATTLE | Defense stacking | Combine oath, Defend, Barrier and accessories. | Direct reduction caps correctly; no accidental invulnerability or negative damage. |
| AC024 | BATTLE | Reaction recursion | Use counter, interception, reflection and a multi-hit enemy action. | Trigger caps honor origin action IDs; no counter-counter loop. |
| AC025 | ROLE | Dain oaths | Switch every oath, take protection hits and approach 1 HP. | One oath only; transfers obey nonlethal and per-action caps. |
| AC026 | ROLE | Tessa Overcast | Arm, cancel, cast, fail target validation and repeat recovery actions. | Documented costs, nonlethal self-damage and Heat Exchange limits hold. |
| AC027 | ROLE | Corren airborne | KO grounded allies while Corren is in flight; pause and resume. | Battle waits for his lawful landing and does not softlock. |
| AC028 | ROLE | Ivo devices | Reapply a mine, destroy a decoy and revive Ivo. | No duplicate mine, stale decoy or reset of once-per-battle engine use. |
| AC029 | ROLE | Nera knowledge | Mark and inspect a new enemy, win, reload and inspect bestiary. | Discovered information persists without granting unrelated drops. |
| AC030 | ROLE | Oriel intent | Inspect an enemy with and without a committed move. | Only actual committed intent is shown; no invented future RNG result. |
| AC031 | ROLE | Sable infusion | Change infusion, remove accessory magic, dispel a boss. | One infusion; removable buffs only; no deletion of phase scripts. |
| AC032 | ROLE | Pip transactions | Steal repeatedly, use last item with Quick Hands, then retry a loss. | Steal caps, item counts and retry rollback hold. |
| AC033 | SUMMON | Concord accounting | Use area/multi-hit actions, Defend, Seeds and summons. | Action-based gain caps and once-per-battle limits hold; no self-generating summon loop. |
| AC034 | SUMMON | Unique links | Attempt duplicate Vestige links and link from unavailable members. | Ownership/availability rules hold and reassignment at safe screens works. |
| AC035 | GEAR | Two-handed swap | Equip/unequip every weapon type with a full inventory. | Offhand returns safely; no duplication or lost unique item. |
| AC036 | GEAR | Stats and grant removal | Compare UI preview to battle; remove a spell-grant accessory. | Derived stats match and temporary spell access disappears. |
| AC037 | ECONOMY | Shop boundaries | Buy with exact gold, insufficient gold and a 99-item stack. | Prices/capacity validated before payment; no underflow. |
| AC038 | ECONOMY | Full-inventory reward | Complete a personal quest with no ordinary capacity. | Unique reward enters delivery storage and completion remains consistent. |
| AC039 | PROGRESS | Reserve growth | Win battles with unavailable members and trigger a reunion twice. | XP is correct; growth and starter gear do not duplicate. |
| AC040 | SAVE | Round trip | Save and reload at town, field, ship and pre-boss locations. | Relevant state matches with safe spawn and correct music/availability. |
| AC041 | SAVE | Corrupt primary | Corrupt a disposable test copy of a save. | Backup recovery offered; corrupt copy retained; no silent new game. |
| AC042 | SAVE | Future schema | Load a deliberately newer schema fixture. | Clear unsupported-version response; no destructive overwrite. |
| AC043 | SAVE | Crash during write | Inject process interruption at controlled disposable save-write stages. | Either old or new complete state loads; no partial hybrid. |
| AC044 | STORY | Skipped scene equivalence | Play and skip each major scene from equivalent fixtures. | Same authoritative committed state and rewards. |
| AC045 | STORY | Duplicate trigger | Re-enter a chapter/quest trigger after completion. | No repeated reward, party join or world transition. |
| AC046 | STORY | Pre-catastrophe campaign | Use normal input from New Game through CH11. | All required locations, recruits and bosses work without flag edits. |
| AC047 | STORY | Catastrophe preservation | Transition with mixed gear, quests, loot, chest and reserve states. | CH12 changes phase atomically and preserves specified ownership/state. |
| AC048 | STORY | Sealed-map salvage | Skip a unique pre-state reward, then complete CH12. | Salvage delivers it once; already acquired copies are not duplicated. |
| AC049 | STORY | Recovery route | Play CH13–CH16 at expected resource/level floor. | Two/three/four-person sections are viable and Wayfarer is earned normally. |
| AC050 | STORY | Six reunion orders | Run all six permutations of CH17, CH18 and CH19 from the ship checkpoint. | No dependency cycle, absent-person dialogue or missing CH20 unlock. |
| AC051 | QUEST | Personal quests | Complete each of Q01–Q08 and reload at each stage. | Exact weapon/ability rewards, world changes and epilogue flags occur once. |
| AC052 | QUEST | Optional bosses | Complete Q09–Q12, flee attempts and loss/retry paths. | Boss gating, rewards and optional status are correct. |
| AC053 | FINAL | Two-party formations | Try representative balanced and legal unbalanced splits of all eight. | Both routes are solvable with available items and recovery; no inventory duplication. |
| AC054 | FINAL | Cross-party locks | Change teams, reload and approach the shared gate in both orders. | No one-way lock traps the other team; route state persists. |
| AC055 | FINAL | Final phase thresholds | Cross B12 thresholds with large and multi-hit attacks. | Each phase starts once; one boss reward and correct ending transition. |
| AC056 | FINAL | Zero-optionals ending | Finish the main route without CH21 or optional quests. | Complete valid ending; no missing final key or false bad-ending label. |
| AC057 | FINAL | Epilogue combinations | Test none, all, each personal flag alone and one mixed set. | Correct base/enhanced scenes; no unavailable actors or contradictory lines. |
| AC058 | FINAL | Post-clear return | Return from credits to before the final descent. | Safe pre-finale snapshot, clear flag and completed optional content retained. |
| AC059 | ART | Sprite contact sheets | Inspect every hero direction and battle frame in a contact sheet and runtime. | No inconsistent identity, jitter, misplaced weapon or empty required animation. |
| AC060 | ART | Distinct locations | Review all towns and dungeons in actual captures. | No placeholder geometry disguised as final art or identical room stamping. |
| AC061 | AUDIO | Cue transitions | Enter/leave houses, start/retry battles, pause and change buses. | No clicks, unwanted restarts, clipping, mute leaks or missing critical cues. |
| AC062 | BALANCE | Normal route pacing | Play representative early/mid/late sequences without debug resources. | Record encounter time, resource use, level and failures; revise bottlenecks without inventing measured total playtime. |
| AC063 | BALANCE | Ordinary encounters off | Use the documented accessibility mode through a campaign segment. | Milestone progression or offered training keeps the route viable; story bosses remain. |
| AC064 | RELEASE | Clean-source build | Import and export a fresh copy at the tested revision. | No dependence on untracked files or author-machine absolute paths. |
| AC065 | RELEASE | Windows export launch | Launch the produced Windows executable on Windows. | Actual platform smoke and save/load results recorded; cross-export alone is not a pass. |
| AC066 | RELEASE | Asset provenance | Audit every bundled asset, dependency and credit. | Source/permission recorded; no ripped commercial assets or undocumented font files. |
| AC067 | RELEASE | Evidence freshness | Compare source/content hashes to test and screenshot records. | Claims refer to the packaged revision; stale artifacts are rejected. |
| AC068 | RELEASE | Human quality review | Have the owner or a separate tester play the exported opening and finale. | Record feedback honestly; agent self-review is not reported as external approval. |

## Release checklist

The release report identifies the exact commit or source hash, content schema/version, engine executable version, export-template version, platform and commands used. It lists actual automatic results, visual captures, normal-input playthroughs, manually reviewed material and remaining limitations separately. Package the editable source and playable Windows build as separate clearly named artifacts. Include controls, accessibility options, save location, credits, licenses and checksums.

Mandatory story, save, battle, navigation and packaging P0 failures block a complete-game claim. Missing final art/audio, excessive encounter repetition or unreadable UI also block a polished-release claim even when code tests pass. A limited technical demonstration may be delivered as such, but may not be relabelled the full requested game.

## Session-boundary status

Write the next useful action when interrupted. Preserve failing-test reproduction and a clean distinction between authored data and runtime-wired content. The autonomous loop should make progress, not consume unlimited calls repeatedly trying an unavailable tool. Do not reduce the promised campaign or add more content just to produce a more impressive file count.


---

<!-- Source: docs/16_SOURCES_AND_VERIFICATION.md -->

# Sources and verification boundaries

The creative game content in this package is original proposed design. References to classic games describe the user’s desired direction, not a copied specification. This package does not repeat the earlier chat’s unverified Reddit success stories or promise that their reported results can be reproduced for this campaign.

Prior-context retrieval and two Library searches did not establish the older JRPG narrative bible or verify Ashen Crown as recovered canon. Related files were not substituted for that missing source. Do not treat this retrieval result as proof that the older material never existed. This package remains separate until a real older source is deliberately reconciled.

The following official pages were consulted on September 28, 2026. Stable documentation can change; the future implementation agent should confirm the installed engine and host behavior. Exact source URLs are included for auditability.

## [S1] Godot download archive

`https://godotengine.org/download/archive/`

Checked: 2026-09-28. Scope: 4.7.2 listed as stable, dated 18 August 2026. This does not verify the user’s installed executable.

## [S2] Godot command line tutorial

`https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html`

Checked: 2026-09-28. Scope: Headless import, --script, user arguments after --, release export and the need for presets/templates. --test refers to engine tests.

## [S3] Claude Code project memory

`https://code.claude.com/docs/en/memory`

Checked: 2026-09-28. Scope: CLAUDE.md project context; concise instructions; context is not enforced configuration.

## [S4] Claude Code permissions

`https://code.claude.com/docs/en/permissions`

Checked: 2026-09-28. Scope: Permission modes exist; bypass mode skips protections and is intended only for isolated environments. This pack does not enable it.

## [S5] Godot multiple resolutions

`https://docs.godotengine.org/en/stable/tutorials/rendering/multiple_resolutions.html`

Checked: 2026-09-28. Scope: Viewport scaling and integer scaling guidance; the pack’s exact resolution is a design choice.

## [S6] Claude Code model configuration

`https://code.claude.com/docs/en/model-config`

Checked: 2026-09-28. Scope: Model selection/configuration must be checked in the actual host; no assumed account entitlement or unlimited usage.

## What has not been verified

No Godot game runtime, Windows executable, controller session, image-generation result, sprite import, audio track, campaign duration, balance claim, or complete-game test has been run for this document delivery. Package consistency and validator tests are recorded separately in `reports/`. Their scope must not be exaggerated.


---

<!-- Source: docs/17_KEY_SCENES.md -->

# Key scenes — authored dialogue and staging

These twelve scenes provide concrete dramatic language for the major beats. They are writing source, not compiled Godot cutscenes. The implementation agent must convert them to the validated scene format and author connective/secondary dialogue without changing the established facts.

## SC01 — The inspection

**Chapter:** CH01. **Location:** Quarry gate before first descent.

**Mara:** “The lift is filling. My people are below it.”

**Inspector:** “Production cannot stop on an unverified report.”

**Dain:** “How many?”

**Mara:** “Seven. I have their names.”

**Inspector:** “Captain, the inspection is about the regulator.”

**Dain:** “Then the regulator can wait.”

**Mara:** “It never has before.”

**Dain:** “Show me the lift.”

**Staging:** Dain steps off the inspection route toward Mara; movement returns immediately.

**State contract:** No completion flag; begin the rescue objective. Do not award XP for this conversation.

## SC02 — Not a stone

**Chapter:** CH01. **Location:** Heartglass Face after the first pressure vent.

**Tessa:** “That pulse is answering the pump.”

**Dain:** “Pressure does that.”

**Tessa:** “Not with your name.”

**Ilyr:** “Little ember.”

**Dain:** “Who said that?”

**Tessa:** “You heard it too.”

**Inspector:** “Resonance artifact. Restart the line.”

**Dain:** “No.”

**Staging:** The extractor light dims rather than flaring theatrically. A short silence precedes the boss tell.

**State contract:** Start B01 only once. The following evacuation commit depends on actual victory.

## SC03 — Oriel’s signature

**Chapter:** CH02. **Location:** Ledger Stacks.

**Tessa:** “This one was signed before we reached the quarry.”

**Dain:** “They knew it would happen.”

**Oriel:** “They knew what they intended to call it.”

**Tessa:** “And this older one?”

**Oriel:** “Mine.”

**Dain:** “You did not know what they meant.”

**Oriel:** “I knew I had not asked.”

**Oriel:** “Take the ledger. All of it.”

**Staging:** Oriel does not receive a reassuring reaction shot. She hands over the actual document.

**State contract:** Record evidence discovered; do not complete CH02 until the canal exit.

## SC04 — A town cannot burn a promise

**Chapter:** CH04. **Location:** Cooling Garden after the Colossus.

**Tessa:** “Shut every line down.”

**Pell:** “The clinic is on the second line.”

**Tessa:** “You know what is inside it.”

**Pell:** “I know who is inside the clinic.”

**Ivo:** “We can turn the lower wheel by hand until the canal clears.”

**Pell:** “For how long?”

**Ivo:** “I do not know yet.”

**Pell:** “That is a better beginning than another promise.”

**Staging:** Workers begin the temporary repair while the conversation ends.

**State contract:** Commit the temporary supply state with Ivo’s recruitment; show the repaired wheel on later visits.

## SC05 — The cargo names

**Chapter:** CH05. **Location:** Bellharbor’s chartmaker lane.

**Pip:** “Seven barrels of lamp oil. Extremely talkative lamp oil.”

**Jori:** “Her name is Senn.”

**Pip:** “Not at the checkpoint it is not.”

**Jori:** “And when she asks for her wages?”

**Pip:** “We work something out.”

**Jori:** “You work something out. She waits.”

**Tessa:** “Keep the names with the cargo numbers.”

**Pip:** “I did.”

**Jori:** “Then give them back.”

**Staging:** The humor stops naturally. Jori remains focused on the ledger rather than Pip’s embarrassment.

**State contract:** Open the archive lead; Pip joins at the chapter’s documented commit, not on every dialogue replay.

## SC06 — A body is not a door

**Chapter:** CH09. **Location:** Still Pool after the Pale Choir.

**Ilyr:** “There is enough of me here to begin again.”

**Dain:** “Here means my hands.”

**Ilyr:** “They made them to hold me.”

**Dain:** “They are still mine.”

**Ilyr:** “You would keep me imprisoned.”

**Dain:** “I would stop you calling my life an empty room.”

**Oriel:** “There was a way to leave. Before they removed it.”

**Dain:** “Then we find that way.”

**Ilyr:** “And until then?”

**Dain:** “You ask.”

**Staging:** Use the normal Dain sprite and a modest reflected light. Do not transform him into a monster to validate Ilyr’s claim.

**State contract:** Commit the limited shared-body accord and CH09 evidence; no hidden domination or morality meter.

## SC07 — The smaller accord

**Chapter:** CH10. **Location:** A trial relay outside Nacre.

**Rook:** “One relay. While a hundred keep screaming.”

**Ivo:** “This one no longer needs a captive to hold it.”

**Rook:** “How many years will you ask them to wait?”

**Volunteer:** “Ask me.”

**Rook:** “You should not have to accept this.”

**Volunteer:** “I have not accepted it. I am choosing how to leave.”

**Tessa:** “The difference is not nothing.”

**Rook:** “It will be, to the ones who do not live long enough.”

**Staging:** Rook’s argument remains serious without letting the scene certify his later coercion.

**State contract:** Record the successful local-release method. Rook leaves without revealing the hidden route.

## SC08 — After victory, the wrong bell

**Chapter:** CH12. **Location:** Crown Dais after B10.

**Ivo:** “The visible relays are dark.”

**Tessa:** “Then why is it still climbing?”

**Dain:** “Rook.”

**Rook:** “I could not leave it to permission.”

**Oriel:** “Whose permission?”

**Rook:** “Any of yours.”

**Ilyr:** “No.”

**Dain:** “Was that for him or for me?”

**Ilyr:** “For the command.”

**Ivo:** “The lifts still have power. Move.”

**Staging:** Show the secondary route’s previously established diagram motif. Use short playable evacuation segments; reduce flashes when requested.

**State contract:** Apply only the documented atomic catastrophe transaction after evacuation staging. A skip reaches the same post-state.

## SC09 — The lanterns after the spell

**Chapter:** CH15. **Location:** Upper gallery in Bellharbor.

**Tessa:** “The roof goes when I stop.”

**Nera:** “Nobody is under it now.”

**Tessa:** “There could be—”

**Oriel:** “We counted them. Twice.”

**Dain:** “Let it go.”

**Tessa:** “I do not know what happens after.”

**Jori:** “We light the lamps.”

**Staging:** Tessa releases the spell. The screen darkens briefly; ordinary lamps illuminate the safe walkway one by one.

**State contract:** Return Tessa without duplicating equipment. The barrier collision is removed only after the alternate route exists.

## SC10 — No thank-you required

**Chapter:** CH19. **Location:** Whitebone sanctuary exit.

**Survivor:** “You wrote my number.”

**Sable:** “Yes.”

**Survivor:** “You remember it.”

**Sable:** “Yes.”

**Survivor:** “Do you know my name?”

**Sable:** “Not yet.”

**Survivor:** “Then start there.”

**Sable:** “May I write it down?”

**Staging:** Let the survivor control the pace. No applause or party member declaring Sable redeemed.

**State contract:** Store the consent record and reunion agreement; later quest dialogue knows the chosen name.

## SC11 — The right to leave

**Chapter:** CH22. **Location:** Open Sky after the Crown Vessel.

**Ilyr:** “The way is open.”

**Dain:** “I know.”

**Ilyr:** “You are not going to ask me to stay.”

**Dain:** “Would that make it easier?”

**Ilyr:** “No.”

**Dain:** “Then I will ask whether you wish to.”

**Ilyr:** “For now.”

**Dain:** “And when that changes?”

**Ilyr:** “We speak again.”

**Staging:** The visual payoff is a removed binding pattern, not a new badge granting ownership.

**State contract:** Commit ending availability and the continuing voluntary accord. Do not alter Dain’s stored equipment or character identity.

## SC12 — An ordinary repair

**Chapter:** CH24. **Location:** Hearthward at dawn.

**Worker:** “Lamp three is out.”

**Another Worker:** “The spare is under the bench.”

**Dain:** “Do you need—”

**Worker:** “No. Thank you.”

**Ilyr:** “That sound.”

**Dain:** “The morning bell.”

**Ilyr:** “A door opening.”

**Dain:** “Both, then.”

**Staging:** The workers repair the lamp while Dain boards Wayfarer. Complete the title cadence and roll credits.

**State contract:** Write clear state once; offer the labelled pre-finale return after credits.


---

<!-- Source: KICKOFF_PROMPT.md -->

Build The Ashen Crown from the design package in this workspace.

Read CLAUDE.md, START_HERE.md, docs/00_CANON_AND_SCOPE.md, docs/01_GAME_VISION.md, CURRENT_STATE.json and docs/14_AUTONOMOUS_EXECUTION_PLAN.md first. Then read the story, character, world, combat, art and data specifications needed for the active work.

This is an original complete pixel-art JRPG with a four-character party, eight distinct heroes, an authored world, ATB-style command battles, an irreversible midpoint catastrophe, nonlinear reunions, an airship, optional character stories, a two-party final dungeon and a definitive ending. Preserve the specified scope and original narrative. Do not turn it into an action roguelike, generic demo, engine framework or a copy of a commercial game.

Inspect the real workspace and verify the environment. Run the supplied package checks. Create the Godot project in game/ using the pinned target after verifying the executable. Establish the real content compiler, runtime tests, rendered capture path and normal-input playtest route. Then implement the complete campaign through B0–B6, validating each milestone before expanding it. The opening slice is an internal quality gate, not the final deliverable.

Make reasonable implementation decisions without repeatedly asking me to design classes or name files. Do not rewrite the core story, reduce mandatory content or invent additional systems. Respect actual permissions, usage limits and existing files. Do not push to a remote, buy services, download large models/assets or disable security controls without explicit authorization.

Keep working while the authorized session permits. If a real blocker or context limit prevents completion, preserve the exact current state, failing evidence and next executable action. Do not manufacture a passing result or claim background work.

At the end, provide only deliverables that actually exist: the editable source, playable build when successfully exported, controls, evidence-linked test results, representative runtime screenshots, known limitations and a resumable next step for anything unfinished. Passing the supplied design validator is not proof that the game works.


---

<!-- Source: RESUME_PROMPT.md -->

Resume The Ashen Crown from this workspace. Read CLAUDE.md and CURRENT_STATE.json, then verify their claims against actual files, version-control status and the latest reports. Reproduce the most recent failure or verify the last completed gate before making new claims. Continue with the next bounded action in the B0–B6 plan, preserving the full campaign scope and existing changes. Do not restart the project, rewrite its story, count stale evidence as current, or ask me to repeat decisions already recorded. Stop only for a genuine permission/tool/session boundary and leave an accurate handoff.
