#  Developed by Lukas Sauer at the Heidelberg Institute of Theoretical Studies on 3/20/19 11:21 AM.
#  Last modified on 3/20/19 11:21 AM.
#  (C) 2019. All rights reserved.

import numpy as np
import numpy.linalg as la

def rotate_vectors(p, q):
    """
    This function calculates the the rotation matrix needed to rotate the vector p to the direction of the vector
    q. It doesn't scale the vectors.
    :param p: The start vector (a 3-dim numpy array)
    :param q: The goal vector (a 3-dim numpy array)
    :return: The rotation matrix (a 3x3-dim numpy array)
    """
    p = p / la.norm(p)
    q = q / la.norm(q)

    # Check whether p and q are equal
    if la.norm(p-q) == 0:
        return np.eye(3)

    scal = np.dot(p, q)
    cross = np.cross(p, q)
    ncross = la.norm(cross)

    G = np.array([[scal, -ncross, 0], \
                  [ncross, scal, 0], \
                  [0, 0, 1]])
    midvec = q - scal * p
    midvec = midvec / la.norm(midvec)
    basechangeinv = np.array([p, midvec, cross]).T

    return np.matmul(np.matmul(basechangeinv, G), la.inv(basechangeinv))

def rotate_by_angle_2dim(angle):
    """
    Returns the two-dimensional rotation matrix

    :param angle:
    :return: a two-times-two numpy array
    """
    cosine = np.cos(angle)
    sine = np.sin(angle)

    R = np.array(((cosine, -sine), (sine, cosine)))

    return R
