extends TestCase
## Ranching (meta/ranch.gd): content, livestock production over the world clock, crop plots, conditions, old saves.

func _at(day: int, clock: float) -> void:
	Game.S["day"] = day
	Game.S["clock"] = clock

func test_ranch_content() -> void:
	var d = Ranch.data()
	eq(Ranch.order().size(), 8, "eight ranches")
	for rid in Ranch.order():
		var r = Ranch.info(rid)
		check(Content.data["maps"].has(str(r["map"])), "%s map %s exists" % [rid, r["map"]])
		check(Content.data["shops"].has(str(r["shop"])), "%s seed box exists" % rid)
		check(r["animals"].size() >= 3, "%s sells three kinds of livestock" % rid)
		for c in r["seeds"]:
			check(Content.data["items"].has(str(Ranch.crop(c)["seed"])), "%s seed item for %s" % [rid, c])
	for k in d["animals"]:
		check(Content.data["items"].has(str(d["animals"][k]["good"])), "good item for %s" % k)
	for iid in ["RK01", "RK02", "RK03", "RK04", "RF01", "RA01"]:
		check(Content.item(iid).get("sellable", false), "%s sells" % iid)
	check(Content.item("RK01").get("kind", "") == "consumable", "milk is a consumable")
	var cooked = 0
	for rc in Content.data["gear2"]["recipes"].values():
		if str(rc["result"]).begins_with("RF") or str(rc["result"]) == "RA01":
			cooked += 1
	check(cooked >= 6, "cooking recipes registered (%d)" % cooked)

func test_buy_once_and_produce() -> void:
	fresh_game()
	_at(0, 480.0)
	Game.S["inventory"]["gold"] = 5000
	eq(Ranch.can_buy("R01", "cow"), "ok", "a cow is for sale at Fallowmere")
	eq(Ranch.can_buy("R01", "bunny"), "unknown", "Fallowmere sells no coneys")
	eq(Ranch.buy("R01", "cow"), "ok", "bought")
	eq(Game.gold(), 5000 - Ranch.price("R01", "cow"), "price paid")
	eq(Ranch.buy("R01", "cow"), "owned", "only once per kind per ranch")
	check(Ranch.cond(["R01", "own", "cow"]), "condition: owns the cow")
	check(not Ranch.cond(["R01", "own", "pig"]), "condition: no pig")
	check(Game.eval_cond(["ranch:R01:own:cow"]), "eval_cond hook")
	eq(Ranch.ready_count("R01", "cow"), 0, "nothing on the first morning")
	_at(1, 480.0)
	eq(Ranch.ready_count("R01", "cow"), 1, "one milk after a day")
	check(Game.eval_cond(["ranch:R01:ready"]), "crate ready condition")
	_at(9, 480.0)
	eq(Ranch.ready_count("R01", "cow"), 3, "capped at three")
	var got = Ranch.collect("R01")
	eq(got, [["RK01", 3]], "crate hands over the milk")
	eq(Game.count("RK01"), 3, "milk in the bag")
	eq(Ranch.ready_count("R01", "cow"), 0, "crate empty")
	_at(9, 1200.0)
	eq(Ranch.ready_count("R01", "cow"), 0, "a full crate wasted the extra days")
	_at(10, 480.0)
	eq(Ranch.ready_count("R01", "cow"), 1, "counting restarted at collection")
	eq(Game.stat("ranch_animals"), 1, "counter: animals")
	eq(Game.stat("ranch_herds"), 1, "counter: ranches with livestock")

func test_partial_collect_keeps_remainder() -> void:
	fresh_game()
	_at(0, 0.0)
	Game.S["inventory"]["gold"] = 5000
	Ranch.buy("R01", "dove")
	_at(1, 720.0)          # 1.5 days: one egg, half a day banked
	eq(Ranch.collect("R01"), [["RK02", 1]], "one egg")
	_at(2, 0.0)            # half a day later the second egg is due
	eq(Ranch.ready_count("R01", "dove"), 1, "remainder of the period carried over")

func test_no_gold_no_beast() -> void:
	fresh_game()
	Game.S["inventory"]["gold"] = 10
	eq(Ranch.buy("R03", "cow"), "gold", "too poor")
	check(not Ranch.owns("R03", "cow"), "nothing bought")
	eq(Game.gold(), 10, "no crowns taken")

func test_plots_plant_grow_harvest() -> void:
	fresh_game()
	_at(3, 600.0)
	check(not Ranch.plant("R01", 1, "RS02"), "no seed, no planting")
	Game.add_item("RS02", 2)
	check(Ranch.plant("R01", 1, "RS02"), "carrot planted")
	eq(Game.count("RS02"), 1, "one seed used")
	check(not Ranch.plant("R01", 1, "RS02"), "plot already taken")
	check(not Ranch.plant("R01", 9, "RS02"), "no such plot")
	check(not Ranch.plot_ready("R01", 1), "not ripe yet")
	eq(Ranch.harvest("R01", 1), [], "cannot pull it green")
	check(Ranch.plot_left("R01", 1) > 0.0, "time left reported")
	_at(4, 600.0)
	check(Ranch.plot_ready("R01", 1), "ripe after a day")
	var h = Ranch.harvest("R01", 1)
	eq(h, ["RV02", 3], "three carrots")
	eq(Game.count("RV02"), 3, "carrots in the bag")
	check(Ranch.plot("R01", 1).is_empty(), "plot empty again")
	eq(Game.stat("ranch_harvests"), 1, "counter: harvests")
	# a seed bought at one ranch grows at another
	check(Ranch.plant("R09", 2, "RS02"), "seed travels")

func test_old_save_without_ranch() -> void:
	fresh_game()
	Game.S.erase("ranch")
	check(not Ranch.owns("R01", "cow"), "no state reads as nothing owned")
	eq(Ranch.ready_total("R01"), 0, "no goods")
	eq(Ranch.record_rows().size(), 8, "records still list every ranch")
	Game.S["inventory"]["gold"] = 5000
	eq(Ranch.buy("R02", "pig"), "ok", "state created on demand")
	check(typeof(Game.S.get("ranch")) == TYPE_DICTIONARY, "ranch state created")

func test_clock_running_backwards_is_harmless() -> void:
	fresh_game()
	_at(5, 0.0)
	Game.S["inventory"]["gold"] = 5000
	Ranch.buy("R04", "bunny")
	_at(2, 0.0)
	eq(Ranch.ready_count("R04", "bunny"), 0, "no negative production")

func test_records_lines() -> void:
	fresh_game()
	Game.S["inventory"]["gold"] = 5000
	Ranch.buy("R07", "dove")
	var lines = Ranch.record_lines("R07")
	check(lines.size() >= 8, "info panel lines")
	eq(str(lines[0][0]), "Maple Gate Farm", "ranch name first")
	var rows = Ranch.record_rows()
	var r7 = rows.filter(func(r): return r["value"] == "R07")[0]
	eq(str(r7["right"]), "1/3", "owned count in the list")
