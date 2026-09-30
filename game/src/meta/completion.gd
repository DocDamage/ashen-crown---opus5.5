class_name Completion
extends RefCounted
## Open-world completion (Records > Stats): places visited, questlines, chests, Vestiges, superbosses and bestiary.
## Each part is a fraction; the total is their average, shown as a percentage.

static func _chests_total() -> int:
	var ids = {}
	for mid in Content.data["maps"]:
		for e in Content.data["maps"][mid]["entities"]:
			if e["type"] == "chest":
				ids[e["id"]] = true
	return ids.size()

static func parts() -> Array:
	var locs: Dictionary = Content.data.get("locations", {})
	var visited = 0
	for l in Game.S.get("discovered", []):
		if locs.has(l):
			visited += 1
	var qdone = 0
	for q in Content.data.get("quests", {}):
		if Game.quest_state(q) == "COMPLETED":
			qdone += 1
	var sb = 0
	for i in range(1, 13):
		if Game.superboss_down("SB%02d" % i):
			sb += 1
	return [
		["Places visited", visited, locs.size()],
		["Questlines", qdone, Content.data.get("quests", {}).size()],
		["Chests", Game.S.get("chests", []).size(), _chests_total()],
		["Vestiges", Game.S.get("vestiges", []).size(), Content.data.get("vestiges", {}).size()],
		["Superbosses", sb, 12],
		["Bestiary", int(Achievements.meta_value("bestiary_pct")), 100],
	]

static func percent() -> int:
	var ps = parts()
	var sum = 0.0
	for p in ps:
		sum += clampf(float(p[1]) / maxf(1.0, float(p[2])), 0.0, 1.0)
	return int(floor(100.0 * sum / ps.size()))
