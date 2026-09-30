local A = dofile("F:/Ashen Crown/The Ashen Crown/Repo/tools/aseprite/lib_ashen.lua")
local log, close = A.logger(A.OUT .. "_logs/ping.txt")
log("pong " .. tostring(app.version))
close()
