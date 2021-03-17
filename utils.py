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
            #We store at maximum 15 contiguous zeros
            #This allows us to use 4 bits for each element in compressed vector
            if abs(element) > 0.1 or zerosCount >= 15:
                indexVector.append(zerosCount)
                dataVector.append(element)
                indexVector[0] += 1
                zerosCount = 0
            else:
                zerosCount += 1

    return dataVector, indexVector

def compressMultiple(matrixlist):
    dataVector = []
    indexVector = [0]
    zerosCount = 0
    for matrix in matrixlist:
        for row in matrix:
            for element in row:
                if element > 0 or zerosCount > 15:
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

def convolveMultiple(activations, weight_list):
    result = np.zeros((len(activations), len(activations[0])))
    for weights in weight_list:
        result += convolve(activations, weights)
    return result



