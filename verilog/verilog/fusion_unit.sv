module fusion_unit (
    clk,
    a[7:0],
    b[7:0],
    sa,
    sb,
    cfga[1:0],
    cfgb[1:0],
    out[63:0]
);

input clk;
input [7:0] a;
input [7:0] b;
input sa;
input sb;
input [1:0] cfga;
input [1:0] cfgb;

output  [63:0] out;

wire [15:0] out0, out1, out2, out3;
wire signed [15:0] out0_ext, out1_ext, out2_ext, out3_ext, out0_a_ext, out1_a_ext, out2_a_ext, out3_a_ext;
wire signed [63:0] sum;
wire sa_0, sa_1, sa_2, sa_3;
wire sb_0, sb_1, sb_2, sb_3;
wire sft_ctrl_0_1, sft_ctrl_0_2;
wire [1:0] sft_ctrl_0_3;

quarter_unit qu_0 (
    .clk(clk),
    .a[3:0](a[3:0]),
    .b[3:0](b[3:0]),
    .sa[1:0]({sa_1,sa_0}),
    .sb[1:0]({sb_1,sb_0}),
    .sft_ctrl_1(sft_ctrl_0_1),
    .sft_ctrl_2(sft_ctrl_0_2),
    .sft_ctrl_3[1:0](sft_ctrl_0_3[1:0]),
    .out[15:0](out0[15:0])
);

quarter_unit qu_1 (
    .clk(clk),
    .a[3:0](a[7:4]),
    .b[3:0](b[3:0]),
    .sa[1:0]({sa_3,sa_2}),
    .sb[1:0]({sa_1,sa_0}),
    .sft_ctrl_1(sft_ctrl_0_1),
    .sft_ctrl_2(sft_ctrl_0_2),
    .sft_ctrl_3[1:0](sft_ctrl_0_3[1:0]),
    .out[15:0](out1[15:0])
);

quarter_unit qu_2 (
    .clk(clk),
    .a[3:0](a[3:0]),
    .b[3:0](b[7:4]),
    .sa[1:0]({sa_1,sa_0}),
    .sb[1:0]({sa_3,sa_2}),
    .sft_ctrl_1(sft_ctrl_0_1),
    .sft_ctrl_2(sft_ctrl_0_2),
    .sft_ctrl_3[1:0](sft_ctrl_0_3[1:0]),
    .out[15:0](out2[15:0])
);

quarter_unit qu_3 (
    .clk(clk),
    .a[3:0](a[7:4]),
    .b[3:0](b[3:0]),
    .sa[1:0]({sa_3,sa_2}),
    .sb[1:0]({sa_3,sa_2}),
    .sft_ctrl_1(sft_ctrl_0_1),
    .sft_ctrl_2(sft_ctrl_0_2),
    .sft_ctrl_3[1:0](sft_ctrl_0_3[1:0]),
    .out[15:0](out3[15:0])
);

