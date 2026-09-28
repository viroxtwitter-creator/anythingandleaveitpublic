local resolve = bmd.scriptapp("Resolve")
local project = assert(resolve:GetProjectManager():GetCurrentProject(), "No project is open")
local timeline = nil
for i = 1, project:GetTimelineCount() do
  local candidate = project:GetTimelineByIndex(i)
  if candidate:GetName():match("^AUTO %- Fortnite") and candidate:GetEndFrame() - candidate:GetStartFrame() == 23705 then
    timeline = candidate
  end
end
assert(timeline, "Could not find the completed 6:35 AUTO timeline")
assert(project:SetCurrentTimeline(timeline), "Could not select the completed AUTO timeline")

local original = {}
for i = 1, timeline:GetTrackCount("audio") do
  original[i] = timeline:GetIsTrackEnabled("audio", i)
  assert(timeline:SetTrackEnable("audio", i, i == 2))
end

local ok, created = pcall(function()
  return timeline:CreateSubtitlesFromAudio({
    [resolve.SUBTITLE_LANGUAGE] = resolve.AUTO_CAPTION_ENGLISH,
    [resolve.SUBTITLE_CHARS_PER_LINE] = 15,
    [resolve.SUBTITLE_LINE_BREAK] = resolve.AUTO_CAPTION_LINE_SINGLE,
    [resolve.SUBTITLE_GAP] = 0
  })
end)
for i, state in ipairs(original) do timeline:SetTrackEnable("audio", i, state) end
assert(ok and created, "Resolve could not create subtitles from the microphone audio")

local track = timeline:GetTrackCount("subtitle")
local items = timeline:GetItemListInTrack("subtitle", track) or {}
assert(#items > 0, "Resolve created no subtitle clips")
assert(timeline:GetEndFrame() - timeline:GetStartFrame() == 23705, "Subtitles changed the edit length")
print("AUTO_NATIVE_SUBTITLES_VERIFIED " .. #items .. " timeline=" .. timeline:GetName())
