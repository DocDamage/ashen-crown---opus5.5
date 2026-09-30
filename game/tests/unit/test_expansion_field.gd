extends TestCase
## Field and world systems (expansion pass s3): the world clock and night conditions, encounters by phase and
## zone conditions, waystones and travel networks, Brackhorn terrain rules, airship upgrades and the sea floor,
## roaming wyrm gating and the arena ladder. Fixtures edit state directly (labelled unit evidence).

func _post(ch16: bool = true) -> void:
	fresh_game()
	Game.S["world_phase"] = "post"
	if ch16:
		Game.complete_chapter("CH16")

# ---------------------------------------------------------------- time
func test_night_conditions() -> void:
	fresh_game()
	eq(float(Game.S["clock"]), 480.0, "new games start at 08:00")
	Game.S["clock"] = 21.0 * 60.0
	check(Game.eval_cond(["night"]), "21:00 is night")
	check(not Game.eval_cond(["!night"]), "!night false at 21:00")
	check(not Game.eval_cond(["day"]), "day false at night")
	Game.S["clock"] = 3.0 * 60.0
	check(Game.eval_cond(["night"]), "03:00 is night")
	Game.S["clock"] = 12.0 * 60.0
	check(Game.eval_cond(["!night"]), "noon is not night")
	check(Game.eval_cond(["hour:10-14"]), "noon inside 10-14")
	check(not Game.eval_cond(["hour:14-18"]), "noon outside 14-18")
	Game.S["clock"] = 23.5 * 60.0
	check(Game.eval_cond(["hour:22-4"]), "hour ranges wrap past midnight (23:30 in 22-4)")
	Game.S["clock"] = 5.0 * 60.0
	check(not Game.eval_cond(["hour:22-4"]), "05:00 outside 22-4")
	check(Game.eval_cond(["hour:22-4"]) == false and Game.eval_cond(["!hour:22-4"]), "negated hour")

func test_sleep_and_day_counter() -> void:
	fresh_game()
	Game.S["clock"] = 22.0 * 60.0
	FieldSys.sleep_until("morning")
	eq(float(Game.S["clock"]), FieldSys.MORNING, "sleep until morning wakes at 06:00")
	eq(int(Game.S["day"]), 1, "sleeping past midnight counts a day")
	FieldSys.sleep_until("evening")
	eq(float(Game.S["clock"]), FieldSys.EVENING, "sleep until evening wakes at 18:00")
	eq(int(Game.S["day"]), 1, "morning to evening stays on the same day")
	Game.S["clock"] = 1439.0
	var flipped = FieldSys.advance(2.0)
	eq(int(Game.S["day"]), 2, "the clock rolling over midnight counts a day")
	check(not flipped, "01:00 is still night: no night change at midnight")
	Game.S["clock"] = 19.0 * 60.0 + 59.0
	check(FieldSys.advance(2.0), "20:00 starts the night (NPC schedules refresh)")

func test_npc_schedule_by_night() -> void:
	fresh_game()
	var f: Field = QA.main.field
	QA.main.enter_field("N01_R01", "default")
	var orig: Dictionary = f.map
	f.map = f.map.duplicate(true)
	f.map["entities"].append({"type": "npc", "id": "s3_night_watch", "x": 3, "y": 8, "dir": "down", "sprite": "worker", "talk": "", "wander": false,
		"name": "", "solid": true, "cond": ["night"]})
	Game.S["clock"] = 600.0
	f.refresh_npcs()
	check(f.actor("s3_night_watch").is_empty(), "if=night NPC absent by day")
	Game.S["clock"] = 1300.0
	f.refresh_npcs()
	check(not f.actor("s3_night_watch").is_empty(), "if=night NPC present at night")
	f.map = orig
	f.refresh_npcs()

