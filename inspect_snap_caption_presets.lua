local resolve=bmd.scriptapp("Resolve");local manager=resolve:GetProjectManager()
local original=manager:GetCurrentProject();local originalName=original and original:GetName() or nil
for _,projectName in ipairs({"TEMPLATE","tenny FN","R6 Unlock Arctic","MW4 Video"}) do
 local project=manager:LoadProject(projectName)
 if project then
  print("PROJECT "..projectName)
  local function walk(folder,depth)
   print(string.rep(" ",depth).."FOLDER "..folder:GetName())
   for _,clip in ipairs(folder:GetClipList() or {}) do
    print(string.rep(" ",depth+1).."CLIP "..clip:GetName().." type="..tostring(clip:GetClipProperty("Type")).." format="..tostring(clip:GetClipProperty("Format")))
   end
   for _,child in ipairs(folder:GetSubFolderList() or {}) do walk(child,depth+1) end
  end
  walk(project:GetMediaPool():GetRootFolder(),0)
 end
end
if originalName then manager:LoadProject(originalName) end
print("RESTORED "..tostring(originalName))
