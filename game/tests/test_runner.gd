extends Node
## Runtime test runner. Runs inside the game process (autoloads available):
##   godot --headless --path game -- --qa-tests [--qa-out DIR]
## Each tests/unit/*.gd file extends TestCase; every method named test_* is executed.

var results: Array = []

func run_all() -> int:
	var files = []
	var da = DirAccess.open("res://tests/unit")
	for f in da.get_files():
		if f.ends_with(".gd"):
			files.append("res://tests/unit/" + f)
	files.sort()
	var passed = 0
	var failed = 0
	var lines = []
	for path in files:
		var scr = load(path)
		if scr == null or not scr.can_instantiate():
			lines.append("LOAD FAIL " + path)
			failed += 1
			continue
		for m in scr.get_script_method_list():
			var name: String = m["name"]
			if not name.begins_with("test_"):
				continue
			var tc = scr.new()
			tc.snapshot()
			var ok = true
			var err = ""
			await tc.call(name)
			if tc.failures.size() > 0:
				ok = false
				err = "; ".join(tc.failures)
			tc.restore()
			var label = "%s::%s" % [path.get_file().get_basename(), name]
			if ok:
				passed += 1
				lines.append("PASS " + label)
			else:
				failed += 1
				lines.append("FAIL " + label + " -- " + err)
	lines.append("")
	lines.append("TOTAL %d passed, %d failed (content %s, engine %s)" % [passed, failed, Content.hash, Engine.get_version_info()["string"]])
	for l in lines:
		print(l)
	var out: String = QA.out_dir
	DirAccess.make_dir_recursive_absolute(out)
	var f = FileAccess.open(out + "/runtime_tests.log", FileAccess.WRITE)
	if f:
		f.store_string("\n".join(lines) + "\n")
	return 0 if failed == 0 else 1
