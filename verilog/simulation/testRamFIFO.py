import cocotb
from cocotb.triggers import Timer
from cocotb.clock import Clock
import unittest


class RamFIFO:
    def __init__(self, ram, ram_indices, bitwidth):
        self.ram = ram[1:]
        self.ram_indices = ram_indices[1:]
        self.bitwidth = bitwidth
        self.index = 0

    def generate_next_8bit(self):
        value = self.ram[self.index]
        self.index += 1
        return value

    def generate_next(self):
        values = [0] * 4
        indices = [0] * 16
        if self.bitwidth == 2:
            indices[0:3] = self.ram_indices[self.index : self.index + 4]
            values = [
                self.generate_next_8bit(),
                self.generate_next_8bit(),
                self.generate_next_8bit(),
                self.generate_next_8bit(),
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


def parley_ram(ram_fifo, ram, ram_indices):
    if defined(ram_fifo.ram_address.value):
        address = ram_fifo.ram_address.value.integer
        if address < len(ram):
            value = ram[address]
            index = ram_indices[address]
            ram_fifo.ram_value <= value
            ram_fifo.ram_indices_value <= index


# def verify_8bit(tc, ram_fifo, ram, ram_indices):


# def verify_fifo(tc, ram_fifo, ram, ram_indices, bitwidth):
#     if bitwidth == 2:
#         verify_fifo(tc, ram_fifo, ram, ram_indices)


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
def reads_four_eight_bit_value_in_four_cycles(dut):
    tc = unittest.TestCase()
    ram_fifo = dut.ram_fifo

    bitwidth = 2
    ram_fifo.bitwidth <= bitwidth
    yield reset_dut(ram_fifo)

    ram = [4, 1, 2, 3, 4]
    ram_indices = [0, 5, 6, 7, 8]

    for i in range(4):
        yield cycle(ram_fifo, ram, ram_indices)

        tc.assertFalse(ram_fifo.done.value)
        tc.assertFalse(ram_fifo.data_ready.value)

    yield cycle(ram_fifo, ram, ram_indices)

    tc.assertTrue(ram_fifo.done.value)
    tc.assertTrue(ram_fifo.data_ready.value)

    ram_fifo.advance <= 1
    yield Timer(1)

    yield cycle(ram_fifo, ram, ram_indices)

    ram_fifo.advance <= 0
    yield Timer(1)

    model = RamFIFO(ram, ram_indices, bitwidth)
    model.verify(ram_fifo, tc)

@cocotb.test()
def reads_four_eight_bit_value_from_first_batch(dut):
    tc = unittest.TestCase()
    ram_fifo = dut.ram_fifo

    bitwidth = 2
    ram_fifo.bitwidth <= bitwidth
    yield reset_dut(ram_fifo)

    ram = [8, 1, 2, 3, 4, 2, 4, 6, 8]
    ram_indices = [0, 5, 6, 7, 8, 1, 2, 3, 4]

    for i in range(4):
        yield cycle(ram_fifo, ram, ram_indices)

        tc.assertFalse(ram_fifo.done.value)
        tc.assertFalse(ram_fifo.data_ready.value)

    yield cycle(ram_fifo, ram, ram_indices)

    tc.assertFalse(ram_fifo.done.value)
    tc.assertTrue(ram_fifo.data_ready.value)

    ram_fifo.advance <= 1
    yield Timer(1)

    yield cycle(ram_fifo, ram, ram_indices)

    ram_fifo.advance <= 0
    yield Timer(1)

    tc.assertFalse(ram_fifo.done.value)
    tc.assertFalse(ram_fifo.data_ready.value)

@cocotb.test()
def reads_four_eight_bit_value_from_second_batch(dut):
    tc = unittest.TestCase()
    ram_fifo = dut.ram_fifo

    bitwidth = 2
    ram_fifo.bitwidth <= bitwidth
    yield reset_dut(ram_fifo)

    ram = [8, 1, 2, 3, 4, 2, 4, 6, 8]
    ram_indices = [0, 5, 6, 7, 8, 1, 2, 3, 4]

    for i in range(4):
        yield cycle(ram_fifo, ram, ram_indices)

    yield cycle(ram_fifo, ram, ram_indices)

    ram_fifo.advance <= 1
    yield Timer(1)

    yield cycle(ram_fifo, ram, ram_indices)

    ram_fifo.advance <= 0
    yield Timer(1)

    model = RamFIFO(ram, ram_indices, bitwidth)
    model.verify(ram_fifo, tc, advance=False)

    for i in range(2):
        yield cycle(ram_fifo, ram, ram_indices)

        tc.assertFalse(ram_fifo.done.value)
        tc.assertFalse(ram_fifo.data_ready.value)

        model.verify(ram_fifo, tc, advance=False)

    yield cycle(ram_fifo, ram, ram_indices)

    tc.assertTrue(ram_fifo.done.value)
    tc.assertTrue(ram_fifo.data_ready.value)

    model.verify(ram_fifo, tc, advance=True)

    ram_fifo.advance <= 1
    yield Timer(1)

    yield cycle(ram_fifo, ram, ram_indices)

    ram_fifo.advance <= 0
    yield Timer(1)

    model.verify(ram_fifo, tc, advance=False)
