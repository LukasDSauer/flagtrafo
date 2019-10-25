#  Developed by Lukas Sauer at the Heidelberg Institute of Theoretical Studies on 2/19/19 6:36 PM.
#  Last modified on 2/19/19 6:36 PM.
#  (C) 2019. All rights reserved.

import numpy as np
import numpy.linalg as la

def project_point(n, p):
    """
    This function projects the projective point to the affine plane defined by the normal vector with distance 1 to
    the origin.

    :param n: the normal vector of the projection plane
    :param p: a projective point (a three-dimensional numpy array)
    :return:
    """

    if la.norm(n) != 1:
        n = n / la.norm(n)

    # TODO: Why do we do this? Is this do avoid numerical cancellation?
    if n[2] < 0:
        n = -1 * n

    # If the point (i.e. the line in R^3) is parallel to the projection plane, it can't be projected.
    # This is the case iff the point defining the line is perpendicular to the normal vector of the plane.
    assert np.dot(n, p) != 0, \
        "The point %r is on the boundary plane. Therefore it cannot be projected." % p

    # Projecting the point to the projection plane
    p = p / np.dot(n, p)
    p = p - n

    return p


def line_intersection(l1, l2):
    """
    Returns the intersection of the two projective lines l1 and l2. l1 and l2 are defined by their linear forms
    (i.e. the non-trivial linear form whose kernel is the projective line).
    
    The intersection between the two projective lines l_i and l_i-1 (i.e. planes defined via a normal vector) is
    a projective point (i.e. a line), which can be expressed by a vector perpendicular to the two normal vectors.
    
    :param l1: a vector defining the first linear form (a 3-dim numpy array)
    :param l2: a vector defining the second linear form (a 3-dim numpy array)
    :return: the intersection point (a 3-dim numpy array)
    """
    return np.cross(l1, l2)


def connecting_line(p1, p2):
    """
    Returns the connecting line of two projective points. The resulting projective line is represented via its linear
    form. The vector representing the linear form is simply the vector perpendicular to both p1 and p2.
    
    Remark the beautiful duality here. In terms of calculation, line_intersection() and connecting_line() are the same
    thing.

    :param p1: a vector defining the first point (a 3-dim numpy array)
    :param p2: a vector defining the second point (a 3-dim numpy array)
    :return: the connecting line (a 3-dim numpy array)
    :author:
    """
    return np.cross(p1, p2)

# def reflect_point_through_plane(p, l):
#     """
#     Returns the reflection of the point p through the plane with normal vector l.
#
#     :param p:
#     :param l:
#     :return:
#     """
#     return p - 2*np.dot(p,l)/np.dot(l, l)*l

def transform_four_points(points, other_points):
    """
    Four points in general position can be be mapped to arbitrary other four points in general position
    by means of a projective transformation. This functions returns this transformation.

    :param points: a list of four three-dim. numpy arrays
    :return: a 3x3- numpy-array
    """
    a = transform_standard_to_four_points(points)
    b = transform_standard_to_four_points(other_points)

    return np.matmul(b, la.inv(a))


def transform_standard_to_four_points(points):
    """
    Four points in general position can be be mapped to [1,0,0], [0,1,0], [0,0,1] and [1,1,1]
    by means of a projective transformation. This functions returns this transformation.

    :param points: a list of four three-dim. numpy arrays
    :return: a 3x3- numpy-array
    """
    b = np.column_stack([points[i] for i in range(3)])

    nu = np.matmul(la.inv(b), points[3])

    transformation = np.column_stack([nu[0]*points[0], nu[1]*points[1], nu[2]*points[2]])

    return transformation


def get_reflection(l, v):
    """
    In projective space, a reflection along a line l and a point v is defined as

    R(x) = x - l(x)v

    where l(.) is the linear form defining the projective line.
    l must be normalized such that l(v) = 2.

    This function returns the matrix defining the reflection.

    :param l: a three-dim numpy array
    :param v: a three-dim numpy array
    :return: a three times three numpy array
    """
    if not np.matmul(l.T, v) == 2:
        l = np.multiply(2/np.dot(l, v), l)
    ref = np.matmul(np.reshape(v, (3, 1)), np.reshape(l.T, (1, 3)))
    return np.eye(3) - ref