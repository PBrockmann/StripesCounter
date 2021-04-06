#!/usr/bin/env python

#=================================================================
# Author: Patrick Brockmann CEA/DRF/LSCE - Feb 2021
#=================================================================

#------------------------------------------------------------------
version = "v07"
date = "2021/02/11"

#------------------------------------------------------------------
import sys, re, os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D
from skimage.measure import profile_line
import peakutils

import cv2

import text_line # for annotation on lines

#------------------------------------------------------------------
imageFileName = sys.argv[1]
#print("#-----------------------------------")
#print("File: ", imageFileName)

#------------------------------------------------------------------
img = cv2.imread(imageFileName)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#equalized = cv2.equalizeHist(gray)
mask = cv2.inRange(gray, 0, 0)

#------------------------------------------------------------------
try:
    import pytesseract

    scaleDetected = pytesseract.image_to_string(mask)
    matchObj = re.match(r'[^0-9]*([0-9]*)mm', scaleDetected.strip())
    scaleValue = float(matchObj.group(1))
    #print("Detected scale value: ", scaleValue)
    
    fld = cv2.ximgproc.createFastLineDetector()
    lines = fld.detect(mask)
    scaleLength = 0
    for line in lines:
        point1 = np.array((line[0][0],line[0][1]))
        point2 = np.array((line[0][2],line[0][3]))
        length = np.linalg.norm(point1 - point2)
        #print(point1, point2, dist)
        if (length > scaleLength):
            scaleLength = int(length) 
    #print("Detected scale length in pixel: ", scaleLength)
    
    scalePixel = scaleValue / scaleLength
except:
    scaleValue = 0 
    scaleLength = 0 
    scalePixel = 1

#------------------------------------------------------------------
point1 = [0,0]
point2 = [0,0]
image_object = None
point1_object = None
point2_object = None
line_object = None

offset = [0,0]
current_artist = None
currently_dragging = False

point_alpha_default = 0.4
point_alpha_pick = 0.1

kernelSize = 3 
peakutils_minDist = 1
peakutils_thres = 0.5

dist_profil = None
profil = None
profil_convolved = None
indexes = None

line1 = line2 = line3 = None
counterFilename = 1 

#------------------------------------------------------------------
fig, ax = plt.subplots(nrows=2, figsize=(8,8))
plt.tight_layout()
fig.subplots_adjust(top=0.9, bottom=0.15)

fig.canvas.set_window_title(imageFileName)

#------------------------------------------------------------------
alphaLevel = 1.0 # Contrast control (1.0-3.0)
betaLevel = 0 # Brightness control (0-100)
adjusted = cv2.convertScaleAbs(gray, alpha=alphaLevel, beta=betaLevel)

image_object = ax[0].imshow(adjusted, cmap='gray')

ax[0].set_title(os.path.basename(imageFileName) + '\n' 
    + "          Scale length detected [pixels]: %s" %(scaleLength) + '\n'
    + "          Scale value detected [mm]: %s" %(scaleValue),
    loc='left', fontsize=10)

ax[0].set_aspect('equal')
ax[0].autoscale(False)

#------------------------------------------------------------------
def on_click(event):
    global point1_object, point2_object, line_object
    global point1, point2
    global dist_profil, profil, profil_convolved, indexes
    global line1, line2, line3

    if event and event.dblclick:
        if point1_object == None:
            point1 = [event.xdata, event.ydata]
            point1_object = patches.Circle(point1, radius=50, fc='r', fill=False, color='r',
                alpha=point_alpha_default, transform=ax[0].transData, label="point1")
            ax[0].add_patch(point1_object)
            point1_object.set_picker(5)
        elif point2_object == None:
            point2 = [event.xdata, event.ydata]
            point2_object = patches.Circle(point2, radius=50, fc='r', fill=False, color='r', 
                alpha=point_alpha_default, transform=ax[0].transData, label="point2")
            ax[0].add_patch(point2_object)
            point2_object.set_picker(5)
        plt.draw()

    if point1_object != None and point2_object != None:

        #point1_object.set_visible(False)
        #point2_object.set_visible(False)

        if line_object != None:
            line_object[0].remove()
            line_object = None
        line_object = ax[0].plot([point1[0], point2[0]], [point1[1], point2[1]], 
                alpha=0.5, c='r', lw=2, picker=True)
        plt.draw()

        line_object[0].set_pickradius(5)

        for canvas in set(artist.figure.canvas for artist in [point1_object, point2_object, line_object[0]]):
            canvas.mpl_connect('button_press_event', on_press)
            canvas.mpl_connect('button_release_event', on_release)
            canvas.mpl_connect('pick_event', on_pick)
            canvas.mpl_connect('motion_notify_event', on_motion)

        profil = profile_line(adjusted, 
                (point1[1], point1[0]), (point2[1], point2[0]),                                   # (Y1, X1), (Y2, X2) 
                order=0, mode='constant', cval=0)

        ax[1].clear()

        dist_profil = np.linspace(0, scalePixel*len(profil), num=len(profil))
        ax[1].plot(dist_profil, profil, c='r', lw=1, alpha=0.8)
        
        kernel = np.ones(kernelSize) / kernelSize
        kernelOffset = int(kernelSize/2)

        # mode='same' gives artefact at start and end 
        #profil_convolved = np.convolve(profil, kernel, mode='same')
        #ax[1].plot(dist_profil, profil_convolved, c='c', lw=1, alpha=0.8)

        # use mode='valid' but need to take into account with absysse values (dist_profil[int(kernelSize/2):-int(kernelSize/2)])
        profil_convolved = np.convolve(profil, kernel, mode='valid')
        if kernelSize == 1 :
            ax[1].plot(dist_profil, profil_convolved, c='b', lw=1, alpha=0.8)
        else:
            ax[1].plot(dist_profil[kernelOffset:-kernelOffset], profil_convolved, c='b', lw=1, alpha=0.8)

        # https://peakutils.readthedocs.io/en/latest/reference.html
        indexes = peakutils.indexes(profil_convolved, thres=peakutils_thres, thres_abs=False, min_dist=peakutils_minDist)
        ax[1].scatter(dist_profil[indexes+kernelOffset], profil_convolved[indexes], c='b', s=10)  # add offset of the kernel/2

        stripesNb = len(indexes)
        stripesDist = dist_profil[indexes[-1]+kernelOffset]-dist_profil[indexes[0]+kernelOffset]
        line1 = "Number of stripes: %3d" %(stripesNb)
        line2 = "Length of stripes: %.5f  (first: %.5f, last: %.5f)" \
                     %(stripesDist,  dist_profil[indexes[0]+kernelOffset], dist_profil[indexes[-1]+kernelOffset])
        line3 = "Growth stripe rate (µm/stripe): %.5f" %(1000*stripesDist/stripesNb)

        ax[1].text(0.2, 0.1, line1 + '\n' + line2 + '\n' + line3, va="top", transform=fig.transFigure)
        
        ax[1].grid(linestyle='dotted')

