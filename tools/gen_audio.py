"""Deterministic programmatic audio: 30 music cues + 32 SFX (docs/12). Original material only.
Development-grade synthesis (additive/FM/Karplus-Strong), rendered to OGG Vorbis via ffmpeg.
The main theme contour is 1, 5, 4, 2, b3 (rest); the title withholds its final cadence and the ending
(M030) completes it. Every cue is replaceable one file at a time (game/assets/audio/music/<ID>.ogg)."""
import json, os, subprocess, sys, wave
import numpy as np

SR = 22050
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "game", "assets", "audio")
rng = np.random.default_rng(1234)


def midi_hz(n):
    return 440.0 * 2 ** ((n - 69) / 12.0)


def env(n, a=0.01, d=0.1, s=0.7, r=0.2):
    t = np.arange(n) / SR
    total = n / SR
    e = np.ones(n) * s
    ai = t < a
    e[ai] = t[ai] / max(a, 1e-4)
    di = (t >= a) & (t < a + d)
    e[di] = 1 - (1 - s) * (t[di] - a) / max(d, 1e-4)
    ri = t > total - r
    e[ri] *= np.clip((total - t[ri]) / max(r, 1e-4), 0, 1)
    return e


def osc(kind, f, n, detune=0.0):
    t = np.arange(n) / SR
    ph = 2 * np.pi * f * t
    if kind == "sine":
        return np.sin(ph)
    if kind == "tri":
        return 2 / np.pi * np.arcsin(np.sin(ph))
    if kind == "saw":
        # band-limited-ish saw by summing harmonics
        out = np.zeros(n)
        for k in range(1, 9):
            if f * k > SR / 2.5:
                break
            out += np.sin(ph * k) / k
        return out * 0.6
    if kind == "square":
        out = np.zeros(n)
        for k in range(1, 12, 2):
            if f * k > SR / 2.5:
                break
            out += np.sin(ph * k) / k
        return out * 0.8
    if kind == "reed":
        return 0.7 * np.sin(ph) + 0.25 * np.sin(3 * ph) + 0.12 * np.sin(5 * ph)
    return np.sin(ph)


def voice(inst, note, dur):
    n = int(dur * SR)
    if n <= 0:
        return np.zeros(0)
    f = midi_hz(note)
    if inst == "strings":
        x = osc("saw", f, n) * 0.5 + osc("saw", f * 1.003, n) * 0.5
        x = lowpass(x, 0.25)
        return x * env(n, 0.12, 0.2, 0.8, min(0.3, dur * 0.4)) * 0.35
    if inst == "brass":
        x = osc("square", f, n) * 0.6 + osc("saw", f, n) * 0.4
        x = lowpass(x, 0.2)
        return x * env(n, 0.05, 0.15, 0.7, 0.12) * 0.3
    if inst == "reed":
        vib = 1 + 0.004 * np.sin(2 * np.pi * 5.0 * np.arange(n) / SR)
        t = np.arange(n) / SR
        x = 0.7 * np.sin(2 * np.pi * f * vib * t) + 0.25 * np.sin(6 * np.pi * f * vib * t)
        return x * env(n, 0.06, 0.1, 0.75, 0.15) * 0.3
    if inst == "flute":
        t = np.arange(n) / SR
        vib = 1 + 0.005 * np.sin(2 * np.pi * 5.5 * t)
        x = np.sin(2 * np.pi * f * vib * t) + 0.08 * rng.standard_normal(n) * env(n, 0.02, 0.05, 0.2, 0.05)
        return x * env(n, 0.05, 0.1, 0.8, 0.12) * 0.28
    if inst == "pluck":
        return karplus(f, n) * 0.45
    if inst == "mallet":
        t = np.arange(n) / SR
        x = np.sin(2 * np.pi * f * t) * np.exp(-t * 6) + 0.3 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 14)
        return x * 0.4
    if inst == "bell":
        t = np.arange(n) / SR
        x = np.zeros(n)
        for ratio, amp, dec in ((1, 1, 2.2), (2.76, 0.5, 3.5), (5.4, 0.25, 5), (8.93, 0.12, 7)):
            x += amp * np.sin(2 * np.pi * f * ratio * t) * np.exp(-t * dec)
        return x * 0.22
    if inst == "bass":
        x = osc("tri", f, n) * 0.8 + osc("sine", f / 2, n) * 0.3
        return x * env(n, 0.01, 0.1, 0.8, 0.06) * 0.45
    if inst == "pad":
        x = osc("tri", f, n) * 0.5 + osc("sine", f * 2.001, n) * 0.2 + osc("tri", f * 0.998, n) * 0.4
        return lowpass(x, 0.15) * env(n, 0.4, 0.3, 0.8, min(0.6, dur * 0.5)) * 0.25
    if inst == "organ":
        x = osc("sine", f, n) + 0.5 * osc("sine", f * 2, n) + 0.25 * osc("sine", f * 3, n)
        return x * env(n, 0.03, 0.05, 0.9, 0.08) * 0.18
    return osc("sine", f, n) * env(n) * 0.3


