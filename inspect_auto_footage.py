from app_paths import add_dependencies
add_dependencies()
import av
from PIL import Image,ImageDraw
from pathlib import Path
source=Path(r'T:\Arc Raiders\Arc Raiders 2026.09.04 - 00.14.54.03.mp4')
out=Path('analysis/auto-cut');out.mkdir(exist_ok=True)
c=av.open(str(source));v=c.streams.video[0]
print('fps',v.base_rate,'size',v.width,v.height,flush=True)
for page in range(4):
 sheet=Image.new('RGB',(1600,1000),'#171717');draw=ImageDraw.Draw(sheet)
 for i in range(20):
  sec=(page*20+i)*15
  c.seek(int(sec/v.time_base),stream=v)
  frame=next((f for f in c.decode(v) if f.time>=sec),None)
  if frame is None:continue
  im=frame.to_image();im.thumbnail((320,175))
  x=i%5*320;y=i//5*250
  sheet.paste(im,(x,y));draw.text((x+8,y+182),f'{sec//60:02}:{sec%60:02} / {sec}s',fill='white')
 sheet.save(out/f'overview-{page+1}.jpg')
 print('page',page+1,flush=True)
c.close()
