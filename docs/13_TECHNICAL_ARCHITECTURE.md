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
