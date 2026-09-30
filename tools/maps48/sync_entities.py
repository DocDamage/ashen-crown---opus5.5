"""Keep auto-dressed map copies in step with their sources.

autoskin.py writes content_src/maps/z48_auto.map: each map's ORIGINAL header and entities with the dressed grid.
When a source map's header or entity lines are edited later, run this to copy them into the z48_auto copy (the
dressed grid is kept; grid size must not change - if it did, re-run autoskin for that map on the owner's PC).
Usage: python3 tools/maps48/sync_entities.py [--check]"""
import os, re, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
MAPS = os.path.join(REPO, "content_src", "maps")


def split_sections(text):
    parts = re.split(r"^(?==== )", text, flags=re.M)
    head, secs = parts[0], []
    for p in parts[1:]:
        secs.append((p.split("\n", 1)[0][4:].strip(), p))
    return head, secs


def parts_of(sec):
    """-> (header lines, legend line or None, grid lines, entity lines)"""
    lines = sec.rstrip("\n").split("\n")[1:]
    hdr, legend, grid, ents, mode = [], None, [], [], "hdr"
    for ln in lines:
        s = ln.strip()
        if mode == "hdr":
            if s.startswith("legend:"):
                legend = ln
            elif s == "grid:":
                mode = "grid"
            else:
                hdr.append(ln)
        elif mode == "grid":
            if s.startswith("entities:"):
                mode = "ent"
            else:
                grid.append(ln)
        else:
            ents.append(ln)
    return hdr, legend, grid, ents


def main():
    check = "--check" in sys.argv
    src = {}
    for p in sorted(glob.glob(os.path.join(MAPS, "*.map"))):
        if os.path.basename(p).startswith("z48_"):
            continue
        for mid, sec in split_sections(open(p, encoding="utf-8").read())[1]:
            src[mid] = sec
    ap = os.path.join(MAPS, "z48_auto.map")
    head, secs = split_sections(open(ap, encoding="utf-8").read())
    out, changed = [], []
    for mid, sec in secs:
        if mid not in src:
            out.append(sec)
            continue
        h1, lg1, g1, e1 = parts_of(sec)
        h0, lg0, g0, e0 = parts_of(src[mid])
        if h0 == h1 and e0 == e1:
            out.append(sec)
            continue
        if len(g0) != len(g1) or (g0 and g1 and len(g0[0].rstrip()) != len(g1[0].rstrip())):
            print("SIZE CHANGED (re-run autoskin):", mid)
            out.append(sec)
            continue
        lines = ["=== " + mid] + h0 + ([lg1] if lg1 else []) + ["grid:"] + g1 + ["entities:"] + e0
        out.append("\n".join(lines).rstrip("\n") + "\n\n" if sec.endswith("\n\n") else "\n".join(lines) + "\n")
        changed.append(mid)
    if changed and not check:
        open(ap, "w", encoding="utf-8").write(head + "".join(out))
    print(("would sync" if check else "synced"), len(changed), "maps:", " ".join(changed[:30]) + (" ..." if len(changed) > 30 else ""))


if __name__ == "__main__":
    main()
