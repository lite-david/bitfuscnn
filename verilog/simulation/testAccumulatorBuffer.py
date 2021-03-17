import cocotb
from cocotb.triggers import Timer
from cocotb.clock import Clock
import unittest
from enum import Enum
import math


class BufferAddressInfo:
    def __init__(tc, buffer_count, tile_size=4):
        tc.buffer_count = buffer_count
        tc.tile_size = tile_size


@cocotb.coroutine
def reset_dut(dut):
    dut.reset_n <= 0
    dut.clk <= 0
    yield Timer(100, units="ns")
    dut.reset_n <= 1
    yield Timer(100, units="ns")


@cocotb.coroutine
def set_bit(wire, i, val):
    old_val = wire.value
    not_mask = 1 << i
    mask = not_mask ^ 0xFFFFFF
    masked_val = mask & old_val
    new_val = (val << i) | masked_val
    wire <= new_val
    # print(i, val)
    # print("{},{},{},{},{}".format(bin(old_val), bin(new_val), bin(mask), bin(masked_val), bin(val << i)))
    yield Timer(1)


def get_bit(wire, i):
    not_mask = 1 << i
    mask = not_mask ^ 0xFFFFFF
    if wire.value & mask != 0:
        return 1
    return 0


def get_ppu_output(ppu, bank_count):
    ppu_output = PPUOutput()
    ppu_output.cycle_done = ppu.cycle_done.value
    ppu_output.clear_to_send = False
    if ppu.clear_to_send.value == 1:
        ppu_output.clear_to_send = True
    ppu_output.exchange_done = ppu.exchange_done.value
    ppu_output.buffer_outputs = []

    for i in range(bank_count):
        if ppu.buffer_write_enable[i] == 0:
            new_value = (0, -1, -1, -1)
            ppu_output.buffer_outputs.append(new_value)
            continue
        value = ppu.buffer_data_write[i].value
        row = ppu.buffer_row_write[i].value
        column = ppu.buffer_column_write[i].value
        new_value = (value, row, column, 0)
        ppu_output.buffer_outputs.append(new_value)

    ppu_output.neighbor_outputs = []
    for i in range(8):
        val = ppu.neighbor_output_value[i].value.integer
        row = ppu.neighbor_output_row[i].value.integer
        column = ppu.neighbor_output_column[i].value.integer
        write_enable = ppu.neighbor_output_write_enable[i]
        if write_enable == 0:
            new_value = (0, -1, -1, -1)
            ppu_output.neighbor_outputs.append(new_value)
            continue
        new_value = (val, row, column, 0)
        ppu_output.neighbor_outputs.append(new_value)

    return ppu_output


def defined(value):
    string = value._str
    if "x" in string or "z" in string:
        return False
    return True


def bank_from_rcc(row, column, channel, buffer_address_info, bitwidth=0):
    row_upper = row >> bitwidth
    row_section = row % (1 << bitwidth)
    small_buffcount = buffer_address_info.buffer_count >> bitwidth
    shift = row_upper * 3
    shift = shift % buffer_address_info.buffer_count
    index = (
        column + shift + row_section * small_buffcount
    ) % buffer_address_info.buffer_count
    return int(index)


def entry_from_rcc(row, column, channel, buffer_address_info, bitwidth=0):
    return row >> bitwidth


def bank_entry_to_rc(bank, entry, buffer_address_info, bitwidth=0):
    small_buffcount = buffer_address_info.buffer_count >> bitwidth
    row = entry
    row_msb = row << bitwidth
    shift = row * 3
    shift = shift % buffer_address_info.buffer_count
    column = bank - shift
    if bank < shift:
        column = bank + buffer_address_info.buffer_count - shift
    col_div = int(math.log2(buffer_address_info.buffer_count))
    row_lsb = column >> (col_div - bitwidth)
    column = column % small_buffcount
    row = row_msb | row_lsb

    return (row, column)


@cocotb.coroutine
def read_output(accumulator_buffer, entry):
    accumulator_buffer.buffer_bank_entry <= entry
    yield Timer(1)
    return accumulator_buffer.buffer_data_read.value


def set_write(accumulator_buffer, row, column, data, we):
    accumulator_buffer.buffer_row_write <= row
    accumulator_buffer.buffer_column_write <= column
    accumulator_buffer.buffer_data_write <= data
    accumulator_buffer.buffer_write_enable <= we


