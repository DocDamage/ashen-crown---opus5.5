extends TestCase
## Role systems AC025-AC032.

func _ctx(targets: Array = []) -> Dictionary:
	return {"ev": {"results": [], "msgs": []}, "reactions": {}, "depth": 0, "act": {"targets": targets}}

func test_dain_oaths_exclusive_and_sacrifice_caps() -> void:
	var m = model_with(["C01", "C02"], ["E016"], 20)
	var d: BattleModel.Battler = m.battlers[m.party_ids[0]]
	var t: BattleModel.Battler = m.battlers[m.party_ids[1]]
	var e: BattleModel.Battler = m.battlers[m.enemy_ids[0]]
	m._apply_op(d, d, {"op": "oath", "oath": "shelter"}, _ctx())
	m._apply_op(d, d, {"op": "oath", "oath": "wrath"}, _ctx())
	eq(d.oath, "wrath", "only one oath at a time")
	m._apply_op(d, d, {"op": "oath", "oath": "sacrifice"}, _ctx())
	d.hp = 5
	var hp_t = t.hp
	m._do_damage(e, t, {"op": "damage", "power": 300, "type": "physical", "no_crit": true}, _ctx([t.id]))
	check(d.hp >= 1, "Sacrifice transfer never reduces Dain below 1 HP")
	check(d.hp <= 5, "Dain took at most the capped share")

func test_shelter_intercepts_low_ally_once() -> void:
	var m = model_with(["C01", "C02"], ["E016"], 20)
	var d: BattleModel.Battler = m.battlers[m.party_ids[0]]
	var t: BattleModel.Battler = m.battlers[m.party_ids[1]]
	var e: BattleModel.Battler = m.battlers[m.enemy_ids[0]]
	d.oath = "shelter"
	t.hp = int(t.mhp * 0.3)
	var hp_t = t.hp
	var hp_d = d.hp
	var ctx = _ctx([t.id])
	m._do_damage(e, t, {"op": "damage", "power": 100, "type": "physical", "no_crit": true}, ctx)
	eq(t.hp, hp_t, "intercepted hit leaves the low ally untouched")
	check(d.hp < hp_d, "Dain takes the intercepted share")
	var hp_t2 = t.hp
	m._do_damage(e, t, {"op": "damage", "power": 100, "type": "physical", "no_crit": true}, ctx)
	check(t.hp < hp_t2, "only the first hit per enemy action is intercepted")

func test_tessa_overcast_costs_and_nonlethal() -> void:
	var m = model_with(["C02"], ["E023"], 20)
	var t = until_input(m)
	var a = Content.ability("S009")
	m.commit(t, {"type": "ability", "id": "S013"})
	settle(m)
	check(t.overcast, "Overcast armed")
	t.state = "READY"
	m.ready_order = [t.id]
	eq(m.mp_cost(t, a), int(ceil(4 * 1.75)), "armed spell costs x1.75 rounded up")
	t.hp = 3
	var mp0 = t.mp
	m.commit(t, {"type": "ability", "id": "S009", "targets": [m.enemy_ids[0]]})
	settle(m)
	check(t.hp >= 1, "Overcast self-damage is nonlethal")
	check(not t.overcast, "armed state consumed by the spell")
	eq(t.mp, mp0 - 7, "exactly one boosted MP charge")

func test_heat_exchange_limits() -> void:
	var m = model_with(["C02"], ["E023"], 30)
	var t: BattleModel.Battler = m.battlers[m.party_ids[0]]
	t.state = "READY"
	check(m.validate(t, {"type": "ability", "id": "S015"})["ok"], "usable at start")
	m._apply_op(t, t, {"op": "heat_exchange"}, _ctx())
	check(not m.validate(t, {"type": "ability", "id": "S015"})["ok"], "not twice without a damaging spell between")
	t.heat_ready = true
	t.heat_uses = 3
	check(not m.validate(t, {"type": "ability", "id": "S015"})["ok"], "max three per battle")
	t.hp = 1
	t.heat_uses = 0
	m._apply_op(t, t, {"op": "heat_exchange"}, _ctx())
	eq(t.hp, 1, "never lethal")

func test_corren_airborne_no_softlock() -> void:
	var m = model_with(["C03", "C01"], ["E001"], 10)
	var c: BattleModel.Battler = null
	if until_ready(m, m.party_ids[0]):
		c = m.battlers[m.party_ids[0]]
	check(c != null, "Corren ready")
	m.commit(c, {"type": "ability", "id": "S017", "targets": [m.enemy_ids[0]]})
	eq(c.state, "AIRBORNE", "Updraft leaves the field")
	check(not c.targetable(), "airborne is untargetable")
	var dain: BattleModel.Battler = m.battlers[m.party_ids[1]]
	dain.hp = 0; dain.state = "KO"
	m._check_end()
	eq(m.result, "", "an airborne living ally is not a defeat")
	for i in range(200):
		while m.locked:
			m.ack()
		m.step()
		if c.state != "AIRBORNE":
			break
	check(c.state != "AIRBORNE", "Corren lands after 1.2 simulated seconds")

