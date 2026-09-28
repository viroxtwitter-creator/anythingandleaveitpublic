from app_paths import add_dependencies
add_dependencies()
import av
from PIL import Image,ImageDraw
from pathlib import Path
out=Path('analysis/editing-style/references')
for num,name,times in [(2,'astrion fortnite.mov',[2,30,53,76,99,121,144,162,183,200,218,240]),(3,'arctic MW4.mov',[3,15,30,45,60,75,90,110,130,146,161,177])]:
 c=av.open(str(Path(r'C:\Users\jordan\Desktop\F VIDEOS')/name));v=c.streams.video[0];sheet=Image.new('RGB',(1600,900),'#191919');d=ImageDraw.Draw(sheet)
 for j,sec in enumerate(times):
  c.seek(int(sec/v.time_base),stream=v);f=next(f for f in c.decode(v) if f.time>=sec);im=f.to_image();im.thumbnail((400,225));x=j%4*400;y=j//4*300;sheet.paste(im,(x,y));d.text((x+5,y+232),f'Finished export {sec}s',fill='white')
 c.close();sheet.save(out/f'{num}-finished-export.jpg');print('export sheet',num,flush=True)
