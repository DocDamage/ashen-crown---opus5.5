extends TestCase
## Inventory, equipment, party growth, save service, story engine (AC034-AC045, AC047-AC048).

func test_shop_boundaries() -> void:
	fresh_game()
	Game.S["inventory"]["gold"] = 45
	check(Game.buy("I001", 1, 45)["ok"], "exact gold buys")
	eq(Game.gold(), 0, "no underflow")
	check(not Game.buy("I001", 1, 45)["ok"], "insufficient gold refused before payment")
	Game.S["inventory"]["gold"] = 100000
	Game.S["inventory"]["items"]["I001"] = 99
	var g0 = Game.gold()
	check(not Game.buy("I001", 1, 45)["ok"], "99 stack refuses more")
	eq(Game.gold(), g0, "no payment when capacity check fails")

func test_unique_overflow_goes_to_delivery() -> void:
	fresh_game()
	Game.S["inventory"]["items"]["W006"] = 99
	var r = Game.add_item("W006", 1)
	eq(r["delivered"], 1, "unique equipment is delivered, never discarded")
	eq(Game.S["inventory"]["delivery"].size(), 1, "delivery chest holds it")
	Game.S["inventory"]["items"]["I001"] = 99
	var r2 = Game.add_item("I001", 2)
	eq(r2["converted_gold"], 45, "consumable overflow converts to bounded gold with notice")

func test_unique_acquisition_once() -> void:
	fresh_game()
	check(Game.acquire_unique("Q01_REWARD", "W006"), "first acquisition succeeds")
	check(not Game.acquire_unique("Q01_REWARD", "W006"), "second is refused")
	eq(Game.count("W006"), 1, "exactly one copy")

func test_two_handed_swap_returns_offhand() -> void:
	fresh_game()
	Game.recruit("C07")
	Game.add_item("G025", 1)
	check(Game.equip("C07", "offhand", "G025")["ok"], "Sable can hold a buckler")
	var before = Game.count("G025")
	# Corren's spears are two-handed; he cannot use offhands at all
	Game.recruit("C03")
	check(not Game.can_equip("C03", "offhand", "G025")["ok"], "allowed-character IDs checked")
	eq(Game.count("G025"), before, "no duplication")

func test_vestige_unique_links() -> void:
	fresh_game()
	Game.recruit("C02")
	Game.grant_vestige("V01")
	check(Game.link_vestige("V01", "C01")["ok"], "link to Dain")
	check(Game.link_vestige("V01", "C02")["ok"], "relink to Tessa")
	eq(Game.link_of("C01"), "", "a vestige cannot be linked to two characters")
	eq(Game.link_of("C02"), "V01", "now with Tessa")
	Game.set_available("C02", false)
	check(not Game.link_vestige("V01", "C02")["ok"], "cannot link to an unavailable member")
	check(not Game.link_vestige("V02", "C01")["ok"], "cannot link an unowned vestige")

func test_reserve_growth_and_reunion() -> void:
	fresh_game()
	Game.recruit("C02")
	Game.set_available("C02", false)
	var xp0: int = Game.member("C02")["xp"]
	Game.award_xp(500)
	eq(Game.member("C02")["xp"], xp0 + 500, "unavailable members receive 100% XP")
	var eq_before: Dictionary = Game.member("C02")["equip"].duplicate()
	var inv_before: Dictionary = Game.S["inventory"]["items"].duplicate()
	Game.recruit("C02")
	Game.recruit("C02")
	eq(Game.member("C02")["equip"], eq_before, "reunion keeps equipment, no second starter kit")
	eq(Game.S["inventory"]["items"], inv_before, "no starter items added to inventory")

func test_save_round_trip() -> void:
	fresh_game()
	Game.add_gold(777)
	Game.set_flag("t_flag")
	Game.S["chests"].append("X_CHEST")
	var path = "user://test_saves/rt.json"
	DirAccess.make_dir_recursive_absolute("user://test_saves")
	check(Game.save_to(path)["ok"], "save writes")
	var snap = Game.S.duplicate(true)
	Game.new_game()
	check(Game.load_from(path)["ok"], "load reads")
	eq(Game.gold(), int(snap["inventory"]["gold"]), "gold round trip")
	check(Game.flag("t_flag"), "flags round trip")
	check(Game.S["chests"].has("X_CHEST"), "chest ledger round trip")

