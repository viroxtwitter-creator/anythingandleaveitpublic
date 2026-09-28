import os
import sys
from pathlib import Path
from app_paths import ROOT, add_dependencies
add_dependencies()
os.environ.setdefault('HF_HOME',str(ROOT/'.model-cache'))
os.environ.setdefault('HF_HUB_DISABLE_SYMLINKS_WARNING','1')
import json, hashlib, traceback, time
import av
from PySide6.QtCore import Qt, QUrl, QThread, Signal, QTimer
from PySide6.QtGui import QColor, QShortcut, QKeySequence, QFontDatabase, QFont, QPixmap
from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,
    QLabel,QPushButton,QComboBox,QLineEdit,QListWidget,QListWidgetItem,QSplitter,
    QDoubleSpinBox,QSlider,QMessageBox,QFileDialog,QFrame,QCheckBox,QSizePolicy)
from PySide6.QtMultimedia import QMediaPlayer,QAudioOutput,QVideoSink
from review_core import *

DEFAULT_SOURCE=Path("T:/Tom Clancy's Rainbow Six Siege/Tom Clancy's Rainbow Six Siege 2026.08.21 - 22.30.24.03.mp4")
EDIT=Path('C:/Users/jordan/Desktop/F VIDEOS/arctic unlock frost.mov')
STYLE='''
QWidget { background: #11161e; color: #e5eaf2; font-family: "Segoe UI"; font-size: 13px; }
QLabel#title {font-size:26px; font-weight:700; color:#ffffff;}
QLabel#muted {color:#9eabbc;}
QPushButton {background:#263343; border:1px solid #3b4b60; border-radius:6px; padding:9px 13px;}
QPushButton:hover {background:#35465c;}
QPushButton:disabled {color:#697687; background:#1b2430;}
QPushButton#primary {background:#396de6; border-color:#5283ef; color:white; font-weight:600;}
QPushButton#cut {background:#57343d; border-color:#87515b;}
QLineEdit,QComboBox,QDoubleSpinBox {background:#1c2633; border:1px solid #3b4b60; padding:7px; border-radius:5px;}
QListWidget {background:#151e29; border:1px solid #2f3f52; border-radius:7px; outline:none;}
QListWidget::item {padding:11px; border-bottom:1px solid #263343;}
QListWidget::item:selected {background:#284365; color:white;}
QSlider::groove:horizontal {height:5px; background:#364659; border-radius:2px;}
QSlider::handle:horizontal {background:#73a0ff; width:13px; margin:-5px 0; border-radius:6px;}
QSplitter::handle {background:#11161e; width:14px;}
'''

def configure_app(app):
    for name in ['segoeui.ttf','segoeuib.ttf']:
        path=Path('C:/Windows/Fonts')/name
        if path.exists():QFontDatabase.addApplicationFont(str(path))
    app.setFont(QFont('Segoe UI',10))
    app.setStyleSheet(STYLE)

class VideoPreview(QLabel):
    def __init__(self):
        super().__init__('Select a passage to preview its video.')
        self.setAlignment(Qt.AlignCenter);self.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Ignored)
        self.sink=QVideoSink(self);self.sink.videoFrameChanged.connect(self.frame)
        self.picture=None
    def videoSink(self):return self.sink
    def frame(self,frame):
        if frame.isValid():
            self.picture=QPixmap.fromImage(frame.toImage());self.draw_picture()
    def draw_picture(self):
        if self.picture and not self.picture.isNull():self.setPixmap(self.picture.scaled(self.size(),Qt.KeepAspectRatio,Qt.FastTransformation))
    def resizeEvent(self,event):super().resizeEvent(event);self.draw_picture()

