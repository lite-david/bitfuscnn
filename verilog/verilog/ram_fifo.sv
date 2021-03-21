module ram_fifo #(
  parameter integer RAM_ADDRESS_WIDTH = 14,
  parameter integer RAM_VALUE_WIDTH = 24,
  parameter integer INDEX_WIDTH = 4,
  parameter integer OUTPUT_DIM = 4,
  parameter integer SMALLEST_ELEMENT_WIDTH = 2
) (
  input logic clk,
  input logic reset_n,
  input logic [1:0] bitwidth,
  
  input logic advance,

  input logic [RAM_VALUE_WIDTH-1:0] ram_value,
  input logic [INDEX_WIDTH-1:0] ram_indices_value,
  output wire [RAM_ADDRESS_WIDTH-1:0] ram_address,

  output logic [4*SMALLEST_ELEMENT_WIDTH-1:0] value_fifo_out[OUTPUT_DIM],
  output logic [INDEX_WIDTH-1:0] index_fifo_out[OUTPUT_DIM*4],

  output logic done,
  output logic data_ready
);

logic [RAM_ADDRESS_WIDTH-1:0] length;
logic [RAM_ADDRESS_WIDTH-1:0] read_location;
logic [$clog2(OUTPUT_DIM*4):0] values_read;

logic [4*SMALLEST_ELEMENT_WIDTH-1:0] build_value_fifo_out[OUTPUT_DIM];
logic [INDEX_WIDTH-1:0] build_index_fifo_out[OUTPUT_DIM*4];

logic [RAM_ADDRESS_WIDTH-1:0] next_length;
logic [RAM_ADDRESS_WIDTH-1:0] next_read_location;
logic [4*SMALLEST_ELEMENT_WIDTH-1:0] next_value_fifo_out;
logic [$clog2(OUTPUT_DIM)-1:0] next_value_fifo_out_index;
logic [INDEX_WIDTH-1:0] next_index_fifo_out;
logic [$clog2(OUTPUT_DIM*4)-1:0] next_index_fifo_out_index;
logic update_output_fifos;

logic [$clog2(OUTPUT_DIM*4):0] next_values_read;

assign ram_address = read_location;

int i;
task reset();
for(i = 0; i<OUTPUT_DIM; i++) begin
  value_fifo_out[i] <= 0;
  build_value_fifo_out[i] <= 0;
end
for(i = 0; i<OUTPUT_DIM*4; i++) begin
  index_fifo_out[i] <= 0;
  build_index_fifo_out[i] <= 0;
end

length <= 1;
read_location <= 0;
values_read <= 0;
endtask

task step();
length <= next_length;
read_location <= next_read_location;
values_read <= next_values_read;
for(i = 0; i<OUTPUT_DIM; i++) begin
  if(next_value_fifo_out_index == i && update_output_fifos) begin
    build_value_fifo_out[i] <= next_value_fifo_out;
    $display("build_value_fifo_out[%1d] = %d", i, next_value_fifo_out);
  end
end

for(i = 0; i<OUTPUT_DIM*4; i++) begin
  if(next_index_fifo_out_index == i && update_output_fifos) begin
    build_index_fifo_out[i] <= next_index_fifo_out;
  end
end

if(advance && data_ready) begin
  $display("advancing");
  for(i = 0; i<OUTPUT_DIM; i++) begin
    value_fifo_out[i] <= build_value_fifo_out[i];
  end

  for(i = 0; i<OUTPUT_DIM*4; i++) begin
    index_fifo_out[i] <= build_index_fifo_out[i];
  end
end
endtask

always @(posedge clk or negedge reset_n) begin
  if(!reset_n) begin
    reset();
  end else begin
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
  data_ready = 0;
  update_output_fifos = 0;
  next_value_fifo_out_index = 0;
  next_index_fifo_out_index = 0;
  next_value_fifo_out = 0;
  next_index_fifo_out = 0;
  next_read_location = read_location;
  next_values_read = values_read;

  if(read_location == 0) begin
    next_length = ram_value;
  end

  if(read_location > next_length) begin
    done = 1;
  end

  if(values_read == values_for_bitwidth()) begin
    data_ready = 1;
    if(advance) begin
      next_values_read = 0;
      $display("next_values_read = 0");
    end
  end

  if(read_location <= length && read_location != 0) begin
    update_output_fifos = next_values_read < values_for_bitwidth();
    next_value_fifo_out_index = next_values_read;
    next_index_fifo_out_index = next_values_read;
    next_value_fifo_out = ram_value;
    next_index_fifo_out = ram_indices_value;
  end

  if(should_advance(next_values_read)) begin
    next_read_location = read_location + 1;
    if(read_location > 0 && !advance) begin
      next_values_read = values_read + 1;
      $display("next_values_read = %d", next_values_read);
    end
  end
end

initial begin
  $monitor("done = %d, read_location = %d, length = %d, next_value_fifo_out %d, values_read=%d", done, read_location, length, next_value_fifo_out, values_read);
end
  
endmodule