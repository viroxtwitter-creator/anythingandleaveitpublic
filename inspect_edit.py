import sys, pathlib, zipfile, re, xml.etree.ElementTree as ET, json
sys.path.insert(0,str(pathlib.Path('.analysis-deps').resolve()))
import av
from PIL import Image, ImageDraw
out=pathlib.Path('analysis');out.mkdir(exist_ok=True)
f=r'C:\Users\jordan\Desktop\F VIDEOS\arctic unlock frost.mov'
c=av.open(f)
print('EXPORT', [(s.type,str(s.codec_context.name) if s.codec_context else None,str(s.duration),str(s.time_base)) for s in c.streams])
canvas=Image.new('RGB',(960,4*205),'#171717'); draw=ImageDraw.Draw(canvas)
for i,t in enumerate([2,10,20,35,50,65,80,95,110,130,150,170]):
 c.seek(int(t*1000000))
 for frame in c.decode(video=0):
  if frame.time>=t:break
 im=frame.to_image();im.thumbnail((320,180));x=i%3*320;y=i//3*205;canvas.paste(im,(x,y));draw.text((x+5,y+182),f'{t//60:02}:{t%60:02}',fill='white')
canvas.save(out/'export-overview.jpg');c.close()
z=zipfile.ZipFile(next(pathlib.Path('.').glob('*.drp')))
s='SeqContainer/fe39524a-9428-4ddd-a92f-5f87e2e33fbf.xml'
root=ET.fromstring(re.sub(r'(<\/?\w+)::',r'\1__',z.read(s).decode()))
print('ROOT',root.tag)
print('CHILDREN',[(e.tag,len(e)) for e in root])
for e in root.iter():
 if 'Track' in e.tag and len(e)>2:
  clips=[n for n in e.iter() if n.tag in ['Sm2TiVideoClip','Sm2TiAudioClip']]
  if clips:print('TRACK',e.tag,[(n.tag,(n.text or '')[:80]) for n in e if len(n)==0 and 'Blob' not in n.tag][:10],len(clips))
rows=[]
for e in root.iter():
 if e.tag in ['Sm2TiVideoClip','Sm2TiAudioClip']:
  rows.append(dict(type=e.tag,**{n.tag:n.text for n in e if n.tag in ['Name','Start','Duration','In','MediaFilePath']}))
(out/'main-timeline.json').write_text(json.dumps(rows,indent=2))
print('FIRST',json.dumps(rows[:8]))

