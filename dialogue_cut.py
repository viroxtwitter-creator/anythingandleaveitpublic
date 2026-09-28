"""Tight word boundaries with restart, abandoned-take and repeat removal."""
import re
from difflib import SequenceMatcher
from review_core import merge_intervals,complement
from dialogue_flow import disfluencies,speech_ranges

def token(w):return re.sub('[^a-z0-9]','',w['text'].lower())

def canonical(ts):
    noise={'so','alright','guys','and','already','also','fully','honestly','just','oh'}
    out=[]
    for t in ts:
        if t=='everythings':out.extend(['everything','is'])
        elif t not in noise:out.append(t)
    if out[-3:]==['to','be','honest']:out=out[:-3]
    while out and out[-1] in ('that','this','up'):out.pop()
    return out

CONTENT_STOP={'a','an','the','i','im','you','he','she','it','we','they','is','are','was','were','be','been',
              'do','does','did','have','has','had','of','to','for','in','on','at','with','from','and','or',
              'but','so','that','this','there','here','my','your','our','their',
              'think','will','would','should','could','can','gonna','going'}
RESTART_STEMS=(('i','think'),('i','dont'),('i','just'),('im','gonna'),('im','going','to'),
               ('we','have'),('we','need'),('were','gonna'),('were','going','to'),
               ('this','is'),('thats','why'),('if','you'),('as','you','can','see'))

def common_prefix(a,b):
    n=0
    while n<min(len(a),len(b)) and a[n]==b[n]:n+=1
    return n

def content(ts):return {t for t in ts if t and t not in CONTENT_STOP and len(t)>1}

def unfinished(words):
    text=words[-1]['text'].rstrip()
    ts=[token(w) for w in words]
    return text.endswith(('...', '…', '-', '—')) or ts[-1] in {'a','an','the','to','of','with','because','if','and','but'}

def related_restart(a,b,distance):
    """Aggressive only in a short retake window; callbacks farther away are preserved."""
    if distance>12:return False
    ca,cb=canonical(a),canonical(b)
    if not ca or not cb:return False
    if ca==cb and tuple(ca) in {('my','god'),('no','way')}:return False
    # Exact short lines are often repeated reactions/takes ("this is insane").
    if ca==cb and len(ca)>=2 and len(set(ca))>=2:return True
    ratio=SequenceMatcher(None,ca,cb,autojunk=False).ratio()
    match=max((m.size for m in SequenceMatcher(None,ca,cb,autojunk=False).get_matching_blocks()),default=0)
    shared=content(ca)&content(cb)
    if min(len(ca),len(cb))>=5 and len(shared)>=3 and (ratio>=.70 or match>=4):return True
    # A later, fuller sentence that repeats most of an abandoned phrase.
    if match>=4 and match/min(len(ca),len(cb))>=.55 and len(shared)>=2:return True
    # Spoken false starts frequently retain a scaffold but change the ending.
    for stem in RESTART_STEMS:
        n=len(stem)
        if tuple(ca[:n])==stem and tuple(cb[:n])==stem and len(ca)<=10:
            # Shared grammatical openings alone say nothing about repeated meaning.
            if len(ca)<=n+1 or (len(shared)>=2 and ratio>=.65):return True
    return False

