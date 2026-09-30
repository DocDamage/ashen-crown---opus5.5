# Overhaul step 3+ progress (engine rebuild onward)

Owner instruction 2026-09-30: "just work on the project from here to finish, i will worry about missing audio later".
Work happens on the owner's PC (device shell, Godot 4.7.2 Linux build in the VM at ~/bin/godot, Xvfb for captures).

## Done
- Engine: 960x720 viewport; UI/world layers scaled x3 (layouts stay in 320x240 units); text (Pixelated Elegance, GGBotNet
  CC0) and window frames drawn at native resolution; party of five; Easy/Normal/Hard (per save, enemy HP x0.75/1/1.35,
  damage x0.8/1/1.2); Mature setting with one-time 18+ confirmation; name entry on joining + `name`/`rename` scene commands.
- Cast: tools/art/hero_import.py + hero_cast.json -> assets/ext/heroes/<cid>/ (field 4-dir sheet, battle strips, portrait).
  tools/content/cast.py renames C01-C08 (Raven, Morwen, Vespera, Rune Golem, Elowen, Aurex, Crimson Oni, Sak) and adds
  C09-C17 with kits S101-S172 and signature commands. New heroes share an original hero's equipment class.
- Battle: painted arenas (install_overhaul.py arenas), heroes at native size with their own animations, 5-row panel,
  sprite spell/buff effects from the owner's packs (install_overhaul.py vfx -> fx.json), status effects.
- Audio: soundtrack casting M001-M030 + M101-M126, fanfare jingles (victory, inn, join ...), library SFX (FX001-FX057).

## Next
- Vestiges V01-V12 (renames, records, Esper-style learning); spell icons in menus.
- Enemy art (best-fit library art per enemy, native resolution).
- Field at 48px native (CuteSCKR skins), Tiled import, map rework by region, world maps (Winlu), NPC townsfolk.
- Story: names/pronouns in scripts, join scenes for C09-C12, secret recruit sites for C13-C17, Brackhorn, Lanternwake.
