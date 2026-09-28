local resolve=bmd.scriptapp("Resolve")
local project=resolve:GetProjectManager():GetCurrentProject();local timeline=project:GetCurrentTimeline()
local items=timeline:GetItemListInTrack("video",1) or {}
print("STATE "..project:GetName().." "..timeline:GetName().." items="..#items)
for _,kind in ipairs({"video","audio","subtitle"}) do
 print("TRACKS "..kind.."="..timeline:GetTrackCount(kind))
 for track=1,timeline:GetTrackCount(kind) do print(" TRACK "..kind..track.." items="..#(timeline:GetItemListInTrack(kind,track) or {})) end
end
for _,index in ipairs({34,54,77,97,123,145}) do
 local item=items[index]
 print(string.format("ITEM %d %s dur=%s comps=%s",index,item and item:GetName() or "nil",item and item:GetDuration() or "nil",item and item:GetFusionCompCount() or "nil"))
end
