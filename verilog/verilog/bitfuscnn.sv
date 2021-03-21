module bitfuscnn
  #(parameter integer RAM_WIDTH = 14,
    parameter integer BANK_COUNT = 64,
    parameter integer TILE_SIZE = 256,
    parameter integer BUFFER_WIDTH = TILE_SIZE*TILE_SIZE/BANK_COUNT,
    parameter integer INDEX_WIDTH = 4,
    parameter integer DATA_WIDTH = 16) (
    input clk,
    input reset_n,
    input read_ram,
    input write_ram,
    input [1:0] mul_cfg,
    input act_sign_cfg,
    input weight_sign_cfg,
    input [3:0] weight_dim,
    input [3:0] weight_count,
    input [7:0] activation_count,
    input [8:0] activation_dim,
    inout [47:0] ram_data,
    output [24:0] oaram_value,
    output [INDEX_WIDTH-1:0] oaram_indices_value,
    output [RAM_WIDTH-1:1] oaram_address,
    output oaram_write_enable,
    input wire[DATA_WIDTH-1:0] neighbor_input_value[8],
    input wire[$clog2(TILE_SIZE)-1:0] neighbor_input_row[8],
    input wire[$clog2(TILE_SIZE)-1:0] neighbor_input_column[8],
    input wire [7:0]neighbor_input_write_enable,

    output weight_done,
    output activation_done,

    input wire [7:0]neighbor_exchange_done,
    input wire neighbor_cts[8],

    input transfer,

    output wire clear_to_send,
    output wire exchange_done,
    output wire[DATA_WIDTH-1:0] neighbor_output_value[8],
    output wire[$clog2(TILE_SIZE)-1:0] neighbor_output_row[8],
    output wire[$clog2(TILE_SIZE)-1:0] neighbor_output_column[8],
    output wire neighbor_output_write_enable[8],

    output wire ppu_done
);

logic [7:0] weight_fifo[4], activation_fifo[4], mult_weight_pipe_in[4], mult_activation_pipe_in[4];
logic [63:0] mult_pipe_out_0[16], mult_pipe_out_1[16], mult_wire_out[16];
logic [15:0] weight_index_fifo[4], activation_index_fifo[4], weight_index_pipe_in[4], activation_index_pipe_in[4];
logic [3:0] weight_index_fifo_x[16], activation_index_fifo_x[16];
logic [$clog2(TILE_SIZE)-1:0] row_coordinate[256], column_coordinate[256], row_coordinate_pipe_out[256], column_coordinate_pipe_out[256];

logic [2:0] count;
logic ram_read_done;

logic [7:0] front_buffer_row_write[BANK_COUNT], front_buffer_column_write[BANK_COUNT], front_buffer_data_write[BANK_COUNT];
logic [7:0] front_buffer_row_write_pipe[BANK_COUNT], front_buffer_column_write_pipe[BANK_COUNT], front_buffer_data_write_pipe[BANK_COUNT];
logic front_buffer_write_enable[BANK_COUNT], front_buffer_write_enable_pipe[BANK_COUNT];

logic cxb_stall;

logic transfer_1;

logic [$clog2(TILE_SIZE)-1:0] back_buffer_row_write[BANK_COUNT];
logic [$clog2(TILE_SIZE)-1:0] back_buffer_column_write[BANK_COUNT];
logic [DATA_WIDTH-1:0] back_buffer_data_write[BANK_COUNT];
logic back_buffer_write_enable[BANK_COUNT];

logic [$clog2(BANK_COUNT)-1:0] back_buffer_bank_read;
logic [$clog2(BUFFER_WIDTH)-1:0] back_buffer_bank_entry;
logic [15:0] back_buffer_data_read;

logic [4:0] weight_counter;
logic [7:0] activation_counter;

integer i;

