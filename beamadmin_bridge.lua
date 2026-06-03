local PLUGIN = "beamadmin_bridge"
local BASE_DIR = "Resources/Server/beamadmin_bridge"
local QUEUE_FILE = BASE_DIR .. "/queue.json"
local STATUS_FILE = BASE_DIR .. "/status.json"
local BANS_FILE = BASE_DIR .. "/bans.json"
local RESULTS_FILE = BASE_DIR .. "/results.log"
local TICK_EVENT = "beamadmin.bridge.tick"

local bans = {
    names = {},
    ips = {},
}

local function log(message)
    print("[" .. PLUGIN .. "] " .. tostring(message))
end

local function now()
    if os and os.time then return os.time() end
    return 0
end

local function trim(value)
    local text = tostring(value or "")
    text = text:gsub("[%c\r\n\t]", " ")
    text = text:gsub("^%s+", ""):gsub("%s+$", "")
    return text
end

local function lower(value)
    return trim(value):lower()
end

local function ensureDir()
    if FS and FS.Exists and FS.CreateDirectory and not FS.Exists(BASE_DIR) then
        FS.CreateDirectory(BASE_DIR)
    end
end

local function readJson(path, fallback)
    local handle = io.open(path, "r")
    if not handle then return fallback end
    local text = handle:read("*a")
    handle:close()
    if not text or text == "" then return fallback end
    local ok, decoded = pcall(function() return Util.JsonDecode(text) end)
    if ok and decoded ~= nil then return decoded end
    return fallback
end

local function writeJson(path, payload)
    local handle = io.open(path, "w")
    if not handle then return false end
    handle:write(Util.JsonEncode(payload))
    handle:close()
    return true
end

local function appendResult(commandId, ok, message)
    local handle = io.open(RESULTS_FILE, "a")
    if handle then
        handle:write(Util.JsonEncode({
            at = now(),
            commandId = commandId or "",
            ok = ok and true or false,
            message = tostring(message or "")
        }) .. "\n")
        handle:close()
    end
end

local function getIdentifiers(playerId)
    local ok, identifiers = pcall(function() return MP.GetPlayerIdentifiers(playerId) end)
    if ok and type(identifiers) == "table" then return identifiers end
    return {}
end

local function getPlayers()
    local ok, players = pcall(function() return MP.GetPlayers() end)
    if ok and type(players) == "table" then return players end
    return {}
end

local function findPlayer(command)
    local wantedId = tonumber(command.playerId)
    local wantedName = lower(command.playerName)
    for playerId, playerName in pairs(getPlayers()) do
        if (wantedId and tonumber(playerId) == wantedId) or (wantedName ~= "" and lower(playerName) == wantedName) then
            return tonumber(playerId), playerName
        end
    end
    return nil, nil
end

local function saveBans()
    writeJson(BANS_FILE, bans)
end

local function loadBans()
    local decoded = readJson(BANS_FILE, bans)
    if type(decoded) == "table" then
        bans.names = type(decoded.names) == "table" and decoded.names or {}
        bans.ips = type(decoded.ips) == "table" and decoded.ips or {}
    end
end

local function writeStatus()
    local players = {}
    for playerId, playerName in pairs(getPlayers()) do
        local identifiers = getIdentifiers(playerId)
        table.insert(players, {
            id = tostring(playerId),
            name = tostring(playerName or ""),
            ip = tostring(identifiers.ip or ""),
            beammp = tostring(identifiers.beammp or ""),
        })
    end
    writeJson(STATUS_FILE, {
        seenAt = now(),
        playerCount = #players,
        players = players,
        bans = bans,
    })
end

local function executeCommand(command)
    local action = tostring(command.action or "")
    local reason = trim(command.reason)
    if reason == "" then reason = "Admin action from BeamAdmin" end

    if action == "unban" then
        local name = lower(command.playerName)
        if name ~= "" then bans.names[name] = nil end
        saveBans()
        return true, "unbanned " .. tostring(command.playerName or "")
    end

    local playerId, playerName = findPlayer(command)
    if not playerId then
        return false, "player not found"
    end

    if action == "kick" then
        MP.DropPlayer(playerId, reason)
        return true, "kicked " .. tostring(playerName)
    end

    if action == "ban" then
        local identifiers = getIdentifiers(playerId)
        local key = lower(playerName)
        if key ~= "" then bans.names[key] = reason end
        if identifiers.ip and tostring(identifiers.ip) ~= "" then bans.ips[tostring(identifiers.ip)] = reason end
        saveBans()
        MP.DropPlayer(playerId, reason)
        return true, "banned " .. tostring(playerName)
    end

    return false, "unknown action"
end

local function processQueue()
    local queue = readJson(QUEUE_FILE, {})
    if type(queue) ~= "table" or #queue == 0 then return end
    writeJson(QUEUE_FILE, {})
    for _, command in ipairs(queue) do
        local ok, success, message = pcall(function()
            local commandOk, commandMessage = executeCommand(command)
            return commandOk, commandMessage
        end)
        if ok then
            appendResult(command.id, success, message)
            log(tostring(message))
        else
            appendResult(command.id, false, success)
            log("command failed: " .. tostring(success))
        end
    end
end

function onInit()
    ensureDir()
    loadBans()
    writeStatus()
    MP.RegisterEvent(TICK_EVENT, "onBeamAdminBridgeTick")
    MP.RegisterEvent("onPlayerAuth", "onPlayerAuth")
    pcall(function() MP.CancelEventTimer(TICK_EVENT) end)
    MP.CreateEventTimer(TICK_EVENT, 2000)
    log("loaded")
end

function onShutdown()
    pcall(function() MP.CancelEventTimer(TICK_EVENT) end)
    writeStatus()
end

function onBeamAdminBridgeTick()
    processQueue()
    writeStatus()
end

function onPlayerAuth(playerName, playerRole, isGuest, identifiers)
    loadBans()
    local nameKey = lower(playerName)
    local ip = ""
    if type(identifiers) == "table" then ip = tostring(identifiers.ip or "") end
    if nameKey ~= "" and bans.names[nameKey] then
        return "You are banned from this server: " .. tostring(bans.names[nameKey])
    end
    if ip ~= "" and bans.ips[ip] then
        return "You are banned from this server: " .. tostring(bans.ips[ip])
    end
end
