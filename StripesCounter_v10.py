#!/usr/bin/env python

#=================================================================
# Author: Patrick Brockmann CEA/DRF/LSCE - April 2021
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
    import matplotlib.patches as patches
    from matplotlib.lines import Line2D
    import matplotlib.pyplot as plt
    
    from skimage.measure import profile_line
    import peakutils
    
    import numpy as np
    import cv2
    from shapely.geometry import Point, LineString
    
    import text_line

except:
    print("Some modules have not been found:")
    print("---> re, matplotlib, PyQt5, skimage, peakutils, numpy, cv2, shapely")
    sys.exit()

#======================================================
version = "v10.93"
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

        self.cboxPeaks = QCheckBox("Display peaks on current profile")
        self.cboxPeaks.setChecked(False)
        self.cboxPeaks.toggled.connect(self.toggled_cboxPeaks)

        self.cboxReverseProfile = QCheckBox("Reverse profile")
        self.cboxReverseProfile.setChecked(False)
        self.cboxReverseProfile.toggled.connect(self.toggled_cboxReverseProfile)

        #-----------------------
        #self.fig, self.ax = plt.subplots(nrows=2, figsize=(8,8), gridspec_kw={'height_ratios': [2, 1]})
        self.fig, self.ax = plt.subplots(nrows=2, figsize=(8,8))
        self.fig.tight_layout()
        self.fig.subplots_adjust(top=0.9, bottom=0.15)

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
        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        #self.toolbar = NavigationToolbar(self.canvas, self)
        #self.toolbar.pan()

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
        #layoutV1.addWidget(self.toolbar)

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
        self.alpha_default = 0.3

        self.line_object = None
        self.lineWithWidthList = []
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

        self.dist_profile = None
        self.profile = None
        self.profile_convolved = None
        self.indexes = None
        self.peaksCurve = None
        self.peaks = None
        self.peakHover0 = None
        self.peakHover1 = None

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
        self.buttonSave.setEnabled(False)

        self.mySliderKernelSize.setValue(self.kernelSize)
        self.mySliderProfileLinewidth.setValue(self.profileLinewidth)
        self.mySliderPeakUtils_minDist.setValue(self.peakutils_minDist)
        self.mySliderPeakUtils_thres.setValue(self.peakutils_thres)

        self.ax[0].set_visible(False)
        self.ax[1].set_visible(False)

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
        self.update_lineWithWidthList()
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
        if event.inaxes == self.ax[0]:              # to zoom and pan in ax[0]
            # https://stackoverflow.com/questions/11551049/matplotlib-plot-zooming-with-scroll-wheel
            scale_zoom = 1.2
            cur_xlim = self.ax[0].get_xlim()
            cur_ylim = self.ax[0].get_ylim()
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
            self.ax[0].set_xlim([xdata - new_width * (1-relx), xdata + new_width * (relx)])
            self.ax[0].set_ylim([ydata - new_height * (1-rely), ydata + new_height * (rely)])

            self.canvas.draw()

    #------------------------------------------------------------------
    def on_release(self, event):
        self.current_artist = None
        self.press = False
        if self.line_object != None:
            self.line_object.set_alpha(self.alpha_default)
        for p in list(self.ax[0].patches):
            p.set_alpha(self.alpha_default)
        self.canvas.draw()

    #------------------------------------------------------------------
    def on_pick(self, event):

        # https://stackoverflow.com/questions/29086662/matplotlib-pick-event-functionality
        # filter because the scroll wheel is registered as a button
        if event.mouseevent.button == 'down' or event.mouseevent.button == 'up':
            #print("pick", event.mouseevent.button)
            return

        if self.current_artist is None:
            self.current_artist = event.artist
            #print("pick ", self.current_artist)
            if isinstance(event.artist, patches.Circle):
                if event.mouseevent.dblclick:
                    if self.mousepress == "right":
                        #print("double click right")
                        if len(self.ax[0].patches) > 2:
                            #print("\ndelete", event.artist.get_label())
                            event.artist.remove()
                            xdata = list(self.line_object.get_xdata())
                            ydata = list(self.line_object.get_ydata())
                            for i in range(0,len(xdata)):
                                if event.artist.get_label() == self.listLabelPoints[i]:
                                    xdata.pop(i) 
                                    ydata.pop(i) 
                                    self.listLabelPoints.pop(i)
                                    break
                            #print('--->', self.listLabelPoints)
                            self.line_object.set_data(xdata, ydata)
                            self.update_lineWithWidthList()
                            self.drawProfile()
                            self.canvas.draw()
                else:
                    x0, y0 = self.current_artist.center
                    x1, y1 = event.mouseevent.xdata, event.mouseevent.ydata
                    self.offset = [(x0 - x1), (y0 - y1)]
                    event.artist.set_alpha(1.0)
                    self.canvas.draw()
            elif isinstance(event.artist, Line2D):
                if event.mouseevent.dblclick:
                    if self.mousepress == "left":
                        #print("double click left")
                        self.n = self.n+1
                        x, y = event.mouseevent.xdata, event.mouseevent.ydata
                        newPointLabel = "point"+str(self.n)
                        point_object = patches.Circle([x, y], radius=self.radius, color='red', fill=False, lw=2,
                                alpha=self.alpha_default, transform=self.ax[0].transData, label=newPointLabel)
                        point_object.set_picker(5)
                        self.ax[0].add_patch(point_object)
                        xdata = list(self.line_object.get_xdata())
                        ydata = list(self.line_object.get_ydata())
                        #print('\ninit', self.listLabelPoints)
                        pointInserted = False
                        for i in range(0,len(xdata)-1):
                            #print("--> testing inclusion %s in [%s-%s]" 
                            #        %(newPointLabel, self.listLabelPoints[i], self.listLabelPoints[i+1]))
                            line = LineString([(xdata[i], ydata[i]), (xdata[i+1], ydata[i+1])])
                            point = Point(x,y)
                            if line.distance(point) < 20:           # 20 = minimum distance in pixel for point inclusion on line
                                xdata.insert(i+1, x)
                                ydata.insert(i+1, y)
                                self.listLabelPoints.insert(i+1, newPointLabel)
                                pointInserted = True
                                #print("include", newPointLabel)
                                break
                        self.line_object.set_data(xdata, ydata)
                        self.update_lineWithWidthList()
                        #print('final', listLabelPoints)
                        #if not pointInserted:
                            #print("Error: point not inserted, too far from line")
                            #point_object.remove()
                        self.drawProfile()
                        self.canvas.draw()
                else:
                    xdata = event.artist.get_xdata()
                    ydata = event.artist.get_ydata()
                    x1, y1 = event.mouseevent.xdata, event.mouseevent.ydata
                    self.offset = xdata[0] - x1, ydata[0] - y1
                    event.artist.set_alpha(1.0)
                    self.canvas.draw()

    #------------------------------------------------------------------
    def on_motion(self, event):
        #----------------------------------------------
        # display hover scatter points when mouse passes over a peak
        if self.peakHover0 != None:
            self.peakHover0.remove()
            self.peakHover0 = None
            self.canvas.draw()
        if self.peakHover1 != None:
            self.peakHover1.remove()
            self.peakHover1 = None
            self.canvas.draw()

        cont = False
        if event.inaxes == self.ax[0] and self.peaks != None and self.cboxPeaks.isChecked():
            cont, ind = self.peaks.contains(event)
        elif event.inaxes == self.ax[1]:
            cont, ind = self.peaksCurve.contains(event)
        if cont and self.peaks != None:
            i = ind["ind"][0]
            pos = self.peaks.get_offsets()[i]
            self.peakHover0 = self.ax[0].scatter(pos[0], pos[1],
                                                 c='yellow', s=10, zorder=12)
            pos = self.peaksCurve.get_offsets()[i]
            self.peakHover1 = self.ax[1].scatter(pos[0], pos[1],
                                                 c='yellow', s=200, edgecolors='b', lw=1, alpha=0.8, zorder=0)
            self.canvas.draw()

        #----------------------------------------------
        if not self.press: return
        if event.xdata == None or event.ydata == None: return

        #----------------------------------------------
        if self.current_artist != None:
            dx, dy = self.offset
            if isinstance(self.current_artist, patches.Circle):
                cx, cy =  event.xdata + dx, event.ydata + dy
                self.current_artist.center = cx, cy
                #print("moving", self.current_artist.get_label())
                xdata = list(self.line_object.get_xdata())
                ydata = list(self.line_object.get_ydata())
                for i in range(0,len(xdata)): 
                    if self.listLabelPoints[i] == self.current_artist.get_label():
                        xdata[i] = cx
                        ydata[i] = cy
                        break
                self.line_object.set_data(xdata, ydata)
            elif isinstance(self.current_artist, Line2D):
                xdata = list(self.line_object.get_xdata())
                ydata = list(self.line_object.get_ydata())
                xdata0 = xdata[0]
                ydata0 = ydata[0]
                for i in range(0,len(xdata)): 
                        xdata[i] = event.xdata + dx + xdata[i] - xdata0
                        ydata[i] = event.ydata + dy + ydata[i] - ydata0 
                self.line_object.set_data(xdata, ydata)
                for p in list(self.ax[0].patches):
                    pointLabel = p.get_label()
                    i = self.listLabelPoints.index(pointLabel) 
                    p.center = xdata[i], ydata[i]
            self.update_lineWithWidthList()
            self.canvas.draw()
            self.drawProfile()
        elif event.inaxes == self.ax[0]:              # to zoom and pan in ax[0]
            dx = event.xdata - self.xpress
            dy = event.ydata - self.ypress
            self.cur_xlim -= dx
            self.cur_ylim -= dy
            self.ax[0].set_xlim(self.cur_xlim)
            self.ax[0].set_ylim(self.cur_ylim)
            self.canvas.draw()

    #------------------------------------------------------------------
    def on_press(self, event):
        self.press = True
        if event.button == 3:
            self.mousepress = "right"
        elif event.button == 1:
            self.mousepress = "left"
        if event.inaxes == self.ax[0]:              # to zoom and pan in ax[0]
            self.cur_xlim = self.ax[0].get_xlim()
            self.cur_ylim = self.ax[0].get_ylim()
            self.xpress = event.xdata
            self.ypress = event.ydata
        if event and event.dblclick:
            if len(self.listLabelPoints) < 2:
                self.n = self.n+1
                x, y = event.xdata, event.ydata
                newPointLabel = "point"+str(self.n)
                point_object = patches.Circle([x, y], radius=self.radius, color='red', fill=False, lw=2,
                        alpha=self.alpha_default, transform=self.ax[0].transData, label=newPointLabel)
                point_object.set_picker(5)
                self.ax[0].add_patch(point_object)
                self.listLabelPoints.append(newPointLabel)
                if len(self.listLabelPoints) == 2:
                    xdata = []
                    ydata = []
                    for p in list(self.ax[0].patches):
                        cx, cy = p.center
                        xdata.append(cx)
                        ydata.append(cy)
                    self.line_object, = self.ax[0].plot(xdata, ydata, alpha=self.alpha_default, c='red', lw=2, picker=True)
                    self.line_object.set_pickradius(5)
                    self.update_lineWithWidthList()
                self.canvas.draw()
                self.drawProfile()

    #------------------------------------------------------------------
    def drawProfile(self):
        if self.line_object is None:
            return 

        try:
            if self.scaleValue != 0. and self.scaleLength != 0:
                self.scalePixel = self.scaleValue / self.scaleLength
            else:
                self.scalePixel = 1

            xdata = list(self.line_object.get_xdata())
            ydata = list(self.line_object.get_ydata())
            line = LineString(list(zip(xdata,ydata)))

            listEndSegment = [0]
            self.profile =  np.array([]) 
            self.profile_mx = np.array([])
            self.profile_my = np.array([])
            self.profile_segment = np.array([])
            self.dist_profile = np.array([])
            for i in range(0,len(xdata)-1):
                #print("---", i, xdata[i], xdata[i+1])
                profile_tmp = profile_line(self.adjusted, (ydata[i], xdata[i]), (ydata[i+1], xdata[i+1]),
                                            order=0, mode='constant', cval=0, linewidth=self.profileLinewidth)

                profile_mx_tmp = profile_line(self.mx, (ydata[i], xdata[i]), (ydata[i+1], xdata[i+1]),
                                            order=0, mode='constant', cval=0, linewidth=self.profileLinewidth)
                profile_my_tmp = profile_line(self.my, (ydata[i], xdata[i]), (ydata[i+1], xdata[i+1]),
                                            order=0, mode='constant', cval=0, linewidth=self.profileLinewidth)

                self.profile = np.concatenate((self.profile, profile_tmp))
                self.profile_mx = np.concatenate((self.profile_mx, profile_mx_tmp))
                self.profile_my = np.concatenate((self.profile_my, profile_my_tmp))
                self.profile_segment = np.concatenate((self.profile_segment, profile_mx_tmp*0 + i+1))	# store segment number
                dist_profile_tmp = np.linspace(0, self.scalePixel*len(profile_tmp), num=len(profile_tmp))
                if i > 0:
                    # add last point of previous segment
                    self.dist_profile = np.concatenate((self.dist_profile, dist_profile_tmp + self.dist_profile[-1]))
                else:
                    self.dist_profile = np.concatenate((self.dist_profile, dist_profile_tmp))
                listEndSegment.append(self.dist_profile[-1])

            self.ax[1].set_visible(True)
            self.ax[1].clear()
            self.ax[1].set_facecolor('whitesmoke')
            
            if self.cboxReverseProfile.isChecked():
            	self.profile = 255 - self.profile
            self.ax[1].plot(self.dist_profile, self.profile, c='red', lw=1, alpha=0.8)

            for x in listEndSegment:
                self.ax[1].axvline(x=x, linestyle='dashed', color='red', alpha=0.8)
            
            kernel = np.ones(self.kernelSize) / self.kernelSize
            self.kernelOffset = int(self.kernelSize/2)
            
            # use mode='same' and put boundaries values to np.nan
            self.profile_convolved = np.convolve(self.profile, kernel, mode='same')
            self.profile_convolved[0:self.kernelOffset] = self.profile_convolved[-self.kernelOffset:] = np.nan

            self.ax[1].plot(self.dist_profile, self.profile_convolved, c='b', lw=1, alpha=0.8)
            
            # https://peakutils.readthedocs.io/en/latest/reference.html
            self.indexes = peakutils.indexes(self.profile_convolved, thres=self.peakutils_thres, thres_abs=True, min_dist=self.peakutils_minDist)
            self.peaksCurve = self.ax[1].scatter(self.dist_profile[self.indexes], self.profile_convolved[self.indexes], c='b', s=10)

            if self.peaks != None:
                self.peaks.remove()
                self.peaks = None

            if self.cboxPeaks.isChecked():
            	points = []
            	for i in self.indexes:
                	point = Point(self.profile_mx[i], self.profile_my[i])
                	# Closest point on the line
                	newPoint = line.interpolate(line.project(point))
                	points.append(newPoint)
            	xs = [point.x for point in points]
            	ys = [point.y for point in points]
            	self.peaks = self.ax[0].scatter(xs, ys, c='b', s=5, zorder=10)
           
            stripesNb = len(self.indexes)
            self.line1 = "Number of peaks: %3d" %(stripesNb)
            if stripesNb > 1:
                stripesDist = self.dist_profile[self.indexes[-1]]-self.dist_profile[self.indexes[0]]
                self.line2 = "Length of stripes: %.5f  (first: %.5f, last: %.5f)" \
                                %(stripesDist, self.dist_profile[self.indexes[0]], self.dist_profile[self.indexes[-1]])
                self.line3 = "Growth stripe rate (μm/stripe): %.5f" %(1000*stripesDist/(stripesNb-1))
            else:
                self.line2 = ""
                self.line3 = ""
            self.ax[1].text(0.2, 0.1, self.line1 + '\n' + self.line2 + '\n' + self.line3, 
                                va="top", transform=self.fig.transFigure)
         
            self.ax[1].grid(linestyle='dotted')
            self.ax[1].axhline(self.peakutils_thres, color="b", lw=1, linestyle='solid', alpha=0.8)

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
                    point1Scale = pt1
                    point2Scale = pt2
            #print("Detected scale length in pixel: ", scaleLength)

            if self.scaleLength > 0:
                self.scale_object = self.ax[0].plot([point1Scale[0], point2Scale[0]],
                                                    [point1Scale[1], point2Scale[1]],
                                                    alpha=1.0, c='purple', lw=2)
        except:
            self.scaleLength = 0

        try:
            self.scaleValue_object = self.ax[0].text(
                min(point1Scale[0], point2Scale[0]),
                min(point1Scale[1], point2Scale[1]),
                "   %.3f mm" %(self.scaleValue),
                alpha=1.0, c='purple', horizontalalignment='left', verticalalignment='bottom', clip_on=True)
        except:
            self.scaleValue_object = self.ax[0].text(
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
        #value, okPressed = QInputDialog.getDouble(self, "Get scale value","Value:", self.scaleValue, 0, 100, 1)
        # --> get comma instead of dot
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

        self.ax[0].set_title(os.path.basename(self.imageFileName) + '\n'
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
        self.ax[0].set_title(os.path.basename(self.imageFileName) + '\n' 
            + "          Scale length [pixels]: %s" %(self.scaleLength) + '\n'
            + "          Scale value [mm]: %.3f" %(self.scaleValue),
            loc='left', fontsize=10)
        if self.scale_object == None:
            self.scale_object = self.ax[0].plot([point1Scale[0], point2Scale[0]], 
                                                [point1Scale[1], point2Scale[1]],
                                                alpha=1.0, c='purple', lw=2)
        else:
            self.scale_object[0].set_data([point1Scale[0], point2Scale[0]],
                                          [point1Scale[1], point2Scale[1]])
        self.scaleValue_object.set_position((point1Scale[0], point1Scale[1]))
        self.drawProfile()

    #------------------------------------------------------------------
    def update_lineWithWidthList(self):
        for line in self.lineWithWidthList:
            line.remove()
        self.lineWithWidthList = []
        if self.profileLinewidth > 1:
            xdata = list(self.line_object.get_xdata())
            ydata = list(self.line_object.get_ydata())
            for i in range(len(xdata)-1):
                line = LineString([(xdata[i], ydata[i]), (xdata[i+1], ydata[i+1])])
                dilated = line.buffer(self.profileLinewidth/2., cap_style=2, join_style=1)
                line1, = self.ax[0].plot(*dilated.exterior.xy, alpha=self.alpha_default, c='red', lw=2)
                self.lineWithWidthList.append(line1)
        
    #------------------------------------------------------------------
    def displayImage(self):
        self.initValues()
        self.initInterface()

        self.ax[0].set_visible(True)
        self.ax[0].clear()

        img = cv2.imread(self.imageFileName)
        (self.mx, self.my) = np.meshgrid(np.arange(img.shape[1]), np.arange(img.shape[0]))
        self.gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mask0 = cv2.inRange(self.gray, 0, 0)
        self.mask = cv2.bitwise_not(mask0)
        self.alphaLevel =  self.mySliderAlpha.value()/10.
        self.betaLevel = self.mySliderBeta.value()
        self.adjusted = cv2.convertScaleAbs(self.gray, alpha=self.alphaLevel, beta=self.betaLevel)
        self.image_object = self.ax[0].imshow(self.adjusted, cmap='gray', aspect='equal')
        self.detectScale()

        self.ax[0].set_title(os.path.basename(self.imageFileName) + '\n'
            + "          Scale length [pixels]: %s" %(self.scaleLength) + '\n'
            + "          Scale value [mm]: %.3f" %(self.scaleValue),
            loc='left', fontsize=10)
        self.ax[0].set_adjustable('datalim')

        self.cboxInverseImage.setEnabled(True)
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
        file1.write("# Detected scale value: %.3f\n" %(self.scaleValue))
        file1.write("# Detected scale length in pixel: %d\n" %(self.scaleLength))
        file1.write("# Inverse image: %s\n" %(self.cboxInverseImage.isChecked()))
        file1.write("# Contrast level: %.1f\n" %(self.alphaLevel))
        file1.write("# Brightness level: %d\n" %(self.betaLevel))
        file1.write("# Kernel size: %d\n" %(self.kernelSize))
        file1.write("# Profile linewidth: %d\n" %(self.profileLinewidth))
        file1.write("# PeakUtils - Minimum distance: %d\n" %(self.peakutils_minDist))
        file1.write("# PeakUtils - Threshold: %d\n" %(self.peakutils_thres))
        xdata = list(self.line_object.get_xdata())
        ydata = list(self.line_object.get_ydata())
        file1.write("# Number of segments: %d\n" %(len(xdata)-1))
        for i in range(0,len(xdata)):
            file1.write("#      Point%d: [%d, %d]\n" %(i+1, xdata[i], ydata[i]))
        file1.write("# " + self.line1 + '\n# ' + self.line2 + '\n# ' + self.line3 + '\n')
        file1.write("#================================================\n")
        file1.write("n,xpos,ypos1,ypos2,peak,segment\n")
        profile_convolvedFilled = np.nan_to_num(self.profile_convolved , nan=-999)
        for i,v in enumerate(self.dist_profile):
            if i in self.indexes:
                file1.write("%d,%.7f,%.7f,%.7f,%d,%d\n" 
                    %(i+1, self.dist_profile[i], self.profile[i], profile_convolvedFilled[i], 1, self.profile_segment[i]))
            else:
                file1.write("%d,%.7f,%.7f,%.7f,%d,%d\n" 
                    %(i+1, self.dist_profile[i], self.profile[i], profile_convolvedFilled[i], 0, self.profile_segment[i]))
        file1.close()
        file1NamePNG = os.path.splitext(file1NameCSV)[0] + ".png"
        plt.savefig(file1NamePNG)
        print("---------------------------")
        print("Saved csv file: " + file1NameCSV)
        print("Saved png file: " + file1NamePNG)
        
        # draw the line to keep a record of what has been saved so far.
        self.ax[0].plot(xdata, ydata, alpha=0.5, c='blue', lw=2)
        text_line.CurvedText(
            x=[xdata[0], xdata[-1]],
            y=[ydata[0], ydata[-1]],
            text="File %02d"%self.counterFilename,
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
                "","PNG, JPG, TIF Files (*.png *.jpg *.tif);;PNG Files (*.png);;JPG Files (*.jpg);;TIF Files (*.tif);;All Files (*)", options=options)
        if self.imageFileName:
            self.displayImage()

    #------------------------------------------------------------------
    def exitCall(self):
        self.close()

    #------------------------------------------------------------------
    def aboutCall(self):
        msg = " StripesCounter " + version + """ 

         * Open an image, optionnaly with a scale and value scale annotation
         * Pan the image from a mouse click
         * Zoom in or out with wheel zoom (or 2 fingers pad actions)
         * Enhance the image from brightness and contrast sliders
         * Create a profile line by double clicking
         * At the 2nd point, the profile to be extracted is drawn as a red line
         * The profile of the image is drawn corresponding to the profile line 
         * Add segments to the profile line by double clicking on it
               - left double clicking to add a control point
               - right double clicking to remove a control point 
         * Number of peaks (stripes) are counted from the smoothed profile
         * Adapt various parameters for peak dectection and smoothing
         * Move, modify the profile line and control points if needed
         * Control the width of the profile line
         * Inspect detected peaks with a mouse over from image or profile 
         * Define new scale and scale value if needed
         * Save the image and the data points, visualize the extracted profile

         * Developped by Patrick Brockmann (LSCE)
        """
        QMessageBox.about(self, "About the StripesCounter", msg.strip())

#======================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit( app.exec_() )

