import cocotb
from cocotb.triggers import Timer
from cocotb.clock import Clock

@cocotb.test()
def testBitfuscnn(dut):
    """Try accessing the design."""
    # Get a reference to the "clk" signal on the top-level
    clk = dut.clk
    cocotb.fork(Clock(dut.clk, 100, units='ns').start())

    dut.limiter_low.value = 0
    dut.limiter_high.value = 0

    # spi_sclk = dut.spi_sclk
    # spi_cs = dut.spi_cs
    # spi_mosi = dut.spi_mosi
    # spi_miso = dut.spi_miso

    # spi_cs.value = 0b00
    # spi_mosi.value = 0
    # spi_sclk.value = 0
    # # yield demoTest(dut)
    # # return
    # print("Waiting 100 clock cycles")
    # # yield Timer(10, units='us')
    # print("spi_cs = " + str(dut.spi_miso))
    # print("Copying ASM")
    # yield loadConfig(spi_sclk, spi_mosi, spi_miso, spi_cs)
    # # yield Timer(1, units='ms')
    # print("Sending dac command")
    # # limiterThread = cocotb.fork(cycleLimiter(dut.limiter_low, dut.limiter_high))
    # yield Timer(100*1024, units='ns')
    # with cocotb.wavedrom.trace(dut.ser, dut.cpu.sp, dut.cpu.op8, dut.cpu.pc, dut.cpu.op, dut.cpu.tos, dut.cpu.nos, spi_cs, clk=clk) as waves:
    #     yield Timer(1, units='us')
    #     spi_sclk.value = 1
    #     spi_cs.value = 0b10
    #     yield Timer(100, units='ns')
    #     spi_sclk.value = 0
    #     yield Timer(900, units='ns')
    #     spi_cs.value = 0b00
    #     yield Timer(18, units='us')
    #     # yield spiScan(spi_sclk, spi_mosi, spi_miso, spi_cs)
    #     waves.dumpj(header = {'text':'WaveDrom example', 'tick':0})
    #     waves.write('wavedrom.json', header = {'tick':0}, config = {'hscale':3})

    # # global stop_threads
    # # stop_threads = True
    # # yield limiterThread.join()
    # dut._log.info("Running test!")
    # # for cycle in range(10):
    # #     result = cycle;
    # #     print("Cycle #" + str(result))
    # #     spi_mosi.value = result%2;
    # #     spi_sclk.value = 0
    # #     yield Timer(1, units='us')
    # #     print(str(spi_mosi) + " -> " +
    # #         str(spi_miso) + "; falling")
    # #     spi_sclk.value = 1
    # #     yield Timer(1, units='us')
    # #     print(str(spi_mosi) + " -> " +
    # #         str(spi_miso) + "; rising")
    # dut._log.info("Running test!")
