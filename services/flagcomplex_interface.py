import numpy as np
import copy
from flagcomplex import FlagComplex, FlagTesselator
from flagcomplex.EuklGeometryUtility import rotate_vectors
from flagcomplex.ProjGeometryUtility import transform_four_points

trafo_range = 65
trafo_range_real = trafo_range*2+1  # n values on the minus side, n values on the plus side, and 0.

# Write the following values by hand to avoid rounding problems.
t_step = 0.1   # Can be anything.
t_offset = -6.6  # This must be = (- trafo_range - 1)*t_step


def init_flagcomplex_from_data(n, data, pplane, old_pplane):
    fcomplex = FlagComplex()
    # p0 = np.array([292.75, 107.19999695, 100.])
    # p1 = np.array([468.75, 221.19999695, 100.])
    # p2 = np.array([329.75, 296.20001221, 100.])
    # p3 = np.array([146.75, 222.19999695, 100.])
    # q0 = np.array([-4.69093168e+08, -3.58196522e+08, -3.26950029e+08])
    # q1 = np.array([8.42531086e+08, 1.90862185e+08, 1.82580029e+08])
    # q2 = np.array([5.68916491e+08, 3.50633350e+08, 1.20240019e+08])
    # q3 = np.array([-3.20797029e+08, -6.49864884e+08, -2.15200019e+08])
    #
    #
    # fcomplex.add_flag(p0, q0)
    # fcomplex.add_flag(p1, q1)
    # fcomplex.add_flag(p2, q2)
    # fcomplex.add_flag(p3, q3)
    #
    # fcomplex.set_projection_plane(np.array([0, 0, 1]))

    fcomplex.set_projection_plane(np.array(pplane))
    # The number of flags
    # Adding all flags to the flag complex object
    if old_pplane == [0, 0, 1]:
        for i in range(n):
            p = data['ps'][i]
            # Note: We don't need this. Therefore, I commented it.
            # The webpage svg calculates coordinates on the scale of pixels,
            # which gives us very big numbers. We rescale them by a factor of 100.
            # p[:] = [x/100 for x in p]
            # p.append(1)
            p.append(100)
            direction = data['ds'][i]
            # direction[:] = [x/100 for x in direction]
            # direction.append(1)
            direction.append(100)
            # As we are using the qualities of numpy arrays internally at some points, we can't hand over a mere list.
            fcomplex.add_flag(np.array(p), np.array(direction))

    else:
        for i in range(n):
            p = data['ps'][i]
            p.append(100)
            direction = data['ds'][i]
            direction.append(100)
            rotation_matrix = rotate_vectors(np.array([0, 0, 1]), np.array(old_pplane))
            p = np.matmul(rotation_matrix, p)
            direction = np.matmul(rotation_matrix, direction)
            fcomplex.add_flag(p, direction)

    fcomplex.create_triangulation()
    return fcomplex


def compute_eruption_data(fcomplex, ftess):
    triangle = fcomplex.triangles[0]  # This is equal [0, 1, 2].
    args = {"triangle": triangle, "transformation_style": "Q"}

    return compute_trafo_data(fcomplex, ftess, fcomplex.erupt_triangle, args)


def compute_shear_data(fcomplex, ftess):
    quad = [0, 1, 2, 3]
    args = {"quad": quad}
    return compute_trafo_data(fcomplex, ftess, fcomplex.shear_quadrilateral, args)


def compute_bulge_data(fcomplex, ftess):
    quad = [0, 1, 2, 3]
    args = {"quad": quad}
    return compute_trafo_data(fcomplex, ftess, fcomplex.bulge_quadrilateral, args)


def trafo_eruption_minus_plus(t, fcomplex, triangle0, triangle1, style, other_points):
    fcomplex.erupt_complex_along_triangle(t=-t, triangle=triangle0, transformation_style=style)
    fcomplex.erupt_complex_along_triangle(t=+t, triangle=triangle1, transformation_style=style)
    fcomplex.projective_transformation = transform_four_points(fcomplex.qs, other_points=other_points)


def trafo_eruption_plus_plus(t, fcomplex, triangle0, triangle1, style, other_points):
    fcomplex.erupt_complex_along_triangle(t=+t, triangle=triangle1, transformation_style=style)
    fcomplex.erupt_complex_along_triangle(t=+t, triangle=triangle0, transformation_style=style)
    fcomplex.projective_transformation = transform_four_points(fcomplex.qs, other_points=other_points)


