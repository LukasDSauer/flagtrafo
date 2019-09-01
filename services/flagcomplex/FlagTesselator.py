#  Developed by Lukas Sauer at the Heidelberg Institute of Theoretical Studies on 4/29/19, 11:38 AM.
#  Contact: lukas.sauer@h-its.org.
#  Last modified on 4/29/19, 11:38 AM.
#  (C) 2019. All rights reserved.

import numpy as np

from scipy.spatial import ConvexHull


import drawSvg as draw
import string

from ProjGeometryUtility import get_reflection, connecting_line

from DrawingUtility import draw_path


class FlagTesselator:
    def __init__(self, flagcomplex, steps=3):
        """

        :param flagcomplex: an object of the FlagComplex class
        :param steps: an integer, the number of steps that tesselation is iterated
        """
        # The FlagComplex object containing all the flags
        self.flagcomplex = flagcomplex
        # The number of flags
        self.n = self.flagcomplex.n
        # The number of iterations of the tesselation
        self.steps = steps
        # The initial polygon
        self.initial = None
        # This will be the connecting lines between p_i-1 and p_i. Along these lines, the reflections will be performed.
        self.connecting_ls = None
        # The intersection points between the flags
        self.qs = None
        # The reflection maps
        self.reflections = None
        # The different reflections generate a group. This group can be represented by words, where each reflection
        # is represented by a different letter.
        self.words = None
        self.letters = None
        # The important maps for the tesselation are represented by words up to a certain length, the number of steps.
        self.maps = None

    def refresh_setup(self):
        """
        Makes sure all the coordinates in the flag complex are up to date. Then it computes the necessary reflections and
        the words up to the length = self.steps. Finally, it computes the maps that are represented by those words.

        :return:
        """
        self.flagcomplex.refresh_setup()
        self.initial = np.array([p for p in self.flagcomplex.ps])
        self.qs = self.flagcomplex.qs
        # The lines we want to reflect along are the connecting lines of points p_i and p_i-1.
        self.connecting_ls = [connecting_line(self.flagcomplex.ps[i - 1], self.flagcomplex.ps[i]) for i in range(self.n)]
        self.compute_reflections()
        self.compute_words()
        self.compute_maps_from_words()


    def generate_tesselation(self):
        """
        This function performs the tesselation. It returns a two-dimensional projection of the initial polygon, the
        convex hull of the tesselation, and finally a dictionary of tiles (the reflections of the initial polygon,
        indexed by the words which generate them)

        :return: a triple of objects, the first is a list of numpy arrays, the second as well, the third is a dictionary
        of lists of numpy arrays
        """
        self.refresh_setup()
        tiles = dict()
        # Map the initial polygon according to the different words.
        for word in self.words:
            tiles[word] = [self.map_point_to_two_dim(self.maps[word], y) for y in self.initial]
        # Compute the convex hull.
        maxlwords = np.array([tiles[x] for x in self.words if len(x) == self.steps])
        maxlwords = maxlwords.reshape(-1, 2)
        cv = ConvexHull([x[:2] for x in maxlwords])
        hull_points = cv.vertices
        hull = [maxlwords[h] for h in hull_points]

        return [self.flagcomplex.get_two_dimensional_point(x) for x in self.initial], hull, tiles

    def print_image(self, color="#006666", with_hull=True, with_initial=True, with_tiles = False, without_points=True, fill_convex = False, old=None,
                    data=None, image_offset=0):
        """
        This function performs the tesselation and draws it. It can also draw on existing data.

        :param color: the color used for drawing the convex set
        :param with_hull: a boolean value. Do you want to draw the complex hull?
        :param with_initial: a boolean value. Do you want to highlight the initial polygon?
        :param without_points: a boolean value. Do you want to highlight the points of the polygons?
        :param old: an existing drawSvg object that you want to draw on
        :param data: existing data for the initial polygon, for the convex hull and for the tiles
        :param image_offset:
        :return:
        """
        if data is not None:
            ini, hull, tiles = data[0], data[1], data[2]
        else:
            ini, hull, tiles = self.generate_tesselation()
        if old is not None:
            d = old
        else:
            d = self.generate_canvas(hull, image_offset)
        if with_tiles:
            for word in self.words:
                draw_path(d, tiles[word], col=color, wop=without_points, fill=0.1, width = 0.2)
        if with_initial:
            draw_path(d, ini, col=color, wop=without_points, fill=1, width=0)
        if with_hull:
            if fill_convex:
                fill = 0.2
            else:
                fill = 0
            draw_path(d, hull, col =color, wop= without_points, fill=fill, width=0.4)
        # # d.setPixelScale(2)  # Set number of pixels pert[0][0] geometry unit

        return d

    def map_point_to_two_dim(self, m, x):
        """
        Transforms a projective point with the projective transformation m and then projects it to two dimensions.

        :param m: a projective transformation (3x3 dim np-array)
        :param x: a projective point (three dim np-array)
        :return: a two-dim np-array
        """
        point = np.matmul(m, x)
        return self.flagcomplex.get_two_dimensional_point(point)

    def set_steps(self, s):
        """
        Set the number of steps you want to iterate.

        :param s:
        :return:
        """
        self.steps = s

    def compute_reflections(self):
        """
        Computes the reflections along all connection lines with the respective intersection point.

        :return:
        """
        self.reflections = np.array([get_reflection(self.connecting_ls[i], self.qs[i]) for i in range(self.n)])

    def compute_words(self):
        """
        Computes all the relevant words up to the length self.steps. Words with double letters are irrelevant because
        the letters cancel out.

        :return:
        """
        letters = list(string.ascii_lowercase)[:self.n]
        words = list(string.ascii_lowercase)[:self.n]
        for i in range(1, self.n):
            tmp = words.copy()
            for w in tmp:
                for l in letters:
                    # as l*l = e, we don't need double letters in our words.
                    if w[-1] != l:
                        words.append(w + l)
        self.words = words
        self.letters = letters

    def compute_maps_from_words(self):
        """
        Computes the respective projective transformation from each word.

        :return:
        """
        self.maps = dict()

        reflection_by_letter = dict()
        for i in range(self.n):
            reflection_by_letter[self.letters[i]] = self.reflections[i]

        for word in self.words:
            current = np.eye(3)
            for w in reversed(word):
                current = np.matmul(reflection_by_letter[w], current)
            self.maps[word] = current

    def generate_canvas(self, hull, imageOffset):
        """
        Generates a drawSvg object that the whole tesselation fits on. Currently, this is not working.

        :param hull_to_array:
        :param imageOffset:
        :return:
        """
        hull_to_array = np.array([x for x in hull])
        hminx, hmaxx = np.min(hull_to_array[:, 0]), np.max(hull_to_array[:, 0])
        hminy, hmaxy = np.min(hull_to_array[:, 1]), np.max(hull_to_array[:, 1])
        # width scaled by 100
        width = 100 * (hmaxx - hminx)
        height = 100 * (hmaxy - hminy)
        maxscale = np.max([width, height]) + imageOffset
        # mid scaled by 100
        hmidx = 50 * (hminx + hmaxx)
        hmidy = 50 * (hminy + hmaxy)
        d = draw.Drawing(maxscale, maxscale, origin=(hmidx - 0.5 * maxscale, hmidy - 0.5 * maxscale))
        # background
        d.append(draw.Rectangle(hmidx - 0.5 * maxscale, hmidy - 0.5 * maxscale, maxscale, maxscale, fill='#ffffff'))

        return d