# ---------------------------------------------------------------- encounters
func test_encounters_by_phase_and_zone_conditions() -> void:
	fresh_game()
	var f: Field = QA.main.field
	QA.main.enter_field("N01_R01", "default")
	var keep: Dictionary = f.map
	f.map = f.map.duplicate(true)
	f.map["encounters"] = "OW1"
	f.map["encounters_post"] = "OWP"
	eq(f.encounter_group(Vector2i(2, 2)), "OW1", "pre-fault uses encounters")
	Game.S["world_phase"] = "post"
	eq(f.encounter_group(Vector2i(2, 2)), "OWP", "post-fault uses encounters_post")
	f.map["entities"].append({"type": "zone", "x1": 0, "x2": 5, "y1": 0, "y2": 5, "encounters": "W_NIGHT", "cond": ["night"]})
	Game.S["clock"] = 600.0
	eq(f.encounter_group(Vector2i(2, 2)), "OWP", "a zone with a false if= is ignored")
	Game.S["clock"] = 1320.0
	eq(f.encounter_group(Vector2i(2, 2)), "W_NIGHT", "a zone with a true if= applies")
	eq(f.encounter_group(Vector2i(9, 9)), "OWP", "outside the zone")
	f.map["entities"].pop_back()
	f.map.erase("encounters_post")
	eq(f.encounter_group(Vector2i(2, 2)), "OW1", "no encounters_post: the map group stays after the fault")
	f.map = keep

func test_world_zones_and_night_mix() -> void:
	fresh_game()
	check(not Content.group("W_NIGHT").is_empty() and not Content.group("WP_NIGHT").is_empty(), "night groups exist")
	var f: Field = QA.main.field
	QA.main.enter_field("WORLD", "l_t01")
	eq(FieldSys.night_forms(false), [], "a level-3 party meets no night rares")
	Game.member("C01")["level"] = 40
	check(FieldSys.night_forms(false).size() == Content.group("W_NIGHT").size(), "a strong party meets them all")
	var forms = ["X1"]
	Game.S["clock"] = 600.0
	eq(f._night_mix(forms, Rng.new(5)), forms, "no night mix by day")
	Game.S["clock"] = 1320.0
	var mixed = 0
	for i in range(200):
		if f._night_mix(forms, Rng.new(Game.next_seed("enc"))) != forms:
			mixed += 1
	check(mixed > 20 and mixed < 120, "about a third of night fights come from W_NIGHT (%d of 200)" % mixed)
	QA.main.enter_field("DEEP", "default")
	eq(f._night_mix(forms, Rng.new(1)), forms, "no night mix underground")

# ---------------------------------------------------------------- waystones and travel
func test_waystones_attune_and_rows() -> void:
	fresh_game()
	var all = FieldSys.waystones()
	var ids = all.map(func(w): return w["id"])
	check(ids.has("WS_N02") and ids.has("WS_N41"), "Gallowgate and Oathstone stones on the pre-fault world")
	check(not ids.has("WS_P09"), "the Last Beacon's stone is post-fault only")
	check(ids.size() >= 9, "at least nine stones pre-fault (%d)" % ids.size())
	eq(FieldSys.waystone_rows("surface").size(), 0, "nothing listed before attuning")
	check(FieldSys.attune("WS_N02"), "first touch attunes")
	check(not FieldSys.attune("WS_N02"), "second touch is a no-op")
	FieldSys.attune("WS_T03")
	var rows = FieldSys.waystone_rows("surface", "WS_N02")
	var heads = rows.filter(func(r): return r.get("header", false)).map(func(r): return r["text"])
	eq(heads, ["Crown March", "Cinder Reach"], "grouped by region in world order")
	var here = rows.filter(func(r): return r.has("value") and r["value"]["id"] == "WS_N02")[0]
	check(not here["enabled"], "the stone you stand at is not a destination")
	for w in all:
		check(Content.map(w["map"]).get("entities", []).any(func(e): return e["type"] == "spawn" and e["name"] == w["spawn"]),
			"%s has its arrival spawn" % w["id"])

func test_waystone_touch_on_field_and_post_beacon() -> void:
	fresh_game()
	var f: Field = QA.main.field
	var ws: Dictionary = {}
	for e in Content.map("WORLD")["entities"]:
		if e["type"] == "waystone" and e["id"] == "WS_N41":
			ws = e
	check(not ws.is_empty(), "WS_N41 on WORLD")
	QA.main.enter_field("WORLD", "ws_n41")
	f.place_player(ws["x"], ws["y"], "down")
	f._on_arrive()
	check(FieldSys.is_attuned("WS_N41"), "stepping on the stone attunes it")
	check(FieldSys.network_live(), "pre-fault the network is live")
	Game.S["world_phase"] = "post"
	check(not FieldSys.network_live(), "after the fault the stones are dark")
	FieldSys.attune("WS_P09")
	check(FieldSys.network_live(), "the Last Beacon relights the network")
	check(FieldSys.waystones().any(func(w): return w["id"] == "WS_P09" and w["map"] == "WORLD_POST"), "post stones live on WORLD_POST")

