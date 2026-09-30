# Overhaul step 3+ progress (engine rebuild onward)

Owner instruction 2026-09-30: "just work on the project from here to finish, i will worry about missing audio later".
Work happens on the owner's PC (device shell, Godot 4.7.2 Linux build in the VM at ~/bin/godot, Xvfb for captures);
long QA chains run in the cloud workspace from a tar of `game/` (the device shell kills background jobs per call).

## Done
- Engine: 960x720 (layouts in 320x240 units, layers x3), native-resolution text and frames, party of five,
  Easy/Normal/Hard, Mature setting, naming on join, Name-Keeper NPC (`rename`) in Brackenford and Hearthward.
- Cast: 17 heroes with field/battle/portrait art; C01-C08 renamed (Raven, Morwen, Vespera, the Golem, Elowen, Aurex,
  Oni, Sak) and the whole script rewritten for them (scenes, quests, map text, docs 02/03/17; guide
  docs/overhaul/STORY_GUIDE.md). Post-fault airship text is the Lanternwake.
- New heroes in the story (content_src/scenes/overhaul.scn, called from mandatory chapter scenes so skips give the same
  state): Archangel CH07 (High Landing), Kitsune CH10 (Nacre), Corvus CH13 (Hearthward), Inferna CH14 (flooded
  Rootward); reunions Archangel CH17, Kitsune CH19. Secret recruits with trial fights: Lich King (D11_R05 after Q09),
  Maldrath (T01_POST after CH20), Velkhar (D07P_R03 after CH19), Kael-09 (D08P_R01 after CH16), Night Rider (D04P_R01
  after CH16). Vestiges V09-V12 wait in the field (drawn from their summon art) with trials. Placement:
  tools/maps48/place_entities.py (tagged `#! ov:` lines).
- Vehicles: Brackhorn mount from CH03 (world map, faster, no encounters; Settings "Ride Brackhorn"); pre-fault Wayfarer
  airship at the end of CH10 (landing fields on WORLD), lost at the Crown Dais in CH12; Lanternwake world sprite with
  8-direction frames and shadow (tools/art/install_overhaul.py vehicles; game/src/field/vehicle_art.gd).
- Battle: painted arenas, native heroes, sprite VFX, Vestige summons; **enemy art** for all 40 enemies and 16 bosses at
  native resolution from the owner's packs (install_overhaul.py enemies: BD-09, Factory Monster Pack, Monster Mega
  Pack, Giant Boss, RuneFoundry) with bob, casting pulse and hit flash. Final split: two teams of five, others in reserve.
- Audio: soundtrack casting, jingles, library SFX (deferred sounds listed in Assets\SFX\deferred_sfx_map.json).
- Maps at native 48px: Winlu world maps; hand-made towns (Brackenford pilot; Veyr, Brackenford post, Cinderwake,
  Bellharbor, High Aerie, Nacre, Hearthward - tools/maps48/maps/*.py, guide docs/overhaul/TOWN_GUIDE.md, owner's
  standard docs/overhaul/LAYOUT_STANDARD.md); auto-skins for dungeons and interiors with per-spawn reachability-safe
  dressing.
- Checks: compile_content OK; tools/check_reach.py 0 problems; tools/check_entities_reach.py (stricter, solid NPCs
  block; the 14 remaining hits are counters, barred cells and flag-opened pools by design); runtime tests 64/64;
  full normal-input chain passes (b1, seg2-seg8, segq: New Game to the ending plus all optional quests).

## Known gaps
- Deferred sound effects (owner will handle audio later).
- Conditional map art (tileset_over / block) changes collision but not the 48px art (e.g. raised walkways, rebuilt
  crossings look the same before and after).
- The Lanternwake is not drawn at its berth in Hearthward; no raised decks in Hearthward.
- Windows build: `F:\Ashen Crown\The Ashen Crown\Windows\AshenCrown.exe` (Godot 4.7.2 export, licensed art inside the
  .pck; previous build kept in Windows_previous_pre_overhaul). Export templates were installed in the device VM at
  ~/.local/share/godot/export_templates/4.7.2.stable.
