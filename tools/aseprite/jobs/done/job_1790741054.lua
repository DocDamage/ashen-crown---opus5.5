local A = dofile("F:/Ashen Crown/The Ashen Crown/Repo/tools/aseprite/lib_ashen.lua")
local W = A.OUT .. "_work/"
local log, close = A.logger(A.OUT .. "_logs/job13_runefoundry.txt")
local function build(frames, w, h, durs, tags, outbase, cols, colors)
  local spr = Sprite(w, h, ColorMode.RGB)
  for i, p in ipairs(frames) do
    if i > 1 then spr:newEmptyFrame(i) end
    spr:newCel(spr.layers[1], i, Image{ fromFile = p }, Point(0, 0))
    spr.frames[i].duration = durs[i] / 1000
  end
  for _, t in ipairs(tags) do local tg = spr:newTag(t[2], t[3]); tg.name = t[1] end
  app.command.ColorQuantization{ ui=false, maxColors=colors, withAlpha=false }
  app.command.ChangePixelFormat{ format="indexed", dithering="none" }
  app.fs.makeAllDirectories(app.fs.filePath(outbase))
  spr:saveAs(outbase .. ".aseprite")
  app.command.ChangePixelFormat{ format="rgb" }
  if #frames > 1 then
    app.command.ExportSpriteSheet{ ui=false, askOverwrite=false, type=SpriteSheetType.ROWS, columns=cols,
      textureFilename=outbase .. ".png", dataFilename=outbase .. ".json", dataFormat=SpriteSheetDataFormat.JSON_ARRAY, listTags=true, openGenerated=false }
    app.fs.makeAllDirectories(outbase .. "_frames")
    for i = 1, #spr.frames do
      local img = Image(spr.width, spr.height, ColorMode.RGB); img:drawSprite(spr, i)
      img:saveAs(outbase .. "_frames/" .. string.format("%03d", i - 1) .. ".png")
    end
  else
    spr:saveCopyAs(outbase .. ".png")
  end
  spr:close()
end
local n = 0
local VE = {
  {"V09","V09_grove_colossus",22,276,273,{70,70,70,70,70,70,70,70,120,120,120,120,120,120,120,120,80,80,80,80,80,80},{{"appear",1,8},{"idle",9,16},{"vanish",17,22}}},
  {"V10","V10_thorn_queen",22,272,276,{70,70,70,70,70,70,70,70,120,120,120,120,120,120,120,120,80,80,80,80,80,80},{{"appear",1,8},{"idle",9,16},{"vanish",17,22}}},
  {"V11","V11_ash_wyrm",22,265,276,{70,70,70,70,70,70,70,70,120,120,120,120,120,120,120,120,80,80,80,80,80,80},{{"appear",1,8},{"idle",9,16},{"vanish",17,22}}},
  {"V12","V12_winter_wraith",22,276,276,{70,70,70,70,70,70,70,70,120,120,120,120,120,120,120,120,80,80,80,80,80,80},{{"appear",1,8},{"idle",9,16},{"vanish",17,22}}},
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
local BO = {
  {"03_verdant_elder_mossback_px.png",402,366},
  {"04_verdant_emerald_hydra_px.png",400,402},
  {"05_ashen_magma_tyrant_px.png",399,402},
  {"07_ashen_obsidian_devourer_px.png",402,373},
  {"08_ashen_cinder_demon_px.png",401,402},
  {"09_frostbound_glacier_behemoth_px.png",402,379},
  {"10_frostbound_frosthorn_titan_px.png",355,402},
  {"12_frostbound_boreal_leviathan_px.png",402,399},
}
for _, b in ipairs(BO) do
  local ok, err = pcall(function()
    build({W .. "rf_boss/" .. b[1]}, b[2], b[3], {100}, {}, A.OUT .. "bosses/RuneFoundry/" .. b[1]:gsub("%.png$", ""), 1, 48)
    log("boss " .. b[1]); n = n + 1
  end)
  if not ok then log("FAIL boss " .. b[1] .. " " .. tostring(err)) end
end
log("DONE " .. n)
close()
