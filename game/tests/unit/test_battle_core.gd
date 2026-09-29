extends TestCase
## Battle contract tests (AC015-AC024, AC033, AC055) against the real BattleModel.

func _script_run(seed_value: int, ack_delay: int) -> String:
	## Same seed and public command stream; the presenter acknowledges events after ack_delay frames.
	var m = model_with(["C01", "C02"], ["E001", "E002"], 6, {}, seed_value)
	var pending = 0
	var guard = 0
	while m.result == "" and guard < 200000:
		guard += 1
		if m.locked:
			pending += 1
			if pending >= ack_delay:
				m.ack()
				pending = 0
			continue
		var w = m.awaiting_input()
		if w != null:
			if w.ref == "C02" and w.mp >= 4:
				m.commit(w, {"type": "ability", "id": "S009", "targets": [m.enemy_ids[0]]})
			else:
				m.commit(w, {"type": "attack", "targets": [m.enemy_ids[-1]]})
		m.step()
	return m.state_hash() + ":" + str(m.rewards())

func test_loot_rng_isolated() -> void:
	var m1 = model_with(["C01"], ["E001", "E002"], 6, {}, 4242)
	var r1 = str(m1.rewards())
	var m2 = model_with(["C01"], ["E001", "E002"], 6, {}, 4242)
	var r2 = str(m2.rewards())
	eq(r1, r2, "same seed gives the same loot rolls")

func test_fixed_step_determinism() -> void:
	var a = _script_run(4242, 1)
	var b = _script_run(4242, 7)
	var c = _script_run(4242, 30)
	eq(a, b, "same seed + commands, different presentation pacing -> same end state")
	eq(a, c, "long presentation lock does not alter simulation")
	check(_script_run(4243, 1) != a, "different seed changes outcome")

func test_wait_vs_active() -> void:
	var m = model_with(["C01"], ["E001"], 6, {}, 1, {"mode": "wait"})
	m.menu_open = true
	var t0 = m.tick
	for i in range(120):
		m.step()
	eq(m.tick, t0, "Wait: open command menu pauses simulation")
	var a = model_with(["C01"], ["E001"], 6, {}, 1, {"mode": "active"})
	a.menu_open = true
	var t1 = a.tick
	for i in range(120):
		if a.locked:
			a.ack()
		a.step()
	check(a.tick > t1, "Active: timers advance during selection")
	a.paused = true
	var t2 = a.tick
	for i in range(60):
		a.step()
	eq(a.tick, t2, "pause menu freezes Active mode too")

func test_mp_reservation() -> void:
	var m = model_with(["C02"], ["E001"], 6)
	var tess = until_input(m)
	var mp0 = tess.mp
	m.begin_select(tess)
	m.cancel_select(tess)
	eq(tess.mp, mp0, "cancelled selection consumes nothing")
	var r = m.commit(tess, {"type": "ability", "id": "S009", "targets": [m.enemy_ids[0]]})
	check(r["ok"], "commit ok")
	eq(tess.mp, mp0 - 4, "MP reserved at commit")
	settle(m)
	eq(tess.mp, mp0 - 4, "exactly one MP charge after resolution")

func test_item_reservation_last_phoenix() -> void:
	var m = model_with(["C01", "C02", "C06"], ["E001"], 8, {"I006": 1})
	var dain: BattleModel.Battler = m.battlers[m.party_ids[0]]
	dain.hp = 0
	dain.state = "KO"
	var t = m.battlers[m.party_ids[1]]
	var o = m.battlers[m.party_ids[2]]
	t.state = "READY"; o.state = "READY"
	var r1 = m.commit(t, {"type": "item", "id": "I006", "targets": [dain.id]})
	var r2 = m.commit(o, {"type": "item", "id": "I006", "targets": [dain.id]})
	check(r1["ok"], "first reservation ok")
	check(not r2["ok"], "second ally cannot reserve the same last leaf")
	eq(int(m.inventory["I006"]), 0, "no negative inventory")
	settle(m)
	check(dain.alive(), "revived once")
	eq(int(m.inventory["I006"]), 0, "still exactly zero leaves")

func test_fallen_target_retarget() -> void:
	var m = model_with(["C01"], ["E001", "E001"], 10)
	var d = until_input(m)
	var first: BattleModel.Battler = m.battlers[m.enemy_ids[0]]
	var second: BattleModel.Battler = m.battlers[m.enemy_ids[1]]
	m.commit(d, {"type": "attack", "targets": [first.id]})
	first.hp = 0
	first.state = "KO"
	var hp_before = second.hp
	settle(m)
	check(second.hp < hp_before or m.log.any(func(l): return l.has("retarget")), "offensive action retargets lowest living ID and logs it")

