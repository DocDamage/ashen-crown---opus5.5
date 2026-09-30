"""Group d places: the Deep U01-U19 (Emberdeep U1: dragonborn, delvers of Karag Dun, the Crown dig;
the Lattice U2: builder machines and their keepers). Maps in content_src/maps/x_d.map, scenes in x_d.scn."""

SHOPS = {'SHOP_U02': {'name': 'Stonebeard Outfitters', 'kinds': ['items', 'weapons', 'armor', 'accessories'], 'town': 'U02'},
 'SHOP_U03': {'name': "Scale-Smith's Counter", 'kinds': ['items', 'armor', 'accessories'], 'town': 'U03'},
 'SHOP_U07': {'name': "Boatwright's Stores", 'kinds': ['items', 'weapons', 'armor'], 'town': 'U07'},
 'SHOP_U13': {'name': 'Scaleward Stores', 'kinds': ['items', 'armor'], 'town': 'U13'},
 'SHOP_U15': {'name': "Umbel's Spore Shop", 'kinds': ['items', 'accessories'], 'town': 'U15'},
 'SHOP_U17': {'name': "Keepers' Exchange", 'kinds': ['items', 'weapons', 'armor', 'accessories'], 'town': 'U17'},
 'SHOP_U19': {'name': 'Railhead Stores', 'kinds': ['items', 'weapons', 'armor'], 'town': 'U19'}}

SPEAKERS = {'horrach': ['King Horrach', 'elder'],
 'hild': ['Hild Stonebeard', 'volunteer'],
 'orsik': ['Thane Orsik', 'clerk'],
 'pym': ['Factor Pym', 'guard'],
 'branna': ['Branna Coalhand', 'worker'],
 'nib': ['Nib the Pedlar', 'keeper'],
 'vessa': ['Vessa', 'volunteer'],
 'delver': ['Delver', 'worker'],
 'ysolde': ['Matron Ysolde', 'elder'],
 'dragonborn': ['Dragonborn', 'volunteer'],
 'coll': ['Ferryman Coll', 'sailor'],
 'grisk': ['Foreman Grisk', 'guard'],
 'islander': ['Islander', 'sailor'],
 'dunmore': ['Rail-Master Dunmore', 'worker'],
 'dagna': ['Foreman Dagna', 'worker'],
 'saelith': ['Elder Saelith', 'elder'],
 'kesh': ['Warden Kesh', 'guard'],
 'irrin': ['Irrin', 'volunteer'],
 'tamsin': ['Tamsin Carrow', 'worker'],
 'brask': ['Brask', 'guard'],
 'umbel': ['Grandmother Umbel', 'baker'],
 'terrace': ['Terrace Farmer', 'worker'],
 'liss': ['Keeper Liss', 'clerk'],
 'kiosk': ['Orders Kiosk', 'clerk'],
 'assembler': ['Assembler Prime', 'guard'],
 'noble': ['Traveller', 'clerk'],
 'lkeeper': ['Keeper', 'clerk'],
 'unit': ['Automaton', 'guard'],
 'juno': ['Signalwoman Juno', 'volunteer'],
 'tobin': ['Keeper Tobin', 'clerk']}

LOCATIONS = {'L_U01': {'name': 'The Breach', 'map': 'U01_R01', 'spawn': 'world'},
 'L_U02': {'name': 'Karag Dun', 'map': 'U02_R01', 'spawn': 'world'},
 'L_U03': {'name': 'Emberwell', 'map': 'U03_R01', 'spawn': 'world'},
 'L_U04': {'name': 'The Geode Wood', 'map': 'U04_R01', 'spawn': 'world'},
 'L_U05': {'name': 'Ossuary of Wings', 'map': 'U05_R01', 'spawn': 'world'},
 'L_U06': {'name': 'Magma Ferry', 'map': 'U06_R01', 'spawn': 'world'},
 'L_U07': {'name': 'Cinderlake Isles', 'map': 'U07_R01', 'spawn': 'world'},
 'L_U08': {'name': 'The Crown Dig', 'map': 'U08_R01', 'spawn': 'world'},
 'L_U09': {'name': 'Hearthroot Shrine', 'map': 'U09_R01', 'spawn': 'world'},
 'L_U10': {'name': 'Drakesleep Hollow', 'map': 'U10_R01', 'spawn': 'world'},
 'L_U11': {'name': 'Vaultmouth Rail', 'map': 'U11_R01', 'spawn': 'world'},
 'L_U12': {'name': 'Deepforge Mines', 'map': 'U12_R01', 'spawn': 'world'},
 'L_U13': {'name': 'Scaleward', 'map': 'U13_R01', 'spawn': 'world'},
 'L_U14': {'name': 'The Singing Chasm', 'map': 'U14_R01', 'spawn': 'world'},
 'L_U15': {'name': 'Fungal Terraces', 'map': 'U15_R01', 'spawn': 'world'},
 'L_U16': {'name': 'Lattice Gate', 'map': 'U16_R01', 'spawn': 'world'},
 'L_U17': {'name': 'Meridian', 'map': 'U17_R01', 'spawn': 'world'},
 'L_U18': {'name': 'The Assembly Floors', 'map': 'U18_R01', 'spawn': 'world'},
 'L_U19': {'name': 'Railhead Nine', 'map': 'U19_R01', 'spawn': 'world'}}

