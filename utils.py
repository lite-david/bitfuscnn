'''
Software utilities go here 
'''
#Converts a 2D matrix into a compressed representation 
import numpy as np
def compress(matrix):
    dataVector = []
    indexVector = [0]
    zerosCount = 0
    for row in matrix:
        for element in row:
            if element > 0:
                indexVector.append(zerosCount)
                dataVector.append(element)
                indexVector[0] += 1
                zerosCount = 0
            else:
                zerosCount += 1

    return dataVector, indexVector

def convolve(activations, weights):
    a = np.array(activations)
    w = np.array(weights)
    a = np.pad(a, 1, mode = 'constant')
    m, n = w.shape
    y, x = a.shape
    y = y - m + 1
    x = x - m + 1
    new_image = np.zeros((y,x))
    for i in range(y):
        for j in range(x):
            new_image[i][j] = np.sum(a[i:i+m, j:j+m]*w)
    return new_image



