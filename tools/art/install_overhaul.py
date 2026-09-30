"""Installs processed overhaul art from Assets/_processed into game/assets/ext (git-ignored, licensed art).
Run after tools/art/hero_import.py. Each section is idempotent (copies only when the source is newer).
Usage: python tools/art/install_overhaul.py [section ...]   sections: arenas
"""
import os, shutil, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ASSETS = os.environ.get("ASHEN_ASSETS", os.path.join(os.path.dirname(REPO), "Assets"))
PROC = os.path.join(ASSETS, "_processed")
EXT = os.path.join(REPO, "game", "assets", "ext")

# battle backdrop key (formation "bg") -> arena number (Assets/_processed/battle_backgrounds/arena_NN_px.png)
ARENAS = {
    "quarry": 62, "archive": 28, "conduit": 45, "crown": 48, "crown_core": 2, "dais": 47, "field_post": 71,
    "field_r01": 49, "field_r02": 50, "field_r03": 34, "field_r04": 40, "field_r05": 17, "furnace": 33, "grove": 26,
    "grove_flood": 19, "reef": 11, "sky": 7, "underways": 36, "vault": 42, "whitebone": 15, "winter": 54,
    "deck": "deck",
}


def copy(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
        shutil.copy2(src, dst)
        return 1
    return 0


def arenas():
    n = 0
    for key, num in ARENAS.items():
        if num == "deck":
            src = os.path.join(PROC, "airships", "deck", "deck_battle_px.png")
        else:
            src = os.path.join(PROC, "battle_backgrounds", "arena_%02d_px.png" % num)
        if os.path.exists(src):
            n += copy(src, os.path.join(EXT, "battle_bg", key + ".png"))
    print("arenas:", n, "copied")


# ---------------------------------------------------------------- audio
# Music cues (content "music" ids) -> soundtrack files (owner's casting, brief decision 58; standard section 10).
MUSIC = {
    "M001": ("Echoes Below", "1. MAIN THEME"), "M002": ("Crimson Nocturne", "1. MAIN THEME"),
    "M003": ("Arcane Chronicles", "1. MAIN THEME"), "M004": ("Frozen Echoes", "1. MAIN THEME"),
    "M005": ("Echoes Below", "12. PUZZLE ROOM"), "M006": ("Echoes Below", "5. FOREST AREA"),
    "M007": ("Astral Horizons", "7. ANCIENT TEMPLE"), "M008": ("Sakura no Yume", "12. MINI BOSS"),
    "M009": ("Echoes Below", "10. FUNNY NPC"), "M010": ("Echoes Below", "3. PEACEFUL TOWN"),
    "M011": ("Echoes Below", "4. PEACEFUL TOWN 2"), "M012": ("Arcane Chronicles", "5. ALCHEMY ROOM"),
    "M013": ("DARK PIRATE", "3. PORT TOWN"), "M014": ("Frozen Echoes", "3. SNOW VILLAGE"),
    "M015": ("Sands of Eternity", "3. DESERT TOWN"), "M016": ("Frozen Echoes", "10. SHOP THEME"),
    "M017": ("DARK PIRATE", "5. OPEN SEA"), "M018": ("Arcane Chronicles", "16. SAD MEMORY"),
    "M019": ("Neon Reverie", "7. SKY TRAIN"), "M020": ("Echoes Below", "9. RUINS THEME"),
    "M021": ("Arcane Chronicles", "7. FOREST OF SPELLS"), "M022": ("Crimson Nocturne", "14. FINAL DUNGEON"),
    "M023": ("Echoes Below", "8. WATER AREA"), "M024": ("Arcane Chronicles", "8. SECRET CHAMBER"),
    "M025": ("Echoes Below", "14. BATTLE THEME"), "M026": ("Echoes Below", "15. MINI BOSS"),
    "M027": ("Crimson Nocturne", "15. FINAL BOSS"), "M028": ("Echoes Below", "17. FINAL BOSS"),
    "M029": ("Echoes Below", "3. PEACEFUL TOWN"), "M030": ("Echoes Below", "18. TRUE ENDING"),
    # overhaul cues: regional battles and places (used by formations and maps from the overhaul on)
    "M101": ("DARK PIRATE", "11. BATTLE THEME"), "M102": ("Frozen Echoes", "11. BATTLE THEME"),
    "M103": ("Sands of Eternity", "11. BATTLE THEME"), "M104": ("Neon Reverie", "12. BATTLE THEME"),
    "M105": ("Sakura no Yume", "11. BATTLE THEME"), "M106": ("Crimson Nocturne", "11. BATTLE THEME"),
    "M107": ("Arcane Chronicles", "11. BATTLE THEME"), "M108": ("Echoes Below", "11. SHOP THEME"),
    "M109": ("Neon Reverie", "14. SECRET AREA"), "M110": ("Midnight Velocity", "5. HIGHWAY CRUISE"),
    "M111": ("Sakura no Yume", "4. SHRINE THEME"), "M112": ("Sakura no Yume", "3. BAMBOO FOREST"),
    "M113": ("Frozen Echoes", "7. ICE CAVE"), "M114": ("Sands of Eternity", "7. ANCIENT RUINS"),
    "M115": ("DARK PIRATE", "7. GHOST SHIP"), "M116": ("Crimson Nocturne", "3. CASTLE COURTYARD"),
    "M117": ("Crimson Nocturne", "5. HAUNTED HALLWAY"), "M118": ("Astral Horizons", "5. OPEN SPACE"),
    "M119": ("Echoes Below", "16. FINAL DUNGEON"), "M120": ("Arcane Chronicles", "3. MAGIC ACADEMY"),
    "M121": ("Sands of Eternity", "5. OPEN DESERT"), "M122": ("Frozen Echoes", "5. FROZEN PLAINS"),
    "M123": ("Echoes Below", "6. SNOW AREA"), "M124": ("Echoes Below", "7. DESERT AREA"),
    "M125": ("Neon Reverie", "15. FINAL DUNGEON"), "M126": ("Echoes Below", "13. SECRET AREA"),
}
# Jingles (Assets/Fanfare, 3.7-6.6 s each). Owner can swap numbers here.
JINGLES = {"victory": 9, "level_up": 17, "item": 11, "inn": 6, "save": 7, "join": 1, "quest": 3, "game_over": 20, "rare": 2}
# Sound cues (content "sfx" ids plus overhaul cues FX040+) -> library files (first glob match).
SFX = {
    "FX001": "Fantasy UI*/**/click_select_01.wav", "FX002": "Fantasy UI*/**/confirm_accept_01.wav",
    "FX003": "Fantasy UI*/**/cancel_back_01.wav", "FX004": "game_item/Inventory/ErrorInvalidActio1.mp3",
    "FX005": "Kenney RPG Audio/Audio/bookFlip1.ogg", "FX006": "Fantasy UI*/**/magic_ui_03.wav",
    "FX007": "Kenney RPG Audio/Audio/creak1.ogg", "FX008": "Kenney RPG Audio/Audio/doorOpen_1.ogg",
    "FX009": "Kenney Foley Sounds/Audio/Rocks/stoneDrag1.ogg", "FX010": "Kenney RPG Audio/Audio/metalLatch.ogg",
    "FX011": "Kenney RPG Audio/Audio/footstep00.ogg", "FX012": "Kenney RPG Audio/Audio/footstep05.ogg",
    "FX013": "Kenney Foley Sounds/Audio/Water/drip1.ogg", "FX014": "Pixel_Combat*/**/sword_slash_light_v*.wav",
    "FX015": "Pixel_Combat*/**/hit_creature_soft_v*.wav", "FX016": "Pixel_Combat*/**/shield_block_heavy_v*.wav",
    "FX017": "Pixel_Combat*/**/bow_shot_light_v*.wav", "FX018": "Pixel_Combat*/**/bow_shot_heavy_v*.wav",
    "FX019": "Pixel_Combat*/**/fire_cast_v*.wav", "FX020": "Pixel_Combat*/**/ice_shatter_v*.wav",
    "FX021": "Pixel_Combat*/**/lightning_impact_v*.wav", "FX022": "Pixel_Combat*/**/heal_v*.wav",
    "FX023": "Pixel_Combat*/**/debuff_stun_v*.wav", "FX024": "Fantasy UI*/**/magic_ui_05.wav",
    "FX025": "Pixel_Combat*/**/player_death_v*.wav", "FX026": "Pixel_Combat*/**/enemy_death_small_v*.wav",
    "FX027": "Fantasy UI*/**/rare_special_01.wav", "FX028": "Fantasy UI*/**/quest_notification_01.wav",
    "FX029": "Fantasy UI*/**/rare_special_03.wav", "FX030": "Pixel_Combat*/**/magic_ultimate_v*.wav",
    "FX031": "Fantasy UI*/**/quest_notification_05.wav", "FX032": "Kenney Foley Sounds/Audio/Woosh/woosh3.ogg",
    "FX040": "Pixel_Combat*/**/holy_cast_v*.wav", "FX041": "Pixel_Combat*/**/dark_cast_v*.wav",
    "FX042": "Pixel_Combat*/**/ice_cast_v*.wav", "FX043": "Pixel_Combat*/**/lightning_cast_v*.wav",
    "FX044": "Pixel_Combat*/**/battle_start_v*.wav", "FX045": "Pixel_Combat*/**/attack_miss_v*.wav",
    "FX046": "Pixel_Combat*/**/buff_defense_v*.wav", "FX047": "Kenney Foley Sounds/Audio/Woosh/woosh5.ogg",
    "FX048": "Kenney Foley Sounds/Audio/Rocks/stonesHit1.ogg", "FX049": "Kenney Foley Sounds/Audio/Water/sinkWater1.ogg",
    "FX050": "Pixel_Combat*/**/dark_impact_v*.wav", "FX051": "Pixel_Combat*/**/arcane_impact_v*.wav",
    "FX052": "Pixel_Combat*/**/fireball_impact_v*.wav", "FX053": "Pixel_Combat*/**/sword_critical_hit_v*.wav",
    "FX054": "Pixel_Combat*/**/blunt_critical_hit_v*.wav", "FX055": "Pixel_Combat*/**/arrow_hit_flesh_v*.wav",
    "FX056": "Kenney RPG Audio/Audio/handleCoins.ogg", "FX057": "game_item/Equip/PotionDrinkGulps9.mp3",
}


def ffmpeg(src, dst, extra=()):
    import subprocess
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
        return 0
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, *extra, "-c:a", "libvorbis", "-q:a", "5", dst], check=True)
    return 1


