-- Job 5: giant bosses x0.5 (rotsprite) -> ~1px density matching the heroes; 1366x766 canvases -> 683x383.
-- Every PNG except PREVIEW (animation, effect and part layers) so layers stay aligned.
-- tools/art/boss_crop.py then crops each boss to the union of its frames.
local L0 = dofile("F:/Ashen Crown/The Ashen Crown/Repo/tools/aseprite/lib_ashen.lua")
local log, close = L0.logger(L0.OUT .. "_logs/job5_bosses.txt")
local n, fails = 0, 0
L0.walk(L0.B .. "Giant Bosses", function(p, rel)
  if not p:lower():match("%.png$") or rel:match("PREVIEW") then return end
  local s = L0.open1(p)
  if not s then fails = fails + 1; log("FAIL " .. rel); return end
  app.command.SpriteSize{ ui=false, width=L0.round(s.width/2), height=L0.round(s.height/2), lockRatio=false, method="rotsprite" }
  local dst = L0.OUT .. "bosses/" .. rel
  app.fs.makeAllDirectories(app.fs.filePath(dst))
  s:saveCopyAs(dst); s:close(); n = n + 1
  if n % 200 == 0 then log("progress " .. n) end
end)
log("bosses: " .. n .. " files, " .. fails .. " failures")
close()
