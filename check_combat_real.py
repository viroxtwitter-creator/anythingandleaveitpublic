import json
from dialogue_cut import clean_dialogue
x=json.load(open('analysis/transcript-10672ec2b8a42b-1.json'));s,c,r=clean_dialogue(x,1254.966)
print('Removed repeats',len(r))
for a in r:print(a['earlier'],'=>',a['kept'])
from combat_detection import detect
from pathlib import Path
source=Path(r'T:\Fortnite\Fortnite 2026.09.05 - 20.55.01.01.mp4')
events,info=detect(source,Path('analysis/action-audio-10672ec2b8a42b-0.wav'),'10672ec2b8a42b-0',1254.966,lambda s:print(s,flush=True),lambda:False)
Path('analysis/combat-first-test.json').write_text(json.dumps(dict(events=events,info=info),indent=2));print('Accepted',len(events),sum(b-a for a,b in events),info['visual_rejections'],flush=True)
