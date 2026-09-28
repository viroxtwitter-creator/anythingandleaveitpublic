exec(open('inspect_edit.py',encoding='utf-8-sig').read().split("f=r'")[0])
z=zipfile.ZipFile(next(pathlib.Path('.').glob('*.drp')))
root=ET.fromstring(re.sub(r'(<\/?\w+)::',r'\1__',z.read('SeqContainer/fe39524a-9428-4ddd-a92f-5f87e2e33fbf.xml').decode()))
track=root.find('VideoTrackVec').find('.//Sm2TiTrack')
clips=[]
for e in track.iter('Sm2TiVideoClip'):
 clips.append({k:e.findtext(k) for k in ['Name','Start','Duration','In','MediaFilePath']})
print('BASE TRACK')
for e in clips:
 print(round((int(e['Start'])-216000)/60,2),round(int(e['Duration'])/60,2),round(int(e['In'])/60,2) if e['In'] else None,e['Name'])
print('SOURCE STREAMS')
for p in sorted(set(e['MediaFilePath'] for e in clips if e['MediaFilePath'])):
 c=av.open(p);print(pathlib.Path(p).name,round(c.duration/1e6,2),[(s.type,str(s.average_rate) if s.type=='video' else s.codec_context.channels if s.type=='audio' else '') for s in c.streams]);c.close()