#------------------------------------------------------------------
def on_press(event):
    global adjusted, image_object
    global alphaLevel, betaLevel
    global currently_dragging
    global kernelSize, peakutils_minDist, peakutils_thres
    global counterFilename
    global point1, point2

    currently_dragging = True

    if event.key == '+':
        alphaLevel += 0.1
        alphaLevel = min(3.0, alphaLevel)
        print("Contrast level (1.0-3.0): %.1f" %(alphaLevel))
        adjusted = cv2.convertScaleAbs(gray, alpha=alphaLevel, beta=betaLevel)
        image_object.set_data(adjusted)
        plt.draw()
    elif event.key == '=':
        alphaLevel -= 0.1
        alphaLevel = max(1.0, alphaLevel)
        print("Contrast level (1.0-3.0): %.1f" %(alphaLevel))
        adjusted = cv2.convertScaleAbs(gray, alpha=alphaLevel, beta=betaLevel)
        image_object.set_data(adjusted)
        plt.draw()
    elif event.key == 'b':
        betaLevel += 5 
        #betaLevel = min(100, betaLevel)
        print("---------------------------")
        print("Brightness level: %d" %(betaLevel))
        adjusted = cv2.convertScaleAbs(gray, alpha=alphaLevel, beta=betaLevel)
        image_object.set_data(adjusted)
        plt.draw()
    elif event.key == 'B':
        betaLevel -= 5 
        #betaLevel = max(0, betaLevel)
        print("---------------------------")
        print("Brightness level: %d" %(betaLevel))
        adjusted = cv2.convertScaleAbs(gray, alpha=alphaLevel, beta=betaLevel)
        image_object.set_data(adjusted)
        plt.draw()
    elif event.key == 'o':
        kernelSize += 2 
        print("---------------------------")
        print("Kernel size: ", kernelSize)
    elif event.key == 'O':
        kernelSize -= 2 
        kernelSize = max(1, kernelSize) 
        print("---------------------------")
        print("Kernel size: ", kernelSize)
    elif event.key == 'z':
        peakutils_minDist += 1 
        print("---------------------------")
        print("PeakUtils - Minimum distance: ", peakutils_minDist)
    elif event.key == 'Z':
        peakutils_minDist -= 1 
        peakutils_minDist = max(1, peakutils_minDist) 
        print("---------------------------")
        print("PeakUtils - Minimum distance: ", peakutils_minDist)
    elif event.key == 'e':
        peakutils_thres += 0.1 
        peakutils_thres = min(0.9, peakutils_thres) 
        print("---------------------------")
        print("PeakUtils - Threshold: %.1f" %(peakutils_thres))
    elif event.key == 'E':
        peakutils_thres -= 0.1
        peakutils_thres = max(0.1, peakutils_thres) 
        print("PeakUtils - Threshold: %.1f" %(peakutils_thres))
    elif event.key == 'h':
        print("---------------------------")
        print("Help: h")
        print("Contrast control: +/=")
        print("Brightness control: b/B")
        print("PeakUtils - Minimum distance control: z/Z")
        print("PeakUtils - Threshold control: e/E")
        print("Kernel size control: o/O")
        print("Save: S")
    elif event.key == 'S':
        base=os.path.basename(imageFileName)
        file1Name = os.path.splitext(base)[0] + "_StripesCounter_{}.csv"
        while os.path.isfile(file1Name.format("%02d" %counterFilename)):
            counterFilename += 1
        file1Name = file1Name.format("%02d" %counterFilename)
        file1 = open(file1Name, "w")
        file1.write("#================================================\n")
        file1.write("# StripesCounter " + version + "\n")
        file1.write("# File: %s\n" %(imageFileName))
        file1.write("# Detected scale value: %d\n" %(scaleValue))
        file1.write("# Detected scale length in pixel: %d\n" %(scaleLength))
        file1.write("# Point1: [%d, %d]\n" %(point1[0], point1[1]))
        file1.write("# Point2: [%d, %d]\n" %(point2[0], point2[1]))
        file1.write("# " + line1 + '\n# ' + line2 + '\n# ' + line3 + '\n')
        file1.write("#================================================\n")
        kernelOffset = int(kernelSize/2)
        file1.write("n,xpos,ypos1,ypos2,peak\n")
        for i,v in enumerate(dist_profil):
                if i-kernelOffset >= 0  and i-kernelOffset < len(profil_convolved): 
                        if i-kernelOffset in indexes:
                        	file1.write("%d,%.5f,%.5f,%.5f,%d\n" %(i+1,dist_profil[i], profil[i], profil_convolved[i-kernelOffset],1))
                        else:
                        	file1.write("%d,%.5f,%.5f,%.5f,%d\n" %(i+1,dist_profil[i], profil[i], profil_convolved[i-kernelOffset],0))

                else:
                        file1.write("%d,%.5f,%.5f,%.5f,%d\n" %(i+1,dist_profil[i], profil[i], -999, 0))
        file1.close()
        print("Saved csv file:" + file1Name)
        file1NamePng = os.path.splitext(file1Name)[0] + ".png"
        plt.savefig(file1NamePng)
        print("---------------------------")
        print("Saved csv file: " + file1Name)
        print("Saved pnf file: " + file1NamePng)
        
        # draw the line to keep a record of what has been saved so far.
        ax[0].annotate("", xy=(point1[0], point1[1]), 
                       xytext=(point2[0], point2[1]), 
                       arrowprops=dict(arrowstyle="<->", color="blue"), 
                       alpha=0.5)
        text_line.CurvedText(
            x = [point1[0], point2[0]],
            y =  [point1[1], point2[1]],
            text="File {}".format("%02d" %counterFilename),#'this this is a very, very long text',
            va='bottom',
            axes = ax[0], ##calls ax.add_artist in __init__
            alpha=0.5,
            color="blue"
        )
        plt.draw()
    on_click(None)