@cocotb.coroutine
def cycle_write(accumulator_buffer, row, column, data, we):
    set_write(accumulator_buffer, row, column, data, we)
    yield Timer(1)
    accumulator_buffer.clk <= 1
    yield Timer(1)
    accumulator_buffer.clk <= 0
    yield Timer(1)


@cocotb.test()
def after_reset_reads_zero(dut):
    tc = unittest.TestCase()
    accumulator_buffer = dut.accumulator_buffer
    yield reset_dut(accumulator_buffer)
    BANK_WIDTH = 256

    accumulator_buffer.bitwidth <= 0

    val = yield read_output(accumulator_buffer, 0)
    tc.assertEqual(val, 0)


@cocotb.test()
def write_after_reset_sets_value(dut):
    tc = unittest.TestCase()
    accumulator_buffer = dut.accumulator_buffer
    yield reset_dut(accumulator_buffer)
    BANK_WIDTH = 256
    BITWIDTH = 0
    BANK_COUNT = 256
    buffer_info = BufferAddressInfo(BANK_COUNT)

    accumulator_buffer.bitwidth <= BITWIDTH

    bank = 0
    entry = 0
    value = 1
    row, column = bank_entry_to_rc(bank, entry, buffer_info, bitwidth=BITWIDTH)
    yield cycle_write(accumulator_buffer, row, column, value, 1)

    val = yield read_output(accumulator_buffer, entry)
    tc.assertEqual(val, value)


@cocotb.test()
def adjacent_write_preserves_value(dut):
    tc = unittest.TestCase()
    accumulator_buffer = dut.accumulator_buffer
    yield reset_dut(accumulator_buffer)
    BANK_WIDTH = 256
    BITWIDTH = 0
    BANK_COUNT = 256
    buffer_info = BufferAddressInfo(BANK_COUNT)

    accumulator_buffer.bitwidth <= BITWIDTH

    bank = 0
    entry = 0
    value = 1
    row, column = bank_entry_to_rc(bank, entry, buffer_info, bitwidth=BITWIDTH)
    yield cycle_write(accumulator_buffer, row, column, value, 1)

    bank = 0
    entry = 1
    value = 3
    row, column = bank_entry_to_rc(bank, entry, buffer_info, bitwidth=BITWIDTH)
    yield cycle_write(accumulator_buffer, row, column, value, 1)

    val = yield read_output(accumulator_buffer, 0)
    tc.assertEqual(val, 1)

    bank = 0
    entry = 0
    value = 1
    row, column = bank_entry_to_rc(bank, entry, buffer_info, bitwidth=BITWIDTH)
    yield cycle_write(accumulator_buffer, row, column, value, 1)

    val = yield read_output(accumulator_buffer, 1)
    tc.assertEqual(val, 3)


@cocotb.test()
def repeated_write_accumulates(dut):
    tc = unittest.TestCase()
    accumulator_buffer = dut.accumulator_buffer
    yield reset_dut(accumulator_buffer)
    BANK_WIDTH = 256
    BITWIDTH = 0
    BANK_COUNT = 256
    buffer_info = BufferAddressInfo(BANK_COUNT)

    accumulator_buffer.bitwidth <= BITWIDTH

    bank = 0
    entry = 0
    value = 1
    row, column = bank_entry_to_rc(bank, entry, buffer_info, bitwidth=BITWIDTH)
    yield cycle_write(accumulator_buffer, row, column, value, 1)
    yield cycle_write(accumulator_buffer, row, column, value, 1)

    val = yield read_output(accumulator_buffer, 0)
    tc.assertEqual(val, 2)


@cocotb.test()
def overflow_is_ignored(dut):
    tc = unittest.TestCase()
    accumulator_buffer = dut.accumulator_buffer
    yield reset_dut(accumulator_buffer)
    BANK_WIDTH = 256
    BITWIDTH = 0
    BANK_COUNT = 256
    buffer_info = BufferAddressInfo(BANK_COUNT)

    accumulator_buffer.bitwidth <= BITWIDTH

    bank = 0
    entry = 0
    value = 15
    row, column = bank_entry_to_rc(bank, entry, buffer_info, bitwidth=BITWIDTH)
    yield cycle_write(accumulator_buffer, row, column, value, 1)
    yield cycle_write(accumulator_buffer, row, column, value, 1)

    val = yield read_output(accumulator_buffer, 0)
    tc.assertEqual(val, 14)


