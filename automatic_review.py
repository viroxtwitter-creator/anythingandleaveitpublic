"""One-action automatic cut UI. No repeated-take review cards."""
import sys,os,json,traceback,hashlib
from pathlib import Path
from app_paths import ROOT,add_dependencies
add_dependencies()
from PySide6.QtCore import QThread,Signal,QTimer,Qt,QPropertyAnimation,QEasingCurve
from PySide6.QtWidgets import QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QFileDialog,QComboBox,QFrame,QGraphicsOpacityEffect,QSizeGrip
from cut_review import configure_app
from review_core import save_json
from automatic_cut import probe,plan,send,check_resolve,Cancelled
from retention_dial import RetentionDial

class SoftLabel(QLabel):
    """Interruptible fades: frequent worker messages never queue animations."""
    def __init__(self,*args):
        super().__init__(*args)
        effect=QGraphicsOpacityEffect(self);effect.setOpacity(1);self.setGraphicsEffect(effect)
        self.fade=QPropertyAnimation(effect,b'opacity',self)
        self.fade.setDuration(260);self.fade.setEasingCurve(QEasingCurve.OutCubic)
    def setText(self,text):
        if text==self.text():return
        super().setText(text)
        if self.isVisible() and os.environ.get('RETENTION_REDUCED_MOTION')!='1':
            self.fade.stop();self.fade.setStartValue(.4);self.fade.setEndValue(1);self.fade.start()

class SoftButton(QPushButton):
    def __init__(self,*args):
        super().__init__(*args)
        effect=QGraphicsOpacityEffect(self);effect.setOpacity(.92);self.setGraphicsEffect(effect)
        self.hover=QPropertyAnimation(effect,b'opacity',self)
        self.hover.setDuration(180);self.hover.setEasingCurve(QEasingCurve.OutCubic)
    def transition(self,value):
        self.hover.stop()
        if os.environ.get('RETENTION_REDUCED_MOTION')=='1':self.graphicsEffect().setOpacity(value);return
        self.hover.setStartValue(self.graphicsEffect().opacity());self.hover.setEndValue(value);self.hover.start()
    def enterEvent(self,event):self.transition(1);super().enterEvent(event)
    def leaveEvent(self,event):self.transition(.92);super().leaveEvent(event)

class WindowHeader(QWidget):
    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton:
            handle=self.window().windowHandle()
            if handle and handle.startSystemMove():event.accept();return
            self.drag_offset=event.globalPosition().toPoint()-self.window().pos()
        super().mousePressEvent(event)
    def mouseMoveEvent(self,event):
        if event.buttons() & Qt.LeftButton and hasattr(self,'drag_offset'):
            self.window().move(event.globalPosition().toPoint()-self.drag_offset)
        super().mouseMoveEvent(event)
    def mouseReleaseEvent(self,event):
        if hasattr(self,'drag_offset'):del self.drag_offset
        super().mouseReleaseEvent(event)

class Worker(QThread):
    progress=Signal(str);ready=Signal(dict);failed=Signal(str)
    def __init__(self,source,mic):super().__init__();self.source=source;self.mic=mic
    def run(self):
        try:
            check_resolve()
            result=plan(self.source,self.mic,self.progress.emit,self.isInterruptionRequested)
            if self.isInterruptionRequested():raise Cancelled()
            self.ready.emit(send(result,self.progress.emit))
        except Cancelled:self.failed.emit('Stopped before sending the cut to Resolve.')
        except Exception:
            detail=traceback.format_exc();(ROOT/'analysis'/'automatic-error.log').write_text(detail,encoding='utf-8')
            self.failed.emit(detail.splitlines()[-1])

