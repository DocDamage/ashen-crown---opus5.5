"""T06 Nacre (salt market, quiet cloister, listening pool) and D08 Memory Vault.
D08 mechanic: arrange testimony in chronology; conflicting accounts must both remain in the record."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import Grid, write

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOWN = dict(tileset="town_r05", music="M015", zone="T06", region="R05", location="L_T06")
DUN = dict(tileset="vault", music="M024", zone="D08", region="R05", location="L_D08")


def market():
    g = Grid(44, 30, "N")
    g.rect(2, 3, 41, 26, ":")
    g.blob(22, 14, 8, 5, "N", only=":")
    g.rect(19, 26, 24, 29, ":")
    g.house(3, 4, 8, 3)
    g.house(14, 4, 6, 2)
    g.house(31, 4, 9, 4, chimney=7)     # cloister
    g.house(3, 17, 7, 3)
    g.house(33, 18, 7, 3)
    g.text(18, 12, "aaaa\nnnnn")
    g.text(12, 20, "gg  gg  gg")
    g.put(24, 8, "*"); g.put(10, 13, "*"); g.put(34, 13, "*")
    g.rect(0, 12, 2, 15, ":")             # west: listening pool
    g.e("spawn world 21 28 up")
    g.e("spawn from_cloister 35 8 down")
    g.e("spawn from_pool 1 13 right")
    g.e("spawn default 21 28 up")
    g.e("exit 19..24 29 WORLD l_t06")
    g.e("door 35 7 T06_CLOISTER entry sfx=FX009")
    g.e("exit 0 12..15 T06_POOL from_market")
    g.e("npc sen 22 9 down sprite=sen talk=T06_SEN")
    g.e("npc gardener_n 14 22 up sprite=farmer talk=T06_GARDENER")
    g.e("npc family_a 28 16 left sprite=elder talk=T06_FAMILY")
    g.e("npc family_b 27 17 up sprite=survivor talk=T06_FAMILY")
    g.e("npc salt_seller 20 14 down sprite=keeper talk=T06_SALT")
    g.e("npc water_carrier 8 11 right sprite=worker talk=T06_WATER wander=1")
    g.e("npc pilgrim_n 38 22 left sprite=monk talk=T06_PILGRIM")
    g.e("shop 20 13 SHOP_T06")
    return g.emit("T06_MARKET", name="Nacre - Salt Market", **TOWN)


def cloister():
    g = Grid(20, 14)
    g.rect(1, 1, 18, 12, ".")
    g.text(2, 1, "kk.@..kk.kk")
    g.text(3, 5, "BB.BB..BB.BB")
    g.text(3, 8, "gg......gg")
    g.rect(9, 13, 10, 13, "+")
    g.e("spawn entry 9 12 up")
    g.e("exit 9..10 13 T06_MARKET from_cloister")
    g.e("npc cloister_keeper 5 2 down sprite=monk talk=T06_INN")
    g.e("inn 5 1 scene=T06_INN")
    g.e("npc listener 14 10 up sprite=scholar talk=T06_LISTENER")
    g.e("save 17 10")
    return g.emit("T06_CLOISTER", name="Nacre - Quiet Cloister", tileset="interior_stone", music="M015", zone="T06", location="L_T06", save="true")


def pool():
    g = Grid(32, 22, "N")
    g.rect(2, 2, 29, 19, ":")
    g.blob(15, 10, 8, 5, "9")
    g.rect(29, 9, 31, 12, ":")
    for (x, y) in ((5, 4), (26, 4), (5, 17), (26, 17)):
        g.put(x, y, "*")
    g.e("spawn from_market 30 10 left")
    g.e("exit 31 9..12 T06_MARKET from_pool")
    g.e("npc pool_keeper 15 17 up sprite=sen talk=T06_POOL_KEEPER")
    g.put(24, 14, "m")
    g.e("trigger 22..26 15..16 scene=CH10_SC07 if=flag:accord_cinder,flag:accord_aerie,flag:accord_nacre,!ch:CH10")
    g.e("npc volunteer 22 15 up sprite=volunteer talk=CH10_VOLUNTEER if=ch:CH09,!ch:CH10")
    g.e("read 15 4 \"The listening pool. When it is quiet, you can hear several people remembering the same morning differently.\"")
    return g.emit("T06_POOL", name="Nacre - Listening Pool", **TOWN)


# ------------------------------------------------------------------ D08 Memory Vault (concentric testimony rooms)
def ring_room(w, h, seed):
    g = Grid(w, h)
    g.blob(w // 2, h // 2, w // 2 - 2, h // 2 - 2, ".")
    g.blob(w // 2, h // 2, w // 2 - 7, h // 2 - 7, "#")
    g.blob(w // 2, h // 2, w // 2 - 9, h // 2 - 9, ",")
    cx, cy = w // 2, h // 2
    g.rect(cx - 1, cy - (h // 2 - 6), cx, cy, ",")      # north gap through the inner ring
    g.rect(cx - 1, cy, cx, cy + (h // 2 - 6), ",")      # south gap
    return g


def d_r01():
    g = Grid(40, 28)
    g.rect(4, 4, 35, 23, ".")
    g.rect(18, 24, 21, 27, ".")
    g.rect(18, 0, 21, 4, ".")
    for x in (10, 29):
        g.put(x, 10, "*"); g.put(x, 18, "*")
    g.e("spawn world 19 26 up")
    g.e("spawn from_r02 19 2 down")
    g.e("spawn default 19 26 up")
    g.e("exit 18..21 27 WORLD l_d08")
    g.e("exit 18..21 0 D08_R02 from_r01 if=event:D08_CONSENT")
    g.e("trigger 16..23 14..15 scene=D08_CONSENT if=!event:D08_CONSENT")
    g.e("save 7 20")
    g.e("heal 9 20")
    return g.emit("D08_R01", name="Memory Vault - Listening Gate", encounters="none", save="true", **DUN)


def d_r02():
    g = ring_room(32, 32, 1)
    g.rect(14, 26, 17, 31, ".")
    g.rect(0, 14, 5, 17, ".")
    g.rect(26, 14, 31, 17, ".")
    g.rect(13, 12, 18, 13, ".")
    g.put(15, 15, "8")
    g.e("read 15 14 scene=D08_WALL \"x\"")
    g.e("read 8 6 scene=D08_T1 \"x\"")
    g.put(8, 5, "@")
    g.e("spawn from_r01 15 29 up")
    g.e("spawn from_r03 1 15 right")
    g.e("spawn from_r04 30 15 left")
    g.e("exit 14..17 31 D08_R01 from_r02")
    g.e("exit 0 14..17 D08_R03 from_r02")
    g.e("exit 31 14..17 D08_R04 from_r02")
    return g.emit("D08_R02", name="Memory Vault - Voluntary Accord", encounters="D08", rate="0.6", **DUN)


def d_r03():
    g = Grid(40, 24)
    g.rect(2, 3, 37, 20, ".")
    g.rect(37, 10, 39, 13, ".")
    g.rect(18, 0, 21, 3, ".")
    for x in (8, 16, 24, 32):
        g.put(x, 5, "m")
    g.put(12, 16, "@"); g.put(26, 16, "@")
    g.e("read 12 15 scene=D08_T2A \"x\"")
    g.e("read 26 15 scene=D08_T2B \"x\"")
    g.e("chest D08_C_R03 4 18 I005 1")
    g.e("save 30 6")
    g.e("spawn from_r02 38 11 left")
    g.e("spawn from_r05 19 1 down")
    g.e("exit 39 10..13 D08_R02 from_r03")
    g.e("exit 18..21 0 D08_R05 from_r03 if=flag:d08_chrono locked=\"The choir door will not open to a partial record.\"")
    return g.emit("D08_R03", name="Memory Vault - First Industry", encounters="D08", rate="0.8", **DUN)


def d_r04():
    g = Grid(32, 28)
    g.rect(2, 2, 29, 25, ".")
    g.rect(0, 12, 2, 15, ".")
    g.rect(14, 0, 17, 2, ".")
    g.text(6, 6, "BB..BB..BB")
    g.text(6, 12, "BB..BB..BB")
    g.put(22, 20, "@")
    g.e("read 22 19 scene=D08_T3 \"x\"")
    g.e("chest D08_ELIXIR 26 4 I024 1 acq=ELIXIR_D08")
    g.e("save 20 4")
    # clue-led secret behind the nursery shelves
    g.rect(24, 20, 29, 24, "#")
    g.rect(25, 21, 28, 23, ".")
    g.put(24, 22, ".")
    g.e("chest D08_SECRET_CHEST 27 22 A008 1 acq=D08_SECRET")
    g.e("read 10 22 \"A caretaker's note: 'Keep the day-token with the children's shelves, by the south-east alcove.'\"")
    g.e("spawn from_r02 1 13 right")
    g.e("spawn from_r05 15 1 down")
    g.e("exit 0 12..15 D08_R02 from_r04")
    g.e("exit 14..17 0 D08_R05 from_r04 if=flag:d08_chrono locked=\"The choir door will not open to a partial record.\"")
    return g.emit("D08_R04", name="Memory Vault - Quiet Nursery", encounters="none", **DUN)


def d_r05():
    g = ring_room(40, 32, 2)
    g.rect(0, 22, 6, 25, ".")
    g.rect(34, 22, 39, 25, ".")
    g.rect(18, 0, 21, 5, ".")
    g.blob(20, 16, 8, 6, ".")
    g.rect(18, 22, 21, 25, ".")
    g.path([(3, 23), (20, 23), (36, 23)], ".", 2)
    g.path([(20, 23), (20, 16)], ".", 2)
    g.e("trigger 16..23 14..15 scene=D08_CHOIR if=!flag:b08_done")
    g.e("spawn from_r03 1 23 right")
    g.e("spawn from_r04 38 23 left")
    g.e("spawn from_r06 19 2 down")
    g.e("exit 0 22..25 D08_R03 from_r05")
    g.e("exit 39 22..25 D08_R04 from_r05")
    g.e("exit 18..21 0 D08_R06 from_r05 if=flag:b08_done")
    return g.emit("D08_R05", name="Memory Vault - Choir Chamber", encounters="none", **DUN)


def d_r06():
    g = Grid(32, 24)
    g.rect(3, 3, 28, 20, ".")
    g.blob(15, 10, 6, 4, "9")
    g.rect(14, 20, 17, 23, ".")
    g.e("trigger 12..19 16..17 scene=D08_SC06 if=!ch:CH09")
    g.e("spawn from_r05 15 22 up")
    g.e("exit 14..17 23 D08_R05 from_r06")
    return g.emit("D08_R06", name="Memory Vault - Still Pool", encounters="none", **DUN)


if __name__ == "__main__":
    write(os.path.join(ROOT, "content_src", "maps", "t06_d08.map"),
          [market(), cloister(), pool(), d_r01(), d_r02(), d_r03(), d_r04(), d_r05(), d_r06()], "T06 Nacre + D08 Memory Vault")
    print("t06/d08 written")