func test_warp_item_rules() -> void:
	fresh_game()
	check(Content.item(FieldSys.WARP_ITEM).get("special", "") == "warp", "Wayfarer's Sigil is a warp item")
	var f: Field = QA.main.field
	QA.main.enter_field("WORLD", "l_t01")
	check(FieldSys.warp_allowed(f), "works on the world map")
	QA.main.enter_field("N01_R01", "default")
	check(FieldSys.warp_allowed(f), "works in a town")
	QA.main.enter_field("D01_R01", "default")
	check(not FieldSys.warp_allowed(f), "not in a dungeon")

func test_travel_networks() -> void:
	fresh_game()
	for net in ["rail_u1", "mag_u2", "lava_u1", "lake_u2", "lake_u3"]:
		check(not FieldSys.network(net).is_empty(), "network %s exists" % net)
	var pre = FieldSys.network_rows("lava_u1", "U06_R01").map(func(r): return r["value"]["id"])
	eq(pre, ["U06", "U07"], "pre-fault skiffs: Magma Ferry and Cinderlake Isles")
	Game.S["world_phase"] = "post"
	var post = FieldSys.network_rows("lava_u1", "U06_R01")
	eq(post.map(func(r): return r["value"]["id"]), ["U06", "U15"], "post-fault: Cinderlake is lost, the Terraces channel opens")
	check(not post[0]["enabled"], "the current landing is marked, not a destination")

# ---------------------------------------------------------------- vehicles
func test_brackhorn_terrain_rules() -> void:
	fresh_game()
	Game.S["vehicle"]["mount"] = true
	eq(FieldSys.mounts_owned(), ["bramble"], "only Bramble without quest flags")
	check(FieldSys.can_ride("plains", "WORLD", "bramble"), "Bramble rides plains")
	check(not FieldSys.can_ride("hills", "WORLD", "bramble"), "Bramble balks at hills")
	check(FieldSys.can_ride("hills", "WORLD", "ridgehorn") and FieldSys.can_ride("rocky", "WORLD", "ridgehorn"), "Ridgehorn: hills and rocky")
	check(FieldSys.can_ride("swamp", "WORLD", "fenwader") and not FieldSys.can_ride("swamp", "WORLD", "ridgehorn"), "Fenwader: swamp")
	check(FieldSys.mount_passes("water", "WORLD", "fenwader", true), "Fenwader wades shore water")
	check(not FieldSys.mount_passes("water", "WORLD", "fenwader", false), "but not open water")
	check(not FieldSys.mount_passes("water", "WORLD", "ridgehorn", true), "no other mount wades")
	check(not FieldSys.can_ride("cave_floor", "DEEP", "bramble"), "surface mounts are led on foot in the Deep")
	check(FieldSys.can_ride("cave_floor", "DEEP_POST", "deepstrider") and FieldSys.mount_passes("lava", "DEEP", "deepstrider", false), "Deepstrider: Deep floors and lava crust")
	check(not FieldSys.mount_passes("lava", "WORLD", "deepstrider", false), "no lava crossing on the surface")
	check(FieldSys.MOUNT_SPEED["gilded"] > FieldSys.MOUNT_SPEED["bramble"], "Gilded is the fastest")
	check(not FieldSys.set_mount("ridgehorn"), "a locked variant cannot be chosen")
	Game.set_flag("brackhorn_ridgehorn")
	Game.set_flag("qup1_deepstrider")
	eq(FieldSys.mounts_owned(), ["bramble", "ridgehorn", "deepstrider"], "variants unlock by flag")
	eq(FieldSys.cycle_mount(1), "ridgehorn", "cycle forward")
	eq(FieldSys.cycle_mount(1), "deepstrider", "cycle skips locked variants")
	eq(FieldSys.cycle_mount(1), "bramble", "cycle wraps")
	eq(FieldSys.cycle_mount(-1), "deepstrider", "cycle back")

