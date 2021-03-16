module ppu
  #(parameter integer RAM_WIDTH = 10,
    parameter integer BANK_COUNT = 32,
    parameter integer TILE_SIZE = 128,
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

    output wire cycle_done,

    output wire clear_to_send,
    output wire exchange_done,
    output wire[7:0] neighbor_output_value[8],
    output wire[$clog2(TILE_SIZE)-1:0] neighbor_output_row[8],
    output wire[$clog2(TILE_SIZE)-1:0] neighbor_output_column[8],
    output wire neighbor_output_write_enable[8]

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

output_partials output_partials(clk,
                                reset_n,
                                bitwidth,
                                kernel_size,
                                channel_group_done,
                                neighbor_cts,
                                buffer_bank_read,
                                buffer_bank_entry,
                                buffer_data_read,

                                exchange_done,
                                neighbor_output_value,
                                neighbor_output_row,
                                neighbor_output_column,
                                neighbor_output_write_enable);

assign oaram_address = 0;

assign clear_to_send = !leftover_inputs;

endmodule
