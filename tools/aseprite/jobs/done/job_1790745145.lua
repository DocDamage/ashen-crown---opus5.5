-- Copy G:\All 2D Assets Stay Here\{characters,ansimuz} into the Assets folder (byte-for-byte, skips files already present with the same size)
local A = dofile("F:/Ashen Crown/The Ashen Crown/Repo/tools/aseprite/lib_ashen.lua")
local G = "G:/All 2D Assets Stay Here/"
local log, close = A.logger(A.OUT .. "_logs/job17_copy_from_G.txt")
local files, bytes, skipped, failed = 0, 0, 0, 0
local function copyfile(src, dst)
  if app.fs.isFile(dst) and app.fs.fileSize(dst) == app.fs.fileSize(src) then skipped = skipped + 1; return end
  local i = io.open(src, "rb"); if not i then failed = failed + 1; log("FAIL read " .. src); return end
  app.fs.makeAllDirectories(app.fs.filePath(dst))
  local o = io.open(dst, "wb"); if not o then i:close(); failed = failed + 1; log("FAIL write " .. dst); return end
  while true do
    local chunk = i:read(1048576)
    if not chunk then break end
    o:write(chunk); bytes = bytes + #chunk
  end
  i:close(); o:close(); files = files + 1
end
local function copytree(src, dst)
  app.fs.makeAllDirectories(dst)
  for _, name in ipairs(app.fs.listFiles(src)) do
    local s, d = app.fs.joinPath(src, name), app.fs.joinPath(dst, name)
    if app.fs.isDirectory(s) then copytree(s, d) else
      local ok, err = pcall(copyfile, s, d)
      if not ok then failed = failed + 1; log("FAIL " .. s .. " " .. tostring(err)) end
    end
  end
end
for _, folder in ipairs({"characters", "ansimuz"}) do
  local before = files
  copytree(G .. folder, A.B .. folder)
  log(folder .. ": copied " .. (files - before) .. " files")
end
log(string.format("DONE copied=%d skipped=%d failed=%d MB=%.1f", files, skipped, failed, bytes / 1048576))
close()
