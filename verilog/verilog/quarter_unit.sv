module quarter_unit (
    input [3:0] a,
    input [3:0] b,
    input [1:0] sa,
    input [1:0] sb,
    input sft_ctrl_1,
    input sft_ctrl_2,
    input [1:0] sft_ctrl_3,

    output reg [15:0] out
);

logic [3:0] out0, out1, out2, out3;
logic signed [7:0] out0_ext, out1_ext, out2_ext, out3_ext;
logic signed [15:0] sum;

bitbrick bb_0 (
    .a(a[1:0]),
    .b(b[1:0]),
    .sa(sa[0]),
    .sb(sb[0]),
    .out(out0[3:0])
);

bitbrick bb_1 (
    .a(a[3:2]),
    .b(b[1:0]),
    .sa(sa[1]),
    .sb(sb[0]),
    .out(out1[3:0])
);

bitbrick bb_2 (
    .a(a[1:0]),
    .b(b[3:2]),
    .sa(sa[0]),
    .sb(sb[1]),
    .out(out2[3:0])
);

bitbrick bb_3 (
    .a(a[3:2]),
    .b(b[3:2]),
    .sa(sa[1]),
    .sb(sb[1]),
    .out(out3[3:0])
);

always_comb begin
    out0_ext = (sa[0]||sb[0]) ? {{4{out0[3]}},out0[3:0]} : {4'b0,out0[3:0]};
    out1_ext = (sa[1]||sb[0]) ? {{2{out1[3]}},out1[3:0],2'b00} : {2'b00,out1[3:0],2'b00};
    out2_ext = (sa[0]||sb[1]) ? {{2{out2[3]}},out2[3:0],2'b00} : {2'b00,out2[3:0],2'b00};
    out3_ext = (sa[1]||sb[1]) ? {out3[3:0],4'b0} : {out3[3:0],4'b0};
    sum = out0_ext + out1_ext + out2_ext + out3_ext;
    out[15:0] = (sa[1]||sb[1]) ? {{8{sum[7]}},sum[7:0]} : {8'b0,sum[7:0]};
    case ({sft_ctrl_3[1:0],sft_ctrl_2,sft_ctrl_1})
        4'b1011: begin
            out0_ext = (sa[0]||sb[0]) ? {{4{out0[3]}},out0[3:0]} : {4'b0,out0[3:0]};
            out1_ext = (sa[1]||sb[0]) ? {{2{out1[3]}},out1[3:0],2'b00} : {2'b00,out1[3:0],2'b00};
            out2_ext = (sa[0]||sb[1]) ? {{2{out2[3]}},out2[3:0],2'b00} : {2'b00,out2[3:0],2'b00};
            out3_ext = (sa[1]||sb[1]) ? {out3[3:0],4'b0} : {out3[3:0],4'b0};
            sum = out0_ext + out1_ext + out2_ext + out3_ext;
            out[15:0] = (sa[1]||sb[1]) ? {{8{sum[7]}},sum[7:0]} : {8'b0,sum[7:0]};
        end
        4'b0110: begin
            out0_ext = (sa[0]||sb[0]) ? {{4{out0[3]}},out0[3:0]} : {4'b0,out0[3:0]} ;
            out1_ext = (sa[1]||sb[0]) ? {{4{out1[3]}},out1[3:0]} : {4'b0,out1[3:0]};
            out2_ext = (sa[0]||sb[1]) ? {{2{out2[3]}},out2[3:0],2'b00} : {2'b00,out2[3:0],2'b00};
            out3_ext = (sa[1]||sb[1]) ? {{2{out2[3]}},out3[3:0],2'b00} : {2'b00,out3[3:0],2'b00};
            sum[7:0] = out0_ext + out2_ext;
            sum[15:8] = out1_ext + out3_ext;
            out[15:0] = (sa[1]||sb[1]) ? {{2{sum[5]}},sum[13:8],{2{sum[5]}},sum[5:0]} : {2'b00,sum[13:8],2'b00,sum[5:0]};
        end
        4'b0101: begin
            out0_ext = (sa[0]||sb[0]) ? {{4{out0[3]}},out0[3:0]} : {4'b0,out0[3:0]};
            out1_ext = (sa[1]||sb[0]) ? {{2{out1[3]}},out1[3:0],2'b00} : {2'b00,out1[3:0],2'b00};
            out2_ext = (sa[0]||sb[1]) ? {{4{out2[3]}},out2[3:0]} : {4'b0,out2[3:0]};
            out3_ext = (sa[1]||sb[1]) ? {{2{out2[3]}},out3[3:0],2'b00} : {2'b00,out3[3:0],2'b00};
            sum[7:0] = out0_ext + out1_ext;
            sum[15:8] = out2_ext + out3_ext;
            out[15:0] = (sa[1]||sb[1]) ? {{2{sum[5]}},sum[13:8],{2{sum[5]}},sum[5:0]} : {2'b00,sum[13:8],2'b00,sum[5:0]};
        end
        4'b0000: begin
            out0_ext = (sa[0]||sb[0]) ? {{4{out0[3]}},out0[3:0]} : {4'b0, out0[3:0]};
            out1_ext = (sa[1]||sb[0]) ? {{4{out1[3]}},out1[3:0]} : {4'b0, out1[3:0]};
            out2_ext = (sa[0]||sb[1]) ? {{4{out2[3]}},out2[3:0]} : {4'b0, out2[3:0]};
            out3_ext = (sa[1]||sb[1]) ? {{4{out2[3]}},out3[3:0]} : {4'b0, out3[3:0]};
            sum[3:0] = out0_ext;
            sum[7:4] = out1_ext;
            sum[11:8] = out2_ext;
            sum[15:12] = out3_ext;
            out = sum;
        end
        default: begin
            out = 16'b0;
        end
    endcase
end

endmodule
