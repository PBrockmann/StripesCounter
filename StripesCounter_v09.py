#!/usr/bin/env python

#=================================================================
# Author: Patrick Brockmann CEA/DRF/LSCE - April 2021
#=================================================================

import sys, os, re
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5.Qt import Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.patches as patches
from matplotlib.lines import Line2D

from skimage.measure import profile_line
import peakutils

import numpy as np
import matplotlib.pyplot as plt
import cv2

import text_line

version = "v09.3"

maximumWidth = 250

#plt.rcParams['ytick.left'] = plt.rcParams['ytick.labelleft'] = True
#plt.rcParams['ytick.right'] = plt.rcParams['ytick.labelright'] = True
#plt.rcParams['xtick.bottom'] = plt.rcParams['xtick.labelbottom'] = True
#plt.rcParams['xtick.top'] = plt.rcParams['xtick.labeltop'] = True

class MainWindow(QMainWindow):

    #------------------------------------------------------------------
    def __init__(self):
        QMainWindow.__init__(self)

        self.initValues()

        #-------------------------------
        self.setMinimumSize(QSize(1100, 800))    
        self.setWindowTitle("StripesCounter " + version) 

        # Create new action
        openAction = QAction(QIcon('open.png'), '&Open', self)        
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open document')
        openAction.triggered.connect(self.openCall)

        # Create exit action
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.exitCall)

        # Create about action
        aboutAction = QAction(QIcon('about.png'), '&About', self)        
        aboutAction.setShortcut('F1')
        aboutAction.setStatusTip('About the application')
        aboutAction.triggered.connect(self.aboutCall)

        # Create menu bar and add action
        self.menuBar = self.menuBar()
        fileMenu = self.menuBar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)
        fileMenu = self.menuBar.addMenu('&About')
        fileMenu.addAction(aboutAction)

        self.labelAlpha = QLabel("Contrast level : 1.0")
        self.labelAlpha.setAlignment(Qt.AlignLeft)
        self.labelBeta = QLabel("Brightness level : 0")
        self.labelBeta.setAlignment(Qt.AlignLeft)
        self.labelKernelSize = QLabel("Kernel size : " + str(self.kernelSize))
        self.labelKernelSize.setAlignment(Qt.AlignLeft)
        self.labelPeakUtils_minDist = QLabel("PeakUtils - Minimum distance : " + str(self.peakutils_minDist))
        self.labelPeakUtils_minDist.setAlignment(Qt.AlignLeft)
        self.labelPeakUtils_thres = QLabel("PeakUtils - Threshold : " + str(self.peakutils_thres))
        self.labelPeakUtils_thres.setAlignment(Qt.AlignLeft)

        self.mySliderAlpha = QSlider(Qt.Horizontal, self)
        self.mySliderAlpha.setMaximumWidth(maximumWidth)
        self.mySliderAlpha.setMinimum(10)
        self.mySliderAlpha.setMaximum(30)
        self.mySliderAlpha.setValue(1)
        self.mySliderAlpha.setTickInterval(1)
        self.mySliderAlpha.setTickPosition(QSlider.TicksBelow)
        self.mySliderAlpha.valueChanged[int].connect(self.changeValueAlpha)

        self.mySliderBeta = QSlider(Qt.Horizontal, self)
        self.mySliderBeta.setMaximumWidth(maximumWidth)
        self.mySliderBeta.setMinimum(-100)
        self.mySliderBeta.setMaximum(100)
        self.mySliderBeta.setValue(0)
        self.mySliderBeta.setTickInterval(5)
        self.mySliderBeta.setTickPosition(QSlider.TicksBelow)
        self.mySliderBeta.valueChanged[int].connect(self.changeValueBeta)

        self.mySliderKernelSize = QSlider(Qt.Horizontal, self)
        self.mySliderKernelSize.setMaximumWidth(maximumWidth)
        self.mySliderKernelSize.setMinimum(1)
        self.mySliderKernelSize.setMaximum(51)
        self.mySliderKernelSize.setValue(self.kernelSize)
        self.mySliderKernelSize.setTickInterval(2)
        self.mySliderKernelSize.setSingleStep(2)
        self.mySliderKernelSize.setTickPosition(QSlider.TicksBelow)
        self.mySliderKernelSize.valueChanged[int].connect(self.changeValueKernelSize)

        self.mySliderPeakUtils_minDist = QSlider(Qt.Horizontal, self)
        self.mySliderPeakUtils_minDist.setMaximumWidth(maximumWidth)
        self.mySliderPeakUtils_minDist.setMinimum(1)
        self.mySliderPeakUtils_minDist.setMaximum(30)
        self.mySliderPeakUtils_minDist.setValue(self.peakutils_minDist)
        self.mySliderPeakUtils_minDist.setTickInterval(1)
        self.mySliderPeakUtils_minDist.setTickPosition(QSlider.TicksBelow)
        self.mySliderPeakUtils_minDist.valueChanged[int].connect(self.changeValuePeakUtils_minDist)

        self.mySliderPeakUtils_thres = QSlider(Qt.Horizontal, self)
        self.mySliderPeakUtils_thres.setMaximumWidth(maximumWidth)
        self.mySliderPeakUtils_thres.setMinimum(1)
        self.mySliderPeakUtils_thres.setMaximum(9)
        self.mySliderPeakUtils_thres.setValue(int(self.peakutils_thres*10))
        self.mySliderPeakUtils_thres.setTickInterval(1)
        self.mySliderPeakUtils_thres.setTickPosition(QSlider.TicksBelow)
        self.mySliderPeakUtils_thres.valueChanged[int].connect(self.changeValuePeakUtils_thres)

        #-----------------------
        self.fig, self.ax = plt.subplots(nrows=2, figsize=(8,8), gridspec_kw={
                           'height_ratios': [2, 1]})
        self.fig.tight_layout()
        self.fig.subplots_adjust(top=0.9, bottom=0.15)

        self.canvas = FigureCanvas(self.fig)
        # https://github.com/matplotlib/matplotlib/issues/707/
        self.canvas.setFocusPolicy(Qt.ClickFocus)
        self.canvas.setFocus()

        self.canvas.mpl_connect('button_press_event', self.on_click)

        #-----------------------
        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.pan()

        self.buttonDefineScaleValue = QPushButton('Define scale value')
        self.buttonDefineScaleValue.setMaximumWidth(maximumWidth)
        self.buttonDefineScaleValue.clicked.connect(self.defineScaleValue)

        self.buttonDefineScale = QPushButton('Define scale')
        self.buttonDefineScale.setMaximumWidth(maximumWidth)
        self.buttonDefineScale.clicked.connect(self.defineScale)

        self.buttonSave = QPushButton('Save data as CSV and image as PNG')
        self.buttonSave.setMaximumWidth(maximumWidth)
        self.buttonSave.clicked.connect(self.save)

        layoutH = QHBoxLayout()

        layoutV1 = QVBoxLayout()
        layoutV1.addWidget(self.canvas)
        layoutV1.addWidget(self.toolbar)

        layoutV2 = QVBoxLayout()
        layoutV2.setAlignment(Qt.AlignTop)
        layoutV2.addWidget(self.labelAlpha)
        layoutV2.addWidget(self.mySliderAlpha)
        layoutV2.addSpacing(1)
        layoutV2.addWidget(self.labelBeta)
        layoutV2.addWidget(self.mySliderBeta)
        layoutV2.addSpacing(1)
        layoutV2.addWidget(self.labelKernelSize)
        layoutV2.addWidget(self.mySliderKernelSize)
        layoutV2.addSpacing(1)
        layoutV2.addWidget(self.labelPeakUtils_minDist)
        layoutV2.addWidget(self.mySliderPeakUtils_minDist)
        layoutV2.addSpacing(1)
        layoutV2.addWidget(self.labelPeakUtils_thres)
        layoutV2.addWidget(self.mySliderPeakUtils_thres)
        layoutV2.addSpacing(5)
        layoutV2.addWidget(self.buttonDefineScaleValue)
        layoutV2.addWidget(self.buttonDefineScale)
        layoutV2.addWidget(self.buttonSave)

        layoutH.addLayout(layoutV1)
        layoutH.addLayout(layoutV2)
        #layoutH.addStretch(1)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QWidget()
        widget.setLayout(layoutH)
        self.setCentralWidget(widget)

        self.initInterface()

    #------------------------------------------------------------------
    def initValues(self):
        self.point_alpha_default = 0.4

        self.point1_object = None
        self.point2_object = None
        self.line_object = None
        self.scale_object = None
        self.scaleValue_object = None

        self.scaleValue = 0.
        self.scaleLength = 0

        self.point1 = [0,0]
        self.point2 = [0,0]
        self.offset = [0,0]

        self.current_artist = None
        self.currently_dragging = False

        self.kernelSize = 3 
        self.peakutils_minDist = 1
        self.peakutils_thres = 0.5

        self.dist_profil = None
        self.profil = None
        self.profil_convolved = None
        self.indexes = None

        self.line1 = self.line2 = self.line3 = None
        self.counterFilename = 1

    #------------------------------------------------------------------
    def initInterface(self):
        self.labelAlpha.setEnabled(False)
        self.mySliderAlpha.setEnabled(False)
        self.labelBeta.setEnabled(False)
        self.mySliderBeta.setEnabled(False)
        self.labelKernelSize.setEnabled(False)
        self.mySliderKernelSize.setEnabled(False)
        self.labelPeakUtils_thres.setEnabled(False)
        self.mySliderPeakUtils_thres.setEnabled(False)
        self.labelPeakUtils_minDist.setEnabled(False)
        self.mySliderPeakUtils_minDist.setEnabled(False)
        self.buttonDefineScale.setEnabled(False)
        self.buttonDefineScaleValue.setEnabled(False)
        self.buttonSave.setEnabled(False)

        self.mySliderKernelSize.setValue(self.kernelSize)
        self.mySliderPeakUtils_minDist.setValue(self.peakutils_minDist)
        self.mySliderPeakUtils_thres.setValue(int(self.peakutils_thres*10))

        self.ax[0].set_visible(False)
        self.ax[1].set_visible(False)

    #------------------------------------------------------------------
    def changeValueAlpha(self, value):
        self.alphaLevel = value/10.
        self.labelAlpha.setText("Contrast level : " + str(self.alphaLevel))
        self.adjusted = cv2.convertScaleAbs(self.gray, alpha=self.alphaLevel, beta=self.betaLevel)
        self.image_object.set_data(self.adjusted)
        self.drawProfil()
        self.canvas.draw()

    #------------------------------------------------------------------
    def changeValueBeta(self, value):
        self.betaLevel = value
        self.labelBeta.setText("Brighness level : " + str(self.betaLevel))
        self.adjusted = cv2.convertScaleAbs(self.gray, alpha=self.alphaLevel, beta=self.betaLevel)
        self.image_object.set_data(self.adjusted)
        self.drawProfil()
        self.canvas.draw()

    #------------------------------------------------------------------
    def changeValueKernelSize(self, value):
        if value % 2 != 0:
            self.kernelSize = value
            self.labelKernelSize.setText("Kernel size : " + str(self.kernelSize))
            self.drawProfil()

    #------------------------------------------------------------------
    def changeValuePeakUtils_minDist(self, value):
        self.peakutils_minDist = value
        self.labelPeakUtils_minDist.setText("PeakUtils - Minimum distance : " + str(self.peakutils_minDist))
        self.drawProfil()
        
    #------------------------------------------------------------------
    def changeValuePeakUtils_thres(self, value):
        self.peakutils_thres = value/10.
        self.labelPeakUtils_thres.setText("PeakUtils - Threshold : " + str(self.peakutils_thres))
        self.drawProfil()

    #------------------------------------------------------------------
    def on_press(self, event):
        self.currently_dragging = True

    #------------------------------------------------------------------
    def on_release(self, event):
        self.current_artist = None
        self.currently_dragging = False

    #------------------------------------------------------------------
    def on_pick(self, event):
        if self.current_artist is None:
            self.current_artist = event.artist
            if isinstance(event.artist, patches.Circle):
                #print("circle picked")
                self.current_artist = event.artist
                x0, y0 = self.current_artist.center
                x1, y1 = event.mouseevent.xdata, event.mouseevent.ydata
                self.offset = [(x0 - x1), (y0 - y1)]
            elif isinstance(event.artist, Line2D):
                #print("line picked")
                xdata = event.artist.get_xdata()
                ydata = event.artist.get_ydata()
                x1, y1 = event.mouseevent.xdata, event.mouseevent.ydata
                self.offset = xdata[0] - x1, ydata[0] - y1

    #------------------------------------------------------------------
    def on_motion(self, event):
        if not self.currently_dragging:
            return
        if self.current_artist == None:
            return
        if event.xdata == None:
            return
        dx, dy = self.offset
        if isinstance(self.current_artist, patches.Circle):
            cx, cy =  event.xdata + dx, event.ydata + dy
            self.current_artist.center = cx, cy
            if self.current_artist.get_label() == "point1":
                self.point1 =  [cx, cy]
            elif self.current_artist.get_label() == "point2":
                self.point2 =  [cx, cy]
            self.line_object[0].set_data([self.point1[0], self.point2[0]],[self.point1[1], self.point2[1]])
        elif isinstance(self.current_artist, Line2D):
            xdata = self.current_artist.get_xdata()
            ydata = self.current_artist.get_ydata()
            self.point1 =  [event.xdata + dx, event.ydata + dy]
            self.point2 =  [event.xdata + dx + xdata[1] - xdata[0], event.ydata + dy + ydata[1] - ydata[0]]
            self.current_artist.set_xdata([self.point1[0], self.point2[0]])
            self.current_artist.set_ydata([self.point1[1], self.point2[1]])
            self.point1_object.center = self.point1[0], self.point1[1]
            self.point2_object.center = self.point2[0], self.point2[1]
        self.drawLine()
        
    #------------------------------------------------------------------
    def on_click(self, event):
        if event and event.dblclick:
            if self.point1_object == None:
                self.point1 = [event.xdata, event.ydata]
                self.point1_object = patches.Circle(self.point1, radius=50, fc='r', lw=2, fill=False, color='r',
                    alpha=self.point_alpha_default, transform=self.ax[0].transData, label="point1")
                self.ax[0].add_patch(self.point1_object)
                self.point1_object.set_picker(5)
            elif self.point2_object == None:
                self.point2 = [event.xdata, event.ydata]
                self.point2_object = patches.Circle(self.point2, radius=50, fc='r', lw=2, fill=False, color='r',
                    alpha=self.point_alpha_default, transform=self.ax[0].transData, label="point2")
                self.ax[0].add_patch(self.point2_object)
                self.point2_object.set_picker(5)
                self.line_object = self.ax[0].plot([self.point1[0], self.point2[0]], [self.point1[1], self.point2[1]], 
                    alpha=0.5, c='r', lw=2, picker=True)
            self.canvas.draw()
        self.drawLine()

    #------------------------------------------------------------------
    def drawLine(self):
        if self.point1_object != None and self.point2_object != None and self.line_object != None:
            self.line_object[0].set_data([self.point1[0], self.point2[0]],[self.point1[1], self.point2[1]])
            self.canvas.draw()
            self.line_object[0].set_pickradius(5)
            for canvas in set(artist.figure.canvas for artist in 
                            [self.point1_object, self.point2_object, self.line_object[0]]):
                canvas.mpl_connect('button_press_event', self.on_press)
                canvas.mpl_connect('button_release_event', self.on_release)
                canvas.mpl_connect('pick_event', self.on_pick)
                canvas.mpl_connect('motion_notify_event', self.on_motion)
            self.drawProfil()

    #------------------------------------------------------------------
    def drawProfil(self):
        if self.line_object is None:
            return 

        try:
            if self.scaleValue != 0. and self.scaleLength != 0:
                self.scalePixel = self.scaleValue / self.scaleLength
            else:
                self.scalePixel = 1

            self.profil = profile_line(self.adjusted, 
                    (self.point1[1], self.point1[0]), (self.point2[1], self.point2[0]),   # (Y1, X1), (Y2, X2) 
                    order=0, mode='constant', cval=0)
            
            self.ax[1].set_visible(True)
            self.ax[1].clear()
            
            self.dist_profil = np.linspace(0, self.scalePixel*len(self.profil), num=len(self.profil))
            self.ax[1].plot(self.dist_profil, self.profil, c='r', lw=1, alpha=0.8)
            
            kernel = np.ones(self.kernelSize) / self.kernelSize
            kernelOffset = int(self.kernelSize/2)
            
            # mode='same' gives artefact at start and end 
            #self.profil_convolved = np.convolve(self.profil, self.kernel, mode='same')
            #self.ax[1].plot(self.dist_profil, self.profil_convolved, c='c', lw=1, alpha=0.8)
            
            # use mode='valid' but need to take into account with absysse values 
            #   (dist_profil[int(kernelSize/2):-int(kernelSize/2)])
            self.profil_convolved = np.convolve(self.profil, kernel, mode='valid')
            if self.kernelSize == 1 :
                self.ax[1].plot(self.dist_profil, self.profil_convolved, c='b', lw=1, alpha=0.8)
            else:
                self.ax[1].plot(self.dist_profil[kernelOffset:-kernelOffset], 
                                self.profil_convolved, c='b', lw=1, alpha=0.8)
            
            # https://peakutils.readthedocs.io/en/latest/reference.html
            self.indexes = peakutils.indexes(self.profil_convolved, thres=self.peakutils_thres, 
                            thres_abs=False, min_dist=self.peakutils_minDist)
            self.ax[1].scatter(self.dist_profil[self.indexes+kernelOffset], 
                                self.profil_convolved[self.indexes], c='b', s=10)  # add offset of the kernel/2
            
            stripesNb = len(self.indexes)
            stripesDist = self.dist_profil[self.indexes[-1]+kernelOffset]-self.dist_profil[self.indexes[0]+kernelOffset]
            self.line1 = "Number of stripes: %3d" %(stripesNb)
            self.line2 = "Length of stripes: %.5f  (first: %.5f, last: %.5f)" \
                         %(stripesDist, self.dist_profil[self.indexes[0]+kernelOffset], 
                                        self.dist_profil[self.indexes[-1]+kernelOffset])
            self.line3 = "Growth stripe rate (µm/stripe): %.5f" %(1000*stripesDist/stripesNb)
            
            self.ax[1].text(0.2, 0.1, self.line1 + '\n' + self.line2 + '\n' + self.line3, 
                    va="top", transform=self.fig.transFigure)
            
            self.ax[1].grid(linestyle='dotted')

            self.labelKernelSize.setEnabled(True)
            self.mySliderKernelSize.setEnabled(True)
            self.labelPeakUtils_minDist.setEnabled(True)
            self.mySliderPeakUtils_minDist.setEnabled(True)
            self.labelPeakUtils_thres.setEnabled(True)
            self.mySliderPeakUtils_thres.setEnabled(True)
            self.buttonDefineScaleValue.setEnabled(True)
            self.buttonDefineScale.setEnabled(True)
            self.buttonSave.setEnabled(True)

            self.canvas.draw()

        except:
            #print("Error in drawProfile")
            return 

    #------------------------------------------------------------------
    def openCall(self):
        self.openFileNameDialog()

    #------------------------------------------------------------------
    def detectScale(self):
        try:
            fld = cv2.ximgproc.createFastLineDetector()
            lines = fld.detect(self.mask)
            self.scaleLength = 0
            for line in lines:
                pt1 = np.array((line[0][0],line[0][1]))
                pt2 = np.array((line[0][2],line[0][3]))
                length = np.linalg.norm(pt1 - pt2)
                #print(pt1, pt2, dist)
                if (length > self.scaleLength):
                    self.scaleLength = int(length)
                    self.point1Scale = pt1
                    self.point2Scale = pt2
            #print("Detected scale length in pixel: ", scaleLength)

            if self.scaleLength > 0:
                self.scale_object = self.ax[0].plot([self.point1Scale[0], self.point2Scale[0]], 
                                                    [self.point1Scale[1], self.point2Scale[1]],
                                                    alpha=1.0, c='purple', lw=2)
        except:
            self.scaleLength = 0

        try:
            # Set a default scaleValue_object
            self.scaleValue_object = self.ax[0].text(200, 200, "   %.2f mm" %(self.scaleValue),
                alpha=1.0, c='purple', horizontalalignment='left', verticalalignment='bottom', clip_on=True)

            import pytesseract

            scaleDetected = pytesseract.image_to_string(self.mask)
            matchObj = re.match(r'[^0-9]*([0-9]*)mm', scaleDetected.strip())
            self.scaleValue = float(matchObj.group(1))
            #print("Detected scale value: ", self.scaleValue)
            self.scaleValue_object.set_text("  %.2f mm" %(self.scaleValue))

        except:
            self.scaleValue = 0.

    #------------------------------------------------------------------
    def defineScaleValue(self):
        #value, okPressed = QInputDialog.getDouble(self, "Get scale value","Value:", self.scaleValue, 0, 100, 1)
        # --> get comma instead of dot
        dialog = QInputDialog()
        dialog.setInputMode(QInputDialog.DoubleInput)
        dialog.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        dialog.setLabelText("Value : ")
        dialog.setDoubleMinimum(0)
        dialog.setDoubleMaximum(100)
        dialog.setDoubleStep(1)
        dialog.setDoubleDecimals(2)
        dialog.setDoubleValue(self.scaleValue)
        dialog.setWindowTitle("Get scale value")
        okPressed = dialog.exec_()
        if okPressed:
            self.scaleValue = dialog.doubleValue()
        else:
            return

        self.ax[0].set_title(os.path.basename(self.imageFileName) + '\n'
            + "          Scale length [pixels]: %s" %(self.scaleLength) + '\n'
            + "          Scale value [mm]: %.2f" %(self.scaleValue),
            loc='left', fontsize=10)
        self.scaleValue_object.set_text("   %.2f mm" %(self.scaleValue))
        self.drawProfil()

    #------------------------------------------------------------------
    def defineScale(self):
        self.point1Scale = self.point1
        self.point2Scale = self.point2
        self.scaleLength = int(np.linalg.norm(np.array(self.point1Scale) - np.array(self.point2Scale)))
        self.ax[0].set_title(os.path.basename(self.imageFileName) + '\n' 
            + "          Scale length [pixels]: %s" %(self.scaleLength) + '\n'
            + "          Scale value [mm]: %.2f" %(self.scaleValue),
            loc='left', fontsize=10)
        if self.scale_object == None:
            self.scale_object = self.ax[0].plot([self.point1Scale[0], self.point2Scale[0]], 
                                                [self.point1Scale[1], self.point2Scale[1]],
                                                alpha=1.0, c='purple', lw=2)
        else:
            self.scale_object[0].set_data([self.point1Scale[0], self.point2Scale[0]],
                                          [self.point1Scale[1], self.point2Scale[1]])
        self.scaleValue_object.set_position((self.point1Scale[0], self.point1Scale[1]))
        self.drawProfil()

    #------------------------------------------------------------------
    def displayImage(self):
        self.initValues()
        self.initInterface()

        self.ax[0].set_visible(True)
        self.ax[0].clear()

        img = cv2.imread(self.imageFileName)
        self.gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.mask = cv2.inRange(self.gray, 0, 0)
        self.alphaLevel =  self.mySliderAlpha.value()/10.
        self.betaLevel = self.mySliderBeta.value()
        self.adjusted = cv2.convertScaleAbs(self.gray, alpha=self.alphaLevel, beta=self.betaLevel)
        self.image_object = self.ax[0].imshow(self.adjusted, cmap='gray')
        self.detectScale()

        self.ax[0].set_title(os.path.basename(self.imageFileName) + '\n'
            + "          Scale length [pixels]: %s" %(self.scaleLength) + '\n'
            + "          Scale value [mm]: %.2f" %(self.scaleValue),
            loc='left', fontsize=10)

        self.labelAlpha.setEnabled(True)
        self.mySliderAlpha.setEnabled(True)
        self.labelBeta.setEnabled(True)
        self.mySliderBeta.setEnabled(True)

        self.canvas.draw()

    #------------------------------------------------------------------
    def save(self):
        base=os.path.basename(self.imageFileName)
        file1Name = os.path.splitext(base)[0] + "_StripesCounterFile_{}.csv"
        while os.path.isfile(file1Name.format("%02d" %self.counterFilename)):
            self.counterFilename += 1
        file1NameCSV = file1Name.format("%02d" %self.counterFilename)
        file1 = open(file1NameCSV, "w")
        file1.write("#================================================\n")
        file1.write("# StripesCounter " + version + "\n")
        file1.write("# File: %s\n" %(self.imageFileName))
        file1.write("# Detected scale value: %d\n" %(self.scaleValue))
        file1.write("# Detected scale length in pixel: %d\n" %(self.scaleLength))
        file1.write("# Point1: [%d, %d]\n" %(self.point1[0], self.point1[1]))
        file1.write("# Point2: [%d, %d]\n" %(self.point2[0], self.point2[1]))
        file1.write("# " + self.line1 + '\n# ' + self.line2 + '\n# ' + self.line3 + '\n')
        file1.write("#================================================\n")
        kernelOffset = int(self.kernelSize/2)
        file1.write("n,xpos,ypos1,ypos2,peak\n")
        for i,v in enumerate(self.dist_profil):
                if i-kernelOffset >= 0  and i-kernelOffset < len(self.profil_convolved): 
                        if i-kernelOffset in self.indexes:
                        	file1.write("%d,%.5f,%.5f,%.5f,%d\n" 
                                        %(i+1, self.dist_profil[i], self.profil[i], self.profil_convolved[i-kernelOffset], 1))
                        else:
                        	file1.write("%d,%.5f,%.5f,%.5f,%d\n" 
                                        %(i+1, self.dist_profil[i], self.profil[i], self.profil_convolved[i-kernelOffset], 0))

                else:
                        file1.write("%d,%.5f,%.5f,%.5f,%d\n" %(i+1, self.dist_profil[i], self.profil[i], -999, 0))
        file1.close()
        file1NamePNG = os.path.splitext(file1NameCSV)[0] + ".png"
        plt.savefig(file1NamePNG)
        print("---------------------------")
        print("Saved csv file: " + file1NameCSV)
        print("Saved png file: " + file1NamePNG)
        
        # draw the line to keep a record of what has been saved so far.
        self.ax[0].plot([self.point1[0], self.point2[0]], [self.point1[1], self.point2[1]], 
                alpha=0.5, c='blue', lw=2)
        text_line.CurvedText(
            x=[self.point1[0], self.point2[0]],
            y=[self.point1[1], self.point2[1]],
            text="File {}".format("%02d" %self.counterFilename),
            va='bottom',
            axes=self.ax[0],
            alpha=0.5,
            color="blue"
        )
        self.canvas.draw()

    #------------------------------------------------------------------
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.imageFileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", 
                "","PNG Files (*.png);;JPG Files (*.jpg);;All Files (*)", options=options)
        if self.imageFileName:
            self.displayImage()

    #------------------------------------------------------------------
    def exitCall(self):
        self.close()

    #------------------------------------------------------------------
    def aboutCall(self):
        msg = " StripesCounter " + version + """ 

         * Open an image with a scale and value scale
         * Enhance the image from brightness and contrast sliders
         * Double click to create a 1st point
         * Double click to create a 2nd point
         * A red line is drawn between the 2 previously defined points  
         * A profil along the line is drawn
         * Number of peaks (stripes) are counted from the smoothed profil
         * Move, modify the profil line if needed
         * Define new scale and scale value if needed

         * Developped by Patrick Brockmann (CEA/LSCE)
        """
        QMessageBox.about(self, "About the StripesCounter", msg.strip())

#------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit( app.exec_() )

