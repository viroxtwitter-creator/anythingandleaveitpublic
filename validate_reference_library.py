import json,hashlib
from pathlib import Path
from review_core import read_transcript,save_json,merge_intervals
out=Path('analysis/editing-style/references')
coverage=[]
for num in (1,2,3):
 rows=json.loads((out/f'{num}-selections.json').read_text());labelled=[]
 for source in sorted({r['source'] for r in rows}):
  p=Path(source)
  if p.suffix.lower() not in ('.mp4','.mov'):continue
  st=p.stat();key=hashlib.sha1(f'{p.resolve()}:{st.st_size}:{st.st_mtime_ns}'.encode()).hexdigest()[:14]
  cache=Path('analysis')/f'transcript-{key}-1.json';transcript=read_transcript(cache)
  if transcript is None:continue
  words=[w for s in transcript for w in s['words'] if w['end']>w['start']]
  for r in rows:
   if r['source']!=source:continue
   a,b=r['source_start'],r['source_end'];ws=[w for w in words if w['end']>a and w['start']<b]
   spans=merge_intervals([(w['start'],w['end']) for w in ws],a,b)
   labelled.append(dict(r,transcript_cache=str(cache),source_words=''.join(w['text'] for w in ws).strip(),speech_seconds=sum(y-x for x,y in spans)))
 save_json(out/f'{num}-speech-labelled-selections.json',labelled)
 coverage.append(dict(reference=num,selections_with_cached_transcript=len(labelled),no_transcribed_source_words=sum(not r['source_words'] for r in labelled)))
print(coverage)
lib=json.loads((out/'library.json').read_text())
policy=dict(version=2,target_duration_seconds=None,reference_files=[r['project'] for r in lib['references']],
 selection_rules=['Select meaningful demonstrations, action outcomes and useful reactions.','Compress approach and waiting while preserving understandable setup and payoff.','Keep dialogue by meaning and sentence boundaries, not volume alone.','Retain important quiet-mic gameplay.','Treat purposeful menus and feature demonstrations differently from idle menu time.','Use short picture selections for clear actions, with longer holds where understanding needs them.','Do not enforce median shot length or a target total duration.','Do not learn from unexported leftover timeline material.'],
 evidence_scope='DRP structure, nominal base-track compound mapping, sampled source/export frames and available cached transcripts. Not a trained standalone selector.',
 speech_coverage=coverage,
 validation_required=['Check source-selection quality on recordings not used as references.','Listen to joins and dialogue before declaring a finished-quality edit.','Validate rendered overlay and retime mappings before using them as strong training labels.'])
save_json(Path('analysis/editing-style/reference-guided-policy.json'),policy)
for num in (1,2,3):
 rows=json.loads((out/f'{num}-selections.json').read_text());report=json.loads((out/f'{num}-profile.json').read_text())
 assert all(0<=r['start']<r['end']<=report['finished_duration']+.001 for r in rows)
 assert all(r['source_end']>r['source_start'] for r in rows)
 assert all(rows[i]['end']<=rows[i+1]['start']+.001 for i in range(len(rows)-1))
x=json.loads((out/'1-selections.json').read_text());sample=[r for r in x if 57.38<=r['start']<79.05]
assert len(sample)==8 and abs(sum(r['end']-r['start'] for r in sample)-1300/60)<1e-6
assert len(json.loads((out/'2-profile.json').read_text())['excluded_after_export'])==1
print('PASS: reference placements, known eight-cut sample, export bounds and excluded Fortnite leftover.')
