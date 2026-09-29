class_name Rng
extends RefCounted
## Deterministic xorshift32 stream. Separate instances are used for combat, loot and cosmetics.

var state: int = 2463534242

func _init(seed_value: int = 2463534242) -> void:
	seed_with(seed_value)

func seed_with(seed_value: int) -> void:
	state = seed_value & 0xffffffff
	if state == 0:
		state = 0x9e3779b9

func next_u32() -> int:
	var x = state
	x ^= (x << 13) & 0xffffffff
	x ^= x >> 17
	x ^= (x << 5) & 0xffffffff
	state = x & 0xffffffff
	return state

## Float in [0, 1)
func randf() -> float:
	return float(next_u32()) / 4294967296.0

func randi_range(a: int, b: int) -> int:
	if b <= a:
		return a
	return a + int(next_u32() % (b - a + 1))

func chance(pct: float) -> bool:
	# explicit stream draw (a bare randf() here would resolve to the global, non-seeded RNG)
	return float(next_u32()) / 4294967296.0 * 100.0 < pct

func pick(arr: Array):
	if arr.is_empty():
		return null
	return arr[next_u32() % arr.size()]