func test_mount_on_field_collision() -> void:
	fresh_game()
	var f: Field = QA.main.field
	QA.main.enter_field("WORLD", "l_t01")
	Game.S["vehicle"]["mount"] = true
	# find a shore water cell next to walkable land
	var cell = Vector2i(-1, -1)
	for y in range(f.H):
		for x in range(f.W):
			if f.kind_at(x, y) == "water" and not f.solid_set.has(f.kind_at(x + 1, y)) and f.kind_at(x + 1, y) != "void":
				cell = Vector2i(x, y)
				break
		if cell.x >= 0:
			break
	check(cell.x >= 0, "a shore cell exists")
	check(f.solid_at(cell.x, cell.y), "shore water is solid for Bramble (and on foot)")
	Game.set_flag("brackhorn_fenwader")
	FieldSys.set_mount("fenwader")
	if QA.route == "":
		check(not f.solid_at(cell.x, cell.y), "Fenwader wades the shore water")
		check(f.solid_at(cell.x, cell.y, true), "NPC collision is unchanged")

func test_airship_upgrades_and_sea_floor() -> void:
	_post()
	var f: Field = QA.main.field
	check(Content.data["maps"].has("UNDERSEA"), "UNDERSEA map exists")
	var um: Dictionary = Content.map("UNDERSEA")
	eq(um.get("kind", ""), "world", "UNDERSEA is a world-kind map")
	check(int(um["w"]) < 176 and int(um["h"]) < 132, "the sea floor is smaller than the surface")
	var names = um["entities"].filter(func(e): return e["type"] == "location").map(func(e): return e["dest"])
	for d in ["S3_OLDBELL", "S3_DROWNED", "S3_TITHE", "S3_REEF", "S3_CRADLE", "U40_R01"]:
		check(names.has(d) and Content.data["maps"].has(d), "sea floor place -> %s" % d)
	eq(FieldSys.from_sea(FieldSys.to_sea(Vector2i(100, 60))).distance_to(Vector2i(100, 60)) <= 2.0, true, "dive / surface cells line up")
	# on the sea floor the party is always in the diving hull, with a Mode-7 fallback when the art is missing
	QA.main.enter_field("UNDERSEA", "default")
	eq(f.vehicle, "sub", "UNDERSEA is travelled by submarine")
	check(f.m7 != null, "Mode-7 works on UNDERSEA (baked art or grid fallback)")
	check(f.hud != null, "the minimap works on UNDERSEA")
	eq(f.vehicle_action(), "Surface", "the run key surfaces")
	# the airship: dive needs the Diving Hull over open ocean
	Game.S["vehicle"]["ship"] = true
	Game.S["vehicle"]["ship_map"] = "WORLD_POST"
	var deep_cell = Vector2i(-1, -1)
	var wp: Dictionary = Content.map("WORLD_POST")
	for y in range(40, int(wp["h"])):
		for x in range(int(wp["w"])):
			if wp["legend"].get(String(wp["grid"][y][x]), "") == "deep":
				deep_cell = Vector2i(x, y)
				break
		if deep_cell.x >= 0:
			break
	Game.S["vehicle"]["ship_x"] = deep_cell.x
	Game.S["vehicle"]["ship_y"] = deep_cell.y
	QA.main.enter_field("WORLD_POST", "helm")
	eq(f.vehicle, "ship", "aboard the Lanternwake")
	eq(f.vehicle_action(), "", "no dive without the Diving Hull")
	Game.set_flag("lanternwake_diving")
	eq(f.vehicle_action(), "Dive", "dive over open ocean")
	# grapnel keel: landing anywhere
	check(not FieldSys.grapnel(), "no grapnel yet")
	Game.set_flag("lanternwake_grapnel")
	check(FieldSys.grapnel(), "Grapnel Keel flag")
	Game.set_flag("lanternwake_auger")
	check(FieldSys.auger(), "the auger works after the fault")
	check(Content.map("DEEP_POST")["entities"].any(func(e): return e["type"] == "spawn" and e["name"] == "auger"), "the auger shaft lands in DEEP_POST")

