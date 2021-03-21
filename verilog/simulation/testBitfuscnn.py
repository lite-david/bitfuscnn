import cocotb
from cocotb.triggers import Timer
from cocotb.clock import Clock
import sys
import numpy as np

sys.path
sys.path.append("../../")
import unittest
import utils
import bitfuscnn
import top


def get_mat(size, max_representable, p_zero):
    values = np.random.randint(low=0, high=max_representable, size=size**2)
    if_zero = np.random.random(size=size**2) > p_zero
    return (values * if_zero).reshape((size, size))


@cocotb.test()
def testBitfuscnn(dut):
    """Integration test for top level"""
    np.random.seed(0)
    BITWIDTH = 2
    left_shift = 2**(BITWIDTH+1)
    max_representable = 1 << left_shift - 1
    weights = get_mat(3, max_representable, 0.5)
    input_activations = get_mat(30, max_representable, 0.9)

    compressed_weights, weight_indices = utils.compress(weights)
    compressed_activations, activation_indices = utils.compress(input_activations)

    dut = dut.bitfuscnn
    clk = dut.clk
    yield Timer(0.5, units="ns")
