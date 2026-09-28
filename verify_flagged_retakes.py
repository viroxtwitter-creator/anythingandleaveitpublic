"""Regression audit for the user's Rainbow Six repeat at old timeline 01:00:04:32.

Run only after a fresh packaged export. This reads evidence; it changes no cuts.
"""
import json
from app_paths import ROOT

plan = json.loads((ROOT / 'analysis/last-automatic-cut.json').read_text())
assert '00.10.49.02' in plan['source'], 'This regression belongs to the flagged recording'
checks = [r for r in plan.get('transcript_rechecks', [])
          if 36 <= r['source_start'] <= 37 and r['accepted']]
assert checks, 'The collapsed introductory retake was not recovered'
assert any(r['start'] < 37 and 39.3 < r['end'] < 40
           for r in plan['removed_duplicates']), 'Recovered failed take was not removed'
assert not any(min(b, 39.4) > max(a, 36.67) for a, b in plan['kept']), (
    'The final cut still contains the failed introductory take')
assert any(a <= 40.1 and b >= 43.3 for a, b in plan['kept']), (
    'The complete replacement take was lost or clipped')
print(json.dumps(dict(run=plan['analysis_run_id'], recovered=checks,
                     retained_intro=[r for r in plan['kept'] if r[0] < 44 and r[1] > 36]), indent=2))
print('PASS: final exported plan excludes the flagged failed take and retains its complete replacement')
