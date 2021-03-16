module output_accumulator
       #(parameter integer RAM_WIDTH = 10,
         parameter integer BANK_COUNT = 32,
         parameter integer TILE_SIZE = 256,
         parameter integer INDEX_WIDTH = 4)(
         input wire clk,
         input wire reset_n,
         input wire[1:0] bitwidth,
         input wire[2:0] kernel_size,
         output logic [24:0] oaram_value,
         output logic [INDEX_WIDTH-1:0] oaram_indices_value,
         output logic [RAM_WIDTH-1:1] oaram_address,
         output logic oaram_write_enable,

         output logic [$clog2(BANK_COUNT)-1:0] buffer_bank_read,
         output logic [$clog2(TILE_SIZE)-1:0] buffer_bank_entry,
         input wire [7:0] buffer_data_read,

         input wire [7:0] neighbor_exchange_done,
         output logic done
       );

logic [$clog2(TILE_SIZE):0] row;
logic [$clog2(TILE_SIZE):0] column;
logic [RAM_WIDTH:1] length;

logic [$clog2(TILE_SIZE):0] next_row;
logic [$clog2(TILE_SIZE):0] next_column;
logic [RAM_WIDTH:1] next_length;

logic [24:0] next_oaram_value;
logic [INDEX_WIDTH-1:0] next_oaram_indices_value;
logic [RAM_WIDTH-1:1] next_oaram_address;
logic next_oaram_write_enable;

logic [$clog2(TILE_SIZE):0] true_tile_size;
assign true_tile_size = get_actual_tile_size(TILE_SIZE, bitwidth);

logic [7:0] relu_value;
logic [INDEX_WIDTH:0] zero_counter;
logic [INDEX_WIDTH:0] next_zero_counter;
integer max_zeros;
assign max_zeros = 2**INDEX_WIDTH - 1;

logic do_reset;

logic [$clog2(BANK_COUNT)-1:0] next_buffer_bank_read;
logic [$clog2(TILE_SIZE)-1:0] next_buffer_bank_entry;

task reset();
row <= 0;
column <= 0;
oaram_value <= 0;
oaram_indices_value <= 0;
oaram_address <= 0;
oaram_write_enable <= 0;
length <= 0;
buffer_bank_read <= 0;
buffer_bank_entry <= 0;
zero_counter <= 0;
endtask

task step();
oaram_value <= next_oaram_value;
oaram_indices_value <= next_oaram_indices_value;
oaram_address <= next_oaram_address;
oaram_write_enable <= next_oaram_write_enable;

row <= next_row;
column <= next_column;
length <= next_length;

buffer_bank_read <= next_buffer_bank_read;
buffer_bank_entry <= next_buffer_bank_entry;
zero_counter <= next_zero_counter;
endtask

always @(posedge clk or negedge reset_n) begin
  if(!reset_n) begin
    reset();
  end else begin
    if(do_reset) begin
      reset();
    end else begin
      step();  
    end
  end
end

function logic[$clog2(TILE_SIZE):0] get_actual_tile_size(
  input logic unsigned [$clog2(TILE_SIZE):0] tile_size,
  input logic unsigned [1:0] bitwidth
);
case (bitwidth)
  0: get_actual_tile_size = tile_size;
  1: get_actual_tile_size = tile_size >> 1;
  2: get_actual_tile_size = tile_size >> 3; 
  default: get_actual_tile_size = tile_size;
endcase
endfunction

function logic is_in_center(
    input logic unsigned [$clog2(TILE_SIZE)-1:0] row,
    input logic unsigned [$clog2(TILE_SIZE)-1:0] column
  );
  logic unsigned [3:0] halo_size;
  logic unsigned [$clog2(TILE_SIZE)-1:0] max_center;
  logic unsigned [$clog2(TILE_SIZE):0] actual_tile_size;
  actual_tile_size = get_actual_tile_size(TILE_SIZE, bitwidth);

  halo_size = (kernel_size - 1)/2;
  max_center = actual_tile_size - halo_size;

  if (row < halo_size && column < halo_size)
    return 0;
  if (row >= max_center && column >= max_center)
    return 0;
  if (row < halo_size && column >= max_center)
    return 0;
  if (row >= max_center && column < halo_size)
    return 0;

  if (row < halo_size)
    return 0;
  if (column < halo_size)
    return 0;

  if (row >= max_center)
    return 0;
  if (column >= max_center)
    return 0;


  return 1;
endfunction

function logic [7:0] relu(input logic [7:0] value);
logic [7:0] bit_index;
bit_index = (2 << bitwidth) - 1;
if(value[bit_index]) begin
  relu = 0;
end else begin
  relu = value;
end
endfunction

assign relu_value = relu(buffer_data_read);

function logic [$clog2(BANK_COUNT)-1:0] bank_from_rc(
    input logic[$clog2(TILE_SIZE)-1:0] row,
    input logic[$clog2(TILE_SIZE)-1:0] column);
  logic [$clog2(BANK_COUNT)-1:0] shift;
  logic [$clog2(TILE_SIZE)-1:0] row_upper;
  logic [$clog2(TILE_SIZE)-1:0] row_section;
  logic [$clog2(BANK_COUNT)-1:0] small_buffer_count;
  row_upper = row >> bitwidth;
  row_section = row % (1 << bitwidth);
  small_buffer_count = BANK_COUNT >> bitwidth;
  shift = (row_upper * 3) % BANK_COUNT;
  bank_from_rc = (column + shift + row_section * small_buffer_count) % BANK_COUNT;

endfunction

function logic [$clog2(TILE_SIZE)-1:0] entry_from_rc(
    input logic[$clog2(TILE_SIZE)-1:0] row,
    input logic[$clog2(TILE_SIZE)-1:0] column);
  entry_from_rc = row >> bitwidth;

endfunction

always_comb begin
  done = 0;
  next_oaram_write_enable = 0;
  next_oaram_indices_value = 0;
  next_oaram_address = 0;
  next_oaram_value = 0;
  do_reset = 0;
  next_zero_counter = zero_counter;
  next_column = column;
  next_row = row;
  next_length = length;
  if(!(&neighbor_exchange_done)) begin
    do_reset = 1;
  end
  if(row == true_tile_size) begin
    next_oaram_write_enable = 1;
    next_oaram_value = length;
    done = 1;
  end else begin
    if(is_in_center(row, column)) begin
      if(relu_value == 0 && zero_counter < max_zeros) begin
        next_zero_counter = zero_counter + 1;
      end else begin
        next_length = length + 1;
        next_oaram_write_enable = 1;
        next_oaram_indices_value = zero_counter;
        next_oaram_value = relu_value;
        next_zero_counter = 0;
        next_oaram_address = next_length;
      end
    end
    if(row != true_tile_size) begin
      next_column = column + 1;
      if(next_column == true_tile_size) begin
        next_column = 0;
        next_row = row + 1;
      end
    end
  end
  next_buffer_bank_read = bank_from_rc(next_row, next_column);
  next_buffer_bank_entry = entry_from_rc(next_row, next_column);
end

endmodule