func test_sky_isle_landing() -> void:
	_post()
	Game.complete_chapter("CH07")
	var wp: Dictionary = Content.map("WORLD_POST")
	var loc = wp["entities"].filter(func(e): return e["type"] == "location" and e["id"] == "L_N38")
	check(not loc.is_empty() and loc[0].get("land", false), "the Crucible Isle is a land-only location")
	check(wp["entities"].any(func(e): return e["type"] == "landing" and e["name"] == "Crucible Isle"), "a post-fault landing for N38")
	check(wp["entities"].any(func(e): return e["type"] == "spawn" and e["name"] == "l_n38"), "and its return spawn")
	var f: Field = QA.main.field
	QA.main.enter_field("WORLD_POST", "l_n38")
	check(not f._land_location(Vector2i(loc[0]["x"], loc[0]["y"])).is_empty(), "the airship finds the isle's dock")

# ---------------------------------------------------------------- wyrms
func test_roaming_wyrms_gating() -> void:
	fresh_game()
	check(not Wyrms.active("SB01"), "no wyrms before the fault")
	_post(false)
	check(not Wyrms.active("SB01"), "no wyrms before CH16")
	_post(true)
	check(Wyrms.active("SB01") and Wyrms.active("SB03"), "wyrms roam after CH16")
	var f: Field = QA.main.field
	QA.main.enter_field("WORLD_POST", "l_t07")
	var ids = f.wyrms.list.map(func(w): return w["id"])
	check(ids.has("SB01") and ids.has("SB02") and ids.has("SB03"), "Cindermaw, Thalassar and Aerith-Vael on WORLD_POST (%s)" % str(ids))
	check(not ids.has("SB04"), "Ossathrax stays in the Deep")
	Game.set_flag("sb_SB01_down")
	QA.main.enter_field("WORLD_POST", "l_t07")
	check(not f.wyrms.list.any(func(w): return w["id"] == "SB01"), "a beaten wyrm stops appearing")
	QA.main.enter_field("DEEP_POST", "default")
	check(f.wyrms.list.any(func(w): return w["id"] == "SB04"), "Ossathrax roams DEEP_POST")
	for sb in ["SB01", "SB02", "SB03", "SB04"]:
		check(Content.scene("WYRM_" + sb).get("cmds", []).any(func(c): return c["c"] == "battle" and c["a"][0] == sb and c["a"].has("noflee")), "WYRM_%s runs battle %s noflee" % [sb, sb])

# ---------------------------------------------------------------- weather
func test_weather_rules() -> void:
	fresh_game()
	var wm: Dictionary = Content.map("WORLD")
	var z = wm["entities"].filter(func(e): return e["type"] == "zone" and e["encounters"] == "W_R09")[0]
	var got = {}
	for day in range(40):
		Game.S["day"] = day
		got[FieldSys.weather_at(wm, "WORLD", Vector2i(z["x1"], z["y1"]))] = true
	check(got.has("snow"), "Hoarfrost March snows")
	check(not got.has("rain"), "and never rains")
	eq(FieldSys.weather_at(Content.map("DEEP"), "DEEP", Vector2i(10, 10)), "", "no weather in the Deep")
	eq(FieldSys.weather_at(Content.map("N38_ARENA"), "N38_ARENA", Vector2i(1, 1)), "", "weather: none indoors")
	eq(FieldSys.weather_at(Content.map("N38_R01"), "N38_R01", Vector2i(1, 1)), "fog", "a map header can fix the weather")
	Settings.set_v("weather", false)
	eq(FieldSys.weather_at(Content.map("N38_R01"), "N38_R01", Vector2i(1, 1)), "", "Settings turns weather off")
	Settings.set_v("weather", true)