#------------------------------------------------------------------
def on_release(event):
    global currently_dragging, current_artist
    current_artist = None
    currently_dragging = False

#------------------------------------------------------------------
def on_pick(event):
    global current_artist, offset
    if current_artist is None:
        current_artist = event.artist
        if isinstance(event.artist, patches.Circle):
            current_artist = event.artist
            x0, y0 = current_artist.center
            x1, y1 = event.mouseevent.xdata, event.mouseevent.ydata
            offset = [(x0 - x1), (y0 - y1)]
        elif isinstance(event.artist, Line2D):
            xdata = event.artist.get_xdata()
            ydata = event.artist.get_ydata()
            x1, y1 = event.mouseevent.xdata, event.mouseevent.ydata
            offset = xdata[0] - x1, ydata[0] - y1

#------------------------------------------------------------------
def on_motion(event):
    global current_artist
    global point1, point2
    if not currently_dragging:
        return
    if current_artist == None:
        return
    if event.xdata == None:
        return
    dx, dy = offset
    if isinstance(current_artist, patches.Circle):
        cx, cy =  event.xdata + dx, event.ydata + dy
        current_artist.center = cx, cy
        if current_artist.get_label() == "point1":
            point1 =  [cx, cy]
        elif current_artist.get_label() == "point2":
            point2 =  [cx, cy]
        line_object[0].set_data([point1[0], point2[0]],[point1[1], point2[1]])
    elif isinstance(current_artist, Line2D):
        xdata = current_artist.get_xdata()
        ydata = current_artist.get_ydata()
        point1 =  [event.xdata + dx, event.ydata + dy]
        point2 =  [event.xdata + dx + xdata[1] - xdata[0], event.ydata + dy + ydata[1] - ydata[0]]
        current_artist.set_xdata([point1[0], point2[0]])
        current_artist.set_ydata([point1[1], point2[1]])
        point1_object.center = point1[0], point1[1]
        point2_object.center = point2[0], point2[1]
    #current_artist.figure.canvas.draw()
    on_click(None)
    #plt.draw()

#------------------------------------------------------------------
fig.canvas.mpl_connect('button_press_event', on_click)
fig.canvas.mpl_connect('key_press_event', on_press)
fig.canvas.mpl_connect('key_release_event', on_release)

plt.get_current_fig_manager().toolbar.pan()
#plt.get_current_fig_manager().toolbar.zoom()
plt.show()


