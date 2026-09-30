"""Localization extraction (sys s4).

Dumps every player-visible line of the story (content_src/scenes/*.scn), the map texts (signs, plaques, locked-door
messages, NPC names from content_src/maps/*.map) and the UI string table (game/content/strings/en.json) to CSV
templates for translators. The game itself is English-only; this makes it localization-ready without touching the
story files.

Keys are stable: they depend on the scene id, the command, the speaker and the English text, never on line numbers,
so inserting or moving lines elsewhere does not rename existing keys.
  scene line    scn.<SCENE>.<cmd>.<hash8>            say / doc / objective / journal / rumor
  choice option scn.<SCENE>.choice.<hash8>.<n>
  map text      map.<MAP>.<type>.<x>_<y>             sign / read text, door locked messages, NPC names
  UI string     the en.json key (menu.Items, set.text_size, ...)
<hash8> = first 8 hex digits of sha1("<speaker>|<text>"); a repeated identical line in one scene gets a "~2" suffix.
Mature markup `{m:strong|mild}` is kept verbatim in the source column (translate both halves), and the mild and
strong renderings are added as reference columns.

Output (default build/l10n/): scenes_en.csv, maps_en.csv, ui_en.csv with columns
  key, context, speaker, source, mild, strong, notes
Usage:
  python3 tools/l10n/extract.py [--out DIR]      write the templates
  python3 tools/l10n/extract.py --check          only verify keys are unique (exit 1 on a clash)
A translation is added later as game/content/strings/<lang>.json (UI) plus a scene table the lead can load the same
way (T.set_lang); the CSV keys are what such tables are indexed by.
"""
import csv, glob, hashlib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEXT_CMDS = ("say", "doc", "objective", "journal", "rumor")
MARK = re.compile(r"\{m:([^{}|]*)\|([^{}]*)\}")


def h8(speaker, text):
    return hashlib.sha1(("%s|%s" % (speaker, text)).encode("utf-8")).hexdigest()[:8]


def render(t, strong):
    return re.sub(r"\s{2,}", " ", MARK.sub(lambda m: m.group(1) if strong else m.group(2), t)).strip()


def scenes():
    rows = []
    for fp in sorted(glob.glob(os.path.join(ROOT, "content_src", "scenes", "*.scn"))):
        cur = None
        seen = {}
        for n, raw in enumerate(open(fp, encoding="utf-8").read().split("\n"), 1):
            ln = raw.strip()
            if ln.startswith("@scene"):
                cur = ln.split()[1]
                seen = {}
                continue
            if ln == "@end" or cur is None or ln.startswith("#") or "|" not in ln:
                continue
            head = ln.split("|")[0].split()
            if not head:
                continue
            cmd = head[0]
            ctx = "%s:%d %s" % (os.path.basename(fp), n, cur)
            if cmd == "choice":
                opts = [o.strip() for o in ln.split("|")[1:]]
                base = h8("choice", "|".join(opts))
                for i, o in enumerate(opts):
                    label = o.partition("->")[0].strip()
                    rows.append({"key": "scn.%s.choice.%s.%d" % (cur, base, i + 1), "context": ctx, "speaker": "",
                                 "source": label, "mild": render(label, False), "strong": render(label, True), "notes": "choice option"})
                continue
            if cmd not in TEXT_CMDS:
                continue
            spk = head[1] if cmd == "say" and len(head) > 1 else (head[1] if len(head) > 1 else "")
            text = ln.partition("|")[2].strip()
            k = "scn.%s.%s.%s" % (cur, cmd, h8(spk, text))
            seen[k] = seen.get(k, 0) + 1
            if seen[k] > 1:
                k += "~%d" % seen[k]
            notes = "mature markup" if "{m:" in text else ""
            rows.append({"key": k, "context": ctx, "speaker": spk, "source": text, "mild": render(text, False),
                         "strong": render(text, True) if "{m:" in text else "", "notes": notes})
    return rows


def maps():
    """Map texts. A map id defined in several files (older layouts later replaced) keeps its last definition, as
    tools/compile_content.py does."""
    rows = {}
    for fp in sorted(glob.glob(os.path.join(ROOT, "content_src", "maps", "*.map"))):
        mid = None
        for n, raw in enumerate(open(fp, encoding="utf-8").read().split("\n"), 1):
            if raw.startswith("=== "):
                mid = raw[4:].strip()
                continue
            ln = raw.split("#!")[0].strip()
            if mid is None or not ln:
                continue
            if ln.startswith("name:"):
                add(rows, {"key": "map.%s.name" % mid, "context": "%s:%d" % (os.path.basename(fp), n), "speaker": "",
                             "source": ln[5:].strip(), "mild": "", "strong": "", "notes": "map name"})
                continue
            t = ln.split()
            if t[0] in ("sign", "read") and len(t) > 3:
                text = re.search(r'"(.*)"', ln)
                if text:
                    add(rows, {"key": "map.%s.%s.%s_%s" % (mid, t[0], t[1], t[2]), "context": "%s:%d" % (os.path.basename(fp), n),
                                 "speaker": "", "source": text.group(1), "mild": "", "strong": "", "notes": t[0]})
            for kv in ("locked", "msg", "name"):
                m = re.search(kv + r'="([^"]*)"', ln)
                if m and t[0] in ("door", "exit", "npc", "block", "location"):
                    pos = "%s_%s" % (t[1], t[2]) if t[0] != "npc" else t[1]
                    add(rows, {"key": "map.%s.%s.%s.%s" % (mid, t[0], pos, kv), "context": "%s:%d" % (os.path.basename(fp), n),
                                 "speaker": "", "source": m.group(1), "mild": "", "strong": "", "notes": "%s %s" % (t[0], kv)})
    return list(rows.values())


def add(rows, r):
    rows[r["key"]] = r


def ui():
    d = json.load(open(os.path.join(ROOT, "game", "content", "strings", "en.json"), encoding="utf-8"))
    return [{"key": k, "context": "strings/en.json", "speaker": "", "source": v, "mild": "", "strong": "", "notes": ""}
            for k, v in d.items() if not k.startswith("_")]


def main():
    out = os.path.join(ROOT, "build", "l10n")
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
    sets = {"scenes_en.csv": scenes(), "maps_en.csv": maps(), "ui_en.csv": ui()}
    bad = 0
    for name, rows in sets.items():
        keys = [r["key"] for r in rows]
        dup = {k for k in keys if keys.count(k) > 1} if len(keys) < 5000 else {k for k, c in __import__("collections").Counter(keys).items() if c > 1}
        for k in sorted(dup):
            print("DUPLICATE KEY", name, k)
            bad += 1
    if "--check" not in sys.argv:
        os.makedirs(out, exist_ok=True)
        for name, rows in sets.items():
            with open(os.path.join(out, name), "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=["key", "context", "speaker", "source", "mild", "strong", "notes"])
                w.writeheader()
                w.writerows(rows)
    print("l10n extract:", ", ".join("%s %d" % (k, len(v)) for k, v in sets.items()), "->", out if "--check" not in sys.argv else "(check)",
          "OK" if not bad else "%d duplicate keys" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
