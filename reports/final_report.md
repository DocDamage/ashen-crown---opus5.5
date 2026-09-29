# The Ashen Crown — build report

Revision: git `7428b37` (local repository; nothing pushed). Content build `e528220ab0ff6194`.
Engine: Godot 4.7.2-stable (`4.7.2.stable.official.ed1daf0bf`), Compatibility renderer, 320x240 internal.

## What exists

- **Complete campaign content**: CH01–CH24 (440 scenes), 128 maps, 12 dungeons (D01–D12), 7 towns incl. the
  post-only Hearthward, 8 heroes, 16 bosses (B01–B16), 12 optional quests (Q01–Q12), 8 Vestiges, two authored
  overworlds (pre / post catastrophe) with shared location IDs, the airship Wayfarer (board, fly, land at marked
  fields, recall, deck with formation/stores/rest/crew board), the two-team final dungeon, epilogues, credits with
  the post-credits relay-garden image, a clear save and the labelled post-clear return.
- **Editable source**: `game/` (Godot project), `content_src/` (maps + scenes), `tools/` (content compiler, map
  scripts, art/audio/font generators, reachability/world audits, packaging, chain runner), `docs/` (design package).
- **Windows build**: `AshenCrown.exe` (single file, data embedded), exported from a clean `git archive` of the
  revision (not from the working tree). SHA-256 `df9d11283a76138f9d27bbeccece66eadb5bd03699552c7232c9b80e0c8a6aae`.

## Evidence (all produced by this revision unless marked)

| What | Result | Where |
| --- | --- | --- |
| Runtime tests (in engine) | 57 passed, 0 failed | `reports/evidence/tests/runtime_tests_final.txt` |
| Content compile, strict refs, font-glyph coverage | OK | `reports/evidence/release/compile.txt` |
| Reachability (every entity; every arrival spawn reaches every exit) | 0 problems | `reports/evidence/release/check_reach.txt` |
| World audit (landings have ground; every post location reachable) | OK | `reports/evidence/release/check_world.txt` |
| Clean-archive import + Windows export | OK | `reports/evidence/release/clean_*.txt` |
| Normal-input route chain New Game → credits → post-clear, plus all 12 quests | CHAIN PASS | `reports/evidence/final_chain/` |

### Route chain

The route bots press the same InputMap actions a player does and read only what is on screen/map to decide.
They never edit flags, HP or positions. The campaign is played in segments; each segment starts from the
milestone the previous segment wrote at its end (a save/load handover), so the whole chain is one continuous
playthrough starting from New Game:

| Segment | Covers | Result | Battles | Party level at end |
| --- | --- | --- | --- | --- |
| b1 | Title, New Game, CH01 (B01), lamp save, return to title, Continue, state compared | PASS | 4 | 6 |
| seg2 | CH02-CH04 (B02, B03, B04) | PASS | 5 | ~13 |
| seg3 | CH05-CH07 (chase, B05, ferry, B06) | PASS | 4 | ~16 |
| seg4 | CH08-CH10 (B07, B08, three accords, SC07) | PASS | 5 | ~20 |
| seg5 | CH11-CH12 (B09, B10, escape, catastrophe, Hearthward) | PASS | 2 | ~22 |
| seg6 | CH13-CH16 (two/three/four-person party, B11, SC09, Wayfarer launch) | PASS | 3 | ~24 |
| seg7 | CH17-CH20 by airship (Corren, Pip, Sable; Ash Accord) | PASS | 2 | 29 |
| seg8 | Shopping, grinding, CH22 split teams, B12, SC11, CH23 epilogues, CH24, clear save, credits, post-clear return | PASS | 13 | 33 at B12 |
| segq | All twelve optional quests Q01-Q12 incl. B13-B16 (from the same CH20 milestone) | PASS | 37 | 38-39 |

Chain log: `reports/evidence/final_chain/chain.txt` ("CHAIN PASS"); every segment log prints content hash
`e528220ab0ff6194`. Screenshots from these runs: `reports/evidence/final_chain/screens/`. Earlier development runs
(older builds, kept for history only) are under `reports/evidence/dev_runs/`.

The bot plays the direct route (few detours), buys supplies, uses Equipment > Optimize, and grinds in ordinary
encounter rooms before the final dungeon and the optional bosses; its levels are therefore a lower bound on
what a player would have.

## Bugs found by the routes and fixed this session

- Every weapon/armor shop's Buy list crashed (`str(1.0)` tier key) — players could not buy gear at all.
  Fixed; regression test `test_every_shop_lists_stock_at_every_stage`.
