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
local items=timeline:GetItemListInTrack("video",1) or {}
for _,index in ipairs({32,52,92,119,140}) do
 local item=assert(items[index],"Missing clip "..index)
 print(string.format("CLIP %d start=%d duration=%d comps=%d",index,item:GetStart(),item:GetDuration(),item:GetFusionCompCount()))
 for ci,name in ipairs(item:GetFusionCompNameList() or {}) do
  print(" COMP "..ci.." "..tostring(name))
  local comp=item:GetFusionCompByIndex(ci)
  for _,tool in pairs(comp:GetToolList(false) or {}) do
   print("  TOOL "..tostring(tool.Name).." id="..tostring(tool.ID))
   if tostring(tool.ID):find("Transform") then
    local frames=item:GetDuration();local first=math.max(0,math.floor(frames*4/172+.5));local accent=math.max(first+1,math.floor(frames*21/172+.5));local finish=math.max(accent+1,frames-4)
    local function value(id,time) local v=tool:GetInput(id,time);return tostring(v) end
    print(string.format("   zoom lower=%s/%s/%s upper=%s/%s/%s",value("zoom",first),value("zoom",accent),value("zoom",finish),value("Zoom",first),value("Zoom",accent),value("Zoom",finish)))
    for id,input in pairs(tool:GetInputList() or {}) do print("   INPUT "..tostring(id).." name="..tostring(input.Name)) end
   end
  end
  local path=string.format("C:/Users/jordan/Desktop/Edit/analysis/editing-style/latest-motion-%d.comp",index)
  print(" EXPORT "..tostring(item:ExportFusionComp(path,ci)).." "..path)
 end
end
