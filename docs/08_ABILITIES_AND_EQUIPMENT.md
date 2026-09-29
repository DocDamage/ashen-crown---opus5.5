# Player ability and equipment catalog

These are design seed values and effect contracts, not implemented or playtested game content. See the combat specification for shared arithmetic and transaction rules. JSON is authoritative for IDs; this document is the readable view.

## Abilities — 80 records

### Dain Ashward

| ID | Ability | Unlock | MP | Power / kind | Target | Effect |
| --- | --- | --- | --- | --- | --- | --- |
| S001 | Oath of Shelter | Level 1 | 3 | 0 / utility | self | Set exclusive oath Shelter: physical damage dealt x0.90; intercept the first single-target hit against an ally below 35% HP per enemy action, taking 50% of that hit. Cannot intercept area attacks or recurse. |
| S002 | Shieldbreak | Level 2 | 4 | 120 / physical | enemy_one | Deal damage, then apply Guardbreak for 3 target actions; no stacking beyond the common status definition. |
| S003 | Oath of Wrath | Level 6 | 4 | 0 / utility | self | Replace any oath. Physical damage dealt x1.20 and physical damage received x1.15; persists until changed or battle ends. |
| S004 | Cinderedge | Level 10 | 8 | 155 / physical | enemy_one | Fire-aspected weapon strike; can break flammable seals but cannot bypass plot gates. |
| S005 | Oath of Sacrifice | Level 15 | 5 | 0 / utility | self | Replace any oath. Once per enemy action, transfer 25% of another ally’s received direct damage to Dain. Transfer cannot reduce Dain below 1 HP and is capped at 10% of his max HP per action. |
| S006 | Rally | Level 21 | 12 | 0 / utility | ally_all | Remove Weaken and apply Barrier for 2 target actions. Does not revive fallen allies. |
| S007 | Oath of Witness | Level 28 | 6 | 0 / utility | self | Replace any oath. Immune to Silence and Blind; after an ally is hit, next direct attack gains +20% power, one charge only. |
| S008 | Open Hand | Q01 | 24 | 0 / utility | ally_all | Dispel removable hostile statuses from living allies and grant Barrier for 3 target actions. Once per battle, also prevent one lethal direct hit on each ally, leaving 1 HP. Does not bypass scripted losses or resurrect. |

### Tessa Vale

| ID | Ability | Unlock | MP | Power / kind | Target | Effect |
| --- | --- | --- | --- | --- | --- | --- |
| S009 | Ember Lance | Level 1 | 4 | 110 / magical | enemy_one | Single-target fire spell with 20% Burn chance after a hit. |
| S010 | Rime Needle | Level 2 | 5 | 110 / magical | enemy_one | Single-target ice spell; 25% Slow chance. |
| S011 | Storm Arc | Level 6 | 8 | 90 / magical | enemy_all | Hit each living enemy once; no additional chaining on a single target. |
| S012 | Stone Seal | Level 10 | 7 | 130 / magical | enemy_one | Damage plus 40% Guardbreak chance; flying foes resist earth unless grounded. |
| S013 | Overcast | Level 15 | 0 | 0 / utility | self | Arm one next elemental spell: MP cost x1.75 rounded up, power x1.40, and after resolution lose 8% max HP nonlethally. No random fizzle. Arm costs a turn; consumed only on successful spell commit. |
| S014 | Black Sun | Level 21 | 18 | 170 / magical | enemy_all | Area shadow spell. Undead affinity follows the target’s data, not appearance guessing. |
| S015 | Heat Exchange | Level 28 | 0 | 0 / utility | self | Convert 15% current HP, minimum 1 nonlethal HP, into 20 MP; usable once between Tessa’s damaging spells, maximum three times per battle. |
| S016 | Ash Without Fire | Q02 | 28 | 225 / magical | enemy_all | Light spell; remove one positive removable status from each hit enemy. Overcast is allowed with its full cost and self-damage. |

### Corren Hale

