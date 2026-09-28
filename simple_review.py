"""Three-step front end for the existing local review and Resolve engines."""
from cut_review import *
from PySide6.QtWidgets import QStackedWidget, QProgressBar

class SimpleWindow(Window):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Cut Review — simple mode')
        self.resize(1020,820)
        self.engine_ui=self.takeCentralWidget()
        self.engine_ui.hide()
        self.engine_ui.setParent(self)
        self.cards=[];self.card_index=0;self.choice_history=[];self.trial_cut=None;self.busy=False
        base=QWidget();self.setCentralWidget(base)
        layout=QVBoxLayout(base);layout.setContentsMargins(30,22,30,22);layout.setSpacing(14)
        title=QLabel('Cut Review');title.setObjectName('title');layout.addWidget(title)
        self.steps=QLabel();self.steps.setObjectName('muted');layout.addWidget(self.steps)
        self.pages=QStackedWidget();layout.addWidget(self.pages,1)
        self.note=QLabel('');self.note.setWordWrap(True);self.note.setObjectName('muted');layout.addWidget(self.note)
        self.make_choose_page();self.make_review_page();self.make_done_page()
        pref=ROOT/'analysis'/'simple-preferences.json'
        if pref.exists():
            try:
                last=Path(json.loads(pref.read_text())['source'])
                if last.exists() and last!=self.source:self.load_source(last)
            except (ValueError,KeyError,OSError):pass
        self.update_choice();self.set_page(0)

    def heading(self,text):
        label=QLabel(text);label.setStyleSheet('font-size:24px; font-weight:600;');label.setWordWrap(True);return label
    def action(self,text,fn,primary=False):
        b=self.button(text,fn)
        if primary:b.setObjectName('primary')
        b.setMinimumHeight(46);return b
    def make_choose_page(self):
        page=QWidget();l=QVBoxLayout(page);l.setSpacing(18)
        l.addStretch();l.addWidget(self.heading('1. Choose your recording'))
        intro=QLabel('We’ll find possible repeated takes. You decide which ones to remove.');intro.setWordWrap(True);l.addWidget(intro)
        self.file_label=QLabel();self.file_label.setWordWrap(True);self.file_label.setStyleSheet('background:#1c2633; padding:20px; border-radius:8px;');l.addWidget(self.file_label)
        self.choose_button=self.action('Choose another video',self.open_source);l.addWidget(self.choose_button)
        # Only ask about microphone selection when the recording has no useful label.
        self.audio_help=QWidget();a=QVBoxLayout(self.audio_help)
        a.addWidget(QLabel('Which audio track is your voice?'))
        a.addWidget(self.mic)
        self.voice_test=self.action('Listen to selected track',self.test_voice);a.addWidget(self.voice_test)
        l.addWidget(self.audio_help)
        self.begin_button=self.action('Find repeated takes',self.begin,True);l.addWidget(self.begin_button)
        self.progress=QProgressBar();self.progress.setRange(0,0);self.progress.hide();l.addWidget(self.progress)
        l.addWidget(QLabel('Your recording stays on this PC. No setup needed for the example video.'))
        l.addStretch();self.pages.addWidget(page)
    def make_review_page(self):
        page=QWidget();l=QVBoxLayout(page);l.setSpacing(12)
        top=QHBoxLayout();self.counter=self.heading('2. Check one suggestion');top.addWidget(self.counter);top.addStretch()
        self.finish_button=self.button('Finish for now',self.finish_review);top.addWidget(self.finish_button);l.addLayout(top)
        self.question=QLabel();self.question.setWordWrap(True);l.addWidget(self.question)
        self.video.setMinimumSize(400,230);l.addWidget(self.video,1)
        l.addWidget(self.slider)
        playback=QHBoxLayout()
        playback.addWidget(self.action('Watch original',self.watch_original))
        playback.addWidget(self.action('Preview suggested cut',self.watch_cut))
        playback.addWidget(self.button('Play / Pause',self.toggle_play))
        playback.addWidget(self.clock);l.addLayout(playback)
        self.range_note=QLabel();self.range_note.setWordWrap(True);self.range_note.setObjectName('muted');l.addWidget(self.range_note)
        self.adjust_toggle=QPushButton('Adjust timing (optional)');self.adjust_toggle.setCheckable(True);l.addWidget(self.adjust_toggle)
        self.adjust=QWidget();al=QHBoxLayout(self.adjust)
        al.addWidget(QLabel('Remove from'));al.addWidget(self.start);al.addWidget(QLabel('to'));al.addWidget(self.end)
        al.addWidget(self.button('Start here',lambda:self.start.setValue(self.player.position()/1000)))
        al.addWidget(self.button('End here',lambda:self.end.setValue(self.player.position()/1000)))
        al.addWidget(QLabel('Audio'));al.addWidget(self.listen)
        self.adjust.hide();self.adjust_toggle.toggled.connect(self.adjust.setVisible);l.addWidget(self.adjust)
        decisions=QHBoxLayout()
        self.keep_button=self.action('Keep both',lambda:self.choose(False));decisions.addWidget(self.keep_button)
        self.remove_button=self.action('Remove earlier take',lambda:self.choose(True),True);decisions.addWidget(self.remove_button);l.addLayout(decisions)
        bottom=QHBoxLayout();self.undo_button=self.button('Undo last choice',self.undo_choice);bottom.addWidget(self.undo_button);bottom.addStretch()
        bottom.addWidget(QLabel('Unsure? Choose Keep both.'));l.addLayout(bottom)
        self.pages.addWidget(page)
    def make_done_page(self):
        page=QWidget();l=QVBoxLayout(page);l.setSpacing(18);l.addStretch()
        l.addWidget(self.heading('3. Continue in DaVinci Resolve'))
        self.done_summary=QLabel();self.done_summary.setWordWrap(True);l.addWidget(self.done_summary)
        self.done_help=QLabel('Open your project in Resolve, then click below. We’ll create a separate draft with your approved cuts.');self.done_help.setWordWrap(True);l.addWidget(self.done_help)
        self.send_button=self.action('Send to Resolve',self.send_simple,True);l.addWidget(self.send_button)
        self.send_progress=QProgressBar();self.send_progress.setRange(0,0);self.send_progress.hide();l.addWidget(self.send_progress)
        self.back_button=self.action('Back to suggestions',self.back_to_review);l.addWidget(self.back_button)
        self.another_button=self.action('Choose a different recording',lambda:self.set_page(0));l.addWidget(self.another_button)
        l.addStretch();self.pages.addWidget(page)
    def set_page(self,index):
        self.player.pause();self.trial_cut=None;self.pages.setCurrentIndex(index)
        self.steps.setText(['1  CHOOSE VIDEO     →     2  REVIEW     →     3  SEND TO RESOLVE',
                            '1  Choose video     →     2  REVIEW     →     3  Send to Resolve',
                            '1  Choose video     →     2  Review     →     3  SEND TO RESOLVE'][index])
        self.note.setText('Nothing is removed unless you choose it.')
    def load_source(self,path):
        self.trial_cut=None
        super().load_source(path)
        if hasattr(self,'pages'):
            self.choice_history=[];self.cards=[];self.card_index=0;self.update_choice()
            save_json(ROOT/'analysis'/'simple-preferences.json',{'source':str(self.source)})
    def update_choice(self):
        if not self.source:
            self.file_label.setText('Choose a gameplay recording to get started.');self.begin_button.setEnabled(False);self.audio_help.hide();return
        self.file_label.setText(self.source.name+'\n'+stamp(self.duration)+' long')
        named=any('mic' in n.lower() for n in self.stream_names)
        if named:self.file_label.setText(self.file_label.text()+'\nVoice track: '+self.stream_names[self.mic.currentIndex()]+' (selected automatically)')
        self.audio_help.setVisible(not named and len(self.stream_names)>1)
        self.begin_button.setEnabled(bool(self.stream_names));self.begin_button.setText('Find repeated takes')
        if not self.stream_names:self.note.setText('This video has no audio. Choose a recording with your voice.')
    def test_voice(self):
        self.player.setActiveAudioTrack(self.mic.currentIndex());self.play_at(8,min(18,self.duration))
        self.note.setText('Listening to the selected track. Choose the one containing your voice.')
    def begin(self):
        if not self.source or self.busy:return
        self.player.pause();self.note.setText('Finding possible repeated takes…')
        if read_transcript(self.transcript_path()) is not None:
            self.load_cached();self.start_review();return
        self.busy=True;self.begin_button.setEnabled(False);self.choose_button.setEnabled(False);self.mic.setEnabled(False);self.voice_test.setEnabled(False);self.progress.show()
        self.worker=AnalyzeWorker(self.source,self.mic.currentIndex(),self.duration,self.transcript_path())
        self.worker.progress.connect(self.analysis_progress)
        self.worker.ready.connect(self.analysis_ready)
        self.worker.failed.connect(self.analysis_error)
        self.worker.finished.connect(self.analysis_done)
        self.worker.start()
    def analysis_progress(self,text):
        if text.startswith('Transcribed through'):self.note.setText(text.replace('Transcribed through','Checked'))
        else:self.note.setText('Listening to your recording. This can take a few minutes…')
    def analysis_ready(self,_):self.load_cached();self.start_review()
    def analysis_error(self,error):
        (ROOT/'analysis'/'app-error.log').write_text(error,encoding='utf-8')
        if 'PermissionError' in error:
            self.note.setText('Windows blocked access to an app file. This is an app permissions problem, not a microphone problem. The error has been saved.')
        elif 'ModuleNotFoundError' in error or 'ImportError' in error:
            self.note.setText('A speech-recognition component could not load. Your audio track is selected; the app needs repair. The error has been saved.')
        else:self.note.setText('Analysis could not finish. The error has been saved so it can be checked. Your recording has not been changed.')
    def analysis_done(self):
        self.busy=False;self.begin_button.setEnabled(True);self.choose_button.setEnabled(True);self.mic.setEnabled(True);self.voice_test.setEnabled(True);self.progress.hide()
    def start_review(self):
        self.cards=[r for r in self.rows if r['kind']=='Similar takes']
        self.card_index=next((i for i,r in enumerate(self.cards) if r['id'] not in self.decisions),len(self.cards))
        if self.card_index>=len(self.cards):self.finish_review();return
        self.set_page(1);self.show_card()
    def show_card(self):
        if self.card_index>=len(self.cards):self.finish_review();return
        r=self.cards[self.card_index];self.current=r
        self.start.setValue(r['start']);self.end.setValue(r.get('suggested_end',r['end']))
        self.counter.setText(f'Suggestion {self.card_index+1} of {len(self.cards)}')
        phrase=r['text'].split('“',1)[-1].split('”',1)[0]
        self.question.setText('You said “'+phrase+'” more than once. Would removing the earlier take help?')
        self.range_note.setText(f'Try removing {self.end.value()-self.start.value():.1f} seconds. Preview it first; you can keep both takes.')
        self.adjust_toggle.setChecked(False);self.undo_button.setEnabled(bool(self.choice_history))
        self.trial_cut=None;self.rough=False;self.stop_at=min(self.duration,r['end']+.8)
        self.player.setPosition(round(max(0,r['start']-.7)*1000));self.player.pause()
    def watch_original(self):
        if not self.current:return
        self.trial_cut=None;r=self.current;self.play_at(max(0,r['start']-.7),min(self.duration,r['end']+.8))
        self.note.setText('Playing the original with both takes.')
    def watch_cut(self):
        if not self.current or self.end.value()<=self.start.value():return
        r=self.current;self.play_at(max(0,min(r['start'],self.start.value())-.7),min(self.duration,max(r['end'],self.end.value())+.8))
        self.trial_cut=[self.start.value(),self.end.value()]
        self.note.setText('Preview only. Nothing is removed until you choose Remove earlier take.')
    def position_changed(self,ms):
        trial=getattr(self,'trial_cut',None)
        if trial and trial[0]<=ms/1000<trial[1]-.015:
            self.player.setPosition(round(trial[1]*1000));return
        super().position_changed(ms)
    def choose(self,remove):
        if not self.current or self.end.value()<=self.start.value():return
        # Keep the later take outside the removal by default; edited bounds remain explicit.
        self.choice_history.append((self.card_index,json.loads(json.dumps(self.cuts)),dict(self.decisions)))
        self.trial_cut=None;self.edit_range(remove);self.player.pause();self.card_index+=1
        self.note.setText('Choice saved.');self.show_card()
    def undo_choice(self):
        if not self.choice_history:return
        self.card_index,self.cuts,self.decisions=self.choice_history.pop();self.save();self.refresh_stats()
        self.set_page(1);self.show_card();self.note.setText('Last choice undone.')
    def finish_review(self):
        self.set_page(2)
        removed=sum(b-a for a,b in self.cuts)
        if not self.cards:
            self.done_summary.setText('No repeated takes found. Your recording is unchanged.')
        else:self.done_summary.setText(f'{removed:.1f} seconds marked for removal. Everything else stays.')
        self.send_button.setEnabled(removed>0 and bool(complement(self.cuts,0,self.duration)));self.back_button.setEnabled(bool(self.cards))
        self.done_help.setText('Open your project in Resolve, then click below. Your voice and game audio stay on separate tracks.' if removed else 'There are no cuts to send. You can review the suggestions or choose another recording.')
        if removed and not complement(self.cuts,0,self.duration):self.done_help.setText('These choices remove the entire video. Go back and undo a choice before sending.')
    def back_to_review(self):
        if not self.cards:return
        self.card_index=min(self.card_index,len(self.cards)-1);self.set_page(1);self.show_card()
    def send_simple(self):
        if self.busy or not self.source:return
        self.busy=True;self.send_button.setEnabled(False);self.back_button.setEnabled(False);self.another_button.setEnabled(False);self.send_progress.show()
        self.note.setText('Preparing your draft…');self.save()
        self.export_worker=ExportWorker(self.source,self.duration,self.fps,json.loads(json.dumps(self.rows)),dict(self.decisions),json.loads(json.dumps(self.cuts)))
        self.export_worker.progress.connect(lambda _:self.note.setText('Preparing your draft and keeping both audio tracks…'))
        self.export_worker.ready.connect(self.sent)
        self.export_worker.failed.connect(self.send_failed)
        self.export_worker.finished.connect(self.send_done);self.export_worker.start()
    def sent(self,folder,message):
        self.sent_ok=message.startswith('Created ')
        if self.sent_ok:
            self.done_summary.setText('Done — your draft is open in Resolve.')
            self.done_help.setText('Look for the timeline named “Cut Review draft”. Your original edit is untouched.')
            self.note.setText('You can finish your pacing and sound effects in Resolve.')
        else:
            self.note.setText('The draft couldn’t be confirmed. Check Resolve for a new “Cut Review draft” before trying again.')
            self.done_help.setText(message)
    def send_failed(self,error):
        self.sent_ok=False;(ROOT/'analysis'/'app-error.log').write_text(error,encoding='utf-8')
        self.note.setText('The draft couldn’t be sent. Make sure Resolve has a project open. Your choices are saved.')
    def send_done(self):
        self.busy=False;self.send_progress.hide();self.send_button.setEnabled(not getattr(self,'sent_ok',False));self.back_button.setEnabled(True);self.another_button.setEnabled(True)

