-- Battle backdrops from the Landscape Expansion: 512x512 -> 4:3 crop (lower-weighted) -> 480x360 -> 64 colours -> 2x nearest (960x720)
local A = dofile("F:/Ashen Crown/The Ashen Crown/Repo/tools/aseprite/lib_ashen.lua")
local SRC = A.B .. "Battle Backgrounds/landscape-expansion/Landscapes/"
local DST = A.OUT .. "battle_backgrounds/landscapes/"
local log, close = A.logger(A.OUT .. "_logs/job11_landscapes.txt")
local n = 0
A.walk(SRC, function(p, rel)
  if not p:lower():match("%.png$") then return end
  local ok, err = pcall(function()
    local s = A.open1(p)
    s:crop(Rectangle(0, 80, 512, 384))
    app.command.SpriteSize{ ui=false, width=480, height=360, lockRatio=false, method="bilinear" }
    app.command.ColorQuantization{ ui=false, maxColors=64, withAlpha=false }
    app.command.ChangePixelFormat{ format="indexed", dithering="none" }
    app.command.SpriteSize{ ui=false, width=960, height=720, lockRatio=false, method="nearest" }
    app.command.ChangePixelFormat{ format="rgb" }
    local out = DST .. rel:gsub("%.png$", "_px.png")
    app.fs.makeAllDirectories(app.fs.filePath(out))
    s:saveCopyAs(out); s:close()
    n = n + 1
  end)
  if not ok then log("FAIL " .. rel .. " " .. tostring(err)) end
end)
log("DONE " .. n)
close()