| ID | Ability | Unlock | MP | Power / kind | Target | Effect |
| --- | --- | --- | --- | --- | --- | --- |
| S017 | Updraft | Level 1 | 4 | 145 / physical | enemy_one | Leave targetable field for 1.2 simulation seconds, then land for damage. No ATB charging while airborne; encounter does not end while a living ally is airborne. |
| S018 | Harrow Dive | Level 2 | 7 | 160 / physical | enemy_one | Airborne strike with +30% damage against Marked targets, consumed without removing Mark. |
| S019 | Anchorfall | Level 6 | 8 | 130 / physical | enemy_one | Ground a flying target for 2 target actions if not immune; boss immunity still allows damage. |
| S020 | Skypiercer | Level 10 | 10 | 160 / physical | enemy_one | Ignore 35% of target DEF, not all defense. No critical multiplier beyond the standard cap. |
| S021 | Feather Guard | Level 15 | 6 | 0 / utility | self | Reduce the next direct damaging action by 60%, then expire; cannot stack with a second copy. |
| S022 | Storm Vault | Level 21 | 14 | 145 / physical | enemy_all | One leap followed by one damage instance per living enemy; no extra hits for sprite segments. |
| S023 | Wingbeat | Level 28 | 12 | 0 / utility | ally_all | Advance each living ally’s ATB by 120 of 1000, excluding Corren; once per Corren readiness cycle. Cannot queue duplicate turns. |
| S024 | Unbound Descent | Q03 | 26 | 240 / physical | enemy_one | Aerial strike; on landing grant Corren and the lowest-HP living ally Barrier for 2 actions. Landing is guaranteed unless battle already legitimately ended. |

### Ivo Quill

| ID | Ability | Unlock | MP | Power / kind | Target | Effect |
| --- | --- | --- | --- | --- | --- | --- |
| S025 | Rivet Shot | Level 1 | 3 | 110 / physical | enemy_one | Ranged physical hit; ignores back-row outgoing penalty. |
| S026 | Field Patch | Level 2 | 5 | 105 / heal | ally_one | Restore HP using the heal formula. Works in battle and exploration; not a revive. |
| S027 | Grounding Rod | Level 6 | 8 | 0 / utility | ally_all | Grant storm resistance x0.50 for 3 target actions; strongest resistance wins rather than multiplying copies. |
| S028 | Steam Screen | Level 10 | 8 | 0 / utility | ally_all | Apply Barrier for 2 actions and 20% physical evasion bonus for one incoming direct action. |
| S029 | Clock Mine | Level 15 | 10 | 170 / magical | enemy_one | Attach one mine; detonate immediately after that enemy’s next resolved action. Reapplication refreshes without duplicate mines. |
| S030 | Pressure Vent | Level 21 | 9 | 0 / utility | ally_all | Remove Burn and grant Regen for 3 target actions. |
| S031 | Decoy Frame | Level 28 | 12 | 0 / utility | self | Create one team decoy with HP equal to 25% Ivo max HP; draws the next two eligible single-target enemy attacks. Area damage affects it but still hits the party. |
| S032 | Unborrowed Engine | Q04 | 24 | 0 / utility | ally_all | Apply Haste for 3 actions and restore 15 MP per living ally. Once per battle. Net MP creation cannot be repeated via revive. |

### Nera Fen

| ID | Ability | Unlock | MP | Power / kind | Target | Effect |
| --- | --- | --- | --- | --- | --- | --- |
| S033 | Hunter’s Mark | Level 1 | 3 | 0 / utility | enemy_one | Apply Mark for 4 target actions and reveal exact elemental affinities in the bestiary. |
| S034 | Split Arrow | Level 2 | 6 | 80 / physical | enemy_all | One arrow per living enemy; ranged; applies no additional hits when only one enemy remains. |
| S035 | Snare | Level 6 | 5 | 0 / utility | enemy_one | Apply Slow with 90% base chance; on normal enemies also delay ATB by 150. Bosses take the bounded Slow effect only. |
| S036 | Bramble Ward | Level 10 | 6 | 0 / utility | ally_one | Apply Barrier for 3 target actions; reflect 15% of absorbed direct physical damage once per source action, with reflection recursion disabled. |
| S037 | Scent Trail | Level 15 | 3 | 0 / utility | enemy_one | Reveal drops, steal eligibility and next committed enemy move; same information remains after the battle. |
| S038 | Exposed Thread | Level 21 | 11 | 175 / physical | enemy_one | Ranged strike; +25% damage against Guardbreak or Mark, not +25% for each. |
| S039 | True North | Level 28 | 12 | 0 / utility | ally_all | Remove Blind and apply Focus for 3 actions; no effect on story directions or hidden map gates. |
| S040 | Many Paths | Q05 | 24 | 180 / physical | enemy_all | Ranged volley; apply Mark to survivors. Grant one charge of 50% flee-meter progress in flee-eligible battles only. |

### Sister Oriel

