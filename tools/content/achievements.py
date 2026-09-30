"""In-game achievements (sys s4). No platform API: the list, conditions and progress live in content.json
("achievements") and in the player's profile (user://profile.json) plus the save (S.achievements, carried by NG+).

Each entry: id -> {name, desc, cond, [progress], [hidden], [group]}
  cond      list of Game.eval_cond strings, all must hold. Besides the usual flag:/ch:/q:/var:/event:/clear forms the
            evaluator knows:
              defeated:<enemy id>       the enemy's bestiary entry has at least one defeat
              stat:<key><op><n>         Game.stat(key) counters (see below)
              meta:<key><op><n>         derived values: bestiary_pct, fish_species, fish_caught, max_level, recruited,
                                        vestiges, chests, quests, discovered, achv, gold, ng
            An empty cond means "event-only": the owning system calls Game.achieve(id) itself.
  progress  [value expression, target] for the progress bar, e.g. ["meta:bestiary_pct", 100]; inferred from a single
            numeric cond when omitted.
Counters other systems bump with Game.stat_add(key): battles, boss_wins, boss_nokos, superbosses (automatic, battle
transaction), fish_caught / fish_rare / fish_night / tourney_entries (fishing), crafted / gathered (crafting author),
secrets (hidden areas; secret-area author), arena_wins (arena author; the Arena rank is var:arena_rank), saves,
autosaves, ng_started.
"""

GROUPS = ["Story", "Battle", "Superbosses", "Collection", "Crafts", "Fishing", "Secrets"]

A = {}


def ach(aid, group, name, desc, cond, progress=None, hidden=False):
    A[aid] = {"id": aid, "group": group, "name": name, "desc": desc, "cond": cond, "hidden": hidden}
    if progress:
        A[aid]["progress"] = progress


# ---------------------------------------------------------------- story milestones
ach("ST01", "Story", "The Orders We Carry", "Finish the first chapter.", ["ch:CH01"])
ach("ST02", "Story", "A Road Without Banners", "Leave the Crown's road behind (Chapter 3).", ["ch:CH03"])
ach("ST03", "Story", "Paper Ghosts", "Read what the Drowned Archive kept (Chapter 5).", ["ch:CH05"])
ach("ST04", "Story", "To Borrow Sky", "Cross the Skyspine (Chapter 7).", ["ch:CH07"])
ach("ST05", "Story", "The Smaller Accord", "Bring the first accord together (Chapter 10).", ["ch:CH10"])
ach("ST06", "Story", "Crown of Cinders", "Live through the fault.", ["phase:post"])
ach("ST07", "Story", "The Engine That Waited", "Raise the Lanternwake (Chapter 16).", ["ch:CH16"])
ach("ST08", "Story", "The Ash Accord", "Gather everyone who is left (Chapter 20).", ["ch:CH20"])
ach("ST09", "Story", "Let the Names Remain", "Reach the end of the Final Descent.", ["ch:CH23"])
ach("ST10", "Story", "The First Unborrowed Morning", "See the ending.", ["clear"])
ach("ST11", "Story", "Again, With Scars", "Begin a New Game+.", ["meta:ng>=1"])
ach("ST12", "Story", "Every Road Walked", "Complete 20 questlines.", ["meta:quests>=20"], ["meta:quests", 20])
ach("ST13", "Story", "At the Last Second", "Bring every rescuer back up the Conduit lift.", ["flag:rescue_all"])
ach("ST14", "Story", "Still Five", "Reunite the Bound with everyone.", ["flag:bound_merged"])
ach("ST15", "Story", "The Right Note", "Silence the bell under drowned Veyr.", ["flag:epi_done"])
ach("ST16", "Story", "Every Map Filled", "Reach 100% completion.", ["meta:completion>=100"], ["meta:completion", 100])

# ---------------------------------------------------------------- battle
ach("BT01", "Battle", "Blooded", "Win 50 battles.", ["stat:battles>=50"])
ach("BT02", "Battle", "Veteran", "Win 500 battles.", ["stat:battles>=500"])
ach("BT03", "Battle", "Nobody Falls", "Defeat a boss without anyone being knocked out.", ["stat:boss_nokos>=1"])
ach("BT04", "Battle", "Unbroken Line", "Defeat 10 bosses without a knockout.", ["stat:boss_nokos>=10"])
ach("BT05", "Battle", "Headsman's Tally", "Defeat 25 bosses.", ["stat:boss_wins>=25"])
ach("BT06", "Battle", "Full Strength", "Raise a hero to level 50.", ["meta:max_level>=50"])
ach("BT07", "Battle", "The Old Limit", "Raise a hero to level 99.", ["meta:max_level>=99"])
ach("BT08", "Battle", "Past the Line", "Break the level cap: reach level 100.", ["meta:max_level>=100"])
ach("BT09", "Battle", "Second Ceiling", "Reach level 121 after another level break.", ["meta:max_level>=121"])
ach("BT11", "Battle", "Crucible Novice", "Reach rank 3 on the Crucible ladder.", ["var:arena_rank>=3"])
ach("BT12", "Battle", "Crucible Contender", "Reach rank 7 on the Crucible ladder.", ["var:arena_rank>=7"])
ach("BT13", "Battle", "Crucible Champion", "Reach the top of the Crucible ladder.", ["var:arena_rank>=10"])

