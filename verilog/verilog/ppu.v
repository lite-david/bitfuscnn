import utils::*;

class RCConverter;
//   static function logic [$clog2(BANK_COUNT)-1:0] bank_from_rc(
//     input logic[$clog2(TILE_SIZE)-1:0] row,
//     logic[$clog2(TILE_SIZE)-1:0] column);
//   logic [$clog2(BANK_COUNT)-1:0] shift;
//   shift = (row * 3) % BANK_COUNT;
//   bank_from_rc = (column + shift) % BANK_COUNT;

// endfunction
endclass

module ppu
  #(parameter integer RAM_WIDTH = 10,
    parameter integer BANK_COUNT = 32,
    parameter integer TILE_SIZE = 256,
    parameter integer INDEX_WIDTH = 4)(
    input wire clk,
    input wire reset_n,
    input wire[1:0] bitwidth,
    input wire[2:0] kernel_size,

    input wire channel_group_done,

    output wire [24:0] oaram_value,
    output wire [INDEX_WIDTH-1:0] oaram_indices_value,
    output wire [RAM_WIDTH-1:1] oaram_address,
    output wire oaram_write_enable,

    output wire [$clog2(TILE_SIZE)-1:0] buffer_row_write[BANK_COUNT],
    output wire [$clog2(TILE_SIZE)-1:0] buffer_column_write[BANK_COUNT],
    output wire [7:0] buffer_data_write[BANK_COUNT],
    output wire buffer_write_enable[BANK_COUNT],

    output wire [$clog2(BANK_COUNT)-1:0] buffer_bank_read,
    output wire [$clog2(TILE_SIZE)-1:0] buffer_bank_entry,
    input wire [7:0] buffer_data_read,

    input wire[7:0] neighbor_input_value[8],
    input wire[$clog2(TILE_SIZE)-1:0] neighbor_input_row[8],
    input wire[$clog2(TILE_SIZE)-1:0] neighbor_input_column[8],
    input wire [7:0]neighbor_input_write_enable,

    input wire neighbor_exchange_done[8],
    input wire neighbor_cts[8],

    output logic cycle_done,

    output logic clear_to_send,
    output logic exchange_done,
    output logic[7:0] neighbor_output_value[8],
    output logic[$clog2(TILE_SIZE)-1:0] neighbor_output_row[8],
    output logic[$clog2(TILE_SIZE)-1:0] neighbor_output_column[8],
    output logic neighbor_output_write_enable[8]

  );

logic leftover_inputs;

neighbor_input_processor neighbor_input_processor(clk,
                         reset_n,
                         bitwidth,
                         neighbor_input_value,
                         neighbor_input_row,
                         neighbor_input_column,
                         neighbor_input_write_enable,
                         buffer_row_write,
                         buffer_column_write,
                         buffer_data_write,
                         buffer_write_enable,
                         leftover_inputs);

assign oaram_address = 0;
genvar i;
generate

  for(i = 0; i<8; i++) begin
    assign neighbor_output_write_enable[i] = 0;
  end

endgenerate

assign clear_to_send = !leftover_inputs;

assign buffer_bank_read = 0;
assign buffer_bank_entry = 0;


endmodule
