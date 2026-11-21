local Helpers = require("UEHelpers")
local prefix = "r.Streamline.DLSSNR."
local folder = assert(os.getenv("LOCALAPPDATA")) .. "\\acr\\Saved\\"
local settings = {
    {name = "Enable", default = 1, min = 0, max = 1},
    {name = "Intensity", default = 1, min = 0, max = 1, float = true},
    {name = "Passes", default = 3, min = 1, max = 3},
    {name = "ExtraPassIntensityScale", default = 1, min = 0, max = 1, float = true},
    {name = "Style", min = 0, max = 2},
    {name = "ToneStrength", min = 0, max = 1, float = true},
    {name = "StructuralStrength", min = 0, max = 1, float = true},
}

local pending = false
local lastStatus
local lastWrite = 0

local function requestedValues()
    local values = {}
    local file = io.open(folder .. "ACRNeuralRendering-control.txt", "r")
    if file then
        for line in file:lines() do
            local key, value = line:match("^(%w+)=([%d.]+)%s*$")
            if key then values[key] = tonumber(value) end
        end
        file:close()
    end
    return values
end

local function report(status)
    if status ~= lastStatus then
        print("[ACRNeuralRendering] " .. status .. "\n")
        lastStatus = status
    end
end

local function apply()
    local controller = Helpers.GetPlayerController()
    if not controller or not controller:IsValid() then return end

    local system = StaticFindObject("/Script/Engine.Default__KismetSystemLibrary")
    if not system or not system:IsValid() then return end

    local values = {}
    local requested = requestedValues()
    local matched = true
    for _, setting in ipairs(settings) do
        local name = prefix .. setting.name
        local target = requested[setting.name]
        if not target or target < setting.min or target > setting.max
            or (not setting.float and target % 1 ~= 0) then
            target = setting.default
        end
        local function read()
            if setting.float then return system:GetConsoleVariableFloatValue(name) end
            return system:GetConsoleVariableIntValue(name)
        end

        local actual = read()
        if target and math.abs(actual - target) > 0.0001 then
            system:ExecuteConsoleCommand(controller, name .. " " .. tostring(target), controller)
            actual = read()
        end
        matched = matched and (not target or math.abs(actual - target) <= 0.0001)
        values[#values + 1] = setting.name .. "=" .. tostring(actual)
    end
    local status = (matched and "Verified CVars: " or "CVar override incomplete: ") .. table.concat(values, ", ")
    local now = os.time()
    if status ~= lastStatus or now ~= lastWrite then
        local file = io.open(folder .. "ACRNeuralRendering-status.txt", "w")
        if file then
            file:write(status, "\n")
            file:close()
            lastWrite = now
        end
    end
    report(status)
end

LoopAsync(200, function()
    if pending then return false end
    pending = true
    local scheduled, err = pcall(ExecuteInGameThread, function()
        local ok, reason = pcall(apply)
        pending = false
        if not ok then report(tostring(reason)) end
    end)
    if not scheduled then
        pending = false
        report(tostring(err))
    end
    return false
end)
