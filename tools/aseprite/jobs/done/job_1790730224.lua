-- Job 3: GandalfHardcore NPCs -> hero scale. rotsprite x(90/64) so 64px cells become 90px cells
-- (44px bodies -> ~62px), then contrast +12 and saturation +12 to sit closer to the hero art.
-- A 1px smart outline is added afterwards by tools/art/npc_outline.py.
local L0 = dofile("F:/Ashen Crown/The Ashen Crown/Repo/tools/aseprite/lib_ashen.lua")
local log, close = L0.logger(L0.OUT .. "_logs/job3_npcs.txt")
local SRC = L0.B .. "NPCs/GandalfHardcore characters pack/GandalfHardcore characters pack/"
local DST = L0.OUT .. "npcs/gandalfhardcore/"
app.fs.makeAllDirectories(DST)
local n = 0
for _, name in ipairs(app.fs.listFiles(SRC)) do
  if name:lower():match("%.png$") then
    local s = L0.open1(SRC .. name)
    if not s then log("FAIL " .. name) else
      local sc = 90 / 64
      app.command.SpriteSize{ ui=false, width=L0.round(s.width*sc), height=L0.round(s.height*sc), lockRatio=false, method="rotsprite" }
      local ok, e = pcall(function()
        app.command.BrightnessContrast{ ui=false, brightness=0, contrast=12 }
        app.command.HueSaturation{ ui=false, hue=0, saturation=12, lightness=0, mode="hsl" }
      end)
      if not ok then log("adjust err " .. name .. " " .. tostring(e)) end
      local w, h = s.width, s.height
      s:saveCopyAs(DST .. name); s:close(); n = n + 1
      log(string.format("%s %dx%d", name, w, h))
    end
  end
end
log("npcs: " .. n)
close()