def audio():
    import glob as G
    snd = os.path.join(ASSETS, "Soundtrack")
    tracks = G.glob(os.path.join(snd, "**", "*.mp3"), recursive=True)
    n = 0
    for cue, (pack, prefix) in MUSIC.items():
        hits = [t for t in tracks if pack.lower() in t.lower() and os.path.basename(t).startswith(prefix)]
        if not hits:
            print("music: no track for", cue, pack, prefix)
            continue
        n += copy(sorted(hits)[0], os.path.join(EXT, "audio", "music", cue + ".mp3"))
    print("music:", n, "copied")
    n = 0
    for name, num in JINGLES.items():
        n += ffmpeg(os.path.join(ASSETS, "Fanfare", "FANFARE %d.wav" % num), os.path.join(EXT, "audio", "jingle", name + ".ogg"))
    print("jingles:", n, "converted")
    n = 0
    sroot = os.path.join(ASSETS, "SFX")
    for cue, pat in SFX.items():
        hits = sorted(G.glob(os.path.join(sroot, pat), recursive=True))
        if not hits:
            print("sfx: no file for", cue, pat)
            continue
        n += ffmpeg(hits[0], os.path.join(EXT, "audio", "sfx", cue + ".ogg"), ("-ac", "2", "-ar", "44100"))
    print("sfx:", n, "converted")
    json.dump({"music": {k: list(v) for k, v in MUSIC.items()}, "jingles": JINGLES, "sfx": SFX},
              open(os.path.join(EXT, "audio", "audio_map.json"), "w"), indent=1)


