

#=================================================================
# Author: Patrick Brockmann CEA/DRF/LSCE - May 2022
#=================================================================

import sys, os

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

import numpy as np
import cv2

#======================================================
class MainWindow(QMainWindow):

    #------------------------------------------------------------------
    def __init__(self):
        QMainWindow.__init__(self)

        #-------------------------------
        self.setMinimumSize(QSize(1400, 900))    
        self.setWindowTitle("StripesCounter read sampling") 

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

        # Create menu bar and add action
        self.menuBar = self.menuBar()
        fileMenu = self.menuBar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)

        #-----------------------
        self.fig = plt.figure(figsize=(8,8))
        self.ax0 = self.fig.add_axes([0.08, 0.05, 0.87, 0.90])   #  [left, bottom, width, height]

        self.canvas = FigureCanvas(self.fig)
        # https://github.com/matplotlib/matplotlib/issues/707/
        self.canvas.setFocusPolicy(Qt.ClickFocus)
        self.canvas.setFocus()

        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas.mpl_connect('scroll_event', self.zoom)

        #-----------------------
        layoutH = QHBoxLayout()

        layoutV1 = QVBoxLayout()
        layoutV1.addWidget(self.canvas)

        layoutH.addLayout(layoutV1)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QWidget()
        widget.setLayout(layoutH)
        self.setCentralWidget(widget)

        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage('Ready', 5000)

        self.ax0.set_visible(False)

        #-----------------------
        self.press = False
        self.xpress = 0
        self.ypress = 0
        self.cur_xlim = None 
        self.cur_ylim = None 

        self.scale_zoom = 1.2
        self.imageDisplayedWidthLimit = 2000
        self.subSampling = 1
        self.imageDisplayedWidth = 0 

    #------------------------------------------------------------------
    def zoom(self, event):
        try:
            # https://stackoverflow.com/questions/11551049/matplotlib-plot-zooming-with-scroll-wheel
            cur_xlim = event.inaxes.get_xlim()
            cur_ylim = event.inaxes.get_ylim()
            xdata = event.xdata # get event x location
            ydata = event.ydata # get event y location
            if event.button == 'up':            # zoom in
                scale_factor = 1. / self.scale_zoom
                print('--- up')
                if (self.imageDisplayedWidth < self.imageDisplayedWidthLimit):
                    if (self.subSampling > 1) :
                        self.subSampling -= 1
                        self.sampleImage()
            elif event.button == 'down':        # zoom out
                scale_factor = self.scale_zoom
                print('--- down')
                if (self.imageDisplayedWidth > self.imageDisplayedWidthLimit):
                    self.subSampling += 1
                    self.sampleImage()
            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
            relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata)/(cur_ylim[1] - cur_ylim[0])
            self.cur_xlim = [xdata - new_width * (1-relx), xdata + new_width * (relx)]
            self.cur_ylim = [ydata - new_height * (1-rely), ydata + new_height * (rely)]
            self.displayImage()
        except:
            return

    #------------------------------------------------------------------
    def on_release(self, event):

        #----------------------------------------------
        self.press = False
        self.canvas.draw()

    #------------------------------------------------------------------
    def on_press(self, event):

        #----------------------------------------------
        self.press = True
        if event.inaxes == self.ax0:
            self.cur_xlim = self.ax0.get_xlim()
            self.cur_ylim = self.ax0.get_ylim()
            self.xpress = event.xdata
            self.ypress = event.ydata

    #------------------------------------------------------------------
    def on_motion(self, event):

        #----------------------------------------------
        if not self.press: return
        if event.xdata == None or event.ydata == None: return

        #----------------------------------------------
        if event.inaxes == self.ax0:
            dx = event.xdata - self.xpress
            dy = event.ydata - self.ypress
            self.cur_xlim -= dx
            self.cur_ylim -= dy
            self.displayImage()

    #------------------------------------------------------------------
    def openCall(self):
        self.openFileNameDialog()

    #------------------------------------------------------------------
    def readImage(self):

        self.status_bar.showMessage('Reading file')
        qApp.processEvents()            # Flush events

        self.ax0.set_visible(True)

        print('Reading start')
        self.image = cv2.imread(self.imageFileName, cv2.IMREAD_GRAYSCALE)
        print('Readind end')
        print("Shape: ", self.image.shape)
        #print("Width: ", self.image.shape[1])
        #print("Height: ", self.image.shape[0])
        self.subSampling = np.ceil(np.max(self.image.shape) / self.imageDisplayedWidthLimit).astype(int)
        self.cur_xlim = [0, self.image.shape[1]]
        self.cur_ylim = [self.image.shape[0], 0]
        self.sampleImage()

        self.status_bar.clearMessage()

    #------------------------------------------------------------------
    def sampleImage(self):

        print("Sampling: ", self.subSampling)
        if self.subSampling == 1:
            self.imageResized = self.image
        else:
            self.imageResized = cv2.resize(self.image, None, fx=1./self.subSampling, fy=1./self.subSampling, interpolation = cv2.INTER_NEAREST)
        print("Resized: ", self.imageResized.shape)

    #------------------------------------------------------------------
    def adjustImage(self):

        self.alphaLevel =  self.mySliderAlpha.value()/10.
        self.betaLevel = self.mySliderBeta.value()
        #self.imageAdjusted = cv2.convertScaleAbs(self.image, alpha=self.alphaLevel, beta=self.betaLevel)
        self.imageResizedAdjusted = cv2.convertScaleAbs(self.imageResized, alpha=self.alphaLevel, beta=self.betaLevel)

    #------------------------------------------------------------------
    def displayImage(self):

        ex1 = np.maximum(0, np.min(self.cur_xlim)) 
        ex2 = np.minimum(self.image.shape[1], np.max(self.cur_xlim)) 
        ey1 = np.maximum(0, np.min(self.cur_ylim)) 
        ey2 = np.minimum(self.image.shape[0], np.max(self.cur_ylim))
        x1 = int(ex1 / self.subSampling)
        x2 = int(ex2 / self.subSampling)
        y1 = int(ey1 / self.subSampling)
        y2 = int(ey2 / self.subSampling)

        self.ax0.clear()
        self.ax0.set_adjustable('datalim')
        self.image_object = self.ax0.imshow(self.imageResized[y1:y2, x1:x2], cmap='gray', vmin=0, vmax=255,
                                                aspect='equal', extent=[ex1,ex2,ey2,ey1])
        self.ax0.set_xlim(self.cur_xlim)
        self.ax0.set_ylim(self.cur_ylim)
        self.ax0.text(0.75, 0.99, 'Sampling: 1:%d'%self.subSampling, horizontalalignment='left', verticalalignment='top',
                      transform=self.fig.transFigure)
        self.canvas.draw()
        self.imageDisplayedWidth = (x2 - x1)
        print("Image displayed width: ", self.imageDisplayedWidth)


    #------------------------------------------------------------------
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.imageFileName, _ = QFileDialog.getOpenFileName(self, "Load image", 
                "","PNG, JPG, TIF Files (*.png *.jpg *.tif);;PNG Files (*.png);;JPG Files (*.jpg);;TIF Files (*.tif);;All Files (*)", options=options)
        if self.imageFileName:
            self.readImage()
            self.displayImage()

    #------------------------------------------------------------------
    def exitCall(self):
        self.close()

#======================================================
if __name__ == "__main__":
    qApp = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit( qApp.exec_() )

