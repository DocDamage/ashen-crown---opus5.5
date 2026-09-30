class_name Arena
extends RefCounted
## The Crucible Isle arena (N38): data in content "arena" (tools/content/field_s3.py), state in Game.S["arena"]:
##   {"rank": highest ladder rank won, "solo": [won solo ids], "gauntlet": bool, "bets": wins, "beasts": wins}
## Ladder: fight the next rank only; each rank pays its reward once. Solo: one hero alone. Bets: wager an item from
## the table, win the prize or lose the wager. Gauntlet: the champion's fights in a row, Varro (SB07) last.
## Beasts: when Game.S["captured"] holds monsters (another system), enter one in a bout for a crown stake.
## Arena battles never end the game: a loss restores the party and returns to the hall (run_battle opts.arena).

static func data() -> Dictionary:
	return Content.data.get("arena", {})

static func state() -> Dictionary:
	if Game.S.is_empty():
		return {}
	if not Game.S.has("arena"):
		Game.S["arena"] = {"rank": 0, "solo": [], "gauntlet": false, "bets": 0, "beasts": 0}
	return Game.S["arena"]

static func rank() -> int:
	return int(state().get("rank", 0))

## The next ladder rank to fight ({} when the ladder is done); `open` false when its condition is not met yet.
static func next_rank() -> Dictionary:
	for r in data().get("ladder", []):
		if int(r["rank"]) == rank() + 1:
			var out: Dictionary = r.duplicate()
			out["open"] = Game.eval_cond(r.get("if", []))
			return out
	return {}

static func ladder_done() -> bool:
	return rank() >= data().get("ladder", []).size()

## Record a ladder win: only the next rank counts; returns the reward row the first time, {} otherwise.
static func win_rank(n: int) -> Dictionary:
	var nr = next_rank()
	if nr.is_empty() or int(nr["rank"]) != n or not nr["open"]:
		return {}
	state()["rank"] = n
	Game.add_item(str(nr["reward"]), int(nr.get("n", 1)))
	Game.add_gold(int(nr.get("gold", 0)))
	return nr

static func solo_rows() -> Array:
	var out = []
	for s in data().get("solo", []):
		var won: bool = state().get("solo", []).has(s["id"])
		var ok: bool = rank() >= int(s.get("rank", 0))
		out.append({"row": s, "won": won, "open": ok and not won})
	return out

static func win_solo(sid: String) -> bool:
	for s in data().get("solo", []):
		if s["id"] == sid and not state()["solo"].has(sid) and rank() >= int(s.get("rank", 0)):
			state()["solo"].append(sid)
			Game.add_item(str(s["reward"]), int(s.get("n", 1)))
			return true
	return false

## Bets the party can place now (they own the wager and it is not equipped-only).
static func bet_rows() -> Array:
	var out = []
	for b in data().get("bets", []):
		if Game.count(str(b["wager"])) > 0:
			out.append(b)
	return out

## Settle a bet: the wager is always spent; a win pays the prize. Returns true when the prize was paid.
static func settle_bet(b: Dictionary, won: bool) -> bool:
	if not Game.remove_item(str(b["wager"]), 1):
		return false
	if won:
		Game.add_item(str(b["prize"]), 1)
		state()["bets"] = int(state().get("bets", 0)) + 1
	return won

static func gauntlet_open() -> bool:
	return ladder_done() and Game.eval_cond(data().get("gauntlet_if", [])) and not bool(state().get("gauntlet", false))

## Captured monsters (another system fills Game.S.captured): accepts an Array of ids / {id} dicts or a Dictionary.
static func captured() -> Array:
	var c = Game.S.get("captured", [])
	var out = []
	if typeof(c) == TYPE_DICTIONARY:
		for k in c:
			out.append(str(k))
	elif typeof(c) == TYPE_ARRAY:
		for x in c:
			if typeof(x) == TYPE_DICTIONARY:
				out.append(str(x.get("id", x.get("enemy", ""))))
			else:
				out.append(str(x))
	return out.filter(func(e): return not Content.enemy(e).is_empty())