def lowpass(x, a):
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc)
        y[i] = acc
    return y


def karplus(f, n):
    p = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, p)
    out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * 0.994
    return out


def drum(kind, dur=0.25):
    n = int(dur * SR)
    t = np.arange(n) / SR
    if kind == "kick":
        f = 110 * np.exp(-t * 18) + 40
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10) * 0.8
    if kind == "snare":
        return (rng.standard_normal(n) * 0.5 + np.sin(2 * np.pi * 190 * t) * 0.3) * np.exp(-t * 18) * 0.5
    if kind == "hat":
        x = rng.standard_normal(n)
        x = x - lowpass(x, 0.6)
        return x * np.exp(-t * 60) * 0.25
    if kind == "tom":
        f = 140 * np.exp(-t * 8) + 60
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * 0.5
    if kind == "shaker":
        x = rng.standard_normal(n)
        x = x - lowpass(x, 0.5)
        return x * env(n, 0.02, 0.05, 0.2, 0.05) * 0.12
    return np.zeros(n)


def mix_in(buf, x, start):
    s = int(start * SR)
    if s >= len(buf):
        return
    e = min(len(buf), s + len(x))
    buf[s:e] += x[: e - s]


SCALES = {"major": [0, 2, 4, 5, 7, 9, 11], "minor": [0, 2, 3, 5, 7, 8, 10], "dorian": [0, 2, 3, 5, 7, 9, 10],
          "mixo": [0, 2, 4, 5, 7, 9, 10], "phryg": [0, 1, 3, 5, 7, 8, 10], "lydian": [0, 2, 4, 6, 7, 9, 11]}
# main theme contour: 1 5 4 2 b3 (scale-degree indices; b3 handled as chromatic)
THEME = [(0, 1.0), (4, 1.0), (3, 1.0), (1, 0.5), ("b3", 1.5), (None, 1.0)]


def degree_note(root, scale, deg, octave=0):
    if deg == "b3":
        return root + 3 + 12 * octave
    sc = SCALES[scale]
    o, d = divmod(deg, 7)
    return root + sc[d] + 12 * (o + octave)


def chord_notes(root, scale, deg, octave=0, seventh=False, sus=False):
    base = [deg, deg + 2, deg + 4] + ([deg + 6] if seventh else [])
    if sus:
        base = [deg, deg + 3, deg + 4]
    return [degree_note(root, scale, d, octave) for d in base]


