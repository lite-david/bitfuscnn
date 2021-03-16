module rc_from_bank
       #(
         parameter integer BANK_COUNT = 32,
         parameter integer TILE_SIZE = 256
       ) (
         input logic [$clog2(BANK_COUNT)-1:0] bank,
         input logic [$clog2(TILE_SIZE)-1:0] entry,
         input logic [1:0] bitwidth,
         output logic [$clog2(TILE_SIZE)-1:0] row,
         output logic [$clog2(TILE_SIZE)-1:0] column
       );

function logic [$clog2(TILE_SIZE)-1:0] row_from_bank_entry(
    input logic[$clog2(BANK_COUNT)-1:0] bank,
    input logic[$clog2(TILE_SIZE)-1:0] entry);
  row_from_bank_entry = entry;

endfunction

function logic [$clog2(BANK_COUNT)-1:0] column_from_bank_entry(
    input logic[$clog2(BANK_COUNT)-1:0] bank,
    input logic[$clog2(TILE_SIZE)-1:0] entry);
  logic [$clog2(TILE_SIZE)-1:0] row;
  logic [$clog2(BANK_COUNT)-1:0] shift;
  row = row_from_bank_entry(bank, entry);
  shift = row * 3;
  shift = shift % BANK_COUNT;
  column_from_bank_entry = bank - shift;
  if(bank < shift) begin
    column_from_bank_entry = bank + BANK_COUNT - shift;
  end

endfunction

assign row = row_from_bank_entry(bank, entry);
assign column = column_from_bank_entry(bank, entry);

endmodule