## A beast bout is watched, not played: the higher level wins more often (seeded, deterministic).
static func beast_bout(mine: String, rival: String) -> bool:
	var a = float(Content.enemy(mine).get("level", 1))
	var b = float(Content.enemy(rival).get("level", 1))
	var r = Rng.new(Game.next_seed("loot"))
	return r.randf() < clampf(0.5 + (a - b) * 0.04, 0.15, 0.85)

# ---------------------------------------------------------------- scene flows (`arena <op>`)
static func _fight(main: Node, form: String) -> bool:
	var res: String = await main.run_battle(form, {"scripted": true, "flags": ["noflee"], "arena": true})
	return res == "victory"

static func run(main: Node, a: Array) -> void:
	var op: String = a[0] if a.size() > 0 else ""
	match op:
		"ladder": await _ladder(main)
		"solo": await _solo(main)
		"bet": await _bet(main)
		"gauntlet": await _gauntlet(main)
		"beasts": await _beasts(main)
		"board": await _board(main)

static func _board(main: Node) -> void:
	var nr = next_rank()
	var txt = "Rank %d of %d." % [rank(), data().get("ladder", []).size()]
	if not nr.is_empty():
		txt += " Next: %s." % nr["name"]
	await main.say("", txt)

static func _ladder(main: Node) -> void:
	if ladder_done():
		await main.say("Registrar_Omm", "Your name is at the top of my ladder. Only the champion's gate is left, and I don't keep that book.")
		return
	var nr = next_rank()
	if not nr["open"]:
		await main.say("Registrar_Omm", "Rank %d is not being fought this season. The fighters for it are not on the isle. Come back when the world has moved." % int(nr["rank"]))
		return
	var pick: int = await main.choose(["Fight rank %d: %s" % [int(nr["rank"]), nr["name"]], "Not yet"])
	if pick != 0:
		return
	if await _fight(main, str(nr["form"])):
		var r = win_rank(int(nr["rank"]))
		if not r.is_empty():
			Audio.sfx("FX007")
			await main.say("", "Rank %d taken. Prize: %s x%d and %d crowns." % [int(r["rank"]), Content.item_name(str(r["reward"])), int(r.get("n", 1)), int(r.get("gold", 0))])
	else:
		await main.say("Registrar_Omm", "Carried out on a board. It happens to most. Your rank stands where it stood.")

static func _solo(main: Node) -> void:
	var rows = solo_rows()
	var opts = []
	var open = []
	for r in rows:
		if r["open"]:
			opts.append(str(r["row"]["name"]))
			open.append(r["row"])
	if open.is_empty():
		await main.say("Ser_Anneth", "Nothing for you today. Climb the ladder; I set a solo bout at every few ranks.")
		return
	opts.append("Not yet")
	var pick: int = await main.choose(opts)
	if pick < 0 or pick >= open.size():
		return
	var s: Dictionary = open[pick]
	var ids: Array = Game.active()
	var names = ids.map(func(c): return Game.short_name(c))
	names.append("Never mind")
	var who: int = await main.choose(names)
	if who < 0 or who >= ids.size():
		return
	var keep: Array = Game.S["party"]["active"].duplicate()
	var locked: bool = Game.S["party"].get("locked", false)
	Game.S["party"]["active"] = [ids[who]]
	main.field.update_leader()
	var won = await _fight(main, str(s["form"]))
	Game.S["party"]["active"] = keep
	Game.S["party"]["locked"] = locked
	main.field.update_leader()
	if won and win_solo(str(s["id"])):
		Audio.sfx("FX007")
		await main.say("", "%s stands alone and wins. Prize: %s." % [Game.short_name(ids[who]), Content.item_name(str(s["reward"]))])
	elif not won:
		await main.say("Ser_Anneth", "Alone is hard. That is the whole lesson. Come back when it's easier.")

