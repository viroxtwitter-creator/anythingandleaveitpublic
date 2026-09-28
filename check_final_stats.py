import json
from collections import Counter
r=json.load(open('analysis/last-automatic-cut.json'));print(r['source']);print('duplicates',r['duplicate_takes'],'sfx',Counter(x['kind'] for x in r['sfx_placements']));print('visual rejects',r['combat_checks']['visual_rejections']);print(r['folder'])
