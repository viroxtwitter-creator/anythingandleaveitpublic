"""Source-duration dial. Motion indicates activity, never a fabricated percentage."""
import math
from PySide6.QtCore import Qt,QTimer,QElapsedTimer,QRectF
from PySide6.QtGui import QPainter,QPen,QColor,QFont,QRadialGradient,QLinearGradient,QConicalGradient,QBrush,QFontDatabase
from PySide6.QtWidgets import QWidget
import os

class RetentionDial(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setMinimumHeight(238);self.value='—';self.caption='Recording length';self.busy=False
        self.clock=QElapsedTimer();self.clock.start()
        self.timer=QTimer(self);self.timer.setTimerType(Qt.PreciseTimer);self.timer.setInterval(8);self.timer.timeout.connect(self.update)
        self.number_family='SF Pro Display' if 'SF Pro Display' in QFontDatabase.families() else 'Segoe UI'
        self.setAccessibleName('Recording duration')
    def set_duration(self,seconds,caption='Recording length'):
        seconds=round(seconds);self.value=f'{seconds//60}:{seconds%60:02}';self.caption=caption;self.update()
    def set_busy(self,busy):
        self.busy=busy
        if busy and self.isVisible() and os.environ.get('RETENTION_REDUCED_MOTION')!='1':self.timer.start()
        else:self.timer.stop()
        self.update()
    def hideEvent(self,event):self.timer.stop();super().hideEvent(event)
    def showEvent(self,event):self.set_busy(self.busy);super().showEvent(event)
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing)
        cx,cy=self.width()/2,self.height()/2;radius=min(self.height()/2-15,114)
        # Broad indirect light, painted without blur effects or image assets.
        glow=QRadialGradient(cx,cy,min(cx,cy)-1)
        glow.setColorAt(0,QColor(143,163,188,36));glow.setColorAt(.6,QColor(92,110,140,12));glow.setColorAt(1,QColor(95,110,140,0))
        p.setPen(Qt.NoPen);p.setBrush(glow);p.drawRect(self.rect())
        for i in range(0,60,5):
            angle=math.radians(i*6-90);outer=radius;inner=radius-(7 if i%5==0 else 3)
            p.setPen(QPen(QColor('#535a64'),1))
            from PySide6.QtCore import QPointF
            p.drawLine(QPointF(cx+inner*math.cos(angle),cy+inner*math.sin(angle)),QPointF(cx+outer*math.cos(angle),cy+outer*math.sin(angle)))
        r=radius-16;rect=QRectF(cx-r,cy-r,2*r,2*r)
        # A shaded lens with a directional edge highlight, not a flat ring.
        lens=QLinearGradient(cx-r,cy-r,cx+r,cy+r)
        lens.setColorAt(0,QColor('#2d323a'));lens.setColorAt(.45,QColor('#22272e'));lens.setColorAt(1,QColor('#1a1e25'))
        rim=QConicalGradient(cx,cy,125)
        for at,color in ((0,'#858e9a'),(.18,'#444d58'),(.45,'#272e37'),(.7,'#58616e'),(1,'#858e9a')):rim.setColorAt(at,QColor(color))
        p.setBrush(lens);p.setPen(QPen(QBrush(rim),1.3));p.drawEllipse(rect)
        inner=rect.adjusted(5,5,-5,-5)
        p.setBrush(Qt.NoBrush);p.setPen(QPen(QColor(180,195,210,12),1));p.drawEllipse(inner)
        if self.busy:
            phase=(self.clock.nsecsElapsed()/1e9/3.2)%1 if self.timer.isActive() else 0
            for width,alpha in ((12,12),(7,28),(3,255)):
                p.setPen(QPen(QColor(183,210,240,alpha),width,Qt.SolidLine,Qt.RoundCap));p.drawArc(rect,int((90-phase*360)*16),70*16)
        number=QFont(self.number_family);number.setPixelSize(54);number.setWeight(QFont.Bold);number.setLetterSpacing(QFont.AbsoluteSpacing,-1.6)
        p.setPen(QColor('#f6f7f9'));p.setFont(number)
        p.drawText(QRectF(0,cy-39,self.width(),68),Qt.AlignCenter,self.value)
        font=QFont(self.number_family);font.setPixelSize(12);p.setFont(font);p.setPen(QColor('#a6afb9'))
        p.drawText(QRectF(0,cy+32,self.width(),24),Qt.AlignCenter,self.caption)
