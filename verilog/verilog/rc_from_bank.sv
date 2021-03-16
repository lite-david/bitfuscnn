module rc_from_bank
       #(
         parameter integer BANK_COUNT = 32,
         parameter integer TILE_SIZE = 256
       ) (
         input logic [$clog2(BANK_COUNT)-1:0] bank,
         input logic [$clog2(TILE_SIZE)-1:0] entry,
         input logic unsigned [1:0] bitwidth,
         output logic [$clog2(TILE_SIZE)-1:0] row,
         output logic [$clog2(TILE_SIZE)-1:0] column
       );

function logic [$clog2(TILE_SIZE)-1:0] row_from_bank_entry(
    input logic[$clog2(BANK_COUNT)-1:0] bank,
    input logic[$clog2(TILE_SIZE)-1:0] entry);
  logic [$clog2(BANK_COUNT)-1:0] shift;
  logic [$clog2(TILE_SIZE)-1:0] row_msb;
  logic [1:0] row_lsb;
  logic [$clog2(BANK_COUNT):0] small_buffer_count;
  logic [$clog2(TILE_SIZE)-1:0] column;
  small_buffer_count = BANK_COUNT >> bitwidth;
  row_msb = entry << bitwidth;
  shift = (entry * 3) % BANK_COUNT;
  column = bank - shift;
  if(bank < shift) begin
    column = bank + BANK_COUNT - shift;
  end
  row_lsb = column >> ($clog2(BANK_COUNT) - bitwidth);
  column = column % small_buffer_count;
  row_from_bank_entry = row_msb | row_lsb;

endfunction

function logic [$clog2(BANK_COUNT)-1:0] column_from_bank_entry(
    input logic[$clog2(BANK_COUNT)-1:0] bank,
    input logic[$clog2(TILE_SIZE)-1:0] entry);
  logic [$clog2(BANK_COUNT)-1:0] shift;
  logic [$clog2(TILE_SIZE)-1:0] row_msb;
  logic [1:0] row_lsb;
  logic [$clog2(BANK_COUNT):0] small_buffer_count;
  logic [$clog2(TILE_SIZE)-1:0] column;
  small_buffer_count = BANK_COUNT >> bitwidth;
  row_msb = entry << bitwidth;
  shift = (entry * 3) % BANK_COUNT;
  column = bank - shift;
  if(bank < shift) begin
    column = bank + BANK_COUNT - shift;
  end
  column_from_bank_entry = column % small_buffer_count;

endfunction

assign row = row_from_bank_entry(bank, entry);
assign column = column_from_bank_entry(bank, entry);

endmodule
