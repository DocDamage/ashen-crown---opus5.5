"""Dialogue voice blips (sys s4): writes short synthesized WAVs to game/assets/audio/blips/ plus voices.json, the
speaker -> [voice, pitch] table read by Audio.blip(). Deterministic (fixed seed); re-run after editing VOICES/MAP.
A licensed dialogue pack can replace any voice: drop <voice>.wav into game/assets/ext/audio/blips/ (library override).
Usage: python3 tools/audio/gen_blips.py"""
import json, math, os, random, struct, wave

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "game", "assets", "audio", "blips")
RATE = 22050

def env(i, n, attack=0.004, release=0.02):
    t = i / RATE
    a = min(1.0, t / attack)
    r = min(1.0, (n - i) / (release * RATE))
    return a * r

def osc(kind, ph, rnd):
    x = ph % 1.0
    if kind == "square":
        return 1.0 if x < 0.5 else -1.0
    if kind == "pulse":
        return 1.0 if x < 0.18 else -1.0
    if kind == "triangle":
        return 4 * abs(x - 0.5) - 1.0
    if kind == "saw":
        return 2 * x - 1.0
    if kind == "sine":
        return math.sin(2 * math.pi * x)
    if kind == "noise":
        return rnd.uniform(-1, 1)
    return 0.0

# voice: (layers [(wave, freq multiplier, gain)], base Hz, length s, pitch glide, vibrato Hz)
VOICES = {
    "pulse": ([("square", 1.0, 0.55), ("square", 2.0, 0.12)], 330, 0.050, 0.0, 0),
    "reed": ([("pulse", 1.0, 0.5), ("triangle", 1.0, 0.3)], 392, 0.055, 0.0, 22),
    "tri": ([("triangle", 1.0, 0.9)], 440, 0.050, -0.06, 0),
    "saw": ([("saw", 1.0, 0.45), ("square", 0.5, 0.15)], 262, 0.055, -0.04, 0),
    "bell": ([("sine", 1.0, 0.7), ("sine", 2.76, 0.2), ("sine", 5.4, 0.08)], 523, 0.070, 0.0, 0),
    "stone": ([("square", 1.0, 0.4), ("noise", 1.0, 0.25)], 150, 0.060, -0.1, 0),
    "rasp": ([("saw", 1.0, 0.35), ("noise", 1.0, 0.35)], 220, 0.050, 0.0, 30),
    "chip": ([("square", 1.0, 0.45), ("square", 1.5, 0.3)], 660, 0.040, 0.12, 0),
}

# heroes by id, generic speakers by portrait/type key; anything else falls back to a hash of the key
MAP = {
    "C01": ["pulse", 0.72], "C02": ["bell", 1.08], "C03": ["tri", 1.28], "C04": ["stone", 0.9], "C05": ["reed", 1.22],
    "C06": ["pulse", 0.9], "C07": ["saw", 0.72], "C08": ["tri", 1.6], "C09": ["reed", 1.42], "C10": ["bell", 0.95],
    "C11": ["saw", 1.12], "C12": ["rasp", 0.92], "C13": ["bell", 0.6], "C14": ["pulse", 0.62], "C15": ["saw", 0.58],
    "C16": ["chip", 1.0], "C17": ["rasp", 0.7],
}
TYPES = {
    "guard": ["pulse", 0.82], "soldier": ["pulse", 0.86], "elder": ["tri", 0.82], "child": ["tri", 1.75],
    "survivor": ["tri", 1.0], "keeper": ["reed", 1.0], "clerk": ["reed", 1.16], "sailor": ["saw", 0.92],
    "baker": ["tri", 1.2], "farmer": ["pulse", 1.0], "noble": ["bell", 1.12], "apprentice": ["tri", 1.4],
    "worker": ["pulse", 0.95], "priest": ["bell", 0.85], "merchant": ["reed", 1.05], "delver": ["stone", 1.1],
    "machine": ["chip", 0.8], "dead": ["rasp", 0.6], "monster": ["stone", 0.7],
}

def write(name, spec, seed):
    layers, hz, length, glide, vib = spec
    rnd = random.Random(seed)
    n = int(RATE * length)
    frames = bytearray()
    phases = [0.0] * len(layers)
    for i in range(n):
        f = hz * (1.0 + glide * i / n)
        if vib:
            f *= 1.0 + 0.02 * math.sin(2 * math.pi * vib * i / RATE)
        v = 0.0
        for k, (w, mul, g) in enumerate(layers):
            phases[k] += f * mul / RATE
            v += g * osc(w, phases[k], rnd)
        v *= env(i, n) * 0.55
        frames += struct.pack("<h", int(max(-1.0, min(1.0, v)) * 32000))
    with wave.open(os.path.join(OUT, name + ".wav"), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(bytes(frames))

def main():
    os.makedirs(OUT, exist_ok=True)
    for i, (k, spec) in enumerate(sorted(VOICES.items())):
        write(k, spec, 1000 + i)
    with open(os.path.join(OUT, "voices.json"), "w") as f:
        json.dump({"voices": sorted(VOICES), "map": MAP, "types": TYPES}, f, indent=1)
    print("blips:", len(VOICES), "voices ->", OUT)

if __name__ == "__main__":
    main()