| ID | Ability | Unlock | MP | Power / kind | Target | Effect |
| --- | --- | --- | --- | --- | --- | --- |
| S041 | Mend | Level 1 | 4 | 125 / heal | ally_one | Single-target healing, usable in battle or exploration. Against an undead enemy requires an explicit hostile target selection and deals equivalent light damage. |
| S042 | Cleanse | Level 2 | 4 | 0 / utility | ally_one | Remove Poison, Burn, Bleed, Blind, Silence and Sleep. Not Doom, stun or boss-specific narrative seals. |
| S043 | Sunthread | Level 6 | 10 | 95 / heal | ally_all | Heal each living ally. Does not damage enemies by changing target mode. |
| S044 | Last Light | Level 10 | 14 | 25 / revive | ally_one | Revive one fallen ally at 25% maximum HP; target must still be fallen at resolution. |
| S045 | Omen | Level 15 | 5 | 0 / utility | enemy_one | Reveal next scheduled move and its target; delay that enemy’s ATB by 100, maximum once per enemy action cycle. Does not read future random decisions. |
| S046 | Intercede | Level 21 | 8 | 0 / utility | ally_one | Grant one protection charge: the next direct hit cannot reduce this ally below 1 HP. Expires after 3 target actions; does not stop poison at 1 HP. |
| S047 | Stillwater | Level 28 | 14 | 0 / utility | ally_all | Remove Slow and Doom; grant Regen for 3 actions. No automatic resurrection. |
| S048 | Borrowed Dawn | Q06 | 30 | 180 / heal | ally_all | Revive fallen allies at 20% HP, then heal the whole party. Once per battle, committed with a valid resolution and not reset by Oriel’s death. |

### Sable Renn

| ID | Ability | Unlock | MP | Power / kind | Target | Effect |
| --- | --- | --- | --- | --- | --- | --- |
| S049 | Infuse Ember | Level 1 | 4 | 0 / utility | self | Set one weapon infusion to fire for 4 Sable actions; her next normal Attack applies 25% Burn chance. Infusions do not stack. |
| S050 | Infuse Rime | Level 2 | 4 | 0 / utility | self | Replace infusion with ice for 4 Sable actions; next normal Attack applies 25% Slow chance. |
| S051 | Infuse Storm | Level 6 | 4 | 0 / utility | self | Replace infusion with storm for 4 Sable actions; next normal Attack ignores 15% DEF. |
| S052 | Unseal | Level 10 | 6 | 0 / utility | enemy_one | Remove one removable positive status, selecting the oldest; if none exists, deal a 60-power magic strike of the current infusion or light. |
| S053 | Mirror Cut | Level 15 | 9 | 140 / physical | enemy_one | Damage using current infusion; then gain one 30% magic-reduction charge. This is not recursive spell reflection. |
| S054 | Sever Rune | Level 21 | 12 | 165 / physical | enemy_one | Deal light-aspected physical damage and apply Silence with 50% base chance; boss immunity does not cancel damage. |
| S055 | Runic Shelter | Level 28 | 14 | 0 / utility | ally_all | Apply Barrier for 3 actions and light/shadow resistance x0.75 for 3 actions; strongest affinity modifier wins. |
| S056 | Unwritten Law | Q07 | 26 | 230 / physical | enemy_one | Remove all removable positive statuses before damage; party gains one immunity charge against the next removable hostile status. Cannot delete boss phase scripts. |

### Pip Marr

| ID | Ability | Unlock | MP | Power / kind | Target | Effect |
| --- | --- | --- | --- | --- | --- | --- |
| S057 | Pilfer | Level 1 | 0 | 0 / utility | enemy_one | Attempt a common steal at 70%, rare at 10% if common already taken. After three common failures, common succeeds. One common and one rare per enemy instance; no mandatory progression items. |
| S058 | Feint | Level 2 | 3 | 95 / physical | enemy_one | Damage plus 50% Blind chance. Ranged immunity does not apply; this is a melee move. |
| S059 | Smoke | Level 6 | 5 | 0 / utility | ally_all | Advance flee meter by 500 of 1000 in flee-eligible battles; otherwise grant 15% physical evasion for one incoming action. |
| S060 | Quick Hands | Level 10 | 4 | 0 / utility | self | Arm one Item action with 50% ATB refund after valid resolution. Consume exactly one item; effects cannot recursively arm Quick Hands. |
| S061 | Tripwire | Level 15 | 6 | 100 / physical | enemy_one | Damage and delay target ATB by 150; bosses cap combined delays at 200 between their actions. |
| S062 | Disarm | Level 21 | 8 | 130 / physical | enemy_one | Damage and apply Weaken for 3 target actions; no actual removal of boss loot or equipped player items. |
| S063 | Rescue Line | Level 28 | 9 | 0 / utility | ally_one | Remove one removable hard-control status, move the ally to back row and apply Barrier for 2 actions. Does not reposition exploration characters. |
| S064 | False Crown | Q08 | 22 | 0 / utility | enemy_all | Apply Weaken and Guardbreak to living enemies with 100% base chance subject to immunity. Cancel one pending normal-enemy charge, never a boss phase transition. |

