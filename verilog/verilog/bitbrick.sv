module bitbrick (
    input clk,
    input [1:0] a,
    input [1:0] b,
    input sa,
    input sb,

    output reg [3:0] out
);

logic signed [2:0] sea, seb;
logic signed [5:0] p;

always_comb begin
    sea = {a[1]&sa,a[1:0]};
    seb = {b[1]&sb,b[1:0]};
    
    p = sea * seb;
    out[3:0] = p[3:0];
end

endmodule
