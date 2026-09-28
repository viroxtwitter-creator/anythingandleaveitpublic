"""Invariant audit across every cached recording, without touching Resolve."""
import json
from app_paths import ROOT
from dialogue_cut import clean_dialogue
from review_core import save_json

reports=[]
for path in sorted((ROOT/'analysis').glob('transcript-*.json')):
    transcript=json.loads(path.read_text(encoding='utf-8'))
    words=[w for s in transcript for w in s['words']]
    if not words:continue
    duration=max(w['end'] for w in words)+1
    ranges,cuts,decisions=clean_dialogue(transcript,duration)
    assert all(0<=a<b<=duration for a,b in ranges),path
    assert all(a[1]<=b[0] for a,b in zip(ranges,ranges[1:])),path
    assert all(not(a<d and b>c) for a,b in ranges for c,d in cuts),path
    assert all(r['end']<=r['kept_start'] for r in decisions),path
    reports.append(dict(transcript=path.name,words=len(words),decisions=decisions,kept_seconds=sum(b-a for a,b in ranges)))
save_json(ROOT/'analysis/retention-only-corpus-audit.json',reports)
print('PASS:',len(reports),'cached transcripts;',sum(r['words'] for r in reports),'words; bounded ordered cuts and retained-onset checks')
