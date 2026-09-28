local resolve=bmd.scriptapp('Resolve')
local project=assert(resolve:GetProjectManager():GetCurrentProject())
local timeline=nil
for i=1,project:GetTimelineCount() do
 local t=project:GetTimelineByIndex(i)
 if t:GetName()=='REPAIRED - Fortnite - Fusion zooms' then timeline=t break end
end
assert(timeline,'Repaired timeline not found')
local count=0
for _,item in ipairs(timeline:GetItemListInTrack('video',1) or {}) do
 for _,name in ipairs(item:GetFusionCompNameList() or {}) do
  if name=='AUTO - Jordan punch zoom' then
   count=count+1
   local key='retention-cut-auto-zoom-'..count
   local existing=timeline:GetMarkerByCustomData(key)
   if not existing then
    assert(timeline:AddMarker(item:GetStart()-timeline:GetStartFrame(),'Purple','AUTO ZOOM '..count,
     'Fusion punch zoom: 1.000 to 1.367. Open this clip in Fusion to edit.',1,key))
   end
   assert(timeline:GetMarkerByCustomData(key),'Marker verification failed')
  end
 end
end
assert(count==5,'Expected five zooms')
assert(timeline:Export('C:/Users/jordan/Desktop/Edit/exports/Repaired Fortnite Fusion zooms.drt',resolve.EXPORT_DRT))
assert(resolve:GetProjectManager():SaveProject())
print('ZOOM_MARKERS_VERIFIED '..count)
