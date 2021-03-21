import cocotb
from cocotb.triggers import Timer
from cocotb.clock import Clock
import unittest
import numpy as np

def join_into_num(values, width):
    max_val = 2**width - 1
    capped_values = np.minimum(values, max_val).astype(int)
    result = 0
    for i in capped_values[::-1]:
        result = result << width
        result += i
    return result

class RamFIFO:
    def __init__(self, ram, ram_indices, bitwidth):
        self.ram = ram
        self.ram_indices = ram_indices
        self.bitwidth = bitwidth
        self.index = 0

    def generate_next_8bit(self):
        value = self.ram[self.index]
        self.index += 1
        return value

    def generate_next_4bit(self):
        values = self.ram[self.index:self.index+2]
        self.index += 2
        return int(join_into_num(values, 4))

    def generate_next_2bit(self):
        values = self.ram[self.index:self.index+4]
        self.index += 4
        return int(join_into_num(values, 2))

    def generate_next(self):
        values = [0] * 4
        indices = [0] * 16
        if self.bitwidth == 2:
            indices[0:4] = self.ram_indices[self.index : self.index + 4]
            values = [
                self.generate_next_8bit(),
                self.generate_next_8bit(),
                self.generate_next_8bit(),
                self.generate_next_8bit(),
            ]

        if self.bitwidth == 1:
            indices[0:8] = self.ram_indices[self.index : self.index + 8]
            values = [
                self.generate_next_4bit(),
                self.generate_next_4bit(),
                self.generate_next_4bit(),
                self.generate_next_4bit(),
            ]

        if self.bitwidth == 0:
            indices[0:16] = self.ram_indices[self.index : self.index + 16]
            values = [
                self.generate_next_2bit(),
                self.generate_next_2bit(),
                self.generate_next_2bit(),
                self.generate_next_2bit(),
            ]

        return values, indices

    def verify(self, ram_fifo, tc, advance=True):
        old_index = self.index
        values, indices = self.generate_next()
        for i in range(4):
            fifo_value = ram_fifo.value_fifo_out[i].value
            tc.assertEqual(
                values[i],
                fifo_value,
                "value_fifo_out[{}] should = {} but instead {}".format(
                    i, values[i], fifo_value
                ),
            )

        for i in range(16):
            fifo_value = ram_fifo.index_fifo_out[i].value
            tc.assertEqual(
                indices[i],
                fifo_value,
                "index_fifo_out[{}] should = {} but instead {}".format(
                    i, indices[i], fifo_value
                ),
            )

        if not advance:
            self.index = old_index


@cocotb.coroutine
def reset_dut(dut):
    dut.advance <= 0
    dut.clk <= 0
    dut.reset_n <= 0
    yield Timer(100, units="ns")
    dut.reset_n <= 1
    yield Timer(100, units="ns")


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
    length = (len(ram_elements) -1 ) // per_block + 1
    for i in range(length):
        section = next_n(ram_elements, per_block)
        ram_elements = ram_elements[per_block:]
        indices.append(join_into_num(section, width))
    return indices


def build_ram(ram, ram_indices, parallel, bitwidth):
    values_per_block = parallel >> bitwidth
    value_width = (2**(bitwidth+1))
    indices = build_elements(ram_indices, values_per_block)
    values = build_elements(ram, values_per_block, width = value_width)
    values[0] = len(ram)
    return values, indices


def parley_ram(ram_fifo, ram, ram_indices):
    if defined(ram_fifo.ram_address.value):
        address = ram_fifo.ram_address.value.integer
        if address < len(ram):
            value = ram[address]
            index = ram_indices[address]
            ram_fifo.ram_value <= int(value)
            ram_fifo.ram_indices_value <= int(index)

@cocotb.coroutine
def cycle(ram_fifo, ram, ram_indices):
    parley_ram(ram_fifo, ram, ram_indices)
    yield Timer(1)
    ram_fifo.clk <= 1
    yield Timer(100, units="ns")
    ram_fifo.clk <= 0
    yield Timer(100, units="ns")


@cocotb.test()
def not_done_after_reset(dut):
    tc = unittest.TestCase()
    ram_fifo = dut.ram_fifo
    yield reset_dut(ram_fifo)

    tc.assertFalse(ram_fifo.done.value)


@cocotb.test()
def done_after_loading_zero(dut):
    tc = unittest.TestCase()
    ram_fifo = dut.ram_fifo
    yield reset_dut(ram_fifo)

    ram = [0]
    ram_indices = [0]

    yield cycle(ram_fifo, ram, ram_indices)

    tc.assertTrue(ram_fifo.done.value)

    yield cycle(ram_fifo, ram, ram_indices)

    tc.assertTrue(ram_fifo.done.value)


