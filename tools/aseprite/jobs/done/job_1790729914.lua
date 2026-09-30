-- Ashen Crown: sample resize tests (run from Aseprite: File > Scripts > Run Script)
local B = "F:/Ashen Crown/The Ashen Crown/Assets/"
local OUT = B .. "_processed/_test/"
app.fs.makeAllDirectories(OUT)
local log = io.open(OUT .. "log.txt", "w")
local function L(s) log:write(s .. "\n"); log:flush() end

local function resize(src, dst, w, h, method)
  local s = app.open(src)
  if not s then L("FAIL open " .. src); return end
  app.command.SpriteSize{ ui=false, width=w, height=h, lockRatio=false, method=method }
  s:saveCopyAs(dst); s:close(); L("ok " .. dst)
end

local oni = B .. "heroes/Crimson Oni Animated Samurai Hero!/masterpiece_premium_dark_fantasy_samurai/rotations/south.png"
local kit = B .. "heroes/Crimson Kitsune Empress — Legendary Fox Spirit Samurai Hero/masterpiece_premium_fantasy_samurai_heroine/rotations/south.png"
local gol = B .. "heroes/RUNE_GOLEM_GUARDIAN_OF/RUNE_GOLEM_GUARDIAN_OF/rotations/south.png"
for _, m in ipairs({"nearest", "rotsprite", "bilinear"}) do
  resize(oni, OUT .. "oni_" .. m .. ".png", 125, 125, m)     -- 188 * 2/3
  resize(kit, OUT .. "kit_" .. m .. ".png", 127, 127, m)     -- 156 * 62/76
  resize(gol, OUT .. "golem_" .. m .. ".png", 77, 77, m)     -- 64 * 1.2
  resize(B .. "NPCs/GandalfHardcore characters pack/GandalfHardcore characters pack/Mage.png", OUT .. "mage_" .. m .. ".png", 450, 90, m)
end

-- battle background pixelation variants
local bg = B .. "Battle Backgrounds/Fantasy RPG Battle Arenas HD/Fantasy RPG Battle Arenas HD/Backgrounds/Background_06.png"
local function pix(tag, lw, lh, colors)
  local s = app.open(bg)
  if not s then L("FAIL open bg"); return end
  local cw = math.floor(s.height * 4 / 3)
  s:crop(Rectangle(math.floor((s.width - cw) / 2), 0, cw, s.height))
  app.command.SpriteSize{ ui=false, width=lw, height=lh, lockRatio=false, method="bilinear" }
  app.command.ColorQuantization{ ui=false, maxColors=colors, withAlpha=false }
  app.command.ChangePixelFormat{ format="indexed", dithering="none" }
  app.command.SpriteSize{ ui=false, width=960, height=720, lockRatio=false, method="nearest" }
  app.command.ChangePixelFormat{ format="rgb" }
  s:saveCopyAs(OUT .. "bg06_" .. tag .. ".png"); s:close(); L("ok bg " .. tag)
end
pix("480_48", 480, 360, 48)
pix("480_96", 480, 360, 96)
pix("320_48", 320, 240, 48)
L("DONE")
log:close()
