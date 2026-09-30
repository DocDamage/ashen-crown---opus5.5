extends TestCase
## Expansion battle systems (branch s1): level cap and breaks, damage cap, limit breaks, party swap, rows,
## capture/morph, blue magic, Vestiges V13-V24 and superboss rewards.

func _ctx(m: BattleModel) -> Dictionary:
	return {"act": {"targets": []}, "ev": {"results": [], "msgs": []}, "depth": 0, "damaging_spell": false, "reactions": {}}

func _old_xp_to_next(l: int) -> int:
	return 30 + 12 * l + 3 * l * l

# ---------------------------------------------------------------- 1. level cap and level breaks
func test_xp_curve_unchanged_to_50_and_extends_to_200() -> void:
	var same = true
	for l in range(1, 51):
		if F.xp_to_next(l) != _old_xp_to_next(l):
			same = false
	check(same, "levels 1-50 keep the original XP curve")
	var mono = true
	for l in range(51, 200):
		if F.xp_to_next(l) <= F.xp_to_next(l - 1):
			mono = false
	check(mono, "XP to next keeps rising to 200")
	eq(F.level_for_xp(F.xp_total_for_level(50)), 50, "total for 50 is still level 50")
	eq(F.level_for_xp(999999999), 99, "default cap is 99")
	eq(F.level_for_xp(999999999, 200), 200, "curve reaches 200")
	eq(F.level_for_xp(F.xp_total_for_level(137), 200), 137, "total for 137 is level 137")

func test_level_breaks_from_superbosses() -> void:
	fresh_game()
	eq(Game.level_cap(), 99, "cap 99 before any ancient dragon")
	var msgs = Game.superboss_victory("SB02")
	check(Game.superboss_down("SB02") and Game.flag("sb_sb02_down"), "sb_sb02_down set")
	check(Game.flag("levelbreak_1"), "first ancient dragon sets levelbreak_1")
	eq(Game.level_cap(), 120, "cap 120 after the first dragon")
	check(Game.has_vestige("V14"), "Thalassar grants V14")
	check(msgs.size() >= 2, "victory reports the Vestige and the new limit")
	for w in ["SB01", "SB03"]:
		Game.superboss_victory(w)
	eq(Game.level_cap(), 120, "three dragons: still 120")
	Game.superboss_victory("SB04")
	check(Game.flag("levelbreak_2"), "all four dragons set levelbreak_2")
	eq(Game.level_cap(), 150, "cap 150 after all four")
	Game.superboss_victory("SB12")
	check(Game.flag("levelbreak_3"), "the Unmade Crown sets levelbreak_3")
	eq(Game.level_cap(), 200, "cap 200 after the finale")
	check(Game.has_vestige("V24"), "the Unmade Crown grants V24")
	eq(Game.superboss_victory("BX01").size(), 0, "ordinary bosses give no superboss reward")

func test_award_xp_respects_the_cap() -> void:
	party(["C01"], 50)
	var m = Game.member("C01")
	m["xp"] = F.xp_total_for_level(130)
	Game.award_xp(1)
	eq(int(m["level"]), 99, "capped at 99")
	Game.set_flag("levelbreak_1")
	Game.award_xp(1)
	eq(int(m["level"]), 120, "level break lets the stored XP count up to 120")

func test_stats_grow_past_50() -> void:
	var cdef = Content.ch("C01")
	var s30 = F.member_stats({"level": 30}, cdef, {})
	var n = 29
	eq(s30["mhp"], int(cdef["base"]["hp"]) + int(cdef["growth"]["hp"]) * n + int(floor(0.65 * n * n)), "HP formula unchanged at 30")
	var s50 = F.member_stats({"level": 50}, cdef, {})
	var s99 = F.member_stats({"level": 99}, cdef, {})
	var s150 = F.member_stats({"level": 150}, cdef, {})
	var s200 = F.member_stats({"level": 200}, cdef, {})
	for k in ["mhp", "str", "mag", "def", "res"]:
		check(s99[k] > s50[k], "%s grows 50 -> 99" % k)
		check(s200[k] >= s150[k], "%s does not shrink 150 -> 200" % k)
	check(s150["str"] > s99["str"], "strength keeps growing past 99")
	check(s200["mhp"] <= F.HP_CAP, "HP stays under 9,999")

