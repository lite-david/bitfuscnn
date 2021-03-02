'''
Methods which implement different hardware components of the accelerator go here
'''
def computeCoordinates(weightIndices, activationIndices, weightDim, activationDim):
    # The indices here are the number of zeros before a non-zero element 
    wi = 0
    outputCoordinates = []
    for i in weightIndices:
        wi = wi + i 
        ai = 0
        for j in activationIndices:
            ai = ai + j
            # Compute 2D coordinates for the weight and activation
            wiRow = wi // weightDim
            wiCol = wi % weightDim
            aiRow = ai // activationDim
            aiCol = ai % activationDim
            # Output activation coordinate = 
            # Displacement of index in weight filter from filter center + Input Activation coordinate 
            # The weightDim // 2 is used to calculate the coordinate of filter center 
            oiRow = (weightDim // 2) - wiRow + aiRow
            oiCol = (weightDim // 2) - wiCol + aiCol
            outputCoordinates.append((oiRow, oiCol))
            # Increment by 1 to account for non-zero elements
            ai += 1  
        wi += 1 
    return outputCoordinates
