local M = {}

local function showFlash(message, ttl, sound, big)
    if guihooks and guihooks.trigger then
        guihooks.trigger('ScenarioFlashMessage', {{message, ttl, sound or 0, big ~= false}})
    end
end

local function startLights(data)
    local seconds = 5
    if jsonDecode and type(data) == 'string' and data ~= '' then
        local ok, decoded = pcall(jsonDecode, data)
        if ok and type(decoded) == 'table' and tonumber(decoded.seconds) then
            seconds = tonumber(decoded.seconds)
        end
    end
    seconds = math.max(1, math.min(10, math.floor(seconds)))

    showFlash('GET READY', 1.0, "Engine.Audio.playOnce('AudioGui', 'event:UI_Checkpoint')", true)
    for i = seconds, 1, -1 do
        local sound = "Engine.Audio.playOnce('AudioGui', 'event:UI_Countdown1')"
        if i == 2 then sound = "Engine.Audio.playOnce('AudioGui', 'event:UI_Countdown2')" end
        if i == 1 then sound = "Engine.Audio.playOnce('AudioGui', 'event:UI_Countdown3')" end
        showFlash(tostring(i), 1.0, sound, true)
    end
    showFlash('GO!', 2.0, "Engine.Audio.playOnce('AudioGui', 'event:UI_CountdownGo')", true)
end

if AddEventHandler then
    AddEventHandler('beamadmin:startlights', startLights, 'beamadmin_race_countdown_startlights')
end

M.startLights = startLights

return M
