"""Deterministic review of the actual selected dialogue; not an LLM semantic verdict."""
import re

def tokens(words):return [re.sub('[^a-z0-9]','',w['text'].lower()) for w in words]

def restart_choice(old,new):
    """Exact repeated openings; do not infer equivalence from a shared topic."""
    a,b=tokens(old['words']),tokens(new['words'])
    # Short deictic opening restarted immediately with a specific complete take.
    # Do not discard named places, quantities, or a complete earlier sentence.
    prefix=0
    while prefix<min(len(a),len(b)) and a[prefix]==b[prefix]:prefix+=1
    if (5<=len(a)<=8 and len(b)>=len(a)+3 and prefix>=4 and
        a[-1] in {'game','here','now','this','that','it'} and old['text'].endswith(',') and
        new['source_start']-old['source_end']<=4):
        return 'old'
    # Restart scaffolding often sits after the abandoned opening.
    trimmed=a[:]
    for tail in (['and','of','course'],['of','course'],['and'],['but']):
        if trimmed[-len(tail):]==tail:trimmed=trimmed[:-len(tail)];break
    if len(trimmed)>=4 and len(set(trimmed))>=3 and len(b)>len(trimmed) and b[:len(trimmed)]==trimmed and len(trimmed)<len(a):
        return 'old'
    # An earlier complete explanation must not be followed by its shorter failed
    # repeat. The old detector skipped this case, leaving both in the edit.
    if len(b)>=5 and len(set(b))>=4 and len(a)>len(b) and a[:len(b)]==b and old['text'].endswith(('.','!','?')) and not new['text'].endswith(('!','?')):
        return 'new'
    return None

