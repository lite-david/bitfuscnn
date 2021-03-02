'''
Code for different testcases goes here
'''
import utils
import bitfuscnn

inputs = []    
weights = [
    [0, 23, 0],
    [0, 0, 0],
    [18, 0, 42],
]    
activations = [
    [1, 0, 0],
    [0, 0, 0],
    [0, 0, 0],
]
inputs.append([weights, activations, 3, 3])

activations = [
    [0, 0, 0],
    [0, 1, 0],
    [0, 0, 0],
]
inputs.append([weights, activations, 3, 3])

activations = [
    [1, 0, 0, 0, 1],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0],
]
inputs.append([weights, activations, 3, 5])

for testcase in inputs:
    weights = testcase[0]
    activations = testcase[1]
    weightDim = testcase[2]
    activationDim = testcase[3]
    weightData, weightIndices = utils.compress(weights)
    activationData, activationIndices = utils.compress(activations)
    print(activationIndices)
    print(weightIndices)
    print(bitfuscnn.computeCoordinates(weightIndices[1:], activationIndices[1:], weightDim, activationDim))
