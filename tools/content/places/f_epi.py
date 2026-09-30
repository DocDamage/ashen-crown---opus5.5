"""Post-game epilogue arc: the Belfry Below (content_src/maps/x_epi.map, scenes x_epi.scn, boss BX27)."""
SPEAKERS = {"anse": ["Anse", "elder"]}
QUESTS = [
    {"id": "QEPI", "name": "The Bell That Rang Wrong", "start": "T07", "location": "EP4", "character": "C01",
     "hook": "After the victory, the Crown's sunken bell rings once under the Ember Sea, wrong; old bellwright Anse "
             "offers to lower the party in his diving bell",
     "objectives": "Ride the diving bell down to the Drowned Nave; climb the Bellrope Galleries; ring the carillon's three "
                   "bells in order; face the Wrong Bell in the belfry; come back up and tell Hearthward",
     "decision": "Whether the silenced bell is left in the deep or raised for Hearthward's harbour",
     "result": "The last note of the old Crown is rung right; the sea goes quiet",
     "reward": "The Right Bell (AN40), Veyr's Clapper (WN40), Carillon Mantle (GN40), Nave-Warden Plate (GN41)", "boss": "BX27"},
]
