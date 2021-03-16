module bank_from_rc
       #(
         parameter integer BANK_COUNT = 32,
         parameter integer TILE_SIZE = 256
       ) (
         input logic [$clog2(TILE_SIZE)-1:0] row,
         input logic [$clog2(TILE_SIZE)-1:0] column,
         input logic [1:0] bitwidth,
         output logic [$clog2(BANK_COUNT)-1:0] bank,
         output logic [$clog2(TILE_SIZE)-1:0] entry
       );

function logic [$clog2(BANK_COUNT)-1:0] bank_from_rc(
    input logic[$clog2(TILE_SIZE)-1:0] row,
    input logic[$clog2(TILE_SIZE)-1:0] column);
  logic [$clog2(BANK_COUNT)-1:0] shift;
  shift = (row * 3) % BANK_COUNT;
  bank_from_rc = (column + shift) % BANK_COUNT;

endfunction

function logic [$clog2(TILE_SIZE)-1:0] entry_from_rc(
    input logic[$clog2(TILE_SIZE)-1:0] row,
    input logic[$clog2(TILE_SIZE)-1:0] column);
  entry_from_rc = row;

endfunction

assign bank = bank_from_rc(row, column);
assign entry = entry_from_rc(row, column);

endmodule
