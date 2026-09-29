# The Ashen Crown

An original pixel-art JRPG built in Godot 4.7.2 from the design package in `docs/` (combined copy:
`Ashen_Crown_Master_Handoff_v0_1.md`). Four-person active party from eight heroes, ATB command battles,
an irreversible midpoint catastrophe, reunions in any order, the airship Wayfarer, optional personal quests,
a two-party final dungeon and a definitive ending.

## Play (Windows)

Run `AshenCrown.exe` (single file, the game data is embedded). Saves and settings live in
`%APPDATA%\AshenCrown\`. The window opens at 4x (1280x960) and scales by whole pixels.

### Controls

| Action | Keyboard | Controller |
| --- | --- | --- |
| Move | Arrow keys / WASD | D-pad / left stick |
| Confirm / talk / examine | Z, Enter, Space | A |
| Cancel / back | X, Esc, Backspace | B |
| Menu | C, Tab | Y |
| Run (hold, or toggle in Settings) | Shift | X |
| Page left / right (menus) | Q / E | LB / RB |
| Skip scene | V | Back |

Keys can be rebound in Menu > Settings. Battles default to **Wait** mode (time stops while you choose);
**Active** is available in Settings, as are text speed, screen shake, flashes, encounter rate
(normal / reduced / off with milestone growth) and volume.

Tips: save at lamps, on the world map, or aboard Wayfarer. Enemy intentions are shown as text above the
battle; Defend through telegraphed attacks. Equipment > Optimize equips your strongest owned gear.

## Build from source

```
set ASHEN_LIB=G:\All 2D Assets Stay Here   # owner's licensed art library (see below)
python tools/gen_art.py library          # assemble library art -> game/assets/ext/ (git-ignored)
python tools/compile_content.py          # data + maps + scenes -> game/content/content.json
godot --headless --path game --import
godot --headless --path game -- --qa-tests --qa-out /tmp/qa        # runtime tests
godot --headless --path game --export-release "Windows Desktop" ../build/windows/AshenCrown.exe
```

### Art: licensed library + generated fallback

The FF6-inspired look uses the owner's licensed pixel-art packs (Time Fantasy, ansimuz, Haydeos and others;
see `game/licenses/ART_CREDITS.txt`). Their licences allow use in the game but not redistribution of the raw
files, so they are never committed: `tools/gen_art.py library` reads them from `ASHEN_LIB` and writes the
assembled atlases/sheets to `game/assets/ext/`, which the game prefers at runtime (`Content.art`). Without the
library the game still runs on the project's own generated art. `tools/package.sh` copies `ext/` into the
clean export so the Windows build ships the full art. Dev screenshots:
`godot --path game -- --qa-gallery --qa-out <dir>` (or `--qa-gallery-set map:ALL` for whole-map captures).

Requires Godot 4.7.2-stable and its Windows release export template. See `CLAUDE.md` for every pipeline
(art, audio, font generators, map scripts, reachability checks, route bots) and `reports/` for evidence,
the requirements ledger, decisions and known limitations.
