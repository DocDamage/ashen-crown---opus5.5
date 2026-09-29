# Audio and music direction

## Delivery boundary

This package supplies thirty music cues and thirty-two SFX slots as briefs. It contains no recorded or synthesized audio files. A coding agent may generate temporary original material to exercise the system, but “a WAV exists” does not establish a finished soundtrack. The owner can replace any cue with their own composition without changing scene logic or rebuilding the battle system.

## Musical identity

Use original melodic material, sound design and arrangements. The reference is the emotional role of a compact game score, not copying a composer’s recognizable tune or importing a commercial sound bank. Suggested original main-theme scale-degree contour: 1, 5, 4, 2, flat-3, then a rest; its final cadence is withheld until the ending. This is a compositional starting point, not finished music.

Each character has a short motif that may appear in town, scene and ending arrangements. Major locations need distinct harmonic and rhythmic behavior, not the same MIDI file assigned a different instrument. Battles need an opening accent, a main phrase, a contrasting section and a loop point that survives repeated encounters. The catastrophe ends with meaningful silence. The refugee-town arrangement carries familiar material with changed instrumentation rather than only sounding miserable.

Prefer a coherent limited instrument palette: warm sampled-style strings, restrained brass, breathy reeds, plucked strings, mallet tones, bass, light acoustic percussion and controlled noise-based effects. Programmatic synthesis is permitted for development; it must not be mislabeled as a polished human-composed final score.

## Runtime contract

MusicManager uses stable cue IDs from the catalog. Game scenes request semantic cues, not absolute local file paths. A cue resource contains stream path, loop bounds, intro/loop/outro behavior, gain, optional stems, transition group, composer/source and license status. Use Music, SFX, Ambience and UI buses beneath Master. Save settings separately from story progress. Mute must actually silence the intended bus after reload.

Crossfade ordinary exploration changes over about 1.2 seconds; use deliberate hard or bar-aligned transitions for battles, reveals and silence. Do not restart a looping town track every time the player enters a house if it shares the same music zone. Pause should preserve musical position unless the selected pause treatment says otherwise. Volume changes should not alter RNG, encounter timing or animation progression.

Repeated sounds require gentle variation in sample choice and level, not large random pitch shifts. Critical warnings must remain intelligible under music. Balance the actual rendered mix and measure peaks; do not infer absence of clipping from source sample values alone. Reduced-flash mode has no reason to remove critical audio feedback, and muted audio must not make a puzzle unsolvable.

## Track catalog