func test_revive_refund_when_no_fallen() -> void:
	var m = model_with(["C06", "C01"], ["E001"], 12)
	var ori = until_ready(m, m.party_ids[0])
	var o: BattleModel.Battler = m.battlers[m.party_ids[0]]
	var d: BattleModel.Battler = m.battlers[m.party_ids[1]]
	d.hp = 0; d.state = "KO"
	var mp0 = o.mp
	m.commit(o, {"type": "ability", "id": "S044", "targets": [d.id]})
	d.state = "FILLING"; d.hp = 10
	settle(m)
	eq(o.mp, mp0, "Last Light cancels with full refund when nobody is fallen at resolution")

func test_actor_ko_while_casting_refunds() -> void:
	var m = model_with(["C02"], ["E001"], 8)
	var t = until_input(m)
	var mp0 = t.mp
	# a leap-like cast: use Corren-free path: force a cast timer on Tessa's spell
	m.commit(t, {"type": "ability", "id": "S011"})
	# Before the queued action resolves, the actor is KO'd by an outside source
	t.hp = 0
	m._ko(t, {"ev": {"results": [], "msgs": []}})
	settle(m)
	eq(t.mp, mp0, "reserved MP returned when the caster falls before resolution")

func test_simultaneous_wipe_defeat_priority() -> void:
	var m = model_with(["C01"], ["E001"], 8)
	var d: BattleModel.Battler = m.battlers[m.party_ids[0]]
	var e: BattleModel.Battler = m.battlers[m.enemy_ids[0]]
	d.hp = 0; d.state = "KO"
	e.hp = 0; e.state = "KO"
	m._check_end()
	eq(m.result, "defeat", "defeat takes precedence over a simultaneous enemy wipe")

func test_status_durations_and_hard_control() -> void:
	var m = model_with(["C01"], ["E001"], 8)
	var d: BattleModel.Battler = m.battlers[m.party_ids[0]]
	d.statuses["stun"] = {"dur": 1}
	d.atb = 999.0
	m.step()
	check(not d.statuses.has("stun"), "a skipped opportunity consumes Stun")
	eq(d.state, "FILLING", "skipped actor refills")
	# reapplying stun cannot extend it
	var ctx = {"ev": {"results": [], "msgs": []}, "reactions": {}, "depth": 0, "act": {}}
	d.statuses["stun"] = {"dur": 1}
	m._try_status(m.battlers[m.enemy_ids[0]], d, {"op": "status", "id": "stun", "chance": 100, "dur": 5}, ctx)
	eq(d.statuses["stun"]["dur"], 1, "stun reapplication cannot extend before acting")
	# poison ticks once per actual action and ends
	d.statuses.erase("stun")
	d.statuses["poison"] = {"dur": 2}
	var hp0 = d.hp
	m._after_action(d, {"type": "defend", "key": "x"}, {"ev": {"results": [], "msgs": []}, "reactions": {}, "depth": 0, "act": {}})
	eq(d.hp, hp0 - int(ceil(d.mhp * 0.04)), "poison 4% after acting")
	eq(d.statuses["poison"]["dur"], 1, "duration decremented once")

func test_haste_slow_exclusive() -> void:
	var m = model_with(["C01"], ["E001"], 8)
	var d: BattleModel.Battler = m.battlers[m.party_ids[0]]
	var ctx = {"ev": {"results": [], "msgs": []}, "reactions": {}, "depth": 0, "act": {}}
	m._try_status(d, d, {"op": "status", "id": "haste", "chance": 100}, ctx)
	m._try_status(d, d, {"op": "status", "id": "slow", "chance": 100}, ctx)
	check(d.has("slow") and not d.has("haste"), "slow replaces haste")

func test_boss_immunities_and_delay_cap() -> void:
	var m = model_with(["C01"], ["B01"], 8)
	var b: BattleModel.Battler = m.battlers[m.enemy_ids[0]]
	var ctx = {"ev": {"results": [], "msgs": []}, "reactions": {}, "depth": 0, "act": {}}
	for s in ["sleep", "stun", "doom"]:
		m._try_status(m.battlers[m.party_ids[0]], b, {"op": "status", "id": s, "chance": 100}, ctx)
		check(not b.has(s), "boss immune to " + s)
	b.atb = 800.0
	b.state = "FILLING"
	for i in range(4):
		m._apply_op(m.battlers[m.party_ids[0]], b, {"op": "atb", "amount": -150}, ctx)
	check(b.atb >= 600.0 - 0.01, "boss ATB delay capped at 200 between its actions (got %s)" % b.atb)

func test_defense_stacking_cap() -> void:
	var m = model_with(["C01"], ["E001"], 10)
	var d: BattleModel.Battler = m.battlers[m.party_ids[0]]
	var e: BattleModel.Battler = m.battlers[m.enemy_ids[0]]
	var ctx = {"ev": {"results": [], "msgs": []}, "reactions": {}, "depth": 0, "act": {"targets": [d.id]}}
	# measure unreduced damage with a fixed rng
	m.rng.seed_with(7)
	var hp0 = d.hp
	m._do_damage(e, d, {"op": "damage", "power": 100, "type": "physical", "no_crit": true, "reaction": true}, ctx)
	var base_dmg = hp0 - d.hp
	d.hp = hp0
	d.defending = true
	d.statuses["barrier"] = {"dur": 3}
	d.feather = true
	d.passives = {"phys_reduce": 0.1}
	m.rng.seed_with(7)
	m._do_damage(e, d, {"op": "damage", "power": 100, "type": "physical", "no_crit": true, "reaction": true}, ctx)
	var red_dmg = hp0 - d.hp
	check(red_dmg >= int(floor(base_dmg * 0.2)) - 1 and red_dmg > 0, "stacked reductions stop at 80%% (base %d, reduced %d)" % [base_dmg, red_dmg])

