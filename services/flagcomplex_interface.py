import numpy as np
from flagcomplex import FlagComplex
from flagcomplex.EuklGeometryUtility import rotate_vectors

trafo_range = 100
trafo_range_real = trafo_range*2+1  # n values on the minus side, n values on the plus side, and 0.

# Write the following values by hand to avoid rounding problems.
t_step = 0.1   # This must be = 10/trafo_range
t_offset = -10.1  # This must be = -10 - t_step


def init_flagcomplex_from_data(n, data, pplane, old_pplane):
    fcomplex = FlagComplex()
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

    return fcomplex


def compute_eruption_data(fcomplex, ftess, triangle):
    data = dict()
    fcomplex.erupt_triangle(t=t_offset, triangle=triangle, transformation_style="Q")
    for i in range(trafo_range_real):
        t = -trafo_range + i
        fcomplex.erupt_triangle(t=t_step, triangle=triangle, transformation_style="Q")
        fcomplex.draw_complex()
        fc_drawus = fcomplex.get_projected_us(triangle)

        drawps = rescale_existing_points(3, fcomplex.drawps)
        drawqs = rescale_existing_points(3, fcomplex.drawqs)
        drawus = rescale_existing_points(3, fc_drawus)

        initial_poly, hull, tiles = ftess.generate_tesselation()
        hull = rescale_existing_points(len(hull), hull)

        data[t] = {"ps": drawps, "qs": drawqs, "us": [drawus], "convex": hull}

    return data

def compute_shear_data(fcomplex, ftess, quad):
    data = dict()

    fcomplex.shear_quadrilateral(t=t_offset, quad=quad)
    for i in range(trafo_range_real):
        t = -trafo_range + i
        fcomplex.shear_quadrilateral(t=t_step, quad=quad)
        fcomplex.draw_complex()
        drawps = rescale_existing_points(4, fcomplex.drawps)
        drawqs = rescale_existing_points(4, fcomplex.drawqs)

        triangle0 = [0, 1, 2]
        triangle1 = [0, 2, 3]
        fc_drawus0 = fcomplex.get_projected_us(triangle0)
        fc_drawus1 = fcomplex.get_projected_us(triangle1)
        drawus0 = rescale_existing_points(3, fc_drawus0)
        drawus1 = rescale_existing_points(3, fc_drawus1)

        initial_poly, hull, tiles = ftess.generate_tesselation()
        hull = rescale_existing_points(len(hull), hull)

        data[t] = {"ps": drawps, "qs": drawqs, "us": [drawus0, drawus1], "convex": hull}

    return data

def compute_bulge_data(fcomplex, ftess, quad):
    data = dict()

    fcomplex.bulge_quadrilateral(t=t_offset, quad=quad)
    for i in range(trafo_range_real):
        t = -trafo_range + i

        fcomplex.bulge_quadrilateral(t=t_step, quad=quad)
        fcomplex.draw_complex()
        drawps = rescale_existing_points(4, fcomplex.drawps)
        drawqs = rescale_existing_points(4, fcomplex.drawqs)

        triangle0 = [0, 1, 2]
        triangle1 = [0, 2, 3]
        fc_drawus0 = fcomplex.get_projected_us(triangle0)
        fc_drawus1 = fcomplex.get_projected_us(triangle1)
        drawus0 = rescale_existing_points(3, fc_drawus0)
        drawus1 = rescale_existing_points(3, fc_drawus1)

        initial_poly, hull, tiles = ftess.generate_tesselation()

        hull = rescale_existing_points(len(hull), hull)

        data[t] = {"ps": drawps, "qs": drawqs, "us": [drawus0, drawus1], "convex": hull}

    return data


def rescale_existing_points(n, points):
    """
    This function rescales all the points in the list "points". If an entry doesn't exist,
    it adds None instead.

    :param n: the number of points to be rescaled, e.g. the length of "points".
    :param points: a list of numpy arrays.
    :return: a list of n numpy arrays.
    """
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
