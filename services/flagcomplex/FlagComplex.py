#  Developed by Lukas Sauer at the Heidelberg Institute of Theoretical Studies on 2/19/19 5:12 PM.
#  Contact: lukas.sauer@h-its.org.
#  Last modified on 2/19/19 5:12 PM.
#  (C) 2019. All rights reserved.

import numpy as np
import numpy.linalg as la

from services.flagcomplex.ProjGeometryUtility import project_point, line_intersection, connecting_line, transform_four_points
from services.flagcomplex.EuklGeometryUtility import rotate_vectors, get_ellipse_from_quadratic_form
from services.flagcomplex.DrawingUtility import drawl, draw_flag, drawtri, draw_polygon


class FlagComplex:

    """
    A flag complex is tuple of n flags in the real projective plane RP^2.
    A flag is a projective line with a point lying on that line.
    """

    def __init__(self):
        # Number of flags
        self.n = 0

        # The points p_i
        # (A list of three dimensional numpy arrays)
        self.ps = []
        # The line on which p_i lies can be defined by another point giving a "direction".
        self.ds = []
        # Alternatively, a projective line can be defined as a linear form l_i, as there is a 1-1-correspondence
        # between one-dimensional subspaces of the space of linear forms, and projective lines. (Indeed, a projective
        # line is a plane in R^3, i.e. the kernel of a non-trivial linear form).
        # (A list of three dimensional numpy arrays)
        self.ls = []

        # (A list of three dimensional numpy arrays)
        self.qs = []

        # The normal vector of the plane onto which we project for visualisation (a numpy array)
        self.projection_plane = None

        # The two-dimensional projected versions of ps and qs for visualisation purposes.
        self.drawps = []
        self.drawqs = []

        self.drawps_at_infinity = []
        self.drawqs_at_infinity = []
        
        # A triangulation of the flag complex, i.e. a list of lists of three integers (indexing point self.ps)
        self.triangles = []
        #self.internal_edges = []

    def add_flag(self, p, direction):
        """
        A flag consists of a point p and a line on which the point lies. In our case, the line is simply defined by
        another point direction (the line is connecting the points p and direction).

        We are in two-dimensional projective space, so p and direction should be numpy arrays with three coordinates.
        :param p: The point p (a numpy array with three coordinates).
        :param direction: The point direction (a numpy array with three coordinates).
        :return: No return value.
        """
        self.n = self.n + 1

        self.ps.append(p)
        self.ds.append(direction)
        # The linear form defining the line on which p lies can be expressed as a vector which is perpendicular to
        # both p and direction.
        l = np.cross(p, direction)
        self.ls.append(l)

    def refresh_setup(self):
        """
        The setup of the flag complex is refreshed by calculating the linear forms l_i defining the projective lines
        and the intersection points q_i of the projective lines l_i.

        :return:
        """
        self.ls = [np.cross(self.ps[i], self.ds[i]) for i in range(self.n)]
        # The intersection between the two projective lines l_i and l_i-1 (i.e. planes defined via a normal vector) is
        # a projective point (i.e. a line), which can be expressed by a vector perpendicular to the two normal vectors.
        # TODO: Maybe range(1,self.n)??? Check this out later.
        self.qs = [line_intersection(self.ls[i-1], self.ls[i]) for i in range(self.n)]


    def set_projection_plane(self, vector):
        """
        The real projective plane is the space of lines through the origin in R^3. It can be visualized by projecting
        these lines to an affine plane with distance 1 to the origin.

        We define this affine plane via its normal vector.

        :param vector: The normal vector on the projection plane (a numpy array with three coordinates).
        :return:
        """
        self.projection_plane = vector/la.norm(vector)

    def draw_complex(self):
        """
        For visualizing the flag complex, we want two-dimensional coordinates. We do this by projecting to the
        projection plane defined and then rotate this plane to the affine plane with normal vector [0,0,1].

        We leave the third coordinate (i.e. 1) and thus obtain two-dimensional coordinates.
        :return:
        """
        assert self.projection_plane is not None, \
            "Attention! The projection plane has not been defined."
        
        rotation_matrix = rotate_vectors(self.projection_plane, np.array([0, 0, 1]))

        self.refresh_setup()

        self.drawps = []
        self.drawps_at_infinity = []

        for i in range(self.n):
            p = self.ps[i]
            # We  basically do get_two_dimensional_point for every single point. But we have to generate the rotation
            # matrix just once.
            # Project point to the projection plane
            try:
                drawp = project_point(self.projection_plane, p)
                # Rotate the projected point to the affine plane with normal vector [0, 0, 1].
                drawp = np.matmul(rotation_matrix, drawp)
                self.drawps.append(drawp[:2])
            except AssertionError:
                print("Warning! The point " + str(p)  + " is on the boundary plane. Therefore it cannot be projected.")
                self.drawps_at_infinity.append(i)
                self.drawps.append(None)

        self.drawqs = []
        self.drawqs_at_infinity =[]

        for i in range(self.n):
            q = self.qs[i]
            try:
                drawq = project_point(self.projection_plane, q)
                drawq = np.matmul(rotation_matrix, drawq)
                self.drawqs.append(drawq[:2])
            except AssertionError:
                print("Warning! The point " + str(q) + " is on the boundary plane. Therefore it cannot be projected.")
                self.drawqs_at_infinity.append(i)
                self.drawqs.append(None)


    def get_two_dimensional_point(self, point):
        """
        For visualizing a point, we want two-dimensional coordinates. We do this by projecting to the
        projection plane defined and then rotate this plane to the affine plane with normal vector [0,0,1].

        We leave the third coordinate (i.e. 1) and thus obtain two-dimensional coordinates.

        :param point: a three dimensional numpy array
        :return:
        """
        assert self.projection_plane is not None, \
            "Attention! The projection plane has not been defined."

        rotation_matrix = rotate_vectors(self.projection_plane, np.array([0, 0, 1]))

        # Project point to the projection plane
        point_2dim = project_point(self.projection_plane, point)
        # Rotate the projected point to the affine plane with normal vector [0, 0, 1].
        point_2dim = np.matmul(rotation_matrix, point_2dim)
        # Only return the first two coordinates
        return point_2dim[:2]

    def erupt_triangle(self, t, triangle, transformation_style = "Q"):
        """
        Performs the eruption flow on one triangle of the complex.
        Style Q: The basis is chosen such that the intersection points q_i remain fixed.
        Style P: The basis is chosen that the points of the flags p_i remain fixed.

        :param t: The transformation parameter
        :param triangle: A tuple of three flags (a list of three different integers between 0 and (self.n - 1)).
        :param transformation_style: a string, "P" or "Q"
        :return:
        :author: Sven Gruetzmacher
        """
        #assert self.get_triple_ratio(triangle) > 0, "The triple of flags is not positive!"

        # In a good basis, the transformation matrices g_i have the following nice form.
        gs = [np.diag([1.0, np.exp(t / 3.0), np.exp(-t / 3.0)]),
              np.diag([np.exp(-t / 3.0), 1.0, np.exp(t / 3.0)]),
              np.diag([np.exp(t / 3.0), np.exp(-t / 3.0), 1.0])]

        # However, there is two different styles of choosing this basis.

        # Style Q: The basis is chosen such that the intersection points q_i remain fixed.
        if transformation_style == "Q":
            # The intersection points of the flags in the triangle
            tqs = [line_intersection(self.ls[triangle[i - 1]], self.ls[triangle[i]]) for i in range(3)]
            basis = np.array([tqs[2], tqs[0], tqs[1]])
        # Style P: The basis is chosen that the points of the flags p_i remain fixed.
        elif transformation_style == "P":
            # The points of the flags in the triangle
            tps = [self.ps[i] for i in triangle]
            basis = np.array([tps[0], tps[1], tps[2]])
        else:
            raise Exception("Error! " + transformation_style + " is no valid transformation style!")

        #  Transform the transformation matrices g_i to the standard basis
        base_change_to_std = basis.T
        base_change_from_std = la.inv(base_change_to_std)
        gs = [np.matmul(np.matmul(base_change_to_std, x), base_change_from_std) for x in gs]

        # Perform the eruption flow on the triangle
        for i in range(3):
            self.ps[triangle[i]] = np.matmul(gs[(i + 2) % 3], self.ps[triangle[i]])
            self.ds[triangle[i]] = np.matmul(gs[(i + 2) % 3], self.ds[triangle[i]])
            # The next line is correct, but now we decided to calculate the ls automatically in refresh setup,
            # so it is not needed any more.
            # self.ls[i] = np.matmul(la.inv(gs[(i + 2) % 3]).T, self.ls[i])

        # The ls and qs are refreshed automatically
        self.refresh_setup()

    def bulge_quadrilateral(self, t, quad, style="bulge"):
        """
        Performs the bulge or the shear transformation on a quadrilateral. The points quad[0] and quad[2] define the
        edge along which the quadrilateral is divided for defining the transformation.

        Compare [WZ17], section 3.3, for a definition of the respective transformations (flows).

        :param b
        :param quad: the quadrilateral, i.e. a list of four integers indexing points in self.ps
        :param style: "bulge" for bulge transformation, "shear" for shear transformation
        :return:
        :author: Lukas Sauer
        """
        # Let p_0 and p_2 be the points on the edge.
        # The basis defining the transformation is v_0 (a vector representing p_0), v_2 (a vector representing p_2)
        # and v_{0,2} (a vector representing the intersection point l_0 \cap l_0).
        # The notation is according to [WZ17], section 3.3 (but shifted by -1 to avoid off-by-one-confusions).
        v_0 = self.ps[quad[0]]
        v_2 = self.ps[quad[2]]
        v_0_2 = line_intersection(self.ls[quad[0]], self.ls[quad[2]])

        basech = np.array([v_0, v_0_2, v_2]).T

        if style == "bulge":
            b = np.diag([np.exp(-t / 6.0), np.exp(t / 3.0), np.exp(-t / 6.0)])
            mb = np.diag([np.exp(t / 6.0), np.exp(-t / 3.0), np.exp(t / 6.0)])
        elif style == "shear":
            b = np.diag([np.exp(t / 2.0), 1.0, np.exp(-t / 2.0)])
            mb = np.diag([np.exp(-t / 6.0), 1.0, np.exp(t / 2.0)])
        else:
            raise Exception("Error! " + style + " is not a valid transformation style! It must be 'bulge' or 'shear'.")

        b = np.matmul(basech, np.matmul(b, la.inv(basech)))
        mb = np.matmul(basech, np.matmul(mb, la.inv(basech)))

        self.ds[quad[0]] = np.matmul(b, self.ds[quad[0]])
        self.ds[quad[1]] = np.matmul(b, self.ds[quad[1]])
        self.ds[quad[2]] = np.matmul(mb, self.ds[quad[2]])
        self.ds[quad[3]] = np.matmul(mb, self.ds[quad[3]])

        # The points on the edge, i.e. p_0 and p_2, are left invariant by the transformation anyway, so we don't need
        # to transform them.
        self.ps[quad[1]] = np.matmul(b, self.ps[quad[1]])
        self.ps[quad[3]] = np.matmul(mb, self.ps[quad[3]])

        # The ls and qs are refreshed automatically
        self.refresh_setup()

        """
        quadratic_form = np.array([[0, 0, 1],
                                   [0, 1, 0],
                                   [1, 0, 0]])
        quadratic_form = np.matmul(basech, np.matmul(quadratic_form, la.inv(basech)))
        #symmetrize matrix
        quadratic_form = 0.5*(quadratic_form+quadratic_form.T)

        self.quadratic_form = quadratic_form
        return quadratic_form
        """
    """
    def get_quadratic_form_from_flags(self, flags):
        v_0 = self.ps[flags[0]]
        v_2 = self.ps[flags[1]]
        v_0_2 = line_intersection(self.ls[flags[0]], self.ls[flags[1]])


        basech = np.array([v_0, v_0_2, v_2]).T

        quadratic_form = np.array([[0, 0, 1],
                                   [0, 1, 0],
                                   [1, 0, 0]])
        quadratic_form = np.matmul(basech, np.matmul(quadratic_form, la.inv(basech)))
        # symmetrize matrix
        quadratic_form = 0.5*(quadratic_form+quadratic_form.T)

        self.quadratic_form = quadratic_form
        return quadratic_form
    """


    def shear_quadrilateral(self, t, quad):
        """
        A shortcut for the shear transformation using bulge_quadrilateral with style = "shear".

        :param t: t: the transformation parameter
        :param quad: quad: the quadrilateral, i.e. a list of four integers indexing points in self.ps
        :return:
        """
        self.bulge_quadrilateral(t, quad, "shear")


    def create_triangulation(self):
        """
        Automatically generates a triangulation of the flag complex.

        :return:
        :author: Sven Gruetzmacher
        """
        self.triangles = []
        #self.internal_edges = []
        # internal edges, save indices of ps
        #for i in range(2, self.n - 1):
        #    self.internal_edges.append([0, i])
        # triangles in triangulation
        for i in range(1, self.n - 1):
            self.triangles.append([0, i, i + 1])
            
    def get_inner_triangle(self, triangle):
        """
        Returns the inner triangle T = (u_1, u_2, u_3) (cf. [WZ17] - Figure 1 for nomenclature)
        of the triple of flags given in triangle.

        :param triangle: Three indices of flags in our flag complex (a list of three integers)
        :return: a list of three 3-dim numpy arrays
        :author: Lukas Sauer
        """
        # TODO: For this to make sense, the triple ratio of the triangle must be positive.
        tps = self.get_middle_triangle(triangle)
        # Inside this function, we use nomenclature from Wienhard/Zhang, so tqs[i] is the intersection of the lines
        # l_i-1 and l_i+1 (i.e. tqs[i] lies opposite of tps[i]).
        tqs = self.get_outer_triangle(triangle)

        us = []

        for i in range(3):
            u_i = line_intersection(connecting_line(tps[(i-1) %3], tqs[(i-1) % 3]),
                                    connecting_line(tps[(i+1) % 3], tqs[(i + 1) % 3]))
            us.append(u_i)

        return us

    def get_middle_triangle(self, triangle):
        """
        Returns the middle triangle (p_1, p_2, p_3) (cf. [WZ17] - Figure 1 for nomenclature)
        of the triple of flags given in triangle.

        :param triangle: Three indices of flags in our flag complex (a list of three integers)
        :return: a list of three 3-dim numpy arrays
        :author: Lukas Sauer
        """
        tps = [self.ps[i] for i in triangle]
        return tps

    def get_outer_triangle(self, triangle):
        """
        Returns the outer triangle (q_1, q_2, q_3) (cf. [WZ17] - Figure 1 for nomenclature) of the triple of flags
        given in triangle.

        :param triangle: Three indices of flags in our flag complex (a list of three integers)
        :return: a list of three 3-dim numpy arrays
        :author: Lukas Sauer
        """
        # Inside this function, we use nomenclature from Wienhard/Zhang, so tqs[i] is the intersection of the lines
        # l_i-1 and l_i+1 (i.e. tqs[i] lies opposite of tps[i]).
        tqs = [line_intersection(self.ls[triangle[(i - 1) % 3]], self.ls[triangle[(i + 1) % 3]]) for i in range(3)]
        return tqs

    def get_flag(self, index):
        """
        For a given index, it returns the point and the line of the corresponding flag.

        :param index: a positive integer
        :return: a tuple of two three-dim numpy arrays
        """
        return (self.ps[index], self.ls[index])


    def visualize(self, d, col=dict(), with_inner_triangles = False, with_middle_triangles = True,
                  with_helper_lines=False, with_ellipse = False, with_label=False, ellipse_flags = None,
                  with_flags = True):
        """
        Visualizes the flag complex. Possible keys for defining colors are currently:
        points, inner, ellipse

        :param d: a drawSvg.drawing object for visualizing points, lines etc.
        :param col: a dictionary of strings defining colors of different objects.
        :param with_inner_triangles: visualizes the inner triangles u_i (compare [WZ17] for notation)
        :param with_middle_triangles: visualizes the middle triangle p_i
        :param with_helper_lines: a boolean value, visualize the helper lines defining the inner triangle
        :param with_label: a boolean value, set True for labeling the points self.ps[i] with numbers
        :return:
        """
        self.draw_complex()

        if "middle" not in col:
            col["middle"] = "blue"
        if "inner" not in col:
            col["inner"] = "red"
        if "ellipse" not in col:
            col["ellipse"] = "green"
        if "helper" not in col:
            col["helper"] = "grey"
        if "flags" not in col:
            col["flags"] = "black"

        """
        Need argument ellipse_quad=True
        # Draw ellipse through point specified in quad
        if ellipse_quad is not None:
            points = [self.drawps[i] for i in ellipse_quad]
            # The center is the intersection of the two lines connecting p_0 and p_2 resp. p_1 and p_3.
            center = line_intersection(connecting_line(self.ps[ellipse_quad[0]], self.ps[ellipse_quad[2]]),
                                       connecting_line(self.ps[ellipse_quad[1]], self.ps[ellipse_quad[3]]))
            center = self.get_two_dimensional_point(center)
            ellipse = get_ellipse_from_points_and_center(points, center, resolution=32)
            draw_polygon(d, ellipse, col="grey")
        """
        """
        if with_ellipse:
            if ellipse_flags is not None:
                quadratic_form = self.get_quadratic_form_from_flags(ellipse_flags)
            else:
                quadratic_form = self.quadratic_form
            # whatis = np.matmul(self.ps[0].T, np.matmul(quadratic_form, self.ps[0]))
            # inter = line_intersection(self.ls[0], self.ls[2])
            # whatis2 = np.matmul(self.ps[2].T, np.matmul(quadratic_form, self.ps[2]))
            # whatis_inter = np.matmul(inter.T, np.matmul(quadratic_form, inter))
            # whatis3 = np.matmul(self.ps[1].T, np.matmul(quadratic_form, self.ps[1]))
            # We see: The points p_0 and p_2 lie on the line, but the intersection point of l_0 and l_2 doesn't.
            rotation_matrix = rotate_vectors(self.projection_plane, np.array([0, 0, 1]))
            rotated_form = np.matmul(rotation_matrix, np.matmul(quadratic_form, rotation_matrix.T))
            # p0 = np.array([self.drawps[0][0], self.drawps[0][1], 1])
            # p2 = np.array([self.drawps[2][0], self.drawps[2][1], 1])
            # p3 = np.array([self.drawps[3][0], self.drawps[3][1], 1])
            # whatis_draw = np.matmul(p0.T, np.matmul(rotated_form, p0))
            # whatis_draw2 = np.matmul(p2.T, np.matmul(rotated_form, p2))
            # whatis_draw3 = np.matmul(p3.T, np.matmul(rotated_form, p3))
            ellipse = get_ellipse_from_quadratic_form(rotated_form, resolution=32)
            draw_polygon(d, [ellipse], col=["green"], wop=False)
        """

        if with_ellipse:
            flag1 = self.get_flag(ellipse_flags[0])
            flag2 = self.get_flag(ellipse_flags[1])
            point = self.ps[ellipse_flags[2]]
            ellipse = self.get_conic_through_flags_and_point(flag1, flag2, point, resolution=32)
            self.visualize_polygon(d, ellipse, col=col["ellipse"])


        # Draw the helper lines which define the inner triangle
        if with_helper_lines:
            for triangle in self.triangles:
                tps = self.get_middle_triangle(triangle)
                tqs = self.get_outer_triangle(triangle)
                for i in range(3):
                    self.visualize_connecting_line(d, tps[i], tqs[i], col=col["helper"])

        # Draw the inner triangles (u_1, u_2, u_3)
        if with_inner_triangles:
            for triangle in self.triangles:
                us = self.get_inner_triangle(triangle)
                drawus = [self.get_two_dimensional_point(us[i]) for i in range(3)]
                drawtri(d, drawus, col=col["inner"])

        # Draw the points p and the flags (i.e. the lines that the points are on).
        if with_flags:
            for i in range(self.n):
                if with_label:
                    label = "p"+str(i)
                else:
                    label = ""
                draw_flag(d, self.drawps[i], self.drawqs[i], col=col["flags"], label=label)
                #drawpt(d, self.drawqs[i], col=col)

        # Draw the triangle connecting the points p
        if with_middle_triangles:
            for triangle in self.triangles:
                points = self.get_middle_triangle(triangle)
                points = [self.get_two_dimensional_point(points[i]) for i in range(3)]
                drawtri(d, points, col=col["middle"], pts=True)

        return d

    def get_projected_ps(self):
        """
        Performs draw_complex and returns the drawps.

        :return: a list of two-dimensional numpy arrays
        """
        self.draw_complex()

        return self.drawps

    def get_triple_ratio(self, triangle):
        """
        Returns the triple ratio of the triple of flags.

        :param triangle: a list of three integers
        :return:
        """
        numerator = np.dot(self.ls[triangle[0]], self.ps[triangle[1]]) \
                    * np.dot(self.ls[triangle[1]], self.ps[triangle[2]]) \
                    * np.dot(self.ls[triangle[2]], self.ps[triangle[0]])

        denominator = np.dot(self.ls[triangle[0]], self.ps[triangle[2]]) \
                    * np.dot(self.ls[triangle[2]], self.ps[triangle[1]]) \
                    * np.dot(self.ls[triangle[1]], self.ps[triangle[0]])
        return numerator / denominator

    def visualize_polygon(self, d, polygon, col):
        drawpoly = [self.get_two_dimensional_point(p) for p in polygon]
        draw_polygon(d, [drawpoly], col=[col], wop=True)

    def visualize_connecting_line(self, d, point1, point2, col):
        try:
            drawp1 = self.get_two_dimensional_point(point1)
            drawp2 = self.get_two_dimensional_point(point2)
            drawl(d, drawp1, drawp2, col=col)
        except AssertionError:
            try:
                drawp2 = self.get_two_dimensional_point(point2)
                drawp_add = self.get_two_dimensional_point(np.add(point1,point2))
                drawl(d, drawp_add, drawp2, col=col)
            except AssertionError:
                try:
                    drawp1 = self.get_two_dimensional_point(point1)
                    drawp_add = self.get_two_dimensional_point(np.add(point1, point2))
                    drawl(d, drawp_add, drawp1, col=col)
                except AssertionError:
                    print("Warning! The line between " + str(point1) + " and " + str(point2) + " is a line at infinity.")

    def get_conic_through_flags_and_point(self, flag1, flag2, point, resolution, print_tangent_vector = False):
        """
        This function returns a conic (we usually want an ellipse) going through the points of the two
        flags and the third point, that is tangent to the lines of the two flags.

        :param flag1: a tuple of two numpy three-dim. np arrays (i.e. the point and the line)
        :param flag2: a tuple of two numpy three-dim. np arrays (i.e. the point and the line)
        :param point: a three-dim. numpy array
        :param resolution: A fourth of the number of points in the list returned.
        :return: A list of three dimensional numpy arrays.
        :author: Lukas Sauer
        """

        # For every four points in general position, there is a projective transformation that maps them
        # to arbitrary other four points in general position. So we want to map the four points
        # (i.e. points of flag1 and flag2, the third point, and the intersection point between the two
        # lines) to the points [1,0,1] , [-1,0,1], [0,1,1] and [0,1,0] (i.e. the point at infinity in the
        # projection to [0,0,1]). In fact, we want its inverse.
        other_points = [np.array([1, 0, 1]), np.array([-1, 0, 1]), np.array([0, 1, 1]), np.array([0, 1, 0])]
        points = [flag1[0], flag2[0], point, line_intersection(flag1[1], flag2[1])]
        transformation = la.inv(transform_four_points(points, other_points))

        # In this simple coordinate system, the required ellipse is simply a circle with center (0,0)
        # and radius 1.
        conic = []

        for i in range(4*resolution):
            angle = 2*np.pi*i/(4*resolution)
            circle_point = np.array([np.cos(angle), np.sin(angle), 1])
            conic.append(circle_point)

        if print_tangent_vector:
            # The tangent line at the point [0,1,1] is connecting this point with [1,1,1].
            # Transforming [1,1,1] to original coordinates would yield:
            print("Point defining tangent line to ellipse in " + str(point) + " is:" + str(np.matmul(transformation, np.array([1, 1, 1]))))
            # This gives us the possibility to draw the exact tangent line.

        # Now, as a last step, we transform everything back to the original coordinates.
        return [np.matmul(transformation, p) for p in conic]

"""
References:

[WZ17] A. Wienhard, T. Zhang. Deforming convex real projective structures. (2017)  arXiv:1702.00580
"""