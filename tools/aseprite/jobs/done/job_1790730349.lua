-- Job 2: pixelate the 75 Nirox battle arenas.
-- centre crop to 4:3, scale to 960x720 then 480x360 (bilinear), 64-colour palette per image, no dithering,
-- then 2x nearest to 960x720 so each art pixel is 2x2 screen pixels.
local L0 = dofile("F:/Ashen Crown/The Ashen Crown/Repo/tools/aseprite/lib_ashen.lua")
local log, close = L0.logger(L0.OUT .. "_logs/job2_battle_backgrounds.txt")
local SRC = L0.B .. "Battle Backgrounds/Fantasy RPG Battle Arenas HD/Fantasy RPG Battle Arenas HD/Backgrounds/"
local DST = L0.OUT .. "battle_backgrounds/"
app.fs.makeAllDirectories(DST)
local n = 0
for _, name in ipairs(app.fs.listFiles(SRC)) do
  local num = name:match("^Background_(%d+)%.png$")
  if num then
    local s = L0.open1(SRC .. name)
    if not s then log("FAIL " .. name) else
      local cw = math.floor(s.height * 4 / 3)
      s:crop(Rectangle(math.floor((s.width - cw) / 2), 0, cw, s.height))
      -- step down in stages so bilinear averages every source pixel (a single 2.6x step aliases into speckle)
      app.command.SpriteSize{ ui=false, width=960, height=720, lockRatio=false, method="bilinear" }
      app.command.SpriteSize{ ui=false, width=480, height=360, lockRatio=false, method="bilinear" }
      app.command.ColorQuantization{ ui=false, maxColors=64, withAlpha=false }
      app.command.ChangePixelFormat{ format="indexed", dithering="none" }
      app.command.SpriteSize{ ui=false, width=960, height=720, lockRatio=false, method="nearest" }
      app.command.ChangePixelFormat{ format="rgb" }
      s:saveCopyAs(DST .. "arena_" .. num .. "_px.png"); s:close(); n = n + 1
    end
  end
end
log("battle backgrounds: " .. n)
close()