@cocotb.test()
def reads_four_eight_bit_value_in_one_cycles(dut):
    tc = unittest.TestCase()
    ram_fifo = dut.ram_fifo

    RAM_PARALLEL = 16

    bitwidth = 2
    ram_fifo.bitwidth <= bitwidth
    yield reset_dut(ram_fifo)

    ram = [1, 2, 3, 4]
    ram_indices = [5, 6, 7, 8]
    ram_encoded, ram_indices_encoded = build_ram(ram, ram_indices, RAM_PARALLEL, bitwidth)

    parley_ram(ram_fifo, ram_encoded, ram_indices_encoded)
    yield Timer(1)

    tc.assertTrue(ram_fifo.stall.value)
    tc.assertFalse(ram_fifo.done.value)

    yield cycle(ram_fifo, ram_encoded, ram_indices_encoded)

    tc.assertFalse(ram_fifo.stall.value)
    tc.assertFalse(ram_fifo.done.value)

    ram_fifo.advance <= 1
    yield Timer(1)

    yield cycle(ram_fifo, ram_encoded, ram_indices_encoded)

    ram_fifo.advance <= 0
    yield Timer(1)

    tc.assertFalse(ram_fifo.stall.value)
    tc.assertTrue(ram_fifo.done.value)

    model = RamFIFO(ram, ram_indices, bitwidth)
    model.verify(ram_fifo, tc)

@cocotb.test()
def reads_four_eight_bit_value_from_first_batch(dut):
    tc = unittest.TestCase()
    ram_fifo = dut.ram_fifo

    RAM_PARALLEL = 16

    bitwidth = 2
    ram_fifo.bitwidth <= bitwidth
    yield reset_dut(ram_fifo)

    ram = [1, 2, 3, 4, 2, 4, 6, 8]
    ram_indices = [5, 6, 7, 8, 1, 2, 3, 4]
    ram_encoded, ram_indices_encoded = build_ram(ram, ram_indices, RAM_PARALLEL, bitwidth)

    yield cycle(ram_fifo, ram_encoded, ram_indices_encoded)

    tc.assertFalse(ram_fifo.done.value)
    tc.assertFalse(ram_fifo.stall.value)

    yield cycle(ram_fifo, ram_encoded, ram_indices_encoded)

    tc.assertFalse(ram_fifo.done.value)
    tc.assertFalse(ram_fifo.stall.value)

    ram_fifo.advance <= 1
    yield Timer(1)

    yield cycle(ram_fifo, ram_encoded, ram_indices_encoded)

    ram_fifo.advance <= 0
    yield Timer(1)

    tc.assertFalse(ram_fifo.done.value)
    tc.assertFalse(ram_fifo.stall.value)

    model = RamFIFO(ram, ram_indices, bitwidth)
    model.verify(ram_fifo, tc)

@cocotb.test()
def reads_four_eight_bit_value_from_second_batch(dut):
    tc = unittest.TestCase()
    ram_fifo = dut.ram_fifo

    RAM_PARALLEL = 16

    bitwidth = 2
    ram_fifo.bitwidth <= bitwidth
    yield reset_dut(ram_fifo)

    ram = [1, 2, 3, 4, 2, 4, 6, 8]
    ram_indices = [5, 6, 7, 8, 1, 2, 3, 4]
    ram_encoded, ram_indices_encoded = build_ram(ram, ram_indices, RAM_PARALLEL, bitwidth)

    yield cycle(ram_fifo, ram_encoded, ram_indices_encoded)

    ram_fifo.advance <= 1
    yield Timer(1)

    yield cycle(ram_fifo, ram_encoded, ram_indices_encoded)

    ram_fifo.advance <= 0
    yield Timer(1)

    model = RamFIFO(ram, ram_indices, bitwidth)
    model.verify(ram_fifo, tc, advance=False)

    yield cycle(ram_fifo, ram_encoded, ram_indices_encoded)

    tc.assertFalse(ram_fifo.done.value)

    model.verify(ram_fifo, tc, advance=True)

    ram_fifo.advance <= 1
    yield Timer(1)

    yield cycle(ram_fifo, ram_encoded, ram_indices_encoded)

    ram_fifo.advance <= 0
    yield Timer(1)

    model.verify(ram_fifo, tc, advance=False)
    tc.assertTrue(ram_fifo.done.value)

@cocotb.test()
def reads_four_eight_bit_value_from_second_batch_without_stall(dut):
    tc = unittest.TestCase()
    ram_fifo = dut.ram_fifo

    RAM_PARALLEL = 16

    bitwidth = 2
    ram_fifo.bitwidth <= bitwidth
    yield reset_dut(ram_fifo)

    ram = [1, 2, 3, 4, 2, 4, 6, 8]
    ram_indices = [5, 6, 7, 8, 1, 2, 3, 4]
    ram_encoded, ram_indices_encoded = build_ram(ram, ram_indices, RAM_PARALLEL, bitwidth)

    yield cycle(ram_fifo, ram_encoded, ram_indices_encoded)

    ram_fifo.advance <= 1
    yield Timer(1)

    yield cycle(ram_fifo, ram_encoded, ram_indices_encoded)

    model = RamFIFO(ram, ram_indices, bitwidth)
    model.verify(ram_fifo, tc, advance=True)

    yield cycle(ram_fifo, ram_encoded, ram_indices_encoded)

    model.verify(ram_fifo, tc, advance=True)
    tc.assertTrue(ram_fifo.done.value)

