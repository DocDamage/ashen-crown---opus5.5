class_name GalleryS3
extends RefCounted
## --qa-gallery-set sys_s3: screenshots of the field and world systems (night world, waystones and the travel
## menu, Brackhorn variants, weather, the sea floor, roaming wyrms, the Crucible Isle arena, the inn sleep menu).
## Dev review only: it edits state freely.

static func _at(mid: String, spawn: String) -> Vector2i:
	for e in Content.map(mid).get("entities", []):
		if e["type"] == "spawn" and e["name"] == spawn:
			return Vector2i(e["x"], e["y"])
	return Vector2i(-1, -1)

static func _go(qa: Node, main: Node, mid: String, spawn: String, dir: String = "down", off: Vector2i = Vector2i.ZERO) -> void:
	var at = _at(mid, spawn)
	if off != Vector2i.ZERO:
		# step clear of the landmark billboard: the nearest cell the party can stand on around the offset
		main.enter_field(mid, spawn, at, dir)
		var f: Field = main.field
		var ok = func(k): return not f.solid_set.has(k)
		var c = FieldSys.nearest_cell(mid, at + off, ok, 4)
		if c.x >= 0:
			at = c
	main.enter_field(mid, spawn, at, dir)
	main.field.banner_t = 0.0
	await qa._g_frames(6)
	if main.field.m7 != null:
		main.field.m7.snap(main.field.p_pos + Vector2(8, 12), main.field.m7.profile_key(main.field.vehicle, main.field.riding()))
	await qa._g_frames(4)

