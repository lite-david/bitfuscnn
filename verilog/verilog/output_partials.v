module output_partials #(
         parameter integer BANK_COUNT = 32,
         parameter integer TILE_SIZE = 128
       ) (
         input wire clk,
         input wire reset_n,
         input wire[1:0] bitwidth,
         input wire[2:0] kernel_size,
         input wire channel_group_done,
         input wire neighbor_cts[8],
         output logic [$clog2(BANK_COUNT)-1:0] buffer_bank_read,
         output logic [$clog2(TILE_SIZE)-1:0] buffer_bank_entry,
         input wire [7:0] buffer_data_read,

         output logic exchange_done,
         output logic[7:0] neighbor_output_value[8],
         output logic[$clog2(TILE_SIZE)-1:0] neighbor_output_row[8],
         output logic[$clog2(TILE_SIZE)-1:0] neighbor_output_column[8],
         output logic neighbor_output_write_enable[8]
       );
typedef enum logic[3:0] {
          TOP_LEFT,
          TOP,
          TOP_RIGHT,
          LEFT,
          RIGHT,
          BOTTOM_LEFT,
          BOTTOM,
          BOTTOM_RIGHT,
          NONE
        } Neighbor;

logic [$clog2(TILE_SIZE)-1:0] row;
logic [$clog2(TILE_SIZE)-1:0] column;
logic process_outputs;

logic [$clog2(TILE_SIZE)-1:0] next_row;
logic [$clog2(TILE_SIZE)-1:0] next_column;
logic next_process_outputs;
logic next_exchange_done;

logic[7:0] next_neighbor_output_value[8];
logic[$clog2(TILE_SIZE)-1:0] next_neighbor_output_row[8];
logic[$clog2(TILE_SIZE)-1:0] next_neighbor_output_column[8];
logic next_neighbor_output_write_enable[8];

int i;
task reset;
  row <= 0;
  column <= 0;
  process_outputs <= 0;
  exchange_done <= 0;

  for(i = 0; i<8; i++) begin
    neighbor_output_value[i] <= 0;
    neighbor_output_row[i] <= 0;
    neighbor_output_column[i] <= 0;
    neighbor_output_write_enable[i] <= 0;
  end

endtask

task update;
  row <= next_row;
  column <= next_column;
  process_outputs <= next_process_outputs;
  exchange_done <= next_exchange_done;
  for(i = 0; i<8; i++) begin
    neighbor_output_value[i] <= next_neighbor_output_value[i];
    neighbor_output_row[i] <= next_neighbor_output_row[i];
    neighbor_output_column[i] <= next_neighbor_output_column[i];
    neighbor_output_write_enable[i] <= next_neighbor_output_write_enable[i];
  end

endtask

always @(posedge clk or negedge reset_n) begin
  if(!reset_n) begin
    reset();
  end
  else begin
    update();
  end
end

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

function advance(
    input logic [$clog2(TILE_SIZE)-1:0] row,
    input logic [$clog2(TILE_SIZE)-1:0] column
  );
  logic unsigned [$clog2(TILE_SIZE):0] next_row_big;
  logic unsigned [$clog2(TILE_SIZE):0] next_column_big;
  logic unsigned [$clog2(TILE_SIZE):0] actual_tile_size;
  actual_tile_size = TILE_SIZE >> bitwidth;

  next_row_big = row + 1;
  next_row = next_row_big[$clog2(TILE_SIZE)-1:0];
  if(next_row_big == actual_tile_size) begin
    next_row = 0;
    next_column_big = column + 1;
    next_column = next_column_big[$clog2(TILE_SIZE)-1:0];

    if(next_column_big == actual_tile_size) begin
      next_column = 0;
      next_exchange_done = 1;
    end
  end

endfunction

function Neighbor neighbor_from_rc(
    input logic unsigned [$clog2(TILE_SIZE)-1:0] row,
    input logic unsigned [$clog2(TILE_SIZE)-1:0] column
  );
  logic unsigned [3:0] halo_size;
  logic unsigned [$clog2(TILE_SIZE)-1:0] max_center;
  logic unsigned [$clog2(TILE_SIZE):0] actual_tile_size;
  actual_tile_size = TILE_SIZE >> bitwidth;

  halo_size = (kernel_size - 1)/2;
  max_center = actual_tile_size - halo_size;

  if (row < halo_size && column < halo_size)
    return TOP_LEFT;
  if (row >= max_center && column >= max_center)
    return BOTTOM_RIGHT;
  if (row < halo_size && column >= max_center)
    return TOP_RIGHT;
  if (row >= max_center && column < halo_size)
    return BOTTOM_LEFT;

  if (row < halo_size)
    return TOP;
  if (column < halo_size)
    return LEFT;

  if (row >= max_center)
    return BOTTOM;
  if (column >= max_center)
    return RIGHT;

  return NONE;
endfunction

