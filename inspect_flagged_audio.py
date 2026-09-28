"""Read-only investigation of the user's flagged audio; does not export a cut."""
import json,wave
from pathlib import Path
from app_paths import ROOT,add_dependencies
add_dependencies()
import numpy as np
from faster_whisper import WhisperModel

p=json.loads((ROOT/'analysis/last-automatic-cut.json').read_text())
path=next((ROOT/'analysis').glob('*transcript*'+p['analysis_run_id']+'*.wav'))
with wave.open(str(path)) as f:
    rate=f.getframerate()
    audio=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(np.float32)/32768
with wave.open(str(ROOT/'analysis/flagged-4s32-microphone.wav'),'wb') as f:
    f.setparams((1,2,rate,0,'NONE','not compressed'))
    f.writeframes((audio[round(36.58*rate):round(43.62*rate)]*32768).astype('<i2').tobytes())
model=WhisperModel(str(ROOT/'.model-cache/speech-small.en'),device='cpu',compute_type='int8',cpu_threads=4)
results=[]
for a,b in [(35.8,44),(36.5,40),(39.0,44),(40,44)]:
    segments,_=model.transcribe(audio[round(a*rate):round(b*rate)],language='en',vad_filter=False,
        temperature=0,beam_size=5,word_timestamps=True,condition_on_previous_text=False)
    for s in segments:
        row=dict(window=[a,b],start=a+s.start,end=a+s.end,text=s.text,
            words=[dict(text=w.word,start=a+w.start,end=a+w.end,probability=w.probability) for w in s.words])
        results.append(row)
        print(json.dumps(row),flush=True)
(ROOT/'analysis/flagged-4s32-window-transcripts.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
