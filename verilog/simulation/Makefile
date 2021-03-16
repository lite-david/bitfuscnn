BITFUSCNN=$(PWD)/../verilog
BITFUSCNN_SRC=$(BITFUSCNN)/sim_top.v $(BITFUSCNN)/ppu.v $(BITFUSCNN)/coordinatecomputation.v $(BITFUSCNN)/fusion_unit.sv $(BITFUSCNN)/quarter_unit.sv $(BITFUSCNN)/bitbrick.sv
# GPS_SRC+= $(GPS)/FULL_ADDER.v $(GPS)/LOGGER.v $(GPS)/SAMPLER.v
VERILOG_SOURCES = $(BITFUSCNN_SRC)
# VERILOG_SOURCES+= $(XILINX)/verilog/src/glbl.v
# COMPILE_ARGS+= -y$(XILINX)/verilog/src/simprims
# COMPILE_ARGS+= -y$(XILINX)/verilog/src/unimacro
# COMPILE_ARGS+= -y$(XILINX)/verilog/src/unisims
# COMPILE_ARGS+= -s glbl
# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file:
TOPLEVEL=sim_top
# MODULE is the name of the Python test file:
MODULE=testBitfuscnn,testPPU,testCoordinateComputation,testFusionUnit

# include ~/src/cocotb/cocotb/makefiles/Makefile.inc
# include ~/src/cocotb/cocotb/makefiles/Makefile.sim

include $(shell cocotb-config --makefile)/Makefile.sim
