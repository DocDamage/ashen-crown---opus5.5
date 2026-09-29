# Start here — The Ashen Crown

This is the game’s design and autonomous-build handoff, **not a playable game**. Keep it in a new dedicated folder. Do not extract it over an existing project or ask an agent to replace older JRPG canon with it.

## Immediate workflow

1. Extract the ZIP into a new folder and open that folder in your IDE/Claude Code workspace.
2. Read `docs/00_CANON_AND_SCOPE.md` and skim `docs/01_GAME_VISION.md`. `MASTER_HANDOFF.md` is the combined reading copy; specialist files and JSON are easier for implementation.
3. Select the actual Opus 5.5 option available in the host’s model selector. In Claude Code, verify the model through its model configuration UI/command rather than trusting a chat sentence or an assumed alias. Host/account availability is not guaranteed by this package. [S6]
4. Run the package checks below. Configure the Godot executable with `GODOT_BIN` or `--godot`; the environment doctor checks it without installing anything.
5. Paste the contents of `KICKOFF_PROMPT.md`. The agent should build the complete campaign through internal gates, not stop after writing more planning documents.

The root `CLAUDE.md` is intentionally short; it points to detailed specifications instead of importing the entire bible into every turn. Claude project instructions supply context, not a security boundary. Use the host’s real permissions and a dedicated workspace. [S3, S4] Do not disable all protections on your ordinary desktop just to reduce prompts. No remote push, paid service or large asset/model download is authorized by the kickoff.

## Commands that work in this package now

From the extracted package directory, using Python 3.10 or newer:

```text
python tools/validate_pack.py
python -m unittest discover -s tools -p "test_*.py" -v
python tools/doctor.py
```

On Windows, `py -3` may be used instead of `python` when that launcher is available. The first command validates design records. The second tests the validator and helper behavior. The third checks this machine’s environment and may correctly report that Godot is missing. None launches a game because `game/project.godot` has not been created yet.

To select an already installed Godot executable explicitly:

```text
python tools/doctor.py --godot "C:\Tools\Godot\Godot_v4.7.2-stable_win64_console.exe"
```

That path is an example, not a discovered path on your computer. Replace it with the actual executable. Matching export templates are checked later by the real export step. Do not assume that a successful `--version` check proves templates, rendering or controller access.

## Commands for the agent to establish after implementation

The following are templates, **not runnable completion checks for the current pack**. The agent must create the referenced project, runner and export preset, then record actual outcomes. [S2]

```text
<GODOT_BIN> --headless --path game --import
<GODOT_BIN> --headless --path game --script res://tests/run_all.gd
<GODOT_BIN> --path game -- --qa-route opening --qa-capture
<GODOT_BIN> --headless --path game --export-release "Windows Desktop" <ABSOLUTE_BUILD_PATH>/AshenCrown.exe
```

`--qa-route` and `--qa-capture` here are proposed project user arguments after `--`, not built-in Godot features. They must be implemented and tested. A headless run cannot substitute for screenshot evidence. Export success cannot substitute for launching the Windows executable on Windows.

## Included versus future work

Included: plot, cast, geography, room plans, mechanics, acquisition rules, content catalogs, key scene dialogue, six reference prompts, audio briefs, acceptance matrix, agent workflow and package utilities. Future work: actual Godot implementation, full NPC dialogue, final sprites and animation, generated/rendered maps, recorded music/SFX, runtime tests, balancing and playable export. `CURRENT_STATE.json` starts honestly at PACK_AUTHORED; it contains no invented game progress.
