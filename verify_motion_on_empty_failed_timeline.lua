local resolve=bmd.scriptapp("Resolve")
local project=resolve:GetProjectManager():GetCurrentProject();assert(project and project:GetName()=="twst4")
local timeline=project:GetCurrentTimeline();assert(timeline)
local existing=timeline:GetItemListInTrack("video",1) or {}
local pool=project:GetMediaPool();local found=nil
local function walk(folder)
 for _,clip in ipairs(folder:GetClipList() or {}) do
  local path=clip:GetClipProperty("File Path") or ""
  if path:find("Fortnite 2026.09.05 %- 20.55.01.01.mp4",1,false) then found=clip;return end
 end
 for _,child in ipairs(folder:GetSubFolderList() or {}) do walk(child);if found then return end end
end
walk(pool:GetRootFolder());assert(found,"Imported Fortnite source not found")
local clips=timeline:GetItemListInTrack("video",1) or {}
if #clips==0 then clips=pool:AppendToTimeline({{mediaPoolItem=found,startFrame=0,endFrame=204,mediaType=1,trackIndex=1,recordFrame=timeline:GetStartFrame()}}) end
assert(clips and #clips==1);local item=clips[1];local frames=item:GetDuration()
local comp=item:AddFusionComp();assert(comp);comp:Lock()
local mediaIn=comp:FindTool("MediaIn1");local mediaOut=comp:FindTool("MediaOut1");assert(mediaIn and mediaOut)
local transform=comp:AddTool("ofx.com.blackmagicdesign.resolvefx.Transform",0,0);assert(transform)
transform.Source=mediaIn.Output;mediaOut.Input=transform.Output
local first=5;local accent=25;local finish=frames-4;local scale=frames/172
local curve=comp:BezierSpline();transform.zoom=curve
curve:SetKeyFrames({[first]={1.000,RH={9.66666666666667*scale-first,0}},[accent]={1.186,LH={15.3339000940323*scale-accent,1.17332037399091-1.186},RH={69.9950136494165*scale-accent,1.29564128054473-1.186}},[finish]={1.367,LH={119*scale-finish,0}}})
transform.motionBlur=1;comp:Unlock()
local finalIndex=item:GetFusionCompCount()
assert(item:ExportFusionComp([==[C:/Users/jordan/Desktop/Edit/analysis/editing-style/live-motion-verification.comp]==],finalIndex))
print("LIVE_MOTION_TEST_OK "..frames.." comp="..finalIndex)
