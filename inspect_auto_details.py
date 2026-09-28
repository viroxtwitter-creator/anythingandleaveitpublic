from app_paths import add_dependencies
add_dependencies()
import av
from PIL import Image,ImageDraw
from pathlib import Path
out=Path('analysis/auto-cut')
c=av.open(r'T:\Arc Raiders\Arc Raiders 2026.09.04 - 00.14.54.03.mp4');v=c.streams.video[0]
groups=[list(range(198,235,2)),list(range(932,971,2)),list(range(982,1021,2)),list(range(1088,1127,2))]
for page,times in enumerate(groups):
 sheet=Image.new('RGB',(1600,880),'#171717');d=ImageDraw.Draw(sheet)
 for i,sec in enumerate(times):
  c.seek(int(sec/v.time_base),stream=v)
  f=next(f for f in c.decode(v) if f.time>=sec)
  im=f.to_image();im.thumbnail((320,180));x=i%5*320;y=i//5*220
  sheet.paste(im,(x,y));d.text((x+8,y+185),f'{sec//60:02}:{sec%60:02} / {sec}s',fill='white')
 sheet.save(out/f'detail-{page+1}.jpg');print('detail',page+1,flush=True)
c.close()
