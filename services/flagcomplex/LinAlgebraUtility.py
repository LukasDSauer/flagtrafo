#  Developed by Lukas Sauer at the Heidelberg Institute of Theoretical Studies on 17.05.19, 15:05.
#  Last modified on 17.05.19, 15:04.
#  (C) 2019. All rights reserved.

import numpy as np
from copy import deepcopy

def get_adj(matrix):
    """
    Get the adjugate matrix of a 3x3 matrix.

    :param matrix: a 3dim numpy array
    :return:
    """
    #n = matrix.shape[0]

    # Calculate the cofactor matrix
    c = np.zeros((3,3))#3=n

    for i in range(3):#3=n
        for j in range(3):
            # The matrix obtained by crossing out row i and column j.
            tmp = np.delete(np.delete(matrix, i, 0), j, 1)
            # The determinant of a 2x2-matrix
            det = tmp[0][0]*tmp[1][1]-tmp[1][0]*tmp[0][1]
            c[i][j] = (-1)**(i+j)*det#(matrix[(i-1)%3][(j-1)%3]*matrix[(i+1)%3][(j+1)%3] - matrix[(i-1)%3][(j+1)%3]*matrix[(i+1)%3][(j-1)%3])
    # The adjunct is the transpose of the cofactor matrix.
    return c.T

