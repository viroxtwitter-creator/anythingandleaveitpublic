import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.analysis-deps'))
from analyze_speech import extract, SOURCE, OUT
import av, json
import numpy as np
from faster_whisper import WhisperModel

if __name__ == '__main__':
    c=av.open(str(SOURCE)); duration=c.duration/1e6; c.close()
    wav=OUT/'full-microphone.wav'
    extract(SOURCE,1,0,duration,wav)
    dest=OUT/'full-transcript.json'
    if not dest.exists():
        model=WhisperModel('base.en',device='cpu',compute_type='int8',cpu_threads=4,
                          download_root=str(ROOT/'.model-cache'))
        segments,info=model.transcribe(str(wav),language='en',vad_filter=True,
                    word_timestamps=True,beam_size=3,condition_on_previous_text=False)
        rows=[]
        for s in segments:
            rows.append({'start':s.start,'end':s.end,'text':s.text,
                         'words':[{'start':w.start,'end':w.end,'text':w.word,
                                   'probability':w.probability} for w in s.words]})
            print(f'{s.start:.1f}: {s.text}',flush=True)
        dest.write_text(json.dumps(rows,indent=2),encoding='utf-8')
    print('FULL TRANSCRIPT READY',flush=True)
