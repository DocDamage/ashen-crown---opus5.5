extends TestCase
## Ranching (meta/ranch.gd), the Super Retro Ranch rules: tools, hoe / plant / water / grow / harvest on map cells,
## rain, hazards, beasts (affection, pigs growing up, doves laying and hatching, foxes, mice), the rail kart, old saves.

func _at(day: int, clock: float) -> void:
	Game.S["day"] = day
	Game.S["clock"] = clock

func _cell(rid: String, i: int = 0) -> Vector2i:
	return Ranch.plot_cells(str(Ranch.info(rid)["map"]))[i]

## The first slot >= from where `pred` holds for the ranch's weather.
func _slot_where(rid: String, from: int, pred: Callable) -> int:
	for s in range(from, from + 4000):
		if pred.call(Ranch.weather_at_slot(str(Ranch.info(rid)["region"]), s), s):
			return s
	return -1

func _to_slot(s: int, mins: float = 1.0) -> void:
	_at(s / 4, float(s % 4) * 360.0 + mins)

func test_ranch_content() -> void:
	var d = Ranch.data()
	eq(Ranch.order().size(), 8, "eight ranches")
	eq(d["crops"].size(), 19, "all nineteen of the pack's crops")
	for cid in d["crops"]:
		var c = d["crops"][cid]
		check(c["stages"].size() >= 5 and int(c["stages"][0]) == 0, "%s grows through its strip from frame 0" % cid)
		check(Content.data["items"].has(str(c["item"])) and Content.data["items"].has(str(c["seed"])), "%s crop and seed items" % cid)
	for rid in Ranch.order():
		var r = Ranch.info(rid)
		check(Content.data["maps"].has(str(r["map"])), "%s map %s exists" % [rid, r["map"]])
		check(Content.data["shops"].has(str(r["shop"])), "%s seed box exists" % rid)
		check(Ranch.plot_cells(str(r["map"])).size() >= 8, "%s has dirt beds" % rid)
		check(Ranch.rid_of(str(r["map"])) == rid, "%s map knows its ranch" % rid)
		for c in r["seeds"]:
			check(Content.data["items"].has(str(Ranch.crop(c)["seed"])), "%s seed item for %s" % [rid, c])
	for t in ["RT01", "RT02", "RT03"]:
		eq(Content.item(t).get("kind", ""), "key", "%s is a lent key item" % t)
	for iid in ["RK01", "RK02", "RK03", "RK04", "RF01", "RA01"]:
		check(Content.item(iid).get("sellable", false), "%s sells" % iid)
	var cooked = 0
	for rc in Content.data["gear2"]["recipes"].values():
		if str(rc["result"]).begins_with("RF") or str(rc["result"]) == "RA01":
			cooked += 1
	check(cooked >= 7, "cooking recipes registered (%d)" % cooked)

func test_hoe_plant_water_grow_harvest() -> void:
	fresh_game()
	# Brinewell (Pale Basin) never rains, so only the can waters
	var rid = "R05"
	_at(0, 400.0)
	var c = _cell(rid)
	check(Ranch.till(rid, c), "hoed")
	check(not Ranch.till(rid, c), "already hoed")
	check(not Ranch.plant(rid, c, "RS13"), "no seed in the bag")
	Game.add_item("RS13", 2)
	check(Ranch.plant(rid, c, "RS13"), "planted eggplant")
	eq(Game.count("RS13"), 1, "one seed used")
	var p: Dictionary = Ranch.state(rid)["plots"][Ranch.key_of(c)]
	eq(p["c"], "eggplant", "crop on the bed")
	_at(0, 1400.0)
	Ranch.tick(rid)
	eq(int(p["g"]), 0, "a dry crop stalls")
	check(Ranch.water(rid, c), "watered")
	check(Ranch.is_wet(rid, p), "the bed is wet")
	_at(1, 360.0 * 3 + 30.0)          # four quarter-day turns later
	Ranch.tick(rid)
	var last = Ranch.crop("eggplant")["stages"].size() - 1
	eq(int(p["g"]), mini(4, last), "one stage per watered quarter day")
	check(Ranch.is_ripe(p), "eggplant ripe after four stages")
	var h = Ranch.harvest(rid, c)
	eq(h, ["RV13", 3], "the sickle takes the crop")
	eq(Game.count("RV13"), 3, "eggplants in the bag")
	check(Ranch.state(rid)["plots"].has(Ranch.key_of(c)), "the bed stays hoed")
	eq(str(Ranch.state(rid)["plots"][Ranch.key_of(c)]["c"]), "", "and empty")
	eq(Ranch.harvest(rid, c), [], "nothing to cut on an empty bed")
	eq(Game.stat("ranch_harvests"), 1, "counter: harvests")