# ---------------------------------------------------------------- vfx
ELEM_FX = {"fire": "fire", "ice": "ice", "storm": "storm", "earth": "earth", "water": "water", "light": "holy",
           "shadow": "shadow", "poison": "poison", "arcane": "arcane"}


def vfx():
    import glob as G, re
    src = os.path.join(PROC, "vfx")
    out = os.path.join(EXT, "vfx")
    effects = {}
    n = 0
    for sub in ("spell-fx", "buff-fx"):
        meta = json.load(open(os.path.join(src, sub, "effects.json")))["effects"]
        for e in meta:
            f = os.path.join(src, sub, e["file"])
            if not os.path.exists(f):
                continue
            n += copy(f, os.path.join(out, e["name"] + ".png"))
            from PIL import Image
            w, h = Image.open(f).size
            effects[e["name"]] = {"frames": e["frames"], "fps": e["fps"], "loop": e["loop"], "cols": e["columns"],
                                  "rows": e["rows"], "cell": [w // e["columns"], h // e["rows"]], "anchor": e["anchor"],
                                  "shape": e["shape"]}
    fxmap = json.load(open(os.path.join(src, "fx_map.json")))
    content = json.load(open(os.path.join(REPO, "game", "content", "content.json"), encoding="utf-8"))
    status_fx = {k: v.split(" ")[0] for k, v in fxmap["statuses"].items()}
    explicit = {}
    for k, steps in fxmap["spells"].items():
        m = re.match(r"(S\d+)", k)
        if m:
            explicit[m.group(1)] = steps
    abil = {}
    for aid, a in content["abilities"].items():
        elem = ELEM_FX.get(a.get("element", "none"), "")
        aoe = a.get("target", "").endswith("_all")
        if aid in explicit:
            steps = [x.split(" ")[0] for x in explicit[aid]]
            steps = [x for x in steps if x in effects]
            if not steps:
                continue
            cast = [x for x in steps if x.endswith("_cast")]
            bolt = [x for x in steps if x.endswith("_bolt")]
            hit = [x for x in steps if not x.endswith("_cast") and not x.endswith("_bolt")] or steps[-1:]
            abil[aid] = {"cast": cast, "bolt": bolt[0] if bolt else "", "hit": hit, "mode": "center" if any(h.endswith(("_area", "_nova")) for h in hit) and aoe else "each"}
            continue
        kind = a.get("kind", "")
        fam = a.get("family", "")
        hit, cast = [], []
        if kind == "summon":
            hit = [(elem or "arcane") + "_nova"]
        elif kind == "heal":
            cast, hit = ["holy_cast"], ["green_heal"]
        elif kind == "revive":
            cast, hit = ["holy_cast"], ["gold_levelup"]
        elif kind == "physical":
            hit = [elem + "_impact"] if elem else ["white_shine"]
        elif kind == "magical":
            cast = [(elem or "arcane") + "_cast"]
            hit = [(elem or "arcane") + ("_area" if aoe else "_impact")]
        else:
            sts = [o["id"] for o in a.get("ops", []) if o.get("op") == "status"]
            hit = [status_fx[sts[0]]] if sts and sts[0] in status_fx else (["arcane_rune"] if fam == "spell" else ["white_shine"])
            if fam == "spell":
                cast = ["arcane_cast"]
        hit = [h for h in hit if h in effects]
        cast = [c for c in cast if c in effects]
        abil[aid] = {"cast": cast, "bolt": "", "hit": hit, "mode": "center" if aoe and hit and hit[0].endswith(("_area", "_nova")) else "each"}
    json.dump({"effects": effects, "abilities": abil, "statuses": {k: v for k, v in status_fx.items() if v in effects},
               "attack": "white_shine", "events": {"heal": "green_heal", "revive": "gold_levelup", "level_up": "gold_levelup",
               "save": "blue_beam", "concord": "gold_powerup"}},
              open(os.path.join(out, "fx.json"), "w"), indent=1)
    print("vfx:", n, "sheets,", len(effects), "effects,", len(abil), "abilities mapped")


# ---------------------------------------------------------------- vestiges
VESTIGE_KEYS = {"V01": "moth", "V02": "stag", "V03": "whale", "V04": "manta", "V05": "fox", "V06": "tortoise",
                "V07": "hind", "V08": "leviathan", "V09": "colossus", "V10": "thorn", "V11": "wyrm", "V12": "wraith"}


def vestiges():
    import glob as G
    import numpy as np
    from PIL import Image
    src = os.path.join(PROC, "vestiges")
    n = 0
    for vid, key in VESTIGE_KEYS.items():
        hits = G.glob(os.path.join(src, vid + "_*.json"))
        if not hits:
            print("vestige missing", vid)
            continue
        base = hits[0][:-5]
        n += copy(base + ".png", os.path.join(EXT, "vestiges", vid + ".png"))
        meta = json.load(open(base + ".json"))
        fr = meta["frames"]
        tags = {t["name"]: [t["from"], t["to"]] for t in meta["meta"]["frameTags"]}
        info = {"cell": [fr[0]["frame"]["w"], fr[0]["frame"]["h"]], "frames": [[f["frame"]["x"], f["frame"]["y"]] for f in fr],
                "durations": [f["duration"] for f in fr], "tags": tags}
        json.dump(info, open(os.path.join(EXT, "vestiges", vid + ".json"), "w"))
        # portrait: 120x120 native crop around the head (top of the idle pose)
        sheet = Image.open(base + ".png").convert("RGBA")
        i0 = tags.get("idle", [0, 0])[0]
        x, y = fr[i0]["frame"]["x"], fr[i0]["frame"]["y"]
        cell = sheet.crop((x, y, x + fr[i0]["frame"]["w"], y + fr[i0]["frame"]["h"]))
        a = np.array(cell)[..., 3]
        ys, xs = np.nonzero(a > 0)
        top = ys.min()
        row = np.nonzero(a[min(top + 30, a.shape[0] - 1)] > 0)[0]
        cx = int(row.mean()) if len(row) else int(xs.mean())
        side = 120
        box = (max(0, cx - side // 2), max(0, top - 6), max(0, cx - side // 2) + side, max(0, top - 6) + side)
        os.makedirs(os.path.join(EXT, "portraits"), exist_ok=True)
        cell.crop(box).save(os.path.join(EXT, "portraits", key + ".png"))
    print("vestiges:", n, "sheets")


# ---------------------------------------------------------------- spell icons
ELEM_ICON = {"fire": "Fire", "ice": "Water", "water": "Water", "storm": "Air", "light": "Light", "shadow": "Dark",
             "earth": "Fire", "none": "Light", "physical": "Air", "poison": "Dark"}


def spell_icons():
    """One 64px icon per ability from Assets/VFX/spell-fx/Spells (owner's map first, then by element), reduced to 32px
    by 2x2 box averaging (done once here) for menu lines; 64px kept for the battle command window."""
    from PIL import Image
    base = os.path.join(ASSETS, "VFX", "spell-fx", "Spells")
    imap = json.load(open(os.path.join(base, "spell_icon_map.json")))
    content = json.load(open(os.path.join(REPO, "game", "content", "content.json"), encoding="utf-8"))
    pools = {e: sorted(os.listdir(os.path.join(base, e))) for e in os.listdir(base) if os.path.isdir(os.path.join(base, e))}
    used = set()
    pick = {}
    for k, v in imap.items():
        if k.startswith("S") and isinstance(v, str) and "/" in v and not v.startswith("("):
            pick[k.split()[0]] = v
            used.add(v)
    pick["S012"] = "Fire/Eruption"
    used.add("Fire/Eruption")
    for aid, a in sorted(content["abilities"].items()):
        if aid in pick:
            continue
        el = a.get("element", "none")
        if a.get("kind") in ("heal", "revive"):
            el = "light"
        fam = ELEM_ICON.get(el, "Light")
        free = [f"{fam}/{n}" for n in pools[fam] if f"{fam}/{n}" not in used]
        choice = free[0] if free else f"{fam}/{pools[fam][hash(aid) % len(pools[fam])]}"
        pick[aid] = choice
        used.add(choice)
    ids = sorted(pick)
    cols = 32
    rows = (len(ids) + cols - 1) // cols
    at64 = Image.new("RGBA", (cols * 64, rows * 64), (0, 0, 0, 0))
    at32 = Image.new("RGBA", (cols * 32, rows * 32), (0, 0, 0, 0))
    index = {}
    for i, aid in enumerate(ids):
        f = os.path.join(base, pick[aid], "1.png")
        im = Image.open(f).convert("RGBA").resize((64, 64), Image.NEAREST)
        if aid == "S012":
            import numpy as np
            a = np.array(im).astype(float)
            a[..., 0] *= 0.75; a[..., 1] *= 0.6; a[..., 2] *= 0.35
            im = Image.fromarray(a.clip(0, 255).astype("uint8"))
        at64.paste(im, ((i % cols) * 64, (i // cols) * 64))
        at32.paste(im.resize((32, 32), Image.BOX), ((i % cols) * 32, (i // cols) * 32))
        index[aid] = i
    os.makedirs(os.path.join(EXT, "sprites"), exist_ok=True)
    at64.save(os.path.join(EXT, "sprites", "spell_icons_64.png"))
    at32.save(os.path.join(EXT, "sprites", "spell_icons_32.png"))
    json.dump({"cols": cols, "index": index, "source": pick}, open(os.path.join(EXT, "sprites", "spell_icons.json"), "w"), indent=0)
    print("spell icons:", len(ids))


def field_anims():
    src = os.path.join(PROC, "field_anim")
    n = 0
    for f in sorted(os.listdir(src)):
        if not f.endswith(".json"):
            continue
        name = f[:-5]
        meta = json.load(open(os.path.join(src, f)))
        fr = meta["frames"]
        w, h = fr[0]["frame"]["w"], fr[0]["frame"]["h"]
        cols = meta["meta"]["size"]["w"] // w
        info = {"frames": len(fr), "fps": round(1000.0 / max(1, fr[0]["duration"]), 2), "cell": [w, h], "cols": cols}
        n += copy(os.path.join(src, name + ".png"), os.path.join(EXT, "field_anim", name + ".png"))
        json.dump(info, open(os.path.join(EXT, "field_anim", name + ".json"), "w"))
    print("field anims:", n)


def common_sheets():
    """CuteSCKR sheets the engine draws directly (chests, switches): copied like the map builder does."""
    n = 0
    for alias, rel in (("dungeon", "Medieval Fantasy Dungeon & Prison Pixel Art Tileset Pack/2.png"),
                       ("dungeon", "Medieval Fantasy Dungeon & Prison Pixel Art Tileset Pack/4.png")):
        n += copy(os.path.join(ASSETS, "CuteSCKR", rel), os.path.join(EXT, "cute", alias, os.path.basename(rel)))
    print("common sheets:", n)


DIRS8 = ["south", "southwest", "west", "northwest", "north", "northeast", "east", "southeast"]


def _sheet(frames_by_dir, dst_png, dst_json, fps, extra=None):
    """frames_by_dir: {dir: [png paths]} -> one sheet (row per direction) + json {cell, dirs: {dir: [row, n]}, fps}."""
    from PIL import Image
    ims = {d: [Image.open(f).convert("RGBA") for f in fs] for d, fs in frames_by_dir.items() if fs}
    cw = max(i.width for v in ims.values() for i in v)
    chh = max(i.height for v in ims.values() for i in v)
    cols = max(len(v) for v in ims.values())
    rows = list(ims.keys())
    out = Image.new("RGBA", (cw * cols, chh * len(rows)), (0, 0, 0, 0))
    meta = {"cell": [cw, chh], "fps": fps, "dirs": {}}
    for r, d in enumerate(rows):
        for c, im in enumerate(ims[d]):
            out.alpha_composite(im, (c * cw + (cw - im.width) // 2, r * chh + (chh - im.height) // 2))
        meta["dirs"][d] = [r, len(ims[d])]
    meta.update(extra or {})
    os.makedirs(os.path.dirname(dst_png), exist_ok=True)
    out.save(dst_png)
    json.dump(meta, open(dst_json, "w"), indent=1)


def vehicles():
    import glob
    base = os.path.join(PROC, "airships")
    for ship in ("wayfarer", "lanternwake"):
        fr = {d: sorted(glob.glob(os.path.join(base, ship, "world", d, "frame_*.png"))) for d in DIRS8}
        sh = {"shadow_" + d: [os.path.join(base, ship, "world", "shadow", d + ".png")] for d in DIRS8
              if os.path.exists(os.path.join(base, ship, "world", "shadow", d + ".png"))}
        fr.update(sh)
        _sheet(fr, os.path.join(EXT, "vehicles", ship + ".png"), os.path.join(EXT, "vehicles", ship + ".json"), 8)
    mb = os.path.join(PROC, "mount", "brackhorn_frames")
    fr = {}
    for d in DIRS8:
        fr[d] = sorted(glob.glob(os.path.join(mb, "run_%s_*.png" % d)), key=lambda p: int(p.rsplit("_", 1)[1][:-4]))
        fr["walk_" + d] = sorted(glob.glob(os.path.join(mb, "walk_%s_*.png" % d)), key=lambda p: int(p.rsplit("_", 1)[1][:-4]))
    _sheet(fr, os.path.join(EXT, "vehicles", "brackhorn.png"), os.path.join(EXT, "vehicles", "brackhorn.json"), 12)
    for f in glob.glob(os.path.join(base, "icons", "*_icon_*.png")):
        copy(f, os.path.join(EXT, "vehicles", "icons", os.path.basename(f)))
    print("vehicles: installed")


SECTIONS = {"vehicles": vehicles, "common": common_sheets, "arenas": arenas, "audio": audio, "vfx": vfx, "vestiges": vestiges, "icons": spell_icons, "field_anim": field_anims}

if __name__ == "__main__":
    for s in (sys.argv[1:] or SECTIONS.keys()):
        SECTIONS[s]()