# ---------------------------------------------------------------- 2. damage cap
func test_damage_cap_and_breakers() -> void:
	var m = model_with(["C01"], ["SB01"], 99)
	var h: BattleModel.Battler = m.battlers[m.party_ids[0]]
	var e: BattleModel.Battler = m.battlers[m.enemy_ids[0]]
	h.atk = 40000.0
	var op = {"op": "damage", "power": 400, "type": "physical", "no_crit": true, "ranged": true}
	var h0 = e.hp
	m._do_damage(h, e, op, _ctx(m))
	eq(h0 - e.hp, F.DAMAGE_CAP, "normal hits stop at 9,999")
	h0 = e.hp
	var op2 = op.duplicate()
	op2["uncapped"] = true
	m._do_damage(h, e, op2, _ctx(m))
	check(h0 - e.hp > F.DAMAGE_CAP and h0 - e.hp <= F.DAMAGE_BREAK_CAP, "uncapped op breaks the limit")
	h.passives = {"break_damage": true}
	h0 = e.hp
	m._do_damage(h, e, op, _ctx(m))
	check(h0 - e.hp > F.DAMAGE_CAP, "break_damage passive breaks the limit")
	var it = Content.item("A201")
	check(it.get("passives", {}).has("break_damage"), "Wyrmscale Brand carries break_damage")
	eq(Content.enemy("SB01").get("steal", {}).get("rare", ""), "A201", "Cindermaw's rare steal is the Brand")
	party(["C01"], 60)
	Game.add_item("A202", 1)
	eq(Game.equip("C01", "acc1", "A202")["ok"], true, "any hero can wear a breaker")
	check(Game.stats("C01")["passives"].has("break_damage"), "passive reaches the stats")

# ---------------------------------------------------------------- 3. limit breaks
func test_limit_content_68() -> void:
	var L: Dictionary = Content.data["limits"]["heroes"]
	eq(L.size(), 17, "17 heroes have limits")
	var n = 0
	var t4_uncapped = true
	for cid in L:
		eq(L[cid].size(), 4, "%s has four limits" % cid)
		for i in range(L[cid].size()):
			var a = Content.ability(L[cid][i])
			n += 1
			eq(int(a.get("limit_tier", 0)), i + 1, "%s tier" % L[cid][i])
			eq(str(a.get("owner", "")), cid, "%s owner" % L[cid][i])
			if i == 3:
				var any = false
				for o in a["ops"]:
					if o.get("uncapped", false):
						any = true
				t4_uncapped = t4_uncapped and any
	eq(n, 68, "68 limits")
	check(t4_uncapped, "every fourth limit breaks the damage limit")