func test_rain_waters_every_bed() -> void:
	fresh_game()
	var rid = "R01"
	var s = _slot_where(rid, 8, func(w, _s): return w == "rain")
	check(s > 0, "it rains in the Crown March some time")
	_to_slot(s - 1, 10.0)
	var c = _cell(rid)
	Ranch.till(rid, c)
	Game.add_item("RS02", 1)
	Ranch.plant(rid, c, "RS02")
	var p: Dictionary = Ranch.state(rid)["plots"][Ranch.key_of(c)]
	_to_slot(s, 10.0)
	Ranch.tick(rid)
	check(int(p["g"]) >= 1, "the rain grew an unwatered carrot")
	check(Ranch.is_wet(rid, p), "and the bed is wet")

func test_frost_and_embers() -> void:
	fresh_game()
	var rid = "R09"
	var s = _slot_where(rid, 8, func(w, sl): return w == "snow" and sl % 4 == 0)
	check(s > 0, "snowy nights at Rimeholt")
	_to_slot(s - 1, 10.0)
	var c = _cell(rid)
	Ranch.till(rid, c)
	Game.add_item("RS03", 1)
	Ranch.plant(rid, c, "RS03")
	var p: Dictionary = Ranch.state(rid)["plots"][Ranch.key_of(c)]
	p["g"] = 3
	_to_slot(s, 10.0)
	Ranch.tick(rid)
	eq(int(p["g"]), 2, "a snowy night takes a stage off a growing crop")
	eq(int(p["fz"]), s, "frost marked (corn shows its frozen strip)")
	# ember storms at Cinderwake scorch only dry beds, and never below the first stage
	fresh_game()
	rid = "R02"
	_at(0, 10.0)
	c = _cell(rid)
	Ranch.till(rid, c)
	Game.add_item("RS05", 1)
	Ranch.plant(rid, c, "RS05")
	p = Ranch.state(rid)["plots"][Ranch.key_of(c)]
	p["g"] = 1
	_at(6, 10.0)
	Ranch.tick(rid)
	eq(int(p["g"]), 1, "a dry onion stays at its first stage under the ash")

func test_beasts_affection_and_goods() -> void:
	fresh_game()
	_at(0, 480.0)
	Game.add_gold(20000)
	eq(Ranch.can_buy("R01", "cow"), "ok", "a cow for sale")
	eq(Ranch.buy("R01", "cow"), "ok", "bought")
	eq(Ranch.buy("R01", "cow"), "owned", "once per ranch")
	check(Game.eval_cond(["ranch:R01:own:cow"]), "condition hook")
	eq(Ranch.ready_good("R01", "cow"), 0, "no milk on the day she comes")
	Ranch.tend("R01", "cow")
	eq(Ranch.aff("R01", "cow"), 1, "petting raises affection")
	Ranch.tend("R01", "cow")
	eq(Ranch.aff("R01", "cow"), 1, "once a day")
	_at(1, 480.0)
	eq(Ranch.ready_good("R01", "cow"), 1, "milk the next day")
	Ranch.tend("R01", "cow")
	eq(Game.count("RK01"), 1, "milk taken while petting")
	eq(Ranch.ready_good("R01", "cow"), 0, "milked today")
	Ranch.state("R01")["animals"]["cow"]["aff"] = 6
	_at(2, 480.0)
	eq(Ranch.ready_good("R01", "cow"), 2, "a fond cow gives double")
	# piglets grow up, then root up truffles every second day
	eq(Ranch.buy("R01", "pig"), "ok", "piglet bought")
	check(not Ranch.pig_grown("R01"), "a piglet")
	eq(Ranch.ready_good("R01", "pig"), 0, "piglets root up nothing")
	_at(5, 480.0)
	check(Ranch.pig_grown("R01"), "grown after three days")
	eq(Ranch.ready_good("R01", "pig"), 1, "the first truffle")
	# neglect costs affection
	_at(10, 480.0)
	Ranch.tick("R01")
	check(Ranch.aff("R01", "cow") < 6, "unpetted for days, she cools")

func test_doves_lay_hatch_and_foxes() -> void:
	fresh_game()
	Game.add_gold(20000)
	_at(0, 480.0)
	var rid = "R07"
	Ranch.tick(rid)
	Ranch.buy(rid, "bird")
	eq(Ranch.birds(rid), 2, "a pair of doves")
	check(Game.eval_cond(["ranch:R07:birds:2"]) and not Game.eval_cond(["ranch:R07:birds:3"]), "dove count conditions")
	_at(1, 480.0)
	Ranch.tick(rid)
	eq(Ranch.eggs(rid), 2, "each dove lays in the night")
	var msg = Ranch.nest_take(rid)
	check(msg.begins_with("Dove Egg x2"), "eggs from the nest: " + msg)
	eq(Ranch.eggs(rid), 0, "nest empty")
	# eggs left alone hatch into a third dove
	_at(5, 480.0)
	Ranch.tick(rid)
	eq(Ranch.birds(rid), 3, "an egg left three days hatched")
	# the pen gate left open at night lets the fox at the nest
	check(Ranch.eggs(rid) > 0, "eggs waiting")
	Ranch.state(rid)["gate"] = true
	check(Game.eval_cond(["ranch:R07:gate"]), "gate condition")
	_at(6, 200.0)
	Ranch.tick(rid)
	eq(Ranch.eggs(rid), 0, "the fox took them in the night")
	eq(int(Ranch.state(rid)["fox"]), 6, "fox night recorded")

