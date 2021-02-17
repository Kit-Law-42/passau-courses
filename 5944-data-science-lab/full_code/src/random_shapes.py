"""
This file is primary taken from https://stackoverflow.com/questions/50731785/create-random-shape-contour-using-matplotlib
"""
#
import os

import cv2
import numpy as np
from numpy import random
from scipy.special import binom
import matplotlib as mpl
import matplotlib.pyplot as plt
import tkinter

bernstein = lambda n, k, t: binom(n, k) * t ** k * (1. - t) ** (n - k)


def bezier(points, num=200):
    number_of_points = len(points)
    t = np.linspace(0, 1, num=num)
    curve = np.zeros((num, 2))

    # Calculate the outer product of all vectors.
    for i in range(number_of_points):
        curve += np.outer(bernstein(number_of_points - 1, i, t), points[i])
    return curve


class Segment():
    def __init__(self, p1, p2, angle1, angle2, **kw):
        self.p1 = p1;
        self.p2 = p2
        self.angle1 = angle1;
        self.angle2 = angle2
        self.numpoints = kw.get("numpoints", 100)
        r = kw.get("r", 0.3)
        d = np.sqrt(np.sum((self.p2 - self.p1) ** 2))
        self.r = r * d
        self.p = np.zeros((4, 2))
        self.p[0, :] = self.p1[:]
        self.p[3, :] = self.p2[:]
        self.calc_intermediate_points(self.r)

    def calc_intermediate_points(self, r):
        self.p[1, :] = self.p1 + np.array([self.r * np.cos(self.angle1),
                                           self.r * np.sin(self.angle1)])
        self.p[2, :] = self.p2 + np.array([self.r * np.cos(self.angle2 + np.pi),
                                           self.r * np.sin(self.angle2 + np.pi)])
        self.curve = bezier(self.p, self.numpoints)


def get_curve(points, **kw):
    segments = []
    for i in range(len(points) - 1):
        seg = Segment(points[i, :2], points[i + 1, :2], points[i, 2], points[i + 1, 2], **kw)
        segments.append(seg)
    curve = np.concatenate([s.curve for s in segments])
    return segments, curve


def ccw_sort(p):
    d = p - np.mean(p, axis=0)
    s = np.arctan2(d[:, 0], d[:, 1])
    return p[np.argsort(s), :]


def get_bezier_curve(a, rad=0.2, edgy: float = 0):
    """ given an array of points *a*, create a curve through
    those points.
    *rad* is a number between 0 and 1 to steer the distance of
          control points.
    *edgy* is a parameter which controls how "edgy" the curve is,
           edgy=0 is smoothest."""
    p = np.arctan(edgy) / np.pi + .5
    a = ccw_sort(a)
    a = np.append(a, np.atleast_2d(a[0, :]), axis=0)
    d = np.diff(a, axis=0)
    ang = np.arctan2(d[:, 1], d[:, 0])
    f = lambda ang: (ang >= 0) * ang + (ang < 0) * (ang + 2 * np.pi)
    ang = f(ang)
    ang1 = ang
    ang2 = np.roll(ang, 1)
    ang = p * ang1 + (1 - p) * ang2 + (np.abs(ang2 - ang1) > np.pi) * np.pi
    ang = np.append(ang, [ang[0]])
    a = np.append(a, np.atleast_2d(ang).T, axis=1)
    s, c = get_curve(a, r=rad, method="var")
    x, y = c.T
    return x, y, a


def get_random_points(n=5, scale=0.8, mindst=None, rec=0):
    """ create n random points in the unit square, which are *mindst*
    apart, then scale them."""
    mindst = mindst or .7 / n
    a = np.random.rand(n, 2)
    d = np.sqrt(np.sum(np.diff(ccw_sort(a), axis=0), axis=1) ** 2)
    if np.all(d >= mindst) or rec >= 200:
        return a * scale
    else:
        return get_random_points(n=n, scale=scale, mindst=mindst, rec=rec + 1)


def generate(number_of_masks_to_generate: int, path: str, start_index: int = 0, position: tuple = None, size: tuple = (256, 256),
             number_of_points: int = None, rad: float = 0.2, edgy: float = 0.9, picture_scale: int = None):
    """
    Generates masks
    :param start_index: first image will be named "start_index.png"
    :param path: the path where to save the images.
    :param number_of_masks_to_generate: the number of images to generate.
    :param position: box coordinate where to draw the mask [x1, x2, y1, y2].
    :param size: picture size (width, height).
    :param number_of_points: number of points used to generate the mask, more points means more complex shape.
    :param rad: controls the angles.
    :param edgy: controls how smooth is the shape. 0 is the smoothest.
    :param picture_scale: proportion of the mask compared to the image size.
    :return:
    """
    mpl.use("Agg")
    mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=["#FFFFFF"])
    root = tkinter.Tk()
    my_dpi = root.winfo_fpixels('1i')

    (w, h) = size
    random_scale = False
    random_position = False
    random_point_number = False

    # Set scale, point_number and position to random if no input exists
    if picture_scale is None:
        random_scale = True
    if position is None:
        random_position = True
    if number_of_points is None:
        random_point_number = True

    for index in range(start_index, number_of_masks_to_generate):
        if random_scale:
            picture_scale = random.randint(low=1, high=50)

        if random_position:
            # Calculate the minimum height and width needed
            min_width_needed = int(w / 100 * picture_scale)
            min_height_needed = int(h / 100 * picture_scale)
            #
            starting_point_x = random.randint(10, w - min_width_needed - 10)
            starting_point_y = random.randint(10, h - min_height_needed - 10)

            position = [starting_point_x, starting_point_x + min_width_needed, starting_point_y,
                        starting_point_y + min_height_needed]

        if random_point_number:
            number_of_points = random.randint(8, 26)

        a = get_random_points(n=number_of_points, scale=1)
        x, y, _ = get_bezier_curve(a, rad=rad, edgy=edgy)

        # Draw first patch and save it
        fig = plt.figure(figsize=(w / my_dpi, h / my_dpi), dpi=my_dpi)
        fig.patch.set_facecolor('#000000')
        plt.ioff()
        plt.axis('off')
        plt.fill_between(x, y)
        plt.plot(x, y, '#FFFFFF')
        fig.savefig("tmp.png", dpi=my_dpi)

        # Load the patch
        image = cv2.imread("tmp.png")

        # Scale it and plot it.
        fig2 = plt.figure(figsize=(w / my_dpi, h / my_dpi), dpi=my_dpi)
        fig2.patch.set_facecolor('#000000')
        ax = plt.axes([0, 0, 1, 1], frameon=False)
        ax.set_xlim(0, w)
        ax.set_ylim(0, h)
        plt.axis('off')
        plt.imshow(image, extent=position)

        fig2.savefig(os.path.join(path, str(index) + ".png"), dpi=my_dpi)
        os.remove("tmp.png")