task reset();
    for(i = 0; i<4; i++) begin
        // weight_fifo[i] <= 0;
        // activation_fifo[i] <= 0;
        // weight_index_fifo[i] <= 0;
        // activation_index_fifo[i] <= 0;
        // mult_weight_pipe_in[i] <= 0;
        // mult_activation_pipe_in[i] <= 0;
        // weight_index_pipe_in[i] <= 0;
        // activation_index_pipe_in[i] <= 0;
    end
    // count <= 0;
    // ram_read_done <= 0;
    // transfer_1 <= 0;
    
    // activation_counter <= 0;
    for(i = 0; i<16; i++) begin
        // mult_pipe_out_0[i] <= 0;
        // mult_pipe_out_1[i] <= 0;
    end
    for(i = 0; i<256; i++) begin
        // row_coordinate_pipe_out[i] <= 0;
        // column_coordinate_pipe_out[i] <= 0;
        // front_buffer_row_write[i] <= 0;
        // front_buffer_column_write[i] <= 0;
        // front_buffer_data_write[i] <= 0;
        // front_buffer_row_write_pipe[i] <= 0;
        // front_buffer_column_write_pipe[i] <= 0;
        // front_buffer_data_write_pipe[i] <= 0;
        // front_buffer_write_enable[i] <= 0;
        // front_buffer_write_enable_pipe[i] <= 0;
    end
endtask

// task fifo_reset_weight();
//     for(i = 0; i<4; i++) begin
//         weight_fifo[i] <= 0;
//         weight_index_fifo[i] <= 0;
//     end
//     count <= 0;
//     ram_read_done <= 0;
//     weight_counter <= 0;
// endtask

// task fifo_reset_activation();
//     for(i = 0; i<4; i++) begin
//         activation_fifo[i] <= 0;
//         activation_index_fifo[i] <= 0;
//     end
//     activation_counter <= 0;
// endtask

// task weight_advance();
//     for(i=0;i<3;i++) begin
//         weight_fifo[i+1] <= weight_fifo[i];
//         weight_index_fifo[i+1] <= weight_index_fifo[i];
//     end
//     weight_fifo[0] <= ram_data[7:0];
//     weight_index_fifo[0] <= ram_data[23:8];
// endtask

// task activation_advance();
//     for(i=0;i<3;i++) begin
//         activation_fifo[i+1] <= activation_fifo[i];
//         activation_index_fifo[i+1] <= activation_index_fifo[i];
//     end
//     activation_fifo[0] <= ram_data[31:24];
//     activation_index_fifo[0] <= ram_data[47:31];
// endtask

task mult_crdnt_inpipe_reset();
    for(i = 0; i<4; i++) begin
        mult_weight_pipe_in[i] <= 0;
        weight_index_pipe_in[i] <= 0;
        mult_activation_pipe_in[i] <= 0;
        activation_index_pipe_in[i] <= 0;
    end
endtask

task mult_crdnt_outpipe_reset();
    for(i = 0; i<16; i++) begin
        mult_pipe_out_0[i] <= 0;
        mult_pipe_out_1[i] <= 0;
    end
    for(i = 0; i<256; i++) begin
        row_coordinate_pipe_out[i] <= 0;
        column_coordinate_pipe_out[i] <= 0;
    end
endtask

// always_ff@(posedge clk or negedge reset_n) begin
//     if(!reset_n) begin
//         // reset();
        
//     end else begin
//         weight_counter <= weight_counter + 1;
//     end
// end

always_ff@(posedge clk or negedge reset_n) begin //read weight from ram
    if(!reset_n) begin
        // reset();
        for(i = 0; i<4; i++) begin
            weight_fifo[i] <= 0;
            weight_index_fifo[i] <= 0;
        end
        weight_counter <= 0;
        count <= 0;
        ram_read_done <= 0;
        weight_counter <= 0;
    end else begin
        if(cxb_stall) begin
            for(i = 0; i<4; i++) begin
                weight_fifo[i] <= 0;
                weight_index_fifo[i] <= 0;
            end
            count <= 0;
            ram_read_done <= 0;
            weight_counter <= 0;
        end else if(count < 4) begin
            for(i=0;i<3;i++) begin
                weight_fifo[i+1] <= weight_fifo[i];
                weight_index_fifo[i+1] <= weight_index_fifo[i];
            end
            weight_fifo[0] <= ram_data[7:0];
            weight_index_fifo[0] <= ram_data[23:8];
            count <= count + 1;
            ram_read_done <= 0;
        end else begin
            count <= count;
            for(i=0;i<4;i++) begin
                weight_fifo[i] <= weight_fifo[i];
                weight_index_fifo[i] <= weight_index_fifo[i];
            end
            ram_read_done <= 1;
            weight_counter <= weight_counter + 4;
        end
    end