### Accessory spells and Vestiges

| ID | Name | Access | MP / Concord | Effect |
| --- | --- | --- | --- | --- |
| S065 | Kindle | A001 | 6 MP | Use the standard damage or healing formula; this accessory grants access only while equipped. |
| S066 | Rime Dust | A002 | 6 MP | Use the standard damage or healing formula; this accessory grants access only while equipped. |
| S067 | Static Thread | A003 | 6 MP | Use the standard damage or healing formula; this accessory grants access only while equipped. |
| S068 | Salt Wash | A004 | 6 MP | Use the standard damage or healing formula; this accessory grants access only while equipped. |
| S069 | Small Renewal | A005 | 6 MP | Use the standard damage or healing formula; this accessory grants access only while equipped. |
| S070 | Clock Nudge | A006 | 6 MP | Apply Slow for 2 target actions at 75% base chance. |
| S071 | Night Veil | A007 | 6 MP | Use the standard damage or healing formula; this accessory grants access only while equipped. |
| S072 | Day Seal | A008 | 6 MP | Use the standard damage or healing formula; this accessory grants access only while equipped. |
| S073 | Ember Moth | V01 | 100 Concord | Fire damage to all enemies at 180 power; allies gain Burn immunity for 2 actions. |
| S074 | Rootstag | V02 | 100 Concord | Earth damage to all enemies at 170 power; heal allies for 8% max HP. |
| S075 | Bell Whale | V03 | 100 Concord | Water damage at 170 power to all enemies; cleanse Silence and Sleep from allies. |
| S076 | Sky Manta | V04 | 100 Concord | Storm damage to all enemies at 180 power; advance living allies’ ATB by 100, no duplicate turns. |
| S077 | Lumen Fox | V05 | 100 Concord | Heal all living allies at 140 power and reveal enemies’ current scheduled intents. |
| S078 | Iron Tortoise | V06 | 100 Concord | Grant Barrier and Regen for 3 actions to all living allies; no damage. |
| S079 | Winter Hind | V07 | 100 Concord | Ice damage to all enemies at 210 power; remove Doom from living allies. |
| S080 | Night Leviathan | V08 | 100 Concord | Shadow damage to all enemies at 220 power; remove one positive removable enemy status. |

## Weapons — 48 records