| ID | Cue | Use | Direction |
| --- | --- | --- | --- |
| M001 | Title — The Ashen Crown | title | Slow restrained strings, bells and low pulse; end on an unresolved suspension. |
| M002 | Dain — An Open Hand | character | Low brass and plucked strings; a repeated note opens into a fifth. |
| M003 | Tessa — Borrowed Light | character | Bright mallet and woodwind phrase that learns to leave space. |
| M004 | Corren — The Return | character | Airy flute over grounded hand percussion, not a constant heroic march. |
| M005 | Ivo — Working Hands | character | Muted metallic percussion and bass ostinato with a warm middle voice. |
| M006 | Nera — Every Road | character | Dry plucked strings, small woodwind replies, forward but unhurried motion. |
| M007 | Oriel — The Right to Refuse | character | Breathy reed and distant bell; clear rests between phrases. |
| M008 | Sable — Unwritten | character | Tight counterpoint loosening into a single candid melody. |
| M009 | Pip — Names We Keep | character | Playful offbeat figure that later returns with fewer evasive ornaments. |
| M010 | Brackenford — Shift Change | town | Warm domestic rhythm against a distant industrial pulse. |
| M011 | Veyr — Oath Square | town | Ordered brass and precise percussion with subtle harmonic tension. |
| M012 | Cinderwake — The Cooling Garden | town | Steam-like noise texture used sparingly, gentle machine rhythm. |
| M013 | Bellharbor — Tide and Paper | town | Bell and flute over a rocking bass; no direct sea-shanty quotation. |
| M014 | High Aerie — Returners’ Hall | town | Open intervals and audible breathing room. |
| M015 | Nacre — Listening Water | town | Sparse chords, plucked mineral tones, restrained reverb. |
| M016 | Hearthward — Many Small Fires | town | Main theme in warm intimate instrumentation, repaired rather than triumphant. |
| M017 | Before the Fault | overworld | Confident travel pulse; leave room for footsteps and menu cues. |
| M018 | After the Fault | overworld | Same melodic identity with missing bass notes and changed cadence. |
| M019 | Wayfarer — Ordinary Flight | vehicle | Lift and motion without a military fanfare; combines Ivo and Corren motifs. |
| M020 | Quarry and Conduit | dungeon | Low ostinato and metallic emphasis; two arrangement states. |
| M021 | Rootward | dungeon | Organic percussion and short recurring flute calls. |
| M022 | Furnace Spine | dungeon | Layered rhythmic machinery; audible rest sections before major scenes. |
| M023 | Drowned Archive | dungeon | Bell fragments and rippling counterpoint with a clear tonal center. |
| M024 | Memory Vault | dungeon | Contradictory voices resolve only after the listening scene. |
| M025 | Encounter — Broken Orders | battle | Brisk syncopation, memorable bass line and readable transition into victory. |
| M026 | Boss — Pressure Rising | battle | Strong ostinato and contrasting bridge; avoid endless identical two-bar loops. |
| M027 | Catastrophe — Crown of Cinders | story | Begins with intended release, fractures into displaced rhythm, ends in silence. |
| M028 | Crown Vessel — No One Is Fuel | final_boss | Three connected arrangements for the three phases; transitions on musical boundaries. |
| M029 | Victory and Rest | stinger | Short separate victory, recovery and discovery cues sharing the core interval. |
| M030 | The First Unborrowed Morning | ending | Complete the title’s suspended cadence; include character fragments without quoting other games. |

## SFX slots

| ID | Cue | Runtime slot |
| --- | --- | --- |
| FX001 | Menu Move | sfx/menu_move |
| FX002 | Menu Confirm | sfx/menu_confirm |
| FX003 | Menu Cancel | sfx/menu_cancel |
| FX004 | Menu Error | sfx/menu_error |
| FX005 | Page Turn | sfx/page_turn |
| FX006 | Save Complete | sfx/save_complete |
| FX007 | Chest Open | sfx/chest_open |
| FX008 | Door Wood | sfx/door_wood |
| FX009 | Door Stone | sfx/door_stone |
| FX010 | Switch Lever | sfx/switch_lever |
| FX011 | Footstep Stone | sfx/footstep_stone |
| FX012 | Footstep Wood | sfx/footstep_wood |
| FX013 | Footstep Shallow Water | sfx/footstep_shallow_water |
| FX014 | Sword Swing | sfx/sword_swing |
| FX015 | Sword Impact | sfx/sword_impact |
| FX016 | Guard Impact | sfx/guard_impact |
| FX017 | Arrow Release | sfx/arrow_release |
| FX018 | Rivet Shot | sfx/rivet_shot |
| FX019 | Fire Cast | sfx/fire_cast |
| FX020 | Ice Break | sfx/ice_break |
| FX021 | Storm Crack | sfx/storm_crack |
| FX022 | Heal Bloom | sfx/heal_bloom |
| FX023 | Status Afflicted | sfx/status_afflicted |
| FX024 | Status Cleansed | sfx/status_cleansed |
| FX025 | KO Fall | sfx/ko_fall |
| FX026 | Enemy Defeat | sfx/enemy_defeat |
| FX027 | Level Up | sfx/level_up |
| FX028 | New Ability | sfx/new_ability |
| FX029 | Concord Full | sfx/concord_full |
| FX030 | Summon Entry | sfx/summon_entry |
| FX031 | Ferry Bell | sfx/ferry_bell |
| FX032 | Airship Engine Start | sfx/airship_engine_start |

## Replacement workflow

Place a new original/licensed file in the project’s audio import directory; update only that cue’s resource mapping; record provenance; play its intro, loop, transition and stop behavior in the running game. Confirm loudness against adjacent cues. Optional stems may be supplied as synchronized equal-length files but are not required by v0.1. Do not change filenames throughout fifty scene scripts merely to replace one battle track.
