-- VFX: build tagged .aseprite + JSON for every spell/buff effect from the pixelated 128 sheets in _processed/vfx
local A = dofile("F:/Ashen Crown/The Ashen Crown/Repo/tools/aseprite/lib_ashen.lua")
local log, close = A.logger(A.OUT .. "_logs/job15_vfx.txt")
local n = 0
local function readjson(p) local f = io.open(p, "r"); local s = f:read("a"); f:close(); return json.decode(s) end
for _, pack in ipairs({"spell-fx", "buff-fx"}) do
  local base = A.OUT .. "vfx/" .. pack .. "/"
  local data = readjson(base .. "effects.json")
  for _, e in ipairs(data.effects) do
    local ok, err = pcall(function()
      local sheet = Image{ fromFile = base .. e.file }
      local cw, ch = e.cell["128"][1], e.cell["128"][2]
      local spr = Sprite(cw, ch, ColorMode.RGB)
      for i = 0, e.frames - 1 do
        if i > 0 then spr:newEmptyFrame(i + 1) end
        local x, y = (i % e.columns) * cw, math.floor(i / e.columns) * ch
        spr:newCel(spr.layers[1], i + 1, Image(sheet, Rectangle(x, y, cw, ch)), Point(0, 0))
        spr.frames[i + 1].duration = 1 / e.fps
      end
      local tg = spr:newTag(1, e.frames); tg.name = e.loop and "loop" or "once"
      local out = base .. "aseprite/" .. e.name
      app.fs.makeAllDirectories(base .. "aseprite")
      spr:saveAs(out .. ".aseprite")
      spr:close(); n = n + 1
    end)
    if not ok then log("FAIL " .. e.name .. " " .. tostring(err)) end
  end
end
log("DONE " .. n)
close()
