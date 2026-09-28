import tempfile,wave
from pathlib import Path
from app_paths import add_dependencies
add_dependencies()
import numpy as np
from dialogue_cut import clean_dialogue
from pause_cleanup import clean_pauses

def transcript(text):
    return [dict(words=[dict(text=' '+t,start=1+i*.2,end=1+(i+1)*.2) for i,t in enumerate(text.split())])]
for text in ('I um I think this works.', 'because because this works.',
             'Look at this look at this enemy.',
             "not gonna lie guys the fact that this I'm not gonna lie guys the fact. I'm not banned right now."):
    assert clean_dialogue(transcript(text),30)[2],text
for text in ('Go go go!', 'Shake it shake it shake it!', 'That is very very good!',
             'I think the graphics look amazing. I think the controls feel awkward.'):
    assert not clean_dialogue(transcript(text),30)[2],text
with tempfile.TemporaryDirectory() as folder:
    wav=Path(folder)/'voice.wav'
    samples=np.zeros(5*16000,dtype=np.int16)
    samples[:16000]=1000;samples[4*16000:]=1000
    def write():
        with wave.open(str(wav),'wb') as f:
            f.setparams((1,2,16000,0,'NONE','not compressed'));f.writeframes(samples.tobytes())
    write()
    kept,removed=clean_pauses([[0,5]],wav)
    assert len(kept)==2 and removed
    assert abs(kept[0][1]-1.15)<.025 and abs(kept[1][0]-3.91)<.025
    assert clean_pauses([[0,5]],wav,[(.9,4.1)])[0]==[[0,5]]
    samples[16000:4*16000]=100 # quiet but audible speech must survive
    write();assert not clean_pauses([[0,5]],wav)[1]
print('PASS: interrupted stutters, long restarts, emphasis safeguards, internal dead air and quiet audio')
