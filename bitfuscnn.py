'''
Methods which implement different hardware components of the accelerator go here
'''

import utils

class CoordinateComputation:
    def __init__(self, weightIndices, activationIndices, weightDim, activationDim, f, i):
        # This list acts like the weight FIFO. Once a weightFIFO object is available this can be replaced with the
        # object And a method like weightFIFO.get() should return a list of weights
        self.weightIndices = weightIndices
        self.activationIndices = activationIndices  # This list acts like the IARAM
        self.weightDim = weightDim
        self.activationDim = activationDim
        self.f = f
        self.i = i
        # Running sum to track current index for weights and activations
        self.weightIndex = 0
        self.activationIndex = 0
        # Since unit can run for only f weights, keep track of where to resume from
        self.weightPointer = 0
        # Since unit can run only for i activations, keep track of where to resume from
        self.activationPointer = 0

    def getCoordinates(self):
        # The indices here are the number of zeros before a non-zero element 
        outputCoordinates = []
        wi = self.weightIndex
        ai = self.activationIndex
        # Loop limits are f and i so at most there are fxi output coordinates
        for i in range(self.f):
            if self.weightPointer + i >= len(self.weightIndices):
                break
            wi += self.weightIndices[self.weightPointer + i]
            ai = self.activationIndex
            for j in range(self.i):
                if self.activationPointer + j >= len(self.activationIndices):
                    break
                ai += self.activationIndices[self.activationPointer + j]
                # Compute 2D coordinates for the weight and activation
                weightIndexRow = wi // self.weightDim
                weightIndexCol = wi % self.weightDim
                activationIndexRow = ai // self.activationDim
                activationIndexCol = ai % self.activationDim
                # Output activation coordinate = 
                # Displacement of index in weight filter from filter center + Input Activation coordinate 
                # The weightDim // 2 is used to calculate the coordinate of filter center 
                oiRow = (self.weightDim // 2) - weightIndexRow + activationIndexRow
                oiCol = (self.weightDim // 2) - weightIndexCol + activationIndexCol
                # oiRow =  activationIndexRow - weightIndexRow
                # oiCol =  activationIndexCol - weightIndexCol
                outputCoordinates.append((oiRow, oiCol))
                # Increment by 1 to account for non-zero elements
                ai += 1
                ai %= (self.activationDim * self.activationDim)
            # Increment by 1 to account for non-zero elements
            wi += 1
            # reset weight incase straddling across different weight filters K = 1 and K = 2 for example.
            wi %= (self.weightDim * self.weightDim)
        self.activationIndex = ai
        self.weightIndex = wi
        self.activationPointer += self.i
        if self.weightPointer >= len(self.weightIndices):
            # Ideally we should do a weightFIFO.get() here
            pass
        if self.activationPointer >= len(self.activationIndices):
            self.weightPointer += self.f
            self.activationPointer = 0
        return outputCoordinates


class BufferBankArray:
    # Initializes 'a' buffer banks, each with fxi entries.
    def __init__(self, a, f, i):
        self.buffer = [[0] * f * i] * a

    def get(self, bank, entry):
        return self.buffer[bank][entry]

    def accumulate(self, bank, entry, value):
        self.buffer[bank][entry] += value

    def clear(self):
        self.buffer = [[0] * len(x) for x in self.buffer]


# Routes FxI inputs to Ax(FxI) buffer banks
class Crossbar:
    def __init__(self, a, f, i, bufferbank):
        self.a = a
        self.f = f
        self.i = i

    def route(self, inputs):
        pass


class MultiplierArray:
    def __init__(self, weights, activations, f, i):
        self.f = f
        self.i = i
        self.weights = weights
        self.activations = activations
        # Since unit can run for only f weights, keep track of where to resume from
        self.weightPointer = 0
        # Since unit can run only for i activations, keep track of where to resume from
        self.activationPointer = 0

    def multiply(self):
        output = []
        # Loop limits are f and i so atmost there are fxi output coordinates
        for i in range(self.f):
            if self.weightPointer + i >= len(self.weights):
                break
            for j in range(self.i):
                if self.activationPointer + j >= len(self.activations):
                    break
                output.append(self.weights[self.weightPointer + i] * self.activations[self.activationPointer + j])
        self.activationPointer += self.i
        if self.weightPointer >= len(self.weights):
            self.weightPointer = 0
        if self.activationPointer >= len(self.activations):
            self.weightPointer += self.f
            self.activationPointer = 0
        return output
