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
 * A red line is drawn between the 2 previously defined points  
 * A profil along the line is drawn
 * Number of peaks (stripes) are counted from the smoothed profil
 * Move, modify the profil line if needed
 * Define new scale and scale value if needed