@cocotb.test()
def larger_bitwidth_accumulates_larger_value(dut):
    tc = unittest.TestCase()
    accumulator_buffer = dut.accumulator_buffer
    yield reset_dut(accumulator_buffer)
    BANK_WIDTH = 256
    BITWIDTH = 1
    BANK_COUNT = 256
    buffer_info = BufferAddressInfo(BANK_COUNT)

    accumulator_buffer.bitwidth <= BITWIDTH

    bank = 0
    entry = 0
    value = 15
    row, column = bank_entry_to_rc(bank, entry, buffer_info, bitwidth=BITWIDTH)
    yield cycle_write(accumulator_buffer, row, column, value, 1)
    yield cycle_write(accumulator_buffer, row, column, value, 1)

    val = yield read_output(accumulator_buffer, 0)
    tc.assertEqual(val, 30)


@cocotb.test()
def larger_bitwidth_still_overflows(dut):
    tc = unittest.TestCase()
    accumulator_buffer = dut.accumulator_buffer
    yield reset_dut(accumulator_buffer)
    BANK_WIDTH = 256
    BITWIDTH = 1
    BANK_COUNT = 256
    buffer_info = BufferAddressInfo(BANK_COUNT)

    accumulator_buffer.bitwidth <= BITWIDTH

    bank = 0
    entry = 0
    value = 255
    row, column = bank_entry_to_rc(bank, entry, buffer_info, bitwidth=BITWIDTH)
    yield cycle_write(accumulator_buffer, row, column, value, 1)
    yield cycle_write(accumulator_buffer, row, column, value, 1)

    val = yield read_output(accumulator_buffer, 0)
    tc.assertEqual(val, 254)


@cocotb.test()
def adjacent_write_preserves_value_in_larger_bitwidth(dut):
    tc = unittest.TestCase()
    accumulator_buffer = dut.accumulator_buffer
    yield reset_dut(accumulator_buffer)
    BANK_WIDTH = 256
    BITWIDTH = 1
    BANK_COUNT = 256
    buffer_info = BufferAddressInfo(BANK_COUNT)

    accumulator_buffer.bitwidth <= BITWIDTH

    bank = 0
    entry = 0
    value = 255
    row, column = bank_entry_to_rc(bank, entry, buffer_info, bitwidth=BITWIDTH)
    yield cycle_write(accumulator_buffer, row, column, value, 1)

    bank = 0
    entry = 1
    value = 129
    row, column = bank_entry_to_rc(bank, entry, buffer_info, bitwidth=BITWIDTH)
    yield cycle_write(accumulator_buffer, row, column, value, 1)

    val = yield read_output(accumulator_buffer, 0)
    tc.assertEqual(val, 255)

    bank = 0
    entry = 0
    value = 255
    row, column = bank_entry_to_rc(bank, entry, buffer_info, bitwidth=BITWIDTH)
    yield cycle_write(accumulator_buffer, row, column, value, 1)

    val = yield read_output(accumulator_buffer, 1)
    tc.assertEqual(val, 129)


@cocotb.test()
def adjacent_write_preserves_value_in_largest_bitwidth(dut):
    tc = unittest.TestCase()
    accumulator_buffer = dut.accumulator_buffer
    yield reset_dut(accumulator_buffer)
    BANK_WIDTH = 256
    BITWIDTH = 2
    BANK_COUNT = 256
    buffer_info = BufferAddressInfo(BANK_COUNT)

    accumulator_buffer.bitwidth <= BITWIDTH

    bank = 0
    entry = 0
    value = 0x7FFE
    row, column = bank_entry_to_rc(bank, entry, buffer_info, bitwidth=BITWIDTH)
    yield cycle_write(accumulator_buffer, row, column, value, 1)

    bank = 0
    entry = 1
    value = 0x8001
    row, column = bank_entry_to_rc(bank, entry, buffer_info, bitwidth=BITWIDTH)
    yield cycle_write(accumulator_buffer, row, column, value, 1)

    val = yield read_output(accumulator_buffer, 0)
    tc.assertEqual(val, 0x7FFE)

    bank = 0
    entry = 0
    value = 0x7FFE
    row, column = bank_entry_to_rc(bank, entry, buffer_info, bitwidth=BITWIDTH)
    yield cycle_write(accumulator_buffer, row, column, value, 1)

    val = yield read_output(accumulator_buffer, 1)
    tc.assertEqual(val, 0x8001)


