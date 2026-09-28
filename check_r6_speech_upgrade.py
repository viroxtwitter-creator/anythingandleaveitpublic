import json
from pathlib import Path
from app_paths import ROOT,add_dependencies
add_dependencies()
from analyze_speech import extract
from faster_whisper import WhisperModel
r=json.loads((ROOT/'exports/Retention cut 20260909-034348-3000/automatic-plan.json').read_text())
wav=ROOT/'analysis/r6-small-model-opening.wav'
extract(Path(r['source']),r['microphone'],0,120,wav)
model=WhisperModel(str(ROOT/'.model-cache/speech-small.en'),device='cpu',compute_type='int8',cpu_threads=4)
segments,_=model.transcribe(str(wav),language='en',vad_filter=True,word_timestamps=True,beam_size=5,condition_on_previous_text=False)
rows=[]
for s in segments:
    print(round(s.start,2),s.text,flush=True)
    rows.append(dict(start=s.start,end=s.end,text=s.text,words=[dict(start=w.start,end=w.end,text=w.word,probability=w.probability) for w in s.words]))
(ROOT/'analysis/r6-small-model-opening.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
