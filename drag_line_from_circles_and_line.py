import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D
import cv2

imageFileName = "BEL17-2-2_1.66x_milieu0001.png"

img = cv2.imread(imageFileName)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

point1 = [500,500]
point2 = [700,200]
point_alpha_default = 0.4
point_alpha_pick = 0.1

currently_dragging = False
current_artist = None
offset = [0,0]

def on_press(event):
    global currently_dragging
    currently_dragging = True

def on_release(event):
    global current_artist, currently_dragging
    current_artist = None
    currently_dragging = False

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
   
    plt.draw()

#================================================
fig, ax = plt.subplots()

ax.set_aspect('equal')
ax.imshow(gray, cmap='gray')

point1_object = patches.Circle(point1, radius=50, fc='r', 
        alpha=point_alpha_default, transform=ax.transData, label="point1")
point2_object = patches.Circle(point2, radius=50, fc='r', 
        alpha=point_alpha_default, transform=ax.transData, label="point2")

ax.add_patch(point1_object)
ax.add_patch(point2_object)

line_object = ax.plot([point1[0], point2[0]], [point1[1], point2[1]], 
            alpha=0.8, c='r', lw=2, picker=True)

point1_object.set_picker(5)
point2_object.set_picker(5)
line_object[0].set_pickradius(5)

for canvas in set(artist.figure.canvas for artist in [point1_object, point2_object, line_object[0]]):
    canvas.mpl_connect('button_press_event', on_press)
    canvas.mpl_connect('button_release_event', on_release)
    canvas.mpl_connect('pick_event', on_pick)
    canvas.mpl_connect('motion_notify_event', on_motion)

plt.show()

