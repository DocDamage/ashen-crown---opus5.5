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
