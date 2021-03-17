import cocotb
from cocotb.triggers import Timer
from cocotb.clock import Clock
import sys
sys.path
sys.path.append('../../')
import unittest
import utils
import bitfuscnn


@cocotb.coroutine
def reset_dut(dut):
    reset = dut.crossbar.reset_n
    reset <= 0
    yield Timer(100, units="ns")
    reset <= 1
    yield Timer(100, units="ns")

@cocotb.test()
def crossbar_route_8bit(dut):
    clk = dut.crossbar.clk
    bitwidth = dut.crossbar.bitwidth
    products = dut.crossbar.products 
    row_coordinate = dut.crossbar.row_coordinate
    column_coordinate = dut.crossbar.column_coordinate    

    buffer_row_write = dut.crossbar.buffer_row_write
    buffer_column_write = dut.crossbar.buffer_column_write
    buffer_data_write = dut.crossbar.buffer_data_write
    buffer_write_enable = dut.crossbar.buffer_write_enable
    crossbar_stall = dut.crossbar.crossbar_stall
    inputs_sent = dut.crossbar.inputs_sent
    next_inputs_sent = dut.crossbar.next_inputs_sent
    next_buffer_write_enable = dut.crossbar.next_buffer_write_enable
    used_banks = dut.crossbar.used_banks

    yield reset_dut(dut)
    clk <= 0
    yield Timer(100, units="ns")
    #Setup inputs 
    bitwidth <=  2
    for i in range(16):
        products[i] <= i
        row_coordinate[i] <= 5
        column_coordinate[i] <= 5 

    clk <= 1 
    yield Timer(100, units="ns")


    print(inputs_sent.value)
    print(next_inputs_sent.value)
    print(used_banks.value)
    
    clk <= 0
    yield Timer(100, units="ns")
    clk <= 1 
    yield Timer(100, units="ns")

    print(inputs_sent.value)
    print(next_inputs_sent.value)
    print(used_banks.value)
    
    clk <= 0
    yield Timer(100, units="ns")
    clk <= 1 
    yield Timer(100, units="ns")
    
    print(inputs_sent.value)
    print(next_inputs_sent.value)
    print(used_banks.value)
    

    clk <= 0
    yield Timer(100, units="ns")
    clk <= 1 
    yield Timer(100, units="ns")
    
    print(inputs_sent.value)
    print(next_inputs_sent.value)
    print(used_banks.value)



