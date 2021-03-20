module ppu
  #(parameter integer RAM_WIDTH = 14,
    parameter integer BANK_COUNT = 256,
    parameter integer TILE_SIZE = 256,
    parameter integer BUFFER_WIDTH = 256,
    parameter integer INDEX_WIDTH = 4,
    parameter integer DATA_WIDTH = 16)(
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
    output wire [DATA_WIDTH-1:0] buffer_data_write[BANK_COUNT],
    output wire buffer_write_enable[BANK_COUNT],

    output logic [$clog2(BANK_COUNT)-1:0] buffer_bank_read,
    output logic [$clog2(BUFFER_WIDTH)-1:0] buffer_bank_entry,
    input wire [DATA_WIDTH-1:0] buffer_data_read,

    input wire[DATA_WIDTH-1:0] neighbor_input_value[8],
    input wire[$clog2(TILE_SIZE)-1:0] neighbor_input_row[8],
    input wire[$clog2(TILE_SIZE)-1:0] neighbor_input_column[8],
    input wire [7:0]neighbor_input_write_enable,

    input wire [7:0]neighbor_exchange_done,
    input wire neighbor_cts[8],

    output wire cycle_done,

    output wire clear_to_send,
    output wire exchange_done,
    output wire[DATA_WIDTH-1:0] neighbor_output_value[8],
    output wire[$clog2(TILE_SIZE)-1:0] neighbor_output_row[8],
    output wire[$clog2(TILE_SIZE)-1:0] neighbor_output_column[8],
    output wire neighbor_output_write_enable[8]

  );

logic leftover_inputs;

logic [$clog2(BANK_COUNT)-1:0] partial_buffer_bank_read;
logic [$clog2(TILE_SIZE)-1:0] partial_buffer_bank_entry;

logic [$clog2(BANK_COUNT)-1:0] accumulator_buffer_bank_read;
logic [$clog2(TILE_SIZE)-1:0] accumulator_buffer_bank_entry;

always_comb begin
  buffer_bank_read = partial_buffer_bank_read;
  buffer_bank_entry = partial_buffer_bank_entry;

  if(&neighbor_exchange_done) begin
    buffer_bank_read = accumulator_buffer_bank_read;
    buffer_bank_entry = accumulator_buffer_bank_entry;
  end
end

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

defparam neighbor_input_processor.TILE_SIZE=TILE_SIZE;
defparam neighbor_input_processor.BANK_COUNT=BANK_COUNT;
defparam neighbor_input_processor.DATA_WIDTH=DATA_WIDTH;

output_partials output_partials(clk,
                                reset_n,
                                bitwidth,
                                kernel_size,
                                channel_group_done,
                                neighbor_cts,
                                partial_buffer_bank_read,
                                partial_buffer_bank_entry,
                                buffer_data_read,

                                exchange_done,
                                neighbor_output_value,
                                neighbor_output_row,
                                neighbor_output_column,
                                neighbor_output_write_enable);

defparam output_partials.TILE_SIZE=TILE_SIZE;
defparam output_partials.BANK_COUNT=BANK_COUNT;
defparam output_partials.DATA_WIDTH=DATA_WIDTH;

output_accumulator output_accumulator(
                     clk,
                     reset_n,
                     bitwidth,
                     kernel_size,
                     oaram_value,
                     oaram_indices_value,
                     oaram_address,
                     oaram_write_enable,

                     accumulator_buffer_bank_read,
                     accumulator_buffer_bank_entry,
                     buffer_data_read,

                     neighbor_exchange_done,
                     cycle_done
                   );

defparam output_accumulator.TILE_SIZE=TILE_SIZE;
defparam output_accumulator.BANK_COUNT=BANK_COUNT;
defparam output_accumulator.RAM_WIDTH = RAM_WIDTH;
defparam output_accumulator.DATA_WIDTH=DATA_WIDTH;

assign clear_to_send = !leftover_inputs;

endmodule
