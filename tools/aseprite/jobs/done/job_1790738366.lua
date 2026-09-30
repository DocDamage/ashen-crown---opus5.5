local A = dofile("F:/Ashen Crown/The Ashen Crown/Repo/tools/aseprite/lib_ashen.lua")
local W = A.OUT .. "_work/"
local log, close = A.logger(A.OUT .. "_logs/job9_townsfolk_herogaps.txt")
local SCALE = 62/46
local DIRS = {"south","west","east","north"}
local function build(frames, w, h, durs, tags, outbase, scale, cols)
  local spr = Sprite(w, h, ColorMode.RGB)
  local lay = spr.layers[1]
  for i, p in ipairs(frames) do
    if i > 1 then spr:newEmptyFrame(i) end
    local img = Image{ fromFile = p }
    spr:newCel(lay, i, img, Point(0, 0))
    spr.frames[i].duration = durs[i] / 1000
  end
  for _, t in ipairs(tags) do local tg = spr:newTag(t[2], t[3]); tg.name = t[1] end
  if scale and scale ~= 1 then
    app.command.SpriteSize{ ui=false, width=A.round(w*scale), height=A.round(h*scale), lockRatio=false, method="rotsprite" }
  end
  app.fs.makeAllDirectories(app.fs.filePath(outbase))
  spr:saveAs(outbase .. ".aseprite")
  app.command.ExportSpriteSheet{ ui=false, askOverwrite=false, type=SpriteSheetType.ROWS, columns=cols or 5,
    textureFilename=outbase .. ".png", dataFilename=outbase .. ".json", dataFormat=SpriteSheetDataFormat.JSON_ARRAY,
    listTags=true, splitTags=false, openGenerated=false }
  local fw, fh = spr.width, spr.height
  spr:close()
  return fw, fh
end
local n = 0

