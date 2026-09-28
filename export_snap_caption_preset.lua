local resolve=bmd.scriptapp("Resolve");local manager=resolve:GetProjectManager()
local original=manager:GetCurrentProject();local originalName=original and original:GetName() or nil
local project=manager:LoadProject("tenny FN");assert(project,"Open tenny FN reference project")
local pool=project:GetMediaPool();local preset=nil
local function walk(folder)
 if folder:GetName()=="Snap Captions" then
  for _,clip in ipairs(folder:GetClipList() or {}) do if clip:GetName()=="Text+" then preset=clip;return end end
 end
 for _,child in ipairs(folder:GetSubFolderList() or {}) do walk(child);if preset then return end end
end
walk(pool:GetRootFolder());assert(preset,"Text+ preset missing from tenny FN/Snap Captions")
local timeline=pool:CreateTimelineFromClips("__AUTO SNAP PRESET EXPORT__",{preset});assert(timeline,"Could not create preset carrier")
local path=[==[C:/Users/jordan/Desktop/Edit/analysis/editing-style/Snap Captions Preset.drt]==]
assert(timeline:Export(path,resolve.EXPORT_DRT),"Could not export preset carrier")
assert(pool:DeleteTimelines({timeline}),"Could not remove generated preset carrier")
if originalName then manager:LoadProject(originalName) end
print("SNAP_PRESET_EXPORTED "..path)