class AutomaticWindow(QMainWindow):
    def __init__(self):
        super().__init__();self.setWindowTitle('clipemo.com');self.resize(480,660);self.setMinimumSize(440,640)
        self.setWindowFlag(Qt.FramelessWindowHint,True)
        self.setAttribute(Qt.WA_TranslucentBackground,True)
        self.setStyleSheet('''
            QMainWindow { background: #11131c; }
            QWidget#canvas { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #1c2033,stop:0.55 #141722,stop:1 #11131c); }
            QWidget { font-family: 'SF Pro Display'; font-size: 13px; color: #f1f2f7; }
            QLabel { background: transparent; border: none; }
            QLabel#title { font-size: 23px; font-weight: 600; letter-spacing: -0.5px; }
            QLabel#muted, QLabel#caption { color: #a6adc3; }
            QLabel#eyebrow { color: #74747c; font-size: 11px; font-weight: 600; letter-spacing: 2px; }
            QLabel#section { font-size: 13px; font-weight: 600; color: #cbd0df; }
            QLabel#mark { background: #2d3551; color: #dce3ff; border: 1px solid #454f72; border-radius: 12px; font-size: 22px; font-weight: 600; }
            QLabel#badge { color: #52615c; background: #e9eeeb; border-radius: 12px; padding: 6px 12px; font-size: 11px; }
            QFrame#card { background: #202434; border: 1px solid #33394e; border-radius: 16px; }
            QPushButton { background: #2a3043; border: 1px solid #41495f; border-radius: 8px; padding: 8px 14px; font-weight: 600; }
            QPushButton:hover { background: #2a3043; }
            QPushButton:pressed { background: #3b435a; }
            QPushButton:focus { border: 2px solid #a8b9ff; }
            QPushButton#primary { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #536dd9,stop:1 #7277d9); color: white; border: 1px solid #8493ed; border-radius: 10px; font-size: 14px; }
            QPushButton#primary:pressed { background: #485abd; }
            QPushButton#primary:focus { border: 2px solid #d0d9ff; }
            QPushButton:disabled, QPushButton#primary:disabled { background: #272c3d; color: #929bb2; border: 1px solid #353c51; }
            QComboBox { background: #191d2b; border: 1px solid #41495f; border-radius: 8px; padding: 8px; }
            QComboBox QAbstractItemView { background: #202434; color: #f1f2f7; selection-background-color: #465584; }
            QProgressBar { border: none; background: #292e40; border-radius: 2px; max-height: 4px; }
            QProgressBar::chunk { background: #8a9aee; border-radius: 2px; }
        ''')
        self.source=None;self.worker=None;self.result=None
        self.setStyleSheet(self.styleSheet()+'''
            QWidget#canvas { background: qradialgradient(cx:0.16,cy:0.06,radius:1.15,fx:0.16,fy:0.06,stop:0 #43405b,stop:0.32 #2b2b42,stop:0.72 #202233,stop:1 #171a28); }
            QLabel#title { font-size: 16px; font-weight: 600; letter-spacing: 0px; }
            QFrame#dock { background: qlineargradient(x1:0,y1:0,x2:0.8,y2:1,stop:0 #3b384f,stop:0.45 #302e44,stop:1 #26283b); border: 1px solid #48445b; border-bottom-color: #292b3c; border-radius: 26px; }
            QPushButton { background: #39364e; border: 1px solid #504b65; border-radius: 16px; padding: 8px 16px; }
            QPushButton:hover { background: #39364e; }
            QPushButton#primary { background: qlineargradient(x1:0,y1:0,x2:0.8,y2:1,stop:0 #a282ff,stop:0.16 #9066fb,stop:0.55 #7a50ee,stop:1 #6040d1); border: 1px solid #a98afa; border-bottom-color: #6950bc; border-radius: 26px; font-size: 16px; }
            QPushButton#primary:pressed { background: #6542d9; }
            QPushButton:focus, QPushButton#primary:focus { border: 1px solid #c8b4ff; }
        ''')
        self.setStyleSheet(self.styleSheet()+'''
            QWidget#canvas { background: qlineargradient(x1:0,y1:0,x2:0.7,y2:1,stop:0 #282d35,stop:0.45 #1c2128,stop:1 #14191f); }
            QWidget { color: #eef1f5; }
            QLabel#title { font-family: 'SF Pro Display'; font-size: 19px; font-weight: 700; }
            QLabel#caption { color: #a8b1bd; }
            QLabel#section { color: #e0e5eb; font-size: 13px; }
            QFrame#dock { background: qlineargradient(x1:0,y1:0,x2:0.7,y2:1,stop:0 #2a3038,stop:1 #20262e); border: 1px solid #3c444f; border-bottom-color: #262e37; border-radius: 23px; }
            QPushButton { color: #dce2e9; background: #343c46; border: none; }
            QPushButton:hover { background: #343c46; }
            QPushButton#primary { color: #192331; background: qlineargradient(x1:0,y1:0,x2:0.3,y2:1,stop:0 #e0e9f5,stop:1 #b7cbe5); border: 1px solid #e4edf9; border-bottom-color: #98acc4; border-radius: 18px; font-size: 15px; }
            QPushButton#primary:pressed { background: #a9bfd9; }
            QPushButton:focus, QPushButton#primary:focus { border: 1px solid #f1f5fc; }
            QPushButton#primary:disabled { color: #aab4c0; background: #333c47; border: 1px solid #48535f; }
        ''')
        self.setStyleSheet(self.styleSheet()+'''
            QMainWindow { background: transparent; }
            QWidget#canvas { border: 1px solid #424a55; border-bottom-color: #252e39; border-radius: 22px; }
            QFrame#dock { background: qlineargradient(x1:0,y1:0,x2:0.6,y2:1,stop:0 #323a44,stop:0.12 #2a323b,stop:1 #20262e); border: 1px solid #46515e; border-right-color: #303a46; border-bottom-color: #171e26; border-radius: 23px; }
            QPushButton#primary { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #f0f5fd,stop:0.09 #dce7f5,stop:0.8 #b7cbe5,stop:1 #a4bad5); border: 1px solid #e5eef9; border-bottom: 2px solid #8198b3; }
            QPushButton#primary:pressed { background: #afc3dc; border: 1px solid #8fa5c0; }
            QPushButton#primary:disabled { background: #333c47; border: 1px solid #48535f; }
            QSizeGrip { background: transparent; }
            QPushButton#secondary { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #414c59,stop:1 #303943); border: 1px solid #4c5867; border-bottom-color: #252e38; }
            QPushButton#secondary:pressed { background: #29323c; border-color: #394452; }
            QPushButton#secondary:disabled { background: #2b333d; color: #8f9caa; border-color: #36414c; }
        ''')
        base=QWidget();base.setObjectName('canvas');self.setCentralWidget(base);layout=QVBoxLayout(base);layout.setContentsMargins(22,24,22,18);layout.setSpacing(10)
        header=WindowHeader();header_layout=QHBoxLayout(header);header_layout.setContentsMargins(0,0,0,0);header_layout.setSpacing(5)
        title=QLabel('clipemo.com');title.setObjectName('title');title.setAttribute(Qt.WA_TransparentForMouseEvents);header_layout.addWidget(title);header_layout.addStretch()
        self.minimize=QPushButton('−');self.minimize.setAccessibleName('Minimize window');self.minimize.setToolTip('Minimize');self.minimize.clicked.connect(self.showMinimized)
        self.close_button=QPushButton('×');self.close_button.setAccessibleName('Close window');self.close_button.setToolTip('Close');self.close_button.clicked.connect(self.close)
        for button in (self.minimize,self.close_button):
            button.setFixedSize(32,30);button.setCursor(Qt.PointingHandCursor)
            button.setStyleSheet('QPushButton { background:transparent; border:none; padding:0; font-size:22px; color:#abb5c1; } QPushButton:hover { background:transparent; color:white; } QPushButton:focus { border:none; color:#b9dcff; } QPushButton:pressed { color:#8296ab; }')
            header_layout.addWidget(button)
        layout.addWidget(header)
        self.dial=RetentionDial();layout.addWidget(self.dial,1)
        dock=QFrame();dock.setObjectName('dock');source_card=QVBoxLayout(dock);source_card.setContentsMargins(24,22,24,20);source_card.setSpacing(12);layout.addWidget(dock)
        row=QHBoxLayout();heading=QLabel('Source recording');heading.setObjectName('caption');row.addWidget(heading);row.addStretch()
        self.choose=SoftButton('Choose file');self.choose.setObjectName('secondary');self.choose.setCursor(Qt.PointingHandCursor);self.choose.clicked.connect(self.pick);row.addWidget(self.choose);source_card.addLayout(row)
        self.file=SoftLabel('Choose a recording to get started.');self.file.setWordWrap(True);self.file.setTextFormat(Qt.PlainText);self.file.setMinimumHeight(42);source_card.addWidget(self.file)
        self.voice_label=QLabel('Commentary track');self.voice_label.setObjectName('caption');source_card.addWidget(self.voice_label)
        self.voice=QComboBox();self.voice.setAccessibleName('Commentary audio track');source_card.addWidget(self.voice)
        self.create=SoftButton('Create automatic cut');self.create.setObjectName('primary');self.create.setMinimumHeight(54);self.create.clicked.connect(self.begin);self.create.setEnabled(False)
        self.create.setCursor(Qt.PointingHandCursor)
        progress_card=QVBoxLayout();progress_card.setContentsMargins(0,0,0,0);progress_card.setSpacing(3);source_card.addLayout(progress_card)
        self.stage=SoftLabel('Ready when you are');self.stage.setObjectName('section');progress_card.addWidget(self.stage)
        self.status=SoftLabel('Open a project in Resolve to begin.');self.status.setObjectName('caption');self.status.setTextFormat(Qt.PlainText);self.status.setWordWrap(True);self.status.setMinimumHeight(44);progress_card.addWidget(self.status)
        source_card.addWidget(self.create)
        footer=QHBoxLayout();footer.addSpacing(16)
        self.details=QLabel('DaVinci Resolve');self.details.setAlignment(Qt.AlignCenter);self.details.setStyleSheet('color: #9ca7b4; font-size: 11px;');footer.addWidget(self.details,1)
        grip=QSizeGrip(self);grip.setFixedSize(16,16);footer.addWidget(grip);layout.addLayout(footer)
        self.voice.hide();self.voice_label.hide()
        try:
            last=Path(json.loads((ROOT/'analysis/simple-preferences.json').read_text())['source'])
            if last.is_file():self.load(last)
        except (OSError,ValueError,KeyError):pass
        if '--source' in sys.argv:self.load(Path(sys.argv[sys.argv.index('--source')+1]))
    def pick(self):
        f,_=QFileDialog.getOpenFileName(self,'Choose your full recording',str(self.source.parent if self.source else ROOT),'Video recordings (*.mp4 *.mov *.mkv *.m4v)')
        if f:self.load(Path(f))
    def load(self,path):
        try:
            duration,fps,names=probe(path)
            self.source=path;self.voice.clear();self.voice.addItems(names)
            mic=next((i for i,n in enumerate(names) if 'microphone' in n.lower() or 'mic'==n.lower()),None)
            if mic is not None:self.voice.setCurrentIndex(mic)
            ambiguous=mic is None and len(names)>1
            self.voice.setVisible(ambiguous);self.voice_label.setVisible(ambiguous)
            voice=names[self.voice.currentIndex()]
            self.dial.set_duration(duration)
            self.file.setText(f'{path.name}\n{voice}')
            self.stage.setText('Ready');self.choose.setText('Change');self.create.setEnabled(True);self.status.setText('Open a Resolve project before starting.')
            save_json(ROOT/'analysis/simple-preferences.json',dict(source=str(path)))
        except Exception as e:self.status.setText('Could not open that recording: '+str(e));self.create.setEnabled(False)
    def begin(self):
        if self.worker and self.worker.isRunning():return
        self.result=None;self.choose.setEnabled(False);self.voice.setEnabled(False);self.create.setEnabled(False)
        self.dial.set_busy(True)
        self.create.setText('Creating your cut…');self.stage.setText('Creating your edit');self.status.setText('Checking Resolve…')
        self.worker=Worker(self.source,self.voice.currentIndex());self.worker.progress.connect(self.status.setText)
        self.worker.ready.connect(self.done);self.worker.failed.connect(self.failed);self.worker.finished.connect(self.finished);self.worker.start()
    def done(self,result):
        self.stage.setText('Your cut is ready')
        self.result=result;d=round(result['edited_duration']);o=round(result['duration'])
        self.dial.set_busy(False);self.dial.set_duration(d,'Finished cut')
        review=result.get('script_review',{})
        self.status.setText(f'{o//60}:{o%60:02} → {d//60}:{d%60:02}  ·  {result["clips"]} clips\nOpen in Resolve. {len(review.get("flags",[]))} joins flagged for review.')
        if result.get('comparison',{}).get('identical_frame_ranges'):
            self.status.setText(self.status.text()+'\nFresh analysis produced the same cut decisions.')
    def failed(self,message):self.stage.setText('Needs your attention');self.status.setText(message)
    def finished(self):
        self.dial.set_busy(False)
        self.choose.setEnabled(True);self.voice.setEnabled(True);self.create.setText('Create automatic cut');self.create.setEnabled(True)
        if '--auto-check' in sys.argv:
            save_json(ROOT/'analysis/automatic-ui-check.json',dict(success=bool(self.result),result=self.result,status=self.status.text(),button=self.create.text()))
            def finish_check():
                self.grab().save(str(ROOT/'analysis/automatic-ui-check.png'));QApplication.instance().quit()
            QTimer.singleShot(500,finish_check)
    def closeEvent(self,event):
        if self.worker and self.worker.isRunning():
            event.ignore();self.status.setText('The cut is still being created. Keep this window open until it finishes.');return
        super().closeEvent(event)

