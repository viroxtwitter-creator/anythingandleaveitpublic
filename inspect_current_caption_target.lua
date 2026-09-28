local resolve = bmd.scriptapp("Resolve")
local project = assert(resolve:GetProjectManager():GetCurrentProject(), "No current project")
print("PROJECT " .. project:GetName())
for i = 1, project:GetTimelineCount() do
  local timeline = project:GetTimelineByIndex(i)
  print(string.format("TIMELINE %d %s duration=%d current=%s", i, timeline:GetName(), timeline:GetEndFrame() - timeline:GetStartFrame(), tostring(project:GetCurrentTimeline() == timeline)))
end
local function walk(folder)
  if folder:GetName():lower():gsub("%s", "") == "snapcaptions" then
    print("SNAP_FOLDER " .. folder:GetName())
    for _, clip in ipairs(folder:GetClipList() or {}) do
      print("SNAP_ITEM " .. clip:GetName() .. " type=" .. tostring(clip:GetClipProperty("Type")) .. " path=" .. tostring(clip:GetClipProperty("File Path")))
    end
  end
  for _, child in ipairs(folder:GetSubFolderList() or {}) do walk(child) end
end
walk(project:GetMediaPool():GetRootFolder())
