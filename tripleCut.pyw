#! /usr/bin/python

""" TRIPLECUT v1.1.0 DATE: 24.11.2016 """
import platform
import sys
import os.path
import comskipper
print(platform.architecture())
import vlc
import glob
import datetime
import fileUtils
from PySide2 import QtGui, QtCore, QtWidgets 

class Player(QtWidgets.QMainWindow):
    """A simple Media Player using VLC and Qt"""
    def __init__(self, master=None):        
        super(Player, self).__init__()
        self.keyHelp = "Space: Play/Pause\nA: Refine Cut to the Left\nD: Refine Cut to the Right\nS: Set Cut at the middle window\nDelete: Delete nearest cut\nBackspace or W: Go to last position\nF1-F10: Goto Cut number X\nNumPad1 or Y: Small Step Back\nNumPad3 or C: Small Step Forward\nNumPad4: Medium Step Back\nNumPad6: Medium Step Forward\nNumPad7 or Q: Large Step Back\nNumPad9 or E: Large Step Forward\n"
        #"""self.keyHelp = "Space: Play/Pause\nA: Refine Cut to the Left\nD: Refine Cut to the Right\nS: Set Cut at the midlle window\nDelete:Delete nearest cut\nBackspace: Go to last position\nF1-F10: Goto Cut number X\nNumPad1,NumPad3,NumPad7: Small/Medium/Large Step Back\nNumPad3,NumPad6,NumPad9: Small/Medium/Large Step Forward\n" """
        self.Title = "tripleCut"
        self.setWindowTitle(self.Title)        
        self.fileLoaded = False

        print(platform.architecture())
        # creating a basic vlc instance
        print("Be sure that the vlc plugins are in the following plugin path and you have the correct version 32 or 64 bit")
        #libinfo=vlc        
        #libinfo=vlc.find_lib()
        #vlc.
        #print(libinfo)
        self.instance = vlc.Instance('--plugin-path=Z:/Programs/AutoOTR/vlc32/plugins')
        #print(self.instance )
        #vlc.tell(code)
        # creating an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()
        self.mediaplayerLeft = self.instance.media_player_new()
        self.mediaplayerRight = self.instance.media_player_new()
        self.setVolume(100)
        self.posMid = 0
        self.posLeft = 0
        self.posRight = 1
        self.history = []
        self.cutlist = []
        self.filename = ""
        self.createUI()        
    
    def dragEnterEvent(self, event): #Drag Drop of Files
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event): #Drag Drop of Files
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event): #Drag Drop of Files
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            url=event.mimeData().urls().pop() #get last file (accepts only one file)
            self.OpenFile(str(url.toLocalFile()))
        else:
            event.ignore()

    def nextFile(self):
        path = os.path.dirname(self.filename)
        files = glob.glob(path + "\*.avi");
        files = sorted(files)
        print(files)
        newFile=""
        setNext=False
        for x in files:
            i=x.replace("\\\\","/")
            i=i.replace("\\","/")
            self.filename.replace("\\","/")
            if setNext:
                newFile=i;
                break;
            print(self.filename,i)
            if i == self.filename:
                setNext=True        
        if len(newFile)>0:            
            self.OpenFile(newFile)    

    def eventFilter(self, source, event): #key handling
        if (event.type() == QtCore.QEvent.KeyPress and source is self.positionslider):
            key = event.key()            
            
            if key == QtCore.Qt.Key_Backspace or key == QtCore.Qt.Key_W : 
                self.loadLastPos()                            
            elif key == QtCore.Qt.Key_Space :
                self.PlayPause()
            elif key == QtCore.Qt.Key_A :
                self.buttonsClickedLeft()
            elif key == QtCore.Qt.Key_D :           
                self.buttonsClickedRight()            
            elif key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_S :
                self.buttonsClickedMid()
            elif key == QtCore.Qt.Key_Up :
                self.jumpSeconds(-1*60,-2)
            elif key == QtCore.Qt.Key_Down :                
                self.jumpSeconds(+1*60,-2)
            elif key == QtCore.Qt.Key_Left:
                self.jumpSeconds(-5,-2)
            elif key == QtCore.Qt.Key_Right :
                self.jumpSeconds(+5,-2)                
            elif key == QtCore.Qt.Key_1 or key == QtCore.Qt.Key_Y :
                self.jumpSeconds(-0.5*60,-1)
            elif key == QtCore.Qt.Key_3 or key == QtCore.Qt.Key_C:
                self.jumpSeconds(+0.5*60,-1)
            elif key == QtCore.Qt.Key_4 :
                self.jumpSeconds(-2*60,-1)
            elif key == QtCore.Qt.Key_6 :
                self.jumpSeconds(+2*60,-1)
            elif key == QtCore.Qt.Key_7 or key == QtCore.Qt.Key_Q:
                self.jumpSeconds(-5*60,-1)
            elif key == QtCore.Qt.Key_9 or key == QtCore.Qt.Key_E:
                self.jumpSeconds(+5*60,-1)
            elif key == QtCore.Qt.Key_Delete :            
                self.deleteCut()
            elif key == QtCore.Qt.Key_F1 :
                self.gotoCut(0)
            elif key == QtCore.Qt.Key_F2 :
                self.gotoCut(1)
            elif key == QtCore.Qt.Key_F3 :
                self.gotoCut(2)
            elif key == QtCore.Qt.Key_F4 :
                self.gotoCut(3)
            elif key == QtCore.Qt.Key_F5 :
                self.gotoCut(4)
            elif key == QtCore.Qt.Key_F6 :
                self.gotoCut(5)
            elif key == QtCore.Qt.Key_F7 :
                self.gotoCut(6)
            elif key == QtCore.Qt.Key_F8 :
                self.gotoCut(7)
            elif key == QtCore.Qt.Key_F9 :
                self.gotoCut(8)
            elif key == QtCore.Qt.Key_F10 :
                self.gotoCut(9)
            elif key == QtCore.Qt.Key_F11 :
                self.gotoCut(10)
            elif key == QtCore.Qt.Key_F12 :
                self.gotoCut(11)
            elif key == QtCore.Qt.Key_N :
                self.nextFile()
        return super(Player, self).eventFilter(source, event)

    def createUI(self):      #UI
        self.widget = QtWidgets.QWidget(self)
        self.setAcceptDrops(True)
        self.setCentralWidget(self.widget)        

        # In this widget, the video will be drawn        
        self.videoframe = QtWidgets.QFrame()
        self.videoframeLeft = QtWidgets.QFrame()
        self.videoframeRight = QtWidgets.QFrame()
        self.drawingframe = QtWidgets.QFrame()
        self.drawingframe.setFixedHeight(50);
        
        self.palette = self.videoframe.palette()        
        self.paletteLeft = self.videoframeLeft.palette()        
        self.paletteRight = self.videoframeRight.palette()
        
        self.positionslider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)        
        self.positionslider.setMaximum(1000)
        self.connect(self.positionslider, QtCore.SIGNAL("sliderMoved(int)"), self.newPositionOne)
        self.connect(self.positionslider, QtCore.SIGNAL("sliderReleased()"), self.newPositionAll)        
        
        self.hbuttonbox4 = QtWidgets.QHBoxLayout()        
        self.playbutton = QtWidgets.QPushButton("Play")
        self.hbuttonbox4.addWidget(self.playbutton)
        self.connect(self.playbutton, QtCore.SIGNAL("clicked()"), self.PlayPause)
        
        self.autocutbutton = QtWidgets.QPushButton("AutoCut")
        self.hbuttonbox4.addWidget(self.autocutbutton)
        self.connect(self.autocutbutton, QtCore.SIGNAL("clicked()"), self.AutoCut)        

        self.label = QtWidgets.QLabel()
        self.hbuttonbox4.addWidget(self.label)

        self.buttonLeft = QtWidgets.QPushButton("|<- (A)")        
        self.connect(self.buttonLeft, QtCore.SIGNAL("clicked()"), self.buttonsClickedLeft)
        self.buttonMid = QtWidgets.QPushButton("CUT (S)")        
        self.connect(self.buttonMid, QtCore.SIGNAL("clicked()"), self.buttonsClickedMid)
        self.buttonRight = QtWidgets.QPushButton("->| (D)")        
        self.connect(self.buttonRight, QtCore.SIGNAL("clicked()"), self.buttonsClickedRight)

        self.hbuttonbox4.addStretch(1)
        self.volumeslider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.volumeslider.setMaximum(100)
        self.volumeslider.setValue(self.mediaplayer.audio_get_volume())
        self.volumeslider.setToolTip("Volume")
        self.hbuttonbox4.addWidget(self.volumeslider)
        self.connect(self.volumeslider, QtCore.SIGNAL("valueChanged(int)"), self.setVolume)

        self.fullLayout = QtWidgets.QVBoxLayout()
        
        self.vboxlayout = QtWidgets.QHBoxLayout()
        self.vboxlayout.addWidget(self.videoframeLeft)
        self.vboxlayout.addWidget(self.videoframe)
        self.vboxlayout.addWidget(self.videoframeRight)

        self.hbuttonbox2 = QtWidgets.QHBoxLayout()
        self.hbuttonbox2.addWidget(self.positionslider)

        self.hbuttonbox3 = QtWidgets.QHBoxLayout()
        self.hbuttonbox3.addWidget(self.buttonLeft)
        self.hbuttonbox3.addWidget(self.buttonMid)
        self.hbuttonbox3.addWidget(self.buttonRight)

        self.hDrawing = QtWidgets.QHBoxLayout()
        self.hDrawing.addWidget(self.drawingframe)        

        self.fullLayout.addLayout(self.hbuttonbox4)        
        self.fullLayout.addLayout(self.hbuttonbox3)        
        self.fullLayout.addLayout(self.vboxlayout)   #movies        
        self.fullLayout.addLayout(self.hDrawing)        
        self.fullLayout.addLayout(self.hbuttonbox2)
                
        self.widget.setLayout(self.fullLayout)

        Xopen = QtWidgets.QAction("&Open", self)
        self.connect(Xopen, QtCore.SIGNAL("triggered()"), self.OpenFile)
        Xhelp = QtWidgets.QAction("&ShortCuts", self)
        self.connect(Xhelp, QtCore.SIGNAL("triggered()"), self.ShowHelp)
        Xexit = QtWidgets.QAction("&Exit", self)
        self.connect(Xexit, QtCore.SIGNAL("triggered()"), sys.exit)
        menubar = self.menuBar()
        filemenu = menubar.addMenu("&File")
        filemenu.addAction(Xopen)        
        filemenu.addAction(Xhelp)        
        filemenu.addAction(Xexit)

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(200)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.timerFunction)
        self.timer.start()

        QtGui.qApp.installEventFilter(self)
        self.installEventFilter(self)
        self.widget.installEventFilter(self)
        self.videoframeLeft.installEventFilter(self.videoframeLeft)
        self.videoframeRight.installEventFilter(self.videoframeRight)
        self.videoframe.installEventFilter(self.videoframe)

    def secondsToString(self,sec):
        avg = datetime.timedelta(seconds=sec)    
        avg = avg - datetime.timedelta(microseconds=avg.microseconds)
        return str(avg)
        
    def paintEvent(self, event): #paints the cutlist below the movies, is called every several 100ms
        qp = QtGui.QPainter()
        qp.begin(self)


        RR = self.videoframe.rect()
        #RR.translate(0,-400)
        #RR.setHeight(RR.height()*2)
        tl = self.videoframe.mapToParent(RR.topLeft());        
        br = self.videoframe.mapToParent(RR.bottomRight());        
        RR=QtCore.QRect(tl,br)
        RR.setWidth(RR.width()*3/2)
        RR.translate(-RR.width()/6,0)
        if not self.fileLoaded:
            qp.drawText(RR, QtCore.Qt.AlignCenter, "DROP FILES HERE")
        
        R = self.drawingframe.rect()
        R.translate(5,20) #don't know why, but we need to move rect some pixel down
        R.setWidth(R.width()-12) #the slider has not the full width 
        tl = self.drawingframe.mapToParent(R.topLeft());        
        br = self.drawingframe.mapToParent(R.bottomRight());        
        R=QtCore.QRect(tl,br)
    
        
                    
        
        doFill = 1
        last=-1.0;
        if not self.fileLoaded:
            return
        dummy, pureFilename = os.path.split(self.filename)
        self.stringList=["[General]", "Application=tripleCut.exe", "Version=1.0","ApplyToFile="+pureFilename, "FramesPerSecond=25", "IntendedCutApplicationName=VirtualDub" , "IntendedCutApplication=VirtualDub.exe", "NoOfCuts="+str(int(len(self.cutlist)/2)), "OriginalFileSizeBytes="+str(os.path.getsize(self.filename)), "[Info]", "Author=haribertlondon", "RatingByAuthor=3"]
        
        counter = 0
        self.duration = 0
        for (index, item) in enumerate(self.cutlist):            
            qp.setPen(QtGui.QPen(QtCore.Qt.red, 2));
            X=int(round(R.left()+item*R.width()))        
            qp.drawLine(QtCore.QPoint(X,tl.y()),QtCore.QPoint(X,br.y()))          
            
            qp.setPen(QtGui.QPen(QtCore.Qt.blue, 4));
            #ff=qp.font()
            #qp.setFont(QtGui.QFont("times",15))
            qp.drawText(QtCore.QRect(X-50+4,tl.y()+(index % 2)*10,100,br.y()-tl.y()), QtCore.Qt.AlignCenter, str(index+1) )
            #qp.setFont(ff);
              
            if last>=0:                
                if doFill == 1:                    
                    self.stringList.append(" ")
                    self.stringList.append("[Cut"+str(counter)+"]")
                    self.stringList.append("Start="+str(self.percentToSeconds(last)))
                    self.stringList.append("Duration="+str(self.percentToSeconds(item-last)))
                    self.duration = self.duration + self.percentToSeconds(item-last)
                    counter=counter+1
                    qp.setBrush(QtGui.QBrush(QtGui.QColor(40,10,100)));
                    doFill = 0;                    
                
                    X1=int(round(R.left()+item*R.width()))
                    X2=int(round(R.left()+last*R.width()))        
                    qp.fillRect(X1,tl.y(),X2-X1,br.y()-tl.y(),QtGui.QBrush(QtGui.QColor(40,10,100,70)))                
                else:
                    doFill = 1
            last=item
        
        qp.setPen(QtGui.QPen(QtGui.QColor(0,150,0,255), 2,QtCore.Qt.DashDotLine));  
        X=int(round(R.left()+self.posMid*R.width()))
        qp.drawText(QtCore.QRect(X-50,tl.y(),100,br.y()-tl.y()),
                    QtCore.Qt.AlignCenter, self.secondsToString(self.percentToSeconds(self.posMid))
                    +"\n"+self.secondsToString(self.percentToSeconds(self.posRight-self.posLeft))
                    )

        qp.setPen(QtGui.QPen(QtGui.QColor(0,0,0,50), 2,QtCore.Qt.DashDotLine));  
        qp.drawLine(QtCore.QPoint(X,tl.y()),QtCore.QPoint(X,br.y()))        
        

        X=int(round(R.left()+self.posLeft*R.width()))        
        qp.drawLine(QtCore.QPoint(X,tl.y()),QtCore.QPoint(X,br.y()))            

        X=int(round(R.left()+self.posRight*R.width()))        
        qp.drawLine(QtCore.QPoint(X,tl.y()),QtCore.QPoint(X,br.y()))       
        
        qp.end()

        if len(self.cutlist)>1:
            fileUtils.writeList(self.filename+'.cutlist', self.stringList)            

        if len(self.cutlist)% 2 == 1 :
            currentStr = "("+self.secondsToString(self.duration+self.percentToSeconds(abs(self.posMid-self.cutlist[-1])))+")"
        else:
            currentStr = ""
        
        self.label.setText("Cut: "+self.secondsToString(self.duration)+currentStr+" Full: "+self.secondsToString(self.percentToSeconds(1.0)))

    def gotoCut(self, cutlistidx):
        if cutlistidx < len(self.cutlist):
            self.newPositionOneInterval(self.cutlist[cutlistidx]*1000, 2*60)
            self.newPositionAll()

    def secondsToPercent(self, seconds) :        
        return float(seconds)*1000 / float(self.media.get_duration())

    def percentToSeconds(self, percent):
        return float(percent) * float(self.media.get_duration())/1000.0

    def jumpSeconds(self, seconds, interval) :

        if interval == -1:
            interval = abs(seconds)
        elif interval == -2:
            interval = self.percentToSeconds(abs(self.posRight-self.posLeft)/2.0)
        
        self.newPositionOneInterval( (self.posMid + self.secondsToPercent(seconds))*1000, interval)
        self.newPositionAll()
        self.saveLastPos()    

    def saveLastPos(self): #history of last positions
        self.history.append([self.posLeft, self.posRight, self.posMid])

    def deleteCut(self):
        #self.cutlist.pop() #delete last entry of the cutlist, too simple
        #get closest cut
        idx = min(range(len(self.cutlist)), key=lambda i: abs(self.cutlist[i]-self.posMid))        
        self.cutlist.pop(idx)

    def loadLastPos(self):                
        if len(self.history) > 0:
            triple = self.history.pop()            
            if abs(self.posLeft-triple[0])<1e-4 and abs(self.posRight-triple[1])<1e-4 and abs(self.posMid-triple[2])<1e-4:                
                self.loadLastPos()
            else:    
                self.posLeft= triple[0]
                self.posRight=triple[1]
                self.posMid=triple[2]
            
                self.newPositionAll()                

    def checkIfCutAccurate(self): # if left and right < 0.7sec, go to next cut
        if self.percentToSeconds(abs(self.posRight-self.posLeft))<0.7: #if cut is better than 1 sec, take this one
            self.buttonsClickedMid()
        
    def buttonsClickedRight(self):        
        self.posLeft=self.posMid;
        self.posMid=max(0,min(1,(self.posMid+self.posRight)/2))
        self.saveLastPos() 
        self.newPositionAll()

    def buttonsClickedLeft(self):        
        self.posRight=self.posMid;
        self.posMid=max(0,min(1,((self.posMid+self.posLeft)/2)))
        self.saveLastPos() 
        self.newPositionAll()
        self.checkIfCutAccurate()

    def buttonsClickedMid(self):
        self.cutlist.append(self.posMid)
        self.cutlist.sort()
        self.jumpSeconds(+9*60, 5*60) #jump x minutes

    def AutoCut(self):        
        comskipper.execute("Z:\\Programs\\comskip\\",self.filename)
        self.loadEdlFile(self.filename)
        

    def PlayPause(self):
        """Toggle play/pause status"""
        if self.mediaplayer.is_playing():
            self.mediaplayer.audio_set_volume(0)
            self.mediaplayer.pause()            
            self.isPaused = True
        else:
            if self.mediaplayer.play() == -1:
                self.OpenFile()
                return
            self.mediaplayer.play()
            self.mediaplayer.audio_set_volume(self.volume)
            self.timer.start()

    def ShowHelp(self):        
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("ShortCuts")
        msg.setInformativeText(self.keyHelp);
        msg.setWindowTitle(self.Title)        
        msg.exec_()
        
    def loadEdlFile(self, filename):               
        edlFile=filename.replace(".avi",".edl")

        if os.path.isfile(edlFile):
            try:                           
                fobj = fileUtils.loadList(edlFile)
                for line in fobj:
                    row = line.split("\t")   
                    t0=float(row[0]);        
                    t1=float(row[1]);                             
                    if (t1-t0)>60 or True: #only add ads larger than 1 minute                   
                        self.cutlist.append(self.secondsToPercent(t0))
                        self.cutlist.append(self.secondsToPercent(t1))                   
            except Exception as e:            
                print(e)
                pass
        
    def loadCutlist(self, filename):               
        cutlistFile=filename+".cutlist"
        validFile = False
        if os.path.isfile(cutlistFile):
            try:                           
                fobj = fileUtils.loadList(cutlistFile)
                for line in fobj:
                    print(line)
                    if "Start=" in line:
                        print("START")
                        t0=float(line.replace("Start=",""));
                        self.cutlist.append(self.secondsToPercent(t0))
                    if "Duration=" in line:
                        print("DUR")
                        t1=float(line.replace("Duration=",""))+t0;                                        
                        self.cutlist.append(self.secondsToPercent(t1))
                        validFile = True
            except Exception as e:            
                print(e)
        return validFile

    def OpenFile(self, filename=None):
        """Open a media file in a MediaPlayer"""
        self.fileLoaded = False
        if filename is None:
            filename = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", os.path.expanduser('~'))
        if not filename:
            return

        
        if not os.path.isfile(filename):
            return

        self.fileLoaded = True
        self.filename = filename        
        self.cutlist = [] #stores the cutlist

        self.setWindowTitle(self.Title+" "+self.filename)
        
        self.media = self.instance.media_new(filename)
        self.mediaLeft = self.instance.media_new(filename)
        self.mediaRight = self.instance.media_new(filename)
        # put the media in the media player
        self.mediaplayer.set_media(self.media)
        self.mediaplayerLeft.set_media(self.mediaLeft)
        self.mediaplayerRight.set_media(self.mediaRight)

        # parse the metadata of the file
        self.media.parse()
        self.mediaLeft.parse()
        self.mediaRight.parse()        
      
        self.mediaplayer.set_hwnd(self.videoframe.winId())
        self.mediaplayerLeft.set_hwnd(self.videoframeLeft.winId())
        self.mediaplayerRight.set_hwnd(self.videoframeRight.winId())

        self.mediaplayer.audio_set_volume(0)
        self.mediaplayerLeft.audio_set_volume(0)
        self.mediaplayerRight.audio_set_volume(0)

        validCutlist = self.loadCutlist(filename)
        if not validCutlist:
            self.loadEdlFile(filename)
        
            

        self.posMid = 0                
        self.jumpSeconds(+5*60,-1) # jump to 5min at the beginning of the movie
        self.newPositionAll()
        self.saveLastPos()                        

    def setVolume(self, Volume):
        self.volume=Volume;
        self.mediaplayer.audio_set_volume(Volume)
        self.mediaplayerLeft.audio_set_volume(0)
        self.mediaplayerRight.audio_set_volume(0)

    def newPositionAll(self):                      
        self.mediaplayer.play()        
        self.mediaplayer.set_position(self.posMid)        
        self.mediaplayer.next_frame()
        
        self.mediaplayerLeft.play()        
        self.mediaplayerLeft.set_position(self.posLeft)
        self.mediaplayerLeft.next_frame()
        
        self.mediaplayerRight.play()        
        self.mediaplayerRight.set_position(self.posRight)        
        self.mediaplayerRight.next_frame()

        self.updateUI()        

    def newPositionOne(self, position):
        self.newPositionOneInterval(position, 5*60)
        
    def newPositionOneInterval(self, position, interval):                        
        if self.posMid > 1:            
            self.posRight = 1
            self.posLeft = max(1-2*self.secondsToPercent(interval),0)
            self.posMid = max(min(1-self.secondsToPercent(interval),1),0)
        elif self.posMid < 0:
            self.posMid = max(0,min(1,(self.secondsToPercent(interval))))
            self.posLeft = 0
            self.posRight = 2*self.secondsToPercent(interval)
        else:
            self.posMid = max(0,min(1,(position/1000.0)))
            self.posRight = min(self.posMid+self.secondsToPercent(interval),1)
            self.posLeft = max(self.posMid-self.secondsToPercent(interval),0)

        self.mediaplayer.set_position(self.posMid)        
                        
    def setPosition(self, position):
        """Set the position"""         
        self.mediaplayer.set_position(position / 1000.0)
        self.newPosition(position / 1000.0)                

    def updateUI(self):                
        self.positionslider.setValue(self.mediaplayer.get_position() * 1000) # setting the slider to the desired position
        self.update()

    def timerFunction(self):
        self.updateUI()

        self.posMid = max(0,min(1,(self.mediaplayer.get_position())))

        #if (self.mediaplayer.get_position()>self.posRight): #loop between left and right position
        #    self.posMid = self.posLeft
        #    self.newPositionAll()
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    player = Player()
    player.show()
    player.resize(640, 330)
    if sys.argv[1:]:
        player.OpenFile(sys.argv[1])
    else:
        player.OpenFile("")    
    sys.exit(app.exec_())
