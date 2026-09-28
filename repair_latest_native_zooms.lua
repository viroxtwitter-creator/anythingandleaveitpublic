local resolve=bmd.scriptapp("Resolve")
local project=assert(resolve:GetProjectManager():GetCurrentProject(),"No project")
local wanted="AUTO - Fortnite 2026.09.05 - 20.55.01.01 - 2026-09-06 23-51-17"
local timeline=nil
for i=1,project:GetTimelineCount() do
 local candidate=project:GetTimelineByIndex(i)
 if candidate:GetName()==wanted or candidate:GetName()=='REPAIRED - Fortnite - Fusion zooms' then timeline=candidate break end
end
if not timeline then
 timeline=assert(project:GetMediaPool():ImportTimelineFromFile('C:/Users/jordan/Desktop/Edit/exports/Automatic cut 20260906-235116-95700/Automatic cut.drt'),"Could not restore saved edit")
 timeline:SetName('REPAIRED - Fortnite - Fusion zooms')
end
assert(project:SetCurrentTimeline(timeline))
local items=timeline:GetItemListInTrack("video",1) or {}
local repaired=0
for _,index in ipairs({32,52,92,119,140}) do
 local item=assert(items[index],"Missing zoom clip "..index)
 local names=item:GetFusionCompNameList() or {}
 local oldName=nil
 for _,name in ipairs(names) do if name=="AUTO - Jordan punch zoom" then oldName=name break end end
 assert(oldName,"Missing generated Fusion comp on clip "..index)
 local oldComp=item:GetFusionCompByIndex(1);if oldComp then pcall(function() oldComp:Unlock() end) end
 local comp=assert(oldComp,"Missing composition")
 comp:Lock()
 local mediaIn=assert(comp:FindTool("MediaIn1"),"Missing MediaIn1")
 local mediaOut=assert(comp:FindTool("MediaOut1"),"Missing MediaOut1")
 for _,tool in pairs(comp:GetToolList(false) or {}) do
  if tool.ID=="ofx.com.blackmagicdesign.resolvefx.Transform" then tool:Delete() end
 end
 local transform=comp:FindTool('Transform1')
 if not transform then transform=assert(comp:AddTool("Transform",0,0),"Could not add native Fusion Transform") end
 transform.Input=mediaIn.Output
 mediaOut.Input=transform.Output
 local frames=item:GetDuration()
 local first=math.max(0,math.floor(frames*4/172+.5))
 local accent=math.max(first+1,math.floor(frames*21/172+.5))
 local finish=math.max(accent+1,frames-4)
 local scale=frames/172
 local curve=comp:BezierSpline();transform.Size=curve
 curve:SetKeyFrames({
  [first]={1.000,RH={9.66666666666667*scale-first,0}},
  [accent]={1.186,LH={15.3339000940323*scale-accent,1.17332037399091-1.186},RH={69.9950136494165*scale-accent,1.29564128054473-1.186}},
  [finish]={1.367,LH={119*scale-finish,0}}
 })
 transform.MotionBlur=1
 comp:Unlock()
 assert(transform.ID=="Transform","Native Transform verification failed")
 assert(transform:GetInput("Size",first)==1,"Zoom start verification failed")
 assert(transform:GetInput("Size",accent)==1.186,"Zoom accent verification failed")
 assert(transform:GetInput("Size",finish)==1.367,"Zoom finish verification failed")
 assert(transform.Input:GetConnectedOutput():GetTool().Name==mediaIn.Name,"Wrong source connection")
 assert(mediaOut.Input:GetConnectedOutput():GetTool().Name==transform.Name,"Wrong output connection")
 assert(item:ExportFusionComp('C:/Users/jordan/Desktop/Edit/analysis/editing-style/repaired-native-'..index..'.comp',1))
 repaired=repaired+1
end
print("AUTO_NATIVE_ZOOMS_REPAIRED "..repaired)