func test_mice_and_the_cat() -> void:
	fresh_game()
	var rid = "R08"
	var c = _cell(rid)
	Ranch.till(rid, c)
	Ranch.state(rid)["plots"][Ranch.key_of(c)] = {"c": "berry", "g": 5, "w": -1}
	var st = Ranch.state(rid)
	var s = -1
	for k in range(4, 4000, 4):
		if Ranch._roll(rid, k, "mice") < 0.35:
			s = k
			break
	check(s > 0, "a mouse night exists")
	Ranch._day(rid, st, s / 4, s)
	eq(int(st["plots"][Ranch.key_of(c)]["g"]), 4, "no cat: mice nibbled the ripe berries")
	st["plots"][Ranch.key_of(c)]["g"] = 5
	st["animals"]["cat"] = {"t": 0.0, "d": 0, "aff": 0, "pet": -1, "got": 0}
	Ranch._day(rid, st, s / 4, s)
	eq(int(st["plots"][Ranch.key_of(c)]["g"]), 5, "the cat keeps them off")
	eq(int(st["caught"]), s / 4, "and leaves the catch on the step")

func test_kart_ships_and_pays_next_morning() -> void:
	fresh_game()
	_at(3, 900.0)
	var rid = "R03"
	Game.add_item("RV08", 10)
	Game.add_item("RK01", 2)
	check(Ranch.shippable().has("RV08"), "radishes ship")
	check(Ranch.kart_load(rid, "RV08", 10) and Ranch.kart_load(rid, "RK01", 2), "loaded")
	eq(Game.count("RV08"), 0, "out of the bag")
	var v = Ranch.kart_value(rid)
	eq(v, int(round((34 / 2 * 10 + 40 / 2 * 2) * 1.1)), "sell value plus the line's bonus")
	var g0 = Game.gold()
	check(Ranch.kart_send(rid), "sent")
	check(Ranch.kart_away(rid) and not Ranch.kart_back(rid), "down the line")
	eq(Ranch.kart_collect(rid), 0, "nothing the same day")
	_at(4, 300.0)
	check(not Ranch.kart_back(rid), "not before morning")
	_at(4, 400.0)
	check(Ranch.kart_back(rid), "back in the morning")
	eq(Ranch.kart_collect(rid), v, "coins in the chest")
	eq(Game.gold(), g0 + v, "paid")
	check(not Ranch.kart_away(rid) and not Ranch.kart_back(rid), "ready again")
	eq(Game.stat("ranch_kart"), 1, "counter: kart trips")

func test_lend_tools_condition() -> void:
	fresh_game()
	check(not Game.eval_cond(["ranch:R01:tools"]), "no tools yet")
	Ranch.state("R01")["tools"] = true
	check(Game.eval_cond(["ranch:R01:tools"]), "lent")

func test_old_first_pass_save_migrates() -> void:
	fresh_game()
	_at(4, 600.0)
	Game.S["ranch"] = {"R01": {"animals": {"cow": {"t": 0.0}, "dove": {"t": 100.0}}, "plots": {"1": {"crop": "carrot", "t": 50.0}}}}
	var seeds = Game.count("RS02")
	var st = Ranch.state("R01")
	eq(int(st["v"]), 2, "migrated")
	check(Ranch.owns("R01", "cow") and Ranch.owns("R01", "bird"), "the cow stays; doves become the dove kind")
	check(not Ranch.owns("R01", "dove"), "no old kind left")
	eq(Game.count("RS02"), seeds + 1, "the old plot's seed came back")
	check(st["plots"].is_empty(), "no numbered plots left")
	check(bool(st["tools"]), "an old rancher's customer keeps the tools")
	Ranch.state("R01")
	eq(Game.count("RS02"), seeds + 1, "migration runs once")
	# and saves with no ranch key at all
	fresh_game()
	Game.S.erase("ranch")
	eq(Ranch.peek("R01"), {}, "peek on a save without ranching")
	check(not Game.eval_cond(["ranch:R01:any"]), "conditions are false")
	Game.add_gold(5000)
	eq(Ranch.buy("R01", "cow"), "ok", "buying creates the state")

func test_clock_running_backwards_is_harmless() -> void:
	fresh_game()
	_at(5, 600.0)
	var c = _cell("R05")
	Ranch.till("R05", c)
	Game.add_item("RS13", 1)
	Ranch.plant("R05", c, "RS13")
	Ranch.tick("R05")
	_at(2, 100.0)
	Ranch.tick("R05")
	eq(int(Ranch.state("R05")["plots"][Ranch.key_of(c)]["g"]), 0, "no growth from a clock set back")
	eq(int(Ranch.state("R05")["u"]), Ranch.slot_now(), "the ranch clock follows")
