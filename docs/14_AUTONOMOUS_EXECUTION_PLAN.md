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