# ---------------------------------------------------------------- superbosses (bosses2.py SB01-SB12)
_SB = [("SB01", "Cindermaw"), ("SB02", "Thalassar"), ("SB03", "Aerith-Vael"), ("SB04", "Ossathrax"), ("SB05", "CURATOR"),
       ("SB06", "Mother Sepulchre"), ("SB07", "Varro the Unbeaten"), ("SB08", "The Choir That Remains"),
       ("SB09", "the Ledger"), ("SB10", "the Tally"), ("SB11", "the Verdict"), ("SB12", "The Unmade Crown")]
for i, (sb, nm) in enumerate(_SB):
    ach("SB%02d" % (i + 1), "Superbosses", "Felled: " + nm, "Defeat %s." % nm, ["defeated:" + sb], hidden=i >= 8)
ach("SB13", "Superbosses", "The Four Wyrms", "Defeat all four ancient dragons.", ["defeated:SB01", "defeated:SB02", "defeated:SB03", "defeated:SB04"])
ach("SB14", "Superbosses", "Nothing Left to Fear", "Defeat every superboss.", ["stat:superbosses>=12"] + ["defeated:%s" % s for s, _ in _SB],
    ["stat:superbosses", 12])

# ---------------------------------------------------------------- collection
ach("CL01", "Collection", "Field Notes", "Fill 25% of the bestiary.", ["meta:bestiary_pct>=25"])
ach("CL02", "Collection", "Naturalist", "Fill 50% of the bestiary.", ["meta:bestiary_pct>=50"])
ach("CL03", "Collection", "Every Monster Named", "Fill the bestiary.", ["meta:bestiary_pct>=100"])
ach("CL04", "Collection", "The Seventeen", "Recruit all seventeen heroes.", ["meta:recruited>=17"], ["meta:recruited", 17])
ach("CL05", "Collection", "Vestige Bearer", "Hold 12 Vestiges.", ["meta:vestiges>=12"])
ach("CL06", "Collection", "Every Vestige", "Hold all 24 Vestiges.", ["meta:vestiges>=24"])
ach("CL07", "Collection", "Light Fingers", "Open 100 chests.", ["meta:chests>=100"])
ach("CL08", "Collection", "Cartographer", "Discover 60 places.", ["meta:discovered>=60"])

# ---------------------------------------------------------------- crafting and gathering (hooks for the crafting author)
ach("CR01", "Crafts", "First Rivet", "Craft something.", ["stat:crafted>=1"])
ach("CR02", "Crafts", "Journeyman", "Craft 25 items.", ["stat:crafted>=25"])
ach("CR03", "Crafts", "Master of the Bench", "Craft 100 items.", ["stat:crafted>=100"])
ach("CR04", "Crafts", "Gleaner", "Gather materials 50 times.", ["stat:gathered>=50"])

# ---------------------------------------------------------------- fishing (fishing.gd bumps the stats)
ach("FS01", "Fishing", "First Bite", "Land a fish.", ["stat:fish_caught>=1"])
ach("FS02", "Fishing", "Net Worth", "Land 100 fish.", ["stat:fish_caught>=100"])
ach("FS03", "Fishing", "Rare Waters", "Land a rare fish.", ["stat:fish_rare>=1"])
ach("FS04", "Fishing", "Night Line", "Land a fish that only bites after dark.", ["stat:fish_night>=1"])
ach("FS05", "Fishing", "Angler's Log", "Log 20 kinds of fish.", ["meta:fish_species>=20"])
ach("FS06", "Fishing", "Every Fin and Claw", "Log every kind of fish.", ["meta:fish_species>=44"])
ach("FS07", "Fishing", "The Silver Hook", "Win the Saltwhistle Open.", ["flag:fishing_champion"])

# ---------------------------------------------------------------- secrets and misc
ach("SC01", "Secrets", "Off the Map", "Find 5 secret places.", ["stat:secrets>=5"], hidden=True)
ach("SC02", "Secrets", "Nothing Stays Buried", "Find 20 secret places.", ["stat:secrets>=20"], hidden=True)
ach("SC04", "Secrets", "Completionist", "Unlock 45 other achievements.", ["meta:achv>=45"], ["meta:achv", 45])


def apply(content):
    content["achievements"] = {"groups": GROUPS, "list": A, "order": list(A.keys())}
    return content