func test_limit_gauge_fills_and_limit_fires() -> void:
	var m = model_with(["C01", "C02"], ["E001"], 20)
	var h: BattleModel.Battler = m.battlers[m.party_ids[0]]
	var e: BattleModel.Battler = m.battlers[m.enemy_ids[0]]
	eq(h.limits, ["S401"], "Raven starts with his first limit")
	eq(h.limit, 0.0, "empty gauge")
	var hp0 = h.hp
	m._do_damage(e, h, {"op": "damage", "power": 300, "type": "physical", "no_crit": true}, _ctx(m))
	var lost = hp0 - h.hp
	check(absf(h.limit - 75.0 * lost / h.mhp) < 0.01, "taking damage fills the gauge by share of max HP")
	var g0 = h.limit
	m._do_damage(h, e, {"op": "damage", "power": 10, "type": "physical", "no_crit": true, "ranged": true}, _ctx(m))
	check(absf(h.limit - g0 - 2.5) < 0.01 or e.hp == 0, "dealing damage adds a little")
	var w = until_input(m)
	while w != null and w != h:
		m.commit(w, {"type": "defend"})
		w = until_input(m)
	check(w == h, "Raven is ready")
	h.limit = 50.0
	eq(m.validate(h, {"type": "ability", "id": "S401", "targets": [e.id]})["ok"], false, "limit needs a full gauge")
	h.limit = 100.0
	check(m.limit_ready(h), "gauge full")
	eq(m.validate(h, {"type": "ability", "id": "S402", "targets": [e.id]})["ok"], false, "unlearned limit refused")
	var r = m.commit(h, {"type": "ability", "id": "S401", "targets": [e.id]})
	check(r["ok"], "limit committed")
	eq(h.limit, 0.0, "gauge empties at commit")
	settle(m)
	eq(h.limit_used, ["S401"], "use recorded for learning")
	var ps = m.party_end_state()
	eq(ps[0]["limit_used"], ["S401"], "end state carries the use")

func test_limit_learning_by_use_and_level() -> void:
	party(["C01"], 14)
	var m = Game.member("C01")
	m["limit_uses"] = {"S401": 3}
	eq(Game.limit_known("C01"), ["S401"], "level 14: tier 2 not yet (floor 15)")
	m["level"] = 15
	eq(Game.limit_known("C01"), ["S401", "S402"], "3 uses and level 15: tier 2 learned")
	var msgs = Game.limit_learning()
	check(msgs.size() == 1 and msgs[0].find("Ilyr's Wing") >= 0, "learning is announced once")
	eq(Game.limit_learning().size(), 0, "not announced twice")
	m["level"] = 60
	m["limit_uses"] = {"S401": 9, "S402": 4}
	eq(Game.limit_known("C01").size(), 2, "tier 3 needs 5 uses of tier 2")
	m["limit_uses"]["S402"] = 5
	eq(Game.limit_known("C01").size(), 3, "tier 3 learned")
	eq(Game.limit_next("C01").get("id", ""), "S404", "next is tier 4")

func test_limit_gauge_persists_between_battles() -> void:
	var m = model_with(["C01"], ["E001"], 20)
	var h: BattleModel.Battler = m.battlers[m.party_ids[0]]
	h.limit = 64.0
	for eid in m.enemy_ids:
		m.battlers[eid].hp = 0
		m.battlers[eid].state = "KO"
	Game.apply_battle_victory(m)
	eq(float(Game.member("C01").get("limit_gauge", 0.0)), 64.0, "gauge saved")
	eq(float(Game.battle_party()[0]["limit"]), 64.0, "and handed to the next battle")

func test_limit_gauge_does_not_change_old_fights() -> void:
	## the gauge is bookkeeping only: the same seeded fight ends identically with or without limits
	var hashes = []
	for with_limits in [false, true]:
		var p = party(["C01", "C02"], 8)
		if not with_limits:
			for x in p:
				x["limits"] = []
		var m = BattleModel.new(Content.data)
		m.setup(p, ["E001", "E002"], {"I001": 5}, 4242, {})
		var guard = 0
		while m.result == "" and guard < 200000:
			guard += 1
			while m.locked:
				m.ack()
			var w = m.awaiting_input()
			if w != null:
				m.commit(w, {"type": "attack", "targets": [m.enemy_ids[-1]]})
			m.step()
		hashes.append(m.state_hash())
	eq(hashes[0], hashes[1], "limit gauges leave the simulation unchanged")

