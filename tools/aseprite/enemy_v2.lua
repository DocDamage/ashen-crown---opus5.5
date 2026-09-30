-- Enemy art v2 (step 2): for each entry in Assets/_processed/enemies_v2/manifest.json:
--   resize the cut-out source to its battle size, harden the alpha (no soft halos), reduce the palette to hard-edged
--   pixel art (painted packs get fewer colours), then build a 10-frame strip:
--   idle 0-3 (breathing), attack 4-6 (wind-up, lunge, recover), cast 7-8 (rise), hurt 9 (recoil).
-- Output: _processed/enemies_v2/out/<id>.png + <id>.json. Called by jobs made with tools/art/enemy_job.py.
local A = dofile("F:/Ashen Crown/The Ashen Crown/Repo/tools/aseprite/lib_ashen.lua")
local ROOT = A.OUT .. "enemies_v2/"
local M = {}

local FR = {
  {1.000, 1.000, 0, 0}, {0.994, 1.012, 0, 0}, {0.988, 1.024, 0, 0}, {0.994, 1.012, 0, 0},
  {1.020, 0.980, -4, 0}, {1.040, 1.000, 10, 0}, {1.020, 1.000, 4, 0},
  {1.000, 1.010, 0, -3}, {1.000, 1.020, 0, -6},
  {0.980, 1.000, -7, 0},
}
local TAGS = { idle = {0, 3}, attack = {4, 6}, cast = {7, 8}, hurt = {9, 9} }

local function harden(img)
  for it in img:pixels() do
    local c = it()
    local a = app.pixelColor.rgbaA(c)
    if a < 128 then it(0) else
      it(app.pixelColor.rgba(app.pixelColor.rgbaR(c), app.pixelColor.rgbaG(c), app.pixelColor.rgbaB(c), 255))
    end
  end
end

-- painted art gets a dark 1px outline (edge pixels darkened) so it sits with the pixel-art packs
local function outline(img)
  local w, h = img.width, img.height
  local pc = app.pixelColor
  local src = img:clone()
  local function opaque(x, y)
    if x < 0 or y < 0 or x >= w or y >= h then return false end
    return pc.rgbaA(src:getPixel(x, y)) > 0
  end
  for y = 0, h - 1 do
    for x = 0, w - 1 do
      if opaque(x, y) and (not opaque(x - 1, y) or not opaque(x + 1, y) or not opaque(x, y - 1) or not opaque(x, y + 1)) then
        local c = src:getPixel(x, y)
        img:drawPixel(x, y, pc.rgba(math.floor(pc.rgbaR(c) * 0.35), math.floor(pc.rgbaG(c) * 0.35), math.floor(pc.rgbaB(c) * 0.4), 255))
      end
    end
  end
end

function M.run(ids, log)
  local man = json.decode(io.open(ROOT .. "manifest.json"):read("a"))
  app.fs.makeAllDirectories(ROOT .. "out")
  local n = 0
  for _, id in ipairs(ids) do
    local e = man[id]
    local ok, err = pcall(function()
      local s = A.open1(ROOT .. "src/" .. id .. ".png")
      if s.colorMode ~= ColorMode.RGB then app.command.ChangePixelFormat{ format="rgb" } end
      app.command.SpriteSize{ ui=false, width=e.w, height=e.h, lockRatio=false, method=e.method }
      app.command.FlattenLayers{}
      local img = s.cels[1].image
      harden(img)
      app.command.ColorQuantization{ ui=false, maxColors=e.colors, withAlpha=false }
      app.command.ChangePixelFormat{ format="indexed", dithering="none" }
      app.command.ChangePixelFormat{ format="rgb" }
      if e.painted then outline(s.cels[1].image) end
      local cel = s.cels[1]
      local base = Image(s.width, s.height, ColorMode.RGB)
      base:drawImage(cel.image, cel.position)
      local cw = math.ceil(e.w * 1.06) + 24
      local ch = math.ceil(e.h * 1.03) + 8
      local out = Image(cw * #FR, ch, ColorMode.RGB)
      for i, f in ipairs(FR) do
        local fw = math.max(1, A.round(e.w * f[1]))
        local fh = math.max(1, A.round(e.h * f[2]))
        local fi = base:clone()
        fi:resize{ width=fw, height=fh, method="nearest" }
        local x = (i - 1) * cw + math.floor((cw - fw) / 2) + f[3]
        local y = ch - 2 - fh + f[4]
        out:drawImage(fi, Point(x, y))
      end
      out:saveAs(ROOT .. "out/" .. id .. ".png")
      s:close()
      local meta = { cell = {cw, ch}, frames = #FR, foot = {math.floor(cw / 2), ch - 2}, tags = TAGS, w = e.w, h = e.h }
      local f = io.open(ROOT .. "out/" .. id .. ".json", "w"); f:write(json.encode(meta)); f:close()
      n = n + 1
    end)
    if not ok then log("FAIL " .. id .. " " .. tostring(err)) end
    while app.sprite do app.sprite:close() end
  end
  log("DONE " .. n .. "/" .. #ids)
end
return M