function logic [$clog2(TILE_SIZE)-1:0] get_neighbor_r(
    input logic [$clog2(TILE_SIZE)-1:0] row,
    input logic [$clog2(TILE_SIZE)-1:0] column,
    Neighbor neighbor
  );
  logic unsigned [3:0] halo_size;
  logic unsigned [$clog2(TILE_SIZE)-1:0] row_top;
  logic unsigned [$clog2(TILE_SIZE)-1:0] row_bottom;
  logic unsigned [$clog2(TILE_SIZE)-1:0] column_left;
  logic unsigned [$clog2(TILE_SIZE)-1:0] column_right;
  logic unsigned [$clog2(TILE_SIZE):0] actual_tile_size;
  actual_tile_size = TILE_SIZE >> bitwidth;

  halo_size = (kernel_size - 1)/2;
  row_top = actual_tile_size - row - 2 * halo_size;
  row_bottom = row - actual_tile_size + 2 * halo_size;
  column_left = actual_tile_size - column - 2 * halo_size;
  column_right = column - actual_tile_size + 2 * halo_size;

  get_neighbor_r = row;
  if (neighbor == TOP_LEFT)
    get_neighbor_r = row_top;

  if (neighbor == TOP)
    get_neighbor_r = row_top;

  if (neighbor == TOP_RIGHT)
    get_neighbor_r = row_top;

  if (neighbor == LEFT)
    get_neighbor_r = row;

  if (neighbor == RIGHT)
    get_neighbor_r = row;

  if (neighbor == BOTTOM_LEFT)
    get_neighbor_r = row_bottom;

  if (neighbor == BOTTOM)
    get_neighbor_r = row_bottom;

  if (neighbor == BOTTOM_RIGHT)
    get_neighbor_r = row_bottom;
endfunction

function logic [$clog2(TILE_SIZE)-1:0] get_neighbor_c(
    input logic [$clog2(TILE_SIZE)-1:0] row,
    input logic [$clog2(TILE_SIZE)-1:0] column,
    Neighbor neighbor
  );
  logic unsigned [3:0] halo_size;
  logic unsigned [$clog2(TILE_SIZE)-1:0] row_top;
  logic unsigned [$clog2(TILE_SIZE)-1:0] row_bottom;
  logic unsigned [$clog2(TILE_SIZE)-1:0] column_left;
  logic unsigned [$clog2(TILE_SIZE)-1:0] column_right;
  logic unsigned [$clog2(TILE_SIZE):0] actual_tile_size;
  actual_tile_size = TILE_SIZE >> bitwidth;

  halo_size = (kernel_size - 1)/2;
  row_top = actual_tile_size - row - 2 * halo_size;
  row_bottom = row - actual_tile_size + 2 * halo_size;
  column_left = actual_tile_size - column - 2 * halo_size;
  column_right = column - actual_tile_size + 2 * halo_size;

  get_neighbor_c = column;
  if (neighbor == TOP_LEFT)
    get_neighbor_c = column_left;

  if (neighbor == TOP)
    get_neighbor_c = column;

  if (neighbor == TOP_RIGHT)
    get_neighbor_c = column_right;

  if (neighbor == LEFT)
    get_neighbor_c = column_left;

  if (neighbor == RIGHT)
    get_neighbor_c = column_right;

  if (neighbor == BOTTOM_LEFT)
    get_neighbor_c = column_left;

  if (neighbor == BOTTOM)
    get_neighbor_c = column;

  if (neighbor == BOTTOM_RIGHT)
    get_neighbor_c = column_right;

endfunction

genvar k;
generate
  for(k = 0; k<8; k++) begin
    assign next_neighbor_output_value[k] = buffer_data_read;
  end

endgenerate

Neighbor neighbor;
always_comb begin
  for(i = 0; i<8; i++) begin
    next_neighbor_output_row[i] = 0;
    next_neighbor_output_column[i] = 0;
    next_neighbor_output_write_enable[i] = 0;
  end

  next_process_outputs = process_outputs;
  next_row = 0;
  next_column = 0;
  buffer_bank_read = 0;
  buffer_bank_entry = 0;

  if(!process_outputs && channel_group_done) begin
    next_process_outputs = 1;
    next_exchange_done = 0;
  end

  if(!(exchange_done || !next_process_outputs)) begin
    buffer_bank_read = bank_from_rc(row, column);
    buffer_bank_entry = entry_from_rc(row, column);

    if(buffer_data_read == 0) begin
      advance(row, column);
    end
    else begin

      neighbor = neighbor_from_rc(row, column);

      if(neighbor == NONE) begin
        advance(row, column);
      end
      else if(neighbor_cts[neighbor]) begin
        advance(row, column);
        next_neighbor_output_row[neighbor] = get_neighbor_r(row, column, neighbor);
        next_neighbor_output_column[neighbor] = get_neighbor_c(row, column, neighbor);
        next_neighbor_output_write_enable[neighbor] = 1;
      end
    end
  end
end

endmodule
