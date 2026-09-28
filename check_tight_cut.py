from automatic_cut import plan
from automatic_sfx import prepare_effect,choose_placements
from review_core import save_json
from collections import Counter
r=plan(r'T:\Fortnite\Fortnite 2026.09.05 - 20.55.01.01.mp4',1,print)
e=prepare_effect();p=choose_placements(r,e)
save_json('analysis/tight-cut-check.json',r)
print('RESULT',len(r['kept']),sum(b-a for a,b in r['kept']),r['duplicate_takes'])
print('RETAKES',[(x['start'],x['earlier']) for x in r['removed_duplicates']])
print('ASSETS',[(k,round(v['duration'],2)) for k,v in e['assets'].items()])
print('SFX',Counter(x['kind'] for x in p))