def main():
    from PySide6.QtNetwork import QLocalServer,QLocalSocket
    app=QApplication(sys.argv);configure_app(app)
    checking='--launch-check' in sys.argv or '--auto-check' in sys.argv
    name='retention-cut-'+hashlib.sha1(str(ROOT).encode()).hexdigest()[:12]
    if checking:name+='-'+str(os.getpid())
    socket=QLocalSocket();socket.connectToServer(name)
    if socket.waitForConnected(400):socket.write(b'show');socket.flush();socket.waitForBytesWritten(400);return 0
    server=QLocalServer();server.listen(name);window=AutomaticWindow();window.show()
    def reveal():
        client=server.nextPendingConnection()
        if client:client.disconnectFromServer();client.deleteLater()
        window.showNormal();window.raise_();window.activateWindow()
    server.newConnection.connect(reveal)
    if '--launch-check' in sys.argv:
        def check():
            save_json(ROOT/'analysis/automatic-launch-check.json',dict(visible=window.isVisible(),title=window.windowTitle(),button=window.create.text(),old_review_buttons=False,executable=sys.executable))
            window.grab().save(str(ROOT/'analysis/automatic-launch-check.png'));app.quit()
        QTimer.singleShot(1200,check)
    if '--auto-check' in sys.argv:QTimer.singleShot(500,window.create.click)
    return app.exec()

if __name__=='__main__':sys.exit(main())