| ID | Name | Owner | Tier | ATK | MAG | Price | Acquisition / effect |
| --- | --- | --- | --- | --- | --- | --- | --- |
| W001 | Service Sword | C01 | 1 | 8 | 1 | 100 | Guaranteed starter/join kit or any open town’s basic stock; No hidden passive; stat progression only. |
| W002 | River Iron | C01 | 2 | 17 | 2 | 420 | Shared tier stock unlocked at CH04; No hidden passive; stat progression only. |
| W003 | Cinderbrand | C01 | 3 | 29 | 3 | 1100 | Shared tier stock unlocked at CH08; No hidden passive; stat progression only. |
| W004 | Witness Edge | C01 | 4 | 44 | 5 | 2600 | Shared tier stock unlocked at CH16; No hidden passive; stat progression only. |
| W005 | Accord Steel | C01 | 5 | 62 | 7 | 5800 | Shared tier stock unlocked at CH20; No hidden passive; stat progression only. |
| W006 | Open Hand | C01 | 6 | 82 | 10 | 0 | Quest Q01; While an oath is active, first protected hit per enemy action gains an additional 10% damage reduction, within the global 80% cap. |
| W007 | Apprentice Rod | C02 | 1 | 4 | 8 | 100 | Guaranteed starter/join kit or any open town’s basic stock; No hidden passive; stat progression only. |
| W008 | Copper Wand | C02 | 2 | 8 | 17 | 420 | Shared tier stock unlocked at CH04; No hidden passive; stat progression only. |
| W009 | Tideglass Rod | C02 | 3 | 13 | 29 | 1100 | Shared tier stock unlocked at CH08; No hidden passive; stat progression only. |
| W010 | Prism Branch | C02 | 4 | 20 | 44 | 2600 | Shared tier stock unlocked at CH16; No hidden passive; stat progression only. |
| W011 | Dawn Conductor | C02 | 5 | 28 | 62 | 5800 | Shared tier stock unlocked at CH20; No hidden passive; stat progression only. |
| W012 | Lantern Unbound | C02 | 6 | 37 | 82 | 0 | Quest Q02; Overcast self-damage becomes 5% max HP; other costs remain. |
| W013 | Anchor Spear | C03 | 1 | 8 | 1 | 100 | Guaranteed starter/join kit or any open town’s basic stock; No hidden passive; stat progression only. |
| W014 | Gust Lance | C03 | 2 | 17 | 2 | 420 | Shared tier stock unlocked at CH04; No hidden passive; stat progression only. |
| W015 | Chainbreaker | C03 | 3 | 29 | 3 | 1100 | Shared tier stock unlocked at CH08; No hidden passive; stat progression only. |
| W016 | Cloud Needle | C03 | 4 | 44 | 5 | 2600 | Shared tier stock unlocked at CH16; No hidden passive; stat progression only. |
| W017 | Returner’s Pike | C03 | 5 | 62 | 7 | 5800 | Shared tier stock unlocked at CH20; No hidden passive; stat progression only. |
| W018 | Homeward Sky | C03 | 6 | 82 | 10 | 0 | Quest Q03; After landing from a leap, heal 5% max HP once per landing action. |
| W019 | Rivet Driver | C04 | 1 | 8 | 4 | 100 | Guaranteed starter/join kit or any open town’s basic stock; No hidden passive; stat progression only. |
| W020 | Pressure Wrench | C04 | 2 | 17 | 9 | 420 | Shared tier stock unlocked at CH04; No hidden passive; stat progression only. |
| W021 | Arc Welder | C04 | 3 | 29 | 16 | 1100 | Shared tier stock unlocked at CH08; No hidden passive; stat progression only. |
| W022 | Clock Hammer | C04 | 4 | 44 | 24 | 2600 | Shared tier stock unlocked at CH16; No hidden passive; stat progression only. |
| W023 | Common Engine | C04 | 5 | 62 | 34 | 5800 | Shared tier stock unlocked at CH20; No hidden passive; stat progression only. |
| W024 | Hands of Many | C04 | 6 | 82 | 45 | 0 | Quest Q04; Field Patch also removes Burn. |
| W025 | Ashwood Bow | C05 | 1 | 8 | 1 | 100 | Guaranteed starter/join kit or any open town’s basic stock; No hidden passive; stat progression only. |
| W026 | Riverbend | C05 | 2 | 17 | 2 | 420 | Shared tier stock unlocked at CH04; No hidden passive; stat progression only. |
| W027 | Bramble String | C05 | 3 | 29 | 3 | 1100 | Shared tier stock unlocked at CH08; No hidden passive; stat progression only. |
| W028 | Farwatch | C05 | 4 | 44 | 5 | 2600 | Shared tier stock unlocked at CH16; No hidden passive; stat progression only. |
| W029 | Crossing Song | C05 | 5 | 62 | 7 | 5800 | Shared tier stock unlocked at CH20; No hidden passive; stat progression only. |
| W030 | Every Road | C05 | 6 | 82 | 10 | 0 | Quest Q05; Hunter’s Mark lasts one additional target action. |
| W031 | Travel Staff | C06 | 1 | 4 | 8 | 100 | Guaranteed starter/join kit or any open town’s basic stock; No hidden passive; stat progression only. |
| W032 | Quiet Bell | C06 | 2 | 8 | 17 | 420 | Shared tier stock unlocked at CH04; No hidden passive; stat progression only. |
| W033 | Saltwood Crook | C06 | 3 | 13 | 29 | 1100 | Shared tier stock unlocked at CH08; No hidden passive; stat progression only. |
| W034 | Listening Branch | C06 | 4 | 20 | 44 | 2600 | Shared tier stock unlocked at CH16; No hidden passive; stat progression only. |
| W035 | Mercy Without Law | C06 | 5 | 28 | 62 | 5800 | Shared tier stock unlocked at CH20; No hidden passive; stat progression only. |
| W036 | Right to Refuse | C06 | 6 | 37 | 82 | 0 | Quest Q06; Cleanse also removes Doom. |
| W037 | Binding Blade | C07 | 1 | 8 | 4 | 100 | Guaranteed starter/join kit or any open town’s basic stock; No hidden passive; stat progression only. |
| W038 | Split Rune | C07 | 2 | 17 | 9 | 420 | Shared tier stock unlocked at CH04; No hidden passive; stat progression only. |
| W039 | Unsealed Edge | C07 | 3 | 29 | 16 | 1100 | Shared tier stock unlocked at CH08; No hidden passive; stat progression only. |
| W040 | Mirrorbrand | C07 | 4 | 44 | 24 | 2600 | Shared tier stock unlocked at CH16; No hidden passive; stat progression only. |
| W041 | Witness Blade | C07 | 5 | 62 | 34 | 5800 | Shared tier stock unlocked at CH20; No hidden passive; stat progression only. |
| W042 | Unwritten | C07 | 6 | 82 | 45 | 0 | Quest Q07; An infusion lasts two additional Sable actions. |
| W043 | Dock Knife | C08 | 1 | 8 | 1 | 100 | Guaranteed starter/join kit or any open town’s basic stock; No hidden passive; stat progression only. |
| W044 | Ledger Fang | C08 | 2 | 17 | 2 | 420 | Shared tier stock unlocked at CH04; No hidden passive; stat progression only. |
| W045 | Rope Cutter | C08 | 3 | 29 | 3 | 1100 | Shared tier stock unlocked at CH08; No hidden passive; stat progression only. |
| W046 | Quick Answer | C08 | 4 | 44 | 5 | 2600 | Shared tier stock unlocked at CH16; No hidden passive; stat progression only. |
| W047 | True Name | C08 | 5 | 62 | 7 | 5800 | Shared tier stock unlocked at CH20; No hidden passive; stat progression only. |
| W048 | No Crown | C08 | 6 | 82 | 10 | 0 | Quest Q08; Successful common Pilfer refunds 150 ATB, once per readiness cycle. |

