local resolve=bmd.scriptapp("Resolve")
local project=resolve:GetProjectManager():GetCurrentProject()
assert(project and project:GetName()=="twst4")
local timeline=project:GetCurrentTimeline();assert(timeline and timeline:GetName():match("^AUTO %- Fortnite"))
local item=(timeline:GetItemListInTrack("video",1) or {})[34];assert(item and item:GetFusionCompCount()==0)
local frames=item:GetDuration();local comp=item:AddFusionComp();assert(comp);comp:Lock()
local mediaIn=comp:FindTool("MediaIn1");local mediaOut=comp:FindTool("MediaOut1")
local transform=comp:AddTool("ofx.com.blackmagicdesign.resolvefx.Transform",0,0);assert(transform)
transform.Source=mediaIn.Output;mediaOut.Input=transform.Output
local first=math.max(0,math.floor(frames*4/172+.5));local accent=math.max(first+1,math.floor(frames*21/172+.5));local finish=math.max(accent+1,frames-4);local scale=frames/172
local curve=comp:BezierSpline();transform.zoom=curve
curve:SetKeyFrames({[first]={1.000,RH={9.66666666666667*scale,1.000}},[accent]={1.186,LH={15.3339000940323*scale,1.17332037399091},RH={69.9950136494165*scale,1.29564128054473}},[finish]={1.367,LH={119*scale,1.367}}})
transform.motionBlur=1;comp:Unlock()
local old=(item:GetFusionCompNameList() or {})[item:GetFusionCompCount()];if old then item:RenameFusionCompByName(old,"AUTO - Jordan punch zoom") end
assert(item:ExportFusionComp([==[C:/Users/jordan/Desktop/Edit/analysis/editing-style/fortnite-motion-probe.comp]==],1))
print(string.format("MOTION_CURVE_PROBE_OK %d %d %d %d",frames,first,accent,finish))
