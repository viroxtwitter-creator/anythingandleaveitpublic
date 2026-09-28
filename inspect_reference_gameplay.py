from app_paths import add_dependencies
add_dependencies()
import av,json
from PIL import Image,ImageDraw
from pathlib import Path
out=Path('analysis/editing-style/references')
for num in (2,3):
 rows=json.loads((out/f'{num}-selections.json').read_text())
 rows=[r for r in rows if any(g in r['source'].lower() for g in ('fortnite','modern warfare'))]
 picks=[rows[round(i*(len(rows)-1)/11)] for i in range(12)]
 sheet=Image.new('RGB',(1600,900),'#191919');draw=ImageDraw.Draw(sheet);containers={}
 for j,r in enumerate(picks):
  source=r['source'];c=containers.setdefault(source,av.open(source)) if source not in containers else containers[source]
  v=c.streams.video[0];sec=(r['source_start']+r['source_end'])/2
  c.seek(int(sec/v.time_base),stream=v);f=next(f for f in c.decode(v) if f.time>=sec)
  im=f.to_image();im.thumbnail((400,220));x=j%4*400;y=j//4*300;sheet.paste(im,(x,y))
  draw.text((x+5,y+226),f"Timeline {r['start']:.1f}s / source {sec:.1f}s",fill='white')
  draw.text((x+5,y+244),f"Kept {r['end']-r['start']:.2f}s, nested depth {r['nested_depth']}",fill='white')
 for c in containers.values():c.close()
 sheet.save(out/f'{num}-selected-gameplay.jpg');print('contact sheet',num,flush=True)
