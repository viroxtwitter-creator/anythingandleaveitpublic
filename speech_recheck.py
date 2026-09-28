"""Recover retakes that ASR hid inside implausibly stretched word timestamps."""
from difflib import SequenceMatcher
import re
import wave
import numpy as np


def tokens(words):
    return re.findall(r'[a-z0-9]+',' '.join(w['text'] for w in words).lower())


def recover(transcript,wav,model,progress=lambda _:None,cancel=lambda:False):
    suspects=[(i,w) for i,s in enumerate(transcript) for w in s['words']
              if 1.15<=w['end']-w['start']<=8]
    if not suspects:return transcript,[]
    with wave.open(str(wav)) as f:
        rate=f.getframerate()
        audio=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(np.float32)/32768
    duration=len(audio)/rate
    replacements={};reports=[]
    for index,anchor in suspects:
        if index in replacements:continue
        if cancel():
            from automatic_cut import Cancelled
            raise Cancelled()
        segment=transcript[index]
        if segment['end']-segment['start']>18:continue
        lo,hi=anchor['start'],anchor['end']
        hop=max(1,round(rate*.02))
        samples=audio[round(lo*rate):round(hi*rate)]
        samples=samples[:len(samples)//hop*hop]
        if len(samples)<hop*8:continue
        energy=np.sqrt(np.mean(samples.reshape(-1,hop)**2,axis=1))
        threshold=max(.0003,min(.004,float(np.percentile(energy,90))*.05))
        quiet=energy<threshold
        runs=[];start=None
        for j,is_quiet in enumerate(np.r_[quiet,False]):
            if is_quiet and start is None:start=j
            if not is_quiet and start is not None:
                if (j-start)*hop/rate>=.16:runs.append((start,j))
                start=None
        # A real internal pause is independent evidence that this is not one word.
        runs=[(a,b) for a,b in runs if a*hop/rate>.08 and (len(energy)-b)*hop/rate>.08]
        if not runs:continue
        a,b=max(runs,key=lambda r:r[1]-r[0])
        split=lo+(a+b)*hop/rate/2
        windows=[(max(0,segment['start']-.25),split),(split,min(duration,segment['end']+.30))]
        if min(y-x for x,y in windows)<1:continue
        progress(f'Re-listening to a possible hidden restart at {int(lo)//60}:{int(lo)%60:02}…')
        parts=[]
        for x,y in windows:
            segments,_=model.transcribe(audio[round(x*rate):round(y*rate)],language='en',
                vad_filter=False,temperature=0,beam_size=5,word_timestamps=True,condition_on_previous_text=False)
            words=[dict(start=x+w.start,end=x+w.end,text=w.word,probability=w.probability)
                   for s in segments for w in s.words if w.end>=w.start]
            parts.append(words)
        left,right=parts
        if not left or not right:continue
        lt,rt=tokens(left),tokens(right)
        match=max(SequenceMatcher(None,lt,rt,autojunk=False).get_matching_blocks(),key=lambda m:m.size)
        shared=set(lt[match.a:match.a+match.size])-{'a','an','the','is','this','that','it','and','to','i','we','you'}
        old=tokens(segment['words'])
        coverage=sum(m.size for m in SequenceMatcher(None,old,lt+rt,autojunk=False).get_matching_blocks())/max(1,len(old))
        confidence=min(sum(w.get('probability',0) for w in part)/len(part) for part in parts)
        accepted=bool(match.size>=4 and len(shared)>=2 and len(lt+rt)>=len(old)+3 and coverage>=.70 and confidence>=.65)
        report=dict(source_start=segment['start'],source_end=segment['end'],
            suspect_word=anchor['text'],suspect_duration=hi-lo,split=split,
            original_text=segment.get('text',''),recovered_text=[''.join(w['text'] for w in part).strip() for part in parts],
            accepted=accepted,coverage=float(coverage),confidence=float(confidence),
            reason='Repeated phrase recovered in separate acoustic windows' if accepted else 'No reliable additional repeated phrase; original retained')
        reports.append(report)
        if accepted:
            replacements[index]=[dict(start=part[0]['start'],end=part[-1]['end'],
                text=''.join(w['text'] for w in part),words=part) for part in parts]
    return [new for i,s in enumerate(transcript) for new in replacements.get(i,[s])],reports
