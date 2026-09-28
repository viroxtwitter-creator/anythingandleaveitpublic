import json
from automatic_sfx import prepare_effect,choose_placements,contextual_candidates
assets=prepare_effect()['assets']
def ws(text):return [dict(text=t,start=i*.15,end=i*.15+.1,probability=.99) for i,t in enumerate(text.split())]
assert not contextual_candidates(ws('if we lost'),assets)
assert not contextual_candidates(ws('we nearly died'),assets)
assert not contextual_candidates(ws('if it is not working'),assets)
assert any(c['kind']=='boom' for c in contextual_candidates(ws('oh my god'),assets))
assert any(c['kind']=='fail' for c in contextual_candidates(ws('we lost'),assets))
assert any(c['kind']=='success' for c in contextual_candidates(ws('lets go'),assets))
assert any(c['kind']=='data' for c in contextual_candidates(ws('look at the numbers'),assets))
assert any(c['kind']=='cinematic' for c in contextual_candidates(ws('there it is'),assets))
r=json.load(open('analysis/last-automatic-cut.json'));p=choose_placements(r,dict(assets=assets));fps=r['fps']
assert len(p)>4
assert all(a['start_frame']+a['duration_frames']+fps<=b['start_frame'] for a,b in zip(p,p[1:]))
memes=[a for a in p if a['group']=='memes'];assert all(b['start_frame']-a['start_frame']>=30*fps for a,b in zip(memes,memes[1:]))
assert all('Spoken cue:' in a['reason'] for a in memes)
transition_kinds={a['kind'] for a in p if a['priority']==1}
assert transition_kinds-{'whoosh','sweep'},'Transition design should use more than whooshes.'
print('PASS: contextual cues, hypothetical exclusions, nonoverlap, meme spacing;',len(p),'effects.')
