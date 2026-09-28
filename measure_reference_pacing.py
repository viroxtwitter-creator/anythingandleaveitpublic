"""Measure source-word handles in nominal reference picture selections."""
import hashlib,json,statistics
from pathlib import Path
from app_paths import ROOT

def main():
    rows=[]
    for number in (1,2,3):
        selections=json.loads((ROOT/f'analysis/editing-style/references/{number}-speech-labelled-selections.json').read_text())
        cache={}
        for selection in selections:
            source=Path(selection['source'])
            if not source.is_file():continue
            if str(source) not in cache:
                st=source.stat();key=hashlib.sha1(f'{source.resolve()}:{st.st_size}:{st.st_mtime_ns}'.encode()).hexdigest()[:14]
                labelled=ROOT/selection.get('transcript_cache','missing')
                paths=[labelled] if labelled.is_file() else list((ROOT/'analysis').glob(f'transcript-{key}-*.json'))
                # Only unambiguous cached microphone transcripts are eligible.
                cache[str(source)]=[w for s in json.loads(paths[0].read_text()) for w in s['words']] if len(paths)==1 else []
            a,b=selection['source_start'],selection['source_end']
            words=[w for w in cache[str(source)] if w['end']>a and w['start']<b and 0<w['end']-w['start']<3]
            if len(words)<3:continue
            lead=words[0]['start']-a;tail=b-words[-1]['end']
            # Exclude cut-through words and long action holds from dialogue handle estimates.
            rows.append(dict(reference=number,lead=lead,tail=tail,source=str(source),start=a,end=b))
    assert rows,'No eligible reference timing samples'
    report=dict(scope='Nominal source picture edges versus cached ASR word times; not acoustic alignment or J/L-cut measurement',samples=rows,
        references={str(n):sum(r['reference']==n for r in rows) for n in (1,2,3)},
        eligible_leads=sum(0<=r['lead']<=.6 for r in rows),eligible_tails=sum(0<=r['tail']<=.6 for r in rows),
        cut_through_start=sum(r['lead']<0 for r in rows),cut_through_end=sum(r['tail']<0 for r in rows),
        lead_median=statistics.median(r['lead'] for r in rows if 0<=r['lead']<=.6),
        tail_median=statistics.median(r['tail'] for r in rows if 0<=r['tail']<=.6))
    path=ROOT/'analysis/editing-style/dialogue-pacing.json'
    path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
if __name__=='__main__':main()
