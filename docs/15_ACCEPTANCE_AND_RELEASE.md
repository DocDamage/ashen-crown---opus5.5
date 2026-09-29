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