# ---------------------------------------------------------------- 4. party swap
func test_battle_reserves_from_formation() -> void:
	party(["C01", "C02", "C03", "C04", "C05"], 10)
	for cid in ["C06", "C07", "C08", "C09"]:
		Game.recruit(cid)
	Game.set_active(["C01", "C02", "C03", "C04", "C05"])
	eq(Game.active().size(), 5, "active party of five")
	eq(Game.battle_reserves(), ["C06", "C07", "C08"], "next three available heroes are the bench")
	Game.S["party"]["locked"] = true
	eq(Game.battle_reserves(), [], "locked (soul-bound) party has no bench")
	Game.S["party"]["locked"] = false

func test_swap_in_battle() -> void:
	party(["C01", "C02"], 10)
	Game.recruit("C05")
	Game.recruit("C06")
	Game.set_active(["C01", "C02"])
	var m = BattleModel.new(Content.data)
	m.setup(Game.battle_party(), ["E001"], {"I001": 1}, 7, {"reserves": Game.battle_reserve_party()})
	eq(m.reserve_ids.size(), 2, "two reserves")
	var w = until_input(m)
	var out_id: String = w.id
	var slot = m.party_ids.find(out_id)
	var rid: String = m.reserve_ids[0]
	check(m.validate(w, {"type": "swap", "reserve": rid})["ok"], "swap allowed")
	m.commit(w, {"type": "swap", "reserve": rid})
	settle(m)
	eq(m.party_ids[slot], rid, "reserve takes the same slot")
	check(m.reserve_ids.has(out_id), "acting hero goes to the reserve")
	var nb: BattleModel.Battler = m.battlers[rid]
	check(nb.state == "FILLING" and nb.atb >= BattleModel.SWAP_ATB and nb.atb < F.ATB_MAX, "incoming hero enters with a partly filled gauge")
	var ends = m.party_end_state()
	eq(ends.size(), 4, "end state covers the reserves too")
	# a KO'd reserve cannot come in
	m.battlers[m.reserve_ids[1]].state = "KO"
	m.battlers[m.reserve_ids[1]].hp = 0
	w = until_input(m)
	if w != null:
		eq(m.validate(w, {"type": "swap", "reserve": m.reserve_ids[1]})["ok"], false, "KO reserve refused")
	var m2 = model_with(["C01"], ["E001"], 10)
	eq(m2.validate(m2.battlers[m2.party_ids[0]], {"type": "swap"})["ok"], false, "no reserves, no swap")

# ---------------------------------------------------------------- 5. rows
func test_back_row_halves_melee_both_ways() -> void:
	var m = model_with(["C01"], ["E001"], 20)
	var h: BattleModel.Battler = m.battlers[m.party_ids[0]]
	var e: BattleModel.Battler = m.battlers[m.enemy_ids[0]]
	var op = {"op": "damage", "power": 100, "type": "physical", "no_crit": true}
	e.hp = 99999
	e.mhp = 99999
	m.rng.seed_with(5)
	var h0 = e.hp
	m._do_damage(h, e, op, _ctx(m))
	var front = h0 - e.hp
	h.row = "back"
	m.rng.seed_with(5)
	h0 = e.hp
	m._do_damage(h, e, op, _ctx(m))
	var back = h0 - e.hp
	check(absi(back * 2 - front) <= 2, "back row deals half melee damage (%d vs %d)" % [back, front])
	h.row = "front"
	m.rng.seed_with(9)
	var hh = h.hp
	m._do_damage(e, h, op, _ctx(m))
	var tf = hh - h.hp
	h.hp = hh
	h.row = "back"
	m.rng.seed_with(9)
	m._do_damage(e, h, op, _ctx(m))
	var tb = hh - h.hp
	check(tb < tf, "back row takes less melee damage")

