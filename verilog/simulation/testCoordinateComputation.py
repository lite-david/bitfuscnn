import cocotb
from cocotb.triggers import Timer
from cocotb.clock import Clock
import sys
sys.path
sys.path.append('../../')
import unittest
import utils
import bitfuscnn

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

@cocotb.coroutine
def reset_dut(dut):
    reset = dut.coordinatecomputation.reset_n
    reset <= 0
    yield Timer(100, units="ns")
    reset <= 1
    yield Timer(100, units="ns")

@cocotb.test()
def test_8bit_4x4_coordinate_computation(dut):
    weights = [
        [0, 1, 1],
        [0, 0, 0],
        [1, 0, 1],
    ]
    activations = [
        [0, 1, 2],
        [3, 4, 0],
        [0, 0, 0],
    ]
    cweights, weightindices = utils.compress(weights)
    cactivations, activationindices = utils.compress(activations)
    sw_coordinatecompute = bitfuscnn.CoordinateComputation(weightindices[1:], activationindices[1:], 3, 3, 4, 4)
    outputcoordinates = sw_coordinatecompute.getCoordinates()
    # print(outputcoordinates)
    
    tc = unittest.TestCase()
    clk = dut.coordinatecomputation.clk
    bitwidth = dut.coordinatecomputation.bitwidth
    weight_indices = dut.coordinatecomputation.weight_indices
    activation_indices = dut.coordinatecomputation.activation_indices
    weight_dim = dut.coordinatecomputation.weight_dim
    activation_dim = dut.coordinatecomputation.activation_dim

    yield reset_dut(dut)
    clk <= 0
    yield Timer(100, units="ns")
    bitwidth <= 3
    for i in range(4):
        weight_indices[i] <= weightindices[i+1]
        activation_indices[i] <= activationindices[i+1]
    activation_dim <= 3
    weight_dim <= 3
    yield Timer(1)
    
    clk <= 1
    yield Timer(100, units="ns")
    for i in range(16):
        if outputcoordinates[i][0] == -1:
            tc.assertEqual(int(dut.coordinatecomputation.row_coordinate[i]), 65535)
        else:
            tc.assertEqual(int(dut.coordinatecomputation.row_coordinate[i]), outputcoordinates[i][0], "i={}".format(i))

        if outputcoordinates[i][1] == -1:
            tc.assertEqual(int(dut.coordinatecomputation.column_coordinate[i]), 65535)
        else:
            tc.assertEqual(int(dut.coordinatecomputation.column_coordinate[i]), outputcoordinates[i][1])


@cocotb.test()
def test_4bit_8x8_coordinate_computation(dut):
    weights = [
        [0, 1, 1],
        [1, 1, 1],
        [1, 1, 1],
    ]
    activations = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
    ]
    cweights, weightindices = utils.compress(weights)
    cactivations, activationindices = utils.compress(activations)
    sw_coordinatecompute = bitfuscnn.CoordinateComputation(weightindices[1:], activationindices[1:], 3, 3, 8, 8)
    outputcoordinates = sw_coordinatecompute.getCoordinates()
    # print(outputcoordinates)
    
    tc = unittest.TestCase()
    clk = dut.coordinatecomputation.clk
    bitwidth = dut.coordinatecomputation.bitwidth
    weight_indices = dut.coordinatecomputation.weight_indices
    activation_indices = dut.coordinatecomputation.activation_indices
    weight_dim = dut.coordinatecomputation.weight_dim
    activation_dim = dut.coordinatecomputation.activation_dim

    yield reset_dut(dut)
    clk <= 0
    yield Timer(100, units="ns")
    bitwidth <= 2
    for i in range(8):
        weight_indices[i] <= weightindices[i+1]
        activation_indices[i] <= activationindices[i+1]
    activation_dim <= 3
    weight_dim <= 3
    clk <= 1
    yield Timer(100, units="ns")
    for i in range(64):
        if outputcoordinates[i][0] == -1:
            tc.assertEqual(int(dut.coordinatecomputation.row_coordinate[i]), 65535)
        else:
            tc.assertEqual(int(dut.coordinatecomputation.row_coordinate[i]), outputcoordinates[i][0])

        if outputcoordinates[i][1] == -1:
            tc.assertEqual(int(dut.coordinatecomputation.column_coordinate[i]), 65535)
        else:
            tc.assertEqual(int(dut.coordinatecomputation.column_coordinate[i]), outputcoordinates[i][1])

@cocotb.test()
def test_2bit_16x16_coordinate_computation(dut):
    weights = [
        [0, 1, 1, 0, 0],
        [1, 1, 1, 0, 1],
        [1, 1, 1, 0, 1],
        [1, 1, 1, 0, 0],
        [1, 1, 1, 0 ,0],
    ]
    activations = [
        [0, 2, 1, 0, 0],
        [1, 2, 2, 0, 1],
        [1, 2, 1, 0, 1],
        [0, 3, 1, 2, 0],
        [3, 1, 2, 0 ,0],
    ]
    cweights, weightindices = utils.compress(weights)
    cactivations, activationindices = utils.compress(activations)
    sw_coordinatecompute = bitfuscnn.CoordinateComputation(weightindices[1:], activationindices[1:], 5, 5, 16, 16)
    outputcoordinates = sw_coordinatecompute.getCoordinates()
    # print(outputcoordinates)
    
    tc = unittest.TestCase()
    clk = dut.coordinatecomputation.clk
    bitwidth = dut.coordinatecomputation.bitwidth
    weight_indices = dut.coordinatecomputation.weight_indices
    activation_indices = dut.coordinatecomputation.activation_indices
    weight_dim = dut.coordinatecomputation.weight_dim
    activation_dim = dut.coordinatecomputation.activation_dim

    yield reset_dut(dut)
    clk <= 0
    yield Timer(100, units="ns")
    bitwidth <= 1
    for i in range(16):
        weight_indices[i] <= weightindices[i+1]
        activation_indices[i] <= activationindices[i+1]
    activation_dim <= 5
    weight_dim <= 5
    clk <= 1
    yield Timer(100, units="ns")
    for i in range(64):
        if outputcoordinates[i][0] == -1:
            tc.assertEqual(int(dut.coordinatecomputation.row_coordinate[i]), 65535)
        else:
            tc.assertEqual(int(dut.coordinatecomputation.row_coordinate[i]), outputcoordinates[i][0])

        if outputcoordinates[i][1] == -1:
            tc.assertEqual(int(dut.coordinatecomputation.column_coordinate[i]), 65535)
        else:
            tc.assertEqual(int(dut.coordinatecomputation.column_coordinate[i]), outputcoordinates[i][1])
