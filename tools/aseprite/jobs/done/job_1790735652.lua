-- Job 8: pixelate the owner's airship art (sliced by tools/art/slice_airships.py).
--  * world-map / top-down / landed / fold sprites, icons and effects: 1x density, 32-colour palette, no dither
--  * side views (flying, damaged, burning, rising from the sea): 2x backdrop layer, stored at art size
--    (Wayfarer x1.0, Lanternwake x1.3), 32 colours; the engine shows them doubled like the parallax skies
--  * deck stage: battle backdrop (4:3 crop, arena pipeline) and a wide 360px-tall version for deck scenes
local L0 = dofile("F:/Ashen Crown/The Ashen Crown/Repo/tools/aseprite/lib_ashen.lua")
local log, close = L0.logger(L0.OUT .. "_logs/job8_airships.txt")
local S = L0.OUT .. "airships/_slices/"
local O = L0.OUT .. "airships/"
local function quant(n)
  app.command.ColorQuantization{ ui=false, maxColors=n, withAlpha=false }
  app.command.ChangePixelFormat{ format="indexed", dithering="none" }
  app.command.ChangePixelFormat{ format="rgb" }
end
local n = 0
for _, group in ipairs({ "wayfarer", "lanternwake", "icons", "fx" }) do
  for _, name in ipairs(app.fs.listFiles(S .. group)) do
    if name:match("%.png$") then
      local s = L0.open1(S .. group .. "/" .. name)
      local side = name:match("^side_") or name:match("^rise_")
      local sub = side and "side_view/" or ((group == "wayfarer" or group == "lanternwake") and "world_src/" or "")
      if side then
        local k = (group == "lanternwake") and 1.3 or 1.0
        if k ~= 1.0 then
          app.command.SpriteSize{ ui=false, width=L0.round(s.width*k), height=L0.round(s.height*k), lockRatio=false, method="bilinear" }
        end
      end
      quant(32)
      local dst = O .. group .. "/" .. sub .. name
      app.fs.makeAllDirectories(app.fs.filePath(dst))
      local w, h = s.width, s.height
      s:saveCopyAs(dst); s:close(); n = n + 1
      log(string.format("%s/%s%s %dx%d", group, sub, name, w, h))
    end
  end
end
-- deck stage
local deck = S .. "deck/deck_stage_full.png"
local s = L0.open1(deck)
local cw = math.floor(s.height * 4 / 3)
s:crop(Rectangle(math.floor((s.width - cw) / 2), 0, cw, s.height))
app.command.SpriteSize{ ui=false, width=960, height=720, lockRatio=false, method="bilinear" }
app.command.SpriteSize{ ui=false, width=480, height=360, lockRatio=false, method="bilinear" }
quant(64)
app.command.SpriteSize{ ui=false, width=960, height=720, lockRatio=false, method="nearest" }
app.fs.makeAllDirectories(O .. "deck")
s:saveCopyAs(O .. "deck/deck_battle_px.png"); s:close()
s = L0.open1(deck)
app.command.SpriteSize{ ui=false, width=L0.round(s.width * 360 / s.height), height=360, lockRatio=false, method="bilinear" }
quant(64)
s:saveCopyAs(O .. "deck/deck_wide_px.png"); s:close()
log("airship sprites: " .. n .. " + 2 deck backdrops")
close()
