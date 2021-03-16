import cocotb
from cocotb.triggers import Timer
import sys

sys.path
sys.path.append("../../")

import ppu as ppu_py
import unittest


@cocotb.coroutine
def set_rc(tc, dut, row, column, bitwidth):
    row_wire = dut.row
    column_wire = dut.column
    bitwidth_wire = dut.bitwidth
    row_output = dut.row_output
    column_output = dut.column_output
    row_wire <= row
    column_wire <= column
    bitwidth_wire <= bitwidth
    yield Timer(1)
    tc.assertEqual(row, row_output.value)
    tc.assertEqual(column, column_output.value)

@cocotb.test()
def test_bank_entry_to_rcc_inverts_bank(dut):
    tc = unittest.TestCase()
    # ppu = dut.ppu
    # yield reset_dut(ppu)
    BUFFER_COUNT = 32
    # BUFFER_WIDTH = 32
    # buffer_info = ppu.BufferAddressInfo(BUFFER_COUNT)

    # for bitwidth in range(0, 3):


    yield set_rc(tc, dut, 0,0, 2)
    yield set_rc(tc, dut, 5,0, 2)
    yield set_rc(tc, dut, 0,3, 2)
    yield set_rc(tc, dut, 7,20, 2)
    # row = 0
    # column = 0
    # channel = 0
    # bank = ppu_py.bank_from_rcc(row, column, channel, buffer_info)
    # entry = ppu_py.entry_from_rcc(row, column, channel, buffer_info)
    # rcc = ppu_py.bank_entry_to_rcc(bank, entry, buffer_info)
    # tc.assertEqual(rcc, (row, column, channel))

    # row = 5
    # column = 0
    # channel = 0
    # bank = ppu_py.bank_from_rcc(row, column, channel, buffer_info)
    # entry = ppu_py.entry_from_rcc(row, column, channel, buffer_info)
    # rcc = ppu_py.bank_entry_to_rcc(bank, entry, buffer_info)
    # tc.assertEqual(rcc, (row, column, channel))

    # row = 0
    # column = 3
    # channel = 0
    # bank = ppu_py.bank_from_rcc(row, column, channel, buffer_info)
    # entry = ppu_py.entry_from_rcc(row, column, channel, buffer_info)
    # rcc = ppu_py.bank_entry_to_rcc(bank, entry, buffer_info)
    # tc.assertEqual(rcc, (row, column, channel))

    # row = 7
    # column = 20
    # channel = 0
    # bank = ppu_py.bank_from_rcc(row, column, channel, buffer_info)
    # entry = ppu_py.entry_from_rcc(row, column, channel, buffer_info)
    # rcc = ppu_py.bank_entry_to_rcc(bank, entry, buffer_info)
    # tc.assertEqual(rcc, (row, column, channel))