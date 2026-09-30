-- Cutscene stills and title art: owner images in Assets/Stills/<id>.(png|jpg|webp) -> _processed/stills/<id>.png
-- Centre-crop to 4:3, resize to 320x240, reduce to a 48-colour palette with no dithering (the game's SNES look).
local A = dofile("F:/Ashen Crown/The Ashen Crown/Repo/tools/aseprite/lib_ashen.lua")
local M = {}

function M.one(src, dst, log)
  local s = A.open1(src)
  if not s then log("FAIL open " .. src); return end
  if s.colorMode ~= ColorMode.RGB then app.command.ChangePixelFormat{ format="rgb" } end
  app.command.FlattenLayers{ visibleOnly=true }
  local w, h = s.width, s.height
  local cw, ch = w, math.floor(w * 3 / 4)
  if ch > h then ch = h; cw = math.floor(h * 4 / 3) end
  s:crop(math.floor((w - cw) / 2), math.floor((h - ch) / 2), cw, ch)
  s:resize(320, 240)
  app.command.ColorQuantization{ ui=false, withAlpha=false, maxColors=48, useRange=false, algorithm=0 }
  app.command.ChangePixelFormat{ format="indexed", dithering="none" }
  app.command.ChangePixelFormat{ format="rgb" }
  app.fs.makeAllDirectories(app.fs.filePath(dst))
  s:saveCopyAs(dst)
  s:close()
  log("OK " .. dst)
end

function M.run(log)
  local dir = A.B .. "Stills/"
  if not app.fs.isDirectory(dir) then log("no Stills folder"); log("DONE"); return end
  for _, name in ipairs(app.fs.listFiles(dir)) do
    local ext = string.lower(app.fs.fileExtension(name))
    if ext == "png" or ext == "jpg" or ext == "jpeg" or ext == "webp" or ext == "bmp" then
      M.one(dir .. name, A.OUT .. "stills/" .. app.fs.fileTitle(name) .. ".png", log)
    end
  end
  log("DONE")
end
return M
