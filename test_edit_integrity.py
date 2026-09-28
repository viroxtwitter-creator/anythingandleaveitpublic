from script_review import restart_choice,review_script
from cut_integrity import protect_words
from test_contextual_takes import fixture


def row(text,start):
    t,r=fixture([text],[start])
    return dict(text=text,words=t[0]['words'],source_start=r[0][0],source_end=r[0][1])


assert restart_choice(row("Alright guys we're in game,",1),row("Alright guys we're in the shooting range using this setting.",3))=='old'
assert restart_choice(row("Alright guys we're in Paris,",1),row("Alright guys we're in the shooting range using this setting.",3)) is None
assert restart_choice(row("Alright guys we're in game.",1),row("Alright guys we're in the shooting range using this setting.",3)) is None
t,r=fixture(['This is a complete sentence that must remain.'])
k,report=review_script(t,r,audit_only=True)
assert k==r and not report['changes'],'Audit-only pass modified the edit'
# Protect the first word even if a waveform pass clips its quiet leading sound.
k,changes=protect_words([[1.12,r[0][1]]],t,[],30,60)
assert k[0][0]<=1 and changes
t,r=fixture(['This is a useful complete thought But','But let us start the next game.'])
k,report=review_script(t,r)
assert any(c['reason']=='Abandoned connecting word repeated at the next take' for c in report['changes'])
t=[dict(words=[dict(start=2,end=2.2,text=' with...'),dict(start=2.2,end=2.8,text=' Alright')])]
k,_=protect_words([[2.6,2.9]],t,[(1,2.1)],10,60)
assert 2.2<=k[0][0]<2.22,'Half-deleted word tail restored before the retained word'
from transcript_quality import clean
collapsed=dict(start=1,end=1.5,text='unreliable recognition',words=[dict(start=1,end=1.5,probability=.006,text=' for')]+
    [dict(start=1.5,end=1.5,probability=.5,text=' word') for _ in range(6)])
assert clean([collapsed])[0]==[]
valid=dict(collapsed,words=collapsed['words'][:3])
assert clean([valid])[0]==[valid],'Ordinary zero-duration alignment words were lost'
print('PASS: unfinished generic opener, named-place/complete-sentence safeguards, non-mutating audit')