local TOWN = {
  {"cozy_village","village_kid_free",84,84},
  {"cozy_village","village_elder",96,96},
  {"cozy_village","shepherd_girl",92,92},
  {"cozy_village","village_farmer",96,96},
  {"cozy_village","caf_owner",88,88},
  {"cozy_village","village_baker",92,92},
  {"cozy_village","flower_gardener",92,92},
  {"cozy_village","fisherman",92,92},
  {"cozy_village","village_blacksmith",96,96},
  {"cozy_village","traveling_merchant",88,88},
  {"cozy_village","librarian",92,92},
  {"kingdom_citizens","village_blacksmith",92,92},
  {"kingdom_citizens","guild_receptionist",88,88},
  {"kingdom_citizens","traveling_merchant",92,92},
  {"kingdom_citizens","tavern_keeper",92,92},
  {"kingdom_citizens","royal_guard",96,96},
  {"kingdom_citizens","elder_scholar",92,92},
  {"kingdom_citizens","village_baker",92,92},
  {"kingdom_citizens","herbalist",84,84},
  {"kingdom_citizens","tavern_waitress",88,88},
  {"kingdom_citizens","noble_lady",92,92},
  {"beastfolk","wolf_ranger_male",96,96},
  {"beastfolk","snow_leopard_huntress_female",96,96},
  {"beastfolk","lion_paladin_male",96,96},
  {"beastfolk","bear_berserker_male",92,92},
  {"beastfolk","fox_shadowblade_male",92,92},
  {"beastfolk","tiger_samurai_male",92,92},
  {"beastfolk","cat_assassin_female",92,92},
  {"beastfolk","deer_druid_female",96,96},
  {"beastfolk","owl_sorceress_female",80,80},
  {"beastfolk","rabbit_elemental_mage_female",92,92},
  {"steampunk","iron_baron_male",96,96},
  {"steampunk","sky_navigator",92,92},
  {"steampunk","steam_knight_male",96,96},
  {"steampunk","clockwork_engineer_male",96,96},
  {"steampunk","airship_captain_male",92,92},
  {"steampunk","tesla_gunner_male",92,92},
  {"steampunk","steam_duchess_female",88,88},
  {"steampunk","clockwork_huntress_female",84,84},
  {"steampunk","gearblade_assassin",92,92},
  {"steampunk","arc_reactor_mage",92,92},
  {"steampunk","young_apprentice_engineer_free_character",84,84},
  {"samurai_yokai","samurai_warlord_male",92,92},
  {"samurai_yokai","spirit_yokai_priestess_female",96,96},
  {"samurai_yokai","shrine_maiden_warrior_female",92,92},
  {"samurai_yokai","ronin_blade_master_male",92,92},
  {"samurai_yokai","kitsune_assassin_female",96,96},
  {"samurai_yokai","imperial_shogun_male",92,92},
  {"samurai_yokai","moonlight_samurai_female",88,88},
  {"samurai_yokai","oni_hunter_male",92,92},
  {"samurai_yokai","sakura_blade_dancer_female",96,96},
  {"samurai_yokai","dragon_clan_samurai_male",96,96},
  {"frozen_kingdom","frozen_kingdom_ice_knight_male",92,92},
  {"frozen_kingdom","ice_blade_warrior_female",96,96},
  {"frozen_kingdom","frozen_valkyrie_female",96,96},
  {"frozen_kingdom","frost_assassin_male",92,92},
  {"frozen_kingdom","ice_witch_queen_female",96,96},
  {"frozen_kingdom","glacier_paladin_male",88,88},
  {"frozen_kingdom","snow_huntress_female",92,92},
  {"frozen_kingdom","frozen_berserker_male",96,96},
  {"frozen_kingdom","crystal_priestess_female",88,88},
  {"frozen_kingdom","frost_prince_male",92,92},
  {"atlantis","atlantis_recruit_free_character",96,96},
  {"atlantis","crystal_guardian",92,92},
  {"atlantis","stormcaller_champion",96,96},
  {"atlantis","crystal_blade_princess",92,92},
  {"atlantis","tide_priestess",92,92},
  {"atlantis","coral_huntress",96,96},
  {"atlantis","pearl_sentinel",88,88},
  {"atlantis","abyss_dancer",92,92},
  {"atlantis","royal_trident_knight",96,96},
  {"atlantis","ocean_vanguard",96,96},
  {"atlantis","sea_dragon_hunter",96,96},
  {"arcane","arcane_grand_wizard_male",92,92},
  {"arcane","arcane_spellblade_male",88,88},
  {"arcane","crimson_magic_queen_female",92,92},
  {"arcane","celestial_witch_female",92,92},
  {"arcane","fire_battlemage_male",96,96},
  {"arcane","shadow_sorceress_female",96,96},
  {"arcane","holy_archmage_male",92,92},
  {"arcane","frost_enchantress_female",88,88},
  {"arcane","necromancer_king_male",96,96},
  {"arcane","necromancer_king_2_male",88,88},
  {"arcane","nature_priestess_female",80,80},
  {"dark_dungeon","cursed_crypt_knight_male",96,96},
  {"dark_dungeon","moonless_spellweaver_female",88,88},
  {"dark_dungeon","ashen_torchbearer_male",88,88},
  {"dark_dungeon","bloodrune_executioner_male",92,92},
  {"dark_dungeon","shadow_dungeon_assassin_male",92,92},
  {"dark_dungeon","abyssal_necromancer_male",92,92},
  {"dark_dungeon","crimson_cathedral_priestess_female",92,92},
  {"dark_dungeon","nightshade_huntress_female",92,92},
  {"dark_dungeon","forbidden_alchemist_female",92,92},
  {"dark_dungeon","relic_valkyrie_of_the_abyss_female",92,92},
  {"enchanted_forest","emerald_forest_ranger",84,84},
  {"enchanted_forest","lunar_forest_archer",84,84},
  {"enchanted_forest","vineblade_dancer",88,88},
  {"enchanted_forest","fairy_queen_guardian",92,92},
  {"enchanted_forest","nature_oracle",88,88},
  {"enchanted_forest","serpent_forest_enchantress",92,92},
  {"enchanted_forest","ancient_antler_druid",92,92},
  {"enchanted_forest","moonleaf_assassin",92,92},
  {"enchanted_forest","wildfire_beast_hunter",88,88},
  {"enchanted_forest","mushroom_alchemist",96,96},
  {"enchanted_forest","thornblade_knight",96,96},
  {"enchanted_forest","spirit_wolf_shaman",92,92},
  {"enchanted_forest","blossom_priestess",88,88},
  {"enchanted_forest","butterfly_witch",92,92},
  {"dragonborn","young_dragon_squire_free",92,92},
  {"dragonborn","storm_dragon_warden",96,96},
  {"dragonborn","dragon_queen",92,92},
  {"dragonborn","dragon_emperor",92,92},
  {"dragonborn","dragon_paladin",92,92},
  {"dragonborn","dragon_berserker",92,92},
  {"dragonborn","dragon_flame_mage",88,88},
  {"dragonborn","dragon_huntress",96,96},
  {"dragonborn","dragon_assassin",92,92},
  {"dragonborn","dragon_priestess",96,96},
  {"dragonborn","dragon_guardian",96,96},
  {"vampire_hunters","crimson_vampire_hunter_male",88,88},
  {"vampire_hunters","raven_blood_priestess_female",92,92},
  {"vampire_hunters","holy_exorcist_nun_female",84,84},
  {"vampire_hunters","bloodborne_hunter_male",92,92},
  {"vampire_hunters","vampire_slayer_duchess_female",92,92},
  {"vampire_hunters","cursed_crossbow_hunter_male",92,92},
  {"vampire_hunters","moonlight_vampire_huntress_female",92,92},
  {"vampire_hunters","black_coffin_executioner_male",92,92},
  {"vampire_hunters","crimson_witch_hunter_female",92,92},
  {"vampire_hunters","holy_knight_of_dawn_male",96,96},
  {"infernal","demon_emperor",92,92},
  {"infernal","doom_vanguard",96,96},
  {"infernal","infernal_prince_free_character",88,88},
  {"infernal","infernal_warlord",96,96},
  {"infernal","succubus_queen",92,92},
  {"infernal","blood_priest",88,88},
  {"infernal","hell_knight",92,92},
  {"infernal","flame_sorcerer",96,96},
  {"infernal","abyssal_assassin",96,96},
  {"infernal","bone_champion",96,96},
  {"infernal","infernal_dragon_tamer",92,92},
  {"dark_gothic","dark_corrupted_female_knight_pixel",92,92},
  {"dark_gothic","dark_fantasy_gothic_knight_pixel",92,92},
  {"dark_gothic","dark_queen_pixel_art_gothic",92,92},
  {"dark_gothic","masterpiece_pixel_art_gothic_armored",92,92},
  {"dark_gothic","masterpiece_pixel_art_gothic_female",92,92},
  {"dark_gothic","pixel_art_demonic_gothic_warrior",96,96},
  {"dark_gothic","pixel_art_gothic_assassin_girl",92,92},
  {"dark_gothic","pixel_art_gothic_valkyrie_dark",92,92},
  {"dark_gothic","pixel_art_gothic_warrior_girl",96,96},
  {"dark_gothic","pixel_art_gothic_witch_dark",92,92},
  {"psych_horror","the_chained_executioner_male",92,92},
  {"psych_horror","the_blood_oracle_female",92,92},
  {"psych_horror","the_candle_priestess_female",92,92},
  {"psych_horror","the_bone_surgeon_male",92,92},
  {"psych_horror","the_weeping_nun_female",92,92},
  {"psych_horror","the_dungeon_jailer_male",88,88},
  {"psych_horror","the_spider_cultist_female",92,92},
  {"psych_horror","the_ashen_knight_male",92,92},
  {"psych_horror","the_mirror_witch_female",96,96},
  {"psych_horror","the_mad_prisoner_male",84,84},
}
for _, t in ipairs(TOWN) do
  local ok, err = pcall(function()
    local src = W .. "native/" .. t[1] .. "/" .. t[2] .. "/"
    local frames, durs, tags = {}, {}, {}
    for di, d in ipairs(DIRS) do
      local s = #frames + 1
      table.insert(frames, src .. d .. "_0.png"); table.insert(durs, 400)
      for k = 1, 4 do table.insert(frames, src .. d .. "_" .. k .. ".png"); table.insert(durs, 150) end
      table.insert(tags, {"stand_" .. d, s, s})
      table.insert(tags, {"walk_" .. d, s + 1, s + 4})
    end
    local fw, fh = build(frames, t[3], t[4], durs, tags, A.OUT .. "townsfolk/" .. t[1] .. "/" .. t[2], SCALE, 5)
    log("town " .. t[1] .. "/" .. t[2] .. " " .. fw .. "x" .. fh)
    n = n + 1
  end)
  if not ok then log("FAIL town " .. t[2] .. " " .. tostring(err)) end
