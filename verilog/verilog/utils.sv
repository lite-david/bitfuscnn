module bank_from_rcc #(
  parameter integer BANK_COUNT = 32,
  parameter integer TILE_SIZE = 256
) (
  input logic [$clog2(TILE_SIZE)-1:0] row,
  input logic [$clog2(TILE_SIZE)-1:0] column,
  input logic [1:0] bitwidth,
  output logic [$clog2(BANK_COUNT)-1:0] bank
);
  
endmodule