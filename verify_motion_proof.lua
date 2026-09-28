local resolve=bmd.scriptapp("Resolve")
local project=resolve:GetProjectManager():GetCurrentProject()
assert(project and project:GetName()=="test2")
local timeline=project:GetCurrentTimeline()
assert(timeline and timeline:GetName()=="AUTO MOTION PROOF - Jordan Fusion zooms")
local items=timeline:GetItemListInTrack("video",1) or {}
assert(#items==85)
for _,index in ipairs({73,78,82}) do
 local item=items[index]
 assert(item:GetFusionCompCount()==1,"Expected one generated comp on clip "..index)
 local comp=item:GetFusionCompByIndex(1)
 assert(comp:FindTool("Transform1"),"Missing Transform1 on clip "..index)
 local path=string.format([==[C:/Users/jordan/Desktop/Edit/analysis/editing-style/motion-proof-%d.comp]==],index)
 assert(item:ExportFusionComp(path,1),"Could not export proof comp")
 print("VERIFIED_ZOOM "..index.." "..item:GetDuration())
end
print("MOTION_PROOF_VERIFIED 3")