static func run(qa: Node, main: Node) -> void:
	var f: Field = main.field
	for cid in ["C02", "C03", "C04"]:
		Game.recruit(cid)
	for ch in ["CH01", "CH02", "CH03", "CH04", "CH05", "CH06", "CH07", "CH08", "CH09"]:
		Game.complete_chapter(ch)
	# 1) night on the world map beside the Gallowgate waystone (attuned: its rune glows)
	FieldSys.attune("WS_N02")
	FieldSys.attune("WS_N41")
	FieldSys.attune("WS_T03")
	FieldSys.attune("WS_T04")
	FieldSys.attune("WS_U02")
	Game.S["clock"] = 1330.0
	await _go(qa, main, "WORLD", "ws_n02", "down", Vector2i(1, 2))
	await qa._g_shot("s3_world_night_waystone")
	Game.S["clock"] = 700.0
	await qa._g_frames(3)
	await qa._g_shot("s3_world_day_waystone")
	# 2) the waystone travel menu (surface tab, then the Deep tab)
	var tm = TravelMenu.new()
	tm.main = main
	var here = FieldCmds._here_waystone(main)
	tm.setup("Waystones", [["Surface", FieldSys.waystone_rows("surface", here)], ["The Deep", FieldSys.waystone_rows("deep", here)]], "Left/Right: surface or the Deep")
	main.ui.add_child(tm)
	await qa._g_frames(6)
	await qa._g_shot("s3_waystone_menu")
	tm.handle("right")
	await qa._g_frames(4)
	await qa._g_shot("s3_waystone_menu_deep")
	tm.queue_free()
	var tn = TravelMenu.new()
	tn.main = main
	tn.setup("Delver Mine-Rail", [["Where to?", FieldSys.network_rows("rail_u1", "U11_R01")]])
	main.ui.add_child(tn)
	await qa._g_frames(6)
	await qa._g_shot("s3_rail_menu")
	tn.queue_free()
	# 3) Brackhorn variants: Ridgehorn in the Skyspine hills, Gilded on the plains, Deepstrider in the Deep
	Game.S["vehicle"]["mount"] = true
	for fl in ["brackhorn_ridgehorn", "brackhorn_fenwader", "qup1_deepstrider", "brackhorn_gilded"]:
		Game.set_flag(fl)
	FieldSys.set_mount("ridgehorn")
	await _go(qa, main, "WORLD", "l_t05", "down", Vector2i(0, 4))
	f.p_dir = "right"
	await qa._g_frames(4)
	await qa._g_shot("s3_mount_ridgehorn")
	FieldSys.set_mount("gilded")
	await _go(qa, main, "WORLD", "l_t01", "down", Vector2i(0, 4))
	f.p_dir = "left"
	await qa._g_frames(4)
	await qa._g_shot("s3_mount_gilded")
	FieldSys.set_mount("fenwader")
	await _go(qa, main, "WORLD", "l_n22", "down", Vector2i(3, 3))
	await qa._g_shot("s3_mount_fenwader_fog")
	FieldSys.set_mount("deepstrider")
	await _go(qa, main, "DEEP", "l_u02")
	await qa._g_shot("s3_mount_deepstrider")
	Game.S["vehicle"]["mount"] = false
	# 4) weather: snow (Hoarfrost), ash (Cinder Reach), sandstorm (Pale Basin), rain (a town), fog (the sky isle)
	for w in [["WORLD", "l_n32", "snow"], ["WORLD", "l_t03", "ash"], ["WORLD", "l_t06", "sandstorm"], ["N01_R01", "default", "rain"]]:
		await _go(qa, main, w[0], w[1])
		f.weather.want(w[2], true)
		f._weather_t = 999.0
		await qa._g_frames(8)
		await qa._g_shot("s3_weather_%s" % w[2])
	f._weather_t = 0.0
	# 5) the Crucible Isle arena (pre-fault, by the sky cable)
	for m in [["N38_R01", "cable"], ["N38_ARENA", "entry"], ["N38_PIT", "entry"]]:
		await _go(qa, main, m[0], m[1], "up")
		await qa._g_shot("s3_arena_%s" % m[0])
	# 6) the inn menu with the sleep options
	await qa._g_menu("inn", {"price": 60}, "s3_inn_sleep")
	# 7) World of Ruin after CH16: roaming wyrms, the airship over the ocean, the sea floor in the diving hull
	Game.S["world_phase"] = "post"
	Game.complete_chapter("CH16")
	Game.set_flag("lanternwake_diving")
	await _go(qa, main, "WORLD_POST", "l_n10")
	for w in f.wyrms.list:
		if w["id"] == "SB01":
			w["pos"] = Vector2(f.p_tile) + Vector2(1, -3)
			w["target"] = w["pos"]
	await qa._g_frames(4)
	await qa._g_shot("s3_wyrm_cindermaw")
	Game.S["vehicle"]["ship"] = true
	Game.S["vehicle"]["ship_map"] = "WORLD_POST"
	var oc = FieldSys.nearest_cell("WORLD_POST", Vector2i(120, 128), func(k): return k == "deep")
	Game.S["vehicle"]["ship_x"] = oc.x
	Game.S["vehicle"]["ship_y"] = oc.y
	main.enter_field("WORLD_POST", "helm")
	f.banner_t = 0.0
	await qa._g_frames(6)
	f.m7.snap(f.p_pos + Vector2(8, 12), "ship")
	for w in f.wyrms.list:
		if w["id"] == "SB03":
			w["pos"] = Vector2(f.p_tile) + Vector2(-2, -4)
			w["target"] = w["pos"]
	await qa._g_frames(6)
	await qa._g_shot("s3_airship_dive_hint_skywyrm")
	var t = FieldSys.nearest_cell(FieldSys.SEA_MAP, FieldSys.to_sea(f.p_tile), func(k): return not FieldSys.sub_solid(k))
	main.enter_field(FieldSys.SEA_MAP, "default", t, "down")
	f.banner_t = 0.0
	await qa._g_frames(6)
	f.m7.snap(f.p_pos + Vector2(8, 12), "sub")
	for w in f.wyrms.list:
		if w["id"] == "SB02":
			w["pos"] = Vector2(f.p_tile) + Vector2(2, -3)
			w["target"] = w["pos"]
	await qa._g_frames(6)
	await qa._g_shot("s3_undersea_sub_thalassar")
	await _go(qa, main, FieldSys.SEA_MAP, "l_s01")
	await qa._g_shot("s3_undersea_oldbell")
	f.hud.reveal(f.p_tile, 60)
	f.show_map = true
	await qa._g_frames(6)
	await qa._g_shot("s3_undersea_fullmap")
	f.show_map = false
	for m in [["S3_OLDBELL", "default"], ["S3_TITHE", "default"], ["S3_CRADLE", "default"]]:
		await _go(qa, main, m[0], m[1], "up")
		await qa._g_shot("s3_sea_%s" % m[0])
	await _go(qa, main, "DEEP_POST", "l_u30")
	for w in f.wyrms.list:
		if w["id"] == "SB04":
			w["pos"] = Vector2(f.p_tile) + Vector2(2, -3)
			w["target"] = w["pos"]
	await qa._g_frames(4)
	await qa._g_shot("s3_wyrm_ossathrax")
