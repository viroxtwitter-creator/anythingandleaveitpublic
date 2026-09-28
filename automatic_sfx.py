"""Context-linked SFX from the user's library. No inferred visual kills or hits."""
import json,hashlib,wave,re
from pathlib import Path
from app_paths import ROOT,add_dependencies
add_dependencies()
import av
import numpy as np
from review_core import save_json,read_transcript
SFX_ROOT=Path(r'C:\Users\jordan\Desktop\SFX')
SPECS={
 'whoosh':('dragon-studio-simple-whoosh-382724.mp3',-24,'accents'),
 'riser':('dragon-studio-swoosh-riser-reverb-390309.mp3',-27,'accents'),
 'pop_reverb':('soundreality-pop-reverb-423718.mp3',-26,'accents'),
 'pop_up':('Pop up Sound effect ( 256kbps cbr ).mp3',-25,'accents'),
 'button':('Button_Plate Click (Minecraft Sound) - Sound Effect for editing - Sound Library (youtube).mp3',-24,'accents'),
 'cash':('modestas123123-cash-register-kaching-sound-effect-125042.mp3',-25,'accents'),
 'notification':('universfield-new-notification-051-494246.mp3',-26,'accents'),
 'camera':('voicebosch-camera-shutter-187326.mp3',-26,'accents'),
 'camera_flash':('kauasilbershlachparodes-camera-flash-494027.mp3',-26,'accents'),
 'data':('Y2Mate.is - 5 data readout sound effect  (1).mp3',-27,'accents'),
 'cinematic':('lordsonny-cinematic-boom-171285.mp3',-28,'accents'),
 'tick':('voicebosch-ticking-clock-182894.mp3',-30,'accents'),
 'sweep':('soundreality-whoosh-take-flight-384632.mp3',-26,'accents'),
 'pop':('dragon-studio-pop-402324.mp3',-24,'accents'),
 'click':('universfield-computer-mouse-click-352734.mp3',-24,'accents'),
 'boom':('bithuh-vine-boom-392646.mp3',-23,'memes'),
 'fail':('Spongebob Boo-womp Sound.mp3',-24,'memes'),
 'error':('freesound_community-windows-error-sound-effect-35894.mp3',-25,'memes'),
 'success':('Level Up (Minecraft Sound) - Sound Effect for editing.mp3',-25,'memes'),
}
RULES={
 'boom':['oh my god','no way','this is insane','thats crazy','thats insane','what the hell'],
 'fail':['i died','we died','we lost','i lost','that didnt work','just disconnected'],
 'error':['not working','doesnt work','its broken','an error'],
 'success':['lets go','we won','i won','we win'],
 'pop':['look at this','look at that','right there'],
 'cash':['just bought','i bought','we bought','got paid'],
 'notification':['just unlocked','we unlocked','i unlocked','level up'],
 'camera':['take a screenshot','take a picture'],
 'data':['look at the numbers','here are the stats','these are the stats','the results are'],
 'cinematic':['there it is','the big reveal','finally got it'],
 'tick':['countdown','seconds left','wait for it'],
 'click':['click on','click this','select this','press this'],
}
MAX_SECONDS={'riser':6.5,'camera':2.0,'data':2.0,'tick':2.0}

