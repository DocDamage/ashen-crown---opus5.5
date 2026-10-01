"""Remove maps' auto-dressed copies from content_src/maps/z48_auto.map so the compiler uses their (rebuilt) sources.
The lead re-runs tools/maps48/autoskin.py for them on the owner's PC afterwards. Usage: python3 tools/maps/undress.py ID ..."""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, "content_src", "maps", "z48_auto.map")
txt = open(p).read()
parts = re.split(r"^(?==== )", txt, flags=re.M)
keep = [parts[0]]
drop = set(sys.argv[1:])
n = 0
for s in parts[1:]:
    mid = s.split("\n", 1)[0][4:].strip()
    if mid in drop:
        n += 1
        continue
    keep.append(s)
open(p, "w").write("".join(keep))
print("undressed", n, "maps")
