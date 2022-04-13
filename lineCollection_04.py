
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from shapely.geometry import Point,LineString
from matplotlib.backend_bases import MouseButton

import sys

#=======================================================
fig, ax = plt.subplots(1, 1, figsize=(8,6))

ax.set_aspect('equal')
ax.grid()
ax.set_facecolor('lightgray')

ax.set_xlim(0,10)
ax.set_ylim(0,10)

#=======================================================
segmentsList = []
ticksCollectionList = []

segment, = ax.plot([2,6],[5,8] , color='r')
segmentsList.append(segment)
ticksCollectionList.append(LineCollection([], color='b'))
ax.add_collection(ticksCollectionList[0])

segment, = ax.plot([1,8],[1,8] , color='r')
segmentsList.append(segment)
ticksCollectionList.append(LineCollection([], color='b'))
ax.add_collection(ticksCollectionList[1])

segment, = ax.plot([2,8],[2,2] , color='r')
segmentsList.append(segment)
ticksCollectionList.append(LineCollection([], color='b'))
ax.add_collection(ticksCollectionList[2])

tickOver = None

#=======================================================
def draw_ticks(segment, xList, yList, length=0.25):
    xdata = list(segment.get_xdata())
    ydata = list(segment.get_ydata())
    line = LineString([(xdata[0], ydata[0]), (xdata[1], ydata[1])])
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

a = draw_ticks(segmentsList[1], [3,4,5], [3,4,5])
ticksCollectionList[1].set_segments(a)

#=======================================================
def onpress(event):
    # segments
    for n, segment in enumerate(segmentsList):
        cont, ind = segment.contains(event)
        if cont:
            #print("segment", n)
            if event.button is MouseButton.LEFT:
                xdata = list(segment.get_xdata())
                ydata = list(segment.get_ydata())
                line = LineString([(xdata[0], ydata[0]), (xdata[1], ydata[1])])
                # Closest point on the line
                point = Point(event.xdata, event.ydata)
                newPoint = line.interpolate(line.project(point))
                tick = draw_ticks(segment, [newPoint.coords[0][0]], [newPoint.coords[0][1]])
                ticks = ticksCollectionList[n].get_segments()
                ticks.append(tick[0])
                ticksCollectionList[n].set_segments(ticks)
                sortTicksFromSegment(n)
                fig.canvas.draw()
            break

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
    segment = segmentsList[segmentNum]
    ticks = ticksCollectionList[segmentNum].get_segments()

    xdata = list(segment.get_xdata())
    ydata = list(segment.get_ydata())
    ticksDistance = []
    for p in ticks:
        distance = Point(xdata[0], ydata[0]).distance(Point(p[1]))     # p[1] is on the segment
        ticksDistance.append(distance)
    sortIndices = np.argsort(ticksDistance)
    ticksSorted = np.array(ticks)[sortIndices]

    ticksCollectionList[segmentNum].set_segments(ticksSorted)

#=======================================================
fig.canvas.mpl_connect('button_press_event', onpress)
fig.canvas.mpl_connect('key_press_event', onkeypress)
fig.canvas.mpl_connect('motion_notify_event', onmotion)    

plt.show()

