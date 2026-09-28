import os
os.environ['QT_QPA_PLATFORM']='offscreen'
os.environ['QT_LOGGING_RULES']='qt.multimedia.*=false'
from simple_review import *

app=QApplication([]);configure_app(app)
w=SimpleWindow();w.show();w.audio.setMuted(True)
original_cuts=json.loads(json.dumps(w.cuts));original_decisions=dict(w.decisions)
checks={}
def exercise():
    try:
        assert w.pages.currentIndex()==0
        assert not w.audio_help.isVisible(), 'Named microphone should not need a setup choice'
        assert not w.engine_ui.isVisible()
        w.cuts=[];w.decisions={};w.begin()
        assert w.pages.currentIndex()==1 and len(w.cards)==15
        assert not w.adjust.isVisible()
        w.watch_cut();assert w.trial_cut and not w.cuts
        w.choose(True);assert w.cuts and w.card_index==1
        w.undo_choice();assert not w.cuts and w.card_index==0
        w.choose(False);assert not w.cuts and w.card_index==1
        w.finish_review();assert w.pages.currentIndex()==2 and not w.send_button.isEnabled()
        w.back_to_review();w.choose(True);w.finish_review()
        assert w.send_button.isEnabled()
        w.sent('test','Created Cut Review draft test with separate audio.');w.send_done()
        assert not w.send_button.isEnabled() and 'Done' in w.done_summary.text()
        w.sent('test','Export saved, but Resolve import did not finish.');w.send_done()
        assert w.send_button.isEnabled() and 'confirmed' in w.note.text()
        w.set_page(0);w.grab().save(str(ROOT/'analysis/simple-step-1.png'))
        w.set_page(1);w.show_card();w.watch_original()
        checks['passed']=True
    except Exception as e:checks['error']=repr(e)
def finish():
    w.player.pause();w.grab().save(str(ROOT/'analysis/simple-step-2.png'))
    w.cuts=original_cuts;w.decisions=original_decisions;w.save();w.close();app.quit()
QTimer.singleShot(2000,exercise);QTimer.singleShot(5000,finish)
app.exec();print(checks)
assert checks.get('passed') and 'error' not in checks,checks