- Encounter meter reset on every room change, so short dungeon rooms almost never produced battles.
- D04 Blue Valve room, D05 Witness Vault and D03 Hollow Grove had entrances sealed off by pipes/shelves/trees.
- Missing save lamps before several bosses; boss names clipped in the battle panel; long objectives overflowed.
- Em-dashes rendered as missing-glyph boxes (compiler now normalizes and fails on any glyph the font lacks).
- D06 and D12 post-state locations were unreachable (island/reef without ground); Q11's boss trigger never armed.

## Balance changes (recorded in `reports/decisions.md`)

B11 is fought by the two-person recovery party (no escort add, x0.72 attack); catch-up XP after each story level
floor (+35 % per level below floor+4, cap x4); Hearthward supplies give Ethers; CH20 floor 33.

## Visual pass 2026-09-29 (FF6-inspired, owner request)

Commits after `66f6be5`: groundwork, character art, battle art, UI, field tiles, render caching. Content hash
unchanged (`e528220ab0ff6194`); only presentation code and art changed.

- **Look**: SNES Final Fantasy VI conventions (docs/11 revision): blue-gradient bevelled windows with a hand cursor
  and a Window colour setting; autotiled 16x16 field tiles with shorelines, cliffs, walls with dark tops and
  cast shadows, forests of tall pines; Time Fantasy field sprites recoloured to the character bible; side-view
  party in battle against large relit enemies on panoramic backdrops; new title screen and logo.
- **Art source**: owner-licensed library packs assembled by `python tools/gen_art.py library` into git-ignored
  `game/assets/ext/` (licences allow game use, not raw redistribution); the committed generated art remains the
  fallback. Credits: `game/licenses/ART_CREDITS.txt`; per-asset sources/licences: `reports/asset_ledger.json`.
- **Renderer**: library ground is composited per 16x16-cell chunk into textures (animation frames pre-baked),
  one quad per chunk; overhanging objects are y-sorted. Field frame time is at or below the old generated renderer.
- **Evidence** (`reports/evidence/art_chain/`): runtime tests 57/57; reachability 0 problems; world audit OK;
  normal-input chain b1 → seg2..seg7 → seg8 ∥ segq = **CHAIN PASS** on this art (seg8 13 battles, segq 37);
  re-run after the props pass: CHAIN PASS again (`reports/evidence/props_chain/`), tests 57/57.
  A first chain run exposed a frame-rate regression (airship legs overshooting at `--qa-speed 4`); fixed by the
  chunk renderer, then the full chain was re-run from New Game.
- **Review tools**: `--qa-gallery` (title/menus/field/battles), `--qa-gallery-set map:ALL` (stitched maps),
  `--qa-gallery-set perf:IDS` (field frame time). Dev-only; never gameplay evidence.
- **Props pass (same day)**: tents, awnings (two-cell "pair" rule: a run pairs up from its left end), statues,
  pillars, signs, counters, bells and floor grates now come from Time Fantasy pieces; rails, laundry lines and
  world-map mountains are composed in code from library pixels (no ready-made piece exists in the library).
  Mountains are FF6-style peaks with a lit left flank, variants per cell and a snow-capped inner peak.
  The party is drawn at 2x in battle on a wider diagonal (FF6 weight next to the large enemies).
- **Open**: licence confirmations for the Time Fantasy "Elements" kit and ansimuz packs (owner). Still generated:
  carts, boats, murals, sluices, lifts, braziers, altars, anvils, vines, cables, tall pipes and the world-map
  town/dungeon markers.

## Known limitations

- **Windows launch not verified on Windows.** The build was exported and its checksum verified after copying to
  your folder, but no Windows run happened here (computer-use could not launch an unregistered .exe). AC065/AC068 are open.
- Art, music and sound are programmatic (generated by project code); functional and consistent, plain in places,
  not final-quality art or audio. No listening review was possible (headless dummy audio driver).
- Reunions are played in one order by the routes; all six orders are verified at the state level by a test that
  runs the real completion scenes.
- Only the zero-optional-quest ending was route-played; enhanced epilogue lines are branches not individually played.
- Encounters-off mode, controller-only play, key remapping and reduced-effects play were not exercised end to end.
- Full acceptance status per criterion: `reports/requirements_ledger.md`.

## Resume

`RESUME_PROMPT.md` + `CURRENT_STATE.json`. Re-run everything with `tools/run_chain.sh`, `--qa-tests`, and
`tools/package.sh`.