def clean_dialogue(transcript,duration):
    words=sorted([w for s in transcript for w in s['words'] if 0<=w['start']<=w['end']<=duration+.1
                  and w['end']-w['start']<3],key=lambda w:w['start'])
    words,disfluent=disfluencies(words,duration)
    groups=[]
    for w in words:
        if not groups or w['start']-groups[-1][-1]['end']>.65 or (token(w)=='so' and len(groups[-1])>=5 and w['start']-groups[-1][-1]['end']>.3) or (len(groups[-1])>=4 and groups[-1][-1]['text'].rstrip().endswith(('.', '?', '!'))):groups.append([])
        groups[-1].append(w)
    split=[]
    for group in groups:
        ts=[token(w) for w in group];point=None
        if len(set(ts[:4]))>=3:
            for j in range(5,len(ts)-3):
                if ts[:4]==ts[j:j+4] and group[j]['start']-group[0]['start']<=20:
                    point=j-1 if ts[j-1]=='alright' else j;break
        split.extend([group[:point],group[point:]] if point else [group])
    groups=split;removed=[]
    # An isolated grammatical lead-in with no payload is an abandoned start.
    # Do not classify a whole sentence as unfinished merely from ASR punctuation.
    empty_starts={('i','was'),
                  ('i','was','gonna'),('im','gonna'),('im','going','to'),('we','were','gonna')}
    for i,group in enumerate(groups[:-1]):
        ts=tuple(token(w) for w in group)
        next_group=groups[i+1]
        gap=next_group[0]['start']-group[-1]['end']
        if ts in empty_starts and gap>=1.2:
            removed.append(dict(start=max(0,group[0]['start']-.075),end=group[-1]['end']+.12,
                earlier=''.join(w['text'] for w in group).strip(),kept=''.join(w['text'] for w in next_group).strip(),
                kept_start=next_group[0]['start'],reason='Abandoned grammatical start before a long pause'))
    for i,old in enumerate(groups):
        a=[token(w) for w in old]
        if len(a)<2 or len(set(a))<2:continue
        for new in groups[i+1:]:
            distance=new[0]['start']-old[-1]['end']
            if distance>180:break
            b=[token(w) for w in new]
            if len(b)<2:continue
            # Do not mistake contradictory statements or different numbers for retakes.
            protected=lambda ts:{t for t in ts if any(c.isdigit() for c in t) or t in ('not','never','dont','cant','wont','isnt','doesnt')}
            # Immediate restarts can correct a number/negation; separated statements cannot.
            if protected(a)!=protected(b):continue
            ca,cb=canonical(a),canonical(b)
            # Prefer a finished take over a subsequent failed attempt. Later is
            # not automatically better, and ASR punctuation alone is weak evidence.
            if not unfinished(old) and (unfinished(new) or len(cb)<len(ca)*.65):continue
            if ca==cb and tuple(ca) in {('my','god'),('no','way')}:continue
            nearby=distance<=35
            ratio=SequenceMatcher(None,a,b,autojunk=False).ratio()
            canonical_ratio=SequenceMatcher(None,ca,cb,autojunk=False).ratio()
            same=(nearby and ((min(len(a),len(b))>=5 and ratio>=.84) or (min(len(ca),len(cb))>=5 and canonical_ratio>=.86)
                              or related_restart(a,b,distance)))
            # Longer-range repeats need more evidence so recurring reactions and
            # normal callbacks are not treated as abandoned takes.
            distant=(not nearby and min(len(ca),len(cb))>=7 and len(set(ca))>=4
                     and abs(len(ca)-len(cb))<=2 and canonical_ratio>=.96)
            prefix=nearby and len(ca)>=4 and len(cb)>=len(ca) and ca==cb[:len(ca)]
            if same or distant or prefix:
                removed.append(dict(start=max(0,old[0]['start']-.09),end=min(duration,old[-1]['end']+.12),
                    earlier=''.join(w['text'] for w in old).strip(),kept=''.join(w['text'] for w in new).strip(),
                    kept_start=new[0]['start'],reason=('Repeated line later in recording; later version kept' if distant
                    else 'Nearby matching retake; later version kept')))
                break
    # Restarts anywhere inside one breath, including after a valid lead-in such as
    # "I'm not gonna lie ...". Keep that lead-in and remove only the abandoned clause.
    for group in groups:
        ts=[token(w) for w in group]
        found=None
        for j in range(3,len(ts)-1):
            for start in range(max(0,j-14),j-2):
                first=canonical(ts[start:j]);later=canonical(ts[j:])
                if len(first)<2 or len(later)<2:continue
                prefix=common_prefix(first,later)
                stem=any(tuple(first[:len(s)])==s and tuple(later[:len(s)])==s for s in RESTART_STEMS)
                if prefix<3 and not stem:continue
                shared=len(content(first)&content(later))
                number_correction=stem and any(any(c.isdigit() for c in t) for t in first+later)
                if stem and shared<2 and not number_correction:continue
                if not stem and shared<2:continue
                if group[j]['start']-group[start]['start']>20:continue
                found=(start,j);break
            if found:break
        if found:
            start,j=found
            removed.append(dict(start=max(0,group[start]['start']-.09),end=max(0,group[j]['start']-.09),
                earlier=''.join(w['text'] for w in group[start:j]).strip(),kept=''.join(w['text'] for w in group[j:]).strip(),
                kept_start=group[j]['start'],reason='Restarted phrase; later version kept'))
    removed.extend(disfluent)
    # Retake padding must not truncate an adjacent retained word. Clamp each edge
    # against real word boundaries, then deduplicate overlapping detector evidence.
    for row in removed:
        row['end']=min(row['end'],row.get('cut_limit',row['kept_start']-.075))
    removed.sort(key=lambda r:(r['start'],-r['end']))
    unique=[]
    for row in removed:
        if row['end']<=row['start']:continue
        if any(x['start']<=row['start'] and x['end']>=row['end'] for x in unique):continue
        unique.append(row)
    cuts=merge_intervals([(r['start'],r['end']) for r in unique],0,duration)
    return subtract(speech_ranges(words,duration),cuts),cuts,unique

def subtract(ranges,cuts):
    return [r for a,b in ranges for r in complement(cuts,a,b)]
