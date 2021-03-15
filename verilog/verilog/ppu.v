module ppu
       #(parameter integer RAM_WIDTH = 10,
         parameter integer BANK_COUNT = 32,
         parameter integer TILE_SIZE = 32,
         parameter integer INDEX_WIDTH = 4)(
         input wire clk,
         input wire reset_n,
         input wire[3:0] bitwidth,
         input wire[2:0] kernel_size,

         input wire channel_group_done,

         output logic [24:0] oaram_value,
         output logic [INDEX_WIDTH-1:0] oaram_indices_value,
         output logic [RAM_WIDTH-1:1] oaram_address,
         output logic oaram_write_enable,

         output logic [$clog2(TILE_SIZE)-1:0] buffer_row_write[BANK_COUNT],
         output logic [$clog2(TILE_SIZE)-1:0] buffer_column_write[BANK_COUNT],
         output logic [7:0] buffer_data_write[BANK_COUNT],
         output logic buffer_write_enable[BANK_COUNT],

         output logic [$clog2(BANK_COUNT)-1:0] buffer_bank_read,
         input wire [7:0] buffer_data_read,

         input wire[7:0] neighbor_input_value[8],
         input wire[$clog2(TILE_SIZE)-1:0] neighbor_input_row[8],
         input wire[$clog2(TILE_SIZE)-1:0] neighbor_input_column[8],
         input wire neighbor_input_write_enable[8],

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

assign oaram_address = 0;
genvar i;
generate

  for(i = 0; i<BANK_COUNT; i++) begin
    assign buffer_write_enable[i] = 0;
  end

  for(i = 0; i<8; i++) begin
    assign neighbor_output_write_enable[i] = 0;
  end

endgenerate

assign clear_to_send = 1;

endmodule
