"""Compare DRP references, resolving nominal base-track compound placements.
Not a rendered visibility reconstruction: overlays, transitions and retimes need review.
"""
import collections,json,re,statistics,struct,zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
from app_paths import ROOT,add_dependencies
add_dependencies()
import av
from learn_edit_reference import frame_value
from review_core import save_json

def doubles(s):return struct.unpack('<dd',bytes.fromhex(s))
def analyse(path):
 with zipfile.ZipFile(path) as z:
  roots={n:ET.fromstring(re.sub(r'(<\/?\w+)::',r'\1__',z.read(n).decode())) for n in z.namelist() if n.endswith('.xml')}
 ids={e.get('DbId'):e for r in roots.values() for e in r.iter() if e.get('DbId')}
 sequences={e.get('DbId'):e for r in roots.values() for e in r.iter('Sm2Sequence')}
 containers={r.findtext('.//Sm2TiTrack/Sequence'):(n,r) for n,r in roots.items() if r.find('VideoTrackVec') is not None}
 mains=[(sid,s) for sid,s in sequences.items() if ids.get(s.findtext('Parent')) is not None and ids[s.findtext('Parent')].tag=='Sm2Timeline']
 assert len(mains)==1,(path.name,'Ambiguous main timeline')
 sid,seq=mains[0];fps=doubles(seq.findtext('FrameRate'))[0];origin,duration=doubles(seq.findtext('MediaExtents'))
 unresolved=[]
 def walk(sid,chain=()):
  if sid in chain:raise ValueError('Compound cycle')
  s=sequences[sid];rate=doubles(s.findtext('FrameRate'))[0];zero=doubles(s.findtext('MediaExtents'))[0]
  if sid not in containers:return []
  tracks=containers[sid][1].find('VideoTrackVec')
  if not len(tracks):return []
  result=[]
  for c in tracks[0].iter('Sm2TiVideoClip'):
   start=frame_value(c.findtext('Start'))/rate-zero;dur=frame_value(c.findtext('Duration'))/rate
   source=c.findtext('MediaFilePath');ref=c.findtext('MediaRef');owner=ids.get(ref)
   source_rate=doubles(c.findtext('MediaFrameRate'))[0] if c.findtext('MediaFrameRate') else rate
   inside=(frame_value(c.findtext('In')) or 0)/(source_rate or rate)
   if source:
    result.append(dict(start=start,end=start+dur,source_start=inside,source_end=inside+dur,
     source=source,name=c.findtext('Name'),entry_ids=[c.get('DbId')],nested_depth=len(chain),mapping='nominal constant-speed'))
   elif owner is not None and owner.find('./Sequence/Sm2Sequence') is not None:
    child=owner.find('./Sequence/Sm2Sequence');child_id=child.get('DbId')
    for leaf in walk(child_id,chain+(sid,)):
     a=max(inside,leaf['start']);b=min(inside+dur,leaf['end'])
     if b<=a:continue
     offset=a-leaf['start'];r=dict(leaf,start=start+a-inside,end=start+b-inside,
      source_start=leaf['source_start']+offset,source_end=leaf['source_start']+offset+b-a,
      entry_ids=[c.get('DbId')]+leaf['entry_ids']);result.append(r)
   else:unresolved.append(dict(name=c.findtext('Name'),start=start,duration=dur,depth=len(chain),reason='non-source title/generator or unresolved reference'))
  return sorted(result,key=lambda r:r['start'])
 export_names={'1st video example Rainbow 6 Siege.drp':'arctic unlock frost.mov','2nd video example fortnite.drp':'astrion fortnite.mov','3rd video example mw4.drp':'arctic MW4.mov'}
 export=Path(r'C:\Users\jordan\Desktop\F VIDEOS')/export_names[path.name]
 with av.open(str(export)) as media:export_duration=media.duration/av.time_base
 # These exports were checked at multiple matching timeline positions. Extra
 # project material beyond the rendered end is not a finished-edit example.
 leaves=walk(sid);excluded=[r for r in leaves if r['start']>=export_duration];kept=[]
 for r in leaves:
  if r['start']>=export_duration:continue
  r=dict(r)
  if r['end']>export_duration:
   r['source_end']-=r['end']-export_duration;r['end']=export_duration
  kept.append(r)
 leaves=kept;runs=[]
 for r in leaves:
  if runs and runs[-1]['source']==r['source'] and abs(runs[-1]['end']-r['start'])<1e-6 and abs(runs[-1]['source_end']-r['source_start'])<1e-6:
   runs[-1]['end']=r['end'];runs[-1]['source_end']=r['source_end'];runs[-1]['entry_ids']+=r['entry_ids']
  else:runs.append(dict(r))
 by_source=[]
 for source in sorted({r['source'] for r in runs}):
  clips=[r for r in runs if r['source']==source];lengths=[r['end']-r['start'] for r in clips]
  by_source.append(dict(source=source,exists=Path(source).is_file(),selections=len(clips),seconds=sum(lengths),median=statistics.median(lengths),minimum=min(lengths),maximum=max(lengths)))
 all_paths=sorted({e.text for r in roots.values() for e in r.iter('MediaFilePath') if e.text})
 audio_names=collections.Counter(c.findtext('Name') for c in containers[sid][1].iter('Sm2TiAudioClip') if (c.findtext('MediaFilePath') or '').lower().endswith(('.mp3','.wav')))
 gameplay=[r for r in runs if any(game in r['source'].lower() for game in ('rainbow six siege','fortnite','modern warfare'))]
 lengths=[r['end']-r['start'] for r in gameplay]
 report=dict(project=path.name,sequence=containers[sid][0],fps=fps,duration=duration,
  finished_export=str(export),finished_duration=export_duration,excluded_after_export=excluded,
  available_media=len(all_paths),missing_media=[p for p in all_paths if not Path(p).is_file()],
  nominal_base_source_selections=len(runs),nested_leaf_entries=sum(r['nested_depth']>0 for r in leaves),
  nominal_gameplay_selections=len(gameplay),gameplay_median=statistics.median(lengths) if lengths else None,
  gameplay_min=min(lengths) if lengths else None,gameplay_max=max(lengths) if lengths else None,
  sources=by_source,common_audio_assets=audio_names.most_common(8),
  limitations=['Nominal base-track mapping includes compound placements; does not establish topmost rendered visibility or retimed source mapping.','No inference that omitted material is uninteresting without audiovisual comparison.'])
 return report,runs,unresolved

def main():
 out=ROOT/'analysis/editing-style/references';out.mkdir(exist_ok=True)
 reports=[]
 for i,path in enumerate(sorted(ROOT.glob('*.drp')),1):
  report,runs,unresolved=analyse(path);reports.append(report)
  save_json(out/f'{i}-profile.json',report);save_json(out/f'{i}-selections.json',runs);save_json(out/f'{i}-non-source-items.json',unresolved)
  print(json.dumps({k:v for k,v in report.items() if k not in ('sources','common_audio_assets','limitations')},indent=2))
 save_json(out/'library.json',dict(target_duration_seconds=None,references=reports,status='reference extraction, not a trained model'))
if __name__=='__main__':main()
