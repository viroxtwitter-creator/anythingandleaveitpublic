"""Conservative microphone-energy refinement; never a semantic speech verdict."""
import wave
import numpy as np

def refine_edges(ranges,wav,events=(),exclusions=()):
    with wave.open(str(wav),'rb') as f:
        if f.getnchannels()!=1 or f.getsampwidth()!=2:
            raise ValueError('Boundary analysis requires mono 16-bit microphone audio')
        rate=f.getframerate()
        signal=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(np.float32)/32768
    hop=max(1,round(rate*.01));step=hop/rate
    signal=signal[:len(signal)//hop*hop]
    if not len(signal):return ranges,[]
    energy=np.sqrt(np.mean(signal.reshape(-1,hop)**2,axis=1))
    duration=len(signal)/rate
    result=[];changes=[]
    for index,(a,b) in enumerate(ranges):
        lo=max(0,a-.3,result[-1][1] if result else 0)
        hi=min(duration,b+.3,ranges[index+1][0] if index+1<len(ranges) else duration)
        # Deleted takes are hard barriers, not silence to extend back across.
        for x,y in exclusions:
            if y<=a+.001:lo=max(lo,y)
            if x>=b-.001:hi=min(hi,x)
        left=max(0,int(lo/step));right=min(len(energy),int(hi/step))
        local=energy[left:right]
        if len(local)<3:result.append([a,b]);continue
        floor=float(np.percentile(local,15));peak=float(np.percentile(local,95))
        threshold=max(.0008,floor*3,peak*.045)
        if peak<threshold*2:result.append([a,b]);continue
        active=local>threshold
        # Ignore isolated clicks; require at least 30 ms of sustained energy.
        sustained=np.convolve(active.astype(int),np.ones(3,dtype=int),'valid')==3
        mask=np.zeros(len(local),dtype=bool)
        for offset in (0,1,2):mask[offset:offset+len(sustained)] |= sustained
        times=(np.flatnonzero(mask)+left)*step
        inside=times[(times>=a)&(times<b)]
        if not len(inside):result.append([a,b]);continue
        start=inside[0];end=inside[-1]+step
        # Follow only the same acoustic phrase across the proposed boundary.
        for t in times[times<start][::-1]:
            if start-(t+step)>.08:break
            start=t
        for t in times[times>=end-.000001]:
            if t-end>.08:break
            end=t+step
        na=max(lo,start-.075);nb=min(hi,end+.12)
        # Large disagreement needs review, not an aggressive automatic rewrite.
        if abs(na-a)>.6:na=a
        if abs(nb-b)>.6:nb=b
        # Preserve selected gameplay at either edge, even with a quiet microphone.
        if any(x<max(a,na)+.01 and y>min(a,na) for x,y in events):na=a
        if any(x<max(b,nb) and y>min(b,nb)-.01 for x,y in events):nb=b
        if nb-na<.1:na,nb=a,b
        result.append([na,nb])
        if abs(na-a)>.015 or abs(nb-b)>.015:
            changes.append(dict(before=[a,b],after=[na,nb],reason='Microphone energy edge refinement'))
    return result,changes
