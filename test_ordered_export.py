import json,tempfile
from pathlib import Path
from review_core import export_review
with tempfile.TemporaryDirectory() as d:
 p=Path(d)
 ranges=[[8,10],[1,4],[8,10]]
 export_review(p/'ordered','source.mp4',12,60,[],{},keep_ranges=ranges,timeline_prefix='AUTO ',draft_note='AI-selected draft')
 data=json.loads((p/'ordered/review.json').read_text())
 assert data['kept']==ranges
 assert data['removed']==[[0,1],[4,8],[10,12]]
 lua=(p/'ordered/create_resolve_draft.lua').read_text()
 assert '{8.000000, 10.000000},\n{1.000000, 4.000000},\n{8.000000, 10.000000}' in lua
 assert 'Only manually marked' not in lua
 export_review(p/'old','source.mp4',12,60,[],{},cuts=[[2,4]])
 assert json.loads((p/'old/review.json').read_text())['kept']==[[0,2],[4,12]]
 for bad in ([], [[-1,2]], [[1,13]], [[2,2]], [[float('nan'),2]]):
  try:export_review(p/'bad','source.mp4',12,60,[],{},keep_ranges=bad)
  except ValueError:pass
  else:raise AssertionError(bad)
print('PASS: ordered teaser/repeated ranges, original removal workflow, invalid-plan rejection')
