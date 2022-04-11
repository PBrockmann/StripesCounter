
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
ax.set_facecolor('lightgray')

ax.set_xlim(0,10)
ax.set_ylim(0,10)

#=======================================================
segmentsCollection = LineCollection([], color='r')
ax.add_collection(segmentsCollection)

ticksCollectionList = []

#----------------------------
segs2 = [ [[2,5],[6,8]], [[1,1],[8,8]], [[2,2],[8,2]] ]
segmentsCollection.set_segments(segs2)

ticksCollectionList.append(LineCollection([], color='b'))
ax.add_collection(ticksCollectionList[0])

ticksCollectionList.append(LineCollection([], color='b'))
ax.add_collection(ticksCollectionList[1])

ticksCollectionList.append(LineCollection([], color='b'))
ax.add_collection(ticksCollectionList[2])

tickOver = None

#=======================================================
def draw_ticks(segment, xList, yList, length=0.25):
    line = LineString(segment)   
    left = line.parallel_offset(length, 'left')
    right0 = line.parallel_offset(length, 'right')
    right = LineString([right0.boundary.geoms[1], right0.boundary.geoms[0]]) # flip because 'right' orientation
    ticks = []
    for i,x in enumerate(xList):
        p = Point(xList[i],yList[i])
        a = left.interpolate(line.project(p))
        b = right.interpolate(line.project(p))
        ticks.append(LineString([a, p, b]).coords)           # keep p point to sort from distance later
    return ticks

a = draw_ticks(segmentsCollection.get_segments()[1], [3,4,5], [3,4,5])
ticksCollectionList[1].set_segments(a)

#=======================================================
def draw_tick(segment, x, y, length=0.25):
    line = LineString(segment)   
    left = line.parallel_offset(length, 'left')
    right0 = line.parallel_offset(length, 'right')
    right = LineString([right0.boundary.geoms[1], right0.boundary.geoms[0]]) # flip because 'right' orientation
    p = Point(x,y)
    a = left.interpolate(line.project(p))
    b = right.interpolate(line.project(p))
    line  = LineString([a, p, b])           # keep p point to sort from distance later
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
            tick = draw_tick(segment, x0, y0)
            ticks = ticksCollectionList[i].get_segments()
            ticks.append(tick.coords)
            ticksCollectionList[i].set_segments(ticks)
            sortTicksFromSegment(i)
            fig.canvas.draw()

    # ticks
    for ticksCollection in ticksCollectionList:
        cont, ind = ticksCollection.contains(event)
        if cont:
            i = ind["ind"][0]
            #print("tick", ind, i)
            if event.button is MouseButton.RIGHT:
                ticks = ticksCollection.get_segments()
                del ticks[i]
                ticksCollection.set_segments(ticks)
                fig.canvas.draw()
                break

#=======================================================
def onkeypress(event):
    if event.key == 'x':
        for i,ticksCollection in enumerate(ticksCollectionList):
            ticks = ticksCollection.get_segments()
            for n,p in enumerate(ticks):
                print(i, n, p[1])

#=======================================================
def onmotion(event):
    global tickOver

    if tickOver != None:
        tickOver.remove()
        tickOver = None
        fig.canvas.draw()

    # ticks
    for ticksCollection in ticksCollectionList:
        cont, ind = ticksCollection.contains(event)
        if cont:
            i = ind["ind"][0]
            tick = ticksCollection.get_segments()[i]
            tickOver, = ax.plot([tick[0][0],tick[-1][0]],[tick[0][1],tick[-1][1]], c="yellow", alpha=1, lw=5, zorder=0)
            fig.canvas.draw()
            break

#=======================================================
def sortTicksFromSegment(segmentNum):
    segment = segmentsCollection.get_segments()[segmentNum]
    ticks = ticksCollectionList[segmentNum].get_segments()

    ticksDistance = []
    for p in ticks:
        distance = Point(segment[0][0], segment[0][1]).distance(Point(p[1]))     # p[1] is on the segment
        ticksDistance.append(distance)
    sortIndices = np.argsort(ticksDistance)
    ticksSorted = np.array(ticks)[sortIndices]

    ticksCollectionList[segmentNum].set_segments(ticksSorted)

#=======================================================
fig.canvas.mpl_connect('button_press_event', onpress)
fig.canvas.mpl_connect('key_press_event', onkeypress)
fig.canvas.mpl_connect('motion_notify_event', onmotion)    

plt.show()

