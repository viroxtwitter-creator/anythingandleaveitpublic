import sys,json,hashlib
sys.path.insert(0,'.analysis-deps')
import av
from pathlib import Path
from review_media import audio_sidecars
from analyze_speech import SOURCE
for i,x in enumerate(audio_sidecars(SOURCE)):
 def packets(path,index):
  c=av.open(str(path));s=c.streams.audio[index];print('meta',s.start_time,str(s.time_base),s.duration)
  c.seek(int(229e6));data={}
  for p in c.demux(s):
   if p.pts is None:continue
   t=float(p.pts*p.time_base)
   if t>236:break
   if t>=230:data[round(t*48000)]=hashlib.sha256(bytes(p)).hexdigest()
  c.close();return data
 a=packets(SOURCE,i);b=packets(x['path'],0)
 print('PACKETS',i,len(a),len(b),'keys',list(a)[:3],list(b)[:3], 'IDENTICAL',a==b)