class ExportWorker(QThread):
    progress=Signal(str)
    ready=Signal(str,str)
    failed=Signal(str)
    def __init__(self,source,duration,fps,rows,decisions,cuts):
        super().__init__();self.args=(source,duration,fps,rows,decisions,cuts)
    def run(self):
        try:
            from review_media import audio_sidecars
            import subprocess
            source,duration,fps,rows,decisions,cuts=self.args
            audio=audio_sidecars(source,self.progress.emit)
            folder=ROOT/'exports'/time.strftime('%Y%m%d-%H%M%S')
            export_review(folder,source,duration,fps,rows,decisions,cuts,audio)
            script=folder/'create_resolve_draft.lua'
            command='dofile('+json.dumps(script.as_posix())+')'
            (folder/'READ ME.txt').write_text('This draft contains only manually approved cuts.\nVideo uses the original recording. Audio sidecars copy the source AAC packets without re-encoding.\nKeep the audio-for-resolve folder: Resolve links to those files.\n\nIf automatic import is unavailable, open Resolve > Workspace > Console, select Lua and run:\n'+command+'\n',encoding='utf-8')
            exe=Path('C:/Program Files/Blackmagic Design/DaVinci Resolve/fuscript.exe')
            if not exe.exists():self.ready.emit(str(folder),'Export saved. Automatic Resolve connection is unavailable; use READ ME.txt.');return
            self.progress.emit('Creating a separate draft timeline in Resolve…')
            try:
                result=subprocess.run([str(exe),'-l','lua',str(script)],capture_output=True,text=True,timeout=60,
                                      creationflags=subprocess.CREATE_NO_WINDOW)
            except subprocess.TimeoutExpired:
                self.ready.emit(str(folder),'Resolve did not respond in time. Check for a new draft before retrying.');return
            output=result.stdout+'\n'+result.stderr
            (folder/'resolve-output.txt').write_text(output,encoding='utf-8')
            if 'CUT_REVIEW_OK ' in output:
                name=output.split('CUT_REVIEW_OK ',1)[1].splitlines()[0]
                self.ready.emit(str(folder),'Created '+name+' with separate, linked audio tracks.')
            else:self.ready.emit(str(folder),'Export saved, but Resolve import did not finish. See resolve-output.txt; any partial draft is separate from your original timeline.')
        except Exception:self.failed.emit(traceback.format_exc())

class AnalyzeWorker(QThread):
    progress=Signal(str)
    ready=Signal(list)
    failed=Signal(str)
    def __init__(self,source,index,duration,cache):
        super().__init__(); self.source=source;self.index=index;self.duration=duration;self.cache=cache
    def run(self):
        try:
            from analyze_speech import extract
            self.progress.emit('Reading microphone audio locally…')
            wav=self.cache.with_suffix('.wav')
            extract(self.source,self.index,0,self.duration,wav)
            if self.isInterruptionRequested(): return
            from faster_whisper import WhisperModel
            self.progress.emit('Transcribing locally. You can continue playing the recording.')
            model_dir=next((p.parent for p in (ROOT/'.model-cache').rglob('model.bin')
                            if (p.parent/'config.json').is_file() and (p.parent/'tokenizer.json').is_file()),None)
            if model_dir is None:
                raise RuntimeError('The local speech model is missing. Restore the app model-cache folder.')
            model=WhisperModel(str(model_dir),device='cpu',compute_type='int8',cpu_threads=4)
            segments,_=model.transcribe(str(wav),language='en',vad_filter=True,
                  word_timestamps=True,beam_size=3,condition_on_previous_text=False)
            result=[]
            for s in segments:
                if self.isInterruptionRequested():return
                result.append(dict(start=s.start,end=s.end,text=s.text,
                    words=[dict(start=w.start,end=w.end,text=w.word,probability=w.probability) for w in s.words]))
                self.progress.emit(f'Transcribed through {stamp(s.end)} / {stamp(self.duration)}')
            save_json(self.cache,result);self.ready.emit(result)
        except Exception:
            self.failed.emit(traceback.format_exc())

