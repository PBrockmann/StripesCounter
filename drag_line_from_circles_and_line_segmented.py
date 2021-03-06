import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D
import cv2

#------------------------------------------------
imageFileName = "BEL17-2-2_1.66x_milieu0001.png"
img = cv2.imread(imageFileName)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#------------------------------------------------
listLabelPoints = []
point_alpha_default = 0.8
mousepress = None
currently_dragging = False
current_artist = None
offset = [0,0]

#------------------------------------------------
def on_press(event):
    global currently_dragging
    global mousepress
    currently_dragging = True
    if event.button == 3:
        mousepress = "right"
    elif event.button == 1:
        mousepress = "left"

#------------------------------------------------
def on_release(event):
    global current_artist, currently_dragging
    current_artist = None
    currently_dragging = False

#------------------------------------------------
def on_pick(event):
    global current_artist, offset, n
    global listLabelPoints
    if current_artist is None:
        current_artist = event.artist
        #print("pick ", current_artist)
        if isinstance(event.artist, patches.Circle):
            if event.mouseevent.dblclick:
                if mousepress == "right":
                    #print("double click right")
                    if len(ax.patches) > 2:
                        #print("\ndelete", event.artist.get_label())
                        event.artist.remove()
                        xdata = list(line_object[0].get_xdata())
                        ydata = list(line_object[0].get_ydata())
                        for i in range(0,len(xdata)):
                            if event.artist.get_label() == listLabelPoints[i]:
                                xdata.pop(i) 
                                ydata.pop(i) 
                                listLabelPoints.pop(i)
                                break
                        #print('--->', listLabelPoints)
                        line_object[0].set_data(xdata, ydata)
                        plt.draw()
            else:
                x0, y0 = current_artist.center
                x1, y1 = event.mouseevent.xdata, event.mouseevent.ydata
                offset = [(x0 - x1), (y0 - y1)]
        elif isinstance(event.artist, Line2D):
            if event.mouseevent.dblclick:
                if mousepress == "left":
                    #print("double click left")
                    n = n+1
                    x, y = event.mouseevent.xdata, event.mouseevent.ydata
                    newPointLabel = "point"+str(n)
                    point_object = patches.Circle([x, y], radius=50, color='r', fill=False, lw=2,
                            alpha=point_alpha_default, transform=ax.transData, label=newPointLabel)
                    point_object.set_picker(5)
                    ax.add_patch(point_object)
                    xdata = list(line_object[0].get_xdata())
                    ydata = list(line_object[0].get_ydata())
                    #print('\ninit', listLabelPoints)
                    pointInserted = False
                    for i in range(0,len(xdata)-1):
                        #print("--> testing inclusion %s in [%s-%s]" 
                        #        %(newPointLabel, listLabelPoints[i], listLabelPoints[i+1]))
                        #print('----->', min(xdata[i],xdata[i+1]), '<', x, '<', max(xdata[i],xdata[i+1]))
                        #print('----->', min(ydata[i],ydata[i+1]), '<', y, '<', max(ydata[i],ydata[i+1]))
                        if x > min(xdata[i],xdata[i+1]) and x < max(xdata[i],xdata[i+1]) and \
                           y > min(ydata[i],ydata[i+1]) and y < max(ydata[i],ydata[i+1]) :
                            xdata.insert(i+1, x)
                            ydata.insert(i+1, y)
                            listLabelPoints.insert(i+1, newPointLabel)
                            pointInserted = True
                            #print("include", newPointLabel)
                            break
                    line_object[0].set_data(xdata, ydata)
                    #print('final', listLabelPoints)
                    plt.draw()
                    if not pointInserted:
                        print("Error: point not inserted")
            else:
                xdata = event.artist.get_xdata()
                ydata = event.artist.get_ydata()
                x1, y1 = event.mouseevent.xdata, event.mouseevent.ydata
                offset = xdata[0] - x1, ydata[0] - y1

#------------------------------------------------
def on_motion(event):
    global current_artist
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
        #print("moving", current_artist.get_label())
        xdata = list(line_object[0].get_xdata())
        ydata = list(line_object[0].get_ydata())
        for i in range(0,len(xdata)): 
            if listLabelPoints[i] == current_artist.get_label():
                xdata[i] = cx
                ydata[i] = cy
                break
        line_object[0].set_data(xdata, ydata)
    elif isinstance(current_artist, Line2D):
        xdata = list(line_object[0].get_xdata())
        ydata = list(line_object[0].get_ydata())
        xdata0 = xdata[0]
        ydata0 = ydata[0]
        for i in range(0,len(xdata)): 
                xdata[i] = event.xdata + dx + xdata[i] - xdata0
                ydata[i] = event.ydata + dy + ydata[i] - ydata0 
        line_object[0].set_data(xdata, ydata)
        for p in ax.patches:
            pointLabel = p.get_label()
            i = listLabelPoints.index(pointLabel) 
            p.center = xdata[i], ydata[i]
    plt.draw()

#================================================
fig, ax = plt.subplots()

ax.set_aspect('equal')
ax.imshow(gray, cmap='gray')

point1 = [100,100]
point1_object = patches.Circle(point1, radius=50, color='r', fill=False, lw=2,
        alpha=point_alpha_default, transform=ax.transData, label="point1")
point1_object.set_picker(5)
listLabelPoints.append("point1")

point2 = [700,900]
point2_object = patches.Circle(point2, radius=50, color='r', fill=False, lw=2,
        alpha=point_alpha_default, transform=ax.transData, label="point2")
point2_object.set_picker(5)
listLabelPoints.append("point2")

n = 2

ax.add_patch(point1_object)
ax.add_patch(point2_object)

line_object = ax.plot([point1[0], point2[0]], [point1[1], point2[1]], 
            alpha=0.8, c='r', lw=2, picker=True, zorder=1)
line_object[0].set_pickradius(5)

fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('button_release_event', on_release)
fig.canvas.mpl_connect('pick_event', on_pick)
fig.canvas.mpl_connect('motion_notify_event', on_motion)

plt.show()
