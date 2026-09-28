local resolve = bmd.scriptapp("Resolve")
local project = assert(resolve:GetProjectManager():GetCurrentProject())
for i = 1, project:GetTimelineCount() do
  local timeline = project:GetTimelineByIndex(i)
  print("TIMELINE " .. i .. " " .. timeline:GetName())
  for track = 1, timeline:GetTrackCount("video") do
    for _, item in ipairs(timeline:GetItemListInTrack("video", track) or {}) do
      local media = item:GetMediaPoolItem()
      print(string.format(" ITEM track=%d name=%s start=%s duration=%s media=%s", track, item:GetName(), tostring(item:GetStart()), tostring(item:GetDuration()), tostring(media)))
      if media then
        print("  MEDIA name=" .. tostring(media:GetName()) .. " type=" .. tostring(media:GetClipProperty("Type")) .. " path=" .. tostring(media:GetClipProperty("File Path")))
      end
      local comp = item:GetFusionCompByIndex(1)
      print("  COMP " .. tostring(comp))
      if comp then
        for _, tool in pairs(comp:GetToolList(false) or {}) do print("   TOOL " .. tostring(tool.Name) .. " " .. tostring(tool.ID)) end
      end
    end
  end
end
