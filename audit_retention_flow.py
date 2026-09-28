import json
from app_paths import ROOT
from automatic_cut import select_ranges
from review_core import save_json

def main():
    old=json.loads((ROOT/'exports/Automatic cut 20260906-235116-95700/automatic-plan.json').read_text())
    transcript=json.loads((ROOT/'analysis/transcript-10672ec2b8a42b-1.json').read_text())
    kept,speech,rows=select_ranges(transcript,old['action'],old['duration'])
    report=dict(previous_seconds=sum(b-a for a,b in old['kept']),new_seconds=sum(b-a for a,b in kept),
        previous_clips=len(old['kept']),new_clips=len(kept),decisions=rows,kept=kept)
    save_json(ROOT/'analysis/retention-flow-audit.json',report)
    for row in rows:print(round(row['start'],2),row['reason'],':',row['earlier'],'=>',row['kept'])
    print('SUMMARY', {k:v for k,v in report.items() if k not in ('decisions','kept')})
if __name__=='__main__':main()