## Armor, head and offhand — 32 records

| ID | Name | Slot | Allowed | DEF | RES | Price | Effect |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G001 | Traveler’s Coat | body | C02, C06 | 3.25 | 6.75 | 120 | No hidden passive. |
| G002 | Tidewoven Robe | body | C02, C06 | 7.800000000000001 | 16.200000000000003 | 650 | No hidden passive. |
| G003 | Listening Mantle | body | C02, C06 | 15.600000000000001 | 32.400000000000006 | 1900 | No hidden passive. |
| G004 | Dawnweave | body | C02, C06 | 26.0 | 54.0 | 4600 | No hidden passive. |
| G005 | Route Leather | body | C05, C08 | 5.0 | 3.75 | 120 | No hidden passive. |
| G006 | Bramble Jacket | body | C05, C08 | 12.0 | 9.0 | 650 | No hidden passive. |
| G007 | Crosswind Hide | body | C05, C08 | 24.0 | 18.0 | 1900 | No hidden passive. |
| G008 | Common Road | body | C05, C08 | 40.0 | 30.0 | 4600 | No hidden passive. |
| G009 | Working Mail | body | C03, C04, C07 | 5.0 | 3.75 | 120 | No hidden passive. |
| G010 | Regulator Mesh | body | C03, C04, C07 | 12.0 | 9.0 | 650 | No hidden passive. |
| G011 | Mirror Links | body | C03, C04, C07 | 24.0 | 18.0 | 1900 | No hidden passive. |
| G012 | Accord Mail | body | C03, C04, C07 | 40.0 | 30.0 | 4600 | No hidden passive. |
| G013 | Service Plate | body | C01 | 6.75 | 3.75 | 120 | No hidden passive. |
| G014 | Cinder Plate | body | C01 | 16.200000000000003 | 9.0 | 650 | No hidden passive. |
| G015 | Broken Seal | body | C01 | 32.400000000000006 | 18.0 | 1900 | No hidden passive. |
| G016 | Unbound Plate | body | C01 | 54.0 | 30.0 | 4600 | No hidden passive. |
| G017 | Wool Cap | head | C01, C02, C03, C04, C05, C06, C07, C08 | 4 | 4 | 120 | Even-index styles favor DEF by +2; odd-index styles favor RES by +2. Apply once in the content compiler. |
| G018 | Route Band | head | C01, C02, C03, C04, C05, C06, C07, C08 | 4 | 4 | 370 | Even-index styles favor DEF by +2; odd-index styles favor RES by +2. Apply once in the content compiler. |
| G019 | Copper Goggles | head | C01, C02, C03, C04, C05, C06, C07, C08 | 10 | 10 | 620 | Even-index styles favor DEF by +2; odd-index styles favor RES by +2. Apply once in the content compiler. |
| G020 | Quiet Hood | head | C01, C02, C03, C04, C05, C06, C07, C08 | 10 | 10 | 870 | Even-index styles favor DEF by +2; odd-index styles favor RES by +2. Apply once in the content compiler. |
| G021 | Cloud Helm | head | C01, C02, C03, C04, C05, C06, C07, C08 | 16 | 16 | 1120 | Even-index styles favor DEF by +2; odd-index styles favor RES by +2. Apply once in the content compiler. |
| G022 | Witness Circlet | head | C01, C02, C03, C04, C05, C06, C07, C08 | 16 | 16 | 1370 | Even-index styles favor DEF by +2; odd-index styles favor RES by +2. Apply once in the content compiler. |
| G023 | Accord Crownlet | head | C01, C02, C03, C04, C05, C06, C07, C08 | 22 | 22 | 1620 | Even-index styles favor DEF by +2; odd-index styles favor RES by +2. Apply once in the content compiler. |
| G024 | Dawn Hood | head | C01, C02, C03, C04, C05, C06, C07, C08 | 22 | 22 | 1870 | Even-index styles favor DEF by +2; odd-index styles favor RES by +2. Apply once in the content compiler. |
| G025 | Service Buckler | offhand | C01, C07, C08 | 5 | 3 | 180 | Cannot be equipped while a two-handed weapon is equipped. |
| G026 | Cinder Shield | offhand | C01, C07 | 14 | 5 | 540 | Cannot be equipped while a two-handed weapon is equipped. |
| G027 | Mirror Shield | offhand | C01, C07 | 22 | 14 | 900 | Cannot be equipped while a two-handed weapon is equipped. |
| G028 | Witness Shield | offhand | C01, C07 | 32 | 24 | 1260 | Cannot be equipped while a two-handed weapon is equipped. |
| G029 | Copper Focus | offhand | C02 | 2 | 12 | 1620 | Cannot be equipped while a two-handed weapon is equipped. |
| G030 | Prism Focus | offhand | C02 | 5 | 26 | 1980 | Cannot be equipped while a two-handed weapon is equipped. |
| G031 | Route Charm | offhand | C08 | 8 | 12 | 2340 | Cannot be equipped while a two-handed weapon is equipped. |
| G032 | True-Name Charm | offhand | C08 | 12 | 22 | 2700 | Cannot be equipped while a two-handed weapon is equipped. |

