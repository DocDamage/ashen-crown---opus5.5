-- Job 4 (test): giant boss downscale x0.5, two methods on two frames
local L0 = dofile("F:/Ashen Crown/The Ashen Crown/Repo/tools/aseprite/lib_ashen.lua")
local log, close = L0.logger(L0.OUT .. "_logs/job4_boss_test.txt")
local T = L0.OUT .. "_test/boss/"
app.fs.makeAllDirectories(T)
local GB = L0.B .. "Giant Bosses/"
local frames = {
  ogre = GB .. "Giant Boss Pack –  2D Pixel Art Boss Collection/Giant Boss Pack –  2D Pixel Art Boss Collection/Boss (1)/ANIMATION/PNG/",
  serpent = GB .. "Giant Boss Pack  2 –  2D Pixel Art Boss Collection/Giant Boss Pack  2 –  2D Pixel Art Boss Collection/Boss (1)/ANIMATION/PNG/",
}
for tag, dir in pairs(frames) do
  local files = app.fs.listFiles(dir); table.sort(files)
  local f = dir .. files[math.floor(#files / 3) + 1]
  log(tag .. " " .. f)
  -- A: rotsprite
  local s = L0.open1(f)
  app.command.SpriteSize{ ui=false, width=L0.round(s.width/2), height=L0.round(s.height/2), lockRatio=false, method="rotsprite" }
  s:saveCopyAs(T .. tag .. "_rot.png"); s:close()
  -- B: palette from the full-size art, bilinear halve, snap back to that palette
  s = L0.open1(f)
  app.command.ColorQuantization{ ui=false, maxColors=96, withAlpha=false }
  app.command.SpriteSize{ ui=false, width=L0.round(s.width/2), height=L0.round(s.height/2), lockRatio=false, method="bilinear" }
  app.command.ChangePixelFormat{ format="indexed", dithering="none" }
  app.command.ChangePixelFormat{ format="rgb" }
  s:saveCopyAs(T .. tag .. "_pal.png"); s:close()
  -- C: nearest
  s = L0.open1(f)
  app.command.SpriteSize{ ui=false, width=L0.round(s.width/2), height=L0.round(s.height/2), lockRatio=false, method="nearest" }
  s:saveCopyAs(T .. tag .. "_near.png"); s:close()
end
log("done"); close()
