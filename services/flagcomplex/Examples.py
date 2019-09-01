#  Developed by Lukas Sauer at the Heidelberg Institute of Theoretical Studies on 2/20/19 11:59 AM.
#  Contact: lukas.sauer@h-its.org.
#  Last modified on 2/20/19 11:59 AM.
#  (C) 2019. All rights reserved.


from FlagComplex import FlagComplex
import numpy as np
from scipy.spatial import ConvexHull


def construct_from_ratio(ratio):
    """
    Constructs a triple of flags with a certain triple ratio.

    :param ratio: a float value defining the desired triple ratio
    :return: A FlagComplex object
    :author: Sven Gruetzmacher
    """
    assert ratio >= 0
    actratio = np.cbrt(ratio)
    convexpar = 1.0 / (actratio + 1)

    p1 = np.array([0, convexpar, 1 - convexpar])
    p2 = np.array([1 - convexpar, 0, convexpar])
    p3 = np.array([convexpar, 1 - convexpar, 0])
    ps = [p1, p2, p3]

    qs = [np.eye(3)[i] for i in range(3)]

    fcomplex = FlagComplex()
    for i in range(3):
        fcomplex.add_flag(ps[i], qs[(i+2) % 3])

    fcomplex.refresh_setup()
    fcomplex.set_projection_plane(np.array([1, 1, 1]))

    return fcomplex


# draw outer polygon and set points with ratio
def generate_random(n):  # builds ps qs and flag
    qs = []

    while True:
        okay = False
        choic = []
        # create points with min-distance and take convexhull
        while not okay:
            choic = np.sort(np.random.choice(10 * n, 2 * n, replace=False))
            mindist = np.min([choic[i + 1] - choic[i] for i in range(n - 1)])
            if mindist > 0.1 * n:
                okay = True

        for i in choic:
            angle = i * (2 * np.pi) / (10 * n)
            radius = 1.0 + 0.3 * (i % 3)
            pt = np.array([radius * np.sin(angle), radius * np.cos(angle), 1.0])
            qs.append(pt)

        cv = ConvexHull([x[:2] for x in qs])
        hull_points = cv.vertices
        if len(hull_points) > n:
            choic = np.sort(np.random.choice(len(hull_points), n, replace=False))
            hull_points = [hull_points[k] for k in choic]
            qs = [qs[s] for s in hull_points]
            break

    # generate ps p_i between q_i-1 and q_i
    ps = []
    for i in range(n):
        ratio = 0.1 * np.random.randint(3, 8)
        pt = (1 - ratio) * qs[(i + 1) % n][:2] + ratio * qs[i][:2]
        ps.append(np.array([pt[0], pt[1], 1]))

    fcomplex = FlagComplex()

    for i in range(n):
        fcomplex.add_flag(ps[i], qs[i])

    fcomplex.set_projection_plane(np.array([0, 0, 1]))
    return fcomplex




