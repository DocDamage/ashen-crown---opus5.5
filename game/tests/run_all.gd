extends SceneTree
## Wrapper for the templated command `godot --headless --path game --script res://tests/run_all.gd`.
## Godot's --script mode does not register autoload singletons, so the suite is executed inside a
## normal game process (--qa-tests) and its exit code is relayed here.
func _initialize() -> void:
	var out = []
	var args = ["--headless", "--path", ProjectSettings.globalize_path("res://"), "--", "--qa-tests", "--qa-out", ProjectSettings.globalize_path("user://qa")]
	var code = OS.execute(OS.get_executable_path(), args, out, true)
	for l in out:
		print(l)
	quit(code)
