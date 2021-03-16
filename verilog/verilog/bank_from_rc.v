module bank_from_rc
       #(
         parameter integer BANK_COUNT = 32,
         parameter integer TILE_SIZE = 256
       ) (
         input logic [$clog2(TILE_SIZE)-1:0] row,
         input logic [$clog2(TILE_SIZE)-1:0] column,
         input logic unsigned [1:0] bitwidth,
         output logic [$clog2(BANK_COUNT)-1:0] bank,
         output logic [$clog2(TILE_SIZE)-1:0] entry
       );

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

assign bank = bank_from_rc(row, column);
assign entry = entry_from_rc(row, column);

endmodule