@cocotb.test()
def reads_sixteen_two_bit_value_in_one_cycles(dut):
    tc = unittest.TestCase()
    ram_fifo = dut.ram_fifo

    RAM_PARALLEL = 16

    bitwidth = 0
    ram_fifo.bitwidth <= bitwidth
    yield reset_dut(ram_fifo)

    ram = [1, 2, 3, 0] * 4
    ram_indices = [5, 6, 7, 8] * 4
    ram_encoded, ram_indices_encoded = build_ram(ram, ram_indices, RAM_PARALLEL, bitwidth)

    parley_ram(ram_fifo, ram_encoded, ram_indices_encoded)
    yield Timer(1)

    tc.assertTrue(ram_fifo.stall.value)
    tc.assertFalse(ram_fifo.done.value)

    yield cycle(ram_fifo, ram_encoded, ram_indices_encoded)

    tc.assertFalse(ram_fifo.stall.value)
    tc.assertFalse(ram_fifo.done.value)

    ram_fifo.advance <= 1
    yield Timer(1)

    yield cycle(ram_fifo, ram_encoded, ram_indices_encoded)

    ram_fifo.advance <= 0
    yield Timer(1)

    tc.assertFalse(ram_fifo.stall.value)
    tc.assertTrue(ram_fifo.done.value)

    model = RamFIFO(ram, ram_indices, bitwidth)
    model.verify(ram_fifo, tc)

@cocotb.test()
def reads_sixteen_four_bit_value_in_two_cycles(dut):
    tc = unittest.TestCase()
    ram_fifo = dut.ram_fifo

    RAM_PARALLEL = 16

    bitwidth = 1
    ram_fifo.bitwidth <= bitwidth
    yield reset_dut(ram_fifo)

    ram = [1, 2, 3, 0, 15, 7, 7, 9] * 2
    ram_indices = [5, 6, 7, 8] * 4
    ram_encoded, ram_indices_encoded = build_ram(ram, ram_indices, RAM_PARALLEL, bitwidth)

    parley_ram(ram_fifo, ram_encoded, ram_indices_encoded)
    yield Timer(1)

    tc.assertTrue(ram_fifo.stall.value)
    tc.assertFalse(ram_fifo.done.value)

    yield cycle(ram_fifo, ram_encoded, ram_indices_encoded)

    tc.assertFalse(ram_fifo.stall.value)
    tc.assertFalse(ram_fifo.done.value)

    ram_fifo.advance <= 1
    yield Timer(1)

    yield cycle(ram_fifo, ram_encoded, ram_indices_encoded)

    model = RamFIFO(ram, ram_indices, bitwidth)
    model.verify(ram_fifo, tc, advance=True)

    yield cycle(ram_fifo, ram_encoded, ram_indices_encoded)

    model.verify(ram_fifo, tc, advance=True)
    tc.assertTrue(ram_fifo.done.value)

@cocotb.test()
def restarts_cycle_if_advance_asserted_again(dut):
    tc = unittest.TestCase()
    ram_fifo = dut.ram_fifo

    RAM_PARALLEL = 16

    bitwidth = 1
    ram_fifo.bitwidth <= bitwidth
    yield reset_dut(ram_fifo)

    ram = [1, 2, 3, 0, 15, 7, 7, 9] * 2
    ram_indices = [5, 6, 7, 8] * 4
    ram_encoded, ram_indices_encoded = build_ram(ram, ram_indices, RAM_PARALLEL, bitwidth)

    parley_ram(ram_fifo, ram_encoded, ram_indices_encoded)
    yield Timer(1)

    tc.assertTrue(ram_fifo.stall.value)
    tc.assertFalse(ram_fifo.done.value)

    yield cycle(ram_fifo, ram_encoded, ram_indices_encoded)

    tc.assertFalse(ram_fifo.stall.value)
    tc.assertFalse(ram_fifo.done.value)

    ram_fifo.advance <= 1
    yield Timer(1)

    yield cycle(ram_fifo, ram_encoded, ram_indices_encoded)

    model = RamFIFO(ram, ram_indices, bitwidth)
    model.verify(ram_fifo, tc, advance=True)

    yield cycle(ram_fifo, ram_encoded, ram_indices_encoded)

    model.verify(ram_fifo, tc, advance=True)
    tc.assertTrue(ram_fifo.done.value)

    yield cycle(ram_fifo, ram_encoded, ram_indices_encoded)

    model = RamFIFO(ram, ram_indices, bitwidth)
    model.verify(ram_fifo, tc, advance=True)

    yield cycle(ram_fifo, ram_encoded, ram_indices_encoded)

    model.verify(ram_fifo, tc, advance=False)
    tc.assertTrue(ram_fifo.done.value)

    ram_fifo.advance <= 0
    yield Timer(1)

    yield cycle(ram_fifo, ram_encoded, ram_indices_encoded)

    model.verify(ram_fifo, tc, advance=False)
    tc.assertTrue(ram_fifo.done.value)

    yield cycle(ram_fifo, ram_encoded, ram_indices_encoded)

    model.verify(ram_fifo, tc, advance=False)
    tc.assertTrue(ram_fifo.done.value)