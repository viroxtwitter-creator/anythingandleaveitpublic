import tempfile,wave,json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from speech_recheck import recover


def segment(text,a,b):
    ts=text.split();step=(b-a)/len(ts)
    return dict(start=a,end=b,text=text,words=[dict(start=a+i*step,end=a+(i+1)*step,text=' '+t,probability=.95) for i,t in enumerate(ts)])


with tempfile.TemporaryDirectory() as folder:
    wav=Path(folder)/'voice.wav';rate=16000
    samples=np.ones(rate*8,dtype=np.int16)*2000
    samples[rate*3:rate*4]=0
    with wave.open(str(wav),'wb') as f:
        f.setparams((1,2,rate,0,'NONE','not compressed'));f.writeframes(samples.tobytes())
    original=segment('This is a very clear useful setting for everyone',1,7)
    original['words'][4].update(start=2.5,end=4.5)
    class Model:
        def __init__(self,texts):self.texts=iter(texts);self.calls=0
        def transcribe(self,audio,**kwargs):
            self.calls+=1
            words=segment(next(self.texts),.2,len(audio)/rate-.2)['words']
            return iter([SimpleNamespace(words=[SimpleNamespace(start=w['start'],end=w['end'],word=w['text'],probability=.95) for w in words])]),None
    model=Model(['This is a very clear useful setting','This is a very clear useful setting for everyone'])
    output,reports=recover([original],wav,model)
    assert reports[0]['accepted'] and len(output)==2 and model.calls==2
    json.dumps(reports)
    model=Model(['This is a very clear','useful setting for everyone'])
    output,reports=recover([original],wav,model)
    assert output==[original] and not reports[0]['accepted'],'Ordinary pause rewritten as a repeat'
    normal=segment('A completely normal sentence stays untouched',1,3)
    model=Model([])
    assert recover([normal],wav,model)==([normal],[]) and model.calls==0
print('PASS: hidden repeat recovered, ordinary pause and normal words preserved, JSON audit serializable')
