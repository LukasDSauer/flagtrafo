import numpy as np
from flagcomplex import FlagComplex
from flagcomplex.EuklGeometryUtility import rotate_vectors
from flagcomplex.ProjGeometryUtility import connecting_line, line_intersection


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
            fcomplex.add_flag(p, direction)

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


def compute_eruption_data(fcomplex, triangle, width, height):
    data = dict()
    fcomplex.erupt_triangle(t=-10.01, triangle=triangle, transformation_style="Q")
    for i in range(2001):
        t = -1000 + i
        fcomplex.erupt_triangle(t=0.01, triangle=triangle, transformation_style="Q")
        fcomplex.draw_complex()
        fc_drawus = fcomplex.get_projected_us(triangle)

        drawps = rescale_existing_points(3, fcomplex.drawps)
        drawqs = rescale_existing_points(3, fcomplex.drawqs)
        drawus = rescale_existing_points(3, fc_drawus)

        frameints = compute_intersection_points_with_frame(width, height, fcomplex)
        frameints = [rescale_existing_points(2, points) for points in frameints]


        data[t] = {"ps": drawps, "qs": drawqs, "us": drawus, "frameints": frameints}

    return data

def compute_shear_data(fcomplex, quad, width, height):
    data = dict()

    fcomplex.shear_quadrilateral(t=-10.01, quad=quad)
    for i in range(2001):
        t = -1000 + i
        fcomplex.shear_quadrilateral(t=0.01, quad=quad)
        fcomplex.draw_complex()

        drawps = rescale_existing_points(4, fcomplex.drawps)
        drawqs = rescale_existing_points(4, fcomplex.drawqs)

        frameints = compute_intersection_points_with_frame(width, height, fcomplex)
        frameints = [rescale_existing_points(2, points) for points in frameints]

        data[t] = {"ps": drawps, "qs": drawqs, "frameints": frameints}

    return data

def compute_bulge_data(fcomplex, quad, width, height):
    data = dict()

    fcomplex.bulge_quadrilateral(t=-10.01, quad=quad)
    for i in range(2001):
        t = -1000 + i
        fcomplex.bulge_quadrilateral(t=0.01, quad=quad)
        fcomplex.draw_complex()

        drawps = rescale_existing_points(4, fcomplex.drawps)
        drawqs = rescale_existing_points(4, fcomplex.drawqs)

        frameints = compute_intersection_points_with_frame(width, height, fcomplex)
        frameints = [rescale_existing_points(len(points), points) for points in frameints]

        data[t] = {"ps": drawps, "qs": drawqs, "frameints": frameints}

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


def compute_intersection_points_with_frame(width, height, fcomplex):
    rotation_matrix = rotate_vectors(np.array([0, 0, 1]), fcomplex.projection_plane)
    image_bottom_line = connecting_line(np.array([0, 0, 100]), np.array([width, 0, 100]))
    image_top_line = connecting_line(np.array([0, height, 100]), np.array([width, height, 100]))
    image_left_line = connecting_line(np.array([0, 0, 100]), np.array([0, height, 100]))
    image_right_line = connecting_line(np.array([width, 0, 100]), np.array([width, height, 100]))

    image_bottom_line = np.matmul(rotation_matrix, image_bottom_line)
    image_top_line = np.matmul(rotation_matrix, image_top_line)
    image_left_line = np.matmul(rotation_matrix, image_left_line)
    image_right_line = np.matmul(rotation_matrix, image_right_line)

    frame_lines = [image_bottom_line, image_top_line, image_left_line, image_right_line]
    intersection_points = []

    for line in fcomplex.ls:
        intersection_points_for_line = []
        for fline in frame_lines:
            try:
                point = line_intersection(line, fline)
                point_2dim = fcomplex.get_two_dimensional_point(point)
                if 0 <= point_2dim[0] <= width and 0 <= point_2dim[1] <= height:
                    intersection_points_for_line.append(point_2dim)
            except AssertionError:
                0
        intersection_points.append(intersection_points_for_line)

    return intersection_points











