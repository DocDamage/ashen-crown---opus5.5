-- Shared helpers for Ashen Crown Aseprite batch jobs.
local M = {}
M.B = "F:/Ashen Crown/The Ashen Crown/Assets/"
M.OUT = M.B .. "_processed/"

function M.logger(path)
  app.fs.makeAllDirectories(app.fs.filePath(path))
  local f = io.open(path, "w")
  return function(s) f:write(s .. "\n"); f:flush() end, function() f:close() end
end

-- open exactly one file (never as a numbered sequence)
function M.open1(path)
  app.command.OpenFile{ ui=false, filename=path, oneframe=true }
  local s = app.sprite
  if s and app.fs.normalizePath(s.filename) == app.fs.normalizePath(path) then return s end
  return s
end

function M.walk(dir, fn, rel)
  rel = rel or ""
  for _, name in ipairs(app.fs.listFiles(dir)) do
    local p = app.fs.joinPath(dir, name)
    local r = (rel == "") and name or (rel .. "/" .. name)
    if app.fs.isDirectory(p) then M.walk(p, fn, r) else fn(p, r) end
  end
end

function M.round(x) return math.floor(x + 0.5) end
return M
