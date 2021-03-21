BITFUSCNN=$(PWD)/../verilog
BITFUSCNN_SRC= $(BITFUSCNN)/bank_from_rc.sv $(BITFUSCNN)/rc_from_bank.sv
BITFUSCNN_SRC+= $(BITFUSCNN)/top.sv $(BITFUSCNN)/sim_top.sv $(BITFUSCNN)/ppu.sv $(BITFUSCNN)/coordinatecomputation.sv
BITFUSCNN_SRC+= $(BITFUSCNN)/neighbor_input_processor.sv  $(BITFUSCNN)/output_partials.sv 
BITFUSCNN_SRC+= $(BITFUSCNN)/output_accumulator.sv $(BITFUSCNN)/accumulator_buffer.sv
BITFUSCNN_SRC+= $(BITFUSCNN)/accumulator_bank.sv $(BITFUSCNN)/accumulator_banks.sv
BITFUSCNN_SRC+= $(BITFUSCNN)/fusion_unit.sv $(BITFUSCNN)/bitbrick.sv $(BITFUSCNN)/quarter_unit.sv
BITFUSCNN_SRC+= $(BITFUSCNN)/crossbar.sv $(BITFUSCNN)/bitfuscnn.sv $(BITFUSCNN)/ram_fifo.sv
# GPS_SRC+= $(GPS)/FULL_ADDER.v $(GPS)/LOGGER.v $(GPS)/SAMPLER.v
VERILOG_SOURCES = $(BITFUSCNN_SRC)
# VERILOG_SOURCES+= $(XILINX)/verilog/src/glbl.v
# COMPILE_ARGS+= -y$(XILINX)/verilog/src/simprims
# COMPILE_ARGS+= -y$(XILINX)/verilog/src/unimacro
# COMPILE_ARGS+= -y$(XILINX)/verilog/src/unisims
# COMPILE_ARGS+= -sv
COMPILE_ARGS+= -Wno-sensitivity-entire-vector
# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file:
TOPLEVEL=sim_top
# MODULE is the name of the Python test file:
MODULE=testCoordinateComputation,testBankRC,testAccumulatorBuffer,testAccumulatorBank,testAccumulatorBanks,testPPU,testFusionUnit,testCrossbar,testRamFIFO
# MODULE=testRamFIFO
MODULE=testBitfuscnn
# MODULE=testAccumulatorBanks

# SIM=verilator

# include ~/src/cocotb/cocotb/makefiles/Makefile.inc
# include ~/src/cocotb/cocotb/makefiles/Makefile.sim

include $(shell cocotb-config --makefile)/Makefile.sim
