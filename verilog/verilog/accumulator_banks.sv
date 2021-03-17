module accumulator_banks #(
  parameter integer BUFFER_WIDTH = 8,
  parameter integer TILE_SIZE = 256,
  parameter integer SMALLEST_ELEMENT_WIDTH = 4,
  parameter integer BANK_COUNT = 256
) (
  input wire clk,
  input wire reset_n,
  input wire transfer,
  input wire[1:0] bitwidth,

  input wire [$clog2(TILE_SIZE)-1:0] front_buffer_row_write[BANK_COUNT],
  input wire [$clog2(TILE_SIZE)-1:0] front_buffer_column_write[BANK_COUNT],
  input wire [7:0] front_buffer_data_write[BANK_COUNT],
  input wire front_buffer_write_enable[BANK_COUNT],

  input wire [$clog2(TILE_SIZE)-1:0] back_buffer_row_write[BANK_COUNT],
  input wire [$clog2(TILE_SIZE)-1:0] back_buffer_column_write[BANK_COUNT],
  input wire [7:0] back_buffer_data_write[BANK_COUNT],
  input wire back_buffer_write_enable[BANK_COUNT],

  input wire [$clog2(BUFFER_WIDTH)-1:0] front_buffer_bank_entry,
  input wire [$clog2(TILE_SIZE)-1:0] front_buffer_bank_read,
  output wire [SMALLEST_ELEMENT_WIDTH*4-1:0] front_buffer_data_read,

  input wire [$clog2(BUFFER_WIDTH)-1:0] back_buffer_bank_entry,
  input wire [$clog2(TILE_SIZE)-1:0] back_bbuffer_bank_read,
  output wire [SMALLEST_ELEMENT_WIDTH*4-1:0] back_buffer_data_read
);
  
endmodule