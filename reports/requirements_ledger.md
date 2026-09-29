# Requirements ledger (docs/15 acceptance criteria)

Content build a0ca87511117187d. Counts: owner 1, partial 19, unverified 3, verified 45

| ID | Area | Criterion | Status | Evidence / note |
| --- | --- | --- | --- | --- |
| AC001 | BOOT | Clean import | verified | Fresh copy (no .godot cache) imported headless; the first pass logs the usual font-before-import notice, the second pass is clean. |
| AC002 | BOOT | No accidental replacement | verified | The connected folder held only the two handoff markdown files; nothing there was overwritten (deliverables go to new subfolders). |
| AC003 | DATA | Content compiler coverage | verified | Compiler fails on unknown ops, refs, maps, scenes, ragged grids; --strict fails on pending location refs. |
| AC004 | DATA | Acquisition coverage | partial | Starter kits, shops (by chapter tier), chests, quests and salvage cover the catalog; no automated per-item source trace yet. |
| AC005 | UI | New game route | verified | B1 route: Title -> New Game -> Brackenford with normal input. |
| AC006 | UI | Controller-only session | partial | Joypad buttons/axes are bound for every action; no physical controller session was run. |
| AC007 | UI | Native-resolution text | partial | Captures reviewed at 320x240; long objective toasts now wrap. Not every panel was inspected at every scale. |
| AC008 | UI | Remapping and focus loss | partial | Rebinding and pause-on-focus-loss are implemented and persisted; not exercised by an automated test. |
| AC009 | UI | Reduced effects | partial | Shake/flash toggles and volume exist; tells are text + icon so they survive reduced effects. Not separately play-tested. |
| AC010 | WORLD | Doorway graph | partial | Offline: every entity reachable and every arrival spawn reaches every exit of its room. Runtime: all story doorways crossed by the chained routes. |
| AC011 | WORLD | Puzzle reset | partial | Wrong valve/relay/dial/bell choices reset or explain without consuming items; verified by design review and partly by routes (not every wrong input automated). |
| AC012 | WORLD | Y-sort and collision | partial | Y-sorted actors/props and door interaction verified in captures; no systematic sweep. |
| AC013 | WORLD | Encounter meter | partial | Meter advances only on completed steps on encounter terrain; menus/switches/wall pushes cannot step. Not unit-tested. |
| AC014 | WORLD | Landing failure | verified | test_post_state::test_landing_needs_marked_field. |
| AC015 | BATTLE | Fixed-step determinism | verified | test_battle_core::test_fixed_step_determinism. |
| AC016 | BATTLE | Wait vs Active | verified | test_battle_core::test_wait_vs_active. |
| AC017 | BATTLE | MP reservation | verified | test_battle_core::test_mp_reservation. |
| AC018 | BATTLE | Item reservation | verified | test_battle_core::test_item_reservation_last_phoenix. |
| AC019 | BATTLE | Fallen target retarget | verified | test_battle_core::test_fallen_target_retarget, test_revive_refund_when_no_fallen. |
| AC020 | BATTLE | Actor KO while casting | verified | test_battle_core::test_actor_ko_while_casting_refunds. |
| AC021 | BATTLE | Simultaneous wipe | verified | test_battle_core::test_simultaneous_wipe_defeat_priority. |
| AC022 | BATTLE | Status duration | verified | test_battle_core::test_status_durations_and_hard_control, test_haste_slow_exclusive, test_boss_immunities_and_delay_cap. |
| AC023 | BATTLE | Defense stacking | verified | test_battle_core::test_defense_stacking_cap. |
| AC024 | BATTLE | Reaction recursion | verified | test_battle_core::test_counter_no_recursion. |
| AC025 | ROLE | Dain oaths | verified | test_battle_roles::test_dain_oaths_exclusive_and_sacrifice_caps, test_shelter_intercepts_low_ally_once. |
| AC026 | ROLE | Tessa Overcast | verified | test_battle_roles::test_tessa_overcast_costs_and_nonlethal, test_heat_exchange_limits. |
| AC027 | ROLE | Corren airborne | verified | test_battle_roles::test_corren_airborne_no_softlock. |
| AC028 | ROLE | Ivo devices | verified | test_battle_roles::test_ivo_mine_and_decoy. |
| AC029 | ROLE | Nera knowledge | partial | test_battle_roles::test_nera_mark_bonus_not_multiplied; bestiary persistence covered by save round trip, not a dedicated test. |
| AC030 | ROLE | Oriel intent | verified | test_battle_roles::test_oriel_omen_reads_only_committed. |
| AC031 | ROLE | Sable infusion | verified | test_battle_roles::test_sable_single_infusion. |
| AC032 | ROLE | Pip transactions | verified | test_battle_roles::test_pip_steal_caps. |
| AC033 | SUMMON | Concord accounting | verified | test_battle_core::test_concord_accounting. |
| AC034 | SUMMON | Unique links | verified | test_campaign::test_vestige_unique_links. |
| AC035 | GEAR | Two-handed swap | verified | test_campaign::test_two_handed_swap_returns_offhand. |
| AC036 | GEAR | Stats and grant removal | verified | test_battle_roles::test_accessory_spell_removed_with_accessory; test_formulas::test_equipment_change_does_not_regrow. |
| AC037 | ECONOMY | Shop boundaries | verified | test_campaign::test_shop_boundaries; test_post_state::test_every_shop_lists_stock_at_every_stage (regression for the tier-key crash found by the seg8 route). |
| AC038 | ECONOMY | Full-inventory reward | verified | test_campaign::test_unique_overflow_goes_to_delivery. |
| AC039 | PROGRESS | Reserve growth | verified | test_campaign::test_reserve_growth_and_reunion; test_formulas::test_join_level. |
| AC040 | SAVE | Round trip | partial | test_campaign::test_save_round_trip; B1 saves at a lamp, returns to title and reloads through the menu. Ship/pre-boss reloads not separately automated. |
| AC041 | SAVE | Corrupt primary | verified | test_campaign::test_corrupt_primary_offers_backup. |
| AC042 | SAVE | Future schema | verified | test_campaign::test_future_schema_rejected. |
| AC043 | SAVE | Crash during write | verified | test_campaign::test_crash_during_write_keeps_complete_state. |
| AC044 | STORY | Skipped scene equivalence | verified | test_story::test_skip_equivalence. |
| AC045 | STORY | Duplicate trigger | verified | test_story::test_once_scene_not_reapplied; test_post_state::test_personal_quest_reward_once. |
| AC046 | STORY | Pre-catastrophe campaign | verified | Normal-input chain: b1 (New Game..CH01) -> seg2 -> seg3 -> seg4 -> seg5 (CH11, then CH12), each segment resuming from the milestone the previous one wrote. No flag edits in routes. |
| AC047 | STORY | Catastrophe preservation | verified | test_campaign::test_catastrophe_transaction_preserves_ownership; test_post_state::test_catastrophe_scene_commits_post_state; seg5 reaches Hearthward through the real scene. |
| AC048 | STORY | Sealed-map salvage | verified | test_campaign::test_salvage_forwarding_once. |
| AC049 | STORY | Recovery route | verified | seg6: CH13-CH16 with the two-, three- and four-person party; Wayfarer earned in play. |
| AC050 | STORY | Six reunion orders | partial | test_post_state::test_reunion_orders_all_six runs the real completion scenes in all six orders; the routes play one order (CH17, CH18, CH19) end to end. |
| AC051 | QUEST | Personal quests | partial | segq plays Q01-Q08 to COMPLETED with normal input (rewards and final techniques granted); reload at every stage is covered only by the quest-state tests, not per stage in play. |
| AC052 | QUEST | Optional bosses | verified | segq defeats B13, B14, B15 and B16 (Q12 before the final commitment) and receives V07, V08, A023, A024; defeat/Retry paths occurred in dev runs. |
| AC053 | FINAL | Two-party formations | partial | seg8 plays the default balanced split; unbalanced splits are allowed by the split screen (healer warning) but not route-tested. |
| AC054 | FINAL | Cross-party locks | verified | test_post_state::test_team_locks_alternate_without_trapping. |
| AC055 | FINAL | Final phase thresholds | partial | test_battle_core::test_boss_phase_threshold_once; B12 fought in seg8. |
| AC056 | FINAL | Zero-optionals ending | verified | seg8 finishes CH22-CH24 with zero optional quests; the ending, credits and clear save complete. |
| AC057 | FINAL | Epilogue combinations | partial | Each epilogue line branches on its quest flag; only the zero-quest combination is route-played. |
| AC058 | FINAL | Post-clear return | verified | seg8 chooses Continue from Before the Final Descent and lands at the Accord Dock with the post_clear flag. |
| AC059 | ART | Sprite contact sheets | partial | Generated sprites reviewed by the agent only; status 'generated', not final art. |
| AC060 | ART | Distinct locations | partial | Every location has its own composition; art is programmatic and plain in places. |
| AC061 | AUDIO | Cue transitions | unverified | Cue switching implemented; no listening test (headless audio is a dummy driver). |
| AC062 | BALANCE | Normal route pacing | partial | Route traces record level, battles and resources per segment; the bot takes direct paths, so it is a lower bound for play time. |
| AC063 | BALANCE | Ordinary encounters off | unverified | level_floor milestone growth exists for encounters-off; no campaign segment run in that mode. |
| AC064 | RELEASE | Clean-source build | verified | Clean copy imported and exported the Windows build with no author-machine paths. |
| AC065 | RELEASE | Windows export launch | unverified | Build copied to the owner's folder and checksum-verified there; it was not launched on Windows (computer use could not run an unregistered executable). |
| AC066 | RELEASE | Asset provenance | verified | All art/audio/font generated by project code; Godot MIT license and third-party notices bundled. |
| AC067 | RELEASE | Evidence freshness | verified | Final chain, runtime tests and clean-archive export all ran on revision 7428b37 / content e528220ab0ff6194 (logs print the content hash). |
| AC068 | RELEASE | Human quality review | owner | Needs the owner or a separate human tester; agent self-review is not a substitute. |
