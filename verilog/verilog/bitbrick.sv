module bitbrick (
    clk,
    a[1:0]
    b[1:0]
    sa,
    sb,
    out[3:0]
);

input clk;
input a[1:0];
input b[1:0];
input sa;
input sb;

output reg [3:0] out;

wire signed [2:0] sea, seb;
wire signed [5:0] p;

always_comb begin
    assign sea = {a[1]&sa,a[1:0]}
    assign seb = {b[1]&sb,b[1:0]}

    assign p = sea * seb;
    assign out[3:0] = p[3:0];
end
  
endmodule