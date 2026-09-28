local resolve=bmd.scriptapp("Resolve")
local project=resolve:GetProjectManager():GetCurrentProject()
assert(project and project:GetName()=="test2")
local timeline=project:GetCurrentTimeline()
assert(timeline and timeline:GetName()=="AUTO MOTION PROOF - Jordan Fusion zooms")
local items=timeline:GetItemListInTrack("video",1) or {}
local targets={{73,"oh my god"},{78,"pretty insane"},{82,"pretty insane"}}
for _,target in ipairs(targets) do
 local item=items[target[1]];assert(item)
 for _,name in ipairs(item:GetFusionCompNameList() or {}) do
  assert(item:DeleteFusionCompByName(name),"Could not replace generated proof comp")
 end
 local frames=item:GetDuration();local comp=item:AddFusionComp();assert(comp)
 comp:Lock()
 local mediaIn=comp:FindTool("MediaIn1");local mediaOut=comp:FindTool("MediaOut1")
 local transform=comp:AddTool("ofx.com.blackmagicdesign.resolvefx.Transform",0,0);assert(transform)
 transform.Source=mediaIn.Output;mediaOut.Input=transform.Output
 local first=math.max(0,math.floor(frames*4/172+.5))
 local accent=math.max(first+1,math.floor(frames*21/172+.5))
 local finish=math.max(accent+1,frames-4)
 local scale=frames/172
 local curve=comp:BezierSpline();transform.zoom=curve
 curve:SetKeyFrames({
  [first]={1.000,RH={9.66666666666667*scale-first,0}},
  [accent]={1.186,LH={15.3339000940323*scale-accent,1.17332037399091-1.186},RH={69.9950136494165*scale-accent,1.29564128054473-1.186}},
  [finish]={1.367,LH={119*scale-finish,0}}
 })
 transform.motionBlur=1;comp:Unlock()
 local old=(item:GetFusionCompNameList() or {})[item:GetFusionCompCount()]
 if old then item:RenameFusionCompByName(old,"AUTO - Jordan punch zoom") end
 print(string.format("REPAIRED_ZOOM %d frames=%d keys=%d,%d,%d",target[1],frames,first,accent,finish))
end
print("MOTION_PROOF_REPAIRED 3")
