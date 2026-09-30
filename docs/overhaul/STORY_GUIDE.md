# Story rewrite guide (overhaul cast)

The eight original party members keep their ids, story functions, scenes, flags and personal quests.
Only their names, identities and pronouns change. Edit dialogue/narration TEXT only.

## Name map (old -> new)

| id | old | new (full) | new short | pronouns | identity notes |
|---|---|---|---|---|---|
| C01 | Dain Ashward / Dain | Raven, the Executioner | Raven | he | dragonborn man, 34. Was a crown oath knight; now framed as the Crown's executioner (escorted labor convoys, carried out sentences). Still shares his body with Ilyr (the dragon fragment) - keep all Ilyr material. |
| C02 | Tessa Vale / Tessa | Morwen, Witch of the Eclipse | Morwen | she | human woman, 22. "Overcast mage" -> "eclipse witch"; her magic is witchcraft of the eclipse (Overcast/Black Sun fit). |
| C03 | Corren Hale / Corren | Vespera, Moonhare Warrior | Vespera | he -> SHE | moonhare woman (rabbit-eared folk), 31, dragoon of the aerial guard. Sister: Captain Edda Hale (keep; Vespera is "Vespera Hale" if a surname is ever needed). |
| C04 | Ivo Quill / Ivo | Rune Golem | the Golem / Golem | he (unchanged) | a rune-driven construct, built 49 years ago as a relay engineer. Designed the pressure regulator. Pell Quill is no longer his husband: Pell is the workshop organizer who has maintained him for decades and is his closest friend/family. Replace human body details (curls, hands aching, etc.) with construct ones (runes, plates, joints, oil). "Ivo" as a speaker name -> "Golem"; in narration use "the Golem". |
| C05 | Nera Fen / Nera | Elowen, Guardian of the Moonlit Grove | Elowen | she | woman, 29, displaced guardian of the Moonlit Grove, a ranger/guide. |
| C06 | Sister Oriel / Oriel | Aurex, Dragonblood Champion | Aurex | she -> HE | man, 42, oracle-champion whose dragon blood carries memory/visions his order mistook for divine law. Drop "Sister"; if a title is needed use "Champion Aurex". Brass bell etc. can stay. |
| C07 | Sable Renn / Sable | Crimson Oni | Oni | she -> HE | oni man, 36, former binding officer, spellblade. "Renn" dropped. NEVER change the dungeon name "Sable Conduit" (and similar place names containing Sable). |
| C08 | Pip Marr / Pip | Sak, Guardian of the Cat Kingdom | Sak | he | cat-folk man, 27, forger who fakes deaths. Brother Jori Marr -> "Jori" (Sak's brother; drop "Marr"). |

Other recurring characters are unchanged (Ilyr, Mara Pell, Voss, Rook, Edda, Sen, Ansel, Pell Quill, Jori).
Vestige renames: "whale" = Tide Serpent, "manta" = Sky Griffon (already done in ch06/ch07).

## Rules
- Do NOT change: `@scene` ids, labels, speaker keys (`say dain | ...` stays `dain`), flags, commands, item/ability ids, map ids.
- Change the words after `|` and narration text, choice labels, and quoted names.
- Fix all pronouns/possessives for Vespera (she/her), Aurex (he/him/his), Oni (he/him/his) - also "sister"/"brother", "woman"/"man", "ma'am"/"sir", etc. that refer to them.
- Keep the tone and length of lines. Keep lines short (dialogue box ~40 chars x 3 lines; don't make lines much longer).
- Names are whole words; beware substrings (e.g. "Pip" in "pipe", "Ivo" in other words, "Nera" in "general"). Use word boundaries.
- "Sable Conduit" is a place - keep it.
- After editing, run `python3 tools/compile_content.py` from the Repo root; it must print no errors.
