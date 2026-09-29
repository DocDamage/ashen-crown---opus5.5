"""Report ragged map rows (authoring aid)."""
import glob, re, sys
bad = 0
for fp in sorted(glob.glob("content_src/maps/*.map")):
    for block in re.split(r"^=== ", open(fp).read(), flags=re.M)[1:]:
        lines = block.split("\n"); mid = lines[0].strip()
        g = []; on = False
        for ln in lines[1:]:
            if ln.strip() == "grid:": on = True; continue
            if ln.startswith("entities:"): break
            if on and ln.strip(): g.append(ln)
        ws = [len(r) for r in g]
        if len(set(ws)) > 1:
            bad += 1
            print(mid, "widths", ws)
print("ragged maps:", bad)
