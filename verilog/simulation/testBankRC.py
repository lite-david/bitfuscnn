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
    
    tc.assertEqual(row, row_output.value.integer)
    tc.assertEqual(column, column_output.value.integer)
    return dut.entry.value.integer

@cocotb.test()
def test_bank_entry_to_rcc_inverts_bank(dut):
    tc = unittest.TestCase()
    BANK_COUNT = 32

    for bitwidth in range(0, 3):
        max_dim = BANK_COUNT >> bitwidth
        for row in range(max_dim):
            for col in range(max_dim):
                entry = yield set_rc(tc, dut, row,col, bitwidth)
                max_entry = max_dim**2 // BANK_COUNT
                tc.assertLessEqual(entry, max_entry)