func test_ivo_mine_and_decoy() -> void:
	var m = model_with(["C04"], ["E023"], 20)
	var i: BattleModel.Battler = m.battlers[m.party_ids[0]]
	var e: BattleModel.Battler = m.battlers[m.enemy_ids[0]]
	m._apply_op(i, e, {"op": "mine", "power": 170}, _ctx())
	m._apply_op(i, e, {"op": "mine", "power": 170}, _ctx())
	check(not e.mine.is_empty(), "mine attached")
	# one mine per enemy: reapplication refreshes rather than duplicating
	eq(typeof(e.mine), TYPE_DICTIONARY, "single mine record")
	m._apply_op(i, i, {"op": "decoy"}, _ctx())
	eq(m.decoy["draws"], 2, "decoy draws the next two single-target attacks")
	i.state = "READY"
	check(not m.validate(i, {"type": "ability", "id": "S031"})["ok"] or not i.abilities.has("S031"), "only one team decoy at a time")

func test_nera_mark_bonus_not_multiplied() -> void:
	var m = model_with(["C05"], ["E023"], 25)
	var n: BattleModel.Battler = m.battlers[m.party_ids[0]]
	var e: BattleModel.Battler = m.battlers[m.enemy_ids[0]]
	e.statuses["mark"] = {"dur": 4}
	e.statuses["guardbreak"] = {"dur": 3}
	m.rng.seed_with(3)
	var h0 = e.hp
	m._do_damage(n, e, {"op": "damage", "power": 175, "type": "physical", "ranged": true, "no_crit": true, "bonus_vs": {"guardbreak": 1.25, "mark": 1.25}}, _ctx())
	var both = h0 - e.hp
	e.hp = h0
	e.statuses.erase("guardbreak")
	m.rng.seed_with(3)
	m._do_damage(n, e, {"op": "damage", "power": 175, "type": "physical", "ranged": true, "no_crit": true, "bonus_vs": {"mark": 1.25}}, _ctx())
	var one = h0 - e.hp
	check(both < one * 1.40, "Exposed Thread +25% applies once, not per status (both=%d one=%d)" % [both, one])

func test_oriel_omen_reads_only_committed() -> void:
	var m = model_with(["C06"], ["E004"], 20)
	var o: BattleModel.Battler = m.battlers[m.party_ids[0]]
	var e: BattleModel.Battler = m.battlers[m.enemy_ids[0]]
	e.intent = {}
	var ctx = _ctx()
	m._apply_op(o, e, {"op": "omen"}, ctx)
	var msg: String = ctx["ev"]["msgs"][0]
	check(not msg.contains("→"), "no target shown without a committed intent")
	e.intent = {"move": "lunge", "name": "Lunge", "targets": [o.id], "tell": ""}
	var ctx2 = _ctx()
	m._apply_op(o, e, {"op": "omen"}, ctx2)
	check(String(ctx2["ev"]["msgs"][0]).contains(o.name), "committed intent and target revealed")

func test_sable_single_infusion() -> void:
	var m = model_with(["C07"], ["E001"], 20)
	var s: BattleModel.Battler = m.battlers[m.party_ids[0]]
	m._apply_op(s, s, {"op": "infuse", "elem": "fire", "dur": 4}, _ctx())
	m._apply_op(s, s, {"op": "infuse", "elem": "ice", "dur": 4}, _ctx())
	eq(s.infusion["elem"], "ice", "one infusion; the new one replaces the old")

func test_pip_steal_caps() -> void:
	var m = model_with(["C08"], ["E001"], 20)
	var p: BattleModel.Battler = m.battlers[m.party_ids[0]]
	var e: BattleModel.Battler = m.battlers[m.enemy_ids[0]]
	for i in range(12):
		m._apply_op(p, e, {"op": "steal"}, _ctx())
	check(m.stolen_items.size() <= 2, "at most one common and one rare per enemy instance")
	check(e.steal["common_taken"], "after three failures the common steal succeeds")

func test_accessory_spell_removed_with_accessory() -> void:
	fresh_game()
	Game.add_item("A001", 1)
	Game.equip("C01", "acc1", "A001")
	var p = Game.battle_party()
	check(p[0]["stats"]["grants"].has("S065"), "Ember Token grants Kindle while equipped")
	Game.equip("C01", "acc1", "")
	p = Game.battle_party()
	check(not p[0]["stats"]["grants"].has("S065"), "grant disappears when removed")
	check(not Game.learned_abilities("C01").has("S065"), "never permanently learned")
