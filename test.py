'''
Code for different testcases goes here
'''
import utils
from bitfuscnn import CoordinateComputation, MultiplierArray
from scipy.ndimage import convolve

weights = [
    [1, 0, 1],
    [0, 0, 0],
    [1, 0, 1],
]
activations = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]
cweights, weightindices = utils.compress(weights)
cactivations, activationindices = utils.compress(activations)

coordinatecompute = CoordinateComputation(weightindices[1:], activationindices[1:], 3, 3, 4, 4)
multiplierarray = MultiplierArray(cweights, cactivations, 4, 4)

results = {}
cycle = 0
outputcoordinates = coordinatecompute.getCoordinates()

while (len(outputcoordinates) > 0):
    products = multiplierarray.multiply()
    for coordinate, product in zip(outputcoordinates, products):
        if coordinate not in results:
            results[coordinate] = product
        else:
            results[coordinate] += product

    outputcoordinates = coordinatecompute.getCoordinates()
    cycle += 1
print('Cycles: ' + str(cycle))
print(results)
print(utils.convolve(activations, weights))

weights = [
    [1, 0, 1],
    [0, 0, 0],
    [1, 0, 1],
]
activations = [
    [10, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0]
]
cweights, weightindices = utils.compress(weights)
cactivations, activationindices = utils.compress(activations)

coordinatecompute = CoordinateComputation(weightindices[1:], activationindices[1:], 3, 5, 4, 4)
multiplierarray = MultiplierArray(cweights, cactivations, 4, 4)

results = {}
cycle = 0
outputcoordinates = coordinatecompute.getCoordinates()

while (len(outputcoordinates) > 0):
    products = multiplierarray.multiply()
    for coordinate, product in zip(outputcoordinates, products):
        if coordinate not in results:
            results[coordinate] = product
        else:
            results[coordinate] += product

    outputcoordinates = coordinatecompute.getCoordinates()
    cycle += 1
print('Cycles: ' + str(cycle))
print(results)
print(utils.convolve(activations, weights))