end

assign weight_done = (weight_counter >= weight_count) ? 1 : 0;
assign activation_done = (activation_counter >= activation_count) ? 1 : 0;

always_ff@(posedge clk or negedge reset_n) begin //read input from ram
    if(!reset_n) begin
        for(i = 0; i<4; i++) begin
            activation_fifo[i] <= 0;
            activation_index_fifo[i] <= 0;
        end
        activation_counter <= 0;
    end else begin
        if(weight_done) begin
            for(i = 0; i<4; i++) begin
                activation_fifo[i] <= 0;
                activation_index_fifo[i] <= 0;
            end
            activation_counter <= 0;
        end else if(count < 4) begin
            for(i=0;i<3;i++) begin
                activation_fifo[i+1] <= activation_fifo[i];
                activation_index_fifo[i+1] <= activation_index_fifo[i];
            end
            activation_fifo[0] <= ram_data[31:24];
            activation_index_fifo[0] <= ram_data[47:31];
        end else begin
            for(i=0;i<4;i++) begin
                activation_fifo[i] <= activation_fifo[i];
                activation_index_fifo[i] <= activation_index_fifo[i];
            end
            activation_counter <= activation_counter + 4;
        end
    end
end

always_ff@(posedge clk or negedge reset_n) begin //multiplier and coordinate computation input pipeline
    if(!reset_n) begin
        // reset();
        for(i = 0; i<4; i++) begin
            mult_weight_pipe_in[i] <= 0;
            mult_activation_pipe_in[i] <= 0;
            weight_index_pipe_in[i] <= 0;
            activation_index_pipe_in[i] <= 0;
        end
    end else begin
        if(!ram_read_done || cxb_stall) begin
            for(i=0;i<4;i++) begin
                mult_weight_pipe_in[i] <= mult_weight_pipe_in[i];
                mult_activation_pipe_in[i] <= mult_activation_pipe_in[i];
                weight_index_pipe_in[i] <= weight_index_pipe_in[i];
                activation_index_pipe_in[i] <= activation_index_pipe_in[i];
            end
        end else begin
            for(i=0;i<4;i++) begin
                mult_weight_pipe_in[i] <= weight_fifo[i];
                mult_activation_pipe_in[i] <= activation_fifo[i];
                weight_index_pipe_in[i] <= weight_index_fifo[i];
                activation_index_pipe_in[i] <= activation_index_fifo[i];
            end
        end
    end
end

genvar x;

generate
    for(x=0;x<16;x++) begin : multiplier
        fusion_unit fu_0 (
            .a(mult_weight_pipe_in[x%4]),
            .b(mult_activation_pipe_in[(x+x/4)%4]),
            .sa(weight_sign_cfg),
            .sb(act_sign_cfg),
            .cfga(mul_cfg),
            .cfgb(mul_cfg),
            .out(mult_wire_out[x])
        );
    end
endgenerate

always_comb begin
    for(i=0;i<4;i++) begin
        weight_index_fifo_x[4*i] = weight_index_pipe_in[i][3:0];
        weight_index_fifo_x[4*i+1] = weight_index_pipe_in[i][7:4];
        weight_index_fifo_x[4*i+2] = weight_index_pipe_in[i][11:8];
        weight_index_fifo_x[4*i+3] = weight_index_pipe_in[i][15:12];
        activation_index_fifo_x[4*i] = activation_index_pipe_in[i][3:0];
        activation_index_fifo_x[4*i+1] = activation_index_pipe_in[i][7:4];
        activation_index_fifo_x[4*i+2] = activation_index_pipe_in[i][11:8];
        activation_index_fifo_x[4*i+3] = activation_index_pipe_in[i][15:12];
    end
