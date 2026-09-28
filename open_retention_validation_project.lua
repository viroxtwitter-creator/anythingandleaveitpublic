local resolve=assert(bmd.scriptapp('Resolve'),'Resolve is still starting')
local manager=assert(resolve:GetProjectManager())
local project=manager:GetCurrentProject()
if not project or project:GetName()=='Untitled Project' then project=manager:LoadProject('twst4') end
assert(project,'Could not open the existing twst4 project')
print('RETENTION_VALIDATION_PROJECT '..project:GetName())
