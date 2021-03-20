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
def crossbar_route_8bit_nostall(dut):
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
    #Setup inputs 
    bitwidth <=  2
    for i in range(16):
        products[i] <= i
        row_coordinate[i] <= i
        column_coordinate[i] <= i 

    clk <= 0
    yield Timer(100, units="ns")
    clk <= 1 
    yield Timer(100, units="ns")
    
    tc = unittest.TestCase()
    tc.assertEqual(int(crossbar_stall),0)


@cocotb.test()
def crossbar_route_4bit_nostall(dut):
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
    #Setup inputs 
    bitwidth <=  1
    acc = 0
    for i in range(64):
        acc |= (i%16) << (i%4)
        if i % 4 == 0:
            products[i//4] <= acc
            acc = 0
        row_coordinate[i] <= i
        column_coordinate[i] <= i 

    clk <= 0
    yield Timer(100, units="ns")
    clk <= 1 
    yield Timer(100, units="ns")
    tc = unittest.TestCase()
    tc.assertEqual(int(crossbar_stall),0)


@cocotb.test()
def crossbar_route_2bit_nostall(dut):
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
    #Setup inputs 
    bitwidth <=  0
    acc = 0
    for i in range(256):
        acc |= (i%4) << (i%16)
        if i % 16 == 0:
            products[i//16] <= acc
            acc = 0
        row_coordinate[i] <= i
        column_coordinate[i] <= i 

    clk <= 0
    yield Timer(100, units="ns")
    clk <= 1 
    yield Timer(100, units="ns")
    tc = unittest.TestCase()
    tc.assertEqual(int(crossbar_stall),0)

@cocotb.test()
def crossbar_route_8bit_stall_16clocks(dut):
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
    #Setup inputs 
    bitwidth <=  2
    for i in range(16):
        products[i] <= i
        row_coordinate[i] <= 5
        column_coordinate[i] <= 5 

    tc = unittest.TestCase()
    clk <= 0
    yield Timer(100, units="ns")
    clk <= 1 
    yield Timer(100, units="ns")
    tc.assertEqual(int(crossbar_stall),0)
    for i in range(15):
        clk <= 0
        yield Timer(100, units="ns")
        clk <= 1 
        yield Timer(100, units="ns")
        tc.assertEqual(int(crossbar_stall),1)
    clk <= 0
    yield Timer(100, units="ns")
    clk <= 1 
    yield Timer(100, units="ns")
    tc.assertEqual(int(crossbar_stall),0)


@cocotb.test()
def crossbar_route_4bit_stall_64clocks(dut):
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
    #Setup inputs 
    bitwidth <=  1
    acc = 0
    for i in range(64):
        acc |= (i%16) << (i%4)
        if i % 4 == 0:
            products[i//4] <= acc
            acc = 0
        row_coordinate[i] <= 5
        column_coordinate[i] <= 5 


    tc = unittest.TestCase()
    clk <= 0
    yield Timer(100, units="ns")
    clk <= 1 
    yield Timer(100, units="ns")
    tc.assertEqual(int(crossbar_stall),0)
    for i in range(63):
        clk <= 0
        yield Timer(100, units="ns")
        clk <= 1 
        yield Timer(100, units="ns")
        tc.assertEqual(int(crossbar_stall),1)
    clk <= 0
    yield Timer(100, units="ns")
    clk <= 1 
    yield Timer(100, units="ns")
    tc.assertEqual(int(crossbar_stall),0)


@cocotb.test()
def crossbar_route_2bit_stall_256clocks(dut):
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
    #Setup inputs 
    bitwidth <=  0
    acc = 0
    for i in range(256):
        acc |= (i%4) << (i%16)
        if i % 16 == 0:
            products[i//16] <= acc
            acc = 0
        row_coordinate[i] <= 5
        column_coordinate[i] <= 5


    tc = unittest.TestCase()
    clk <= 0
    yield Timer(100, units="ns")
    clk <= 1 
    yield Timer(100, units="ns")
    tc.assertEqual(int(crossbar_stall),0)
    for i in range(255):
        clk <= 0
        yield Timer(100, units="ns")
        clk <= 1 
        yield Timer(100, units="ns")
        tc.assertEqual(int(crossbar_stall),1)
    clk <= 0
    yield Timer(100, units="ns")
    clk <= 1 
    yield Timer(100, units="ns")
    tc.assertEqual(int(crossbar_stall),0)