class Song:
    def __init__(self, cue, bpm, root, scale, bars, meter=4, seed=0):
        self.cue, self.bpm, self.root, self.scale, self.bars, self.meter = cue, bpm, root, scale, bars, meter
        self.beat = 60.0 / bpm
        self.len = bars * meter * self.beat
        self.buf = np.zeros(int(self.len * SR) + SR * 3)
        self.r = np.random.default_rng(seed)

    def note(self, inst, midi, start_beat, beats, gain=1.0):
        x = voice(inst, midi, beats * self.beat * 0.98) * gain
        mix_in(self.buf, x, start_beat * self.beat)

    def hit(self, kind, start_beat, gain=1.0):
        mix_in(self.buf, drum(kind) * gain, start_beat * self.beat)

    def chords(self, prog, inst="pad", octave=-1, beats_per=4, gain=1.0, arp=False, sus_last=False):
        b = 0
        i = 0
        while b < self.bars * self.meter:
            deg = prog[i % len(prog)]
            sus = sus_last and b + beats_per >= self.bars * self.meter
            ns = chord_notes(self.root, self.scale, deg, octave, sus=sus)
            if arp:
                for k in range(beats_per * 2):
                    self.note(inst, ns[k % len(ns)] + (12 if k % 4 == 3 else 0), b + k * 0.5, 0.5, gain)
            else:
                for nn in ns:
                    self.note(inst, nn, b, beats_per, gain / len(ns) * 2)
            b += beats_per
            i += 1

    def bassline(self, prog, pattern, octave=-2, beats_per=4, inst="bass", gain=1.0):
        b = 0
        i = 0
        while b < self.bars * self.meter:
            deg = prog[i % len(prog)]
            for off, dur, step in pattern:
                if off < beats_per:
                    self.note(inst, degree_note(self.root, self.scale, deg + step, octave), b + off, dur, gain)
            b += beats_per
            i += 1

    def melody(self, seq, inst, octave=0, start=0.0, gain=1.0):
        b = start
        for deg, dur in seq:
            if deg is not None:
                self.note(inst, degree_note(self.root, self.scale, deg, octave), b, dur, gain)
            b += dur
        return b

    def gen_phrase(self, bars, prog, contour_bias=0, density=2):
        """Seeded melody following the chord of each bar with stepwise motion."""
        seq = []
        cur = 4
        for bar in range(bars):
            chord_deg = prog[bar % len(prog)]
            tones = [chord_deg % 7, (chord_deg + 2) % 7, (chord_deg + 4) % 7]
            beats = self.meter
            pos = 0.0
            while pos < beats:
                dur = self.r.choice([0.5, 1.0, 1.0, 1.5, 2.0] if density == 2 else [1.0, 2.0, 2.0])
                dur = min(dur, beats - pos)
                if self.r.random() < 0.6:
                    target = min(tones, key=lambda t: abs(t - cur % 7))
                    cur = cur - (cur % 7) + target
                else:
                    cur += self.r.choice([-1, 1, 1, -2, 2]) + contour_bias * 0
                cur = int(np.clip(cur, 0, 11))
                seq.append((cur, dur) if self.r.random() > 0.08 else (None, dur))
                pos += dur
        return seq

    def drums(self, pattern, gain=1.0):
        # pattern: list of (beat_offset, kind) within one bar
        for bar in range(self.bars):
            for off, kind in pattern:
                self.hit(kind, bar * self.meter + off, gain)

    def render(self, loop=True, tail_silence=False):
        x = self.buf[: int(self.len * SR)]
        if loop:
            # fold the reverb/decay tail back into the start so the loop point is seamless
            tail = self.buf[int(self.len * SR): int(self.len * SR) + SR * 2]
            x[: len(tail)] += tail
        peak = np.max(np.abs(x)) + 1e-9
        x = x / peak * 0.8
        # gentle soft clip
        x = np.tanh(x * 1.1) / np.tanh(1.1)
        return x


def write_ogg(x, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    wav = path.replace(".ogg", ".tmp.wav")
    d = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(d.tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "libvorbis", "-q:a", "3", path], check=True)
    os.remove(wav)


