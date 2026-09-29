"""Coordinate-based authoring kit that emits content_src/maps/*.map blocks.
Rooms are still hand-designed; the kit only removes row-counting errors."""
import math, random


class Grid:
    def __init__(self, w, h, fill="#"):
        self.w, self.h = w, h
        self.g = [[fill] * w for _ in range(h)]
        self.ents = []

    def put(self, x, y, ch):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.g[y][x] = ch

    def get(self, x, y):
        return self.g[y][x] if 0 <= x < self.w and 0 <= y < self.h else "#"

    def rect(self, x0, y0, x1, y1, ch):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.put(x, y, ch)
        return self

    def box(self, x0, y0, x1, y1, ch):
        for x in range(x0, x1 + 1):
            self.put(x, y0, ch); self.put(x, y1, ch)
        for y in range(y0, y1 + 1):
            self.put(x0, y, ch); self.put(x1, y, ch)
        return self

    def hline(self, y, x0, x1, ch):
        return self.rect(min(x0, x1), y, max(x0, x1), y, ch)

    def vline(self, x, y0, y1, ch):
        return self.rect(x, min(y0, y1), x, max(y0, y1), ch)

    def blob(self, cx, cy, rx, ry, ch, only=None):
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if ((x - cx) / (rx + 0.4)) ** 2 + ((y - cy) / (ry + 0.4)) ** 2 <= 1:
                    if only is None or self.get(x, y) in only:
                        self.put(x, y, ch)
        return self

    def path(self, pts, ch, width=1):
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if x0 == x1:
                self.rect(x0, min(y0, y1), x0 + width - 1, max(y0, y1), ch)
            else:
                self.rect(min(x0, x1), y0, max(x0, x1), y0 + width - 1, ch)
        return self

    def text(self, x, y, rows):
        for dy, r in enumerate(rows.split("\n") if isinstance(rows, str) else rows):
            for dx, ch in enumerate(r):
                if ch != " ":
                    self.put(x + dx, y + dy, ch)
        return self

    def scatter(self, ch, prob, only, seed, area=None):
        r = random.Random(seed)
        x0, y0, x1, y1 = area or (0, 0, self.w - 1, self.h - 1)
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if self.get(x, y) in only and r.random() < prob:
                    self.put(x, y, ch)
        return self

    def _entity_tiles(self):
        pts = set()
        for line in self.ents:
            toks = line.split()
            nums = []
            for t in toks[1:]:
                if ".." in t:
                    a, b = t.split("..")
                    if a.isdigit() and b.isdigit():
                        nums.append((int(a), int(b)))
                        continue
                if t.isdigit():
                    nums.append((int(t), int(t)))
                else:
                    if len(nums) >= 2:
                        break
                    nums = []
            if len(nums) >= 2:
                (x0, x1), (y0, y1) = nums[0], nums[1]
                for y in range(y0 - 1, y1 + 2):
                    for x in range(x0 - 1, x1 + 2):
                        pts.add((x, y))
        return pts

    def decorate(self, chars, count, seed, only, area=None):
        """Scatter solid decorations only in open interiors (all 8 neighbours walkable 'only' tiles) and away
        from entities, so corridors and interaction points are never blocked."""
        r = random.Random(seed)
        x0, y0, x1, y1 = area or (1, 1, self.w - 2, self.h - 2)
        busy = self._entity_tiles()
        cells = [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)]
        r.shuffle(cells)
        placed = 0
        for (x, y) in cells:
            if placed >= count:
                break
            if (x, y) in busy or self.get(x, y) not in only:
                continue
            if not all(self.get(x + dx, y + dy) in only for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                continue
            self.put(x, y, r.choice(chars))
            placed += 1
        return self

    def house(self, x, y, w, door_dx, roof_h=2, windows=True, chimney=None):
        self.rect(x, y, x + w - 1, y + roof_h - 1, "R")
        for i in range(w):
            self.put(x + i, y + roof_h, "Q" if windows and i % 2 == 1 else "W")
        if door_dx >= 0:
            self.put(x + door_dx, y + roof_h, "D")
        if chimney is not None:
            self.put(x + chimney, y, "4")
        return (x + door_dx, y + roof_h)

    def e(self, line):
        self.ents.append(line)
        return self

    def emit(self, mid, **props):
        out = [f"=== {mid}"]
        legend = props.pop("legend", None)
        for k, v in props.items():
            out.append(f"{k}: {v}")
        if legend:
            out.append("legend: " + " ".join(f"{k}={v}" for k, v in legend.items()))
        out.append("grid:")
        out.extend("".join(r) for r in self.g)
        out.append("entities:")
        out.extend(self.ents)
        return "\n".join(out) + "\n"


def write(path, blocks, header=""):
    with open(path, "w", encoding="utf-8") as f:
        if header:
            f.write("#! " + header + "\n")
        f.write("\n".join(blocks))
