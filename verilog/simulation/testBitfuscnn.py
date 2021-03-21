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


def join_into_num(values, width):
    max_val = 2 ** width - 1
    capped_values = np.minimum(values, max_val).astype(int)
    result = 0
    for i in capped_values[::-1]:
        result = result << width
        result += i
    return result


def defined(value):
    string = value._str
    if "x" in string or "z" in string:
        return False
    return True


def next_n(array, n):
    result = []
    if len(array) >= n:
        result = array[:n]
        return result
    result = array[:]
    extra = n - len(array)
    result += [0] * extra
    return result


def build_elements(ram_elements, per_block, width=4):
    indices = [0]
    length = (len(ram_elements) - 1) // per_block + 1
    for i in range(length):
        section = next_n(ram_elements, per_block)
        ram_elements = ram_elements[per_block:]
        indices.append(join_into_num(section, width))
    return indices


def build_ram(ram, ram_indices, parallel, bitwidth):
    values_per_block = parallel >> bitwidth
    value_width = 2 ** (bitwidth + 1)
    indices = build_elements(ram_indices, values_per_block)
    values = build_elements(ram, values_per_block, width=value_width)
    values[0] = len(ram)
    return values, indices


def parley_ram(addr, val, ind, ram, ram_indices):
    if defined(addr.value):
        address = addr.value.integer
        if address < len(ram):
            value = ram[address]
            index = ram_indices[address]
            val <= int(value)
            ind <= int(index)


def get_mat(size, max_representable, p_zero):
    values = np.random.randint(low=0, high=max_representable, size=size ** 2)
    if_zero = np.random.random(size=size ** 2) > p_zero
    return (values * if_zero).reshape((size, size))


@cocotb.coroutine
def reset_dut(dut):
    dut.clk <= 0
    dut.reset_n <= 0
    yield Timer(0.5, units="ns")
    dut.reset_n <= 1
    yield Timer(0.5, units="ns")


@cocotb.coroutine
def do_cycle(
    dut, weights_ram, weights_indices_ram, activations_ram, activations_indices_ram
):
    parley_ram(
        dut.iaram_address,
        dut.iaram_value,
        dut.iaram_indices_value,
        activations_ram,
        activations_indices_ram,
    )
    parley_ram(
        dut.weight_address,
        dut.weight_value,
        dut.weight_indices_value,
        weights_ram,
        weights_indices_ram,
    )

    yield Timer(1)

    dut.clk <= 1
    yield Timer(0.5, units="ns")

    dut.clk <= 0
    yield Timer(0.5, units="ns")


@cocotb.test()
def testBitfuscnn(dut):
    """Integration test for top level"""
    np.random.seed(0)
    BITWIDTH = 2
    left_shift = 2 ** (BITWIDTH + 1)
    max_representable = 1 << left_shift - 1
    weights = get_mat(3, max_representable, 0.5)
    input_activations = get_mat(30, max_representable, 0.9)

    compressed_weights, weight_indices = utils.compress(weights)
    compressed_activations, activation_indices = utils.compress(input_activations)
    weights_ram, weights_indices_ram = build_ram(
        compressed_weights[1:], weight_indices[1:], 16, BITWIDTH
    )
    activations_ram, activations_indices_ram = build_ram(
        compressed_activations[1:], activation_indices[1:], 16, BITWIDTH
    )

    dut = dut.bitfuscnn
    clk = dut.clk
    dut.mul_cfg <= BITWIDTH
    dut.weight_sign_cfg <= 1
    dut.act_sign_cfg <= 1
    dut.weight_dim <= 3
    dut.activation_dim <= 30
    dut.transfer <= 0

    yield reset_dut(dut)

    for i in range(10):
        yield do_cycle(
            dut, weights_ram, weights_indices_ram, activations_ram, activations_indices_ram
        )