def write_wav(x, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    d = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(d.tobytes())


# ---------------------------------------------------------------- cues
def theme_line(s, inst, octave, start, gain=1.0, resolve=False):
    b = start
    for deg, dur in THEME:
        if deg is not None:
            s.note(inst, degree_note(s.root, s.scale, deg, octave) if deg != "b3" else s.root + 3 + 12 * octave, b, dur * 2, gain)
        b += dur * 2
    if resolve:
        s.note(inst, s.root + 12 * octave, b, 4, gain)
    return b


def cue_title(cue="M001", resolve=False):
    s = Song(cue, 66, 50, "minor", 16, seed=1)
    s.chords([0, 5, 3, 4], "strings", -1, 4, 1.0, sus_last=not resolve)
    s.chords([0, 5, 3, 4], "pad", -1, 4, 0.5)
    for k in range(0, 16, 2):
        s.note("bell", s.root + 24 + [0, 7, 5, 3][k // 2 % 4], k * 4, 3, 0.5)
    b = theme_line(s, "reed", 1, 8)
    theme_line(s, "strings", 1, 36, 0.9, resolve=resolve)
    for bar in range(16):
        s.note("bass", s.root - 12, bar * 4, 1.0, 0.6)
    if resolve:
        # completed cadence: V -> I held
        for nn in chord_notes(s.root, "major", 0, 0):
            s.note("strings", nn, 60, 4, 0.6)
    return s.render(loop=not resolve)


def cue_character(cue, root, scale, inst, bpm, seed, lead_bias=0):
    s = Song(cue, bpm, root, scale, 16, seed=seed)
    prog = [[0, 3, 4, 0], [0, 5, 3, 4], [0, 4, 5, 3], [5, 3, 0, 4]][seed % 4]
    s.chords(prog, "pad", -1, 4, 0.6)
    s.bassline(prog, [(0, 1.5, 0), (2, 1, 4), (3, 1, 2)], -2, 4, "bass", 0.6)
    p = s.gen_phrase(8, prog, density=1 if bpm < 90 else 2)
    s.melody(p, inst, 1, 0)
    s.melody(p, inst, 1, 32, 0.9)
    s.melody(s.gen_phrase(8, prog), "pluck", 0, 32, 0.4)
    return s.render()


def cue_town(cue, root, scale, bpm, lead, seed, perc="shaker", extra=None):
    s = Song(cue, bpm, root, scale, 16, seed=seed)
    prog = [[0, 3, 4, 0], [0, 5, 1, 4], [0, 4, 3, 4], [0, 2, 3, 4]][seed % 4]
    s.chords(prog, "pluck", 0, 4, 0.5, arp=True)
    s.chords(prog, "pad", -1, 4, 0.4)
    s.bassline(prog, [(0, 1, 0), (1.5, 0.5, 4), (2, 1, 2), (3, 1, 4)], -2, 4, "bass", 0.55)
    p = s.gen_phrase(8, prog)
    s.melody(p, lead, 1, 0)
    s.melody(s.gen_phrase(8, prog), lead, 1, 32)
    if perc:
        s.drums([(0, perc), (1, perc), (2, perc), (3, perc), (2.5, perc)], 0.8)
    if extra == "bells":
        for bar in range(0, 16, 2):
            s.note("bell", s.root + 24 + 7, bar * 4 + 2, 3, 0.35)
    if extra == "machine":
        s.drums([(0, "tom"), (2.5, "tom")], 0.4)
    if extra == "theme":
        theme_line(s, "reed", 1, 16, 0.7)
    return s.render()


def cue_overworld(cue, root, scale, seed, missing_bass=False):
    s = Song(cue, 104, root, scale, 16, seed=seed)
    prog = [0, 4, 5, 3]
    s.chords(prog, "strings", -1, 4, 0.7)
    if not missing_bass:
        s.bassline(prog, [(0, 1, 0), (1, 0.5, 0), (1.5, 1, 4), (3, 1, 2)], -2, 4, "bass", 0.6)
    else:
        s.bassline(prog, [(0, 2, 0), (3, 1, 4)], -2, 4, "bass", 0.5)
    theme_line(s, "brass" if not missing_bass else "reed", 1, 0, 0.8)
    s.melody(s.gen_phrase(8, prog), "flute", 1, 16)
    theme_line(s, "strings", 1, 48, 0.6)
    s.drums([(0, "kick"), (2, "snare"), (1, "hat"), (3, "hat")], 0.6)
    return s.render()


def cue_dungeon(cue, root, scale, bpm, seed, lead="reed", machine=False, bells=False):
    s = Song(cue, bpm, root, scale, 16, seed=seed)
    prog = [0, 1, 0, 5] if scale in ("phryg", "minor") else [0, 3, 0, 4]
    s.bassline(prog, [(0, 0.5, 0), (0.75, 0.5, 0), (1.5, 0.5, 4), (2.5, 0.5, 0), (3, 0.5, 2)], -2, 4, "bass", 0.6)
    s.chords(prog, "pad", -1, 4, 0.5)
    s.melody(s.gen_phrase(8, prog, density=1), lead, 1, 0, 0.8)
    s.melody(s.gen_phrase(8, prog, density=1), lead, 1, 32, 0.8)
    if machine:
        s.drums([(0, "tom"), (1.5, "tom"), (3, "hat")], 0.5)
    if bells:
        for bar in range(16):
            s.note("bell", s.root + 24 + [0, 3, 7, 10][bar % 4], bar * 4 + 1, 2, 0.3)
    return s.render()


def cue_battle(cue, root, scale, bpm, seed, boss=False):
    s = Song(cue, bpm, root, scale, 16, seed=seed)
    prog = [0, 5, 3, 4] if not boss else [0, 0, 5, 6]
    s.bassline(prog, [(0, 0.5, 0), (0.5, 0.5, 0), (1, 0.5, 7), (1.5, 0.5, 0), (2, 0.5, 4), (2.5, 0.5, 0), (3, 0.5, 2), (3.5, 0.5, 4)], -2, 4, "bass", 0.7)
    s.chords(prog, "brass", 0, 4, 0.55)
    p = s.gen_phrase(8, prog)
    s.melody(p, "strings" if boss else "brass", 1, 0, 0.8)
    s.melody(s.gen_phrase(8, prog), "reed", 1, 32, 0.8)
    s.drums([(0, "kick"), (1, "snare"), (1.5, "kick"), (2, "kick"), (3, "snare"), (0.5, "hat"), (2.5, "hat"), (3.5, "hat")], 0.7)
    if boss:
        for bar in range(16):
            s.note("organ", s.root + 12 + (1 if bar % 4 == 3 else 0), bar * 4, 4, 0.5)
    return s.render()


def cue_story(cue, seed):
    s = Song(cue, 60, 48, "minor", 12, seed=seed)
    s.chords([0, 5, 1, 4], "strings", -1, 4, 0.8)
    theme_line(s, "reed", 1, 4, 0.7)
    # fractured rhythm then silence at the end
    for k in range(10):
        s.hit("tom", 24 + k * 1.3, 0.3 + 0.05 * k)
    x = s.render(loop=False)
    x[-int(SR * 6):] *= np.linspace(1, 0, int(SR * 6)) ** 3
    return x


def cue_stinger(cue):
    s = Song(cue, 120, 60, "major", 4, seed=3)
    for i, d in enumerate([0, 2, 4, 7]):
        s.note("brass", degree_note(60, "major", d, 0), i * 0.5, 0.5, 0.8)
    for nn in chord_notes(60, "major", 0, 0):
        s.note("strings", nn, 2, 6, 0.6)
    s.note("bell", 84, 2, 4, 0.5)
    return s.render(loop=False)


CUES = {}


def build_music():
    CUES["M001"] = lambda: cue_title("M001")
    chars = {"M002": (43, "minor", "brass", 72), "M003": (60, "lydian", "mallet", 112), "M004": (57, "mixo", "flute", 96),
             "M005": (45, "dorian", "mallet", 88), "M006": (52, "dorian", "pluck", 100), "M007": (55, "minor", "reed", 70),
             "M008": (50, "minor", "strings", 84), "M009": (58, "major", "pluck", 120)}
    for i, (cue, (r, sc, inst, bpm)) in enumerate(chars.items()):
        CUES[cue] = (lambda cue=cue, r=r, sc=sc, inst=inst, bpm=bpm, i=i: cue_character(cue, r, sc, inst, bpm, 10 + i))
    towns = {"M010": (55, "major", 96, "reed", None), "M011": (50, "dorian", 92, "brass", None), "M012": (52, "mixo", 84, "mallet", "machine"),
             "M013": (57, "major", 104, "flute", "bells"), "M014": (60, "lydian", 80, "flute", None), "M015": (53, "dorian", 72, "mallet", "bells"),
             "M016": (50, "minor", 78, "reed", "theme")}
    for i, (cue, (r, sc, bpm, lead, ex)) in enumerate(towns.items()):
        CUES[cue] = (lambda cue=cue, r=r, sc=sc, bpm=bpm, lead=lead, ex=ex, i=i: cue_town(cue, r, sc, bpm, lead, 20 + i, "shaker", ex))
    CUES["M017"] = lambda: cue_overworld("M017", 50, "major", 31)
    CUES["M018"] = lambda: cue_overworld("M018", 50, "minor", 31, missing_bass=True)
    CUES["M019"] = lambda: cue_town("M019", 57, "mixo", 110, "flute", 33, "hat", None)
    dungeons = {"M020": (45, "phryg", 84, "reed", True, False), "M021": (52, "dorian", 90, "flute", False, False),
                "M022": (43, "minor", 100, "brass", True, False), "M023": (50, "minor", 76, "reed", False, True),
                "M024": (48, "phryg", 66, "strings", False, True)}
    for i, (cue, (r, sc, bpm, lead, mach, bells)) in enumerate(dungeons.items()):
        CUES[cue] = (lambda cue=cue, r=r, sc=sc, bpm=bpm, lead=lead, mach=mach, bells=bells, i=i: cue_dungeon(cue, r, sc, bpm, 40 + i, lead, mach, bells))
    CUES["M025"] = lambda: cue_battle("M025", 50, "minor", 152, 51)
    CUES["M026"] = lambda: cue_battle("M026", 45, "phryg", 138, 52, boss=True)
    CUES["M027"] = lambda: cue_story("M027", 53)
    CUES["M028"] = lambda: cue_battle("M028", 48, "minor", 132, 54, boss=True)
    CUES["M029"] = lambda: cue_stinger("M029")
    CUES["M030"] = lambda: cue_title("M030", resolve=True)


# ---------------------------------------------------------------- SFX
def sfx_tone(freqs, dur, inst="sine", gain=0.5, gap=0.0):
    out = np.zeros(int(SR * (dur * len(freqs) + gap * len(freqs) + 0.3)))
    for i, f in enumerate(freqs):
        n = int(dur * SR)
        t = np.arange(n) / SR
        if inst == "sine":
            x = np.sin(2 * np.pi * f * t)
        elif inst == "square":
            x = np.sign(np.sin(2 * np.pi * f * t)) * 0.5
        else:
            x = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)
        x *= env(n, 0.005, 0.05, 0.6, dur * 0.5)
        mix_in(out, x * gain, i * (dur + gap))
    return out


def noise(dur, lp=0.3, decay=10, gain=0.5, hp=False):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = rng.standard_normal(n)
    x = lowpass(x, lp)
    if hp:
        x = x - lowpass(x, 0.05)
    return x * np.exp(-t * decay) * gain


def sweep(f0, f1, dur, gain=0.5, kind="sine"):
    n = int(dur * SR)
    f = np.linspace(f0, f1, n)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) if kind == "sine" else np.sign(np.sin(ph)) * 0.5
    return x * env(n, 0.005, 0.05, 0.7, dur * 0.4) * gain


def build_sfx():
    S = {}
    S["FX001"] = sfx_tone([880], 0.03, "sine", 0.3)
    S["FX002"] = sfx_tone([660, 990], 0.04, "sine", 0.35)
    S["FX003"] = sfx_tone([660, 440], 0.04, "sine", 0.3)
    S["FX004"] = sfx_tone([150, 150], 0.06, "square", 0.3, 0.02)
    S["FX005"] = noise(0.12, 0.5, 25, 0.25, hp=True)
    S["FX006"] = sfx_tone([523, 659, 784, 1046], 0.07, "bell", 0.35)
    S["FX007"] = np.concatenate([noise(0.12, 0.1, 12, 0.3), sfx_tone([784, 1175], 0.08, "bell", 0.3)])
    S["FX008"] = np.concatenate([noise(0.08, 0.05, 20, 0.4), sweep(180, 90, 0.2, 0.3)])
    S["FX009"] = noise(0.35, 0.03, 8, 0.6)
    S["FX010"] = np.concatenate([noise(0.04, 0.4, 60, 0.4), sfx_tone([200], 0.05, "square", 0.25)])
    S["FX011"] = noise(0.07, 0.2, 40, 0.25)
    S["FX012"] = noise(0.08, 0.08, 35, 0.3)
    S["FX013"] = noise(0.15, 0.4, 15, 0.2, hp=True)
    S["FX014"] = noise(0.18, 0.6, 16, 0.35, hp=True)
    S["FX015"] = np.concatenate([noise(0.05, 0.3, 50, 0.6), sweep(160, 60, 0.12, 0.4)])
    S["FX016"] = np.concatenate([noise(0.04, 0.5, 60, 0.5), sfx_tone([1200, 900], 0.05, "bell", 0.3)])
    S["FX017"] = sweep(900, 300, 0.12, 0.3)
    S["FX018"] = np.concatenate([noise(0.03, 0.7, 80, 0.5), sfx_tone([400], 0.05, "square", 0.25)])
    S["FX019"] = noise(0.45, 0.15, 5, 0.5) + np.pad(sweep(200, 600, 0.3, 0.2), (0, int(0.15 * SR)))
    S["FX020"] = np.concatenate([sfx_tone([2400, 3100, 1900], 0.04, "bell", 0.35), noise(0.2, 0.7, 14, 0.25, hp=True)])
    S["FX021"] = np.concatenate([noise(0.05, 0.9, 50, 0.7), noise(0.35, 0.2, 7, 0.4)])
    S["FX022"] = sfx_tone([523, 659, 784, 988, 1175], 0.06, "sine", 0.25)
    S["FX023"] = sweep(500, 250, 0.25, 0.3, "square")
    S["FX024"] = sweep(400, 900, 0.2, 0.3)
    S["FX025"] = np.concatenate([sweep(300, 80, 0.3, 0.4), noise(0.2, 0.05, 12, 0.4)])
    S["FX026"] = np.concatenate([sweep(600, 100, 0.25, 0.3, "square"), noise(0.3, 0.3, 9, 0.3)])
    S["FX027"] = sfx_tone([523, 659, 784, 1046, 1318], 0.08, "bell", 0.35)
    S["FX028"] = sfx_tone([784, 988, 1175, 1568], 0.09, "sine", 0.3)
    S["FX029"] = sfx_tone([660, 880, 1320], 0.12, "bell", 0.35)
    S["FX030"] = sweep(120, 900, 0.6, 0.35) + np.pad(noise(0.4, 0.2, 5, 0.2), (0, int(0.2 * SR)))
    S["FX031"] = sfx_tone([392, 392], 0.6, "bell", 0.5, 0.3)
    S["FX032"] = sweep(40, 160, 1.0, 0.5, "square") * 0.6
    return S


def main():
    build_music()
    ledger = []
    only = sys.argv[1:]
    for cue, fn in CUES.items():
        if only and cue not in only and "music" not in only:
            continue
        x = fn()
        path = os.path.join(OUT, "music", cue + ".ogg")
        write_ogg(x, path)
        ledger.append({"id": cue, "path": "game/assets/audio/music/%s.ogg" % cue, "seconds": round(len(x) / SR, 1),
                       "source": "tools/gen_audio.py (programmatic synthesis)", "license": "original", "status": "generated (development-grade)"})
        print("music", cue, round(len(x) / SR, 1), "s")
    if not only or "sfx" in only:
        for fx, x in build_sfx().items():
            x = x / (np.max(np.abs(x)) + 1e-9) * 0.7
            write_wav(x, os.path.join(OUT, "sfx", fx + ".wav"))
            ledger.append({"id": fx, "path": "game/assets/audio/sfx/%s.wav" % fx, "seconds": round(len(x) / SR, 2),
                           "source": "tools/gen_audio.py", "license": "original", "status": "generated (development-grade)"})
    os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
    lp = os.path.join(ROOT, "reports", "audio_ledger.json")
    old = json.load(open(lp)) if os.path.exists(lp) else []
    ids = {e["id"] for e in ledger}
    json.dump(sorted([e for e in old if e["id"] not in ids] + ledger, key=lambda e: e["id"]), open(lp, "w"), indent=1)


if __name__ == "__main__":
    main()