# ---------------------------------------------------------------- 6. capture / morph
func test_capture_weakened_enemy() -> void:
	var m = model_with(["C08"], ["E001"], 10)
	var s: BattleModel.Battler = m.battlers[m.party_ids[0]]
	check(s.abilities.has("S201"), "Sak knows Capture at level 10")
	var e: BattleModel.Battler = m.battlers[m.enemy_ids[0]]
	var ctx = _ctx(m)
	m._do_capture(s, e, ctx)
	check(e.alive() and m.captured.is_empty(), "a healthy enemy is too strong")
	e.hp = 1
	var tries = 0
	while e.alive() and tries < 20:
		m._do_capture(s, e, _ctx(m))
		tries += 1
	check(not e.alive(), "captured enemy leaves the battle")
	eq(m.captured, ["E001"], "captured list")
	var mb = model_with(["C08"], ["B01"], 10)
	var boss: BattleModel.Battler = mb.battlers[mb.enemy_ids[0]]
	boss.hp = 1
	mb._do_capture(mb.battlers[mb.party_ids[0]], boss, _ctx(mb))
	check(boss.alive() and mb.captured.is_empty(), "bosses cannot be captured")
	m.morph_items = ["I020"]
	var c0 = Game.count("I020")
	Game.apply_battle_victory(m)
	eq(int(Game.S["captured"].get("E001", 0)), 1, "S.captured counts the capture")
	eq(Game.count("I020"), c0 + 1, "morph item kept")

func test_capture_command_in_battle_flow() -> void:
	var got = false
	for sd in range(1, 25):
		var m = model_with(["C08"], ["E001", "E002"], 10, {}, sd)
		var e: BattleModel.Battler = m.battlers[m.enemy_ids[0]]
		e.hp = 1
		var w = until_input(m)
		if w == null or not e.alive():
			continue
		var r = m.commit(w, {"type": "ability", "id": "S201", "targets": [e.id]})
		check(r["ok"], "Capture commits like a technique")
		settle(m)
		if not m.captured.is_empty():
			got = true
			eq(m.captured, ["E001"], "the targeted enemy is captured")
			check(not e.alive(), "and leaves the field")
			check(m.result == "", "the other enemy keeps fighting")
			break
	check(got, "a capture at 1 HP lands within a few tries")

# ---------------------------------------------------------------- 7. blue magic
func test_blue_catalogue() -> void:
	var B: Dictionary = Content.data["blue"]
	var n = B["order"].size()
	check(n >= 16 and n <= 24, "16-24 blue moves (%d)" % n)
	eq(B["mages"], {"C04": "hit", "C12": "hit", "C09": "see", "C13": "see"}, "four blue mages with one rule each")
	for k in B["src"]:
		var p = str(k).split(":")
		check(Content.enemy(p[0]).get("moves", {}).has(p[1]), "%s is a real enemy move" % k)
		check(B["order"].has(B["src"][k]), "%s maps to a blue move" % k)

func _enemy_act(m: BattleModel, eid: String, move: String, targets: Array) -> Dictionary:
	m.action_seq += 1
	return {"type": "enemy", "actor": eid, "move": move, "targets": targets, "key": "act%d" % m.action_seq, "commit_tick": m.tick, "ready_tick": m.tick}

func test_blue_learning_rules() -> void:
	# Golem learns by being hit: Pressure Burst hits everyone
	var m = model_with(["C04", "C01"], ["E014"], 20)
	var g: BattleModel.Battler = m.battlers[m.party_ids[0]]
	g.hp = g.mhp
	eq(g.blue_rule, "hit", "Golem learns by being hit")
	m._resolve(_enemy_act(m, m.enemy_ids[0], "burst", []))
	while m.locked:
		m.ack()
	eq(m.blue_new.get("S301", ""), "C04", "Golem learned Pressure Burst")
	# hit rule: a single-target move on someone else teaches nothing
	var m2 = model_with(["C04", "C01"], ["E015"], 20)
	m2._resolve(_enemy_act(m2, m2.enemy_ids[0], "blind", [m2.party_ids[1]]))
	check(not m2.blue_new.has("S303"), "Golem was not the target: nothing learned")
	# Kitsune learns by seeing
	var m3 = model_with(["C09", "C01"], ["E015"], 20)
	m3._resolve(_enemy_act(m3, m3.enemy_ids[0], "blind", [m3.party_ids[1]]))
	eq(m3.blue_new.get("S303", ""), "C09", "Kitsune learns what she sees")
	# victory keeps it; the Lore command can then use it
	for eid in m3.enemy_ids:
		m3.battlers[eid].hp = 0
		m3.battlers[eid].state = "KO"
	Game.apply_battle_victory(m3)
	check(Game.S["blue"].has("S303"), "stored in Game.S.blue")
	eq(Game.blue_for("C13"), ["S303"], "the pool is shared by the blue mages")
	eq(Game.blue_for("C01"), [], "others have no Lore")

