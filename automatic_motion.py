"""Conservative Fusion motion selected from spoken cues and reference curves."""
import hashlib,re
from pathlib import Path
from app_paths import ROOT
from review_core import read_transcript

ZOOM_PHRASES={
    'oh my god':4,'no way':4,'this is insane':4,'thats insane':4,'thats crazy':4,
    'look at this':3,'look at that':3,'there it is':3,'watch this':3,
    'pretty insane':3,'what is this':3,'finally':2,
}

def _words_for(result):
    source=Path(result['source']);stat=source.stat()
    key=hashlib.sha1(f'{source.resolve()}:{stat.st_size}:{stat.st_mtime_ns}'.encode()).hexdigest()[:14]
    transcript=read_transcript(ROOT/'analysis'/f'transcript-{key}-{result["microphone"]}.json') or []
    return sorted([w for s in transcript for w in s['words'] if 0<w['end']-w['start']<3],key=lambda w:w['start'])

def choose_motion(result):
    """Place only transcript-confirmed punch zooms on clips long enough to animate."""
    words=_words_for(result);tokens=[re.sub('[^a-z0-9]','',w['text'].lower()) for w in words]
    cues=[]
    for phrase,priority in ZOOM_PHRASES.items():
        target=phrase.split();n=len(target)
        for i in range(len(words)-n+1):
            if tokens[i:i+n]!=target:continue
            matched=words[i:i+n]
            if any(b['start']-a['end']>1 for a,b in zip(matched,matched[1:])):continue
            if sum(w.get('probability',1) for w in matched)/n<.65:continue
            cues.append(dict(phrase=phrase,source_start=matched[0]['start'],source_end=matched[-1]['end'],priority=priority))
    fps=result['fps'];positions=[];timeline_frame=0
    for clip_index,(a,b) in enumerate(result['kept'],1):
        frames=round(b*fps)-round(a*fps)
        if frames<60:
            timeline_frame+=frames;continue
        matches=[c for c in cues if a<=c['source_start'] and c['source_end']<=b]
        if matches:
            cue=max(matches,key=lambda c:(c['priority'],c['source_end']))
            positions.append(dict(kind='punch_zoom',clip_index=clip_index,anchor_frame=timeline_frame,
                duration_frames=frames,source_start=cue['source_start'],phrase=cue['phrase'],
                reason='Spoken emphasis: '+cue['phrase'],priority=cue['priority']))
        timeline_frame+=frames
    # Keep the automatic layer intentional: one zoom per ten seconds, with a
    # soft cap based on edited length. Higher-confidence reactions win.
    cap=max(1,round(timeline_frame/fps/25))
    accepted=[]
    for cue in sorted(positions,key=lambda c:(-c['priority'],c['anchor_frame'])):
        if any(abs(cue['anchor_frame']-p['anchor_frame'])<10*fps for p in accepted):continue
        accepted.append(cue)
        if len(accepted)>=cap:break
    return sorted(accepted,key=lambda c:c['anchor_frame'])

def lua_for_motion(placements):
    if not placements:return '\nprint("AUTO_MOTION_VERIFIED 0")\n'
    rows=','.join('{'+','.join(map(str,[p['clip_index'],p['duration_frames']]))+'}' for p in placements)
    return r'''
local motionCount=0
for _,r in ipairs({MOTION_ROWS}) do
 local item=videoItems[r[1]];assert(item,"Missing motion target clip")
 assert(item:GetDuration()==r[2],"Motion target duration changed")
 assert(item:GetFusionCompCount()==0,"Fresh motion target already has a Fusion comp")
 local comp=item:AddFusionComp();assert(comp,"Could not add Fusion composition")
 comp:Lock()
 local mediaIn=comp:FindTool("MediaIn1");local mediaOut=comp:FindTool("MediaOut1")
 assert(mediaIn and mediaOut,"Fusion clip has no MediaIn/MediaOut")
 local transform=comp:AddTool("Transform",0,0)
 assert(transform,"Fusion Transform is unavailable")
 transform.Input=mediaIn.Output;mediaOut.Input=transform.Output
 local frames=r[2]
 local first=math.max(0,math.floor(frames*4/172+.5))
 local accent=math.max(first+1,math.floor(frames*21/172+.5))
 local finish=math.max(accent+1,frames-4)
 local scale=frames/172
 local curve=comp:BezierSpline();transform.Size=curve
 curve:SetKeyFrames({
  [first]={1.000,RH={9.66666666666667*scale-first,0}},
  [accent]={1.186,LH={15.3339000940323*scale-accent,1.17332037399091-1.186},RH={69.9950136494165*scale-accent,1.29564128054473-1.186}},
  [finish]={1.367,LH={119*scale-finish,0}}
 })
 transform.MotionBlur=1;comp:Unlock()
 assert(transform.Input:GetConnectedOutput():GetTool().Name==mediaIn.Name,"Zoom source disconnected")
 assert(mediaOut.Input:GetConnectedOutput():GetTool().Name==transform.Name,"Zoom output disconnected")
 assert(math.abs(transform:GetInput("Size",accent)-1.186)<.0001,"Zoom animation missing")
 local names=item:GetFusionCompNameList() or {};local old=names[item:GetFusionCompCount()]
 if old then item:RenameFusionCompByName(old,"AUTO - Jordan punch zoom") end
 motionCount=motionCount+1
 local markerFrame=item:GetStart()-timeline:GetStartFrame()
 assert(timeline:AddMarker(markerFrame,"Purple","AUTO ZOOM "..motionCount,
  "Fusion punch zoom: 1.000 to 1.367. Open this clip in Fusion to edit.",1,
  "retention-cut-auto-zoom-"..motionCount),"Could not mark automatic zoom")
end
assert(timeline:GetEndFrame()-timeline:GetStartFrame()==expectedDuration,"Motion changed draft length")
print("AUTO_MOTION_VERIFIED "..motionCount)
'''.replace('MOTION_ROWS',rows)
