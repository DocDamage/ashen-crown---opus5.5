# Economy (systems s2, 2026-09-30)

The 40-50 hour curve for crowns: what gear costs in each region, what fights pay, what inns charge. Source of truth:
`tools/content/gear2.py` (tiers, gold curve, inns) and `tools/content/crafting.py` (materials, recipes). Numbers below
are generated from the compiled content.

## Rules
- **Early game unchanged.** CH01-CH04 (enemies up to level 14, Crown March and Cinder Reach inns, canon shop stock and
  prices) keep their canon values. Every existing item keeps its id and price.
- **Tier gear price** follows the canon weapon/armour tier prices at the item's level (`weapon_x`, `armor_x` in gear2):
  canon T1-T5 weapon prices 100 / 420 / 1100 / 2600 / 5800, armour 120 / 650 / 1900 / 4600, lerped; beyond the
  last canon tier x1.9 per tier. A region's items sit 30% into its level band (an upgrade on arrival, not an end state).
- **Enemy gold** = canon `10 + 6 x level`, times `1 + 0.035 x (level - 14)` above level 14 (bosses: `60 x level`
  with the same multiplier). Level variants and post-fault re-levelled formations follow their own level.
- **Battles per kit** (weapon + best body armour + head for one hero at the tier's price, divided by the gold of a
  2.2-enemy battle at the band's midpoint) stays at about 8-10 in every region: new gear is always a short grind away,
  never free. For comparison the canon CH04 tier-2 kit costs about 10 battles.
- **Inns**: canon price (25 crowns per recruited hero, capped at 150) is raised to the region's rate (table); the World
  of Ruin surface (post-fault) charges at least 200. Inn scenes that pass an explicit price keep it.
- **Selling** stays at half price. Named items (WN/GN/AN) cannot be sold.
- **Crafting** costs materials plus about 25% of the item's price in crowns (reforges 12%); crafted consumables cost
  materials only. Material sale prices (30-420; Wyrm Heart 2400) make gathering a small income, not a replacement
  for battles.
- **Drops**: new enemies (E041-E120) drop a family part (30%), an element part (15%) and their home's material (12%) on
  top of the canon potion drops; bosses drop their named piece (100%); the ancient wyrms (SB01-SB04) also drop a
  Wyrm Heart (50%).
- **Bestiary completion** (seen / defeated at 25-50-75-100%) pays items, never crowns: High Tonics and Brine Tonics,
  the Hunter's Tally, an Elixir and Starmetal, the Hunter's Codex; Heartsteel and Glowcap Draughts, Grand Tonics and
  Grave Lily Tinctures, the Lantern of the Living, a Wyrm Heart and three Elixirs.

## Region table
| Tier | Region / realm | Band | Stocked after | Item lv | Sword ATK | Sword | Best body | Head | Accessories | Gold / enemy (band lo-hi) | Gold / battle (mid) | Battles per kit | Inn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R01 | Crown March | 1-12 | CH01 | 4.3 | 11 | 200 | 250 | 250 | 300/320 | 16-82 | 107 | 7 | canon (25/hero, max 150) |
| R02 | Cinder Reach | 10-18 | CH03 | 12.4 | 18 | 450 | 580 | 810 | 640/750 | 70-135 | 206 | 9 | canon (25/hero, max 150) |
| R03 | Glass Coast | 14-22 | CH04 | 16.4 | 24 | 790 | 840 | 700 | 920/1090 | 94-182 | 297 | 8 | 60 |
| R08 | Mirewold | 16-24 | CH05 | 18.4 | 27 | 960 | 990 | 1010 | 1090/1290 | 113-208 | 345 | 9 | 80 |
| R04 | Skyspine | 18-26 | CH06 | 20.4 | 30 | 1150 | 1150 | 820 | 1260/1500 | 135-236 | 400 | 8 | 100 |
| U1 | Emberdeep | 18-30 | CH06 | 21.6 | 31 | 1300 | 1240 | 1110 | 1360/1610 | 135-296 | 457 | 8 | 110 |
| R06 | Ember Sea | 20-30 | CH06 | 23.0 | 33 | 1480 | 1350 | 900 | 1490/1760 | 157-296 | 488 | 8 | 90 |
| R05 | Pale Basin | 22-30 | CH08 | 24.4 | 34 | 1650 | 1460 | 1200 | 1610/1900 | 182-296 | 519 | 8 | 120 |
| R07 | Vermilion Reach | 24-32 | CH09 | 26.4 | 37 | 1900 | 1620 | 1010 | 1780/2110 | 208-329 | 583 | 8 | 140 |
| R09 | Hoarfrost March | 28-38 | CH09 | 31.0 | 43 | 2480 | 2170 | 1420 | 2390/2820 | 265-438 | 761 | 8 | 160 |
| U2 | The Lattice | 28-40 | CH10 | 31.6 | 44 | 2550 | 2330 | 1200 | 2560/3030 | 265-478 | 800 | 8 | 180 |
| WOR | World of Ruin | 30-40 | CH12 | 33.0 | 46 | 2920 | 2710 | 1520 | 2980/3520 | 296-478 | 840 | 9 | 200 |
| SKY | Shattered Choir | 30-42 | CH12 | 33.6 | 47 | 3110 | 2870 | 1300 | 3160/3730 | 296-519 | 880 | 8 | 200 |
| U3 | The Hollow Throne | 36-50 | CH15 | 40.2 | 59 | 5220 | 4650 | 1890 | 5120/6040 | 400-701 | 1188 | 10 | 250 |

Gold per enemy is the regular-enemy value at the band's low and high level. "Stocked after" is the chapter whose
completion puts the tier in the region's shops (`SHOP_TIERS` in gear2; weapons only for recruited heroes who can use
them). Canon reference: level 11 enemies pay 76 crowns (unchanged), level 30 pay 296 (canon 190), level 50 pay 701
(canon 310).

## Where the money goes (per region, one hero)
- Weapon upgrade every region (8 classes; new heroes use their template class, `cast.EQUIP_AS`).
- Body armour and head every region (5 pieces: plate, mail, robe, leather, head); two accessories per region.
- Smith upgrades (canon: ore + 30/45/60% of the price) still apply to every weapon and body armour, tier gear included.
- Crafting: early benches (R01-R02) charge 0-300 crowns a recipe; late benches up to 1300 for tier gear and 3000-6000
  for the named-item reforges and the Lantern of the Living, plus rare materials.
