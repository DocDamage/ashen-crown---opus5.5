-- Job 1: hero resize (Oni, Kitsune -> 62px body; Rune Golem x1.2) + NPC style test
local L0 = dofile("F:/Ashen Crown/The Ashen Crown/Repo/tools/aseprite/lib_ashen.lua")
local log, close = L0.logger(L0.OUT .. "_logs/job1_heroes.txt")
local heroes = {
  { dir = "heroes/Crimson Oni Animated Samurai Hero!", scale = 62/93 },
  { dir = "heroes/Crimson Kitsune Empress — Legendary Fox Spirit Samurai Hero", scale = 62/76 },
  { dir = "heroes/RUNE_GOLEM_GUARDIAN_OF", scale = 1.2 },
}
local n, fails = 0, 0
for _, h in ipairs(heroes) do
  L0.walk(L0.B .. h.dir, function(p, rel)
    if not p:lower():match("%.png$") then return end
    local s = L0.open1(p)
    if not s then fails = fails + 1; log("FAIL open " .. p); return end
    local w, hh = L0.round(s.width * h.scale), L0.round(s.height * h.scale)
    app.command.SpriteSize{ ui=false, width=w, height=hh, lockRatio=false, method="rotsprite" }
    local dst = L0.OUT .. h.dir .. "/" .. rel
    app.fs.makeAllDirectories(app.fs.filePath(dst))
    s:saveCopyAs(dst); s:close(); n = n + 1
  end)
  log(h.dir .. " done, total files so far " .. n)
end
log("heroes: " .. n .. " files, " .. fails .. " failures")

-- NPC style test on three sheets
local T = L0.OUT .. "_test/npc/"
app.fs.makeAllDirectories(T)
local G = L0.B .. "NPCs/GandalfHardcore characters pack/GandalfHardcore characters pack/"
for _, f in ipairs({ "Mage.png", "Town crier.png", "Crusader.png", "GandalfHardcore tavern NPCs.png" }) do
  for _, v in ipairs({ "a", "b", "c" }) do
    local s = L0.open1(G .. f)
    local sc = 90 / 64
    app.command.SpriteSize{ ui=false, width=L0.round(s.width*sc), height=L0.round(s.height*sc), lockRatio=false, method="rotsprite" }
    if v ~= "a" then
      local ok, e = pcall(function()
        app.command.Outline{ ui=false, color=Color{ r=20, g=16, b=22, a=255 }, matrix="circle", place="outside" }
      end)
      if not ok then log("outline err " .. tostring(e)) end
    end
    if v == "c" then
      local ok, e = pcall(function()
        app.command.BrightnessContrast{ ui=false, brightness=0, contrast=12 }
        app.command.HueSaturation{ ui=false, hue=0, saturation=12, lightness=0, mode="hsl" }
      end)
      if not ok then log("adjust err " .. tostring(e)) end
    end
    s:saveCopyAs(T .. f:gsub("%.png$", "") .. "_" .. v .. ".png"); s:close()
  end
end
log("npc test done")
close()
