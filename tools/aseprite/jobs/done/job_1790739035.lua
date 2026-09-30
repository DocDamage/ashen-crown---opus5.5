local A = dofile("F:/Ashen Crown/The Ashen Crown/Repo/tools/aseprite/lib_ashen.lua")
local W = A.OUT .. "_work/"
local log, close = A.logger(A.OUT .. "_logs/job10_scenery_vestiges.txt")
local function build(frames, w, h, durs, tags, outbase, cols, colors)
  local spr = Sprite(w, h, ColorMode.RGB)
  local lay = spr.layers[1]
  for i, p in ipairs(frames) do
    if i > 1 then spr:newEmptyFrame(i) end
    spr:newCel(lay, i, Image{ fromFile = p }, Point(0, 0))
    spr.frames[i].duration = durs[i] / 1000
  end
  for _, t in ipairs(tags) do local tg = spr:newTag(t[2], t[3]); tg.name = t[1] end
  if colors then
    app.command.ColorQuantization{ ui=false, maxColors=colors, withAlpha=false }
    app.command.ChangePixelFormat{ format="indexed", dithering="none" }
  end
  app.fs.makeAllDirectories(app.fs.filePath(outbase))
  spr:saveAs(outbase .. ".aseprite")
  if colors then app.command.ChangePixelFormat{ format="rgb" } end
  app.command.ExportSpriteSheet{ ui=false, askOverwrite=false, type=SpriteSheetType.ROWS, columns=cols,
    textureFilename=outbase .. ".png", dataFilename=outbase .. ".json", dataFormat=SpriteSheetDataFormat.JSON_ARRAY,
    listTags=true, openGenerated=false }
  -- also individual frames
  app.fs.makeAllDirectories(outbase .. "_frames")
  for i = 1, #spr.frames do
    local img = Image(spr.width, spr.height, ColorMode.RGB)
    img:drawSprite(spr, i)
    img:saveAs(outbase .. "_frames/" .. string.format("%03d", i - 1) .. ".png")
  end
  spr:close()
end
local n = 0
local SC = {
  {"torch_wall",6,48,96,100},
  {"brazier",6,48,96,100},
  {"campfire",6,48,48,100},
  {"candelabra",4,48,48,140},
  {"chimney_smoke",8,48,96,130},
  {"flag_crown_red",6,48,96,110},
  {"flag_blue",6,48,96,110},
  {"banner_wall_red",4,48,96,180},
  {"banner_wall_blue",4,48,96,180},
  {"water_deep",4,48,48,220},
  {"water_shallow",4,48,48,220},
  {"shore_foam_top",4,48,48,220},
  {"waterfall_top",6,48,48,90},
  {"waterfall_body",6,48,48,90},
  {"waterfall_base",6,48,48,90},
}
for _, s in ipairs(SC) do
  local ok, err = pcall(function()
    local frames, durs = {}, {}
    for i = 0, s[2] - 1 do table.insert(frames, W .. "scenery/" .. s[1] .. "/" .. s[1] .. "_" .. i .. ".png"); table.insert(durs, s[5]) end
    build(frames, s[3], s[4], durs, {{"loop", 1, s[2]}}, A.OUT .. "field_anim/" .. s[1], s[2], nil)
    log("scenery " .. s[1]); n = n + 1
  end)
  if not ok then log("FAIL scenery " .. s[1] .. " " .. tostring(err)) end
end
local VE = {
  {"V01","V01_ember_moth",22,282,268,{70,70,70,70,70,70,70,70,120,120,120,120,120,120,120,120,80,80,80,80,80,80},{{"appear",1,8},{"idle",9,16},{"vanish",17,22}}},
  {"V02","V02_rootstag",22,262,274,{70,70,70,70,70,70,70,70,120,120,120,120,120,120,120,120,80,80,80,80,80,80},{{"appear",1,8},{"idle",9,16},{"vanish",17,22}}},
  {"V03","V03_tide_serpent",22,244,260,{70,70,70,70,70,70,70,70,120,120,120,120,120,120,120,120,80,80,80,80,80,80},{{"appear",1,8},{"idle",9,16},{"vanish",17,22}}},
  {"V04","V04_sky_griffon",22,264,233,{70,70,70,70,70,70,70,70,120,120,120,120,120,120,120,120,80,80,80,80,80,80},{{"appear",1,8},{"idle",9,16},{"vanish",17,22}}},
  {"V05","V05_lumen_fox",22,276,268,{70,70,70,70,70,70,70,70,120,120,120,120,120,120,120,120,80,80,80,80,80,80},{{"appear",1,8},{"idle",9,16},{"vanish",17,22}}},
  {"V06","V06_iron_tortoise",22,282,252,{70,70,70,70,70,70,70,70,120,120,120,120,120,120,120,120,80,80,80,80,80,80},{{"appear",1,8},{"idle",9,16},{"vanish",17,22}}},
  {"V07","V07_winter_hind",22,240,266,{70,70,70,70,70,70,70,70,120,120,120,120,120,120,120,120,80,80,80,80,80,80},{{"appear",1,8},{"idle",9,16},{"vanish",17,22}}},
  {"V08","V08_night_leviathan",22,232,268,{70,70,70,70,70,70,70,70,120,120,120,120,120,120,120,120,80,80,80,80,80,80},{{"appear",1,8},{"idle",9,16},{"vanish",17,22}}},
}
for _, v in ipairs(VE) do
  local ok, err = pcall(function()
    local frames = {}
    for i = 0, v[3] - 1 do table.insert(frames, W .. "vestiges/" .. v[1] .. "/frames/" .. string.format("%03d", i) .. ".png") end
    build(frames, v[4], v[5], v[6], v[7], A.OUT .. "vestiges/" .. v[2], 8, 64)
    log("vestige " .. v[2]); n = n + 1
  end)
  if not ok then log("FAIL vestige " .. v[2] .. " " .. tostring(err)) end
end
log("DONE " .. n)
close()