class Window(QMainWindow):
    def __init__(self):
        super().__init__();self.setWindowTitle('Cut Review — local prototype');self.resize(1380,920)
        self.rows=[];self.filtered=[];self.cuts=[];self.decisions={};self.history=[]
        self.source=None;self.duration=0;self.fps=60;self.current=None;self.stop_at=None
        self.rough=False;self.edit_mode=False;self.worker=None;self.export_worker=None;self.ref=[]
        base=QWidget();self.setCentralWidget(base);layout=QVBoxLayout(base);layout.setContentsMargins(24,18,24,18);layout.setSpacing(12)
        header=QHBoxLayout();title=QLabel('Cut Review');title.setObjectName('title');header.addWidget(title)
        sub=QLabel('Local prototype · review every cut');sub.setObjectName('muted');header.addWidget(sub);header.addStretch()
        self.open_btn=self.button('Open recording',self.open_source);header.addWidget(self.open_btn)
        self.export_btn=self.button('Send draft to Resolve',self.export);self.export_btn.setObjectName('primary');header.addWidget(self.export_btn);layout.addLayout(header)
        self.summary=QLabel();self.summary.setObjectName('muted');layout.addWidget(self.summary)
        split=QSplitter();layout.addWidget(split,1)
        left=QWidget();ll=QVBoxLayout(left);ll.setContentsMargins(0,0,8,0);split.addWidget(left)
        self.video=VideoPreview();self.video.setMinimumSize(520,280);ll.addWidget(self.video,1)
        self.player=QMediaPlayer();self.audio=QAudioOutput();self.audio.setVolume(.65)
        self.player.setAudioOutput(self.audio);self.player.setVideoSink(self.video.videoSink())
        self.player.positionChanged.connect(self.position_changed)
        self.player.tracksChanged.connect(self.tracks_changed)
        self.player.errorOccurred.connect(lambda *_:self.status.setText('Playback error: '+self.player.errorString()))
        self.player.mediaStatusChanged.connect(self.media_status)
        self.pending_seek=None
        self.slider=QSlider(Qt.Horizontal);self.slider.sliderMoved.connect(self.seek_slider);ll.addWidget(self.slider)
        transport=QHBoxLayout();transport.addWidget(self.button('Play / Pause',self.toggle_play));transport.addWidget(self.button('−5s',lambda:self.jump(-5)));transport.addWidget(self.button('+5s',lambda:self.jump(5)))
        self.clock=QLabel('00:00.00');transport.addWidget(self.clock);transport.addStretch()
        self.listen=QComboBox();self.listen.setMinimumWidth(135);self.listen.currentIndexChanged.connect(self.change_audio);transport.addWidget(QLabel('Listen'));transport.addWidget(self.listen)
        self.speed=QComboBox();self.speed.addItems(['1×','1.25×','1.5×','2×']);self.speed.currentIndexChanged.connect(lambda i:self.player.setPlaybackRate([1,1.25,1.5,2][i]));transport.addWidget(self.speed);ll.addLayout(transport)
        box=QFrame();bl=QVBoxLayout(box);box.setStyleSheet('QFrame {background:#18222f; border-radius:8px;}')
        self.explanation=QLabel('Choose a passage on the right to preview it.');self.explanation.setWordWrap(True);bl.addWidget(self.explanation)
        times=QHBoxLayout();self.start=QDoubleSpinBox();self.end=QDoubleSpinBox()
        for widget in [self.start,self.end]:widget.setDecimals(3);widget.setSingleStep(1/60);widget.setSuffix(' s');widget.setMaximum(999999)
        times.addWidget(QLabel('Cut range'));times.addWidget(self.start);times.addWidget(QLabel('to'));times.addWidget(self.end)
        times.addWidget(self.button('Start here',lambda:self.start.setValue(self.player.position()/1000)))
        times.addWidget(self.button('End here',lambda:self.end.setValue(self.player.position()/1000)));bl.addLayout(times)
        buttons=QHBoxLayout();buttons.addWidget(self.button('Preview range',self.preview_range))
        buttons.addWidget(self.button('Keep / restore range',self.keep));cut=self.button('Cut this range',self.cut);cut.setObjectName('cut');buttons.addWidget(cut)
        buttons.addWidget(self.button('Undo',self.undo));bl.addLayout(buttons);ll.addWidget(box)
        lower=QHBoxLayout();lower.addWidget(self.button('Preview rough cut',self.preview_rough));lower.addWidget(self.button('Original recording',self.original));lower.addStretch()
        self.cut_stats=QLabel();lower.addWidget(self.cut_stats);ll.addLayout(lower)
        right=QWidget();rl=QVBoxLayout(right);rl.setContentsMargins(8,0,0,0);split.addWidget(right)
        searchbar=QHBoxLayout();self.filter=QComboBox();self.filter.addItems(['Similar takes','Speech','Quiet mic','Your edit · reference','All passages']);self.filter.currentIndexChanged.connect(self.refresh)
        searchbar.addWidget(self.filter);self.search=QLineEdit();self.search.setPlaceholderText('Search this list…');self.search.textChanged.connect(self.refresh);searchbar.addWidget(self.search);rl.addLayout(searchbar)
        self.list=QListWidget();self.list.setWordWrap(True);self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff);self.list.setResizeMode(QListWidget.Adjust);self.list.currentRowChanged.connect(self.select_row);rl.addWidget(self.list,1)
        self.reference_btn=self.button('Play this moment in your finished edit',self.play_edit);self.reference_btn.setEnabled(False);rl.addWidget(self.reference_btn)
        analyse=QHBoxLayout();analyse.addWidget(QLabel('Transcribe'));self.mic=QComboBox();self.mic.currentIndexChanged.connect(self.mic_changed);analyse.addWidget(self.mic,1)
        self.analyze_btn=self.button('Analyse microphone',self.analyze);analyse.addWidget(self.analyze_btn);rl.addLayout(analyse)
        info=QLabel('Quiet mic = no transcribed words, not proof of dead footage. Similar takes can be deliberate. Adjust the range before cutting.');info.setWordWrap(True);info.setObjectName('muted');rl.addWidget(info)
        split.setSizes([850,500]);self.status=QLabel('Ready');self.status.setWordWrap(True);self.status.setObjectName('muted');layout.addWidget(self.status)
        QShortcut(QKeySequence('Ctrl+Z'),self,activated=self.undo)
        if DEFAULT_SOURCE.exists():self.load_source(DEFAULT_SOURCE)
    def button(self,text,fn):
        b=QPushButton(text);b.clicked.connect(fn);return b
    def source_key(self):
        s=self.source.stat();return hashlib.sha1(f'{self.source.resolve()}:{s.st_size}:{s.st_mtime_ns}'.encode()).hexdigest()[:14]
    def transcript_path(self):
        return ROOT/'analysis'/f'transcript-{self.source_key()}-{self.mic.currentIndex()}.json'
    def state_path(self):return ROOT/'analysis'/f'decisions-{self.source_key()}.json'
    def open_source(self):
        p,_=QFileDialog.getOpenFileName(self,'Open gameplay recording',str(self.source.parent if self.source else ROOT),'Video (*.mp4 *.mov *.mkv *.avi);;All files (*)')
        if p:
            try:self.load_source(Path(p))
            except Exception as e:QMessageBox.warning(self,'Could not open recording',str(e))
    def load_source(self,path):
        c=av.open(str(path))
        if not c.streams.video or not c.duration:c.close();raise ValueError('This file needs a video stream and a readable duration.')
        duration=c.duration/1e6;rate=float(c.streams.video[0].base_rate or c.streams.video[0].average_rate or 60)
        streams=[s.metadata.get('name',f'Audio {i+1}') for i,s in enumerate(c.streams.audio)];c.close()
        if self.source:self.save()
        self.player.stop();self.source=path;self.duration=duration;self.fps=round(rate,3);self.current=None;self.rows=[];self.history=[];self.cuts=[];self.decisions={};self.ref=[]
        self.mic.blockSignals(True);self.mic.clear();self.mic.addItems(streams)
        micindex=next((i for i,n in enumerate(streams) if 'mic' in n.lower()),0);self.mic.setCurrentIndex(micindex);self.mic.blockSignals(False)
        self.stream_names=streams;self.edit_mode=False;self.rough=False;self.player.setSource(QUrl.fromLocalFile(str(path.resolve())))
        self.slider.setRange(0,round(duration*1000));self.start.setMaximum(duration);self.end.setMaximum(duration)
        if self.state_path().exists():
            try:
                state=json.loads(self.state_path().read_text());self.cuts=merge_intervals(state['cuts'],0,duration);self.decisions=state.get('decisions',{})
            except (ValueError,KeyError):self.status.setText('Saved decisions could not be read; starting a fresh review.')
        if path.resolve()==DEFAULT_SOURCE.resolve():
            self.ref=reference_rows()
            demo=ROOT/'analysis'/'full-transcript.json'
            if demo.exists() and not self.transcript_path().exists():
                cached=read_transcript(demo)
                if cached is not None:save_json(self.transcript_path(),cached)
        self.load_cached();self.refresh_stats()
    def mic_changed(self):
        if self.source:self.load_cached()
    def load_cached(self):
        p=self.transcript_path()
        transcript=read_transcript(p)
        self.rows=build_rows(transcript,self.duration) if transcript is not None else []
        self.refresh();self.refresh_stats()
        self.status.setText('Local transcript ready. Select a passage to play; every range stays until you mark it Cut.' if self.rows else 'Select the microphone track, then Analyse microphone. No recording is uploaded.')
    def tracks_changed(self):
        self.listen.blockSignals(True);self.listen.clear()
        count=len(self.player.audioTracks())
        self.listen.addItems(['Finished mix'] if self.edit_mode and count else self.stream_names[:count])
        self.listen.setCurrentIndex(min(self.mic.currentIndex(),count-1) if not self.edit_mode else 0);self.listen.blockSignals(False)
        self.change_audio(self.listen.currentIndex())
    def change_audio(self,index):
        if index>=0:self.player.setActiveAudioTrack(index)
    def media_status(self,status):
        if status in (QMediaPlayer.LoadedMedia,QMediaPlayer.BufferedMedia) and self.pending_seek is not None:
            pos=self.pending_seek;self.pending_seek=None;self.player.setPosition(round(pos*1000));self.player.play()
    def play_at(self,start,end=None,edit=False):
        self.rough=False;self.stop_at=end
        target=EDIT if edit else self.source
        changed=self.edit_mode!=edit
        self.edit_mode=edit
        self.slider.setMaximum(round((176.2 if edit else self.duration)*1000))
        if changed:
            self.pending_seek=start;self.player.setSource(QUrl.fromLocalFile(str(target.resolve())))
        else:
            self.player.setPosition(round(start*1000));self.player.play()
    def refresh(self):
        if not hasattr(self,'list'):return
        mode=self.filter.currentText();query=self.search.text().lower().strip()
        pool=self.ref if mode=='Your edit · reference' else self.rows
        self.filtered=[r for r in pool if (mode in ['All passages','Your edit · reference'] or r['kind']==mode) and query in r['text'].lower()]
        self.list.blockSignals(True);self.list.clear()
        for r in self.filtered:
            item=QListWidgetItem(self.row_text(r))
            self.list.addItem(item)
        self.list.blockSignals(False);self.current=None;self.reference_btn.setEnabled(False)
    def row_text(self,r):
        mark=self.decisions.get(r['id'],'')
        return f"{stamp(r['start'])} – {stamp(r['end'])}  ·  {r['kind']}"+(f'  ·  {mark}' if mark else '')+'\n'+r['text']
    def update_marks(self):
        for i,r in enumerate(self.filtered):self.list.item(i).setText(self.row_text(r))
    def select_row(self,index):
        if not 0<=index<len(self.filtered):return
        self.current=r=self.filtered[index];self.start.setValue(r['start']);self.end.setValue(r.get('suggested_end',r['end']))
        self.explanation.setText(r['text']+(' The cut range initially covers the earlier wording; the preview includes both.' if r['kind']=='Similar takes' else ''))
        self.reference_btn.setEnabled('edit_start' in r);self.play_at(max(0,r['start']-.6),min(self.duration,r['end']+.8))
    def play_edit(self):
        if self.current and 'edit_start' in self.current:
            r=self.current;self.play_at(r['edit_start'],r['edit_start']+r['end']-r['start'],True)
    def position_changed(self,ms):
        t=ms/1000
        if self.rough and not self.edit_mode:
            for a,b in self.cuts:
                if a<=t<b-.015:
                    if b>=self.duration-.02:self.player.pause();self.rough=False;return
                    self.player.setPosition(round(b*1000));return
        if self.stop_at is not None and t>=self.stop_at:
            self.player.pause();self.stop_at=None
        self.clock.setText(('Finished edit  ' if self.edit_mode else 'Source  ')+stamp(t))
        if not self.slider.isSliderDown():self.slider.setValue(ms)
    def toggle_play(self):
        self.stop_at=None
        if self.player.playbackState()==QMediaPlayer.PlayingState:self.player.pause()
        else:self.player.play()
    def jump(self,delta):
        self.stop_at=None;self.player.setPosition(max(0,self.player.position()+int(delta*1000)))
    def seek_slider(self,value):self.stop_at=None;self.player.setPosition(value)
    def preview_range(self):
        if self.end.value()>self.start.value():self.play_at(max(0,self.start.value()-.6),min(self.duration,self.end.value()+.6))
    def edit_range(self,cut):
        if self.edit_mode:
            self.status.setText('Return to the original recording before marking a source cut.');return
        a,b=self.start.value(),self.end.value()
        if b<=a:
            self.status.setText('The end must be later than the start.');return
        self.history.append((json.loads(json.dumps(self.cuts)),dict(self.decisions)))
        if cut:self.cuts=merge_intervals(self.cuts+[[a,b]],0,self.duration)
        else:
            self.cuts=merge_intervals([piece for x,y in self.cuts for piece in complement([[a,b]],x,y)],0,self.duration)
        if self.current:self.decisions[self.current['id']]='Cut range marked' if cut else 'Kept'
        self.save();self.refresh_stats();self.update_marks();self.status.setText(f"{'Marked for removal' if cut else 'Restored'}: {stamp(a)}–{stamp(b)}. Saved locally. Undo is available.")
    def cut(self):self.edit_range(True)
    def keep(self):self.edit_range(False)
    def undo(self):
        if self.history:self.cuts,self.decisions=self.history.pop();self.save();self.refresh_stats();self.update_marks();self.status.setText('Last decision undone.')
    def preview_rough(self):
        self.play_at(0);self.rough=True;self.stop_at=None
        self.status.setText('Rough preview skips your marked cuts. Seek across the recording to check joins; this is not a frame-accurate render.')
    def original(self):self.play_at(self.start.value());self.status.setText('Playing original footage with no skips.')
    def refresh_stats(self):
        if not self.source:return
        n=sum(r['kind']=='Similar takes' for r in self.rows);s=sum(r['kind']=='Speech' for r in self.rows)
        self.summary.setText(f'{self.source.name}  ·  {stamp(self.duration)}  ·  {s} speech passages  ·  {n} possible repeated takes')
        removed=sum(b-a for a,b in self.cuts);self.cut_stats.setText(f'{removed:.1f}s marked for removal  ·  {stamp(self.duration-removed)} remaining')
    def save(self):
        if self.source:save_json(self.state_path(),dict(cuts=self.cuts,decisions=self.decisions))
    def analyze(self):
        if not self.source or self.mic.currentIndex()<0:return
        if self.worker and self.worker.isRunning():return
        self.analyze_btn.setEnabled(False);self.open_btn.setEnabled(False);self.mic.setEnabled(False);self.export_btn.setEnabled(False)
        self.worker=AnalyzeWorker(self.source,self.mic.currentIndex(),self.duration,self.transcript_path())
        self.worker.progress.connect(self.status.setText);self.worker.ready.connect(lambda _:self.load_cached())
        self.worker.failed.connect(lambda e:QMessageBox.warning(self,'Analysis failed',e))
        self.worker.finished.connect(self.analysis_finished);self.worker.start()
    def analysis_finished(self):
        self.analyze_btn.setEnabled(True);self.open_btn.setEnabled(True);self.mic.setEnabled(True);self.export_btn.setEnabled(True)
    def export(self):
        if not self.source:return
        if self.export_worker and self.export_worker.isRunning():return
        if not complement(self.cuts,0,self.duration):
            self.status.setText('Restore at least one section before exporting.');return
        self.player.pause();self.save();self.export_btn.setEnabled(False);self.open_btn.setEnabled(False);self.analyze_btn.setEnabled(False);self.mic.setEnabled(False)
        self.export_worker=ExportWorker(self.source,self.duration,self.fps,json.loads(json.dumps(self.rows)),dict(self.decisions),json.loads(json.dumps(self.cuts)))
        self.export_worker.progress.connect(self.status.setText)
        self.export_worker.ready.connect(lambda folder,message:self.status.setText(message+'  Export saved in '+folder))
        self.export_worker.failed.connect(lambda error:QMessageBox.warning(self,'Export could not finish',error))
        self.export_worker.finished.connect(lambda:(self.export_btn.setEnabled(True),self.open_btn.setEnabled(True),self.analyze_btn.setEnabled(True),self.mic.setEnabled(True)))
        self.export_worker.start()
    def closeEvent(self,event):
        if self.export_worker and self.export_worker.isRunning():
            self.status.setText('Finishing the draft export. Close again once it completes.');event.ignore();return
        if self.worker and self.worker.isRunning():
            self.worker.requestInterruption();self.status.setText('Stopping analysis; close again once it finishes.');event.ignore();return
        self.save();self.player.stop();event.accept()

if __name__=='__main__':
    app=QApplication(sys.argv);configure_app(app);window=Window();window.show()
    QTimer.singleShot(300,lambda:(window.hide(),window.show(),window.raise_(),window.activateWindow()))
    def handle_error(kind,value,tb):
        error=''.join(traceback.format_exception(kind,value,tb))
        (ROOT/'analysis'/'app-error.log').write_text(error,encoding='utf-8')
        QMessageBox.critical(window,'Cut Review encountered a problem',str(value)+'\nDetails are saved in analysis/app-error.log.')
    sys.excepthook=handle_error
    sys.exit(app.exec())
