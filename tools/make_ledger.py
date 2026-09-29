"""Requirements ledger: maps each acceptance criterion (docs/15) to its evidence and an honest status.
Statuses: verified (evidence below exercises it), partial (some of it exercised), unverified (not exercised),
owner (needs the owner or a separate human tester). Writes reports/requirements_ledger.json and .md."""
import json, os, re, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC = open(os.path.join(ROOT, "docs", "15_ACCEPTANCE_AND_RELEASE.md"), encoding="utf-8").read()
ROWS = re.findall(r"^\| (AC\d{3}) \| (\w+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|", DOC, re.M)

T = "reports/evidence/tests/runtime_tests_final.txt"
C = "reports/evidence/final_chain/"
S = {
    "AC001": ("verified", ["reports/evidence/release/clean_import.txt"], "Fresh copy (no .godot cache) imported headless; the first pass logs the usual font-before-import notice, the second pass is clean."),
    "AC002": ("verified", [], "The connected folder held only the two handoff markdown files; nothing there was overwritten (deliverables go to new subfolders)."),
    "AC003": ("verified", ["tools/compile_content.py", "reports/evidence/release/compile.txt"], "Compiler fails on unknown ops, refs, maps, scenes, ragged grids; --strict fails on pending location refs."),
    "AC004": ("partial", ["tools/validate_pack.py", "reports/evidence/release/compile.txt"], "Starter kits, shops (by chapter tier), chests, quests and salvage cover the catalog; no automated per-item source trace yet."),
    "AC005": ("verified", ["reports/evidence/final_chain/b1.txt"], "B1 route: Title -> New Game -> Brackenford with normal input."),
    "AC006": ("partial", ["game/src/autoload/settings.gd"], "Joypad buttons/axes are bound for every action; no physical controller session was run."),
    "AC007": ("partial", ["reports/evidence/final_chain/screens/"], "Captures reviewed at 320x240; long objective toasts now wrap. Not every panel was inspected at every scale."),
    "AC008": ("partial", ["game/src/autoload/settings.gd"], "Rebinding and pause-on-focus-loss are implemented and persisted; not exercised by an automated test."),
    "AC009": ("partial", ["game/src/autoload/settings.gd"], "Shake/flash toggles and volume exist; tells are text + icon so they survive reduced effects. Not separately play-tested."),
    "AC010": ("partial", ["tools/check_reach.py", "reports/evidence/release/check_reach.txt", C], "Offline: every entity reachable and every arrival spawn reaches every exit of its room. Runtime: all story doorways crossed by the chained routes."),
    "AC011": ("partial", ["content_src/scenes/"], "Wrong valve/relay/dial/bell choices reset or explain without consuming items; verified by design review and partly by routes (not every wrong input automated)."),
    "AC012": ("partial", ["reports/evidence/final_chain/screens/"], "Y-sorted actors/props and door interaction verified in captures; no systematic sweep."),
    "AC013": ("partial", ["game/src/field/field.gd"], "Meter advances only on completed steps on encounter terrain; menus/switches/wall pushes cannot step. Not unit-tested."),
    "AC014": ("verified", [T], "test_post_state::test_landing_needs_marked_field."),
    "AC015": ("verified", [T], "test_battle_core::test_fixed_step_determinism."),
    "AC016": ("verified", [T], "test_battle_core::test_wait_vs_active."),
    "AC017": ("verified", [T], "test_battle_core::test_mp_reservation."),
    "AC018": ("verified", [T], "test_battle_core::test_item_reservation_last_phoenix."),
    "AC019": ("verified", [T], "test_battle_core::test_fallen_target_retarget, test_revive_refund_when_no_fallen."),
    "AC020": ("verified", [T], "test_battle_core::test_actor_ko_while_casting_refunds."),
    "AC021": ("verified", [T], "test_battle_core::test_simultaneous_wipe_defeat_priority."),
    "AC022": ("verified", [T], "test_battle_core::test_status_durations_and_hard_control, test_haste_slow_exclusive, test_boss_immunities_and_delay_cap."),
    "AC023": ("verified", [T], "test_battle_core::test_defense_stacking_cap."),
    "AC024": ("verified", [T], "test_battle_core::test_counter_no_recursion."),
    "AC025": ("verified", [T], "test_battle_roles::test_dain_oaths_exclusive_and_sacrifice_caps, test_shelter_intercepts_low_ally_once."),
    "AC026": ("verified", [T], "test_battle_roles::test_tessa_overcast_costs_and_nonlethal, test_heat_exchange_limits."),
    "AC027": ("verified", [T], "test_battle_roles::test_corren_airborne_no_softlock."),
    "AC028": ("verified", [T], "test_battle_roles::test_ivo_mine_and_decoy."),
    "AC029": ("partial", [T], "test_battle_roles::test_nera_mark_bonus_not_multiplied; bestiary persistence covered by save round trip, not a dedicated test."),
    "AC030": ("verified", [T], "test_battle_roles::test_oriel_omen_reads_only_committed."),
    "AC031": ("verified", [T], "test_battle_roles::test_sable_single_infusion."),
    "AC032": ("verified", [T], "test_battle_roles::test_pip_steal_caps."),
    "AC033": ("verified", [T], "test_battle_core::test_concord_accounting."),
    "AC034": ("verified", [T], "test_campaign::test_vestige_unique_links."),
    "AC035": ("verified", [T], "test_campaign::test_two_handed_swap_returns_offhand."),
    "AC036": ("verified", [T], "test_battle_roles::test_accessory_spell_removed_with_accessory; test_formulas::test_equipment_change_does_not_regrow."),
    "AC037": ("verified", [T], "test_campaign::test_shop_boundaries; test_post_state::test_every_shop_lists_stock_at_every_stage (regression for the tier-key crash found by the seg8 route)."),
    "AC038": ("verified", [T], "test_campaign::test_unique_overflow_goes_to_delivery."),
    "AC039": ("verified", [T], "test_campaign::test_reserve_growth_and_reunion; test_formulas::test_join_level."),
    "AC040": ("partial", [T, "reports/evidence/final_chain/b1.txt"], "test_campaign::test_save_round_trip; B1 saves at a lamp, returns to title and reloads through the menu. Ship/pre-boss reloads not separately automated."),
    "AC041": ("verified", [T], "test_campaign::test_corrupt_primary_offers_backup."),
    "AC042": ("verified", [T], "test_campaign::test_future_schema_rejected."),
    "AC043": ("verified", [T], "test_campaign::test_crash_during_write_keeps_complete_state."),
    "AC044": ("verified", [T], "test_story::test_skip_equivalence."),
    "AC045": ("verified", [T], "test_story::test_once_scene_not_reapplied; test_post_state::test_personal_quest_reward_once."),
    "AC046": ("verified", [C], "Normal-input chain: b1 (New Game..CH01) -> seg2 -> seg3 -> seg4 -> seg5 (CH11, then CH12), each segment resuming from the milestone the previous one wrote. No flag edits in routes."),
    "AC047": ("verified", [T, C], "test_campaign::test_catastrophe_transaction_preserves_ownership; test_post_state::test_catastrophe_scene_commits_post_state; seg5 reaches Hearthward through the real scene."),
    "AC048": ("verified", [T], "test_campaign::test_salvage_forwarding_once."),
    "AC049": ("verified", [C], "seg6: CH13-CH16 with the two-, three- and four-person party; Wayfarer earned in play."),
    "AC050": ("partial", [T, C], "test_post_state::test_reunion_orders_all_six runs the real completion scenes in all six orders; the routes play one order (CH17, CH18, CH19) end to end."),
    "AC051": ("partial", [C, T], "segq plays Q01-Q08 to COMPLETED with normal input (rewards and final techniques granted); reload at every stage is covered only by the quest-state tests, not per stage in play."),
    "AC052": ("verified", [C], "segq defeats B13, B14, B15 and B16 (Q12 before the final commitment) and receives V07, V08, A023, A024; defeat/Retry paths occurred in dev runs."),
    "AC053": ("partial", [C, T], "seg8 plays the default balanced split; unbalanced splits are allowed by the split screen (healer warning) but not route-tested."),
    "AC054": ("verified", [T], "test_post_state::test_team_locks_alternate_without_trapping."),
    "AC055": ("partial", [T], "test_battle_core::test_boss_phase_threshold_once; B12 fought in seg8."),
    "AC056": ("verified", [C], "seg8 finishes CH22-CH24 with zero optional quests; the ending, credits and clear save complete."),
    "AC057": ("partial", ["content_src/scenes/ch22.scn"], "Each epilogue line branches on its quest flag; only the zero-quest combination is route-played."),
    "AC058": ("verified", [C], "seg8 chooses Continue from Before the Final Descent and lands at the Accord Dock with the post_clear flag."),
    "AC059": ("partial", ["reports/asset_ledger.json"], "Generated sprites reviewed by the agent only; status 'generated', not final art."),
    "AC060": ("partial", ["reports/evidence/final_chain/screens/"], "Every location has its own composition; art is programmatic and plain in places."),
    "AC061": ("unverified", ["reports/audio_ledger.json"], "Cue switching implemented; no listening test (headless audio is a dummy driver)."),
    "AC062": ("partial", [C], "Route traces record level, battles and resources per segment; the bot takes direct paths, so it is a lower bound for play time."),
    "AC063": ("unverified", ["game/src/story/director.gd"], "level_floor milestone growth exists for encounters-off; no campaign segment run in that mode."),
    "AC064": ("verified", ["reports/evidence/release/clean_export.txt"], "Clean copy imported and exported the Windows build with no author-machine paths."),
    "AC065": ("unverified", [], "Build copied to the owner's folder and checksum-verified there; it was not launched on Windows (computer use could not run an unregistered executable)."),
    "AC066": ("verified", ["reports/asset_ledger.json", "reports/audio_ledger.json", "game/licenses/"], "All art/audio/font generated by project code; Godot MIT license and third-party notices bundled."),
    "AC067": ("verified", [C, T], "Final chain, runtime tests and clean-archive export all ran on revision 7428b37 / content e528220ab0ff6194 (logs print the content hash)."),
    "AC068": ("owner", [], "Needs the owner or a separate human tester; agent self-review is not a substitute."),
}


def main():
    out = []
    for (acid, area, title, how, expect) in ROWS:
        st, ev, note = S.get(acid, ("unverified", [], ""))
        out.append({"id": acid, "area": area, "title": title.strip(), "procedure": how.strip(), "expected": expect.strip(),
                    "status": st, "evidence": ev, "note": note})
    ch = hashlib.sha256(open(os.path.join(ROOT, "game", "content", "content.json"), "rb").read()).hexdigest()[:16]
    json.dump({"content_sha": ch, "criteria": out}, open(os.path.join(ROOT, "reports", "requirements_ledger.json"), "w"), indent=1)
    counts = {}
    for r in out:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    lines = ["# Requirements ledger (docs/15 acceptance criteria)", "", f"Content build {ch}. Counts: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())), "",
             "| ID | Area | Criterion | Status | Evidence / note |", "| --- | --- | --- | --- | --- |"]
    for r in out:
        lines.append(f"| {r['id']} | {r['area']} | {r['title']} | {r['status']} | {r['note']} |")
    open(os.path.join(ROOT, "reports", "requirements_ledger.md"), "w").write("\n".join(lines) + "\n")
    print(counts)


if __name__ == "__main__":
    main()
