import json
from app_paths import add_dependencies
add_dependencies()
import av
from PIL import Image,ImageDraw
v=json.load(open('analysis/screen-check-v1-10672ec2b8a42b-0.json'))
yes=[(float(t),r) for t,r in v.items() if r['gameplay']];no=[(float(t),r) for t,r in v.items() if not r['gameplay']]
rows=[a[i*len(a)//4] for a in (no,yes) for i in range(4)]
canvas=Image.new('RGB',(960,4*295));d=ImageDraw.Draw(canvas)
with av.open(r'T:\Fortnite\Fortnite 2026.09.05 - 20.55.01.01.mp4') as c:
 s=c.streams.video[0]
 for i,(t,r) in enumerate(rows):
  c.seek(int(t/s.time_base),stream=s);f=next(f for f in c.decode(s) if f.time>=t)
  im=f.to_image();im.thumbnail((480,265));x=i%2*480;y=i//2*295;canvas.paste(im,(x,y));d.text((x,y+267),f'{t:.2f}s '+('KEEP' if r['gameplay'] else 'REJECT')+' '+r['label'][16:64],fill='white')
canvas.save('analysis/screen-check-samples.jpg')
