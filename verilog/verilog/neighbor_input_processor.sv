module neighbor_input_processor
       #(parameter integer BANK_COUNT = 32,
         parameter integer TILE_SIZE = 128)(
         input clk, reset_n,
         input wire[1:0] bitwidth,
         input wire[7:0] neighbor_input_value[8],
         input wire[$clog2(TILE_SIZE)-1:0] neighbor_input_row[8],
         input wire[$clog2(TILE_SIZE)-1:0] neighbor_input_column[8],
         input wire [7:0]neighbor_input_write_enable,

         output logic [$clog2(TILE_SIZE)-1:0] buffer_row_write[BANK_COUNT],
         output logic [$clog2(TILE_SIZE)-1:0] buffer_column_write[BANK_COUNT],
         output logic [7:0] buffer_data_write[BANK_COUNT],
         output logic buffer_write_enable[BANK_COUNT],
         output logic leftover_inputs
       );

logic[7:0] proc_neighbor_input_value[8];
logic[$clog2(TILE_SIZE)-1:0] proc_neighbor_input_row[8];
logic[$clog2(TILE_SIZE)-1:0] proc_neighbor_input_column[8];
logic [7:0]proc_neighbor_input_write_enable;

logic [7:0]next_neighbor_input_write_enable;

logic [$clog2(TILE_SIZE)-1:0] next_buffer_row_write[BANK_COUNT];
logic [$clog2(TILE_SIZE)-1:0] next_buffer_column_write[BANK_COUNT];
logic [7:0] next_buffer_data_write[BANK_COUNT];
logic next_buffer_write_enable[BANK_COUNT];

integer i;
task reset();

  for(i = 0; i<8; i++) begin
    proc_neighbor_input_value[i] <= 0;
    proc_neighbor_input_row [i] <= 0;
    proc_neighbor_input_column[i] <= 0;
    proc_neighbor_input_write_enable[i] <= 0;
  end

  for(i = 0; i<BANK_COUNT; i++) begin
    buffer_write_enable[i] <= 0;
  end

endtask

task process_neighbors();
  if(!leftover_inputs) begin
    for(i = 0; i<8; i++) begin
      proc_neighbor_input_value[i] <= neighbor_input_value[i];
      proc_neighbor_input_row[i] <= neighbor_input_row[i];
      proc_neighbor_input_column[i] <= neighbor_input_column[i];
    end
  end

  proc_neighbor_input_write_enable <= next_neighbor_input_write_enable;

  for(i = 0; i<BANK_COUNT; i++) begin
    buffer_write_enable[i] <= next_buffer_write_enable[i];
    buffer_row_write[i] <= next_buffer_row_write[i];
    buffer_column_write[i] <= next_buffer_column_write[i];
    buffer_data_write[i] <= next_buffer_data_write[i];
  end

endtask

always @(posedge clk or negedge reset_n) begin
  if(!reset_n) begin
    reset();
  end
  else begin
    process_neighbors();
  end
end

function logic [$clog2(BANK_COUNT)-1:0] bank_from_rc(
    input logic[$clog2(TILE_SIZE)-1:0] row,
    input logic[$clog2(TILE_SIZE)-1:0] column);
  logic [$clog2(BANK_COUNT)-1:0] shift;
  logic [$clog2(TILE_SIZE)-1:0] row_upper;
  logic [$clog2(TILE_SIZE)-1:0] row_section;
  logic [$clog2(BANK_COUNT)-1:0] small_buffer_count;
  row_upper = row >> bitwidth;
  row_section = row % (1 << bitwidth);
  small_buffer_count = BANK_COUNT >> bitwidth;
  shift = (row_upper * 3) % BANK_COUNT;
  bank_from_rc = (column + shift + row_section * small_buffer_count) % BANK_COUNT;

endfunction

logic[7:0] select_neighbor_input_value[8];
logic[$clog2(TILE_SIZE)-1:0] select_neighbor_input_row[8];
logic[$clog2(TILE_SIZE)-1:0] select_neighbor_input_column[8];
logic select_neighbor_input_write_enable[8];

logic [BANK_COUNT-1:0]used_banks;
logic [$clog2(BANK_COUNT)-1:0] bank;

always_comb begin
  next_neighbor_input_write_enable = proc_neighbor_input_write_enable;
  used_banks = 0;
  bank = 0;

  for(i = 0; i<BANK_COUNT; i++) begin
    next_buffer_write_enable[i] = 0;
    next_buffer_row_write[i] = 0;
    next_buffer_column_write[i] = 0;
    next_buffer_data_write[i] = 0;
  end

  for(i = 0; i<8; i++) begin
    select_neighbor_input_value[i] = neighbor_input_value[i];
    select_neighbor_input_row[i] = neighbor_input_row[i];
    select_neighbor_input_column[i] = neighbor_input_column[i];
    select_neighbor_input_write_enable[i] = neighbor_input_write_enable[i];
    if(leftover_inputs) begin
      select_neighbor_input_value[i] = proc_neighbor_input_value[i];
      select_neighbor_input_row[i] = proc_neighbor_input_row[i];
      select_neighbor_input_column[i] = proc_neighbor_input_column[i];
      select_neighbor_input_write_enable[i] = proc_neighbor_input_write_enable[i];
    end
  end

  for(i = 0; i<8; i++) begin
    if(select_neighbor_input_write_enable[i]) begin
      bank = bank_from_rc(select_neighbor_input_row[i], select_neighbor_input_column[i]);
      if(!used_banks[bank]) begin
        used_banks[bank] = 1;
        next_buffer_row_write[bank] = select_neighbor_input_row[i];
        next_buffer_column_write[bank] = select_neighbor_input_column[i];
        next_buffer_write_enable[bank] = 1;
        next_buffer_data_write[bank] = select_neighbor_input_value[i];
        next_neighbor_input_write_enable[i] = 0;
      end
      else begin
        next_neighbor_input_write_enable[i] = 1;
      end
    end
  end
end

assign leftover_inputs = |proc_neighbor_input_write_enable;

endmodule