import json
from pathlib import Path
s=json.loads(Path('analysis/gunfire-v1-0cb45b0ee6e1a6-0.json').read_text());v=json.loads(Path('analysis/screen-check-v1-0cb45b0ee6e1a6-0.json').read_text());print('R6 screen checks',len(v),'/',sum(r['gun']>=.18 for r in s))