def prepare_effect():
 folder=ROOT/'analysis/sound-effects';folder.mkdir(exist_ok=True)
 assets={}
 for kind,(name,level,group) in SPECS.items():
  source=SFX_ROOT/name
  if not source.is_file():continue
  key=hashlib.sha1(source.read_bytes()).hexdigest()[:12]
  wav=folder/f'context-v1-{kind}-{key}.wav';meta=wav.with_suffix('.json')
  if wav.is_file() and meta.is_file():assets[kind]=json.loads(meta.read_text());continue
  chunks=[]
  with av.open(str(source)) as c:
   res=av.AudioResampler(format='fltp',layout='stereo',rate=48000)
   for f in c.decode(audio=0):chunks.extend(x.to_ndarray() for x in res.resample(f))
   chunks.extend(x.to_ndarray() for x in res.resample(None))
  data=np.concatenate(chunks,axis=1);amp=np.max(np.abs(data),axis=0);maximum=float(amp.max())
  if maximum<1e-7:continue
  active=np.flatnonzero(amp>maximum*10**(-42/20))
  lo=max(0,int(active[0])-480);hi=min(len(amp),int(active[-1])+960)
  data=data[:,lo:hi].copy()
  seconds=data.shape[1]/48000;limit=MAX_SECONDS.get(kind,5)
  if seconds>limit:
   if kind not in MAX_SECONDS:continue # Don't truncate an unknown long meme or music file.
   samples=round(limit*48000)
   data=data[:,-samples:] if kind=='riser' else data[:,:samples]
  data*=10**(level/20)/np.max(np.abs(data));fade=min(480,data.shape[1]//4)
  data[:,:fade]*=np.linspace(0,1,fade);data[:,-fade:]*=np.linspace(1,0,fade)
  peak=int(np.argmax(np.max(np.abs(data),axis=0)))
  with wave.open(str(wav),'wb') as w:
   w.setparams((2,2,48000,0,'NONE','not compressed'));w.writeframes((data.T*32767).astype('<i2').tobytes())
  asset=dict(path=str(wav),original=str(source),duration=data.shape[1]/48000,peak_offset=peak/48000,peak_dbfs=level,group=group)
  save_json(meta,asset);assets[kind]=asset
 if 'whoosh' not in assets:raise ValueError('The short whoosh is missing from Desktop/SFX. Turn off sound effects to continue.')
 return dict(assets=assets,source_folder=str(SFX_ROOT))

def contextual_candidates(words,assets):
 tokens=[re.sub('[^a-z0-9]','',w['text'].lower()) for w in words];candidates=[]
 for kind,phrases in RULES.items():
  if kind not in assets:continue
  for phrase in phrases:
   target=phrase.split();n=len(target)
   for i in range(len(words)-n+1):
    if tokens[i:i+n]!=target:continue
    matched=words[i:i+n]
    if any(b['start']-a['end']>1 for a,b in zip(matched,matched[1:])):continue
    if sum(w.get('probability',1) for w in matched)/n<.65:continue
    prefix=tokens[max(0,i-5):i]
    # Don't play a loss/error joke for a hypothetical, negated or near miss.
    if kind in ('fail','error','success','cash','notification','camera') and any(t in prefix for t in ('if','might','could','would','nearly','almost','hopefully','dont','not','never')):continue
    candidates.append(dict(kind=kind,source_start=matched[0]['start'],source_end=matched[-1]['end'],
       reason='Spoken cue: '+phrase,priority=3 if assets[kind]['group']=='memes' else 2))
 return candidates

def choose_placements(result,effect):
 assets=effect['assets'];fps=result['fps'];kept=result['kept'];mapped=[];pos=0
 source=Path(result['source']);s=source.stat()
 key=hashlib.sha1(f'{source.resolve()}:{s.st_size}:{s.st_mtime_ns}'.encode()).hexdigest()[:14]
 transcript=read_transcript(ROOT/'analysis'/f'transcript-{key}-{result["microphone"]}.json') or []
 words=sorted([w for seg in transcript for w in seg['words'] if 0<w['end']-w['start']<3],key=lambda w:w['start'])
 cues=contextual_candidates(words,assets);speech_output=[]
 for i,(a,b) in enumerate(kept):
  end=pos+round(b*fps)-round(a*fps)
  for w in words:
   if a<=w['start'] and w['end']<=b:speech_output.append((pos+(w['start']-a)*fps,pos+(w['end']-a)*fps))
  for cue in cues:
   if a<=cue['source_start'] and cue['source_end']<=b:
    start=pos+round((cue['source_end']-a+.08)*fps)
    mapped.append(dict(cue,start_frame=start,anchor_frame=start))
  if i and a-kept[i-1][1]>=1.2:
   skipped=a-kept[i-1][1]
   if skipped<2.5:kind='click'
   elif skipped<7:kind='pop'
   elif skipped<15:kind='whoosh'
   else:kind='riser'
   if kind not in assets:kind='whoosh'
   mapped.append(dict(kind=kind,start_frame=pos-round(assets[kind]['peak_offset']*fps),
     anchor_frame=pos,reason=f'Picture cut skips {skipped:.1f}s of source footage',priority=1))
  pos=end
  accepted=[];uses={}
  families={'whoosh':['whoosh','sweep'],'sweep':['sweep','whoosh'],
           'riser':['riser','cinematic','sweep'],'pop':['pop','pop_up','pop_reverb'],
           'click':['click','button'],'camera':['camera','camera_flash']}
 # Speech cues take precedence over decorative transition sounds.
 for cue in sorted(mapped,key=lambda c:(-c['priority'],c['start_frame'])):
  cue=dict(cue);family=cue['kind']
  choices=[k for k in families.get(family,[family]) if k in assets]
  cue['kind']=min(choices,key=lambda k:uses.get(k,0))
  asset=assets[cue['kind']];start=cue['start_frame']
  if cue['priority']==1:start=cue['anchor_frame']-round(asset['peak_offset']*fps)
  cue['start_frame']=start
  frames=round(asset['duration']*fps);end=start+frames
  if start<0 or end>pos:continue
  if asset['group']=='memes':
   # Preserve the complete meme sound and avoid laying it over the next sentence.
   if any(x<end and y>start for x,y in speech_output):continue
   if any(p['group']=='memes' and abs(p['start_frame']-start)<30*fps for p in accepted):continue
  spacing=6*fps if cue['priority']==1 else 3*fps
  if any(not(end+fps<=p['start_frame'] or start>=p['start_frame']+p['duration_frames']+fps)
         or abs(start-p['start_frame'])<spacing for p in accepted):continue
  if any(p['kind']==cue['kind'] and abs(start-p['start_frame'])<12*fps for p in accepted):continue
  accepted.append(dict(cue,duration_frames=frames,group=asset['group']))
  uses[cue['kind']]=uses.get(cue['kind'],0)+1
 return sorted(accepted,key=lambda c:c['start_frame'])

def lua_for_effects(effect,placements):
 if not placements:return '\nprint("AUTO_SFX_VERIFIED 0")\n'
 kinds=sorted({p['kind'] for p in placements});indices={k:i+1 for i,k in enumerate(kinds)}
 asset_rows=','.join('[==['+effect['assets'][k]['path'].replace('\\','/')+']==]' for k in kinds)
 rows=','.join('{'+','.join(map(str,[p['start_frame'],p['duration_frames'],indices[p['kind']],1 if p['group']=='accents' else 2]))+'}' for p in placements)
 return '''
local sfxAssets={}
for _,path in ipairs({SFX_ASSETS}) do
 local items=pool:ImportMedia({path});assert(items and #items==1,"Could not import sound effect");table.insert(sfxAssets,items[1])
end
local sfxTrack={}
for i,name in ipairs({"AUTO SFX - accents","AUTO SFX - memes"}) do
 assert(timeline:AddTrack("audio","stereo"),"Could not create SFX track")
 sfxTrack[i]=timeline:GetTrackCount("audio");timeline:SetTrackName("audio",sfxTrack[i],name)
end
local count=0
for _,r in ipairs({SFX_RANGES}) do
 local clips=pool:AppendToTimeline({{mediaPoolItem=sfxAssets[r[3]],startFrame=0,endFrame=r[2],mediaType=2,trackIndex=sfxTrack[r[4]],recordFrame=timeline:GetStartFrame()+r[1]}})
 assert(clips and #clips==1,"Sound-effect import incomplete")
 assert(clips[1]:GetStart()==timeline:GetStartFrame()+r[1] and clips[1]:GetDuration()==r[2],"Sound-effect timing mismatch")
 count=count+1
end
assert(timeline:GetEndFrame()-timeline:GetStartFrame()==expectedDuration,"SFX changed draft length")
print("AUTO_SFX_VERIFIED "..count)
'''.replace('SFX_ASSETS',asset_rows).replace('SFX_RANGES',rows)
