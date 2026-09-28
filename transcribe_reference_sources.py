from app_paths import ROOT,add_dependencies
add_dependencies()
import av,json,hashlib
from pathlib import Path
from analyze_speech import extract
from review_core import read_transcript,save_json
from faster_whisper import WhisperModel
sources=[]
for num in (2,3):
 p=json.loads((ROOT/f'analysis/editing-style/references/{num}-profile.json').read_text())
 for s in sorted(p['sources'],key=lambda s:-s['seconds'])[:(2 if num==2 else 3)]:sources.append(Path(s['source']))
model=None
for source in sources:
 st=source.stat();key=hashlib.sha1(f'{source.resolve()}:{st.st_size}:{st.st_mtime_ns}'.encode()).hexdigest()[:14]
 with av.open(str(source)) as c:
  duration=c.duration/av.time_base;matches=[i for i,s in enumerate(c.streams.audio) if 'microphone' in s.metadata.get('name','').lower()]
 if len(matches)!=1:raise ValueError('Cannot identify microphone: '+str(source))
 index=matches[0];dest=ROOT/'analysis'/f'transcript-{key}-{index}.json'
 if read_transcript(dest) is not None:print('Cached',source.name,flush=True);continue
 print('Transcribing',source.name,flush=True)
 wav=dest.with_suffix('.wav');extract(source,index,0,duration,wav)
 if model is None:
  local=next((ROOT/'.model-cache').rglob('model.bin')).parent
  model=WhisperModel(str(local),device='cpu',compute_type='int8',cpu_threads=4)
 segments,_=model.transcribe(str(wav),language='en',vad_filter=True,word_timestamps=True,beam_size=3,condition_on_previous_text=False)
 rows=[]
 for s in segments:
  rows.append(dict(start=s.start,end=s.end,text=s.text,words=[dict(start=w.start,end=w.end,text=w.word,probability=w.probability) for w in s.words]))
 save_json(dest,rows);print('Saved',source.name,len(rows),'segments',flush=True)