# ---------------------------------------------------------------- arena
func test_arena_ladder_progression() -> void:
	fresh_game()
	var lad: Array = Content.data["arena"]["ladder"]
	eq(lad.size(), 10, "ten ranks")
	for i in range(lad.size() - 1):
		var a = Content.formation(lad[i]["form"])
		var b = Content.formation(lad[i + 1]["form"])
		check(not a.is_empty() and not b.is_empty(), "rank formations exist")
	eq(int(Arena.next_rank()["rank"]), 1, "start at rank 1")
	eq(Arena.win_rank(2), {}, "cannot skip to rank 2")
	var g0 = Game.gold()
	var r1 = Arena.win_rank(1)
	eq(int(r1.get("rank", 0)), 1, "rank 1 won")
	check(Game.count(str(r1["reward"])) >= int(r1["n"]) and Game.gold() == g0 + int(r1["gold"]), "rank reward paid")
	eq(Arena.win_rank(1), {}, "a rank pays once")
	for n in range(2, 7):
		if n == 6:
			Game.complete_chapter("CH09")
		check(not Arena.win_rank(n).is_empty(), "rank %d" % n)
	eq(Arena.rank(), 6, "rank 6 reached pre-fault")
	check(not Arena.next_rank()["open"], "rank 7 waits for the World of Ruin")
	eq(Arena.win_rank(7), {}, "a closed rank cannot be won")
	Game.S["world_phase"] = "post"
	for n in range(7, 11):
		check(not Arena.win_rank(n).is_empty(), "rank %d post-fault" % n)
	check(Arena.ladder_done(), "ladder complete")
	check(not Arena.gauntlet_open(), "gauntlet needs CH16")
	Game.complete_chapter("CH16")
	check(Arena.gauntlet_open(), "gauntlet opens at the top of the ladder after CH16")
	eq(Content.data["arena"]["gauntlet"][-1], "SB07", "Varro is the last fight")

func test_arena_solo_bets_beasts() -> void:
	fresh_game()
	var rows = Arena.solo_rows()
	check(not rows[0]["open"], "solo bouts open with ladder rank")
	Game.S["arena"]["rank"] = 2
	check(Arena.solo_rows()[0]["open"], "first solo bout at rank 2")
	check(Arena.win_solo("solo1") and not Arena.win_solo("solo1"), "solo reward once")
	Game.add_item("I001", 2)
	var b = Arena.bet_rows().filter(func(x): return x["wager"] == "I001")[0]
	var before = Game.count("I002")
	check(Arena.settle_bet(b, true), "won bet pays")
	eq(Game.count("I002"), before + 1, "prize added")
	check(not Arena.settle_bet(b, false), "lost bet pays nothing")
	eq(Game.count("I001"), 6, "each bet spends the wager (6 starting + 2 - 2)")
	eq(Arena.captured(), [], "no captured monsters by default")
	Game.S["captured"] = ["E041", {"id": "E046"}, "nope"]
	eq(Arena.captured(), ["E041", "E046"], "captured list from ids or dicts, unknown ids dropped")
	Game.S.erase("captured")

# ---------------------------------------------------------------- integration: real menus, warps and vehicles
func _frames(n: int) -> void:
	for i in range(n):
		await QA.main.get_tree().process_frame

func _wait_map(mid: String, max_frames: int = 240) -> bool:
	for i in range(max_frames):
		if QA.main.field.map_id == mid and not QA.main.field.busy:
			return true
		await QA.main.get_tree().process_frame
	return QA.main.field.map_id == mid

func test_waystone_menu_travels() -> void:
	fresh_game()
	FieldSys.attune("WS_N41")
	FieldSys.attune("WS_T03")
	QA.main.enter_field("WORLD", "ws_n41")
	var f: Field = QA.main.field
	FieldCmds.waystone_menu(QA.main, false)
	await _frames(3)
	var top = QA.main.router.top()
	check(top is TravelMenu, "the travel menu has focus")
	if top is TravelMenu:
		eq(str(top.list.current().get("value", {}).get("id", "")), "WS_T03", "cursor starts on the first other stone")
		top.handle("confirm")
	check(await _wait_map("WORLD"), "still on the world map")
	await _frames(30)
	var sp = GalleryS3._at("WORLD", "ws_t03")
	eq(f.p_tile, sp, "arrived at the Cinderwake waystone")

