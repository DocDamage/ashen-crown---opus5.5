-- Land Objects -> 48px grid. Objects stay native (1px, same density as the heroes); seabed ground tiles x3 nearest (one 16px tile = one 48px map tile).
local A = dofile("F:/Ashen Crown/The Ashen Crown/Repo/tools/aseprite/lib_ashen.lua")
local LO = A.B .. "Land Objects/"
local DST = A.OUT .. "land_objects/"
local log, close = A.logger(A.OUT .. "_logs/job14_land_objects.txt")
local n = 0
local function scale(src, dst, k, method)
  local ok, err = pcall(function()
    local s = A.open1(src)
    local w, h = s.width, s.height
    if k ~= 1 then app.command.SpriteSize{ ui=false, width=A.round(w * k), height=A.round(h * k), lockRatio=false, method=method } end
    app.fs.makeAllDirectories(app.fs.filePath(dst))
    s:saveCopyAs(dst); s:close(); n = n + 1
  end)
  if not ok then log("FAIL " .. src .. " " .. tostring(err)) end
end
-- cursed + undead separate objects
for _, set in ipairs({ {"Cursed-Land-Objects-Pixel-Art-for-RPG-Game", "cursed"}, {"the-top-down-undead-land-objects-pixel-art", "undead"} }) do
  A.walk(LO .. set[1] .. "/PNG/Objects_separately", function(p, rel)
    if p:lower():match("%.png$") then scale(p, DST .. set[2] .. "/" .. rel, 1, "nearest") end
  end)
  -- full sheets too, for reference
end
scale(LO .. "Cursed-Land-Objects-Pixel-Art-for-RPG-Game/PNG/Cursed_objects.png", DST .. "cursed/_sheet_Cursed_objects.png", 1, "nearest")
scale(LO .. "the-top-down-undead-land-objects-pixel-art/PNG/Objects_source.png", DST .. "undead/_sheet_Objects_source.png", 1, "nearest")
-- seabed: ground x3 nearest, objects native
local SB = LO .. "Seabed-Pixel-Art-Top-Down-Tileset/"
for _, f in ipairs({"Sand_ground.png", "spots.png"}) do scale(SB .. "Tiled_files/" .. f, DST .. "seabed/ground_x3/" .. f, 3, "nearest") end
for _, f in ipairs({"Objects.png", "Animated_objects1.png", "Animated_objects2.png", "Animated_objects3.png", "Animated_objects4.png", "Animated_objects5.png", "Bubbles.png", "Details.png", "reef_elements.png"}) do
  scale(SB .. "Tiled_files/" .. f, DST .. "seabed/objects/" .. f, 1, "nearest")
end
scale(SB .. "PNG/Objects.png", DST .. "seabed/_sheet_Objects.png", 1, "nearest")
scale(SB .. "PNG/Animated_objects.png", DST .. "seabed/_sheet_Animated_objects.png", 1, "nearest")

-- animated cursed objects: group Name_shadowV_F.png into one .aseprite per Name_shadowV (150ms frames)
local groups = {}
for _, name in ipairs(app.fs.listFiles(DST .. "cursed")) do
  local base, fr = name:match("^(.-_shadow%d)_(%d+)%.png$")
  if base then groups[base] = groups[base] or {}; table.insert(groups[base], tonumber(fr)) end
end
for base, frs in pairs(groups) do
  local ok, err = pcall(function()
    table.sort(frs)
    local first = Image{ fromFile = DST .. "cursed/" .. base .. "_" .. frs[1] .. ".png" }
    local spr = Sprite(first.width, first.height, ColorMode.RGB)
    for i, f in ipairs(frs) do
      if i > 1 then spr:newEmptyFrame(i) end
      spr:newCel(spr.layers[1], i, Image{ fromFile = DST .. "cursed/" .. base .. "_" .. f .. ".png" }, Point(0, 0))
      spr.frames[i].duration = 0.15
    end
    local tg = spr:newTag(1, #frs); tg.name = "loop"
    app.fs.makeAllDirectories(DST .. "cursed/anim")
    spr:saveAs(DST .. "cursed/anim/" .. base .. ".aseprite")
    app.command.ExportSpriteSheet{ ui=false, askOverwrite=false, type=SpriteSheetType.HORIZONTAL,
      textureFilename=DST .. "cursed/anim/" .. base .. ".png", dataFilename=DST .. "cursed/anim/" .. base .. ".json",
      dataFormat=SpriteSheetDataFormat.JSON_ARRAY, listTags=true, openGenerated=false }
    spr:close(); n = n + 1
  end)
  if not ok then log("FAIL group " .. base .. " " .. tostring(err)) end
end
log("DONE " .. n)
close()