case ({cfga[1:0],cfgb[1:0]})
    4'b1010: begin
        assign sa_0 = 1'b0;
        assign sa_1 = 1'b0;
        assign sa_2 = 1'b0;
        assign sa_3 = sa;
        assign sb_0 = 1'b0;
        assign sb_1 = 1'b0;
        assign sb_2 = 1'b0;
        assign sb_3 = sb;
        assign sft_ctrl_0_1 = 1'b1;
        assign sft_ctrl_0_2 = 1'b1;
        assign sft_ctrl_0_3 = 2'b10;
        assign out0_ext = out0[15:0];
        assign out1_ext = {out1[11:0],4'b0};
        assign out2_ext = {out2[11:0],4'b0};
        assign out3_ext = {out3[7:0],8'b0};
        assign sum = out0_ext + out1_ext + out2_ext + out3_ext;
        assign out[63:0] = (sa_3||sb_3) ? {{48{sum[15]}},sum[15:0]} : {{48'b0,sum[15:0]};
    end
    4'b1001: begin
        assign sa_0 = 1'b0;
        assign sa_1 = 1'b0;
        assign sa_2 = 1'b0;
        assign sa_3 = sa;
        assign sb_0 = 1'b0;
        assign sb_1 = sb;
        assign sb_2 = 1'b0;
        assign sb_3 = sb;
        assign sft_ctrl_0_1 = 1'b1;
        assign sft_ctrl_0_2 = 1'b1;
        assign sft_ctrl_0_3 = 2'b10;
        assign out0_ext = out0[15:0];
        assign out1_ext = {out1[11:0],4'b0};
        assign out2_ext = out2[15:0];
        assign out3_ext = {out3[11:0],4'b0};
        assign sum[31:0] = out0_ext + out1_ext;
        assign sum[63:32] = out2_ext + out3_ext;
        assign out[63:0] = (sa_3||sb_3) ? {{20{sum[43]}},sum[43:32],{20{sum[11]}},sum[11:0]} : {20'b0,sum[43:32],{20'b0,sum[11:0]};
    end
    4'b0110: begin
        assign sa_0 = 1'b0;
        assign sa_1 = sa;
        assign sa_2 = 1'b0;
        assign sa_3 = sa;
        assign sb_0 = 1'b0;
        assign sb_1 = 1'b0;
        assign sb_2 = 1'b0;
        assign sb_3 = sb;
        assign sft_ctrl_0_1 = 1'b1;
        assign sft_ctrl_0_2 = 1'b1;
        assign sft_ctrl_0_3 = 2'b10;
        assign out0_ext = out0[15:0];
        assign out1_ext = out1[15:0];
        assign out2_ext = {out2[11:0],4'b0};
        assign out3_ext = {out3[11:0],4'b0};
        assign sum[31:0] = out0_ext + out2_ext;
        assign sum[63:32] = out1_ext + out3_ext;
        assign out[63:0] = (sa_3||sb_3) ? {{20{sum[43]}},sum[43:32],{20{sum[11]}},sum[11:0]} : {20'b0,sum[43:32],{20'b0,sum[11:0]};
    end
    4'b1000: begin
        assign sa_0 = 1'b0;
        assign sa_1 = 1'b0;
        assign sa_2 = 1'b0;
        assign sa_3 = sa;
        assign sb_0 = sb;
        assign sb_1 = sb;
        assign sb_2 = sb;
        assign sb_3 = sb;
        assign sft_ctrl_0_1 = 1'b1;
        assign sft_ctrl_0_2 = 1'b0;
        assign sft_ctrl_0_3 = 2'b01;
        assign out0_ext = (sa_3||sb_3) ? {{8{out0[7]}},out0[7:0]} : {8'b0,out0[7:0]};
        assign out1_ext = (sa_3||sb_3) ? {{4{out1[7]}},out1[7:0],4'b0} : {4'b0,out1[7:0],4'b0};
        assign out2_ext = (sa_3||sb_3) ? {{8{out2[7]}},out2[7:0]} : {8'b0,out2[7:0]};
        assign out3_ext = (sa_3||sb_3) ? {{4{out3[7]}},out3[7:0],4'b0} : {4'b0,out3[7:0],4'b0};
        assign out0_a_ext = (sa_3||sb_3) ? {{8{out0[15]}},out0[15:8]} : {8'b0,out0[15:8]};
        assign out1_a_ext = (sa_3||sb_3) ? {{4{out1[15]}},out1[15:8],4'b0} : {4'b0,out1[15:8],4'b0};
        assign out2_a_ext = (sa_3||sb_3) ? {{8{out2[15]}},out2[15:8]} : {8'b0,out2[15:8]};
        assign out3_a_ext = (sa_3||sb_3) ? {{4{out3[15]}},out3[15:8],4'b0} : {4'b0,out3[15:8],4'b0};
        assign sum[15:0] = out0_ext + out1_ext;
        assign sum[31:16] = out0_a_ext + out1_a_ext;
        assign sum[47:32] = out2_ext + out3_ext;
        assign sum[63:48] = out2_a_ext + out3_a_ext;
        assign out[63:0] = (sa_3||sb_3) ? {{6{sum[57]}},sum[57:48],{6{sum[41]}},sum[41:32],{6{sum[25]}},sum[25:16],{6{sum[9]}},sum[9:0]} : {6'b0,sum[57:48],6'b0,sum[41:32],6'b0,sum[25:16],6'b0,sum[9:0]};
    end
    4'b0010: begin
        assign sa_0 = sa;
        assign sa_1 = sa;
        assign sa_2 = sa;
        assign sa_3 = sa;
        assign sb_0 = 1'b0;
        assign sb_1 = 1'b0;
        assign sb_2 = 1'b0;
        assign sb_3 = sb;
        assign sft_ctrl_0_1 = 1'b0;
        assign sft_ctrl_0_2 = 1'b1;
        assign sft_ctrl_0_3 = 2'b01;
        assign out0_ext = (sa_3||sb_3) ? {{8{out0[7]}},out0[7:0]} : {8'b0,out0[7:0]};
        assign out1_ext = (sa_3||sb_3) ? {{8{out1[7]}},out1[7:0]} : {8'b0,out1[7:0]};
        assign out2_ext = (sa_3||sb_3) ? {{4{out2[7]}},out2[7:0],4'b0} : {4'b0,out2[7:0],4'b0};
        assign out3_ext = (sa_3||sb_3) ? {{4{out3[7]}},out3[7:0],4'b0} : {4'b0,out3[7:0],4'b0};
        assign out0_a_ext = (sa_3||sb_3) ? {{8{out0[15]}},out0[15:8]} : {8'b0,out0[15:8]};
        assign out1_a_ext = (sa_3||sb_3) ? {{8{out1[15]}},out1[15:8]} : {8'b0,out1[15:8]};
        assign out2_a_ext = (sa_3||sb_3) ? {{4{out2[15]}},out2[15:8],4'b0} : {4'b0,out2[15:8],4'b0};
        assign out3_a_ext = (sa_3||sb_3) ? {{4{out3[15]}},out3[15:8],4'b0} : {4'b0,out3[15:8],4'b0};
        assign sum[15:0] = out0_ext + out2_ext;
        assign sum[31:16] = out0_a_ext + out2_a_ext;
        assign sum[47:32] = out1_ext + out3_ext;
        assign sum[63:48] = out1_a_ext + out3_a_ext;
        assign out[63:0] = (sa_3||sb_3) ? {{6{sum[57]}},sum[57:48],{6{sum[41]}},sum[41:32],{6{sum[25]}},sum[25:16],{6{sum[9]}},sum[9:0]} : {6'b0,sum[57:48],6'b0,sum[41:32],6'b0,sum[25:16],6'b0,sum[9:0]};
    end
    4'b0101: begin
        assign sa_0 = 1'b0;
        assign sa_1 = sa;
        assign sa_2 = 1'b0;
        assign sa_3 = sa;
        assign sb_0 = 1'b0;
        assign sb_1 = sa;
        assign sb_2 = 1'b0;
        assign sb_3 = sb;
        assign sft_ctrl_0_1 = 1'b1;
        assign sft_ctrl_0_2 = 1'b1;
        assign sft_ctrl_0_3 = 2'b10;
        assign sum[15:0] = out0[15:0];
        assign sum[31:16] = out1[15:0];
        assign sum[47:32] = out2[15:0];
        assign sum[63:48] = out3[15:0];
        assign out = sum;
    end
    4'b0100: begin
        assign sa_0 = 1'b0;
        assign sa_1 = sa;
        assign sa_2 = 1'b0;
        assign sa_3 = sa;
        assign sb_0 = sb;
        assign sb_1 = sb;
        assign sb_2 = sb;
        assign sb_3 = sb;
        assign sft_ctrl_0_1 = 1'b1;
        assign sft_ctrl_0_2 = 1'b0;
        assign sft_ctrl_0_3 = 2'b01;
        assign sum[15:0] = out0[15:0];
        assign sum[31:16] = out1[15:0];
        assign sum[47:32] = out2[15:0];
        assign sum[63:48] = out3[15:0];
        assign out = sum;
    end
    4'b0001: begin
        assign sa_0 = sa;
        assign sa_1 = sa;
        assign sa_2 = sa;
        assign sa_3 = sa;
        assign sb_0 = 1'b0;
        assign sb_1 = sb;
        assign sb_2 = 1'b0;
        assign sb_3 = sb;
        assign sft_ctrl_0_1 = 1'b0;
        assign sft_ctrl_0_2 = 1'b1;
        assign sft_ctrl_0_3 = 2'b01;
        assign sum[15:0] = out0[15:0];
        assign sum[31:16] = out1[15:0];
        assign sum[47:32] = out2[15:0];
        assign sum[63:48] = out3[15:0];
        assign out = sum;
    end
    4'b0000: begin
        assign sa_0 = sa;
        assign sa_1 = sa;
        assign sa_2 = sa;
        assign sa_3 = sa;
        assign sb_0 = sb;
        assign sb_1 = sb;
        assign sb_2 = sb;
        assign sb_3 = sb;
        assign sft_ctrl_0_1 = 1'b0;
        assign sft_ctrl_0_2 = 1'b0;
        assign sft_ctrl_0_3 = 2'b00;
        assign sum[15:0] = out0[15:0];
        assign sum[31:16] = out1[15:0];
        assign sum[47:32] = out2[15:0];
        assign sum[63:48] = out3[15:0];
        assign out = sum;
    end
    default: begin
        assign out = 64'b0;
    end
endcase

endmodule