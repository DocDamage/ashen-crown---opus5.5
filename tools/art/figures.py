"""Character identity specs (docs/03 visual directions) shared by world sprites, battle sprites and portraits."""
from art.pix import hexc

SKIN = {"light": hexc("f0c8a0"), "tan": hexc("d8a070"), "brown": hexc("a8704a"), "dark": hexc("7a4e34"),
        "scales": hexc("c84a3c"), "pale": hexc("f4dcc4")}

FIG = {
    # Dain: 34 dragonborn, broad, crimson scales, charcoal segmented armor, one unpainted gauntlet
    "C01": dict(skin=SKIN["scales"], scales=True, hair=hexc("3a1c1c"), hair_style="short_swept", build="broad", height=1.0,
                top=hexc("4a4c58"), top2=hexc("2e3038"), legs=hexc("35363f"), boots=hexc("2a2224"), armor=True,
                gauntlet=hexc("b8bcc4"), weapon="sword", weapon_col=hexc("c8ccd4"), accent=hexc("8c2a2a"), eye=hexc("f0c040")),
    # Tessa: 22, slim, short dark hair, amber spectacles on forehead, cobalt coat, red mitten casting hand
    "C02": dict(skin=SKIN["light"], hair=hexc("2a2230"), hair_style="bob", build="slim", height=0.93,
                top=hexc("2e54a8"), top2=hexc("1e3878"), legs=hexc("3a3040"), boots=hexc("4a2e24"), coat="long",
                goggles=hexc("e0a030"), mitten=hexc("d83030"), weapon="rod", weapon_col=hexc("a07a4a"), accent=hexc("e0a030"), eye=hexc("3a2a20")),
    # Corren: 31, long ochre scarf weighted ends, narrow teal breastplate, flight harness
    "C03": dict(skin=SKIN["tan"], hair=hexc("5a3a22"), hair_style="short_messy", build="lean", height=1.02,
                top=hexc("2e8a84"), top2=hexc("1e5e5a"), legs=hexc("5a4a3a"), boots=hexc("3a2a20"), scarf=hexc("d09a38"),
                harness=hexc("6a4a2a"), weapon="spear", weapon_col=hexc("b0b8c0"), accent=hexc("d09a38"), eye=hexc("2a2a3a")),
    # Ivo: 49, gray curls, rolled sleeves, copper tool rig, ink-dark apron, stocky
    "C04": dict(skin=SKIN["light"], hair=hexc("9a9aa4"), hair_style="curls", build="stocky", height=0.95,
                top=hexc("c8c0b0"), top2=hexc("9a9080"), legs=hexc("4a4038"), boots=hexc("3a2a20"), apron=hexc("262434"),
                rig=hexc("c07840"), sleeves=True, weapon="wrench", weapon_col=hexc("c07840"), accent=hexc("c07840"), eye=hexc("2a2a3a"), beard=hexc("9a9aa4")),
    # Nera: 29, moss-green cape split at shoulders, long braid, cream fletching, map tube
    "C05": dict(skin=SKIN["brown"], hair=hexc("2a1a14"), hair_style="braid", build="lean", height=0.98,
                top=hexc("8a7a5a"), top2=hexc("6a5a40"), legs=hexc("4a4030"), boots=hexc("3a2a1e"), cape=hexc("4a7a3a"),
                maptube=hexc("8a5a30"), weapon="bow", weapon_col=hexc("8a5a30"), accent=hexc("f0e8c8"), eye=hexc("20140e")),
    # Oriel: 42, ivory stole, plum dress, brass bell without clapper, close-cropped silver hair
    "C06": dict(skin=SKIN["dark"], hair=hexc("c8ccd8"), hair_style="cropped", build="normal", height=0.97,
                top=hexc("6a2a5a"), top2=hexc("4a1a40"), legs=hexc("6a2a5a"), boots=hexc("3a2430"), dress=True, stole=hexc("f0e8d4"),
                bell=hexc("d0a040"), weapon="staff", weapon_col=hexc("a88a5a"), accent=hexc("d0a040"), eye=hexc("1a1010")),
    # Sable: 36, black-violet coat, exposed scarred forearm, straight white blade with broken runes
    "C07": dict(skin=SKIN["pale"], hair=hexc("1c1a24"), hair_style="tied", build="normal", height=1.0,
                top=hexc("3a2a4a"), top2=hexc("22182e"), legs=hexc("241c2c"), boots=hexc("16121c"), coat="long", scar=True,
                weapon="blade", weapon_col=hexc("eef0f4"), accent=hexc("8a6ac8"), eye=hexc("5a4a8a")),
    # Pip: 27, rust waistcoat, green sash, cropped brown curls, satchel larger than his weapon
    "C08": dict(skin=SKIN["tan"], hair=hexc("6a4020"), hair_style="curls_short", build="slim", height=0.9,
                top=hexc("e8dcc0"), top2=hexc("b8ac90"), legs=hexc("4a3a2e"), boots=hexc("3a2a20"), waistcoat=hexc("a84a28"),
                sash=hexc("3a8a4a"), satchel=hexc("8a6038"), weapon="knife", weapon_col=hexc("c0c4cc"), accent=hexc("3a8a4a"), eye=hexc("2a1a10")),
}

