module bitfuscnn (
    input clk,
    input reset_n,
    input read_ram,
    input write_ram,
    input [1:0] mul_cfg,
    input act_sign_cfg,
    input weight_sign_cfg,
    input [3:0] weight_dim,
    input [8:0] activation_dim,
    inout [47:0] ram_data,
);

logic [7:0] weight_fifo[4], activation_fifo[4], mult_weight_pipe_in[4], mult_activation_pipe_in[4];
logic [63:0] mult_pipe_out_0[16], mult_pipe_out_1[16], mult_wire_out[16];
logic [15:0] weight_index_fifo[4], activation_index_fifo[4], weight_index_pipe_in[4], activation_index_pipe_in[4];
logic [3:0] weight_index_fifo_x[16], activation_index_fifo_x[16];
logic [15:0] row_coordinate[256], column_coordinate[256], row_coordinate_pipe_out[256], column_coordinate_pipe_out[256];

logic [2:0] count;
logic ram_read_done;

logic [7:0] front_buffer_row_write[256], front_buffer_column_write[256], front_buffer_data_write[256];
logic [7:0] front_buffer_row_write_pipe[256], front_buffer_column_write_pipe[256], front_buffer_data_write_pipe[256];
logic front_buffer_write_enable[256], front_buffer_write_enable_pipe[256];

logic cxb_stall;

integer i;

task reset();
    for(i = 0; i<4; i++) begin
        weight_fifo[i] <= 0;
        activation_fifo[i] <= 0;
        weight_index_fifo[i] <= 0;
        activation_index_fifo[i] <= 0;
        mult_weight_pipe_in[i] <= 0;
        mult_activation_pipe_in[i] <= 0;
        weight_index_pipe_in[i] <= 0;
        activation_index_pipe_in[i] <= 0;
    end
    count <= 0;
    ram_read_done <= 0;
    for(i = 0; i<16; i++) begin
        mult_pipe_out_0[i] <= 0;
        mult_pipe_out_1[i] <= 0;
    end
    for(i = 0; i<256; i++) begin
        row_coordinate_pipe_out[i] <= 0;
        column_coordinate_pipe_out[i] <= 0;
        front_buffer_row_write[i] <= 0;
        front_buffer_column_write[i] <= 0;
        front_buffer_data_write[i] <= 0;
        front_buffer_row_write_pipe[i] <= 0;
        front_buffer_column_write_pipe[i] <= 0;
        front_buffer_data_write_pipe[i] <= 0;
        front_buffer_write_enable[i] <= 0;
        front_buffer_write_enable_pipe[i] <= 0;
    end
endtask

task fifo_reset();
    for(i = 0; i<4; i++) begin
        weight_fifo[i] <= 0;
        activation_fifo[i] <= 0;
        weight_index_fifo[i] <= 0;
        activation_index_fifo[i] <= 0;
    end
    count <= 0;
    ram_read_done <= 0;
endtask

task mult_crdnt_inpipe_reset();
    fr(i = 0; i<4; i++) begin
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

always_ff@(posegde clk or negedge reset_n) begin //read input and weight from ram
    if(!reset_n) begin
        reset();
    end else begin
        if(read_ram) begin
            fifo_reset();
        end else if(count < 4) begin
            for(i=0;i<3;i++) begin
                weight_fifo[i+1] <= weight_fifo[i];
                activation_fifo[i+1] <= activation_fifo[i];
                weight_index_fifo[i+1] <= weight_index_fifo[i];
                activation_index_fifo[i+1] <= activation_index_fifo[i];
            end
            weight_fifo[0] <= ram_data[7:0];
            activation_fifo[0] <= ram_data[31:24];
            weight_index_fifo[0] <= ram_data[23:8];
            activation_index_fifo[0] <= ram_data[47:31];
            count <= count + 1;
            ram_read_done <= 0;
        end else begin
            count <= count;
            for(i=0;i<4;i++) begin
                weight_fifo[i] <= weight_fifo[i];
                activation_fifo[i] <= activation_fifo[i];
                weight_index_fifo[i] <= weight_index_fifo[i];
                activation_index_fifo[i] <= activation_index_fifo[i];
            end
            ram_read_done <= 1;
        end
    end
end

always_ff@(posegde clk or negedge reset_n) begin //multiplier and coordinate computation input pipeline
    if(!reset) begin
        reset();
    end else begin
        if(!ram_read_done || cxb_stall) begin
            mult_weight_pipe_in[i] <= mult_weight_pipe_in[i];
            mult_activation_pipe_in[i] <= mult_activation_pipe_in[i];
            weight_index_pipe_in[i] <= weight_index_pipe_in[i];
            activation_index_pipe_in[i] <= activation_index_pipe_in[i];
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
    for(x=0;x<16;x++) begin //multiplier array
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
end

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

always_ff@(posegde clk or negedge reset_n) begin //multiplier output pipeline 0
    if(!reset) begin
        reset();
    end else begin
        for(i=0;i<16;i++) begin
            mult_pipe_out_0[i] <= mult_wire_out[i];
        end
    end
end

always_ff@(posegde clk or negedge reset_n) begin //multiplier output pipeline 1 and coordinate computation pipeline 0
    if(!reset) begin
        reset();
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

always_ff@(posegde clk or negedge reset_n) begin //crossbar output pipeline
    if(!reset) begin
        reset();
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

accumulator_banks acc_bank (
    .clk(clk),
    .reset_n(reset_n),
    .transfer(),
    .bitwidth(mul_cfg),
    .front_buffer_row_write(front_buffer_row_write_pipe),
    .front_buffer_column_write(front_buffer_column_write_pipe),
    .front_buffer_data_write(front_buffer_data_write_pipe),
    .front_buffer_write_enable(front_buffer_write_enable_pipe),
    .back_buffer_row_write(),
    .back_buffer_column_write(),
    .back_buffer_data_write(),
    .back_buffer_write_enable(),
    .front_buffer_bank_entry(),
    .front_buffer_bank_read(),
    .front_buffer_data_read(),
    .back_buffer_bank_entry(),
    .back_buffer_bank_read(),
    .back_buffer_data_read()
)