func test_sigil_consumed_only_on_travel() -> void:
	fresh_game()
	FieldSys.attune("WS_N41")
	FieldSys.attune("WS_T03")
	Game.add_item(FieldSys.WARP_ITEM, 2)
	QA.main.enter_field("N01_R01", "default")
	FieldCmds.waystone_menu(QA.main, true)
	await _frames(3)
	var top = QA.main.router.top()
	if top is TravelMenu:
		top.handle("cancel")
	await _frames(3)
	eq(Game.count(FieldSys.WARP_ITEM), 2, "cancelling keeps the sigil")
	FieldCmds.waystone_menu(QA.main, true)
	await _frames(3)
	top = QA.main.router.top()
	if top is TravelMenu:
		top.handle("confirm")
	check(await _wait_map("WORLD"), "the sigil carries the party to a stone")
	eq(Game.count(FieldSys.WARP_ITEM), 1, "one sigil spent")

func test_dive_and_surface() -> void:
	_post()
	Game.set_flag("lanternwake_diving")
	var f: Field = QA.main.field
	var oc = FieldSys.nearest_cell("WORLD_POST", Vector2i(120, 128), func(k): return k == "deep")
	Game.S["vehicle"]["ship"] = true
	Game.S["vehicle"]["ship_map"] = "WORLD_POST"
	Game.S["vehicle"]["ship_x"] = oc.x
	Game.S["vehicle"]["ship_y"] = oc.y
	QA.main.enter_field("WORLD_POST", "helm")
	eq(f.vehicle_action(), "Dive", "dive offered over open ocean")
	await f.ship_dive()
	eq(f.map_id, "UNDERSEA", "dived to the sea floor")
	eq(f.vehicle, "sub", "in the diving hull")
	check(not FieldSys.sub_solid(f.kind_at(f.p_tile.x, f.p_tile.y)), "placed on open sea floor")
	check(f.p_tile.distance_to(FieldSys.to_sea(oc)) < 6.0, "under the dive point")
	await f.sub_surface()
	eq(f.map_id, "WORLD_POST", "surfaced")
	eq(f.vehicle, "ship", "aloft again")
	check(f.p_tile.distance_to(oc) < 12.0, "near the dive point (%s vs %s)" % [str(f.p_tile), str(oc)])

func test_sky_cable_to_arena() -> void:
	fresh_game()
	for ch in ["CH01", "CH02", "CH03", "CH04", "CH05", "CH06", "CH07"]:
		Game.complete_chapter(ch)
	var sc = Content.scene("CABLE_CHOIR")
	check(sc["cmds"].any(func(c): return c["c"] == "warp" and c["a"][0] == "N38_R01"), "the Ninefold cable reaches the Crucible Isle")
	var m = Content.map("N38_R01")
	var ex = m["entities"].filter(func(e): return e["type"] == "exit" and e["dest"] == "WORLD")
	check(not ex.is_empty() and ex[0]["cond"] == ["!phase:post"], "pre-fault the cable is the way back")
	check(m["entities"].any(func(e): return e["type"] == "exit" and e["dest"] == "WORLD_POST"), "post-fault the airship field is")

func test_arena_loss_is_not_game_over() -> void:
	fresh_game()
	QA.main.enter_field("N38_ARENA", "entry")
	var gold = Game.gold()
	var res = [""]
	var run = func():
		res[0] = await QA.main.run_battle("D04_5", {"scripted": true, "flags": ["noflee"], "arena": true})
	run.call()
	for i in range(300):
		if QA.main.battle != null and QA.main.fade_rect.color.a <= 0.001:
			break
		await QA.main.get_tree().process_frame
	for i in range(10):
		await QA.main.get_tree().process_frame
	check(QA.main.battle != null, "the arena bout started")
	if QA.main.battle != null:
		QA.main.battle.emit_signal("finished", "defeat")
	for i in range(240):
		if res[0] != "":
			break
		await QA.main.get_tree().process_frame
	eq(res[0], "defeat", "a lost bout returns defeat")
	eq(QA.main.mode, "field", "back in the field, no game-over menu")
	eq(QA.main.field.map_id, "N38_ARENA", "still in the hall")
	eq(Game.gold(), gold, "the checkpoint restored the state")
	check(int(Game.member("C01")["hp"]) > 0, "the party is restored")
