import json
from pathlib import Path
from review_core import merge_intervals,read_transcript,save_json

def length(xs):return sum(b-a for a,b in xs)
def intersect(xs,ys):return merge_intervals([(max(a,c),min(b,d)) for a,b in xs for c,d in ys if min(b,d)>max(a,c)])
results=[]
for i in (1,2,3):
 folder=Path('analysis/editing-style/references')
 rows=json.loads((folder/f'{i}-speech-labelled-selections.json').read_text())
 records=[]
 for source in sorted({r['source'] for r in rows}):
  selected=[r for r in rows if r['source']==source]
  truth=merge_intervals([(r['source_start'],r['source_end']) for r in selected]);lo=truth[0][0];hi=truth[-1][1]
  transcript=read_transcript(selected[0]['transcript_cache'])
  baseline=merge_intervals([(w['start']-.25,w['end']+.25) for s in transcript for w in s['words'] if w['end']>w['start']],lo,hi)
  overlap=length(intersect(truth,baseline));total=length(truth)
  records.append(dict(source=source,reference_kept_seconds=total,word_only_recovered_seconds=overlap,word_only_kept_seconds=length(baseline),scope_start=lo,scope_end=hi))
 total=sum(r['reference_kept_seconds'] for r in records);overlap=sum(r['word_only_recovered_seconds'] for r in records)
 results.append(dict(reference=i,source_count=len(records),reference_kept_seconds=total,word_only_recall=overlap/total if total else None,sources=records))
save_json(Path('analysis/editing-style/speech-only-baseline.json'),dict(description='Keep transcribed words plus 0.25s padding; compare unique source-time coverage within reference source spans. Partial/nominal mappings, not a viewer-retention or audio-quality metric.',results=results))
print(json.dumps([{k:v for k,v in r.items() if k!='sources'} for r in results],indent=2))
