import os
os.environ['QT_QPA_PLATFORM']='offscreen'
os.environ['QT_LOGGING_RULES']='qt.multimedia.*=false'
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'.analysis-deps'))
from review_core import *

def test_intervals():
    assert merge_intervals([[1,4],[3,7],[9,10]],0,8)==[[1,7]]
    assert complement([[1,4],[3,7]],0,10)==[[0,1],[7,10]]
    assert complement([[0,10]],0,10)==[]
    assert complement([],0,10)==[[0,10]]
    restored=[p for a,b in [[1,9]] for p in complement([[3,5]],a,b)]
    assert restored==[[1,3],[5,9]]

def test_speech():
    trans=json.loads((ROOT/'analysis/full-transcript.json').read_text())
    rows=build_rows(trans,1477.05)
    assert len(reference_rows())==8
    # A segment spans 71–336s: word-level grouping must leave the real long pause.
    assert any(r['kind']=='Quiet mic' and 100<r['start']<200 for r in rows)
    assert not any(r['kind']=='Speech' and r['start']<100 and r['end']>200 for r in rows)
    assert any(r['kind']=='Similar takes' and 18<r['start']<20 for r in rows)
    assert all(r['end']>r['start']>=0 for r in rows)
    return rows

def test_export(rows):
    source=ROOT/'example.mp4'
    dest=export_review(ROOT/'analysis/test-export',source,20,60,rows,{},[[2,4],[3,5],[10,12]])
    data=json.loads((dest/'review.json').read_text())
    assert data['removed']==[[2,5],[10,12]]
    assert data['kept']==[[0,2],[5,10],[12,20]]
    assert abs(sum(b-a for a,b in data['kept'])+sum(b-a for a,b in data['removed'])-20)<1e-8
    lua=(dest/'create_resolve_draft.lua').read_text()
    assert 'CreateEmptyTimeline' in lua and 'Delete' not in lua
    assert 'KEEP_RANGES' not in lua and 'EXPECTED_FPS' not in lua
    data=export_review(ROOT/'analysis/test-export-untouched',source,20,60,rows,{})
    assert json.loads((data/'review.json').read_text())['kept']==[[0,20]]

def test_gui():
    from cut_review import QApplication, Window, configure_app, QTimer
    app=QApplication([]);configure_app(app)
    w=Window();w.show();w.audio.setMuted(True)
    checks={'frame':False,'duration':False}
    def frame_received(frame):
        if frame.isValid():checks['frame']=True
    w.video.videoSink().videoFrameChanged.connect(frame_received)
    original_cuts=json.loads(json.dumps(w.cuts));original_decisions=dict(w.decisions)
    def exercise():
        try:
            assert w.list.count()==15
            w.select_row(0)
            assert 18<w.start.value()<20
            assert w.end.value()<w.current['end']
            w.start.setValue(230);w.end.setValue(231);w.cut()
            assert any(a<=230 and b>=231 for a,b in w.cuts)
            w.undo();assert w.cuts==original_cuts
            w.filter.setCurrentText('Your edit · reference');assert w.list.count()==8
            w.select_row(0)
            assert abs(w.start.value()-233.1)<.01
            checks['duration']=w.player.duration()>1400000
            assert len(w.player.audioTracks())==2
            w.filter.setCurrentText('Similar takes');w.select_row(0)
            print('GUI actions passed',flush=True)
        except Exception as e:
            checks['error']=repr(e)
    def finish():
        w.player.pause();w.grab().save(str(ROOT/'analysis/cut-review-preview.png'))
        w.cuts=original_cuts;w.decisions=original_decisions;w.save()
        print('PLAYBACK CHECK',checks,flush=True)
        w.close();app.quit()
    QTimer.singleShot(3000,exercise);QTimer.singleShot(9000,finish)
    app.exec()
    assert 'error' not in checks,checks
    assert checks['frame'], 'No decoded video frame'
    assert checks['duration'],'Source duration did not load'

if __name__=='__main__':
    test_intervals();rows=test_speech();test_export(rows);test_gui()
    print('ALL CHECKS PASSED')
