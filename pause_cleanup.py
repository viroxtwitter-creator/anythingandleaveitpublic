"""Remove only sustained near-silence, preserving gameplay and natural handles."""
import wave
import numpy as np
from dialogue_cut import subtract

def clean_pauses(ranges,wav,events=()):
    with wave.open(str(wav),'rb') as f:
        if f.getnchannels()!=1 or f.getsampwidth()!=2:raise ValueError('Expected mono PCM microphone audio')
        rate=f.getframerate()
        audio=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(np.float32)/32768
    hop=max(1,round(rate*.02));step=hop/rate
    count=len(audio)//hop
    if not count:return ranges,[]
    energy=np.sqrt(np.mean(audio[:count*hop].reshape(-1,hop)**2,axis=1))
    # Deliberately low ceiling: quiet speech is not the same as dead air.
    threshold=min(.0008,max(.00015,float(np.percentile(energy,15))*1.5))
    quiet=energy<threshold
    boundaries=np.diff(np.r_[False,quiet,False].astype(int))
    cuts=[]
    for first,last in zip(np.flatnonzero(boundaries==1),np.flatnonzero(boundaries==-1)):
        start,end=first*step,last*step
        if end-start<.8:continue
        for a,b in ranges:
            lo,hi=max(a,start),min(b,end)
            if hi-lo<.8:continue
            # Leave 150 ms after preceding speech and 90 ms before following speech.
            left=lo if start<=a else lo+.15
            right=hi if end>=b else hi-.09
            protected=[(max(0,x-.1),y+.1) for x,y in events]
            for x,y in subtract([(left,right)],protected):
                if y-x>=.45:cuts.append((x,y))
    selected=subtract(ranges,cuts)
    return selected,[dict(start=a,end=b,reason='Sustained near-silent microphone gap; gameplay protected') for a,b in cuts]
