class_name FieldCmds
extends RefCounted
## Scene commands for the field and world systems (pass s3), run by the StoryDirector:
##   travel menu waystones [sigil]   the waystone roads (sigil: consumes one Wayfarer's Sigil on travel)
##   travel menu <net>               a travel network from content "travel" (rail_u1, mag_u2, lava_u1, lake_u2, lake_u3)
##   travel sleep morning|evening    sleep (inn scenes): heal and move the clock
##   travel surface | dive           the Lanternwake's diving hull (UNDERSEA <-> WORLD_POST)
##   travel undersea <spawn>         board the diving hull at a spawn of the sea floor (the Throat)
##   travel auger_up                 ride the auger winch from the Deep back to the ship over the Aurora Pit
##   arena <op>                      the Crucible Isle (arena.gd)
## Skipping a scene never skips a menu choice: travel menus only open when the player is in control.

static func run(main: Node, a: Array) -> void:
	var op: String = a[0] if a.size() > 0 else ""
	match op:
		"menu":
			var what: String = a[1] if a.size() > 1 else "waystones"
			if what == "waystones":
				await waystone_menu(main, a.size() > 2 and a[2] == "sigil")
			else:
				await network_menu(main, what)
		"sleep":
			var which: String = a[1] if a.size() > 1 else "morning"
			Game.heal_all()
			FieldSys.sleep_until(which)
			main.field.refresh_npcs()
		"surface":
			await main.field.sub_surface()
		"dive":
			await main.field.ship_dive()
		"undersea":
			Game.S["vehicle"]["mode"] = "sub"
			await main.warp(FieldSys.SEA_MAP, a[1] if a.size() > 1 else "default")
		"auger_up":
			await main.warp("WORLD_POST", "helm")
		_:
			push_error("travel: unknown op " + op)

static func _open(main: Node, title: String, tabs: Array, note: String = "") -> Dictionary:
	if main.director.skipping or QA.route != "":
		return {}
	var tm = TravelMenu.new()
	tm.main = main
	tm.setup(title, tabs, note)
	main.ui.add_child(tm)
	main.router.push(tm)
	var res = [{}]
	tm.done.connect(func(v): res[0] = v)
	await tm.done
	main.router.pop(tm)
	tm.queue_free()
	return res[0]

static func _here_waystone(main: Node) -> String:
	var f: Field = main.field
	for e in f.map.get("entities", []):
		if e["type"] == "waystone" and (Vector2i(e["x"], e["y"]) - f.p_tile).length() <= 1.5:
			return e["id"]
	return ""

static func waystone_menu(main: Node, sigil: bool) -> void:
	if not FieldSys.network_live():
		await main.say("", "The stone is cold. Since the fault the waystones answer nothing. Somewhere a beacon has to be lit first.")
		return
	var here = _here_waystone(main)
	var tabs = [["Surface", FieldSys.waystone_rows("surface", here)], ["The Deep", FieldSys.waystone_rows("deep", here)]]
	var note = "Left/Right: surface or the Deep" if not tabs[0][1].is_empty() and not tabs[1][1].is_empty() else ""
	if tabs[0][1].is_empty() and tabs[1][1].is_empty():
		await main.say("", "No other waystone is attuned yet. Touch a stone to bind it to the road.")
		return
	var pick: Dictionary = await _open(main, "Waystones", tabs, note)
	if pick.is_empty():
		return
	if sigil:
		if Game.count(FieldSys.WARP_ITEM) <= 0:
			return
		Game.remove_item(FieldSys.WARP_ITEM, 1)
	Audio.sfx("FX029")
	Game.S["vehicle"]["mode"] = "foot"
	await main.warp(str(pick["map"]), str(pick["spawn"]), "down")
	main.field.show_banner(str(pick["name"]))

static func network_menu(main: Node, net: String) -> void:
	var nd: Dictionary = FieldSys.network(net)
	if nd.is_empty():
		return
	var rows = FieldSys.network_rows(net, main.field.map_id)
	var pick: Dictionary = await _open(main, str(nd.get("name", net)), [["Where to?", rows]])
	if pick.is_empty():
		return
	Audio.sfx(str(nd.get("sfx", "FX010")))
	await main.fade(true, 0.4)
	if str(nd.get("line", "")) != "":
		await main.say("", str(nd["line"]))
	await main.warp(str(pick["map"]), str(pick["spawn"]), "down")
	await main.fade(false, 0.4)
	main.field.show_banner(str(pick["name"]))
