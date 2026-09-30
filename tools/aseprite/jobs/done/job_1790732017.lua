-- Job 6: parallax sets -> backdrop layer at the same 2x pixel size as the battle arenas.
-- Horizontal sets: each layer scaled (bilinear, in halving steps) to 360 px tall,
-- shown at 2x (720 on screen). Vertical forest set: scaled to 480 px wide.
-- tools/art/layer_clean.py then snaps alpha to 0/255 and reduces each layer to 32 colours.
local L0 = dofile("F:/Ashen Crown/The Ashen Crown/Repo/tools/aseprite/lib_ashen.lua")
local log, close = L0.logger(L0.OUT .. "_logs/job6_parallax.txt")
local n = 0
local function shrink(s, tw, th)
  while s.width > tw * 2 and s.height > th * 2 do
    app.command.SpriteSize{ ui=false, width=L0.round(s.width/2), height=L0.round(s.height/2), lockRatio=false, method="bilinear" }
  end
  app.command.SpriteSize{ ui=false, width=tw, height=th, lockRatio=false, method="bilinear" }
end
L0.walk(L0.B .. "Parallax", function(p, rel)
  if not p:lower():match("%.png$") or rel:match("Bonus") or rel:match("spaceship") then return end
  local s = L0.open1(p)
  if not s then log("FAIL " .. rel); return end
  local tw, th
  if rel:match("vertical") then tw = 480; th = L0.round(s.height * 480 / s.width)
  else th = 360; tw = L0.round(s.width * 360 / s.height) end
  shrink(s, tw, th)
  local dst = L0.OUT .. "parallax/" .. rel
  app.fs.makeAllDirectories(app.fs.filePath(dst))
  s:saveCopyAs(dst); s:close(); n = n + 1
  log(string.format("%s -> %dx%d", rel, tw, th))
end)
log("parallax layers: " .. n)
close()