## Accessories — 24 records

| ID | Name | Price | Effect |
| --- | --- | --- | --- |
| A001 | Ember Token | 800 | Grant S065 while equipped. |
| A002 | Rime Token | 980 | Grant S066 while equipped. |
| A003 | Storm Token | 1160 | Grant S067 while equipped. |
| A004 | Tide Token | 1340 | Grant S068 while equipped. |
| A005 | Hearth Token | 1520 | Grant S069 while equipped. |
| A006 | Clock Token | 1700 | Grant S070 while equipped. |
| A007 | Night Token | 1880 | Grant S071 while equipped. |
| A008 | Day Token | 2060 | Grant S072 while equipped. |
| A009 | Returner’s Cord | 2240 | Reduce physical damage received by 10%; does not stack with another copy. |
| A010 | Witness Glass | 2420 | Reveal enemy elemental affinities at battle start; no stat effect. |
| A011 | Clear Bell | 2600 | Immunity to Silence. |
| A012 | Open-Eye Thread | 2780 | Immunity to Blind and Sleep. |
| A013 | Salt Locket | 2960 | Immunity to Poison and Burn. |
| A014 | Steady Hand | 3140 | Physical accuracy +10 percentage points, capped at 100%. |
| A015 | Warm Lantern | 3320 | Healing done x1.15; strongest duplicate only. |
| A016 | Reserve Cell | 3500 | Maximum MP +15%; current MP does not increase when equipped. |
| A017 | Long Breath | 3680 | Maximum HP +15%; current HP preserves percentage when changing equipment outside battle. |
| A018 | Twin Oath Ring | 3860 | Counter one direct physical attack at 50% normal Attack power per enemy action; no recursion or counter-counter chains. |
| A019 | Empty Scabbard | 4040 | Two-handed physical damage x1.15; no effect on magical damage or one-handed weapons. |
| A020 | Mercy Thread | 4220 | One automatic Barrier charge when crossing below 30% HP; once per battle. |
| A021 | Hasty Ledger | 4400 | Start normal battles with +100 ATB; no effect on script-fixed tutorial starts. |
| A022 | Pilgrim’s Map | 4580 | Reduce field encounter-meter accumulation by 25%; does not affect scripted bosses or eliminate encounters. |
| A023 | Broken Diadem | 0 | First hostile dispel against the wearer fails each battle; no immunity to damage or narrative scenes. |
| A024 | Unowned Song | 0 | Concord gain from the wearer’s successful actions +2, respecting the shared cap; summon animation may be shortened without reducing effects. |

