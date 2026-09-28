-- Adapter for the locally installed Snap Captions; the plugin file is unchanged.
do
local captionTimeline=timeline
local captionProject=project
local function guard()
 assert(resolve:GetProjectManager():GetCurrentProject():GetUniqueId()==captionProject:GetUniqueId(), 'Project changed; captions stopped')
 assert(project:GetCurrentTimeline():GetUniqueId()==captionTimeline:GetUniqueId(), 'Timeline changed; captions stopped')
end
local templates={}
local function findTemplates(folder)
 local normalized=folder:GetName():lower():gsub('%s','')
 if normalized=='snapcaptions' then
  for _,c in ipairs(folder:GetClipList()) do
   if c:GetClipProperty('File Path')=='' and c:GetClipProperty('Type')~='Timeline' then
    if c:GetName()=='Text+' then table.insert(templates,1,c) else table.insert(templates,c) end
   end
  end
 end
 for _,f in ipairs(folder:GetSubFolderList()) do findTemplates(f) end
end
findTemplates(pool:GetRootFolder())
local fh=assert(io.open('SNAP_PLUGIN_PATH','r'));local source=fh:read('*a');fh:close()
local function section(first,last)
 local a=assert(source:find(first,1,true),'Unsupported Snap Captions version')
 local b=assert(source:find(last,a+#first,true),'Unsupported Snap Captions version')
 return source:sub(a,b-1)
end
local converter=section('local function ToTitleCase(', 'local function GenerateTextPlus(')
-- Resolve 20 uses exclusive end frames in this installation.
converter=converter:gsub('testDuration %- 1','testDuration')
converter=converter:gsub('subtitle%["duration"%] %- 1','subtitle["duration"]')
converter=converter:gsub('newClip%["endFrame"%] %- newClip%["startFrame"%] %+ 1','newClip["endFrame"] - newClip["startFrame"]')
converter=converter:gsub('base_duration %* duration_multiplier %+ 0%.999','math.floor(base_duration * duration_multiplier + 0.5)')
converter=converter:gsub('new_duration %- 1','new_duration')
local safeProject={GetCurrentTimeline=function() guard();return captionTimeline end}
local safePool={AppendToTimeline=function(_,clips) guard();return pool:AppendToTimeline(clips) end}
local env=setmetatable({project=safeProject,mediaPool=safePool,fusion_titles={templates[1]},app=resolve:Fusion(),
 CreateDialog=function(_,message) error(message) end},{__index=_G})
local api=assert(load(converter..'\nreturn {read=GetSubtitleData,create=CreateTextPlusClips}', 'Snap Captions automatic adapter','t',env))()
local charPattern='[%z\1-\127\194-\244][\128-\191]*'
local function letters(text)
 local out={};for ch in text:gmatch(charPattern) do table.insert(out,ch) end;return out
end
local function charlen(text) return #letters(text) end
local punctuationRanges={PUNCTUATION_RANGES}
local function punctuation(cp,ch)
 if ch:match('%p') then return true end
 for _,r in ipairs(punctuationRanges) do if cp>=r[1] and cp<=r[2] then return true end end
 return false
end
local function clean(text)
 local chars={}
 for _,ch in ipairs(letters(text)) do
  local b={ch:byte(1,#ch)};local cp=b[1]
  if #b==2 then cp=(b[1]-192)*64+b[2]-128
  elseif #b==3 then cp=(b[1]-224)*4096+(b[2]-128)*64+b[3]-128
  elseif #b==4 then cp=(b[1]-240)*262144+(b[2]-128)*4096+(b[3]-128)*64+b[4]-128 end
  if cp==0x2028 or cp==0x2029 then table.insert(chars,' ')
  elseif not punctuation(cp,ch) then table.insert(chars,ch) end
 end
 local lines={};local line=''
 for word in table.concat(chars):gmatch('%S+') do
  while charlen(word)>15 do
   if line~='' then table.insert(lines,line);line='' end
   local chars=letters(word);table.insert(lines,table.concat(chars,'',1,15));word=table.concat(chars,'',16,#chars)
  end
  if line~='' and charlen(line)+1+charlen(word)>15 then table.insert(lines,line);line='' end
  line=line=='' and word or line..' '..word
 end
 if line~='' then table.insert(lines,line) end
 return table.concat(lines,'\n')
end
guard()
local enabled={}
for i=1,timeline:GetTrackCount('audio') do enabled[i]=timeline:GetIsTrackEnabled('audio',i);assert(timeline:SetTrackEnable('audio',i,i==MICROPHONE_TRACK)) end
local ok,created=pcall(function() return timeline:CreateSubtitlesFromAudio({
 [resolve.SUBTITLE_LANGUAGE]=resolve.AUTO_CAPTION_ENGLISH,
 [resolve.SUBTITLE_CHARS_PER_LINE]=15,
 [resolve.SUBTITLE_LINE_BREAK]=resolve.AUTO_CAPTION_LINE_SINGLE,
 [resolve.SUBTITLE_GAP]=0}) end)
-- Restore original audio even when transcription fails, on the captured timeline only.
for i,state in ipairs(enabled) do timeline:SetTrackEnable('audio',i,state) end
assert(ok and created,'Resolve could not create subtitles from audio')
guard()
local st=timeline:GetTrackCount('subtitle')
local data=api.read(st,timeline:GetStartFrame(),timeline:GetEndFrame(),'None',2,false,{})
local filtered={}
for _,row in ipairs(data) do row.text=clean(row.text);if row.text~='' then table.insert(filtered,row) end end
data=filtered
if #data>0 and templates[1] then
 assert(timeline:AddTrack('video'))
 local vt=timeline:GetTrackCount('video');timeline:SetTrackName('video',vt,'AUTO CAPTIONS - Snap Captions')
 local win={Find=function(_,id) return id=='fill_gaps' and {Checked=false} or {Value=0} end,Repaint=function() end}
 assert(api.create(win,data,1,vt),'Snap Captions conversion failed')
 local clips=timeline:GetItemListInTrack('video',vt)
 assert(#clips==#data,'Caption count mismatch')
 for i,c in ipairs(clips) do
  assert(c:GetStart()==data[i].start and c:GetDuration()==data[i].duration,'Caption timing mismatch')
  local nodes=c:GetFusionCompByIndex(1):GetToolList(false,'TextPlus')
  assert(nodes[1]:GetInput('StyledText')==data[i].text,'Caption text mismatch')
 end
 timeline:SetTrackEnable('subtitle',st,false)
elseif #data>0 then
 print('AUTO_CAPTIONS_FALLBACK Native subtitles kept because no Text+ preset was found in Snap Captions')
end
assert(timeline:GetEndFrame()-timeline:GetStartFrame()==expectedDuration,'Captions changed timeline length')
print('AUTO_CAPTIONS_VERIFIED '..#data)
end
