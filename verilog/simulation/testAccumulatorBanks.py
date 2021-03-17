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
def read_front_output(accumulator_banks, bank, entry):
    accumulator_banks.front_buffer_bank_read <= bank
    accumulator_banks.front_buffer_bank_entry <= entry
    yield Timer(1)
    return accumulator_banks.front_buffer_data_read.value


@cocotb.coroutine
def read_back_output(accumulator_banks, bank, entry):
    accumulator_banks.back_buffer_bank_read <= bank
    accumulator_banks.back_buffer_bank_entry <= entry
    yield Timer(1)
    return accumulator_banks.back_buffer_data_read.value


def set_front_write(accumulator_banks, num, row, column, data, we):
    accumulator_banks.front_buffer_row_write[num] <= row
    accumulator_banks.front_buffer_column_write[num] <= column
    accumulator_banks.front_buffer_data_write[num] <= data
    accumulator_banks.front_buffer_write_enable[num] <= we


def set_back_write(accumulator_banks, num, row, column, data, we):
    accumulator_banks.back_buffer_row_write[num] <= row
    accumulator_banks.back_buffer_column_write[num] <= column
    accumulator_banks.back_buffer_data_write[num] <= data
    accumulator_banks.back_buffer_write_enable[num] <= we


@cocotb.coroutine
def cycle_write(
    accumulator_banks,
    front_row,
    front_column,
    front_data,
    front_we,
    back_row,
    back_column,
    back_data,
    back_we,
    bitwidth = 0
):
    bai = BufferAddressInfo(256)
    front_bank = bank_from_rcc(front_row, front_column, 0, bai)
    back_bank = bank_from_rcc(back_row, back_column, 0, bai)
    set_front_write(accumulator_banks,front_bank, front_row, front_column, front_data, front_we)
    set_back_write(accumulator_banks,back_bank, back_row, back_column, back_data, back_we)
    yield Timer(1)
    accumulator_banks.clk <= 1
    yield Timer(1)
    accumulator_banks.clk <= 0
    yield Timer(1)


@cocotb.test()
def writes_separately_to_front_and_back(dut):
    tc = unittest.TestCase()
    accumulator_banks = dut.accumulator_banks
    yield reset_dut(accumulator_banks)
    BANK_WIDTH = 256
    BITWIDTH = 1
    BANK_COUNT = 256
    buffer_info = BufferAddressInfo(BANK_COUNT)

    accumulator_banks.bitwidth <= BITWIDTH

    front_bank = 5
    front_entry = 0
    front_value = 0x01
    front_we = 1
    front_row, front_column = bank_entry_to_rc(
        front_bank, front_entry, buffer_info, bitwidth=BITWIDTH
    )

    back_bank = 8
    back_entry = 0
    back_value = 0xAB
    back_we = 1
    back_row, back_column = bank_entry_to_rc(
        back_bank, back_entry, buffer_info, bitwidth=BITWIDTH
    )
    yield cycle_write(
        accumulator_banks,
        front_row,
        front_column,
        front_value,
        front_we,
        back_row,
        back_column,
        back_value,
        back_we,
        bitwidth=BITWIDTH
    )

    val = yield read_front_output(accumulator_banks, front_bank, front_entry)
    tc.assertEqual(val, front_value)

    val = yield read_back_output(accumulator_banks, back_bank, back_entry)
    tc.assertEqual(val, back_value)