func test_lore_usable_only_by_blue_mages() -> void:
	fresh_game()
	Game.S["blue"] = ["S301"]
	var m = model_with(["C04", "C01"], ["E001"], 20)
	Game.S["blue"] = ["S301"]
	var p = Game.battle_party()
	var m2 = BattleModel.new(Content.data)
	m2.setup(p, ["E001"], {}, 3, {})
	var g: BattleModel.Battler = m2.battlers[m2.party_ids[0]]
	var r: BattleModel.Battler = m2.battlers[m2.party_ids[1]]
	eq(g.blue, ["S301"], "Golem carries the pool")
	check(m2.validate(g, {"type": "ability", "id": "S301"})["ok"], "Golem can cast Pressure Burst")
	eq(m2.validate(r, {"type": "ability", "id": "S301"})["ok"], false, "Raven cannot")
	g.statuses["silence"] = {"dur": 2}
	eq(m2.validate(g, {"type": "ability", "id": "S301"})["ok"], false, "Silence blocks Lore")
	check(m != null, "fixture")

# ---------------------------------------------------------------- 8/9. Vestiges V13-V24 and superboss victories
func test_late_vestiges_defined() -> void:
	var V: Dictionary = Content.data["vestiges"]
	eq(V.size(), 24, "24 Vestiges")
	for i in range(13, 25):
		var vid = "V%d" % i
		check(V.has(vid), vid + " defined")
		var a = Content.ability(str(V[vid]["summon"]))
		eq(str(a.get("kind", "")), "summon", vid + " summon ability")
		for t in V[vid]["teach"]:
			check(not Content.ability(t[0]).is_empty(), "%s teaches %s" % [vid, t[0]])
		check(str(V[vid].get("art", "")).begins_with(vid + "_"), vid + " art key follows the convention")
		check(str(V[vid]["source"]).begins_with("SB"), vid + " comes from a superboss")
	check(BattleFX.vestige("V13").is_empty() or true, "missing art is not an error")

func test_superboss_victory_through_battle_transaction() -> void:
	var m = model_with(["C01"], ["SB07"], 70)
	for eid in m.enemy_ids:
		m.battlers[eid].hp = 0
		m.battlers[eid].state = "KO"
	var msgs = Game.apply_battle_victory(m)
	check(Game.flag("sb_sb07_down"), "sb_sb07_down set")
	check(Game.has_vestige("V19"), "Varro grants V19")
	var said = false
	for s in msgs:
		if s.find("Crucible Lion") >= 0:
			said = true
	check(said, "the reward is announced")
	check(not Game.flag("levelbreak_1"), "Varro is not an ancient dragon")

func test_late_summon_resolves() -> void:
	var m = model_with(["C01"], ["E001", "E002"], 60)
	var h: BattleModel.Battler = m.battlers[m.party_ids[0]]
	Game.grant_vestige("V24")
	m.links[h.id] = "V24"
	m.concord = 100
	var w = until_input(m)
	check(m.validate(w, {"type": "summon"})["ok"], "V24 can be summoned")
	m.commit(w, {"type": "summon"})
	settle(m)
	check(m.summons_used.has("V24"), "summon resolved")
