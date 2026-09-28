local resolve=bmd.scriptapp("Resolve")
assert(resolve,"Open Resolve first")
local manager=resolve:GetProjectManager()
local original=manager:GetCurrentProject()
local originalName=original and original:GetName() or nil
local output=[==[C:/Users/jordan/Desktop/Edit/analysis/editing-style/fusion-templates/]==]
local targets={"R6 Unlock Arctic","tenny FN","MW4 Video"}

for _,projectName in ipairs(targets) do
 local project=manager:LoadProject(projectName)
 if project then
  local timeline=project:GetCurrentTimeline()
  print("PROJECT "..projectName.." TIMELINE "..(timeline and timeline:GetName() or "NONE"))
  local exportedShake=false
  local exportedZoom=false
  local toolCounts={}
  local fusionItems=0
  if timeline then
   for track=1,timeline:GetTrackCount("video") do
    for _,item in ipairs(timeline:GetItemListInTrack("video",track) or {}) do
     for compIndex=1,item:GetFusionCompCount() or 0 do
      local comp=item:GetFusionCompByIndex(compIndex)
      local ids={}
      if comp then
       for _,tool in pairs(comp:GetToolList(false) or {}) do
        local attrs=tool:GetAttrs() or {}
        local id=tostring(attrs.TOOLS_RegID or "Unknown")
        ids[id]=true;toolCounts[id]=(toolCounts[id] or 0)+1
       end
      end
      local labels={};for id,_ in pairs(ids) do table.insert(labels,id) end;table.sort(labels)
      fusionItems=fusionItems+1
      print(string.format(" ITEM t=%d start=%d dur=%d name=%s tools=%s",track,item:GetStart(),item:GetDuration(),item:GetName(),table.concat(labels,",")))
      if not exportedShake and ids.CameraShake then
       local safe=projectName:gsub("[^%w]+","-"):lower()
       local path=output..safe.."-camera-shake.comp"
       if item:ExportFusionComp(path,compIndex) then print(" EXPORTED "..path);exportedShake=true end
      end
      if not exportedZoom and ids["ofx.com.blackmagicdesign.resolvefx.Transform"] and item:GetName():lower():match("%.mp4$") then
       local safe=projectName:gsub("[^%w]+","-"):lower()
       local path=output..safe.."-zoom.comp"
       if item:ExportFusionComp(path,compIndex) then print(" EXPORTED "..path);exportedZoom=true end
      end
     end
    end
   end
  end
  local totals={};for id,count in pairs(toolCounts) do table.insert(totals,id.."="..count) end;table.sort(totals)
  print(" SUMMARY comps="..fusionItems.." "..table.concat(totals," "))
 else print("PROJECT_MISSING "..projectName) end
end

if originalName then manager:LoadProject(originalName) end
print("RESTORED "..tostring(originalName))
