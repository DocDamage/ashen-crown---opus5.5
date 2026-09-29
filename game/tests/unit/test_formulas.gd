extends TestCase

func test_xp_curve() -> void:
	eq(F.xp_to_next(1), 45, "L1->2 = 30+12+3")
	eq(F.xp_to_next(10), 30 + 120 + 300, "L10->11")
	eq(F.level_for_xp(0), 1, "0 xp is level 1")
	eq(F.level_for_xp(45), 2, "45 xp reaches level 2")
	eq(F.level_for_xp(F.xp_total_for_level(20)), 20, "total for 20 is level 20")
	eq(F.level_for_xp(99999999), F.LEVEL_CAP, "cap at 50")

func test_damage_formulas() -> void:
	eq(F.physical_raw(10, 1, 100), 23.0, "(2*10+3*1)*100/100")
	check(is_equal_approx(F.magical_raw(20, 5, 110), 60.5), "magical raw")
	eq(F.defense_mult(0), 1.0, "no defense")
	eq(F.defense_mult(100), 0.5, "100 def halves")
	eq(F.defense_mult(-5), 1.0, "negative defense clamps to 0")
	eq(F.heal_amount(20, 10, 100, 1000), int(floor((40.0 + 20.0) + 60.0)), "heal formula incl 6% max HP")

func test_reduction_cap() -> void:
	# Defend 0.5 x Barrier 0.75 x Feather 0.4 x phys_reduce 0.9 would be 0.135 -> capped at 0.2 (80%)
	eq(F.combine_reductions([0.5, 0.75, 0.4, 0.9]), 0.2, "total direct reduction capped at 80%")
	eq(F.combine_reductions([0.5]), 0.5, "single reduction")

func test_atb_rate() -> void:
	eq(F.atb_rate(10, 1.0, false, false, false), 150.0, "100+5*SPD")
	eq(F.atb_rate(10, 1.0, true, false, false), 187.5, "haste x1.25")
	eq(F.atb_rate(10, 1.0, false, true, false), 112.5, "slow x0.75")
	eq(F.atb_rate(10, 1.0, false, true, true), 135.0, "boss slow x0.90")
	eq(F.atb_rate(200, 1.0, false, false, false), 100.0 + 5.0 * 99, "SPD clamped to 99")

func test_join_level() -> void:
	eq(F.join_level(5, [10, 12, 14]), 11, "median 12 - 1")
	eq(F.join_level(20, [10, 12, 14]), 20, "never lowers a stored level")
	eq(F.join_level(3, []), 3, "no reference party")

func test_member_stats_growth() -> void:
	fresh_game()
	var m: Dictionary = Game.member("C01")
	m["level"] = 11
	var s = F.member_stats(m, Content.ch("C01"), Content.data["items"])
	# hp = 120 + 54*10 + floor(0.65*100) = 725 (+ gear has no hp)
	eq(s["mhp"], 120 + 540 + 65, "Dain HP growth at level 11")
	eq(s["mmp"], 12 + 30, "Dain MP growth")
	eq(s["spd"], 8 + 2, "SPD +1 per four levels")
	check(s["def"] >= 10 + 10, "DEF +1 per level plus gear")

func test_equipment_change_does_not_regrow() -> void:
	fresh_game()
	var before = Game.stats("C01")
	Game.add_item("W002", 1)
	Game.equip("C01", "weapon", "W002")
	Game.equip("C01", "weapon", "W001")
	var after = Game.stats("C01")
	eq(after["mhp"], before["mhp"], "equipment swaps never trigger level growth")
	eq(after["atk"], before["atk"], "same weapon, same attack")
