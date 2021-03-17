module accumulator_buffer #(
         parameter integer BUFFER_WIDTH = 8,
         parameter integer TILE_SIZE = 256,
         parameter integer SMALLEST_ELEMENT_WIDTH = 4
       ) (
         input wire clk,
         input wire reset_n,
         input wire transfer,
         input wire[1:0] bitwidth,

         input wire [$clog2(TILE_SIZE)-1:0] buffer_row_write,
         input wire [$clog2(TILE_SIZE)-1:0] buffer_column_write,
         input wire [SMALLEST_ELEMENT_WIDTH*4-1:0] buffer_data_write,
         input wire buffer_write_enable,

         input wire [$clog2(BUFFER_WIDTH)-1:0] buffer_bank_entry,
         output logic [SMALLEST_ELEMENT_WIDTH*4-1:0] buffer_data_read,

         input wire [BUFFER_WIDTH*SMALLEST_ELEMENT_WIDTH-1:0] data_in,
         output wire [BUFFER_WIDTH*SMALLEST_ELEMENT_WIDTH-1:0] data_out
       );

logic [BUFFER_WIDTH*SMALLEST_ELEMENT_WIDTH-1:0] data;
logic [SMALLEST_ELEMENT_WIDTH*4-1:0] data_accumulate;

assign data_out = data;

function logic unsigned [3:0] get_bitshift(
    input logic unsigned [1:0] bitwidth
  );

  case (bitwidth)
    0:
      get_bitshift = $clog2(SMALLEST_ELEMENT_WIDTH);
    1:
      get_bitshift = $clog2(2*SMALLEST_ELEMENT_WIDTH);
    2:
      get_bitshift = $clog2(4*SMALLEST_ELEMENT_WIDTH);
    default:
      get_bitshift = 1;
  endcase
endfunction

function logic [$clog2(TILE_SIZE)-1:0] entry_from_r(
    input logic[$clog2(TILE_SIZE)-1:0] row);
  entry_from_r = row >> bitwidth;

endfunction

function logic should_write(
    input logic[$clog2(BUFFER_WIDTH*SMALLEST_ELEMENT_WIDTH)-1:0] base,
    input logic[$clog2(BUFFER_WIDTH*SMALLEST_ELEMENT_WIDTH)-1:0] index);
  logic[$clog2(BUFFER_WIDTH*SMALLEST_ELEMENT_WIDTH):0] base_next;
  base_next = base + (1 << get_bitshift(bitwidth));
  should_write = index >= base && index < base_next && buffer_write_enable;

endfunction

function logic get_bit(
    input logic[$clog2(BUFFER_WIDTH*SMALLEST_ELEMENT_WIDTH)-1:0] index,
    input logic[$clog2(TILE_SIZE)-1:0] row
  );
  logic [$clog2(BUFFER_WIDTH)+1:0] base;
  base = entry_from_r(row);
  base = base << get_bitshift(bitwidth);
  get_bit = data[index];
  if(should_write(base, index)) begin
    get_bit = data_accumulate[index-base];
  end

endfunction

function logic [$clog2(BUFFER_WIDTH*SMALLEST_ELEMENT_WIDTH)-1:0] get_read_loc(
    input logic [$clog2(BUFFER_WIDTH)-1:0] buffer_bank_entry,
    input logic [$clog2(SMALLEST_ELEMENT_WIDTH*4)-1:0] index
  );
  get_read_loc = (buffer_bank_entry << get_bitshift(bitwidth)) + index;
endfunction

function logic is_valid(
    input logic [$clog2(SMALLEST_ELEMENT_WIDTH*4):0] index
  );
  is_valid = index < (1 << get_bitshift(bitwidth));
endfunction

task reset();
  data <= 0;
endtask

int bit_index;
task step();
  if(transfer) begin
    data <= data_in;
  end
  else begin
    for(bit_index = 0; bit_index < BUFFER_WIDTH*SMALLEST_ELEMENT_WIDTH; bit_index++) begin
      data[bit_index] <= get_bit(bit_index, buffer_row_write);
    end
  end

endtask

always @(posedge clk or negedge reset_n) begin
  if(!reset_n) begin
    reset();
  end
  else begin
    step();
  end
end

function logic overflow(
  input logic [SMALLEST_ELEMENT_WIDTH*4-1:0] a,
  input logic [SMALLEST_ELEMENT_WIDTH*4-1:0] b,
  input logic [1:0] bitwidth
);
logic [$clog2(BUFFER_WIDTH*SMALLEST_ELEMENT_WIDTH)-1:0] select;
logic [SMALLEST_ELEMENT_WIDTH*4:0] accumulator;
logic sign_bit;
logic a_sign_bit;
logic b_sign_bit;
logic overflow_bit;
select = 1 << get_bitshift(bitwidth);

accumulator = a + b;
overflow = 0;
sign_bit = accumulator[select-1];
overflow_bit = accumulator[select];
a_sign_bit = a[select-1];
b_sign_bit = b[select-1];
if(!a_sign_bit & !b_sign_bit & sign_bit) begin
  overflow = 1;
end
endfunction

function logic [SMALLEST_ELEMENT_WIDTH*4-1:0] safe_add(
  input logic [SMALLEST_ELEMENT_WIDTH*4-1:0] a,
  input logic [SMALLEST_ELEMENT_WIDTH*4-1:0] b,
  input logic [1:0] bitwidth
);
logic [$clog2(BUFFER_WIDTH*SMALLEST_ELEMENT_WIDTH)-1:0] select;
logic [SMALLEST_ELEMENT_WIDTH*4-1:0] a_inv;
logic [SMALLEST_ELEMENT_WIDTH*4-1:0] b_inv;
logic sign_bit;
logic a_sign_bit;
logic b_sign_bit;
logic overflow_bit;
select = 1 << get_bitshift(bitwidth);

safe_add = a + b;
a_inv = ~a + 1;
b_inv = ~b + 1;
if(overflow(a_inv, b_inv, bitwidth)) begin
  safe_add = (1 << select-1) + 1;
end
if(overflow(a, b, bitwidth)) begin
  safe_add = (1 << select-1) -1;
end
endfunction

int i;
always_comb begin : read_block
  buffer_data_read = 0;
  data_accumulate = 0;

  for(i = 0; i<SMALLEST_ELEMENT_WIDTH*4; i++) begin
    buffer_data_read[i] = data[get_read_loc(buffer_bank_entry,i)];
    buffer_data_read[i] = buffer_data_read[i] & is_valid(i);
    data_accumulate[i] = data[get_read_loc(entry_from_r(buffer_row_write),i)];
    data_accumulate[i] = data_accumulate[i] & is_valid(i);
  end

  data_accumulate = safe_add(data_accumulate, buffer_data_write, bitwidth);
end

// initial begin
//   $monitor("buffer_data_read = %x, buffer_row_write =%d, buffer_data_write=%x, data = %x", buffer_data_read, buffer_row_write, buffer_data_write, data);
// end

endmodule
