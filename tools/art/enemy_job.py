"""Enemy art v2, step 2: queue an Aseprite job (the AshenCrown Job Runner must be running in Aseprite) that processes
the given enemy ids (default: every id in the manifest). Waits for the result unless --nowait."""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import install_overhaul as IO
JOBS = os.path.join(os.path.dirname(HERE), "aseprite", "jobs")
man = json.load(open(os.path.join(IO.PROC, "enemies_v2", "manifest.json")))
ids = [a for a in sys.argv[1:] if not a.startswith("--")] or sorted(man)
stamp = int(time.time())
logname = "enemies_v2_%d.txt" % stamp
lua = ('local A = dofile("F:/Ashen Crown/The Ashen Crown/Repo/tools/aseprite/lib_ashen.lua")\n'
       'local log, close = A.logger(A.OUT .. "_logs/%s")\n'
       'local M = dofile("F:/Ashen Crown/The Ashen Crown/Repo/tools/aseprite/enemy_v2.lua")\n'
       'M.run({%s}, log)\nclose()\n') % (logname, ", ".join('"%s"' % i for i in ids))
open(os.path.join(JOBS, "job_%d_enemies.lua" % stamp), "w").write(lua)
if "--nowait" in sys.argv:
    print("queued", logname); sys.exit(0)
lp = os.path.join(IO.PROC, "_logs", logname)
for _ in range(170):
    time.sleep(1)
    if os.path.exists(lp) and "DONE" in open(lp).read():
        break
print(open(lp).read() if os.path.exists(lp) else "no log yet (job still running?)")
