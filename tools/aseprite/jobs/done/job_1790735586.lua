-- Job 7 (test): airship pixelation variants
local L0 = dofile("F:/Ashen Crown/The Ashen Crown/Repo/tools/aseprite/lib_ashen.lua")
local log, close = L0.logger(L0.OUT .. "_logs/job7_airship_test.txt")
local S = L0.OUT .. "airships/_slices/"
local T = L0.OUT .. "_test/air/"
app.fs.makeAllDirectories(T)
for _, f in ipairs({ "wayfarer/topdown_south_0", "wayfarer/side_fly_0", "lanternwake/side_fly_0" }) do
  local tag = f:gsub("/", "_")
  local function run(v, fn)
    local s = L0.open1(S .. f .. ".png")
    local ok, e = pcall(fn, s)
    if not ok then log(tag .. " " .. v .. " ERR " .. tostring(e)) end
    s:saveCopyAs(T .. tag .. "_" .. v .. ".png"); s:close()
  end
  run("q32", function(s)
    app.command.ColorQuantization{ ui=false, maxColors=32, withAlpha=false }
    app.command.ChangePixelFormat{ format="indexed", dithering="none" }
    app.command.ChangePixelFormat{ format="rgb" }
  end)
  run("q32a", function(s)
    app.command.ColorQuantization{ ui=false, maxColors=32, withAlpha=true }
    app.command.ChangePixelFormat{ format="indexed", dithering="none" }
    app.command.ChangePixelFormat{ format="rgb" }
  end)
  run("half", function(s)
    local w, h = s.width, s.height
    app.command.SpriteSize{ ui=false, width=L0.round(w/2), height=L0.round(h/2), lockRatio=false, method="bilinear" }
    app.command.SpriteSize{ ui=false, width=L0.round(w/2)*2, height=L0.round(h/2)*2, lockRatio=false, method="nearest" }
  end)
end
log("done"); close()
