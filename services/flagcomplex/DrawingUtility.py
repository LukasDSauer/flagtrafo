#  Developed by Lukas Sauer at the Heidelberg Institute of Theoretical Studies on 2/20/19 10:51 AM.
#  Contact: lukas.sauer@h-its.org.
#  Last modified on 2/20/19 10:51 AM.
#  (C) 2019. All rights reserved.

import drawSvg as draw
import numpy as np
from numpy import linalg as la
import colorsys as cl

# Helper functions mainly written by Sven Gruetzmacher
# All this function take two-dimensional euclidean real coordinates

def draw_flag(d, p, dir, col = "black", t = 30, wop=False, label = ""):
    """
    Draws a flag defined by the point p and another point dir to define the line.

    :param d: a drawSvg drawing for the output
    :param p: the point p
    :param dir: the second point on the line
    :param col: a color that is accepted by colorsys
    :param t: the length of the line
    :return:
    :author: Sven Gruetzmacher
    """
    if not wop:
        drawpt(d, p, col=col)
    line_direction = dir - p
    if la.norm(line_direction) == 0:
        print("Warning: Trivial line detected!")
    else:
        # If the points dir and p are very close to each other, the lines will get very short.
        # By appropriately making t larger, we circumvent this problem.
        if la.norm(line_direction) < 1.0:
            t = t*1/la.norm(line_direction)
        drawl(d, p + t*line_direction, p - t*line_direction, col=col)

        if label != "":
            d.append(draw.Text(label, 10, 100 * p[0], 100 * p[1], center=3, fill='blue'))

def drawpt(d, x, col="blue"):
    d.append(draw.Circle(100 * x[0], 100 * x[1], 2, fill=col, stroke_width=1, stroke=col))


def drawcirc(d, x, r, col="white"):
    d.append(draw.Circle(100 * x[0], 100 * x[1], 100 * r, fill=col, stroke_width=1, stroke=col))


def drawl(d, x, y, col="black"):
    d.append(draw.Lines(100 * x[0], 100 * x[1], 100 * y[0], 100 * y[1], close=False, stroke=col))


def drawtri(d, p, col="blue", pts=True, fill=0.0):
    if pts:
        for x in p:
            drawpt(d, x, col)
    # for i in range(3):
    #    drawl(d,p[i],p[(i+1)%3],col)
    x = p[0]
    y = p[1]
    z = p[2]
    d.append(draw.Lines(100 * x[0], 100 * x[1], \
                        100 * y[0], 100 * y[1], \
                        100 * z[0], 100 * z[1], \
                        close=True, stroke=col, fill=col, fill_opacity=str(fill)))


def drawquad(d, p, col="blue", pts=False, fill=0.0):
    if pts:
        for x in p:
            drawpt(d, x, col)
    # for i in range(3):
    #    drawl(d,p[i],p[(i+1)%3],col)
    x = p[0]
    y = p[1]
    z = p[2]
    v = p[3]
    d.append(draw.Lines(100 * x[0], 100 * x[1], \
                        100 * y[0], 100 * y[1], \
                        100 * z[0], 100 * z[1], \
                        100 * v[0], 100 * v[1], \
                        close=True, stroke=col, fill=col, stroke_opacity=str(fill), fill_opacity=str(fill)))


def draw_polygon(d, polygon, col=["#7575ff", "#75ff75", "#ff7575"], wop = True):
    """
    This function connects the list of lists of points in polygon by lines and adds it to the drawing d.
    For each list of points in polygon, a different colour can be used.
    :param d: A drawSvg drawing
    :param polygon: A list of points
    :param col: A list of colours
    :return:
    :author: Lukas Sauer
    """
    length = len(polygon)

    for i in range(length):
        for j in range(len(polygon[i])-1):
            drawl(d, polygon[i][j], polygon[i][j+1], col=col[i%length])
            if not wop:
                drawpt(d, polygon[i][j], col=col[i%length])
        if not wop:
            drawpt(d, polygon[i][-1], col=col[i % length])
        drawl(d, polygon[i][-1], polygon[(i+1)%length][0], col[i%length])


def draw_path(d, points, col="blue", fillcol=None, wop=True, fill=0.0, width=2):
    """
    Draws a closed path through the points, and fills it with a color.

    :param d: a DrawSvg object
    :param points:
    :param col:
    :param fillcol:
    :param wop:
    :param fill:
    :param width:
    :return:
    :author: Sven Gruetzmacher.
    """
    if fillcol is None:
        fillcol = col
    if not wop:
        for x in points:
            drawpt(d, x, col)
    pa = draw.Path(stroke=col, stroke_width=width,
                   fill=fillcol, fill_opacity=fill)
    pa.M(100 * points[0][0], 100 * points[0][1])  # Start path at point (-30, 5)
    for i in range(1, len(points)):
        pa.L(100 * points[i][0], 100 * points[i][1])  # Draw line to (60, 30)
    pa.L(100 * points[0][0], 100 * points[0][1])    # Draw line to start
    d.append(pa)