QUESTS = [{'id': 'QUP3',
  'name': 'The King Under the Mountain',
  'start': 'U02',
  'location': 'U12',
  'character': None,
  'hook': 'King Horrach Stonebeard of Karag Dun has signed eleven years of Crown debt for pumps, props and lamps '
          'while the Forge-Wurm holds his Deepforge Mines and his miners die',
  'objectives': 'Clear the Deepforge Mines of the Forge-Wurm; make Factor Pym show the debt contract in the Crown '
                'Counting House; bring it to the Stone Throne',
  'decision': 'Pay the true principal with clause four (the dead valued at four crowns each) struck out, or tear the '
              'contract up and defy the Crown',
  'result': 'Horrach reads his own debt for the first time; Karag Dun either pays on its own terms or stops shipping '
            'to the Crown',
  'reward': 'Delver Auger plans for the Lanternwake (flag lanternwake_auger), M002 x3, 3000 crowns',
  'boss': 'BX17'},
 {'id': 'QUP1',
  'name': "Emberwell's Debt",
  'start': 'U03',
  'location': 'U08',
  'character': None,
  'hook': "Matron Ysolde of Emberwell: the Crown claims a 'protection' debt, took forty-one young dragonborn for its "
          "dig, and a Crown pipe is drinking the enclave's ember-well cold",
  'objectives': "Find the tithe ledger in the Crown Dig's foreman's office; stop Foreman Grisk's Excavator at the "
                'dig face; bring word back to the Matron',
  'decision': 'Cut the Crown pipe and let the well warm for Emberwell alone, or turn the pipe round and send the '
              "heat to Karag Dun's forges in trade",
  'result': 'The labourers come home; Emberwell either stands alone and warm or bound to the delvers in a '
            'heat-for-iron pact',
  'reward': 'Deepstrider brackhorn (flag qup1_deepstrider), A105 Coal Heart, 2400 crowns',
  'boss': 'BX16'},
 {'id': 'QUP2',
  'name': 'Scaleward',
  'start': 'U13',
  'location': 'U14',
  'character': None,
  'hook': 'Elder Saelith of Scaleward, the hidden dragonborn refuge: nine Crown deserters from the dig are hiding in '
          'the Singing Chasm and ask to be let in; the council is split',
  'objectives': "Hear Tamsin Carrow's deserters at the Singing Chasm; hear Warden Kesh and the healer Irrin; bring "
                'your judgement to the council',
  'decision': "Let all nine in (including Brask, who whipped Emberwell's labourers), let in all but Brask, or keep "
              'the gate shut',
  'result': 'Scaleward opens, half-opens or stays hidden; the deserters settle inside or stay in the chasm',
  'reward': "A114 Kiln Ring or I024 Elixir and 1800 crowns; Scaleward's gratitude",
  'boss': None},
 {'id': 'QC16',
  'name': 'Standing Orders',
  'start': 'U17',
  'location': 'U23',
  'character': 'C16',
  'hook': "A dead orders-kiosk in Meridian's Stacks wakes for Kael-09: his standing orders are 'held', and routing "
          'is unavailable',
  'objectives': 'Meridian: read the orders kiosk with Kael-09; ask Keeper Liss; find the K-series line record on the '
                'Assembly Floors; bring it to Liss. Continues at Vault Omega (U23) and the Prime Relay (U24)',
  'decision': '(later) Whether Kael-09 accepts the orders CURATOR held for him or writes his own',
  'result': 'Kael-09 learns his orders were issued by CURATOR and are held at Vault Omega (flag qc16_meridian_done)',
  'reward': '(later chapters)',
  'boss': 'BX20'}]
