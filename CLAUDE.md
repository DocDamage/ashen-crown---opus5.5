# The Ashen Crown — agent contract

Original pixel-art JRPG built from the design package in `docs/` (combined copy: `Ashen_Crown_Master_Handoff_v0_1.md`).
Godot 4.7.2 Standard, GDScript, Compatibility renderer, 320x240 internal viewport. Project in `game/`.

Read first: `START_HERE.md`, `docs/00_CANON_AND_SCOPE.md`, `docs/14_AUTONOMOUS_EXECUTION_PLAN.md`, `CURRENT_STATE.json`,
then `reports/decisions.md` (authored decisions not present in the handoff).

Pipelines (run from repo root; Python 3.10+):
- `python tools/extract_catalogs.py` — rebuild `data/*.json` from docs (the package JSON was not supplied).
- `python tools/validate_pack.py` and `python -m unittest discover -s tools -p "test_*.py"` — design data checks only.
- `python tools/maps/<file>.py` — map authoring scripts -> `content_src/maps/*.map`.
- `python tools/compile_content.py [--strict]` — compile catalogs + `tools/content/*` + maps + scenes -> `game/content/content.json`.
- `python tools/check_reach.py` — offline map reachability.
- `python tools/gen_art.py`, `python tools/gen_audio.py`, `python tools/gen_font.py` — deterministic original assets.
- Runtime tests: `godot --headless --path game -- --qa-tests --qa-out <dir>` (or `--script res://tests/run_all.gd`).
- Normal-input routes: `godot --path game -- --qa-route <b1|...> --qa-capture --qa-out <dir> [--qa-speed 4]` (needs a display).

Rules: never edit story flags, HP or positions to get a route past a failure; fix the game. Keep the full campaign scope.
Do not claim unverified results; record evidence in `reports/`. No remote push, paid services or large downloads.
