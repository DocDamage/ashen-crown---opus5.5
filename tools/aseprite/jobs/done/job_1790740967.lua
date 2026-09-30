local A = dofile("F:/Ashen Crown/The Ashen Crown/Repo/tools/aseprite/lib_ashen.lua")
local W = A.OUT .. "_work/brackhorn/"
local log, close = A.logger(A.OUT .. "_logs/job12_brackhorn.txt")
local frames = {"walk_south_0","walk_south_1","walk_south_2","walk_south_3","walk_south_4","walk_south_5","walk_south_6","walk_southwest_0","walk_southwest_1","walk_southwest_2","walk_southwest_3","walk_southwest_4","walk_southwest_5","walk_west_0","walk_west_1","walk_west_2","walk_west_3","walk_west_4","walk_northwest_0","walk_northwest_1","walk_northwest_2","walk_northwest_3","walk_northwest_4","walk_northwest_5","walk_north_0","walk_north_1","walk_north_2","walk_north_3","walk_north_4","walk_north_5","walk_north_6","walk_northeast_0","walk_northeast_1","walk_northeast_2","walk_northeast_3","walk_northeast_4","walk_northeast_5","walk_east_0","walk_east_1","walk_east_2","walk_east_3","walk_east_4","walk_southeast_0","walk_southeast_1","walk_southeast_2","walk_southeast_3","walk_southeast_4","walk_southeast_5","run_south_0","run_south_1","run_south_2","run_south_3","run_south_4","run_south_5","run_southwest_0","run_southwest_1","run_southwest_2","run_southwest_3","run_southwest_4","run_southwest_5","run_west_0","run_west_1","run_west_2","run_west_3","run_west_4","run_northwest_0","run_northwest_1","run_northwest_2","run_northwest_3","run_northwest_4","run_northwest_5","run_north_0","run_north_1","run_north_2","run_north_3","run_north_4","run_north_5","run_northeast_0","run_northeast_1","run_northeast_2","run_northeast_3","run_northeast_4","run_northeast_5","run_east_0","run_east_1","run_east_2","run_east_3","run_east_4","run_southeast_0","run_southeast_1","run_southeast_2","run_southeast_3","run_southeast_4","run_southeast_5"}
local durs = {110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,110,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80}
local tags = {{"walk_south",1,7},{"walk_southwest",8,13},{"walk_west",14,18},{"walk_northwest",19,24},{"walk_north",25,31},{"walk_northeast",32,37},{"walk_east",38,42},{"walk_southeast",43,48},{"run_south",49,54},{"run_southwest",55,60},{"run_west",61,65},{"run_northwest",66,71},{"run_north",72,77},{"run_northeast",78,83},{"run_east",84,88},{"run_southeast",89,94}}
local spr = Sprite(128, 96, ColorMode.RGB)
for i, p in ipairs(frames) do
  if i > 1 then spr:newEmptyFrame(i) end
  spr:newCel(spr.layers[1], i, Image{ fromFile = W .. p .. ".png" }, Point(0, 0))
  spr.frames[i].duration = durs[i] / 1000
end
for _, t in ipairs(tags) do local tg = spr:newTag(t[2], t[3]); tg.name = t[1] end
app.command.ColorQuantization{ ui=false, maxColors=32, withAlpha=false }
app.command.ChangePixelFormat{ format="indexed", dithering="none" }
local out = A.OUT .. "mount/brackhorn"
app.fs.makeAllDirectories(A.OUT .. "mount")
spr:saveAs(out .. ".aseprite")
app.command.ChangePixelFormat{ format="rgb" }
app.command.ExportSpriteSheet{ ui=false, askOverwrite=false, type=SpriteSheetType.ROWS, columns=7,
  textureFilename=out .. ".png", dataFilename=out .. ".json", dataFormat=SpriteSheetDataFormat.JSON_ARRAY, listTags=true, openGenerated=false }
app.fs.makeAllDirectories(out .. "_frames")
for i = 1, #spr.frames do
  local img = Image(spr.width, spr.height, ColorMode.RGB); img:drawSprite(spr, i)
  img:saveAs(out .. "_frames/" .. frames[i] .. ".png")
end
spr:close()
log("DONE " .. #frames)
close()
