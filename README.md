# StripesCounter

A PyQt Matplotlib python application to count stripes from microscopic images

 * Automatic detection of the scale length and scale value
 * Display of the microscopic image with a grayscale color map
 * Control of the contrast and the brightness of the image
 * Definition of a profil line from mouse double clicks
 * The profil line can be redefined, moved by picking the line or its bounds
 * Extraction of the profil
 * Smoothing (convolution) from a variable length kernel
 * Detection of the number of the peaks (number of stripes)
 * Growth rate display

![ScreenShot](StripesCounter_v09.gif)  

Sequence of use :

 * Open an image with a scale and value scale
 * Enhance the image from brightness and contrast sliders
 * Double click to create a 1st point
 * Double click to create a 2nd point
 * A red line is drawn between the 2 previously defined points drawn as circles 
 * A profil along the line is drawn
 * Number of peaks (stripes) are counted from the smoothed profil
 * Move, modify the profil line if needed by pick the line or the circles
 * Define new scale and enter new scale value if needed from buttons

## Release notes

v09.2
 * Fix for undefined variables in detectScale.
 * drawProfil in a try-except block to prevent errors

v09.1
 * Fix for scale value recognition

v09
 * First release with a PyQt interface

## Installation

`$ git clone https://github.com/PBrockmann/StripesCounter`

Tested with python 3.8.5, matplotlib 3.4.1, pyqt 5.12.3

## Contrast and brighness reference 

https://docs.opencv.org/4.5.2/d3/dc1/tutorial_basic_linear_transform.html

## PeakUtils reference

https://peakutils.readthedocs.io/en/latest/reference.html#module-peakutils.peak

 * thres (float between [0., 1.]) – Normalized threshold. Only the peaks with amplitude higher than the threshold will be detected.

 * min_dist (int) – Minimum distance between each detected peak. The peak with the highest amplitude is preferred to satisfy this constraint.
