local resolve=bmd.scriptapp("Resolve")
assert(resolve,"Open Resolve first")
local project=resolve:GetProjectManager():GetCurrentProject()
assert(project and project:GetName()=="test2","Motion proof is restricted to the test2 project")
local source=project:GetCurrentTimeline()
assert(source and source:GetName():match("^AUTO %- Modern Warfare 4"),"Select the MW4 AUTO timeline")
local name="AUTO MOTION PROOF - Jordan Fusion zooms"
local timeline=source:DuplicateTimeline(name)
assert(timeline,"Could not duplicate the automatic timeline")
project:SetCurrentTimeline(timeline)
local items=timeline:GetItemListInTrack("video",1) or {}
assert(#items==85,"Unexpected video clip count; original timeline was not changed")

-- These are transcript-confirmed reaction clips in the current proof recording:
-- 73 = "oh my god", 78 and 82 = "pretty insane".
local targets={{73,"oh my god"},{78,"pretty insane"},{82,"pretty insane"}}
for _,target in ipairs(targets) do
 local item=items[target[1]]
 local frames=item:GetDuration()
 assert(frames>=60,"Reaction clip is too short for the reference zoom")
 local comp=item:AddFusionComp()
 assert(comp,"Could not add Fusion composition")
 comp:Lock()
 local mediaIn=comp:FindTool("MediaIn1")
 local mediaOut=comp:FindTool("MediaOut1")
 assert(mediaIn and mediaOut,"Fusion clip has no MediaIn/MediaOut")
 local transform=comp:AddTool("ofx.com.blackmagicdesign.resolvefx.Transform",0,0)
 assert(transform,"ResolveFX Transform is unavailable")
 transform.Source=mediaIn.Output
 mediaOut.Input=transform.Output
 -- Normalized from the MW4 reference's frames 4/21/168 and values
 -- 1.000/1.186/1.367, so it retains the same shape on shorter clips.
 local first=math.max(0,math.floor(frames*4/172+.5))
 local accent=math.max(first+1,math.floor(frames*21/172+.5))
 local finish=math.max(accent+1,frames-4)
 local curve=comp:BezierSpline()
 transform.zoom=curve
 local scale=frames/172
 curve:SetKeyFrames({
  [first]={1.000,RH={9.66666666666667*scale-first,0}},
  [accent]={1.186,LH={15.3339000940323*scale-accent,1.17332037399091-1.186},RH={69.9950136494165*scale-accent,1.29564128054473-1.186}},
  [finish]={1.367,LH={119*scale-finish,0}}
 })
 transform.motionBlur=1
 comp:Unlock()
 local old=(item:GetFusionCompNameList() or {})[item:GetFusionCompCount()]
 if old then item:RenameFusionCompByName(old,"AUTO - Jordan punch zoom") end
 print(string.format("MOTION_ZOOM %d %s frames=%d keys=%d,%d,%d",target[1],target[2],frames,first,accent,finish))
end
assert(timeline:GetEndFrame()-timeline:GetStartFrame()==source:GetEndFrame()-source:GetStartFrame(),"Motion changed timeline duration")
print("MOTION_PROOF_OK "..timeline:GetName().." 3")
