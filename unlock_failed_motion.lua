local resolve=bmd.scriptapp("Resolve")
assert(resolve)
local fusion=resolve:Fusion()
local comp=fusion and fusion:GetCurrentComp() or nil
if comp then comp:Unlock();print("UNLOCKED_CURRENT_COMP") else print("NO_CURRENT_COMP") end
local project=resolve:GetProjectManager():GetCurrentProject();local timeline=project:GetCurrentTimeline()
print("VIDEO_ITEMS "..#(timeline:GetItemListInTrack("video",1) or {}))
