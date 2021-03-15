`define TILE_SIZE 32
`define MAX_BITWIDTH 8

package utils;

  function common();
    $display("Test");
  endfunction

  function logic combine_or(input logic [`MAX_BITWIDTH-1:0] data);
  logic[`MAX_BITWIDTH-1:0] tmp;
  int i;
  tmp[0] = data[0];
  for(i = 1; i<`MAX_BITWIDTH; i++) begin
    tmp[i] = data[i] | tmp[i-1];
  end
  combine_or = tmp[`MAX_BITWIDTH-1];
  endfunction
endpackage