module accumulator_bank #(
         parameter integer BUFFER_WIDTH = 8,
         parameter integer TILE_SIZE = 256,
         parameter integer SMALLEST_ELEMENT_WIDTH = 4
       ) (
         input wire clk,
         input wire reset_n,
         input wire transfer,
         input wire[1:0] bitwidth,

         input wire [$clog2(TILE_SIZE)-1:0] front_buffer_row_write,
         input wire [$clog2(TILE_SIZE)-1:0] front_buffer_column_write,
         input wire [7:0] front_buffer_data_write,
         input wire front_buffer_write_enable,

         input wire [$clog2(BUFFER_WIDTH)-1:0] front_buffer_bank_entry,
         output wire [SMALLEST_ELEMENT_WIDTH*4-1:0] front_buffer_data_read,

         input wire [$clog2(TILE_SIZE)-1:0] back_buffer_row_write,
         input wire [$clog2(TILE_SIZE)-1:0] back_buffer_column_write,
         input wire [SMALLEST_ELEMENT_WIDTH*4-1:0] back_buffer_data_write,
         input wire back_buffer_write_enable,

         input wire [$clog2(BUFFER_WIDTH)-1:0] back_buffer_bank_entry,
         output wire [SMALLEST_ELEMENT_WIDTH*4-1:0] back_buffer_data_read

       );

wire [BUFFER_WIDTH*SMALLEST_ELEMENT_WIDTH-1:0] data_transfer;
wire [BUFFER_WIDTH*SMALLEST_ELEMENT_WIDTH-1:0] data_out;

logic [SMALLEST_ELEMENT_WIDTH*4-1:0] front_buffer_data_write_padded;

function logic [SMALLEST_ELEMENT_WIDTH*4-1:0] sign_extend_2(
  input logic [7:0] value
);
sign_extend_2 = $signed(value[1]);
sign_extend_2[1:0] = value[1:0];
endfunction

function logic [SMALLEST_ELEMENT_WIDTH*4-1:0] sign_extend_4(
  input logic [7:0] value
);
sign_extend_4 = $signed(value[3]);
sign_extend_4[3:0] = value[3:0];
endfunction

function logic [SMALLEST_ELEMENT_WIDTH*4-1:0] sign_extend_8(
  input logic [7:0] value
);
sign_extend_8 = $signed(value[7]);
sign_extend_8[7:0] = value[7:0];
endfunction

function logic [SMALLEST_ELEMENT_WIDTH*4-1:0] sign_extend(
  input logic [7:0] value,
  input logic [1:0] bitwidth
);
case (bitwidth)
  0 : sign_extend = sign_extend_2(value);
  1 : sign_extend = sign_extend_4(value);
  2 : sign_extend = sign_extend_8(value);
  default: sign_extend = sign_extend_2(value);
endcase
endfunction

always_comb begin
  front_buffer_data_write_padded = sign_extend(front_buffer_data_write, bitwidth);
end

accumulator_buffer front_buffer(
  clk,
  reset_n,
  transfer,
  bitwidth,
  front_buffer_row_write,
  front_buffer_column_write,
  front_buffer_data_write_padded,
  front_buffer_write_enable,
  front_buffer_bank_entry,
  front_buffer_data_read,
  0,
  data_transfer
);

defparam front_buffer.BUFFER_WIDTH = BUFFER_WIDTH;
defparam front_buffer.TILE_SIZE = TILE_SIZE;
defparam front_buffer.SMALLEST_ELEMENT_WIDTH = SMALLEST_ELEMENT_WIDTH;

accumulator_buffer back_buffer(
  clk,
  reset_n,
  transfer,
  bitwidth,
  back_buffer_row_write,
  back_buffer_column_write,
  back_buffer_data_write,
  back_buffer_write_enable,
  back_buffer_bank_entry,
  back_buffer_data_read,
  data_transfer,
  data_out
);

defparam back_buffer.BUFFER_WIDTH = BUFFER_WIDTH;
defparam back_buffer.TILE_SIZE = TILE_SIZE;
defparam back_buffer.SMALLEST_ELEMENT_WIDTH = SMALLEST_ELEMENT_WIDTH;

initial begin
  // $monitor("data_transfer = %x, buffer_write_enable = %x, buffer_row_write =%d, buffer_data_write=%x, data = %x", data_transfer, back_buffer.buffer_write_enable, back_buffer.buffer_row_write, back_buffer.buffer_data_write, back_buffer.data);
  // $monitor("front_buffer_data_write_padded = %x", front_buffer_data_write_padded);
end


endmodule