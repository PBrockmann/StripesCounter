# test all imports needed


import sys, os

import re

from PyQt5.Qt import Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.transforms import Bbox
from matplotlib.collections import LineCollection
import matplotlib.patches as patches
import matplotlib.pyplot as plt

from skimage.measure import profile_line
import peakutils

import numpy as np
import cv2
from shapely.geometry import Point, LineString

import datetime
import pandas as pd

import cairo
import xml.dom.minidom
