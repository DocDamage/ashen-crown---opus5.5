# Expansion systems: working brief (for each systems author)

You work in your own git worktree of the game (branch `s1`…`s4`); other authors build other systems in parallel and
the lead merges the branches. Commit your work on your branch (`git -c user.name=Claude -c user.email=noreply@anthropic.com
commit ...`) in logical steps. Keep your changes inside your scope; when you must touch a shared file (`game.gd`,
`field.gd`, `battle_model.gd`, `game_menu.gd`, `main.gd`, `settings.gd`, `compile_content.py`), make small, additive
edits (new functions, new dictionary keys, one-line hooks) so merges stay clean. Never reformat or reorder code.

## The project
- Godot 4.7 SNES-style JRPG (FF6 feel). Logical resolution 320x240 "units", rendered at 960x720 (`UI.U = 3`).
  Read `game/src/ui/ui.gd` (drawing helpers: `UI.win`, `UI.text`, `UI.width`, themes), `game/src/ui/menu_list.gd`
  (the list widget every menu uses), `game/src/ui/game_menu.gd` (field menu pages: items, equip, abilities,
  formation, vestiges, journal, world map, bestiary, settings, save/load, shops, smith, inn), `game/src/main.gd`
  (router, transitions, battles), `game/src/autoload/game.gd` (the save state `Game.S`, conditions `eval_cond`,
  items, party), `game/src/autoload/settings.gd` (player settings + input actions), `game/src/core/battle_model.gd`
  (ATB battle simulation) and `game/src/battle/battle_scene.gd` (battle drawing/input), `game/src/field/field.gd`
  (exploration), `game/src/story/director.gd` (scene commands).
- Content is compiled from `data/*.json` + `tools/content/*.py` + `content_src/maps|scenes` by
  `python3 tools/compile_content.py` into `game/content/content.json` (must end `compile_content: OK`).
  New content modules go in `tools/content/` and are hooked into `compile_content.py` with one import + one call.
- Design bible: `docs/expansion/WORLD_V2.md` (read it: sections 6-11 list the systems). The owner's answers to the
  design questions are summarised in its introduction; follow them.

## Testing (required)
- Unit tests: `game/tests/unit/test_*.gd` (see existing ones; `TestCase` helpers `eq`, `check`, `fresh_game`).
  Add tests for your systems. Run all:
  `cd game && timeout 900 xvfb-run -a -s "-screen 0 1280x1024x24" /home/claude/ac/godot --headless --path . -- --qa-tests`
  → must print `TOTAL N passed, 0 failed`.
- After adding new resources (PNGs) run an import once: `cd game && timeout 1500 /home/claude/ac/godot --headless --path . --import`.
- Visual check: `--qa-gallery-set <set>` in `game/src/autoload/qa.gd` takes screenshots (`--qa-out DIR`); add a
  gallery set for your screens (for example `sys_s2`) and look at the PNGs with the Read tool.
  `cd game && timeout 600 xvfb-run -a -s "-screen 0 1280x1024x24" /home/claude/ac/godot --path . -- --qa-gallery-set sys_s2 --qa-out /tmp/sys_s2`
- Do not break the QA story routes (`game/src/qa/routes.gd`): they drive the real game with inputs. New menus must
  not pop up by themselves on the routes' paths; new battle mechanics must keep the old fights winnable by the bot
  (it uses Attack/Defend/items/abilities). If a new system changes a default, keep the old behaviour when the
  save/setting says so.

## Conventions
- Save state lives in `Game.S`; add new keys with defaults in `new_game()` AND read them with `.get(key, default)`
  so old saves still load.
- Player-facing text: short, FF6-length, the house tone (grim, dry, never silly). No emojis.
- Art: only use images that exist under `game/assets/` (the owner's licensed packs are already installed there,
  e.g. `assets/ext/...`). If you need new art from the owner's packs, write an install script under `tools/art/`
  that copies/cuts from `$ASHEN_ASSETS` (the packs root) into `game/assets/ext/<folder>`, document it, and use a
  clean fallback (drawn rectangles/text) when the files are missing; the lead runs the script on the owner's PC.
- Keep everything data-driven where the game already is (content.json), and deterministic in battle (seeded RNG).
