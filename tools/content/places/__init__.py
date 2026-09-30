"""Expansion place content modules (one per author group): each may define
SHOPS {id: {name, kinds, town}}, SPEAKERS {key: [display name, portrait key]}, LOCATIONS {L_xxx: {name, map, spawn}},
QUESTS [quest dicts like data/quests.json]. compile_content merges them into the formation tables and catalogue."""
import importlib, os, pkgutil


def modules():
    here = os.path.dirname(os.path.abspath(__file__))
    return [importlib.import_module(__name__ + "." + m.name) for m in sorted(pkgutil.iter_modules([here]), key=lambda m: m.name)]


def apply(cat, FM):
    have = {q["id"] for q in cat["quests"]}
    for mod in modules():
        FM.SHOPS.update(getattr(mod, "SHOPS", {}))
        FM.SPEAKERS.update(getattr(mod, "SPEAKERS", {}))
        FM.LOCATIONS.update(getattr(mod, "LOCATIONS", {}))
        for q in getattr(mod, "QUESTS", []):
            if q["id"] not in have:
                cat["quests"].append(q)
                have.add(q["id"])
