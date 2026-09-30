class_name Router
extends Node
## Converts held/pressed actions into discrete UI events with key-repeat and dispatches them to the
## top of a focus stack. Keyboard, gamepad and the QA input bot all go through the same InputMap actions.

var stack: Array = []
var _held = {}
var _repeat_at = {}
const DIRS := ["up", "down", "left", "right"]
const BUTTONS := ["confirm", "cancel", "menu", "page_l", "page_r", "skip"]
const REPEAT_DELAY := 0.28
const REPEAT_RATE := 0.07
const HOLD_DELAY := 0.5
const HOLD_RATE := 0.3
var time = 0.0

func push(n: Object) -> void:
	stack.erase(n)
	stack.append(n)

func pop(n: Object) -> void:
	stack.erase(n)

func top() -> Object:
	while not stack.is_empty() and not is_instance_valid(stack[-1]):
		stack.pop_back()
	return null if stack.is_empty() else stack[-1]

func _process(delta: float) -> void:
	time += delta
	var t = top()
	for d in DIRS:
		var a = "g_" + d
		if Input.is_action_just_pressed(a):
			_repeat_at[d] = time + REPEAT_DELAY
			_send(t, d)
		elif Input.is_action_pressed(a):
			if time >= float(_repeat_at.get(d, 1e9)):
				_repeat_at[d] = time + REPEAT_RATE
				_send(t, d)
	for b in BUTTONS:
		if Input.is_action_just_pressed("g_" + b):
			_repeat_at[b] = time + HOLD_DELAY
			_send(t, b)
			t = top()
		elif b == "confirm" and Settings.get_v("hold_confirm") and Input.is_action_pressed("g_confirm"):
			# accessibility: holding Confirm repeats it (advance text, step through menus) instead of tapping
			if time >= float(_repeat_at.get(b, 1e9)):
				_repeat_at[b] = time + HOLD_RATE
				_send(t, b)
				t = top()

func _send(t: Object, ev: String) -> void:
	if t != null and t.has_method("handle"):
		t.handle(ev)

static func held(dir: String) -> bool:
	return Input.is_action_pressed("g_" + dir)
