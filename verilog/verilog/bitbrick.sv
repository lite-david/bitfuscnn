module bitbrick (
    input clk,
    input a[1:0]
    input b[1:0]
    input sa,
    input sb,

    output reg out[3:0]
);

wire signed [2:0] sea, seb;
wire signed [5:0] p;

always_comb begin
    sea = {a[1]&sa,a[1:0]}
    seb = {b[1]&sb,b[1:0]}
    
    p = sea * seb;
    out[3:0] = p[3:0];
end
  
endmodule