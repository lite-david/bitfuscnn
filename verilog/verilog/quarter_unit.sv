module quarter_unit (
    clk,
    a[3:0],
    b[3:0],
    sa[1:0],
    sb[1:0],
    sft_ctrl_1,
    sft_ctrl_2,
    sft_ctrl_3[1:0],
    out[15:0]
);

input clk;
input [3:0] a;
input [3:0] b;
input [3:0] sa;
input [3:0] sb;
input sft_ctrl_1;
input sft_ctrl_2;
input [1:0] sft_ctrl_3;

output reg signed [15:0] out;

wire [3:0] out0, out1, out2, out3;
wire signed [7:0] out0_ext, out1_ext, out2_ext, out3_ext;
wire signed [15:0] sum;

bitbrick bb_0 (
    .clk(clk),
    .a[1:0](a[1:0]),
    .b[1:0](b[1:0]),
    .sa(sa[0]),
    .sb(sb[0]),
    .out[3:0](out0[3:0])
)

bitbrick bb_1 (
    .clk(clk),
    .a[1:0](a[3:2]),
    .b[1:0](b[1:0]),
    .sa(sa[1]),
    .sb(sb[0]),
    .out[3:0](out1[3:0])
)

bitbrick bb_2 (
    .clk(clk),
    .a[1:0](a[1:0]),
    .b[1:0](b[3:2]),
    .sa(sa[0]),
    .sb(sb[1]),
    .out[3:0](out2[3:0])
)

bitbrick bb_3 (
    .clk(clk),
    .a[1:0](a[3:2]),
    .b[1:0](b[3:2]),
    .sa(sa[1]),
    .sb(sb[1]),
    .out[3:0](out3[3:0])
)

case ({sft_ctrl_3[1:0],sft_ctrl_2,sft_ctrl_1})
    4'b1011: begin
        assign out0_ext = (sa[0]||sb[0]) ? {{4{out0[3]}},out0[3:0]} : {4'b0000,out0[3:0]};
        assign out1_ext = (sa[1]||sb[0]) ? {{2{out1[3]}},out1[3:0],2'b00} : {2'b00,out1[3:0],2'b00};
        assign out2_ext = (sa[1]||sb[0]) ? {{2{out2[3]}},out2[3:0],2'b00} : {2'b00,out2[3:0],2'b00};
        assign out3_ext = (sa[1]||sb[0]) ? {out3[3:0],4'b0000} : {out3[3:0],4'b0000};
        assign sum = out0_ext + out1_ext + out2_ext + out3_ext;
        assign out[15:0] = {8'b00000000,sum[7:0]};
    end
    4'b0110: begin
        assign out0_ext = (sa[1]||sb[0]) ? {{4{out0[3]}},out0[3:0]} : {4'b0000,out0[3:0]} ;
        assign out1_ext = (sa[1]||sb[0]) ? {{4{out1[3]}},out1[3:0]} : {4'b0000,out1[3:0]};
        assign out2_ext = (sa[1]||sb[0]) ? {{2{out2[3]}},out2[3:0],2'b00} : {2'b00,out2[3:0],2'b00};
        assign out3_ext = (sa[1]||sb[0]) ? {{2{out2[3]}},out3[3:0],2'b00} : {2'b00,out3[3:0],2'b00};
        assign sum[7:0] = out0_ext + out2_ext;
        assign sum[15:8] = out1_ext + out3_ext;
        assign out[15:0] = {2'b00,sum[13:8],2'b00,sum[5:0]};
    end
    4'b0101: begin
        assign out0_ext = (sa[1]||sb[0]) ? {{4{out0[3]}},out0[3:0]} : {4'b0000,out0[3:0]};
        assign out1_ext = (sa[1]||sb[0]) ? {{2{out1[3]}},out1[3:0],2'b00} : {2'b00,out1[3:0],2'b00};
        assign out2_ext = (sa[1]||sb[0]) ? {{4{out2[3]}},out2[3:0]} : {4'b0000,out2[3:0]};
        assign out3_ext = (sa[1]||sb[0]) ? {{2{out2[3]}},out3[3:0],2'b00} : {2'b00,out3[3:0],2'b00};
        assign sum[7:0] = out0_ext + out1_ext;
        assign sum[15:8] = out2_ext + out3_ext;
        assign out[15:0] = {2'b00,sum[13:8],2'b00,sum[5:0]};
    end
    4'b0000: begin
        assign out0_ext = (sa[1]||sb[0]) ? {{4{out0[3]}},out0[3:0]} : {4'b0000, out0[3:0]};
        assign out1_ext = (sa[1]||sb[0]) ? {{4{out1[3]}},out1[3:0]} : {4'b0000, out1[3:0]};
        assign out2_ext = (sa[1]||sb[0]) ? {{4{out2[3]}},out2[3:0]} : {4'b0000, out2[3:0]};
        assign out3_ext = (sa[1]||sb[0]) ? {{4{out2[3]}},out3[3:0]} : {4'b0000, out3[3:0]};
        assign sum[3:0] = out0_ext;
        assign sum[7:4] = out1_ext;
        assign sum[11:8] = out2_ext;
        assign sum[15:12] = out3_ext;
        assign out = sum;
    default: begin
        assign out = 16'b0;
    end
endcase

endmodule