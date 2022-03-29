# StripesCounter

A PyQt Matplotlib python application to count stripes from microscopic images

 * Automatic detection of the scale length and scale value
 * Display of the microscopic image with a grayscale color map
 * Control of the contrast and the brightness of the image
 * Definition of a profil line from mouse double clicks
 * Add/Remove points to define a segmented profil
 * Move the profil by picking its line or its control points
 * Smooth the intensity calcul from the control of the profil line width
 * Extraction of the profil
 * Smoothing (convolution) from a variable length kernel
 * Detection of the number of the peaks (number of stripes)
 * Display of detected peaks on image
 * Growth rate display

![ScreenShot](StripesCounter_v10.8.gif)  

Usage :

 * Open an image, optionnaly with a scale and value scale annotation
 * Pan the image from a mouse click
 * Zoom in or out with wheel zoom (or 2 fingers pad actions)
 * Enhance the image from brightness and contrast sliders
 * Create a profil line by double clicking
 * At the 2nd point, the profil to be extracted is drawn as a red line
 * The profil of the image is drawn corresponding to the profil line 
 * Add segments to the profil line by double clicking on it
   * left double clicking to add a control point
   * right double clicking to remove a control point 
 * Number of peaks (stripes) are counted from the smoothed profil
 * Adapt various parameters for peak dectection and smoothing
 * Move, modify the profil line and control points if needed
 * Control the width of the profil line
 * Inspect detected peaks with a mouse over from image or profil
 * Define new scale and scale value if needed
 * Save the image and the data points, visualize the extracted profil

## Release notes

v10.82
 * Smaller radius for control points
 * PeakUtils - Threshold with 0.05 increment steps

v10.81
 * Fix with tesseract v5.0.1
 * Fix error in setting scale value

v10.8
 * Add profil line width control

v10.7
 * Increase precision when save files (7 digits)

v10.6
 * Inverse image feature
 * Option to open both png and jpeg files

v10.5
 * Scale value has now on 3 precision digits

v10.4
 * Add extra informations (segment number, parameters) in csv file

v10.3
 * Highlight peaks when mouse over from image or profil

v10.2
 * Display detected peaks on image

v10.1
 * Zoom and drag with mouse
 * Removed matplotlib Toolbar

v10.0
 * Profil from segmented line 

v09.4
 * Simplify events handling made now on the canvas

v09.3
 * Enforce checking errors with scaleValue and scale objects

v09.2
 * Fix for undefined variables in detectScale
 * drawProfil in a try-except block to prevent errors

v09.1
 * Fix for scale value recognition

v09.0
 * First release with a PyQt interface

## Installation

`$ git clone https://github.com/PBrockmann/StripesCounter`

Tested with
 * matplotlib=3.5.1
 * opencv=4.5.5.64
 * opencv-contrib-python=4.5.5.64
 * peakutils=1.3.3
 * PyQt5=5.15.6
 * pytesseract=0.3.9
 * python=3.9.10
 * scikit-image=0.19.2
 * shapely=1.8.0

## Contrast and brighness reference 

https://docs.opencv.org/4.5.4/d3/dc1/tutorial_basic_linear_transform.html

## PeakUtils reference

https://peakutils.readthedocs.io/en/latest/reference.html#module-peakutils.peak

 * thres (float between [0., 1.]) – Normalized threshold. Only the peaks with amplitude higher than the threshold will be detected.

 * min_dist (int) – Minimum distance between each detected peak. The peak with the highest amplitude is preferred to satisfy this constraint.
