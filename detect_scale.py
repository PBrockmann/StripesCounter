#!/usr/bin/env python

#=================================================================
# Author: Patrick Brockmann CEA/DRF/LSCE - Feb 2021
#=================================================================

# Test detection of the scale
# Usage: ./detect_scale.py BEL17-2-2_1.35x_haut0001.png

#------------------------------------------------------------------
import sys, re, os
import numpy as np
import cv2
import pytesseract

#------------------------------------------------------------------
imageFileName = sys.argv[1]
print("File: ", imageFileName)

#------------------------------------------------------------------
img = cv2.imread(imageFileName)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
mask = cv2.inRange(gray, 0, 0)

print("Writing mask.png")
cv2.imwrite('mask.png', mask)

# https://github.com/tesseract-ocr/tesseract/issues/1913
maskinv= cv2.bitwise_not(mask)
cv2.imwrite('maskinv.png', maskinv)

#------------------------------------------------------------------
try:
    scaleDetected = pytesseract.image_to_string(maskinv)
    matchObj = re.match(r'[^0-9]*([0-9]*)mm', scaleDetected.strip())
    scaleValue = float(matchObj.group(1))
    print("Detected scale value: ", scaleValue)
except:
    print("Detected scale value: not possible")

#------------------------------------------------------------------
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
print("Detected scale length in pixel: ", scaleLength)

try:
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
    print("Detected scale length in pixel: ", scaleLength)
except:
    print("Detected scale length in pixel: not possible")
    
