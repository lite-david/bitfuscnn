'''
Software utilities go here 
'''
#Converts a 2D matrix into a compressed representation 
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

    