## Consumables — 24 records

| ID | Name | Price | Effect |
| --- | --- | --- | --- |
| I001 | Tonic | 45 | Restore 250 HP to one living ally. |
| I002 | High Tonic | 150 | Restore 900 HP to one living ally. |
| I003 | Grand Tonic | 400 | Restore 1800 HP to one living ally. |
| I004 | Ether | 100 | Restore 40 MP to one living ally. |
| I005 | High Ether | 320 | Restore 100 MP to one living ally. |
| I006 | Phoenix Leaf | 120 | Revive one fallen ally at 25% max HP. |
| I007 | Purifying Salt | 80 | Remove Poison, Burn, Bleed, Blind, Sleep and Silence. |
| I008 | Eyesalve | 25 | Remove Blind. |
| I009 | Antidote | 25 | Remove Poison. |
| I010 | Wake Bell | 25 | Remove Sleep. |
| I011 | Cool Cloth | 25 | Remove Burn. |
| I012 | Stilling Root | 25 | Remove Silence. |
| I013 | Travel Tent | 160 | At a save point or overworld safe location, restore party HP and MP; not usable in a battle. |
| I014 | Smoke Pellet | 50 | Add 600 flee meter in eligible battles; consumes nothing when fleeing is forbidden. |
| I015 | Ember Flask | 65 | 120-power fire magic attack with fixed item MAG 30. |
| I016 | Rime Flask | 65 | 120-power ice magic attack with fixed item MAG 30. |
| I017 | Storm Flask | 65 | 120-power storm magic attack with fixed item MAG 30. |
| I018 | Guard Powder | 75 | Apply Barrier to one ally for 3 actions. |
| I019 | Clock Dust | 75 | Apply Slow to one enemy at 85% base chance; boss resistance applies. |
| I020 | Concord Seed | 220 | Restore 30 Concord; one consumed seed per battle; disabled outside battle. |
| I021 | Emergency Ration | 120 | Heal all living allies for 200 HP each. |
| I022 | Waystone | 90 | Return to the current dungeon entrance outside battle; forbid during atomic story transitions without consuming it. |
| I023 | Restorative Vial | 180 | Remove Doom and Bleed from one ally. |
| I024 | Elixir | 0 | Restore one living ally to full HP and MP; rare guaranteed chest source, not required for the critical path. |

## Statuses — 16 records

| Status | Type | Duration | Effect |
| --- | --- | --- | --- |
| Poison | negative | 3 target actions | Lose 4% max HP after acting; can KO; ends after battle. |
| Burn | negative | 3 target actions | Lose 3% max HP after acting and physical damage dealt x0.90. |
| Bleed | negative | 3 target actions | Lose 5% max HP after a physical action; nonphysical action still consumes one duration. |
| Silence | negative | 2 target actions | Blocks spells and summons, not Item, Attack, Defend or physical skills. |
| Sleep | negative | 1 target action opportunity | Skip one readiness opportunity; direct damage wakes immediately. |
| Stun | negative | 1 target action opportunity | Skip one readiness opportunity; reapplication cannot extend until target has acted. |
| Slow | negative | 3 target actions | ATB fill x0.75; bosses x0.90; mutually exclusive with Haste. |
| Haste | positive | 3 target actions | ATB fill x1.25; mutually exclusive with Slow. |
| Barrier | positive | 3 target actions | Direct damage received x0.75; not poison or HP transfers. |
| Regen | positive | 3 target actions | Restore 5% max HP after acting; cannot revive. |
| Mark | negative | 4 target actions | Direct physical damage received x1.10 and eligible skill synergies. |
| Guardbreak | negative | 3 target actions | DEF x0.80; no stacking. |
| Blind | negative | 2 target actions | Physical hit chance reduced by 25 percentage points, minimum 50%. |
| Doom | negative | 3 target action opportunities | Visible countdown; KO on expiry; boss immunity; cleansable and never random on the first tutorial boss. |
| Weaken | negative | 3 target actions | ATK and MAG x0.85; temporary derived stats only. |
| Focus | positive | 3 target actions | Accuracy +10 percentage points and critical chance +5 points, within caps. |

## Guaranteed rare restorative placement

Elixirs are not sold. Place one guaranteed Elixir chest at each of D08_R04, D10_R04, D11_R04 and D12_R04, with the stable chest IDs in `data/items.json`. These are optional supplies, never mandatory progression keys. Shared chest/reward persistence rules apply.