func test_counter_no_recursion() -> void:
	var m = model_with(["C01"], ["E021"], 12)
	var d: BattleModel.Battler = m.battlers[m.party_ids[0]]
	d.passives = {"counter": 0.5}
	d.hp = d.mhp
	var e: BattleModel.Battler = m.battlers[m.enemy_ids[0]]
	var ev = {"type": "action", "results": [], "msgs": []}
	var ctx = {"ev": ev, "depth": 0, "reactions": {}, "act": {"targets": [d.id]}}
	# Chain Kite: two light hits count as one source action -> at most one counter
	m._apply_op(e, d, {"op": "damage", "power": 60, "type": "physical"}, ctx)
	m._apply_op(e, d, {"op": "damage", "power": 60, "type": "physical"}, ctx)
	var counters = ev["msgs"].filter(func(x): return String(x).contains("counters"))
	check(counters.size() <= 1, "one counter per source action (got %d)" % counters.size())

func test_concord_accounting() -> void:
	var m = model_with(["C01", "C02"], ["E023"], 14)
	var d: BattleModel.Battler = m.battlers[m.party_ids[0]]
	var t: BattleModel.Battler = m.battlers[m.party_ids[1]]
	m._gain_concord(d, 6)
	eq(m.concord, 6, "+6 per eligible action")
	t.passives = {"concord_bonus": 2}
	m._gain_concord(t, 6)
	eq(m.concord, 14, "accessory bonus applies")
	m.concord = 0
	for i in range(30):
		m._gain_concord(d, 6)
	eq(m.concord, 100, "Concord caps at 100")
	# summon needs link + 100 and is once per battle
	m.links[d.id] = "V01"
	d.state = "READY"
	var r = m.commit(d, {"type": "summon"})
	check(r["ok"], "summon allowed at 100 Concord")
	eq(m.concord, 0, "summon spends 100")
	m.concord = 100
	settle(m)
	d.state = "READY"
	var r2 = m.validate(d, {"type": "summon"})
	check(not r2["ok"], "each Vestige once per battle")

func test_escape_meter_and_boss_block() -> void:
	var m = model_with(["C01"], ["E001"], 8)
	var d = until_input(m)
	for i in range(4):
		m.commit(d, {"type": "escape"})
		settle(m)
		if m.result == "fled":
			break
		d.state = "READY"
		m.ready_order = [d.id]
	eq(m.result, "fled", "four Escape actions reach 1000 and succeed (no random failure)")
	var b = model_with(["C01"], ["B01"], 8)
	var bd: BattleModel.Battler = b.battlers[b.party_ids[0]]
	bd.state = "READY"
	check(not b.validate(bd, {"type": "escape"})["ok"], "bosses disable Escape")
	check(not b.validate(bd, {"type": "item", "id": "I014"})["ok"], "Smoke Pellet not consumed when fleeing is forbidden")

func test_boss_phase_threshold_once() -> void:
	var m = model_with(["C01"], ["B01"], 8)
	var b: BattleModel.Battler = m.battlers[m.enemy_ids[0]]
	b.hp = int(b.mhp * 0.20)
	var ctx = {"ev": {"results": [], "msgs": []}, "reactions": {}, "depth": 0, "act": {}}
	m._check_phase_and_split(ctx)
	m._check_phase_and_split(ctx)
	eq(m.phase_queue.size(), 1, "crossing two thresholds with one hit queues one transition to the deepest phase")
	settle(m)
	eq(b.ai["phase"], 2, "boss now in its final phase")
	m._check_phase_and_split(ctx)
	eq(m.phase_queue.size(), 0, "phase does not start twice")

func test_part_weakens_telegraphed_hit() -> void:
	var m = model_with(["C01", "C02"], ["B01", {"id": "B01_P1", "part_of": "E1"}], 8)
	var boss: BattleModel.Battler = m.battlers["E1"]
	var valve: BattleModel.Battler = m.battlers["E2"]
	check(valve.tags.has("part"), "valve is a part")
	boss.part_hit = false
	var ctx = {"ev": {"results": [], "msgs": []}, "reactions": {}, "depth": 0, "act": {}}
	m._apply_op(m.battlers[m.party_ids[0]], valve, {"op": "damage", "power": 100, "type": "physical"}, ctx)
	check(boss.part_hit, "striking the valve marks the charged clamp as weakened")
	check(valve.hp >= 1, "parts are never destroyed (counter remains available)")
	m._check_end()
	eq(m.result, "", "a living part alone does not keep or end the battle")
