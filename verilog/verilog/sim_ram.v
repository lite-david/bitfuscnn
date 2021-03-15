module sim_ram #(parameter integer WIDTH = 10)(
         input logic clk,
         input logic write_enable,
         input logic[WIDTH-1:0] address,
         input logic[31:0] data_in,
         output logic [31:0] data_out

       );

logic [WIDTH-1:0][31:0] data;

integer i;
initial begin
  for(i = 0; i<2**WIDTH; i++) begin
    data[i] = 0;
  end
end

always @(posedge clk ) begin
  if(write_enable) begin
    data[address] = data_in;
  end
end

always_comb begin
  data_out = data[address];
end

endmodule