end

coordinatecomputation cc_0 ( //coordinate computation unit
    .clk(clk),
    .reset_n(reset_n),
    .bitwidth(mul_cfg),
    .weight_indices(weight_index_fifo_x),
    .activation_indices(activation_index_fifo_x),
    .weight_dim(weight_dim),
    .activation_dim(activation_dim),
    .row_coordinate(row_coordinate),
    .column_coordinate(column_coordinate)
);

always_ff@(posedge clk or negedge reset_n) begin //multiplier output pipeline 0
    if(!reset_n) begin
        // reset();
        for(i = 0; i<16; i++) begin
            mult_pipe_out_0[i] <= 0;
        end
    end else begin
        for(i=0;i<16;i++) begin
            mult_pipe_out_0[i] <= mult_wire_out[i];
        end
    end
end

always_ff@(posedge clk or negedge reset_n) begin //multiplier output pipeline 1 and coordinate computation pipeline 0
    if(!reset_n) begin
        // reset();
        for(i = 0; i<16; i++) begin
            // mult_pipe_out_0[i] <= 0;
            mult_pipe_out_1[i] <= 0;
        end
        for(i = 0; i<256; i++) begin
            row_coordinate_pipe_out[i] <= 0;
            column_coordinate_pipe_out[i] <= 0;
        end
    end else begin
        if(cxb_stall) begin
            for(i=0;i<16;i++) begin
                mult_pipe_out_1[i] <= mult_pipe_out_1[i];
            end
            for(i=0;i<256;i++) begin
                row_coordinate_pipe_out[i] <= row_coordinate_pipe_out[i];
                column_coordinate_pipe_out[i] <= column_coordinate_pipe_out[i];
            end
        end else begin
            for(i=0;i<16;i++) begin
                mult_pipe_out_1[i] <= mult_pipe_out_0[i];
            end
            for(i=0;i<256;i++) begin
                row_coordinate_pipe_out[i] <= row_coordinate[i];
                column_coordinate_pipe_out[i] <= column_coordinate[i];
            end
        end
    end
end

 crossbar cxb (
     .clk(clk),
     .reset_n(reset_n),
     .bitwidth(mul_cfg),
     //Input from multiplier array
     .products(mult_pipe_out_1),
     //Inputs from coordinate computation
     .row_coordinate(row_coordinate_pipe_out),
     .column_coordinate(column_coordinate_pipe_out),
     //Buffer bank interface
     .buffer_row_write(front_buffer_row_write),
     .buffer_column_write(front_buffer_column_write),
     .buffer_data_write(front_buffer_data_write),
     .buffer_write_enable(front_buffer_write_enable),
     //cross bar stall signal
     .crossbar_stall(cxb_stall)
 );

 defparam cxb.BANK_COUNT = BANK_COUNT;

always_ff@(posedge clk or negedge reset_n) begin //crossbar output pipeline
    if(!reset_n) begin
        // reset();
        for(i = 0; i<BANK_COUNT; i++) begin
            front_buffer_row_write_pipe[i] <= 0;
            front_buffer_column_write_pipe[i] <= 0;
            front_buffer_data_write_pipe[i] <= 0;
            front_buffer_write_enable_pipe[i] <= 0;
        end
    end else begin
        if(!cxb_stall) begin
            for(i=0;i<16;i++) begin
                front_buffer_row_write_pipe[i] <= front_buffer_row_write_pipe[i];
                front_buffer_column_write_pipe[i] <= front_buffer_column_write_pipe[i];
                front_buffer_data_write_pipe[i] <= front_buffer_data_write_pipe[i];
                front_buffer_write_enable_pipe[i] <= front_buffer_write_enable_pipe[i];
            end
        end else begin
            for(i=0;i<16;i++) begin
                front_buffer_row_write_pipe[i] <= front_buffer_row_write[i];
                front_buffer_column_write_pipe[i] <= front_buffer_column_write[i];
                front_buffer_data_write_pipe[i] <= front_buffer_data_write[i];
                front_buffer_write_enable_pipe[i] <= front_buffer_write_enable[i];
            end
        end
    end
