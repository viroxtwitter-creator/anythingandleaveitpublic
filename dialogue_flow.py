"""Word-level disfluencies and phrase-aware handles, before picture selection."""
import re

LEAD=.075
TAIL=.12
SENTENCE_TAIL=.24
INTERNAL_PAUSE=.48
FILLERS={'um','uh','erm','er'}
FUNCTION={'i','im','we','were','the','a','to','it','its','and','but','so','this','that','you','because','if','when','then','they','he','she'}

def norm(w):return re.sub('[^a-z0-9]','',w['text'].lower())

def disfluencies(words,duration):
    removed=[];dead=set()
    def discard(a,b,reason):
        # Remove only the earlier attempt; never consume the next spoken onset.
        left=max(0,words[a]['start']-LEAD)
        # A lead handle must not preserve the tail of the discarded syllable.
        # Abutting words have no room for a handle; overlapping alignment is
        # ambiguous, so leave that attempt intact instead of clipping either word.
        if words[b-1]['end']>words[b]['start']:return
        right=min(words[b]['start'],max(words[b]['start']-LEAD,words[b-1]['end']))
        if a and words[a-1]['end']>left:left=words[a-1]['end']
        if right<=left:return
        dead.update(range(a,b))
        removed.append(dict(start=left,end=right,earlier=''.join(w['text'] for w in words[a:b]).strip(),
            kept=''.join(w['text'] for w in words[b:b+8]).strip(),kept_start=words[b]['start'],cut_limit=right,reason=reason))
    for i,w in enumerate(words[:-1]):
        if i in dead:continue
        # Restart with an intervening hesitation: "I, um, I think".
        j=i+1
        while j<len(words) and norm(words[j]) in FILLERS:j+=1
        if j>i+1 and j<len(words) and norm(w) in FUNCTION and norm(w)==norm(words[j]) and words[j]['start']-w['end']<1.2:
            discard(i,j,'Repeated word interrupted by a hesitation');continue
        # Long exact opening followed by an abandoned tail, then restarted.
        # Search across ASR punctuation groups, but never across a real pause.
        restarted=False
        for j in range(i+5,min(i+17,len(words))):
            if norm(w) not in {'i','im','we','were','not','this','that','because','if'}:break
            if any(words[k+1]['start']-words[k]['end']>.8 for k in range(i,j)):break
            n=0
            while i+n<j and j+n<len(words) and norm(words[i+n])==norm(words[j+n]):n+=1
            tail=words[i+n:j]
            if n<5 or len({norm(x) for x in words[i:i+n]})<4 or len(tail)>4:continue
            if any(x['text'].rstrip().endswith(('.','!','?')) for x in words[i:j]):continue
            if tail and norm(tail[-1]) not in {'this','that','and','but','the','a','to','im','i'}:continue
            # Include an optional "I'm" in the later retained lead-in.
            keep=j-1 if tail and norm(words[j-1])=='im' else j
            discard(i,keep,'Repeated long opening after an abandoned clause');restarted=True;break
        if restarted:continue
        # A recognizer may preserve an audible cut-off syllable as "th-".
        if w['text'].rstrip().endswith(('-', '—')) and len(norm(w))>=2 and norm(words[i+1]).startswith(norm(w)) and words[i+1]['start']-w['end']<.7:
            discard(i,i+1,'Cut-off word restarted immediately');continue
        if norm(w) in FILLERS and words[i+1]['start']-w['end']<1.2:
            discard(i,i+1,'Hesitation filler before continuing speech');continue
        # Longest repeated short prefix first; retain expressive single-word emphasis.
        for n in (8,7,6,5,4,3,2,1):
            if i+2*n>len(words):continue
            a=words[i:i+n];b=words[i+n:i+2*n]
            if any(j in dead for j in range(i,i+2*n)):continue
            if [norm(x) for x in a]!=[norm(x) for x in b]:continue
            if norm(a[0]) not in FUNCTION and not (n>=3 and len({norm(x) for x in a})>=3):continue
            if n>=3 and any(x['text'].rstrip().endswith('.') for x in a):continue
            if norm(a[0])=='it' and i and norm(words[i-1]) not in FUNCTION:continue
            if any(y['start']-x['end']>.7 for x,y in zip(a+b,(a+b)[1:])):continue
            if n>1 and any(x['text'].rstrip().endswith(('!','?')) for x in a):continue
            discard(i,i+n,'Repeated word or short phrase stutter');break
    return [w for i,w in enumerate(words) if i not in dead],removed

def speech_ranges(words,duration):
    groups=[]
    for w in words:
        if not groups or w['start']-groups[-1][-1]['end']>INTERNAL_PAUSE:groups.append([])
        groups[-1].append(w)
    result=[]
    for i,g in enumerate(groups):
        tail=SENTENCE_TAIL if g[-1]['text'].rstrip().endswith(('.','!','?')) else TAIL
        end=min(duration,g[-1]['end']+tail)
        if i+1<len(groups):end=min(end,groups[i+1][0]['start']-LEAD)
        result.append([max(0,g[0]['start']-LEAD),end])
    return result