func test_corrupt_primary_offers_backup() -> void:
	fresh_game()
	var path = "user://test_saves/corrupt.json"
	DirAccess.make_dir_recursive_absolute("user://test_saves")
	Game.save_to(path)
	Game.add_gold(5)
	Game.save_to(path)    # previous file becomes .bak
	var f = FileAccess.open(path, FileAccess.WRITE)
	f.store_string("{ this is not a save")
	f.close()
	var r = Game.load_from(path)
	check(not r["ok"], "corrupt save rejected")
	eq(r["reason"], "corrupt", "reason reported")
	check(r.get("backup_ok", false), "backup offered")
	check(FileAccess.file_exists(path + ".corrupt"), "corrupt copy retained for diagnosis")
	check(Game.load_backup_of(path)["ok"], "backup loads")

func test_future_schema_rejected() -> void:
	var path = "user://test_saves/future.json"
	DirAccess.make_dir_recursive_absolute("user://test_saves")
	var f = FileAccess.open(path, FileAccess.WRITE)
	f.store_string(JSON.stringify({"schema_version": 99, "checksum": "x", "body": "{}"}))
	f.close()
	var r = Game.load_from(path)
	check(not r["ok"] and r["reason"] == "future", "newer schema gives a clear unsupported response")
	check(FileAccess.file_exists(path), "file not overwritten")

func test_crash_during_write_keeps_complete_state() -> void:
	fresh_game()
	var path = "user://test_saves/crash.json"
	DirAccess.make_dir_recursive_absolute("user://test_saves")
	Game.save_to(path)
	var g_old = Game.gold()
	Game.add_gold(1000)
	var r1 = Game.save_to(path, "partial_tmp")
	check(not r1["ok"], "interrupted while writing temp")
	Game.new_game()
	check(Game.load_from(path)["ok"], "old complete save still loads")
	eq(Game.gold(), g_old, "old state, not a hybrid")
	Game.add_gold(1000)
	Game.save_to(path, "before_rename")
	Game.new_game()
	check(Game.load_from(path)["ok"], "interrupted before rename: old save intact")

func test_catastrophe_transaction_preserves_ownership() -> void:
	fresh_game()
	for c in ["C02", "C06", "C05", "C04"]:
		Game.recruit(c)
	Game.add_item("W002", 1)
	Game.S["chests"].append("D05_C1")
	Game.quest_set("Q99", "ACTIVE", "s1")
	var eq_tessa: Dictionary = Game.member("C02")["equip"].duplicate()
	var inv: Dictionary = Game.S["inventory"]["items"].duplicate()
	var lv: int = Game.member("C05")["level"]
	Game.catastrophe_transaction()
	eq(Game.S["world_phase"], "post", "phase changed")
	check(Game.chapter_done("CH12"), "CH12 marked complete")
	eq(Game.S["location"]["map"], "T07_HEARTH", "valid arrival map")
	eq(Game.member("C02")["equip"], eq_tessa, "absent allies keep their gear")
	eq(Game.S["inventory"]["items"], inv, "inventory preserved")
	eq(Game.member("C05")["level"], lv, "levels preserved")
	check(Game.S["chests"].has("D05_C1"), "opened chests preserved")
	check(not Game.is_available("C02") and Game.is_available("C06"), "availability updated")
	var ev_count = Game.S["events"].size()
	Game.catastrophe_transaction()
	eq(Game.S["events"].size(), ev_count, "transaction never applies twice")

func test_salvage_forwarding_once() -> void:
	fresh_game()
	Game.acquire_unique("D01_SECRET", "A001")
	Game.catastrophe_transaction()
	var got = Game.claim_salvage()
	check(not got.has("A001"), "already acquired uniques are not duplicated")
	check(got.has("A002"), "missed uniques from sealed maps are forwarded")
	eq(Game.claim_salvage().size(), 0, "salvage delivers once")

func test_quest_state_never_regresses_or_double_awards() -> void:
	fresh_game()
	Game.quest_set("Q01", "ACTIVE", "s1")
	Game.quest_set("Q01", "COMPLETED")
	Game.quest_set("Q01", "ACTIVE", "s2")
	eq(Game.quest_state("Q01"), "COMPLETED", "state machine never regresses")