@cocotb.test()
def transfer_updates_all_values(dut):
    tc = unittest.TestCase()
    accumulator_buffer = dut.accumulator_buffer
    yield reset_dut(accumulator_buffer)
    BANK_WIDTH = 256
    BITWIDTH = 0
    BANK_COUNT = 256
    buffer_info = BufferAddressInfo(BANK_COUNT)

    accumulator_buffer.bitwidth <= BITWIDTH

    bank = 0
    entry = 0
    value = 1
    row, column = bank_entry_to_rc(bank, entry, buffer_info, bitwidth=BITWIDTH)
    yield cycle_write(accumulator_buffer, row, column, value, 1)

    accumulator_buffer.data_in <= 0xDEADBEEF
    accumulator_buffer.transfer <= 1
    yield Timer(1)
    accumulator_buffer.clk <= 1
    yield Timer(1)
    accumulator_buffer.data_in <= 0
    accumulator_buffer.transfer <= 0
    accumulator_buffer.clk <= 0
    yield Timer(1)

    val = yield read_output(accumulator_buffer, 0)
    tc.assertEqual(val, 0xF)
    val = yield read_output(accumulator_buffer, 1)
    tc.assertEqual(val, 0xE)
    val = yield read_output(accumulator_buffer, 2)
    tc.assertEqual(val, 0xE)
    val = yield read_output(accumulator_buffer, 3)
    tc.assertEqual(val, 0xB)
    val = yield read_output(accumulator_buffer, 4)
    tc.assertEqual(val, 0xD)
    val = yield read_output(accumulator_buffer, 5)
    tc.assertEqual(val, 0xA)
    val = yield read_output(accumulator_buffer, 6)
    tc.assertEqual(val, 0xE)
    val = yield read_output(accumulator_buffer, 7)
    tc.assertEqual(val, 0xD)


@cocotb.test()
def only_writes_with_we(dut):
    tc = unittest.TestCase()
    accumulator_buffer = dut.accumulator_buffer
    yield reset_dut(accumulator_buffer)
    BANK_WIDTH = 256
    BITWIDTH = 1
    BANK_COUNT = 256
    buffer_info = BufferAddressInfo(BANK_COUNT)

    accumulator_buffer.bitwidth <= BITWIDTH

    bank = 0
    entry = 0
    value = 255
    row, column = bank_entry_to_rc(bank, entry, buffer_info, bitwidth=BITWIDTH)
    yield cycle_write(accumulator_buffer, row, column, value, 0)

    val = yield read_output(accumulator_buffer, 0)
    tc.assertEqual(val, 0)
    yield cycle_write(accumulator_buffer, row, column, value, 1)
    yield cycle_write(accumulator_buffer, row, column, value, 0)

    val = yield read_output(accumulator_buffer, 0)
    tc.assertEqual(val, 255)


@cocotb.test()
def accumulator_does_not_overflow(dut):
    tc = unittest.TestCase()
    accumulator_buffer = dut.accumulator_buffer
    yield reset_dut(accumulator_buffer)
    BANK_WIDTH = 256
    BITWIDTH = 0
    BANK_COUNT = 256
    buffer_info = BufferAddressInfo(BANK_COUNT)

    accumulator_buffer.bitwidth <= BITWIDTH

    bank = 0
    entry = 0
    value = 1
    we = 1
    row, column = bank_entry_to_rc(bank, entry, buffer_info, bitwidth=BITWIDTH)
    for i in range(10):
        yield cycle_write(accumulator_buffer, row, column, value, we)

    val = yield read_output(accumulator_buffer, entry)
    tc.assertEqual(val, 7)

@cocotb.test()
def accumulator_does_not_underflow(dut):
    tc = unittest.TestCase()
    accumulator_buffer = dut.accumulator_buffer
    yield reset_dut(accumulator_buffer)
    BANK_WIDTH = 256
    BITWIDTH = 0
    BANK_COUNT = 256
    buffer_info = BufferAddressInfo(BANK_COUNT)

    accumulator_buffer.bitwidth <= BITWIDTH

    bank = 0
    entry = 0
    value = 0b1111 #-1
    we = 1
    row, column = bank_entry_to_rc(bank, entry, buffer_info, bitwidth=BITWIDTH)
    for i in range(10):
        yield cycle_write(accumulator_buffer, row, column, value, we)

    val = yield read_output(accumulator_buffer, entry)
    tc.assertEqual(val, 0b1001) #-7