def review_script(transcript,kept,events=(),semantic=False,progress=lambda _:None,cancel=lambda:False,audit_only=False):
    # Zero-duration alignment entries still carry real linguistic context.
    words=sorted((w for s in transcript for w in s['words'] if 0<=w['end']-w['start']<3),key=lambda w:w['start'])
    def assemble(ranges):
        rows=[];position=0
        for i,(a,b) in enumerate(ranges):
            selected=[w for w in words if (a<w['end'] and w['start']<b) or
                      (w['start']==w['end'] and a<=w['start']<b)]
            rows.append(dict(clip=i+1,source_start=a,source_end=b,timeline_start=position,
                text=''.join(w['text'] for w in selected).strip(),words=selected))
            position+=b-a
        return rows
    rows=assemble(kept);drop=set();changes=[]
    spoken=[] if audit_only else [(i,row) for i,row in enumerate(rows) if row['words']]
    for (oi,old),(ni,new) in zip(spoken,spoken[1:]):
        if oi in drop or ni in drop:continue
        if new['source_start']-old['source_end']>15:continue
        choice=restart_choice(old,new)
        if not choice:continue
        index,row,retained=(oi,old,new) if choice=='old' else (ni,new,old)
        if choice=='new':
            following=next((x for j,x in spoken if j>ni),None)
            if following and following['words'][0]['start']-new['words'][-1]['end']<1.5:continue
        if any(row['source_start']<y and row['source_end']>x for x,y in events):continue
        drop.add(index)
        changes.append(dict(source_start=row['source_start'],source_end=row['source_end'],text=row['text'],kept_text=retained['text'],reason='Repeated opening; complete take retained'))
    for i,(old,new) in enumerate(zip(rows,rows[1:]) if not audit_only else []):
        if i in drop or i+1 in drop:continue
        a,b=tokens(old['words']),tokens(new['words'])
        if len(a)<3 or len(b)<len(a) or len(a)>12:continue
        if new['source_start']-old['source_end']>12:continue
        if a!=b[:len(a)]:continue
        if old['text'].endswith(('!','?')):continue
        # A shorter unfinished prefix or a full exact repeat, never a paraphrase.
        if len(a)<len(b) and old['text'].endswith('.'):continue
        if len(set(a)-{'i','we','the','a','and','is','it','this','that','to'})<2:continue
        if any(old['source_start']<y and old['source_end']>x for x,y in events):continue
        w=old['words']
        if old['source_end']-old['source_start']-(w[-1]['end']-w[0]['start'])>.6:continue
        drop.add(i)
        changes.append(dict(source_start=old['source_start'],source_end=old['source_end'],text=old['text'],
            kept_text=new['text'],reason='Adjacent repeated take in assembled script'))
    result=[r for i,r in enumerate(kept) if i not in drop]
    if not audit_only:
        connector_cuts=[]
        spoken=[r for r in assemble(result) if r['words']]
        for old,new in zip(spoken,spoken[1:]):
            last,first=old['words'][-1],new['words'][0]
            if (tokens([last])[0] in {'and','but','so'} and tokens([last])==tokens([first])
                and 0<=first['start']-last['end']<=15
                and not last['text'].rstrip().endswith(('.', '!', '?'))
                and not any(last['start']<y and old['source_end']>x for x,y in events)):
                left=max(old['source_start'],last['start']-.075,
                         old['words'][-2]['end'] if len(old['words'])>1 else old['source_start'])
                connector_cuts.append((left,old['source_end']))
                changes.append(dict(source_start=left,source_end=old['source_end'],text=last['text'].strip(),
                    kept_text=new['text'],reason='Abandoned connecting word repeated at the next take'))
        if connector_cuts:
            from dialogue_cut import subtract
            result=subtract(result,connector_cuts)
    from attempt_review import repair_attempts
    # Work at word boundaries, not only by deleting whole timeline clips. Iterate
    # a bounded number of times so chains of failed takes resolve in this run.
    for _ in range(0 if audit_only else 3):
        result,repairs=repair_attempts(assemble(result),result,events)
        changes.extend(repairs)
        if not repairs:break
    semantic_report=None
    if semantic and not audit_only:
        from contextual_takes import review
        result,semantic_report=review(transcript,result,events,progress,cancel,editorial=True)
        changes.extend(semantic_report['changes'])
    rows=assemble(result);flags=[]
    dangling={'a','an','the','to','because','if','with','of','and','but'}
    for index,row in enumerate(rows):
        w=row['words']
        if not w:continue
        reasons=[]
        if w[0]['start']<row['source_start']-.035 or w[-1]['end']>row['source_end']+.035:
            reasons.append('Cut overlaps a transcribed word; check the audio')
        following=rows[index+1] if index+1<len(rows) else None
        next_words=following['words'] if following else []
        continues=bool(next_words) and not any(w[-1]['end']<=x['start']<next_words[0]['start'] for x in words) and next_words[0]['start']-w[-1]['end']<=1.2
        if (tokens(w)[-1] in dangling or row['text'].endswith(('...','…','-','—'))) and not continues:
            reasons.append('Possible unfinished clause; may continue across the next cut')
        if sum(x.get('probability',1) for x in w)/len(w)<.65:
            reasons.append('Low transcription confidence; wording may be wrong')
        if reasons:flags.append(dict(clip=row['clip'],timeline_start=row['timeline_start'],
            source_start=row['source_start'],source_end=row['source_end'],text=row['text'],reasons=reasons,
            previous=rows[index-1]['text'] if index else '',next=following['text'] if following else ''))
    for row in rows:row.pop('words')
    return result,dict(method='On-device editorial review, directional meaning checks and word-level restart repair' if semantic else 'Local rule-based assembled-script review; no general semantic model',
        semantic=semantic_report,changes=changes,flags=flags,script=rows)

def readable(report):
    lines=['FINAL SELECTED DIALOGUE',report.get('method','Rule-based checks')+'; listen to flagged joins.','']
    for row in report['script']:
        if row['text']:
            t=row['timeline_start'];lines.append(f"{int(t)//60:02}:{t%60:05.2f}  {row['text']}")
    lines.extend(['','CHECK THESE JOINS'])
    for flag in report['flags']:
        t=flag['timeline_start']
        lines.append(f"{int(t)//60:02}:{t%60:05.2f} | Clip {flag['clip']} | source {flag['source_start']:.2f}s")
        lines.append(f"Before: {flag['previous']}\nCheck: {flag['text']}\nAfter: {flag['next']}\nReason: {'; '.join(flag['reasons'])}\n")
    return '\n'.join(lines)+'\n'