def compute_eruption_data_plus_plus(fcomplex, ftess):
    # data = dict()
    #
    # style = "Q"
    # triangle0 = [1, 2, 0]
    # triangle1 = [2, 3, 0]
    # fcomplex.refresh_setup()
    #
    # ftesselator = FlagTesselator(fcomplex, steps=3)
    #
    # other_points = copy.deepcopy(fcomplex.qs)
    # other_points = [other_points[i - 1] for i in range(4)]
    #
    # fcomplex.set_subdivision([2, 3, 0], {2: [0], 3: [2, 1], 0: [3]})
    # fcomplex.set_subdivision([1, 2, 0], {1: [0, 3], 2: [1], 0: [2]})
    #
    # fcomplex.erupt_complex_along_triangle(t=t_offset, triangle=triangle1, transformation_style=style)
    # fcomplex.erupt_complex_along_triangle(t=t_offset, triangle=triangle0, transformation_style=style)
    #
    # for r in range(1, trafo_range_real):
    #     fcomplex.erupt_complex_along_triangle(t=+t_step, triangle=triangle1, transformation_style=style)
    #     fcomplex.erupt_complex_along_triangle(t=+t_step, triangle=triangle0, transformation_style=style)
    #     fcomplex.projective_transformation = transform_four_points(fcomplex.qs, other_points)
    #     ini, hull, tiles = ftesselator.generate_tesselation()
    #
    #     fcomplex.draw_complex()
    #
    #     drawus = []
    #     for triangle in fcomplex.triangles:
    #         fc_drawus = fcomplex.get_projected_us(triangle)
    #         drawus.append(rescale_existing_points(fc_drawus))
    #
    #     hull = rescale_existing_points(hull)
    #     drawps = rescale_existing_points(fcomplex.drawps)
    #     drawqs = rescale_existing_points(fcomplex.drawqs)
    #
    #     t = -100 + r
    #     data[t] = {"ps": drawps, "qs": drawqs, "us": drawus, "convex": hull}
    #
    # return data

    return compute_two_triangle_eruption_data(fcomplex, ftess, trafo_eruption_plus_plus)


def compute_eruption_data_minus_plus(fcomplex, ftess):
    return compute_two_triangle_eruption_data(fcomplex, ftess, trafo_eruption_minus_plus)


def compute_two_triangle_eruption_data(fcomplex, ftess, ftrafo_twotri):
    style = "Q"

    triangle0 = [1, 2, 0]
    triangle1 = [2, 3, 0]
    fcomplex.refresh_setup()
    other_points = copy.deepcopy(fcomplex.qs)
    other_points = [other_points[i - 1] for i in range(4)]

    fcomplex.set_subdivision([2, 3, 0], {2: [0], 3: [2, 1], 0: [3]})
    fcomplex.set_subdivision([1, 2, 0], {1: [0, 3], 2: [1], 0: [2]})

    args = {"fcomplex": fcomplex, "triangle0": triangle0, "triangle1": triangle1, "style": style,
            "other_points": other_points}

    return compute_trafo_data(fcomplex, ftess, ftrafo_twotri, args)


def compute_trafo_data(fcomplex, ftess, ftrafo, args):
    data = dict()

    ftrafo(t=t_offset, **args)

    for i in range(trafo_range_real):
        ftrafo(t=t_step, **args)
        fcomplex.draw_complex()

        drawus = []
        for triangle in fcomplex.triangles:
            fc_drawus = fcomplex.get_projected_us(triangle)
            drawus.append(rescale_existing_points(fc_drawus))

        drawps = rescale_existing_points(fcomplex.drawps)
        drawqs = rescale_existing_points(fcomplex.drawqs)

        initial_poly, hull, tiles = ftess.generate_tesselation()
        hull = rescale_existing_points(hull)

        t = -trafo_range + i
        data[t] = {"ps": drawps, "qs": drawqs, "us": drawus, "convex": hull}

    return data


def compute_no_trafo_data(fcomplex, ftess):
    fcomplex.draw_complex()

    drawps = rescale_existing_points(fcomplex.drawps)
    drawqs = rescale_existing_points(fcomplex.drawqs)
    drawus = []

    for triangle in fcomplex.triangles:
        fc_drawus = fcomplex.get_projected_us(triangle)
        drawus.append(rescale_existing_points(fc_drawus))

    initial_poly, hull, tiles = ftess.generate_tesselation()

    hull = rescale_existing_points(hull)

    # We have no transformation, so the only valid time value is t=0.
    data = {0: {"ps": drawps, "qs": drawqs, "us": drawus, "convex": hull}}

    return data



def rescale_existing_points(points):
    """
    This function rescales all the points in the list "points". If an entry doesn't exist,
    it adds None instead.

    :param n: the number of points to be rescaled, e.g. the length of "points".
    :param points: a list of numpy arrays.
    :return: a list of n numpy arrays.
    """
    n = len(points)

    points_r = []
    for k in range(n):
        x = points[k]
        if x is not None:
            points_r.append((x * 100).tolist())
        else:
            points_r.append(None)
    return points_r


def compute_ellipse(fcomplex):
    flag1 = fcomplex.get_flag(0)
    flag2 = fcomplex.get_flag(2)
    point = fcomplex.ps[1]
    ellipse = fcomplex.get_conic_through_flags_and_point(flag1, flag2, point, resolution=32)

    ellipse = [100*fcomplex.get_two_dimensional_point(p) for p in ellipse]

    return ellipse
