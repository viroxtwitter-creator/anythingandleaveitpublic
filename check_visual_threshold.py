import json
v=json.load(open('analysis/screen-check-v1-10672ec2b8a42b-0.json'))
from collections import Counter
print(Counter(r['label'] for r in v.values() if r['margin']<0))
print('negative',sum(r['margin']<0 for r in v.values()))
from combat_detection import ScreenCheck
import av
m=ScreenCheck()
with av.open(r'T:\Fortnite\Fortnite 2026.09.05 - 20.55.01.01.mp4') as c:
 s=c.streams.video[0]
 for t in [0,100,150,200,300]:
  c.seek(int(t/s.time_base),stream=s);f=next(f for f in c.decode(s) if f.time>=t);r=m.classify(f.to_image());print(t,r['margin'],r['label'])
