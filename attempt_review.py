"""Contextual selected-speech repair with explicit evidence and bounded lookahead."""
import re
from dialogue_cut import subtract,content,canonical

def token(word):return re.sub('[^a-z0-9]','',word['text'].lower())
def cutoff(word):return word['text'].rstrip().endswith(('...','…','-','—'))
def protected(words):
    return {token(w) for w in words if any(c.isdigit() for c in token(w)) or token(w) in {'not','never','dont','cant','wont','isnt','without'}}

def repair_attempts(rows,ranges,events):
    spoken=[r for r in rows if r['words']];cuts=[];changes=[]
    def remove(row,words,kept,reason):
        if not words:return
        a=max(row['source_start'],words[0]['start']-.06)
        preceding=[w for w in row['words'] if w['end']<=words[0]['start'] and w not in words]
        if preceding:a=max(a,preceding[-1]['end'])
        b=min(row['source_end'],words[-1]['end']+.12)
        if any(a<y and b>x for x,y in events):return
        if b<=a or any(a<y and b>x for x,y in cuts):return
        # Whole-clip removal must also consume its handles.
        if len(words)==len(row['words']):a,b=row['source_start'],row['source_end']
        cuts.append((a,b))
        changes.append(dict(source_start=a,source_end=b,text=''.join(w['text'] for w in words).strip(),kept_text=kept['text'],reason=reason))
    for i,old in enumerate(spoken[:-1]):
        ow=old['words'];lexical=[(j,w) for j,w in enumerate(ow) if token(w)];ot=[token(w) for j,w in lexical]
        new=spoken[i+1];nw=new['words'];nt=[token(w) for w in nw if token(w)]
        if not ot or not nt:continue
        gap=nw[0]['start']-ow[-1]['end']
        if gap>20:continue
        if cutoff(ow[-1]):
            # Keep the sentence, remove only its restarted tail:
            # "... as it's su-" / "as it's super simple".
            matched=False
            for n in range(min(8,len(ot),len(nt)),0,-1):
                a,b=ot[-n:],nt[:n]
                if a[:-1]==b[:-1] and len(a[-1])>=2 and b[-1].startswith(a[-1]) and (n>=2 or len(a[-1])>=3):
                    remove(old,ow[lexical[-n][0]:],new,'Cut-off sentence tail replaced by its completed restart')
                    matched=True;break
            # A short isolated failed clause sharing actual content with a fuller
            # nearby attempt, not a bare conjunction or an unrelated thought.
            if not matched and len(ow)<=5 and len(nw)>len(ow) and not protected(ow):
                shared=content(ot)&content(nt)
                if shared:remove(old,ow,new,'Short cut-off attempt replaced by a fuller nearby take')
        # Compare fuller attempts beyond a short intervening abandoned fragment.
        for later in spoken[i+1:i+4]:
            lw=later['words'];lt=[token(w) for w in lw]
            if lw[0]['start']-ow[-1]['end']>40:break
            if len(ow)<8 or len(lw)<8 or protected(ow)!=protected(lw):continue
            ca,cb=content(canonical(ot)),content(canonical(lt))
            shared=ca&cb
            # High content containment with a common opening; changed endings or
            # a shared subject alone are deliberately insufficient.
            if len(shared)<5 or len(shared)/max(1,len(ca))<.8:continue
            if ot[:2]!=lt[:2] or len(lw)<len(ow)*.85:continue
            if cutoff(lw[-1]):continue
            remove(old,ow,later,'Earlier explanation substantially repeated in a fuller nearby take')
            break
    return subtract(ranges,cuts),changes
