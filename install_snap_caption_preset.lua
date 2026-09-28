local resolve=bmd.scriptapp("Resolve");local project=resolve:GetProjectManager():GetCurrentProject();assert(project)
local pool=project:GetMediaPool();local root=pool:GetRootFolder();local snap=nil;local preset=nil
local function scan(folder)
 if folder:GetName():lower():gsub("%s","")=="snapcaptions" then
  snap=folder
  for _,clip in ipairs(folder:GetClipList() or {}) do if clip:GetName()=="Text+" and clip:GetClipProperty("Type")~="Timeline" then preset=clip end end
 end
 for _,child in ipairs(folder:GetSubFolderList() or {}) do scan(child) end
end
scan(root)
if not preset then
 local carrier=pool:ImportTimelineFromFile([==[C:/Users/jordan/Desktop/Edit/analysis/editing-style/Snap Captions Preset.drt]==],{timelineName="__AUTO SNAP PRESET IMPORT__",importSourceClips=true})
 assert(carrier,"Could not import Snap Captions preset carrier")
 local candidates={}
 local function findImported(folder)
  for _,clip in ipairs(folder:GetClipList() or {}) do
   if clip:GetName()=="Text+" and clip:GetClipProperty("Type")~="Timeline" and clip:GetClipProperty("File Path")=="" then table.insert(candidates,clip) end
  end
  for _,child in ipairs(folder:GetSubFolderList() or {}) do findImported(child) end
 end
 findImported(root);assert(#candidates>0,"Imported carrier did not include Text+ preset")
 if not snap then snap=pool:AddSubFolder(root,"Snap Captions");assert(snap) end
 preset=candidates[#candidates];assert(pool:MoveClips({preset},snap),"Could not move Text+ preset")
 assert(pool:DeleteTimelines({carrier}),"Could not remove preset carrier timeline")
end
print("SNAP_PRESET_READY "..project:GetName().." "..preset:GetName())