if __name__=='__main__':
    from PySide6.QtNetwork import QLocalServer, QLocalSocket
    app=QApplication(sys.argv)
    server_name='cut-review-'+hashlib.sha1(str(ROOT).encode()).hexdigest()[:16]
    checking='--launch-check' in sys.argv
    if checking:server_name+='-check-'+str(os.getpid())
    existing=QLocalSocket();existing.connectToServer(server_name)
    if existing.waitForConnected(500):
        existing.write(b'show');existing.flush();existing.waitForBytesWritten(500);existing.disconnectFromServer()
        sys.exit(0)
    server=QLocalServer()
    if not server.listen(server_name):raise RuntimeError('Could not start Cut Review. Another copy may still be opening.')
    configure_app(app);window=SimpleWindow();window.show()
    def show_existing():
        socket=server.nextPendingConnection()
        if socket:socket.disconnectFromServer();socket.deleteLater()
        window.showNormal();window.raise_();window.activateWindow()
    server.newConnection.connect(show_existing)
    def reveal():
        window.hide();window.show();window.raise_();window.activateWindow()
        save_json(ROOT/'analysis'/'launch-status.json',{'visible':window.isVisible(),'window':int(window.winId()),'platform':app.platformName(),'pid':os.getpid()})
    QTimer.singleShot(300,reveal)
    if checking:
        window.audio.setMuted(True)
        def check_ready():
            import PySide6.QtCore
            save_json(ROOT/'analysis'/'packaged-check.json',{'visible':window.isVisible(),'qt_core':PySide6.QtCore.__file__,
                'root':str(ROOT),'speech_rows':len(window.rows),'executable':sys.executable,'frozen':getattr(sys,'frozen',False)})
            window.close();app.quit()
        QTimer.singleShot(1800,check_ready)
    def handle_error(kind,value,tb):
        (ROOT/'analysis'/'app-error.log').write_text(''.join(traceback.format_exception(kind,value,tb)),encoding='utf-8')
        window.note.setText('Something went wrong. Your saved choices are safe; close and reopen the app.')
    sys.excepthook=handle_error
    sys.exit(app.exec())
