# Progression, economy, menus and accessibility

## Level growth

Level cap is 50. The critical path is initially aimed at the mid-30s through low-40s for the finale, not mandatory level 50. XP needed to move from level L to L+1 is `30 + 12L + 3L²`; these seed values require a full-campaign economy pass. Ordinary enemy XP is in the catalog. Boss XP should initially equal six ordinary encounters at its intended level, then be adjusted with measured pacing.

Each recruited character receives 100% battle XP whether active, in reserve or temporarily unavailable after the catastrophe. Do not divide XP by the number of members. An initial recruit or returning character uses the greater of their stored level and the median level of the currently available party minus one. Apply only missing earned level growth, never repeated growth each time a scene loads. A first recruit has their guaranteed starter weapon and ordinary initial equipment; a reunion retains existing inventory and does not grant those items a second time.

For initial growth, let `n = level − 1`. HP is `hp1 + hp_growth × n + floor(0.65 × n²)` where hp_growth by C01–C08 is 54, 40, 49, 51, 45, 42, 48, 43. MP is `mp1 + mp_growth × n` with growth 3, 6, 3, 4, 3, 6, 4, 3. STR/MAG growth by character is C01 2/1, C02 1/2, C03 2/1, C04 1/2, C05 2/1, C06 1/2, C07 2/2, C08 2/1. DEF and RES gain 1 per level; SPD gains 1 each four levels. Use fixed rounding and equipment modifiers after base growth. Changing equipment must not trigger level growth again.

Each character has seven level-granted signature techniques plus one personal-quest technique. The JSON lists unlock levels. Characters keep their roles: there is no universal spell-learning tree that makes every party member interchangeable. Eight accessory spells offer limited cross-role support while equipped. Do not let removing and re-equipping an accessory permanently teach its spell.

## Equipment

Slots: weapon, offhand, head, body, accessory 1 and accessory 2. A two-handed weapon empties/disables offhand, returning the item to inventory if necessary. Inspect allowed-character IDs, not only a generic role label. Equipment changes are available outside battle or in designated preparation screens. Preview all derived stats and newly granted commands before confirmation.

Each character has six named weapons. Tier 1 is guaranteed at first recruitment and remains purchasable. Tiers 2–5 unlock at CH04, CH08, CH16 and CH20; all open town weapon vendors expose the unlocked shared tier stock. Town presentation and flavor differ, but a lost town cannot block the only useful spear. Tier 6 comes from the corresponding personal quest and is not sellable.

Armor/head/offhand catalog tiers 1–4 unlock at CH01, CH06, CH16 and CH20. Any open general-equipment shop can supply the unlocked tier. First/reunion loadout rules prevent an absent ally from being naked when called into the two-party finale. Post-catastrophe salvage forwards unique rewards from inaccessible maps based on acquisition IDs. Common consumables are not forwarded repeatedly.

## Economy

Use one currency, crowns, with an integer balance and a high safe cap. The name is setting vocabulary, not a second progression resource. All basic shops sell Tonic, Ether, Phoenix Leaf and status remedies from the beginning; the expanded stock opens at CH08. Start with 300 crowns, six Tonics, two Ethers, two Phoenix Leaves and one of each elemental flask needed for the first boss tutorial. Place a free full-recovery point before each mandatory boss.

Inns cost 25 crowns per recruited character, capped at 150. Hearthward’s communal recovery is always free. On the overworld, a Travel Tent restores the available party at a safe location. There is no hard requirement to buy a premium item before progressing. Gold rewards, prices, MP use and chest supply must be playtested together, not balanced in isolation.

Inventory stacks cap at 99. Purchases check total price and remaining capacity before spending. A unique quest reward that would overflow inventory enters a stable delivery chest and appears in the journal; it is never discarded. Consumable overflow converts to a visible bounded gold amount only after notifying the player. Never convert unique equipment or key items automatically. Selling equipment checks that it is not equipped, quest-protected or required by an active transaction.

## Encounter pacing

Use an exploration encounter meter on eligible terrain, with a minimum safe travel period after entering a map or finishing a battle. Default initial target is one encounter per 18–30 seconds of actual eligible walking, tuned by room size and progress. Menus, dialogue, blocked movement, room loading and cutscenes do not advance it. Running may increase distance but should not double annoyance by adding a second timer. Suppress normal encounters near save points, puzzles being operated and story conversations.

Provide an encounter-frequency accessibility option of Normal, Reduced and Off for ordinary random encounters. Scripted story encounters and bosses remain. Off must not strand the player below required levels: use transparent story-milestone XP grants or a clearly offered training service when enabled, and record this setting in the save. Do not secretly scale every enemy to the player and erase progression.

## Menus

Title: New Game, Continue, Load, Settings, Credits, Quit. Continue identifies slot, chapter, location, playtime and save date, not an ambiguous “latest” thumbnail. In-game: Items, Equipment, Abilities, Formation, Vestiges, Journal, World Map, Bestiary, Settings, Save when allowed. Show active and reserve party members, KO state, unavailable-story state and the reason equipment cannot be changed.

The journal records current objective, last clue, known destination and who supplied it. Completed quests keep their story summary. Optional rumors remain distinct from mandatory objectives. The world map supports named discovered locations, landing markers and optional guidance; it does not reveal every secret from the start.

Use persistent keyboard/gamepad navigation, remapping, focus highlight, confirm/cancel consistency, and a confirmation for destructive save overwrite. Mouse is optional, not required. No pixel hunting for a one-pixel menu button. Show elemental affinities with symbols and labels, not color alone.

## Accessibility

Wait mode defaults on. Offer text speed, instant text, hold/toggle run, reduced flashes, zero screen shake, shortened summons, volume buses and encounter frequency. Keep a readable high-contrast font; use an original or appropriately licensed font but do not bundle a font without documented permission. Larger UI uses alternative panel layouts and reflow, not merely cropping a scaled menu. At 320×240, text should generally use an 8–10 pixel readable bitmap body with tested line length; use a higher-resolution UI layer only as an explicit alternative style with visual review, not a silent pixel-density mismatch.

Important choices and cutscenes pause until confirmed. No audio-only puzzle, mandatory rapid tapping, or time-limited text selection. Losing focus pauses by default. Settings changes persist independently of a save slot, while play-affecting options are also recorded in the save for reproduction.
