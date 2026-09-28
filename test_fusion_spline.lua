local resolve=bmd.scriptapp("Resolve")
local project=resolve:GetProjectManager():GetCurrentProject()
assert(project and project:GetName()=="test2")
local timeline=project:GetCurrentTimeline()
assert(timeline and timeline:GetName()=="AUTO MOTION PROOF - Jordan Fusion zooms")
local item=(timeline:GetItemListInTrack("video",1) or {})[73]
local comp=item:GetFusionCompByIndex(1)
local transform=comp and comp:FindTool("Transform1")
assert(transform)
comp:Lock()
transform.zoom=comp:BezierSpline()
transform.zoom[2]=1.000
transform.zoom[12]=1.186
transform.zoom[91]=1.367
comp:Unlock()
assert(item:ExportFusionComp([==[C:/Users/jordan/Desktop/Edit/analysis/editing-style/motion-spline-test.comp]==],1))
print("FUSION_SPLINE_TEST_WRITTEN")