# Named NPCs and reusable role silhouettes (12 roles + recurring people)
def npc(skin, hair, style, top, legs, build="normal", height=1.0, **kw):
    d = dict(skin=SKIN[skin], hair=hexc(hair), hair_style=style, build=build, height=height, top=hexc(top),
             top2=hexc(top), legs=hexc(legs), boots=hexc("2e2420"), eye=hexc("20140e"))
    for k, v in kw.items():
        d[k] = hexc(v) if isinstance(v, str) and len(v) == 6 else v
    d["top2"] = tuple(max(0, int(c * 0.72)) for c in d["top"][:3]) + (255,)
    return d

NPCS = {
    "mara": npc("brown", "3a2418", "tied", "7a5a3a", "4a3a2a", build="stocky", apron="5a4a3a"),
    "inspector": npc("light", "6a6a6a", "short_swept", "5a1e24", "2a2a30", hat="2a2a30"),
    "rook": npc("light", "8a6a4a", "short_messy", "6a6a4a", "3a3a30", coat="long", glasses="c0c0c0"),
    "voss": npc("pale", "b0b0b8", "short_swept", "8a1a1a", "2a2a2a", build="broad", armor=True, gauntlet="c8a040", cape="5a0e14"),
    "pell": npc("dark", "1a1a1a", "short_messy", "4a6a8a", "3a3a3a", build="normal", apron="3a4a5a"),
    "jori": npc("tan", "6a4020", "short_swept", "3a5a4a", "3a3030", build="slim", glasses="a0a0a0"),
    "edda": npc("tan", "4a2a1a", "tied", "2e7a74", "4a3a2a", build="lean", scarf="b88a30"),
    "sen": npc("brown", "e0e0e0", "long", "b0a0c8", "8a7aa0", dress=True),
    "ansel": npc("light", "8a6a3a", "short_swept", "6a6070", "3a3440", build="slim"),
    "ilyr": npc("scales", "f0a040", "short_messy", "e06030", "a03020"),
    "guard": npc("light", "4a3020", "short_swept", "8a2a2a", "3a3a40", armor=True, hat="4a4a58"),
    "worker": npc("tan", "3a2a1a", "short_messy", "8a6a4a", "4a4038", build="stocky", hat="a08040"),
    "clerk": npc("pale", "5a4a3a", "short_swept", "4a4a5a", "2e2e36", build="slim", glasses="a0a0a0"),
    "child": npc("light", "8a5a2a", "short_messy", "c07a3a", "5a4a3a", build="slim", height=0.72),
    "elder": npc("dark", "d8d8d8", "cropped", "6a5a4a", "4a4038", build="normal", height=0.92),
    "baker": npc("light", "c08040", "tied", "e8e0d0", "7a5a3a", build="stocky", apron="f0f0f0"),
    "keeper": npc("brown", "2a1a10", "short_swept", "3a6a3a", "4a3a2a", apron="6a4a2a"),
    "sailor": npc("tan", "1a1a2a", "short_messy", "2a4a7a", "e0e0d0", hat="2a3a6a"),
    "volunteer": npc("scales", "2a1a1a", "long", "8a8a6a", "5a5a4a"),
    "survivor": npc("pale", "3a3a3a", "cropped", "9a9a9a", "5a5a5a", build="slim"),
    "apprentice": npc("light", "c05030", "bob", "3a6aa8", "3a3040", build="slim", height=0.9),
    "patient": npc("dark", "2a2a2a", "long", "e0d8c8", "e0d8c8", dress=True),
    "farmer": npc("tan", "6a4a2a", "short_messy", "6a8a3a", "5a4a30", hat="c0a060"),
    "scholar": npc("pale", "3a2a3a", "long", "5a3a6a", "3a2a3a", dress=True, glasses="c0c0c0"),
    "pilot": npc("tan", "8a8a8a", "short_swept", "2e7a74", "4a3a2a", scarf="b88a30"),
    "monk": npc("brown", "1a1a1a", "cropped", "c8c0a0", "c8c0a0", dress=True),
    "soldier": npc("light", "3a2a1a", "short_swept", "5a5a64", "3a3a40", armor=True),
    "noble": npc("pale", "d0b060", "long", "6a2a6a", "3a1a3a", dress=True),
}
