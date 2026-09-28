local resolve=bmd.scriptapp("Resolve")
local project=assert(resolve:GetProjectManager():GetCurrentProject(),"No project")
local wanted="AUTO - Fortnite 2026.09.05 - 20.55.01.01 - 2026-09-06 23-51-17"
local timeline=nil
for i=1,project:GetTimelineCount() do
 local candidate=project:GetTimelineByIndex(i)
 if candidate:GetName()==wanted then timeline=candidate break end
end
assert(timeline,"Newest strict AUTO timeline not found")
assert(project:SetCurrentTimeline(timeline))
local marks={
 {5495,"oh my god"},{8554,"oh my god"},{14745,"oh my god"},
 {19051,"oh my god"},{22066,"oh my god"}
}
for i,m in ipairs(marks) do
 local custom="retention-cut-auto-zoom-"..i
 if not timeline:GetMarkerByCustomData(custom) then
  assert(timeline:AddMarker(m[1],"Purple","AUTO ZOOM "..i,"Fusion punch zoom · "..m[2],1,custom),"Could not add zoom marker "..i)
 end
end
local absolute=timeline:GetStartFrame()+marks[1][1]
local fps=60
local hours=math.floor(absolute/(fps*3600));absolute=absolute-hours*fps*3600
local minutes=math.floor(absolute/(fps*60));absolute=absolute-minutes*fps*60
local seconds=math.floor(absolute/fps);local frames=absolute-seconds*fps
local tc=string.format("%02d:%02d:%02d:%02d",hours,minutes,seconds,frames)
assert(timeline:SetCurrentTimecode(tc),"Could not move to first zoom")
print("AUTO_ZOOM_MARKERS_VERIFIED 5 first="..tc)
