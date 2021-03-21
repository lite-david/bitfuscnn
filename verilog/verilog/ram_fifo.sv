module ram_fifo #(
         parameter integer RAM_ADDRESS_WIDTH = 14,
         parameter integer RAM_PARALLEL = 16,
         parameter integer INDEX_WIDTH = 4,
         parameter integer OUTPUT_DIM = 4,
         parameter integer SMALLEST_ELEMENT_WIDTH = 2
       ) (
         input logic clk,
         input logic reset_n,
         input logic [1:0] bitwidth,

         input logic advance,

         input logic [RAM_PARALLEL*SMALLEST_ELEMENT_WIDTH-1:0] ram_value,
         input logic [RAM_PARALLEL*INDEX_WIDTH-1:0] ram_indices_value,
         output logic [RAM_ADDRESS_WIDTH-1:0] ram_address,

         output logic [4*SMALLEST_ELEMENT_WIDTH-1:0] value_fifo_out[OUTPUT_DIM],
         output logic [INDEX_WIDTH-1:0] index_fifo_out[OUTPUT_DIM*4],

         output logic done,
         output logic stall
       );

logic [RAM_ADDRESS_WIDTH-1:0] length;
logic [RAM_ADDRESS_WIDTH-1:0] read_location;

logic [RAM_ADDRESS_WIDTH-1:0] next_length;
logic [RAM_ADDRESS_WIDTH-1:0] next_read_location;
logic [4*SMALLEST_ELEMENT_WIDTH-1:0] next_value_fifo_out[OUTPUT_DIM];
logic [INDEX_WIDTH-1:0] next_index_fifo_out[OUTPUT_DIM*4];
logic update_output_fifos;

assign stall = read_location == 0;

int i;
task reset();

  for(i = 0; i<OUTPUT_DIM; i++) begin
    value_fifo_out[i] <= 0;
  end

  for(i = 0; i<OUTPUT_DIM*4; i++) begin
    index_fifo_out[i] <= 0;
  end

  length <= 1;
  read_location <= 0;

endtask

task step();
  length <= next_length;
  read_location <= next_read_location;
  for(i = 0; i<OUTPUT_DIM; i++) begin
    if(advance) begin
      value_fifo_out[i] <= next_value_fifo_out[i];
    end
  end

  for(i = 0; i<OUTPUT_DIM*4; i++) begin
    if(advance) begin
      index_fifo_out[i] <= next_index_fifo_out[i];
    end
  end

endtask

always @(posedge clk or negedge reset_n) begin
  if(!reset_n) begin
    reset();
  end
  else begin
    step();
  end
end

function logic [$clog2(OUTPUT_DIM*4):0] values_for_bitwidth();
  values_for_bitwidth = 4;

  if(bitwidth == 1) begin
    values_for_bitwidth = 8;
  end

  if(bitwidth == 0) begin
    values_for_bitwidth = 16;
  end

endfunction

function logic should_advance(
    input logic [$clog2(OUTPUT_DIM*4):0] values_count
  );
  should_advance = read_location <= next_length;
  should_advance = should_advance && values_count < values_for_bitwidth();
endfunction

always_comb begin
  next_length = length;
  done = 0;
  update_output_fifos = 0;
  next_read_location = read_location;
  ram_address = read_location;

  for(i = 0; i<OUTPUT_DIM; i++) begin
    next_value_fifo_out[i] = 0;
  end

  for(i = 0; i<OUTPUT_DIM*4; i++) begin
    next_index_fifo_out[i] = 0;
  end

  if(read_location == 0) begin
    next_length = ((ram_value - 1) >> (4-bitwidth)) + 1;

    if(ram_value == 0) begin
      next_length = 0;
    end
  end

  if(read_location > next_length) begin
    ram_address = 1;
    done = 1;
  end

  if(read_location <= length && read_location != 0 || advance) begin
    for(i = 0; i<RAM_PARALLEL*SMALLEST_ELEMENT_WIDTH; i++) begin
      next_value_fifo_out[i/(4*SMALLEST_ELEMENT_WIDTH)][i%(4*SMALLEST_ELEMENT_WIDTH)] = ram_value[i];
    end

    for(i = 0; i<RAM_PARALLEL*INDEX_WIDTH; i++) begin
      next_index_fifo_out[i/(RAM_PARALLEL*INDEX_WIDTH/OUTPUT_DIM/4)][i%(RAM_PARALLEL*INDEX_WIDTH/OUTPUT_DIM/4)] = ram_indices_value[i];
    end
  end

  if(advance || read_location == 0) begin
    next_read_location = read_location + 1;
    if(read_location > next_length) begin
      next_read_location = 2;
    end
  end
end

endmodule
