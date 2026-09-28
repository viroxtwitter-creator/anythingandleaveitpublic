local resolve=bmd.scriptapp("Resolve")
assert(resolve,"Open Resolve first")
local manager=resolve:GetProjectManager()
local project=manager:GetCurrentProject()
assert(project,"Open a project first")
print("PROJECT "..project:GetName())
local timeline=project:GetCurrentTimeline()
if timeline then
 print("TIMELINE "..timeline:GetName().." "..timeline:GetTrackCount("video"))
 for track=1,timeline:GetTrackCount("video") do
  for _,item in ipairs(timeline:GetItemListInTrack("video",track) or {}) do
   local count=item:GetFusionCompCount() or 0
   if count>0 then
    print(string.format("ITEM %d %s %d %d comps=%d",track,item:GetName(),item:GetStart(),item:GetDuration(),count))
    for index,name in ipairs(item:GetFusionCompNameList() or {}) do
     print(" COMP "..index.." "..tostring(name))
    end
   end
  end
 end
end
print("PROJECTS")
for _,name in ipairs(manager:GetProjectListInCurrentFolder() or {}) do print(" "..name) end
