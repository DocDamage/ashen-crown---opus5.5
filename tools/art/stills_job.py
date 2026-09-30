"""Cutscene stills and title art (docs/expansion/STILLS.md). The owner drops images named by still id
(ST06_dais.png, title.jpg, ...) into Assets/Stills; this queues the Aseprite job (the AshenCrown Job Runner must be
running in Aseprite), waits for it, then installs the results into game/assets/stills/. --install-only skips the job."""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import install_overhaul as IO
REPO = os.path.dirname(os.path.dirname(HERE))
JOBS = os.path.join(os.path.dirname(HERE), "aseprite", "jobs")
OUT = os.path.join(IO.PROC, "stills")
DEST = os.path.join(REPO, "game", "assets", "stills")
if "--install-only" not in sys.argv:
    stamp = int(time.time())
    logname = "stills_%d.txt" % stamp
    lua = ('local A = dofile("F:/Ashen Crown/The Ashen Crown/Repo/tools/aseprite/lib_ashen.lua")\n'
           'local log, close = A.logger(A.OUT .. "_logs/%s")\n'
           'local M = dofile("F:/Ashen Crown/The Ashen Crown/Repo/tools/aseprite/stills.lua")\n'
           'M.run(log)\nclose()\n') % logname
    open(os.path.join(JOBS, "job_%d_stills.lua" % stamp), "w").write(lua)
    lp = os.path.join(IO.PROC, "_logs", logname)
    for _ in range(170):
        time.sleep(1)
        if os.path.exists(lp) and "DONE" in open(lp).read():
            break
    print(open(lp).read() if os.path.exists(lp) else "no log yet (job still running?)")
os.makedirs(DEST, exist_ok=True)
n = 0
for f in sorted(os.listdir(OUT)) if os.path.isdir(OUT) else []:
    if f.endswith(".png"):
        shutil.copy2(os.path.join(OUT, f), os.path.join(DEST, f))
        n += 1
print("installed", n, "stills into", DEST)