static func _bet(main: Node) -> void:
	var rows = bet_rows()
	if rows.is_empty():
		await main.say("Bookmaker_Sallow", "Nothing on you I'd take. Bring me something worth wagering. Tonics, ethers, leaves, the odd charm.")
		return
	var opts = []
	for b in rows:
		opts.append("%s for %s" % [Content.item_name(str(b["wager"])), Content.item_name(str(b["prize"]))])
	opts.append("No bet")
	var pick: int = await main.choose(opts)
	if pick < 0 or pick >= rows.size():
		return
	var b: Dictionary = rows[pick]
	await main.say("Bookmaker_Sallow", "%s on the table. The house fields its own. Win, and the %s is yours." % [Content.item_name(str(b["wager"])), Content.item_name(str(b["prize"]))])
	var won = await _fight(main, str(b["form"]))
	settle_bet(b, won)
	if won:
		Audio.sfx("FX007")
		await main.say("", "Won: %s." % Content.item_name(str(b["prize"])))
	else:
		await main.say("Bookmaker_Sallow", "The house thanks you for the %s." % Content.item_name(str(b["wager"])))

static func _gauntlet(main: Node) -> void:
	if bool(state().get("gauntlet", false)):
		await main.say("Herald", "The champion's name is yours. The gate stays open for you.")
		return
	if not gauntlet_open():
		await main.say("Herald", "The gauntlet is for the top of the ladder, in a world that has already ended once. Neither is true of you yet.")
		return
	var pick: int = await main.choose(["Run the gauntlet (no rest between fights)", "Not yet"])
	if pick != 0:
		return
	var forms: Array = data().get("gauntlet", [])
	for i in range(forms.size()):
		if i == forms.size() - 1:
			await main.say("Herald", "Last gate. Varro the Unbeaten. He has not lost in the ring in twenty-two years.")
		var ok = await _fight(main, str(forms[i]))
		if not ok:
			await main.say("Herald", "The gauntlet is broken at fight %d. The champion keeps his gate." % (i + 1))
			return
	state()["gauntlet"] = true
	Game.set_flag("arena_champion", true)
	Game.set_flag("sb_SB07_down", true)
	var rw := str(data().get("gauntlet_reward", ""))
	if rw != "":
		Game.add_item(rw, 1)
	Audio.sfx("FX029")
	await main.say("", "Varro kneels in the sand. The Crucible has a new champion.%s" % (" Prize: %s." % Content.item_name(rw) if rw != "" else ""))
	main.field.refresh_npcs()

static func _beasts(main: Node) -> void:
	var mine = captured()
	if mine.is_empty():
		await main.say("Pen-Keeper_Rook", "The pens take captured beasts. You've none I can see. Bring one in and we'll find it a fight.")
		return
	var stake = int(data().get("beast_stake", 200))
	var opts = mine.map(func(e): return str(Content.enemy(e).get("name", e)))
	opts.append("Not today")
	var pick: int = await main.choose(opts)
	if pick < 0 or pick >= mine.size():
		return
	if Game.gold() < stake:
		await main.say("Pen-Keeper_Rook", "The stake is %d crowns. The pens don't run on credit." % stake)
		return
	var pool: Array = Content.group("W_NIGHT")
	var rival := "E118"
	if not pool.is_empty():
		var f = Content.formation(str(pool[Rng.new(Game.next_seed("loot")).next_u32() % pool.size()]))
		if not f.get("enemies", []).is_empty():
			var e0 = f["enemies"][0]
			rival = str(e0 if typeof(e0) == TYPE_STRING else e0.get("id", rival))
	Game.spend_gold(stake)
	var won = beast_bout(mine[pick], rival)
	if won:
		Game.add_gold(stake * 2)
		state()["beasts"] = int(state().get("beasts", 0)) + 1
		await main.say("", "%s beats the house's %s. You take %d crowns." % [opts[pick], Content.enemy(rival).get("name", rival), stake * 2])
	else:
		await main.say("", "The house's %s wins. The stake is gone." % Content.enemy(rival).get("name", rival))
