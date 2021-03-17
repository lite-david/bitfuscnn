import cocotb
from cocotb.triggers import Timer
from cocotb.clock import Clock
import sys
sys.path
sys.path.append('../../')
import unittest

@cocotb.test()
def test_8bit_signed(dut):
    tc = unittest.TestCase()
    a = 200
    b = -100
    c = a*b
    #dut.fusion_unit.qu_0.clk = 0
    #dut.fusion_unit.qu_0.a = a
    #dut.fusion_unit.qu_0.b = b
    #dut.fusion_unit.qu_0.sa = 0
    #dut.fusion_unit.qu_0.sb = 3 
    #dut.fusion_unit.qu_0.sft_ctrl_1 = 1
    #dut.fusion_unit.qu_0.sft_ctrl_2 = 1
    #dut.fusion_unit.qu_0.sft_ctrl_3 = 2
    # dut.fusion_unit.clk = 0
    dut.fusion_unit.a = a
    dut.fusion_unit.b = b
    dut.fusion_unit.sa = 0
    dut.fusion_unit.sb = 1
    dut.fusion_unit.cfga = 2
    dut.fusion_unit.cfgb = 2

    yield Timer(1)

    x = int(dut.fusion_unit.out)
    if x >= 9223372036854775808:
        x -= 18446744073709551616

    tc.assertEqual(x, c)

#@cocotb.test()
#def test_4bit_signed(dut):
#    tc = unittest.TestCase()
#    a = 10
#    b = -7
#    c = a*b
#    dut.fusion_unit.clk = 0
#    dut.fusion_unit.a = a
#    dut.fusion_unit.b = b
#    dut.fusion_unit.sa = 0
#    dut.fusion_unit.sb = 1
#    dut.fusion_unit.cfga = 2
#    dut.fusion_unit.cfgb = 2
#
#    yield Timer(1)
#
#    tc.assertEqual(int(dut.out), c)
#
#@cocotb.test()
#def test_2bit_signed(dut):
#    tc = unittest.TestCase()
#    a = 200
#    b = -100
#    c = a*b
#    dut.fusion_unit.clk = 0
#    dut.fusion_unit.a = a
#    dut.fusion_unit.b = b
#    dut.fusion_unit.sa = 0
#    dut.fusion_unit.sb = 1
#    dut.fusion_unit.cfga = 2
#    dut.fusion_unit.cfgb = 2
#
#    yield Timer(1)
#
#    tc.assertEqual(int(dut.out), c)

@cocotb.test()
def test_8bit_unsigned(dut):
    tc = unittest.TestCase()
    a = 200
    b = 100
    c = a*b
    # dut.fusion_unit.clk = 0
    dut.fusion_unit.a = a
    dut.fusion_unit.b = b
    dut.fusion_unit.sa = 0
    dut.fusion_unit.sb = 0
    dut.fusion_unit.cfga = 2
    dut.fusion_unit.cfgb = 2

    yield Timer(1)

    x = int(dut.fusion_unit.out)
    if x >= 9223372036854775808:
        x -= 18446744073709551616

    tc.assertEqual(x, c)

#@cocotb.test()
#def test_4bit_unsigned(dut):
#    tc = unittest.TestCase()
#    a = 200
#    b = -100
#    c = a*b
#    dut.fusion_unit.clk = 0
#    dut.fusion_unit.a = a
#    dut.fusion_unit.b = b
#    dut.fusion_unit.sa = 0
#    dut.fusion_unit.sb = 1
#    dut.fusion_unit.cfga = 2
#    dut.fusion_unit.cfgb = 2
#
#    yield Timer(1)
#
#    tc.assertEqual(int(dut.out), c)
#
#@cocotb.test()
#def test_2bit_unsigned(dut):
#    tc = unittest.TestCase()
#    a = 200
#    b = -100
#    c = a*b
#    dut.fusion_unit.clk = 0
#    dut.fusion_unit.a = a
#    dut.fusion_unit.b = b
#    dut.fusion_unit.sa = 0
#    dut.fusion_unit.sb = 1
#    dut.fusion_unit.cfga = 2
#    dut.fusion_unit.cfgb = 2
#
#    yield Timer(1)
#
#    tc.assertEqual(int(dut.out), c)
