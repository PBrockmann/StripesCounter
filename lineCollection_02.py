
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from shapely.geometry import Point,LineString
from matplotlib.backend_bases import MouseButton

#=======================================================
fig, ax = plt.subplots(1, 1, figsize=(8,6))

ax.set_aspect('equal')
ax.grid()

ax.set_xlim(0,10)
ax.set_ylim(0,10)

#=======================================================
segmentsCollection = LineCollection([], linestyle='solid', color='r')
ax.add_collection(segmentsCollection)

peaksCollection = LineCollection([], linestyle='solid', color='b')
ax.add_collection(peaksCollection)

segs2 = [ [[2,5],[6,8]], [[1,2],[6,4]], [[2,2],[8,2]] ]
segmentsCollection.set_segments(segs2)

# I would like to save segment number data in the LineCollection instance (peaksCollection)
# Don't know how to store this extra information in the segment of the LineCollection object. 
peaksInSegment = []

#=======================================================
def draw_tick(segment, x, y, length=0.25):
    line = LineString(segment)   
    left = line.parallel_offset(length, 'left')
    right0 = line.parallel_offset(length, 'right')
    right = LineString([right0.boundary.geoms[1], right0.boundary.geoms[0]]) # flip because 'right' orientation
    point = Point(x,y)
    a = left.interpolate(line.project(point))
    b = right.interpolate(line.project(point))
    line  = LineString([a, b])
    return line

#=======================================================
def onpress(event):
    # segments
    cont, ind = segmentsCollection.contains(event)
    if cont:
        i = ind["ind"][0]
        #print("segment", ind, i)
        if event.button is MouseButton.LEFT:
            x0 = event.xdata
            y0 = event.ydata
            segment = segmentsCollection.get_segments()[i]
            peak = draw_tick(segment, x0, y0)
            peaks = peaksCollection.get_segments()
            peaks.append(peak.coords)
            peaksInSegment.append(i)
            peaksCollection.set_segments(peaks)
            fig.canvas.draw()

    # peaks
    cont, ind = peaksCollection.contains(event)
    if cont:
        i = ind["ind"][0]
        #print("peak", ind, i)
        if event.button is MouseButton.RIGHT:
            peaks = peaksCollection.get_segments()
            del peaks[i]
            del peaksInSegment[i]
            peaksCollection.set_segments(peaks)
            fig.canvas.draw()

#=======================================================
def onkeypress(event):
    if event.key == 'x':
        peaks = peaksCollection.get_segments()
        for i,p in enumerate(peaks):
            print(i,  peaksInSegment[i], p[0])

#=======================================================
fig.canvas.mpl_connect('button_press_event', onpress)
fig.canvas.mpl_connect('key_press_event', onkeypress)

plt.show()

