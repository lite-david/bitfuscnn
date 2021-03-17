module accumulator_banks #(
         parameter integer BUFFER_WIDTH = 8,
         parameter integer TILE_SIZE = 256,
         parameter integer SMALLEST_ELEMENT_WIDTH = 4,
         parameter integer BANK_COUNT = 256
       ) (
         input wire clk,
         input wire reset_n,
         input wire transfer,
         input wire[1:0] bitwidth,

         input wire [$clog2(TILE_SIZE)-1:0] front_buffer_row_write[BANK_COUNT],
         input wire [$clog2(TILE_SIZE)-1:0] front_buffer_column_write[BANK_COUNT],
         input wire [7:0] front_buffer_data_write[BANK_COUNT],
         input wire front_buffer_write_enable[BANK_COUNT],

         input wire [$clog2(TILE_SIZE)-1:0] back_buffer_row_write[BANK_COUNT],
         input wire [$clog2(TILE_SIZE)-1:0] back_buffer_column_write[BANK_COUNT],
         input wire [SMALLEST_ELEMENT_WIDTH*4-1:0] back_buffer_data_write[BANK_COUNT],
         input wire back_buffer_write_enable[BANK_COUNT],

         input wire [$clog2(BUFFER_WIDTH)-1:0] front_buffer_bank_entry,
         input wire [$clog2(TILE_SIZE)-1:0] front_buffer_bank_read,
         output logic [SMALLEST_ELEMENT_WIDTH*4-1:0] front_buffer_data_read,

         input wire [$clog2(BUFFER_WIDTH)-1:0] back_buffer_bank_entry,
         input wire [$clog2(TILE_SIZE)-1:0] back_buffer_bank_read,
         output logic [SMALLEST_ELEMENT_WIDTH*4-1:0] back_buffer_data_read
       );

wire [SMALLEST_ELEMENT_WIDTH*4-1:0] front_buffer_data_read_many[BANK_COUNT];
wire [SMALLEST_ELEMENT_WIDTH*4-1:0] back_buffer_data_read_many[BANK_COUNT];

assign front_buffer_data_read = front_buffer_data_read_many[front_buffer_bank_read];
assign back_buffer_data_read = back_buffer_data_read_many[back_buffer_bank_read];

genvar bank_index;
generate

  for(bank_index = 0; bank_index < BANK_COUNT; bank_index ++) begin : accumulator_banks
    accumulator_bank bank(
                       clk,
                       reset_n,
                       transfer,
                       bitwidth,

                       front_buffer_row_write[bank_index],
                       front_buffer_column_write[bank_index],
                       front_buffer_data_write[bank_index],
                       front_buffer_write_enable[bank_index],

                       front_buffer_bank_entry,
                       front_buffer_data_read_many[bank_index],

                       back_buffer_row_write[bank_index],
                       back_buffer_column_write[bank_index],
                       back_buffer_data_write[bank_index],
                       back_buffer_write_enable[bank_index],

                       back_buffer_bank_entry,
                       back_buffer_data_read_many[bank_index]
                     );
    defparam bank.BUFFER_WIDTH = BUFFER_WIDTH;
    defparam bank.TILE_SIZE = TILE_SIZE;
    defparam bank.SMALLEST_ELEMENT_WIDTH = SMALLEST_ELEMENT_WIDTH;
  end

endgenerate

endmodule
