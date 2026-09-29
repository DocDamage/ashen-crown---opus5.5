"""Post-state Glass Coast: T04_UPPER (Bellharbor ropewalk roads over flooded lower streets) and T04_GALLERY
(the upper gallery where Tessa holds her barrier; CH15 / SC09)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import Grid, write

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOWN = dict(tileset="town_r03", music="M013", zone="T04", region="R03", location="L_T04", phase="post")


def upper():
    g = Grid(46, 32, "~")
    g.rect(2, 3, 43, 8, ":")               # upper road (was the ropewalk)
    g.rect(2, 20, 43, 25, ":")             # quay heights
    g.rect(20, 8, 23, 20, "=")             # rope bridge between them
    g.rect(0, 21, 2, 24, ":")              # west: world
    g.rect(40, 0, 43, 3, ":")              # north-east: gallery
    g.house(4, 3, 7, 2); g.house(14, 3, 6, 2); g.house(28, 3, 8, 2, chimney=2)
    g.house(5, 20, 8, 2); g.house(30, 20, 7, 2)
    g.text(8, 24, "aaaa\nnnnn")
    g.text(34, 24, "3333")
    g.put(25, 7, "j")                      # the cooking-pot alarm post
    g.e("spawn world 1 22 right")
    g.e("spawn from_gallery 41 1 down")
    g.e("spawn default 1 22 right")
    g.e("exit 0 21..24 WORLD_POST l_t04")
    g.e("exit 40..43 0 T04_GALLERY from_upper")
    g.e("npc jori_u 24 6 left sprite=jori talk=T04U_JORI")
    g.e("npc pot_child 26 7 left sprite=child talk=T04U_POT")
    g.e("npc chapel_warden 12 22 up sprite=monk talk=T04U_CHAPEL")
    g.e("npc chart_seller 10 23 up sprite=keeper talk=T04U_SHOP")
    g.e("npc ropemaker 36 23 left sprite=worker talk=T04U_ROPE")
    g.e("npc sailor_u 16 7 down sprite=sailor talk=T04U_SAILOR")
    g.e("inn 13 21 scene=T04U_INN")
    g.e("npc apprentice_u 30 24 left sprite=apprentice talk=Q02_HOOK if=ch:CH20")
    g.e("save 17 22")
    g.decorate("cr3l", 14, 90, ":")
    return g.emit("T04_UPPER", name="Bellharbor - Upper Town", save="true", **TOWN)


def gallery():
    g = Grid(40, 28)
    g.rect(2, 3, 37, 5, ",")               # upper walkway (the alternate route out)
    g.rect(38, 3, 39, 5, ",")              # east stair out to the upper town
    g.rect(2, 7, 37, 8, ".")               # under the roof: residents shelter here
    g.put(3, 6, ",")                       # gap from the roof space up to the walkway
    g.rect(2, 11, 37, 12, ".")
    g.rect(2, 13, 37, 25, "w")             # the flooded lower gallery
    g.rect(2, 9, 3, 10, ".")               # west side passage past the barrier
    g.rect(18, 25, 21, 27, ".")            # south: upper town
    g.e("block 12..13 3..5 tile=crate if=!flag:t04g_clear1 msg=\"Fallen rope-bales block the upper walkway. A winch hangs above them.\"")
    g.e("block 26..27 3..5 tile=crate if=!flag:t04g_clear2 msg=\"More fallen bales. There's a second winch.\"")
    g.e("switch winch1 11 8 flag=t04g_clear1 scene=CH15_WINCH1")
    g.e("switch winch2 25 8 flag=t04g_clear2 scene=CH15_WINCH2")
    # the barrier: Tessa's light holds the roof above the shelter
    g.rect(4, 9, 37, 10, "*")
    g.e("tileset_over 4..37 9..10 floor2 if=ch:CH15")
    g.e("npc tessa_g 19 11 up sprite=C02 talk=CH15_TESSA if=!ch:CH15")
    g.e("npc res1 7 7 down sprite=elder talk=CH15_RES1 if=!flag:t04g_res1")
    g.e("npc res2 18 8 down sprite=survivor talk=CH15_RES2 if=!flag:t04g_res2")
    g.e("npc res3 31 7 down sprite=child talk=CH15_RES3 if=!flag:t04g_res3")
    g.e("npc jori_g 35 11 left sprite=jori talk=CH15_JORI if=!ch:CH15")
    g.e("trigger 16..23 22..24 scene=CH15_ARRIVE if=ch:CH14,!event:CH15_ARRIVE")
    g.e("trigger 17..21 12 scene=CH15_SC09 if=flag:t04g_res1,flag:t04g_res2,flag:t04g_res3,!ch:CH15")
    g.e("spawn from_upper 19 26 up")
    g.e("spawn from_stair 38 4 left")
    g.e("spawn default 19 26 up")
    g.e("exit 18..21 27 T04_UPPER from_gallery")
    g.e("exit 39 3..5 T04_UPPER from_gallery if=flag:t04g_clear2")
    return g.emit("T04_GALLERY", name="Bellharbor - Upper Gallery", tileset="archive", music="M013", zone="T04", region="R03",
                  location="L_T04", phase="post")


if __name__ == "__main__":
    write(os.path.join(ROOT, "content_src", "maps", "post_r03.map"), [upper(), gallery()], "Post-state Glass Coast")
    print("post_r03 written")
