class_name TestCase
extends RefCounted
## Minimal assertion base. Fixtures may build state (labelled unit/integration evidence only).

var failures: Array = []
var _saved_S: Dictionary = {}

func snapshot() -> void:
	_saved_S = Game.S.duplicate(true)

func restore() -> void:
	if not _saved_S.is_empty():
		Game.S = _saved_S

func check(cond: bool, msg: String) -> void:
	if not cond:
		failures.append(msg)

func eq(a, b, msg: String) -> void:
	if a != b:
		failures.append("%s (got %s, expected %s)" % [msg, str(a), str(b)])

# ---------------------------------------------------------------- fixtures
func fresh_game() -> void:
	Game.new_game()
	Game.fixture_label = "unit-fixture"

func party(cids: Array, level: int = 10) -> Array:
	fresh_game()
	for cid in cids:
		var m: Dictionary = Game.member(cid)
		m["level"] = level
		m["xp"] = F.xp_total_for_level(level)
		if not Game.is_recruited(cid):
			Game.recruit(cid)
	Game.set_active(cids)
	Game.heal_all()
	return Game.battle_party()

func model_with(cids: Array, enemies: Array, level: int = 10, inv: Dictionary = {}, seed_value: int = 99, opts: Dictionary = {}) -> BattleModel:
	var p = party(cids, level)
	var m = BattleModel.new(Content.data)
	var i = inv if not inv.is_empty() else {"I001": 5, "I006": 1, "I004": 3}
	m.setup(p, enemies, i, seed_value, opts)
	return m

## Advance the model until someone needs input, acknowledging events immediately.
func until_input(m: BattleModel, max_ticks: int = 20000) -> BattleModel.Battler:
	return m.run_until_input(max_ticks)

func until_ready(m: BattleModel, bid: String, max_ticks: int = 20000) -> bool:
	var n = 0
	while n < max_ticks:
		while m.locked:
			m.ack()
		if m.result != "":
			return false
		var w = m.awaiting_input()
		if w != null and w.id == bid:
			return true
		if w != null:
			m.commit(w, {"type": "defend"})
		m.step()
		n += 1
	return false

func settle(m: BattleModel, max_ticks: int = 400) -> void:
	for i in range(max_ticks):
		while m.locked:
			m.ack()
		if m.queue.is_empty() and m.phase_queue.is_empty():
			return
		m.step()
