

#=================================================================
# Author: Patrick Brockmann CEA/DRF/LSCE - May 2022
#=================================================================

import sys, os

#======================================================
try: 
    import re

    from PyQt5.Qt import Qt
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
    
    import matplotlib
    matplotlib.use('Qt5Agg')
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    from matplotlib.figure import Figure
    from matplotlib.transforms import Bbox
    from matplotlib.collections import LineCollection
    import matplotlib.patches as patches
    import matplotlib.pyplot as plt
    
    from skimage.measure import profile_line
    import peakutils
    
    import numpy as np
    import cv2
    from shapely.geometry import Point, LineString

    import datetime
    import pandas as pd

    import cairo

except:
    print("Some modules have not been found:")
    print("---> re, matplotlib, PyQt5, skimage, peakutils, numpy, cv2, shapely")
    sys.exit()

#======================================================
version = "v11.60"
maximumWidth = 250

#======================================================
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

        self.cboxInverseImage = QCheckBox("Inverse image")
        self.cboxInverseImage.setChecked(False)
        self.cboxInverseImage.toggled.connect(self.toggled_cboxInverseImage)

        self.labelAlpha = QLabel("Contrast level: 1.0")
        self.labelAlpha.setAlignment(Qt.AlignLeft)
        self.labelBeta = QLabel("Brightness level: 0")
        self.labelBeta.setAlignment(Qt.AlignLeft)
        self.labelKernelSize = QLabel("Kernel size: " + str(self.kernelSize))
        self.labelKernelSize.setAlignment(Qt.AlignLeft)
        self.labelProfileLinewidth = QLabel("Profile linewidth: " + str(self.profileLinewidth))
        self.labelProfileLinewidth.setAlignment(Qt.AlignLeft)
        self.labelPeakUtils_minDist = QLabel("PeakUtils - Minimum distance: " + str(self.peakutils_minDist))
        self.labelPeakUtils_minDist.setAlignment(Qt.AlignLeft)
        self.labelPeakUtils_thres = QLabel("PeakUtils - Threshold: %d" % self.peakutils_thres)
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

        self.mySliderProfileLinewidth = QSlider(Qt.Horizontal, self)
        self.mySliderProfileLinewidth.setMaximumWidth(maximumWidth)
        self.mySliderProfileLinewidth.setMinimum(1)
        self.mySliderProfileLinewidth.setMaximum(50)
        self.mySliderProfileLinewidth.setValue(self.profileLinewidth)
        self.mySliderProfileLinewidth.setTickInterval(1)
        self.mySliderProfileLinewidth.setTickPosition(QSlider.TicksBelow)
        self.mySliderProfileLinewidth.valueChanged[int].connect(self.changeValueProfileLinewidth)

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
        self.mySliderPeakUtils_thres.setMinimum(0)
        self.mySliderPeakUtils_thres.setMaximum(255)
        self.mySliderPeakUtils_thres.setValue(self.peakutils_thres)
        self.mySliderPeakUtils_thres.setTickInterval(5)
        self.mySliderPeakUtils_thres.setTickPosition(QSlider.TicksBelow)
        self.mySliderPeakUtils_thres.valueChanged[int].connect(self.changeValuePeakUtils_thres)

        self.cboxPeaks = QCheckBox("Display peaks on current segment")
        self.cboxPeaks.setChecked(False)
        self.cboxPeaks.toggled.connect(self.toggled_cboxPeaks)

        self.cboxReverseProfile = QCheckBox("Reverse profile")
        self.cboxReverseProfile.setChecked(False)
        self.cboxReverseProfile.toggled.connect(self.toggled_cboxReverseProfile)

        #-----------------------
        self.fig = plt.figure(figsize=(8,8))
        self.ax0 = self.fig.add_axes([0.06, 0.40, 0.90, 0.52])   #  [left, bottom, width, height]
        self.ax1 = self.fig.add_axes([0.06, 0.12, 0.90, 0.22])

        self.canvas = FigureCanvas(self.fig)
        # https://github.com/matplotlib/matplotlib/issues/707/
        self.canvas.setFocusPolicy(Qt.ClickFocus)
        self.canvas.setFocus()

        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('pick_event', self.on_pick)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas.mpl_connect('scroll_event', self.zoom)

        #-----------------------
        self.buttonDefineScaleValue = QPushButton('Define scale value')
        self.buttonDefineScaleValue.setMaximumWidth(maximumWidth)
        self.buttonDefineScaleValue.clicked.connect(self.defineScaleValue)

        self.buttonDefineScaleLength = QPushButton('Define scale length')
        self.buttonDefineScaleLength.setMaximumWidth(maximumWidth)
        self.buttonDefineScaleLength.clicked.connect(self.defineScaleLength)

        self.buttonDefineScale = QPushButton('Define scale')
        self.buttonDefineScale.setMaximumWidth(maximumWidth)
        self.buttonDefineScale.clicked.connect(self.defineScale)

        self.buttonExtract = QPushButton('Extract peaks from profile')
        self.buttonExtract.setMaximumWidth(maximumWidth)
        self.buttonExtract.clicked.connect(self.extract)

        self.buttonLoad = QPushButton('Load segments and peaks')
        self.buttonLoad.setMaximumWidth(maximumWidth)
        self.buttonLoad.clicked.connect(self.load)

        self.buttonSave = QPushButton('Save segments and peaks')
        self.buttonSave.setMaximumWidth(maximumWidth)
        self.buttonSave.clicked.connect(self.save)

        self.buttonCapture = QPushButton('Capture displayed image')
        self.buttonCapture.setMaximumWidth(maximumWidth)
        self.buttonCapture.clicked.connect(self.capture)

        self.buttonDeleteLastSegment = QPushButton('Delete last segment')
        self.buttonDeleteLastSegment.setMaximumWidth(maximumWidth)
        self.buttonDeleteLastSegment.clicked.connect(self.deleteLastSegment)

        self.buttonSaveFullImage = QPushButton('Save image with segments and peaks')
        self.buttonSaveFullImage.setMaximumWidth(maximumWidth)
        self.buttonSaveFullImage.clicked.connect(self.saveFullImagePNG)

        layoutH = QHBoxLayout()

        layoutV1 = QVBoxLayout()
        layoutV1.addWidget(self.canvas)

        layoutV2 = QVBoxLayout()
        layoutV2.setAlignment(Qt.AlignTop)
        layoutV2.addWidget(self.cboxInverseImage)
        layoutV2.addSpacing(1)
        layoutV2.addWidget(self.labelAlpha)
        layoutV2.addWidget(self.mySliderAlpha)
        layoutV2.addSpacing(1)
        layoutV2.addWidget(self.labelBeta)
        layoutV2.addWidget(self.mySliderBeta)
        layoutV2.addSpacing(1)
        layoutV2.addWidget(self.labelKernelSize)
        layoutV2.addWidget(self.mySliderKernelSize)
        layoutV2.addSpacing(1)
        layoutV2.addWidget(self.labelProfileLinewidth)
        layoutV2.addWidget(self.mySliderProfileLinewidth)
        layoutV2.addSpacing(1)
        layoutV2.addWidget(self.labelPeakUtils_minDist)
        layoutV2.addWidget(self.mySliderPeakUtils_minDist)
        layoutV2.addSpacing(1)
        layoutV2.addWidget(self.labelPeakUtils_thres)
        layoutV2.addWidget(self.mySliderPeakUtils_thres)
        layoutV2.addWidget(self.cboxPeaks)
        layoutV2.addWidget(self.cboxReverseProfile)
        layoutV2.addSpacing(1)
        layoutV2.addWidget(self.buttonDefineScaleValue)
        layoutV2.addWidget(self.buttonDefineScaleLength)
        layoutV2.addWidget(self.buttonDefineScale)
        layoutV2.addSpacing(20)
        layoutV2.addWidget(self.buttonExtract)
        layoutV2.addWidget(self.buttonLoad)
        layoutV2.addWidget(self.buttonSave)
        layoutV2.addSpacing(20)
        layoutV2.addWidget(self.buttonCapture)
        layoutV2.addSpacing(20)
        layoutV2.addWidget(self.buttonDeleteLastSegment)
        layoutV2.addSpacing(20)
        layoutV2.addWidget(self.buttonSaveFullImage)

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
        self.alpha_default = 0.3

        self.line_object = None
        self.scale_object = None
        self.scaleValue_object = None

        self.scaleValue = 0.
        self.scaleLength = 0

        self.offset = [0,0]
        self.n = 0
        self.mousepress = None
        self.listLabelPoints = []

        self.current_artist = None
        self.press = False
        self.xpress = 0
        self.ypress = 0
        self.cur_xlim = 0
        self.cur_ylim = 0

        self.kernelSize = 3 
        self.kernelOffset = 0
        self.profileLinewidth = 1
        self.peakutils_minDist = 1
        self.peakutils_thres = 125 

        self.lineWithWidth = None
        self.dist_profile = None
        self.profile = None
        self.profile_convolved = None
        self.indexes = None
        self.peaksCurve = None
        self.peaks = None
        self.peakOver0 = None
        self.peakOver1 = None
        self.segmentNumb = 0
        self.segmentList = []
        self.segmentTextList = []
        self.peaksExtractedList = []
        self.peakExtractedOver0 = None
        self.peaksExtracted1 = None
        self.peakExtractedOver1 = None
        self.ticksCollectionList = []
        self.tickOver = None

        self.line1 = self.line2 = self.line3 = None
        self.counterFilename = 1

        self.radius = 25

    #------------------------------------------------------------------
    def initInterface(self):
        self.cboxInverseImage.setChecked(False)
        self.cboxInverseImage.setEnabled(False)
        self.labelAlpha.setEnabled(False)
        self.mySliderAlpha.setEnabled(False)
        self.labelBeta.setEnabled(False)
        self.mySliderBeta.setEnabled(False)
        self.labelKernelSize.setEnabled(False)
        self.mySliderKernelSize.setEnabled(False)
        self.labelProfileLinewidth.setEnabled(False)
        self.mySliderProfileLinewidth.setEnabled(False)
        self.labelPeakUtils_thres.setEnabled(False)
        self.mySliderPeakUtils_thres.setEnabled(False)
        self.labelPeakUtils_minDist.setEnabled(False)
        self.cboxPeaks.setEnabled(False)
        self.cboxReverseProfile.setEnabled(False)
        self.mySliderPeakUtils_minDist.setEnabled(False)
        self.cboxPeaks.setChecked(False)
        self.cboxReverseProfile.setChecked(False)
        self.buttonDefineScale.setEnabled(False)
        self.buttonDefineScaleValue.setEnabled(False)
        self.buttonDefineScaleLength.setEnabled(False)
        self.buttonCapture.setEnabled(False)
        self.buttonExtract.setEnabled(False)
        self.buttonSave.setEnabled(False)
        self.buttonLoad.setEnabled(False)
        self.buttonDeleteLastSegment.setEnabled(False)
        self.buttonSaveFullImage.setEnabled(False)

        self.mySliderKernelSize.setValue(self.kernelSize)
        self.mySliderProfileLinewidth.setValue(self.profileLinewidth)
        self.mySliderPeakUtils_minDist.setValue(self.peakutils_minDist)
        self.mySliderPeakUtils_thres.setValue(self.peakutils_thres)

        self.ax0.set_visible(False)
        self.ax1.set_visible(False)

    #------------------------------------------------------------------
    def changeValueAlpha(self, value):
        self.alphaLevel = value/10.
        self.labelAlpha.setText("Contrast level: " + str(self.alphaLevel))
        self.adjusted = cv2.convertScaleAbs(self.gray, alpha=self.alphaLevel, beta=self.betaLevel)
        self.image_object.set_data(self.adjusted)
        self.drawProfile()
        self.canvas.draw()

    #------------------------------------------------------------------
    def toggled_cboxInverseImage(self):
        self.gray = cv2.bitwise_not(self.gray)
        self.adjusted = cv2.convertScaleAbs(self.gray, alpha=self.alphaLevel, beta=self.betaLevel)
        self.image_object.set_data(self.adjusted)
        self.drawProfile()
        self.canvas.draw()

    #------------------------------------------------------------------
    def changeValueBeta(self, value):
        self.betaLevel = value
        self.labelBeta.setText("Brighness level: " + str(self.betaLevel))
        self.adjusted = cv2.convertScaleAbs(self.gray, alpha=self.alphaLevel, beta=self.betaLevel)
        self.image_object.set_data(self.adjusted)
        self.drawProfile()
        self.canvas.draw()

    #------------------------------------------------------------------
    def changeValueKernelSize(self, value):
        if value % 2 != 0:
            self.kernelSize = value
            self.labelKernelSize.setText("Kernel size: " + str(self.kernelSize))
            self.drawProfile()

    #------------------------------------------------------------------
    def changeValueProfileLinewidth(self, value):
        self.profileLinewidth= value
        self.labelProfileLinewidth.setText("Profile linewidth: " + str(self.profileLinewidth))
        self.update_lineWithWidth()
        self.canvas.draw()
        self.drawProfile()

    #------------------------------------------------------------------
    def changeValuePeakUtils_minDist(self, value):
        self.peakutils_minDist = value
        self.labelPeakUtils_minDist.setText("PeakUtils - Minimum distance: " + str(self.peakutils_minDist))
        self.drawProfile()
        
    #------------------------------------------------------------------
    def changeValuePeakUtils_thres(self, value):
        self.peakutils_thres = value
        self.labelPeakUtils_thres.setText("PeakUtils - Threshold: %d" % self.peakutils_thres)
        self.drawProfile()

    #------------------------------------------------------------------
    def toggled_cboxPeaks(self):
        self.drawProfile()

    #------------------------------------------------------------------
    def toggled_cboxReverseProfile(self):
        self.drawProfile()

    #------------------------------------------------------------------
    def zoom(self, event):
        if event.inaxes == self.ax0:              # to zoom and pan in ax[0]
            # https://stackoverflow.com/questions/11551049/matplotlib-plot-zooming-with-scroll-wheel
            scale_zoom = 1.2
            cur_xlim = self.ax0.get_xlim()
            cur_ylim = self.ax0.get_ylim()
            xdata = event.xdata # get event x location
            ydata = event.ydata # get event y location
            if event.button == 'up':
                # deal with zoom in
                scale_factor = 1 / scale_zoom
            elif event.button == 'down':
                # deal with zoom out
                scale_factor = scale_zoom
            else:
                # deal with something that should never happen
                scale_factor = 1
                #print(event.button)
            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
            relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata)/(cur_ylim[1] - cur_ylim[0])
            self.ax0.set_xlim([xdata - new_width * (1-relx), xdata + new_width * (relx)])
            self.ax0.set_ylim([ydata - new_height * (1-rely), ydata + new_height * (rely)])

            self.canvas.draw()

    #------------------------------------------------------------------
    def on_release(self, event):
        self.current_artist = None
        self.press = False
        if self.line_object != None:
            self.line_object.set_alpha(self.alpha_default)
        for p in list(self.ax0.patches):
            p.set_alpha(self.alpha_default)
        self.canvas.draw()

    #------------------------------------------------------------------
    def on_pick(self, event):

        if event.mouseevent.button == 3:
            self.mousepress = "right"
        elif event.mouseevent.button == 1:
            self.mousepress = "left"

        # https://stackoverflow.com/questions/29086662/matplotlib-pick-event-functionality
        # filter because the scroll wheel is registered as a button
        if event.mouseevent.button == 'down' or event.mouseevent.button == 'up':
            #print("pick", event.mouseevent.button)
            return

        if self.current_artist is None:
            self.current_artist = event.artist
            label = event.artist.get_label()
            #print("pick", label)
            if label == "Profile":
                 xdata = event.artist.get_xdata()
                 ydata = event.artist.get_ydata()
                 x1, y1 = event.mouseevent.xdata, event.mouseevent.ydata
                 self.offset = xdata[0] - x1, ydata[0] - y1
                 event.artist.set_alpha(1.0)
                 self.canvas.draw()
            elif label.startswith('Point'):
                 x0, y0 = self.current_artist.center
                 x1, y1 = event.mouseevent.xdata, event.mouseevent.ydata
                 self.offset = [(x0 - x1), (y0 - y1)]
                 event.artist.set_alpha(1.0)
                 self.canvas.draw()

    #------------------------------------------------------------------
    def clearPeaksOver(self):
        if self.peakOver0 != None:
            self.peakOver0.remove()
            self.peakOver0 = None
        if self.peakOver1 != None:
            self.peakOver1.remove()
            self.peakOver1 = None
        if self.peakExtractedOver0 != None:
            self.peakExtractedOver0.remove()
            self.peakExtractedOver0 = None
        if self.peakExtractedOver1 != None:
            self.peakExtractedOver1.remove()
            self.peakExtractedOver1 = None
        if self.tickOver != None:
            self.tickOver.remove()
            self.tickOver = None
        self.canvas.draw()

    #------------------------------------------------------------------
    def on_motion(self, event):

        self.clearPeaksOver()

        # display over scatter points when mouse passes over a peak
        cont = False
        if event.inaxes == self.ax0 and self.peaks != None and self.cboxPeaks.isChecked():
            cont, ind = self.peaks.contains(event)
        elif event.inaxes == self.ax1 and self.peaksCurve != None:
            cont, ind = self.peaksCurve.contains(event)
        if cont and self.peaks != None:
            i = ind["ind"][0]
            pos = self.peaks.get_offsets()[i]
            self.peakOver0 = self.ax0.scatter(pos[0], pos[1],
                                                 c='yellow', s=10, zorder=12)
            pos = self.peaksCurve.get_offsets()[i]
            self.peakOver1 = self.ax1.scatter(pos[0], pos[1],
                                                 c='yellow', s=200, edgecolors='b', lw=1, alpha=0.8, zorder=0)
            self.canvas.draw()

        #----------------------------------------------
        if event.inaxes == self.ax0 and len(self.peaksExtractedList) != 0 and self.line_object == None:
            offset = 0
            for n, peaksExtracted in enumerate(self.peaksExtractedList):
                cont, ind = peaksExtracted.contains(event)
                if cont:
                    i = ind["ind"][0]
                    pos = peaksExtracted.get_offsets()[i]
                    self.peakExtractedOver0 = self.ax0.scatter(pos[0], pos[1], marker='o', 
                                                      c='yellow', s=10, zorder=12)
                    pos = self.peaksExtracted1.get_offsets()[i+offset]
                    self.peakExtractedOver1 = self.ax1.scatter(pos[0], pos[1],
                                                      c='yellow', s=200, edgecolors='b', lw=1, alpha=0.8, zorder=0)
                    break
                offset = offset + len(peaksExtracted.get_offsets()) 
            self.canvas.draw()

        #----------------------------------------------
        if event.inaxes == self.ax1 and len(self.peaksExtractedList) != 0 and self.line_object == None:
            cont, ind = self.peaksExtracted1.contains(event)
            if cont:
                i = ind["ind"][0]
                pos = self.peaksExtracted1.get_offsets()[i]
                self.peakExtractedOver1 = self.ax1.scatter(pos[0], pos[1], marker='o', 
                                                  c='yellow', s=200, edgecolors='b', lw=1, alpha=0.8, zorder=0)
                peaksExtractedAllList = [sc.get_offsets() for sc in self.peaksExtractedList]  # all peaks as a unique list
                peaksExtractedAll = np.concatenate(peaksExtractedAllList)    
                self.peakExtractedOver0 = self.ax0.scatter(peaksExtractedAll[i][0], peaksExtractedAll[i][1], marker='o', 
                                                  c='yellow', s=10, zorder=12)
                self.canvas.draw()

        #----------------------------------------------
        if not self.press: return
        if event.xdata == None or event.ydata == None: return

        #----------------------------------------------
        if self.current_artist != None:
            label = self.current_artist.get_label()
            dx, dy = self.offset
            if label == "Profile":
                xdata = list(self.line_object.get_xdata())
                ydata = list(self.line_object.get_ydata())
                xdata0 = xdata[0]
                ydata0 = ydata[0]
                for i in range(0,len(xdata)): 
                    xdata[i] = event.xdata + dx + xdata[i] - xdata0
                    ydata[i] = event.ydata + dy + ydata[i] - ydata0 
                self.line_object.set_data(xdata, ydata)
                for p in list(self.ax0.patches):
                    pointLabel = p.get_label()
                    i = self.listLabelPoints.index(pointLabel) 
                    p.center = xdata[i], ydata[i]
            elif label.startswith('Point'):
                cx, cy =  event.xdata + dx, event.ydata + dy
                self.current_artist.center = cx, cy
                xdata = list(self.line_object.get_xdata())
                ydata = list(self.line_object.get_ydata())
                for i in range(0,len(xdata)): 
                    if self.listLabelPoints[i] == label:
                        xdata[i] = cx
                        ydata[i] = cy
                        break
                self.line_object.set_data(xdata, ydata)
            self.update_lineWithWidth()
            self.canvas.draw()
            self.drawProfile()
        elif event.inaxes == self.ax0:              # to zoom and pan in ax[0]
            dx = event.xdata - self.xpress
            dy = event.ydata - self.ypress
            self.cur_xlim -= dx
            self.cur_ylim -= dy
            self.ax0.set_xlim(self.cur_xlim)
            self.ax0.set_ylim(self.cur_ylim)
            self.canvas.draw()

    #------------------------------------------------------------------
    def on_press(self, event):
        self.clearPeaksOver()

        self.press = True
        if event.button == 3:
            self.mousepress = "right"
        elif event.button == 1:
            self.mousepress = "left"
        if event.inaxes == self.ax0:              # to zoom and pan in ax[0]
            self.cur_xlim = self.ax0.get_xlim()
            self.cur_ylim = self.ax0.get_ylim()
            self.xpress = event.xdata
            self.ypress = event.ydata
        if event and event.dblclick:
            if len(self.listLabelPoints) < 2:
                self.n = self.n+1
                x, y = event.xdata, event.ydata
                newPointLabel = "Point%d"%self.n
                point_object = patches.Circle([x, y], radius=self.radius, color='red', fill=False, lw=2,
                                              alpha=self.alpha_default, transform=self.ax0.transData, label=newPointLabel)
                point_object.set_picker(5)
                self.ax0.add_patch(point_object)
                self.listLabelPoints.append(newPointLabel)
                if len(self.listLabelPoints) == 2:
                    xdata = []
                    ydata = []
                    for p in list(self.ax0.patches):
                        cx, cy = p.center
                        xdata.append(cx)
                        ydata.append(cy)
                    self.line_object, = self.ax0.plot(xdata, ydata, alpha=self.alpha_default, c='red', lw=2, 
                                                        picker=True, pickradius=5, label="Profile")
                    self.update_lineWithWidth()
                self.canvas.draw()
                self.drawProfile()

        #----------------------------------------------
        if event.inaxes == self.ax0 and len(self.segmentList) != 0 and self.line_object == None:
           for n, segment in enumerate(self.segmentList):
               cont, ind = segment.contains(event)
               if cont:
                   if self.mousepress == "left":
                      xdata = list(segment.get_xdata())
                      ydata = list(segment.get_ydata())
                      line = LineString([(xdata[0], ydata[0]), (xdata[1], ydata[1])])
                      point = Point(event.xdata, event.ydata)
                      # Closest point on the line
                      newPoint = line.interpolate(line.project(point))
                      posPeaks = self.peaksExtractedList[n].get_offsets()
                      newPosPeaks = np.concatenate([posPeaks, np.array(newPoint.coords, ndmin=2)])
                      # Ticks
                      tick = self.drawTicks(line, [newPoint.coords[0][0]], [newPoint.coords[0][1]])
                      ticks = self.ticksCollectionList[n].get_segments()
                      ticks.append(tick[0])
                      # sort peaks along the segment after peak add
                      posDistance = []
                      for p in newPosPeaks:
                          distance = Point(xdata[0], ydata[0]).distance(Point(p))
                          posDistance.append(distance)
                      sortIndices = np.argsort(posDistance)
                      newPosPeaks = newPosPeaks[sortIndices]
                      self.peaksExtractedList[n].set_offsets(newPosPeaks)
                      newTicks = np.array(ticks)[sortIndices]
                      self.ticksCollectionList[n].set_segments(newTicks)
                      self.canvas.draw()
                      self.update_peaksExtractedPlot()
                   break

        #----------------------------------------------
        if event.inaxes == self.ax0 and len(self.peaksExtractedList) != 0 and self.line_object == None:
           for n, peaksExtracted in enumerate(self.peaksExtractedList):
               cont, ind = peaksExtracted.contains(event)
               if cont:
                   if self.mousepress == "right":
                      i = ind["ind"][0]
                      posPeaks = peaksExtracted.get_offsets()
                      ticks = self.ticksCollectionList[n].get_segments()
                      if len(posPeaks) > 2:
                          newPosPeaks = np.delete(posPeaks, i, axis=0)
                          self.peaksExtractedList[n].set_offsets(newPosPeaks)
                          del ticks[i]
                          self.ticksCollectionList[n].set_segments(ticks)
                          self.canvas.draw()
                          self.update_peaksExtractedPlot()
                   break

    #------------------------------------------------------------------
    def defineScalePixel(self):
        if self.scaleValue != 0. and self.scaleLength != 0:
            self.scalePixel = self.scaleValue / self.scaleLength
        else:
            self.scalePixel = 1

    #------------------------------------------------------------------
    def drawProfile(self):
        if self.line_object is None:
            return 

        self.defineScalePixel() 

        try:
            xdata = list(self.line_object.get_xdata())
            ydata = list(self.line_object.get_ydata())

            self.profile =  np.array([]) 
            self.profile_mx = np.array([])
            self.profile_my = np.array([])
            self.dist_profile = np.array([])

            self.profile = profile_line(self.adjusted, (ydata[0], xdata[0]), (ydata[1], xdata[1]),
                                        order=0, mode='constant', cval=0, linewidth=self.profileLinewidth)

            self.profile_mx = profile_line(self.mx, (ydata[0], xdata[0]), (ydata[1], xdata[1]),
                                        order=0, mode='constant', cval=0, linewidth=self.profileLinewidth)
            self.profile_my = profile_line(self.my, (ydata[0], xdata[0]), (ydata[1], xdata[1]),
                                        order=0, mode='constant', cval=0, linewidth=self.profileLinewidth)

            self.dist_profile = np.linspace(0, self.scalePixel*len(self.profile), num=len(self.profile))

            self.ax1.clear()
            self.ax1.set_facecolor('whitesmoke')
            self.ax1.set_visible(True)
            
            if self.cboxReverseProfile.isChecked():
            	self.profile = 255 - self.profile
            self.ax1.plot(self.dist_profile, self.profile, c='red', lw=1, alpha=0.8)

            self.ax1.axvline(x=0, linestyle='dashed', color='gray', alpha=0.8)
            self.ax1.axvline(x=self.dist_profile[-1], linestyle='dashed', color='gray', alpha=0.8)
            
            kernel = np.ones(self.kernelSize) / self.kernelSize
            self.kernelOffset = int(self.kernelSize/2)
            
            # use mode='same' and put boundaries values to np.nan
            self.profile_convolved = np.convolve(self.profile, kernel, mode='same')
            self.profile_convolved[0:self.kernelOffset] = self.profile_convolved[-self.kernelOffset:] = np.nan

            self.ax1.plot(self.dist_profile, self.profile_convolved, c='b', lw=1, alpha=0.8)
            
            # https://peakutils.readthedocs.io/en/latest/reference.html
            self.indexes = peakutils.indexes(self.profile_convolved, thres=self.peakutils_thres, thres_abs=True, min_dist=self.peakutils_minDist)
            self.peaksCurve = self.ax1.scatter(self.dist_profile[self.indexes], self.profile_convolved[self.indexes], c='b', s=10)

            if self.peaks != None:
                self.peaks.remove()
                self.peaks = None

            if self.cboxPeaks.isChecked():
            	line = LineString([(xdata[0], ydata[0]), (xdata[1], ydata[1])])
            	points = []
            	for i in self.indexes:
                	point = Point(self.profile_mx[i], self.profile_my[i])
                	# Closest point on the line
                	newPoint = line.interpolate(line.project(point))
                	points.append(newPoint)
            	xs = [point.x for point in points]
            	ys = [point.y for point in points]
            	self.peaks = self.ax0.scatter(xs, ys, c='b', s=5, zorder=10)
           
            peaksNb = len(self.indexes)
            self.line1 = "Number of peaks: %3d" %(peaksNb)
            if peaksNb > 1:
                stripesDist = self.dist_profile[self.indexes[-1]]-self.dist_profile[self.indexes[0]]
                self.line2 = "Length of stripes: %.5f  (first: %.5f, last: %.5f)" \
                                %(stripesDist, self.dist_profile[self.indexes[0]], self.dist_profile[self.indexes[-1]])
                self.line3 = "Growth stripe rate (unit/stripe): %.5f" %(stripesDist/(peaksNb-1))
                self.ax1.set_title(self.line1 + '\n' + self.line2 + '\n' + self.line3, y=-0.55, loc='left', fontsize=10)
            else:
                self.ax1.set_title(self.line1 + '\n\n', y=-0.55, loc='left', fontsize=10)
         
            self.ax1.grid(linestyle='dotted')
            self.ax1.axhline(self.peakutils_thres, color="b", lw=1, linestyle='solid', alpha=0.8)
            self.ax1.yaxis.set_visible(True)

            self.labelKernelSize.setEnabled(True)
            self.mySliderKernelSize.setEnabled(True)
            self.labelProfileLinewidth.setEnabled(True)
            self.mySliderProfileLinewidth.setEnabled(True)
            self.labelPeakUtils_minDist.setEnabled(True)
            self.mySliderPeakUtils_minDist.setEnabled(True)
            self.labelPeakUtils_thres.setEnabled(True)
            self.mySliderPeakUtils_thres.setEnabled(True)
            self.cboxPeaks.setEnabled(True)
            self.cboxReverseProfile.setEnabled(True)
            self.buttonDefineScaleValue.setEnabled(True)
            self.buttonDefineScaleLength.setEnabled(True)
            self.buttonDefineScale.setEnabled(True)
            self.buttonExtract.setEnabled(True)

            self.canvas.draw()

        except:
            #print("Error in drawProfile")
            return 

    #------------------------------------------------------------------
    def drawTicks(self, line, x, y, length=5):
        left = line.parallel_offset(length, 'left')
        right0 = line.parallel_offset(length, 'right')
        right = LineString([right0.boundary.geoms[1], right0.boundary.geoms[0]]) # flip because 'right' orientation
        ticks = []
        for i in range(len(x)):
            p = Point(x[i],y[i])
            a = left.interpolate(line.project(p))
            b = right.interpolate(line.project(p))
            ticks.append(LineString([a, p, b]).coords)           # keep p point to sort from distance later
        return ticks

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
                    point1Scale = pt1
                    point2Scale = pt2
            #print("Detected scale length in pixel: ", scaleLength)

            if self.scaleLength > 0:
                self.scale_object, = self.ax0.plot([point1Scale[0], point2Scale[0]],
                                                    [point1Scale[1], point2Scale[1]],
                                                    alpha=1.0, c='purple', lw=2)
        except:
            self.scaleLength = 0

        try:
            self.scaleValue_object = self.ax0.text(
                min(point1Scale[0], point2Scale[0]),
                min(point1Scale[1], point2Scale[1]),
                "   %.3f mm" %(self.scaleValue),
                alpha=1.0, c='purple', horizontalalignment='left', verticalalignment='bottom', clip_on=True)
        except:
            self.scaleValue_object = self.ax0.text(
                200, 200,                               # Set a default scaleValue_object at 200,200
                "   %.3f mm" %(self.scaleValue),
                alpha=1.0, c='purple', horizontalalignment='left', verticalalignment='bottom', clip_on=True)

        try:
            import pytesseract

            scaleDetected = pytesseract.image_to_string(self.mask)
            matchObj = re.match(r'[^0-9]*([0-9]*)mm', scaleDetected.strip())
            self.scaleValue = float(matchObj.group(1))
            #print("Detected scale value: ", self.scaleValue)
            self.scaleValue_object.set_text("  %.3f mm" %(self.scaleValue))

        except:
            self.scaleValue = 0.

    #------------------------------------------------------------------
    def defineScaleValue(self):
        dialog = QInputDialog()
        dialog.setInputMode(QInputDialog.DoubleInput)
        dialog.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        dialog.setLabelText("Value: ")
        dialog.setDoubleMinimum(0)
        dialog.setDoubleMaximum(100)
        dialog.setIntStep(1)
        dialog.setDoubleDecimals(3)
        dialog.setDoubleValue(self.scaleValue)
        dialog.setWindowTitle("Get scale value")
        okPressed = dialog.exec_()
        if okPressed:
            self.scaleValue = dialog.doubleValue()
        else:
            return

        self.ax0.set_title(os.path.basename(self.imageFileName) + '\n'
            + "          Scale length [pixels]: %s" %(self.scaleLength) + '\n'
            + "          Scale value [mm]: %.3f" %(self.scaleValue),
            loc='left', fontsize=10)
        self.scaleValue_object.set_text("   %.3f mm" %(self.scaleValue))
        self.drawProfile()

    #------------------------------------------------------------------
    def defineScaleLength(self):
        dialog = QInputDialog()
        dialog.setInputMode(QInputDialog.DoubleInput)
        dialog.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        dialog.setLabelText("Length: ")
        dialog.setDoubleMinimum(0)
        dialog.setDoubleMaximum(10000)
        dialog.setIntStep(1)
        dialog.setDoubleDecimals(0)
        dialog.setDoubleValue(self.scaleLength)
        dialog.setWindowTitle("Get scale length")
        okPressed = dialog.exec_()
        if okPressed:
            self.scaleLength = dialog.doubleValue()
        else:
            return

        if self.scale_object != None:
            self.scale_object.remove()
            self.scale_object = None

        self.ax0.set_title(os.path.basename(self.imageFileName) + '\n'
            + "          Scale length [pixels]: %s" %(self.scaleLength) + '\n'
            + "          Scale value [mm]: %.3f" %(self.scaleValue),
            loc='left', fontsize=10)
        self.scaleValue_object.set_text("   %.3f mm" %(self.scaleValue))
        self.drawProfile()

    #------------------------------------------------------------------
    def defineScale(self):
        xdata = self.line_object.get_xdata()
        ydata = self.line_object.get_ydata()
        point1Scale = [xdata[0], ydata[0]]              # Scale from the 1st segment
        point2Scale = [xdata[1], ydata[1]]
        self.scaleLength = int(np.linalg.norm(np.array(point1Scale) - np.array(point2Scale)))
        self.ax0.set_title(os.path.basename(self.imageFileName) + '\n' 
            + "          Scale length [pixels]: %s" %(self.scaleLength) + '\n'
            + "          Scale value [mm]: %.3f" %(self.scaleValue),
            loc='left', fontsize=10)
        if self.scale_object == None:
            self.scale_object, = self.ax0.plot([point1Scale[0], point2Scale[0]], 
                                                [point1Scale[1], point2Scale[1]],
                                                alpha=1.0, c='purple', lw=2)
        else:
            self.scale_object.set_data([point1Scale[0], point2Scale[0]],
                                          [point1Scale[1], point2Scale[1]])
        self.scaleValue_object.set_position((point1Scale[0], point1Scale[1]))
        self.drawProfile()

    #------------------------------------------------------------------
    def update_lineWithWidth(self):
        if self.lineWithWidth != None:
            self.lineWithWidth.remove()
            self.lineWithWidth = None
        if self.profileLinewidth > 1:
            xdata = list(self.line_object.get_xdata())
            ydata = list(self.line_object.get_ydata())
            line = LineString([(xdata[0], ydata[0]), (xdata[1], ydata[1])])
            dilated = line.buffer(self.profileLinewidth/2., cap_style=2, join_style=1)
            self.lineWithWidth, = self.ax0.plot(*dilated.exterior.xy, alpha=self.alpha_default, c='red', lw=2)
        
    #------------------------------------------------------------------
    def update_peaksExtractedPlot(self):
        self.ax1.set_visible(True)
        self.ax1.clear()
        self.ax1.grid(linestyle='dotted')
        self.ax1.set_facecolor('whitesmoke')
        self.ax1.yaxis.set_visible(False)
        self.ax1.axvline(x=0, linestyle='dashed', color='gray', alpha=0.8)
        self.ax1.set_ylim(-5,5)

        lengthPeaks = []
        for n, peaksExtracted in enumerate(self.peaksExtractedList):
            posPeaks = peaksExtracted.get_offsets()

            if len(lengthPeaks) == 0:
                lengthPeaks.append(0)
            else:
                lengthPeaks.append(lengthPeaks[-1])     # segments are contiguous

            self.ax1.axvline(x=lengthPeaks[-1], linestyle='dashed', color='gray', alpha=0.8)
            self.ax1.text(lengthPeaks[-1], -3, 'S%02d'%(n+1), clip_on=True, alpha=0.8, color='b')
            for i in range(0, len(posPeaks)-1):
                distance = Point(posPeaks[i]).distance(Point(posPeaks[i+1])) * self.scalePixel
                lengthPeaks.append(lengthPeaks[-1] + distance)
            self.ax1.axvline(x=lengthPeaks[-1], linestyle='dashed', color='gray', alpha=0.8)

        self.ax1.plot(lengthPeaks, [0]*len(lengthPeaks), marker='o', c='b', alpha=self.alpha_default, markersize=5)
        self.peaksExtracted1 = self.ax1.scatter(lengthPeaks, [0]*len(lengthPeaks), marker='o', c='b', alpha=self.alpha_default, s=5)

        peaksNb = len(lengthPeaks)
        self.line1 = "Number of peaks: %3d" %(peaksNb)
        if peaksNb > 1:
            self.line2 = "Total length: %.5f"%(lengthPeaks[-1] )
            self.line3 = "Growth stripe rate (unit/stripe): %.5f" %(lengthPeaks[-1]/(peaksNb-1))
            self.ax1.set_title(self.line1 + '\n' + self.line2 + '\n' + self.line3, y=-0.55, loc='left', fontsize=10)
        else:
            self.ax1.set_title(self.line1 + '\n\n', y=-0.55, loc='left', fontsize=10)
        
        self.canvas.draw()

    #------------------------------------------------------------------
    def displayImage(self):
        self.initValues()
        self.initInterface()

        self.ax0.clear()
        self.ax0.set_visible(True)

        self.image = cv2.imread(self.imageFileName)
        (self.mx, self.my) = np.meshgrid(np.arange(self.image.shape[1]), np.arange(self.image.shape[0]))
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        mask0 = cv2.inRange(self.gray, 0, 0)
        self.mask = cv2.bitwise_not(mask0)
        self.alphaLevel =  self.mySliderAlpha.value()/10.
        self.betaLevel = self.mySliderBeta.value()
        self.adjusted = cv2.convertScaleAbs(self.gray, alpha=self.alphaLevel, beta=self.betaLevel)
        self.image_object = self.ax0.imshow(self.adjusted, cmap='gray', aspect='equal')
        self.ax0.set_adjustable('datalim')
        self.detectScale()

        self.ax0.set_title(os.path.basename(self.imageFileName) + '\n'
            + "          Scale length [pixels]: %s" %(self.scaleLength) + '\n'
            + "          Scale value [mm]: %.3f" %(self.scaleValue),
            loc='left', fontsize=10)

        self.cboxInverseImage.setEnabled(True)
        self.labelAlpha.setEnabled(True)
        self.mySliderAlpha.setEnabled(True)
        self.labelBeta.setEnabled(True)
        self.mySliderBeta.setEnabled(True)
        self.buttonLoad.setEnabled(True)
        self.buttonCapture.setEnabled(True)
        self.buttonSaveFullImage.setEnabled(True)

        self.canvas.draw()

    #------------------------------------------------------------------
    def capture(self):
        base=os.path.basename(self.imageFileName)
        file1Name = os.path.splitext(base)[0] + "_StripesCounterFile_capture_{}.png"
        while os.path.isfile(file1Name.format("%02d" %self.counterFilename)):
            self.counterFilename += 1
        file1NamePNG = file1Name.format("%02d" %self.counterFilename)

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file1NamePNG, _ = QFileDialog.getSaveFileName(self, "Capture displayed image",
                file1NamePNG, "PNG Files (*.png)", options=options)
        if file1NamePNG == "": return

        bbox = self.ax0.get_tightbbox(self.fig.canvas.get_renderer())
        bbox = Bbox([[0.0, 2.6], [8.2, 7.6]])
        plt.savefig(file1NamePNG, bbox_inches=bbox)

        #print("Saved png file: " + file1NamePNG)
        
    #------------------------------------------------------------------
    def saveFullImagePNG(self):
        base=os.path.basename(self.imageFileName)
        file1Name = os.path.splitext(base)[0] + "_StripesCounterFile_image_{}.png"
        while os.path.isfile(file1Name.format("%02d" %self.counterFilename)):
            self.counterFilename += 1
        file1NamePNG = file1Name.format("%02d" %self.counterFilename)

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file1NamePNG, _ = QFileDialog.getSaveFileName(self, "Save image with segments and peaks",
                file1NamePNG, "PNG Files (*.png)", options=options)
        if file1NamePNG == "": return

        overlay = self.image.copy()

        fontFace = cv2.FONT_HERSHEY_SIMPLEX
        fontSize = 1
        fontThickness = 1
        for n,segment in enumerate(self.segmentList):
             xdata = list(segment.get_xdata())
             ydata = list(segment.get_ydata())
             x0 = round(xdata[0])
             y0 = round(ydata[0])
             x1 = round(xdata[1])
             y1 = round(ydata[1])
             cv2.line(overlay, pt1=(x0, y0), pt2=(x1, y1), color=(255,0,0),
                      thickness=1, lineType=cv2.LINE_AA)
             text = 'S%02d'%(n+1)
             textsize = cv2.getTextSize(text, fontFace, fontSize, fontThickness)[0]
             offset = (-1 if (y1-y0 >= 0) else 1)*20
             cv2.putText(overlay, text, (round(x0 - textsize[0]/2) , round(y0 + textsize[1]/2) + offset), 
                    fontFace, fontSize, (255, 0, 0), fontThickness, cv2.LINE_AA) 

        for ticksCollection in self.ticksCollectionList:
             ticks = ticksCollection.get_segments()
             for n,t in enumerate(ticks):
                 x0 = round(t[0][0])
                 y0 = round(t[0][1])
                 x1 = round(t[2][0])        # get bounds of the tick
                 y1 = round(t[2][1])
                 if n == 0 or n == len(ticks)-1:
                     color = (255,255,0)
                 else:
                     color = (255,0,0)
                 cv2.line(overlay, pt1=(x0, y0), pt2=(x1, y1), color=color,
                       thickness=1, lineType=cv2.LINE_AA)

        # dst = src1*alpha + src2*beta + gamma
        #alpha = 0.6
        alpha = 1.0             # no alpha on segments and peaks over the original image
        image = cv2.addWeighted(overlay, alpha, self.image, 1-alpha, 0)
        cv2.imwrite(file1NamePNG, image)

    #------------------------------------------------------------------
    def saveFullImageSVG(self):
        base=os.path.basename(self.imageFileName)
        file1Name = os.path.splitext(base)[0] + "_StripesCounterFile_image_{}.svg"
        while os.path.isfile(file1Name.format("%02d" %self.counterFilename)):
            self.counterFilename += 1
        file1NameSVG = file1Name.format("%02d" %self.counterFilename)

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file1NameSVG, _ = QFileDialog.getSaveFileName(self, "Save image with segments and peaks",
                file1NameSVG, "SVG Files (*.svg)", options=options)
        if file1NameSVG == "": return

        with cairo.SVGSurface(file1NameSVG, self.image.shape[1], self.image.shape[0]) as surface:
             context = cairo.Context(surface)
             context.set_line_width(2)
             context.set_source_rgba(0, 0, 1, 1)
             context.set_font_size(14)
             context.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
             for n,segment in enumerate(self.segmentList):
                  xdata = list(segment.get_xdata())
                  ydata = list(segment.get_ydata())
                  x0 = xdata[0]
                  y0 = ydata[0]
                  x1 = xdata[1]
                  y1 = ydata[1]
                  context.move_to(x0, y0)
                  context.line_to(x1, y1)
                  text = 'S%02d'%(n+1)
                  x_bearing, y_bearing, width, height, x_advance, y_advance = context.text_extents(text)
                  offset = (-1 if (y1-y0 >= 0) else 1)*20
                  context.move_to(x0 - (width/2 + x_bearing) , y0 - (height/2 + y_bearing) + offset) 
                  context.show_text(text)
                  context.stroke()

             for ticksCollection in self.ticksCollectionList:
                  ticks = ticksCollection.get_segments()
                  for n,t in enumerate(ticks):
                      x0 = t[0][0]
                      y0 = t[0][1]
                      x1 = t[2][0]        # get bounds of the tick
                      y1 = t[2][1]
                      if n == 0 or n == len(ticks)-1:
                          context.set_source_rgba(0, 1, 1, 1)
                      else:
                          context.set_source_rgba(0, 0, 1, 1)
                      context.move_to(x0, y0)
                      context.line_to(x1, y1)
                      context.stroke()

        print("Saved svg file: " + file1NameSVG)

    #------------------------------------------------------------------
    def appendSegmentAndPeaks(self, x, y):
        self.segmentNumb +=1
        segment, = self.ax0.plot([x[0], x[-1]], [y[0], y[-1]], c='b', lw=2, alpha=self.alpha_default, zorder=10,
                                      label='Segment%02d'%self.segmentNumb)
        self.segmentList.append(segment)
        peaksExtracted = self.ax0.scatter(x, y, c='b', marker='o', s=10, zorder=12, alpha=self.alpha_default,
                                               label='PeaksSegment%02d'%self.segmentNumb)
        self.peaksExtractedList.append(peaksExtracted)

        # ticks
        line = LineString([(x[0], y[0]), (x[-1], y[-1])])
        ticks = self.drawTicks(line, x, y)
        ticksCollection = LineCollection(ticks, color='b', alpha=self.alpha_default)
        self.ticksCollectionList.append(ticksCollection)
        self.ax0.add_collection(ticksCollection)

        #dx = x[-1] - x[0]
        #dy = y[-1] - y[0]
        #angle = np.rad2deg(np.arctan2(dy, dx))
        #right = line.parallel_offset(10, 'right')
        #text = self.ax0.text(right.boundary.geoms[1].xy[0][0], right.boundary.geoms[1].xy[1][0], 
        #         'S%02d'%self.segmentNumb, ha='left', va='bottom', fontsize=12,
        #         transform_rotates_text=True, rotation=angle, rotation_mode='anchor', clip_on=True,
        #         alpha=self.alpha_default, color='b')
        offset = (-1 if (y[-1]-y[0] >= 0) else 1)*20
        text = self.ax0.text(x[0], y[0] + offset, 
                 'S%02d'%self.segmentNumb, ha='center', va='center', fontsize=12,
                 clip_on=True, alpha=self.alpha_default, color='b')
        self.segmentTextList.append(text)

    #------------------------------------------------------------------
    def extract(self):
        if len(self.indexes) < 2:       # if not at least 2 peaks (cannot draw segment)
            return

        xdata = list(self.line_object.get_xdata())
        ydata = list(self.line_object.get_ydata())
        line = LineString([(xdata[0], ydata[0]), (xdata[1], ydata[1])])
        points = []
        for i in self.indexes:
            point = Point(self.profile_mx[i], self.profile_my[i])
            # Closest point on the line
            newPoint = line.interpolate(line.project(point))
            points.append(newPoint)

        line = LineString(points)
        x, y = line.xy
        self.appendSegmentAndPeaks(x, y)

        self.line_object.remove()
        self.line_object = None
        if self.lineWithWidth != None:
            self.lineWithWidth.remove()
            self.lineWithWidth = None
        if self.peaks != None:
            self.peaks.remove()
            self.peaks = None
        for p in list(self.ax0.patches):
            p.remove()
        self.listLabelPoints = []
        self.n = 0
        self.buttonExtract.setEnabled(False)

        self.update_peaksExtractedPlot()

        self.labelKernelSize.setEnabled(False)
        self.mySliderKernelSize.setEnabled(False)
        self.labelProfileLinewidth.setEnabled(False)
        self.mySliderProfileLinewidth.setEnabled(False)
        self.labelPeakUtils_minDist.setEnabled(False)
        self.mySliderPeakUtils_minDist.setEnabled(False)
        self.labelPeakUtils_thres.setEnabled(False)
        self.mySliderPeakUtils_thres.setEnabled(False)
        self.cboxPeaks.setEnabled(False)
        self.cboxReverseProfile.setEnabled(False)
        self.buttonDefineScaleValue.setEnabled(False)
        self.buttonDefineScaleLength.setEnabled(False)
        self.buttonDefineScale.setEnabled(False)

        self.buttonDeleteLastSegment.setEnabled(True)
        self.buttonSave.setEnabled(True)

    #------------------------------------------------------------------
    def load(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        File1NameCSV, _ = QFileDialog.getOpenFileName(self, "Load segments and peaks", 
                "","CSV Files (*.csv);;", options=options)
        if File1NameCSV == "": return

        try:
            df = pd.read_csv(File1NameCSV, skiprows=8)
       
            # Read header to get scaleValue and scaleLength
            df1 = pd.read_csv(File1NameCSV, header=None, skiprows=5, nrows=1)
            self.scaleValue = float(df1[0].values[0].split(':')[1])
            df1 = pd.read_csv(File1NameCSV, header=None, skiprows=6, nrows=1)
            self.scaleLength = int(float(df1[0].values[0].split(':')[1]))
            self.defineScalePixel() 

            if self.scale_object != None:
                self.scale_object.remove()
                self.scale_object = None

            self.ax0.set_title(os.path.basename(self.imageFileName) + '\n'
                + "          Scale length [pixels]: %s" %(self.scaleLength) + '\n'
                + "          Scale value [mm]: %.3f" %(self.scaleValue),
                loc='left', fontsize=10)
            self.scaleValue_object.set_text("   %.3f mm" %(self.scaleValue))

            for i in df['segment'].unique():
                x = df[df['segment'] == i]['xPixel'].to_list()
                y = df[df['segment'] == i]['yPixel'].to_list()
                self.appendSegmentAndPeaks(x, y)

            self.update_peaksExtractedPlot()

            self.buttonSave.setEnabled(True)
            self.buttonDeleteLastSegment.setEnabled(True)

        except:
            msgBox = QMessageBox(self)
            msgBox.setTextFormat(Qt.RichText)
            msgBox.setText("Problem when reading csv file :<br>" + File1NameCSV)
            msgBox.setWindowTitle("Load message")
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec()

    #------------------------------------------------------------------
    def save(self):
        base=os.path.basename(self.imageFileName)
        file1Name = os.path.splitext(base)[0] + "_StripesCounterFile_{}.csv"
        while os.path.isfile(file1Name.format("%02d" %self.counterFilename)):
            self.counterFilename += 1
        file1NameCSV = file1Name.format("%02d" %self.counterFilename)

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file1NameCSV, _ = QFileDialog.getSaveFileName(self, "Save segments and peaks",
                file1NameCSV, "CSV Files (*.csv)", options=options)
        if File1NameCSV == "": return

        overlay = self.image.copy()
        date = datetime.datetime.now().strftime("%Y/%m/%d at %X")

        file1 = open(file1NameCSV, "w")
        file1.write("#================================================\n")
        file1.write("# StripesCounter " + version + "\n")
        file1.write("# Date: " + date + "\n")
        file1.write("# File: %s\n" %(base))
        file1.write("# Number of segments: %d\n"%(self.segmentNumb))
        file1.write("# Scale value [mm]: %.3f\n" %(self.scaleValue))
        file1.write("# Scale length [pixels]: %d\n" %(self.scaleLength))
        file1.write("#================================================\n")

        file1.write("n,xPixel,yPixel,segment,peakNumbInSegment,distanceInSegment,distanceCumulated,stripeLength\n")
        n = 1
        distancePrevious = distanceCumulated = 0
        for s, peaksExtracted in enumerate(self.peaksExtractedList):
            posPeaks = peaksExtracted.get_offsets()
            x0, y0 = posPeaks[0]
            for i, p in enumerate(posPeaks):
                x, y = p
                distance = Point(x0, y0).distance(Point(p)) * self.scalePixel
                if (distance == 0): 
                    stripeLength = 0
                else:
                    stripeLength = distance - distancePrevious
                distanceCumulated += stripeLength
                file1.write('%05d,%014.7f,%014.7f,%03d,%03d,%014.7f,%014.7f,%014.7f\n'%(n, x, y, s+1, i+1, distance, distanceCumulated, stripeLength))
                distancePrevious = distance
                n += 1

        file1.close()

        #print("Saved csv file: " + file1NameCSV)
        
    #------------------------------------------------------------------
    def deleteLastSegment(self):
        self.segmentList[-1].remove()
        self.segmentTextList[-1].remove()
        self.peaksExtractedList[-1].remove()
        self.ticksCollectionList[-1].remove()
        self.canvas.draw()

        del self.peaksExtractedList[-1]
        del self.ticksCollectionList[-1]
        del self.segmentList[-1]
        del self.segmentTextList[-1]
        self.segmentNumb -=1

        self.update_peaksExtractedPlot()

        if len(self.segmentList) == 0:
            self.ax1.set_visible(False)
            self.ax1.clear()
            self.canvas.draw()
            self.buttonDeleteLastSegment.setEnabled(False)
            self.buttonSave.setEnabled(False)

    #------------------------------------------------------------------
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.imageFileName, _ = QFileDialog.getOpenFileName(self, "Load image", 
                "","PNG, JPG, TIF Files (*.png *.jpg *.tif);;PNG Files (*.png);;JPG Files (*.jpg);;TIF Files (*.tif);;All Files (*)", options=options)
        if self.imageFileName:
            self.displayImage()

    #------------------------------------------------------------------
    def exitCall(self):
        self.close()

    #------------------------------------------------------------------
    def aboutCall(self):
        msg = "<h4>StripesCounter " + version + "</h4>" + """ 

Here are the different steps :
<ul>
<li>Open an image, optionnaly with a scale and value scale annotation.
<li>Pan the image from a mouse click.
<li>Zoom in or out with wheel zoom (or 2 fingers pad actions).
<li>Enhance the image from brightness and contrast sliders.
<li>Create a profile segment by double clicking to create control points.
<li>After the 2nd point created, the profile to be extracted is drawn as a red segment. 
<li>The segment can be modified (moved, shifted) by pressing the segment itself 
or its start or end control points.
<li>An intensity profile is extracted from the the image along the profile segment.
<li>Number of peaks are counted from the smoothed profile.
<li>Adapt various parameters for peaks detection and profile smoothing. 
<li>Control the width of the profile segment to integrate. 
<li>Inspect detected peaks with a mouse over from the image or the profile. 
<li>Define new scale and scale value if needed.
<li>Extract the peaks
<li>Modify the extracted peaks by clicking on peaks :
     <ul>
     <li>right click on segment to add a peak,
     <li>left click on a peak to delete it.
     </ul>
<li>Add a new profile segment and repeat the process.
<li>Extracted peaks are considered from contiguous segments. 
<li>Save the "peaks and stripes" in a csv file.
<li>Reload a saved "peaks and stripes" csv file.
<li>Capture the image displayed in the application.
<li>Save the original image with segments and peaks.
</ul>

Developped by Patrick Brockmann (LSCE)
"""

        msgBox = QMessageBox(self)
        msgBox.setTextFormat(Qt.RichText)
        msgBox.setText(msg)
        msgBox.setWindowTitle("About the StripesCounter")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()

#======================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit( app.exec_() )

