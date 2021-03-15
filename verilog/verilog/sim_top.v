module sim_top #(parameter integer RAM_WIDTH = 10,
                 parameter integer BANK_COUNT = 32,
                 parameter integer TILE_SIZE = 256,
                 parameter integer INDEX_WIDTH = 4)( input wire clk
                                                   );

wire reset_n;
wire[1:0] bitwidth;
wire[2:0] kernel_size;

wire channel_group_done;

logic [24:0] oaram_value;
logic [INDEX_WIDTH-1:0] oaram_indices_value;
logic [RAM_WIDTH-1:1] oaram_address;
logic oaram_write_enable;

logic [$clog2(TILE_SIZE)-1:0] buffer_row_write[BANK_COUNT];
logic [$clog2(TILE_SIZE)-1:0] buffer_column_write[BANK_COUNT];
logic [7:0] buffer_data_write[BANK_COUNT];
reg buffer_write_enable[BANK_COUNT];

logic [$clog2(BANK_COUNT)-1:0] buffer_bank_read;
logic [$clog2(TILE_SIZE)-1:0] buffer_bank_row[BANK_COUNT];
logic [$clog2(TILE_SIZE)-1:0] buffer_bank_column[BANK_COUNT];
wire [7:0] buffer_data_read;

wire[7:0] neighbor_input_value[8];
wire[$clog2(TILE_SIZE)-1:0] neighbor_input_row[8];
wire[$clog2(TILE_SIZE)-1:0] neighbor_input_column[8];
wire neighbor_input_write_enable[8];

wire neighbor_exchange_done[8];
wire neighbor_cts[8];

logic cycle_done;

logic clear_to_send;
logic exchange_done;
logic[7:0] neighbor_output_value[8];
logic[$clog2(TILE_SIZE)-1:0] neighbor_output_row[8];
logic[$clog2(TILE_SIZE)-1:0] neighbor_output_column[8];
logic neighbor_output_write_enable[8];
ppu ppu( clk,
         reset_n,
         bitwidth,
         kernel_size,

         channel_group_done,

         oaram_value,
         oaram_indices_value,
         oaram_address,
         oaram_write_enable,

         buffer_row_write,
         buffer_column_write,
         buffer_data_write,
         buffer_write_enable,

         buffer_bank_read,
         buffer_bank_row,
         buffer_bank_column,
         buffer_data_read,

         neighbor_input_value,
         neighbor_input_row,
         neighbor_input_column,
         neighbor_input_write_enable,

         neighbor_exchange_done,
         neighbor_cts,

         cycle_done,

         clear_to_send,
         exchange_done,
         neighbor_output_value,
         neighbor_output_row,
         neighbor_output_column,
         neighbor_output_write_enable);

endmodule