end

local GAPS = {
  {"VELKHAR — Lord of the Dead","Victory_generated","east",10,124,124,{90,90,90,90,160,160,160,160,160,160},{{"intro",1,4},{"loop",5,10}}},
  {"VELKHAR — Lord of the Dead","Victory_generated","west",10,124,124,{90,90,90,90,160,160,160,160,160,160},{{"intro",1,4},{"loop",5,10}}},
  {"CORVUS_HARBINGER_OF_PESTILENCE","Victory_generated","east",15,120,120,{90,90,90,90,90,90,90,90,90,160,160,160,160,160,160},{{"intro",1,9},{"loop",10,15}}},
  {"CORVUS_HARBINGER_OF_PESTILENCE","Victory_generated","west",15,120,120,{90,90,90,90,90,90,90,90,90,160,160,160,160,160,160},{{"intro",1,9},{"loop",10,15}}},
  {"RUNE_GOLEM_GUARDIAN_OF","Death_generated","east",12,168,106,{80,80,80,80,140,140,200,90,90,90,70,400},{{"death",1,12}}},
  {"RUNE_GOLEM_GUARDIAN_OF","Death_generated","west",12,168,106,{80,80,80,80,140,140,200,90,90,90,70,400},{{"death",1,12}}},
  {"NIGHT_RIDER_URBAN_BIKER","Death_generated","east",12,184,88,{80,80,80,80,80,70,70,60,60,90,70,400},{{"death",1,12}}},
  {"NIGHT_RIDER_URBAN_BIKER","Death_generated","west",12,184,88,{80,80,80,80,80,70,70,60,60,90,70,400},{{"death",1,12}}},
  {"🔮 MORWEN — WITCH OF THE ECLIPSE","Victory_generated","east",15,124,124,{90,90,90,90,90,90,90,90,90,160,160,160,160,160,160},{{"intro",1,9},{"loop",10,15}}},
  {"🔮 MORWEN — WITCH OF THE ECLIPSE","Victory_generated","west",15,124,124,{90,90,90,90,90,90,90,90,90,160,160,160,160,160,160},{{"intro",1,9},{"loop",10,15}}},
  {"Archangel Commander — Legendary Celestial Warrior Hero","Victory_generated","east",10,128,128,{90,90,90,90,90,90,160,160,160,160},{{"intro",1,6},{"loop",7,10}}},
  {"Archangel Commander — Legendary Celestial Warrior Hero","Victory_generated","west",10,128,128,{90,90,90,90,90,90,160,160,160,160},{{"intro",1,6},{"loop",7,10}}},
  {"Crimson Oni Animated Samurai Hero!","Hurt_generated","east",7,125,125,{60,70,90,110,80,80,90},{{"hurt",1,7}}},
  {"Crimson Oni Animated Samurai Hero!","Hurt_generated","west",7,125,125,{60,70,90,110,80,80,90},{{"hurt",1,7}}},
  {"Crimson Oni Animated Samurai Hero!","Victory_generated","east",11,125,125,{90,90,90,90,90,160,160,160,160,160,160},{{"intro",1,5},{"loop",6,11}}},
  {"Crimson Oni Animated Samurai Hero!","Victory_generated","west",11,125,125,{90,90,90,90,90,160,160,160,160,160,160},{{"intro",1,5},{"loop",6,11}}},
  {"⚡ KAEL-09 — NEON BLADE OPERATIVE","Victory_generated","east",7,124,124,{90,90,90,90,90,160,160},{{"intro",1,5},{"loop",6,7}}},
  {"⚡ KAEL-09 — NEON BLADE OPERATIVE","Victory_generated","west",7,124,124,{90,90,90,90,90,160,160},{{"intro",1,5},{"loop",6,7}}},
  {"VESPERA — MOONHARE WARRIOR","Death_generated","east",12,184,88,{80,80,80,80,80,70,70,60,60,90,70,400},{{"death",1,12}}},
  {"VESPERA — MOONHARE WARRIOR","Death_generated","west",12,184,88,{80,80,80,80,80,70,70,60,60,90,70,400},{{"death",1,12}}},
  {"Crimson Kitsune Empress — Legendary Fox Spirit Samurai Hero","Hurt_generated","east",7,127,127,{60,70,90,110,80,80,90},{{"hurt",1,7}}},
  {"Crimson Kitsune Empress — Legendary Fox Spirit Samurai Hero","Hurt_generated","west",7,127,127,{60,70,90,110,80,80,90},{{"hurt",1,7}}},
  {"Crimson Kitsune Empress — Legendary Fox Spirit Samurai Hero","Victory_generated","east",6,127,127,{90,90,160,160,160,160},{{"intro",1,2},{"loop",3,6}}},
  {"Crimson Kitsune Empress — Legendary Fox Spirit Samurai Hero","Victory_generated","west",6,127,127,{90,90,160,160,160,160},{{"intro",1,2},{"loop",3,6}}},
  {"🐉 AUREX — DRAGONBLOOD CHAMPION","Victory_generated","east",8,128,128,{90,90,90,90,90,90,160,160},{{"intro",1,6},{"loop",7,8}}},
  {"🐉 AUREX — DRAGONBLOOD CHAMPION","Victory_generated","west",8,128,128,{90,90,90,90,90,90,160,160},{{"intro",1,6},{"loop",7,8}}},
  {"MALDRATH — THE FALLEN KING","Victory_generated","east",10,128,128,{90,90,90,90,90,90,160,160,160,160},{{"intro",1,6},{"loop",7,10}}},
  {"MALDRATH — THE FALLEN KING","Victory_generated","west",10,128,128,{90,90,90,90,90,90,160,160,160,160},{{"intro",1,6},{"loop",7,10}}},
}
for _, g in ipairs(GAPS) do
  local ok, err = pcall(function()
    local src = W .. "out/" .. g[1] .. "/" .. g[2] .. "/" .. g[3] .. "/"
    local dst = A.OUT .. "heroes_battle_gaps/" .. g[1] .. "/" .. g[2] .. "/"
    local frames = {}
    for i = 0, g[4] - 1 do table.insert(frames, src .. string.format("frame_%03d.png", i)) end
    build(frames, g[5], g[6], g[7], g[8], dst .. g[2] .. "_" .. g[3], 1, g[4])
    log("gap " .. g[1] .. " " .. g[2] .. " " .. g[3])
    n = n + 1
  end)
  if not ok then log("FAIL gap " .. g[1] .. " " .. g[2] .. " " .. tostring(err)) end
end
log("DONE " .. n)
close()
