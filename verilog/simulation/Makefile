BITFUSCNN=$(PWD)/../verilog
BITFUSCNN_SRC= $(BITFUSCNN)/bank_from_rc.sv $(BITFUSCNN)/rc_from_bank.sv
BITFUSCNN_SRC+= $(BITFUSCNN)/top.sv $(BITFUSCNN)/sim_top.sv $(BITFUSCNN)/ppu.sv $(BITFUSCNN)/coordinatecomputation.sv
BITFUSCNN_SRC+= $(BITFUSCNN)/neighbor_input_processor.sv  $(BITFUSCNN)/output_partials.sv 
BITFUSCNN_SRC+= $(BITFUSCNN)/output_accumulator.sv $(BITFUSCNN)/accumulator_buffer.sv
# GPS_SRC+= $(GPS)/FULL_ADDER.v $(GPS)/LOGGER.v $(GPS)/SAMPLER.v
VERILOG_SOURCES = $(BITFUSCNN_SRC)
# VERILOG_SOURCES+= $(XILINX)/verilog/src/glbl.v
# COMPILE_ARGS+= -y$(XILINX)/verilog/src/simprims
# COMPILE_ARGS+= -y$(XILINX)/verilog/src/unimacro
# COMPILE_ARGS+= -y$(XILINX)/verilog/src/unisims
# COMPILE_ARGS+= -sv
# COMPILE_ARGS+= -Wno-fatal
# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file:
TOPLEVEL=sim_top
# MODULE is the name of the Python test file:
MODULE=testBitfuscnn,testCoordinateComputation,testBankRC,testAccumulatorBank,testPPU

# SIM=verilator

# include ~/src/cocotb/cocotb/makefiles/Makefile.inc
# include ~/src/cocotb/cocotb/makefiles/Makefile.sim

include $(shell cocotb-config --makefile)/Makefile.sim