end

wire [4*4-1:0] front_buffer_data_read;
wire [$clog2(BUFFER_WIDTH)-1:0] zero_buffer_width = 0;
wire [$clog2(TILE_SIZE)-1:0] zero_tile_size = 0;
wire [$clog2(TILE_SIZE)-1:0] back_buffer_bank_read_padded = back_buffer_bank_read;

accumulator_banks acc_bank (
    .clk(clk),
    .reset_n(reset_n),
    .transfer(transfer),
    .bitwidth(mul_cfg),
    .front_buffer_row_write(front_buffer_row_write_pipe),
    .front_buffer_column_write(front_buffer_column_write_pipe),
    .front_buffer_data_write(front_buffer_data_write_pipe),
    .front_buffer_write_enable(front_buffer_write_enable_pipe),
    .back_buffer_row_write(back_buffer_row_write),
    .back_buffer_column_write(back_buffer_column_write),
    .back_buffer_data_write(back_buffer_data_write),
    .back_buffer_write_enable(back_buffer_write_enable),
    .front_buffer_bank_entry(zero_buffer_width),
    .front_buffer_bank_read(zero_tile_size),
    .front_buffer_data_read(front_buffer_data_read),
    .back_buffer_bank_entry(back_buffer_bank_entry),
    .back_buffer_bank_read(back_buffer_bank_read_padded),
    .back_buffer_data_read(back_buffer_data_read)
);

defparam acc_bank.BUFFER_WIDTH = BUFFER_WIDTH;
defparam acc_bank.BANK_COUNT = BANK_COUNT;

always_ff@(posedge clk or negedge reset_n) begin
    if(!reset_n) begin
        // reset();
        transfer_1 <= 0;
    end else begin
        transfer_1 <= transfer;
    end
end

ppu ppu (
    .clk(clk),
    .reset_n(reset_n),
    .bitwidth(mul_cfg),
    .kernel_size(weight_dim[2:0]),
    .channel_group_done(transfer_1),
    .oaram_value(oaram_value),
    .oaram_indices_value(oaram_indices_value),
    .oaram_address(oaram_address),
    .oaram_write_enable(oaram_write_enable),
    .buffer_row_write(back_buffer_row_write),
    .buffer_column_write(back_buffer_column_write),
    .buffer_data_write(back_buffer_data_write),
    .buffer_write_enable(back_buffer_write_enable),
    .buffer_bank_read(back_buffer_bank_read),
    .buffer_bank_entry(back_buffer_bank_entry),
    .buffer_data_read(back_buffer_data_read),
    .neighbor_input_value(neighbor_input_value),
    .neighbor_input_row(neighbor_input_row),
    .neighbor_input_column(neighbor_input_column),
    .neighbor_input_write_enable(neighbor_input_write_enable),
    .neighbor_exchange_done(neighbor_exchange_done),
    .neighbor_cts(neighbor_cts),
    .cycle_done(ppu_done),
    .clear_to_send(clear_to_send),
    .exchange_done(exchange_done),
    .neighbor_output_value(neighbor_output_value),
    .neighbor_output_row(neighbor_output_row),
    .neighbor_output_column(neighbor_output_column),
    .neighbor_output_write_enable(neighbor_output_write_enable)
);

defparam ppu.BUFFER_WIDTH = BUFFER_WIDTH;
defparam ppu.BANK_COUNT = BANK_COUNT;
defparam ppu.DATA_WIDTH = DATA_WIDTH;

endmodule
