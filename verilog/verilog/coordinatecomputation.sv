module coordinatecomputation
        (
         input wire clk,
         input wire reset_n,
         input wire[1:0] bitwidth,
         input wire[3:0] weight_indices[16],
         input wire[3:0] activation_indices[16],
         input wire[3:0] weight_dim,
         input wire[8:0] activation_dim,
         output logic signed [15:0] row_coordinate[256],
         output logic signed [15:0] column_coordinate[256]
       );


logic [31:0] weight_index[16], activation_index[16], weight_index_row, weight_index_column, activation_index_row, activation_index_column;
integer i,j;
always @(posedge clk or negedge reset_n) begin
  if (!reset_n) begin
    for (i = 0; i<16; i = i + 1) begin
      weight_index[i] <= 0;
      activation_index[i] <= 0;
    end
    for (i = 0; i<256; i = i + 1) begin
      row_coordinate[i] = 0;
      column_coordinate[i] = 0;
    end
    activation_index_row = 0;
    activation_index_column = 0;
    weight_index_row = 0;
    weight_index_column = 0;
  end
  else begin
    case(bitwidth)
      2'b00:
        begin
          //Calculate weight index and activation index from compressed
          //representation
          weight_index[0] = weight_index[15] + weight_indices[0];
          for (i = 1; i<16; i = i + 1) begin
              weight_index[i] = weight_index[i-1] + weight_indices[i] + 1;
          end
          activation_index[0] = activation_index[15] + activation_indices[0];
          for (i = 1; i<16; i = i + 1) begin
              activation_index[i] = activation_index[i-1] + activation_indices[i] + 1;
          end
          
          //Calculate the output row and column coordinates
          for (i = 0; i<16; i = i +1) begin
            for (j = 0; j<16; j = j + 1) begin
              weight_index_row = weight_index[i] / weight_dim;
              weight_index_column = weight_index[i] % weight_dim;
              activation_index_row = activation_index[j] / activation_dim;
              activation_index_column = activation_index[j] % activation_dim;
              row_coordinate[i*16 + j] <= (weight_dim >> 1) - weight_index_row + activation_index_row + 1;
              column_coordinate[i*16 + j] <= (weight_dim >> 1) - weight_index_column + activation_index_column + 1;
            end
          end
        end      
      2'b01: 
        begin
          //Calculate weight index and activation index from compressed
          //representation
          weight_index[0] = weight_index[7] + weight_indices[0];
          for (i = 1; i<8; i = i + 1) begin
              weight_index[i] = weight_index[i-1] + weight_indices[i] + 1;
          end
          activation_index[0] = activation_index[7] + activation_indices[0];
          for (i = 1; i<8; i = i + 1) begin
              activation_index[i] = activation_index[i-1] + activation_indices[i] + 1;
          end
          
          //Calculate the output row and column coordinates
          for (i = 0; i<8; i = i +1) begin
            for (j = 0; j<8; j = j + 1) begin
              weight_index_row = weight_index[i] / weight_dim;
              weight_index_column = weight_index[i] % weight_dim;
              activation_index_row = activation_index[j] / activation_dim;
              activation_index_column = activation_index[j] % activation_dim;
              row_coordinate[i*8 + j] <= (weight_dim >> 1) - weight_index_row + activation_index_row + 1;
              column_coordinate[i*8 + j] <= (weight_dim >> 1) - weight_index_column + activation_index_column + 1;
            end
          end
        end      
      2'b10: 
        begin
          //Calculate weight index and activation index from compressed
          //representation
          weight_index[0] = weight_index[3] + weight_indices[0];
          for (i = 1; i<4; i = i + 1) begin
              weight_index[i] = weight_index[i-1] + weight_indices[i] + 1;
          end
          activation_index[0] = activation_index[3] + activation_indices[0];
          for (i = 1; i<4; i = i + 1) begin
              activation_index[i] = activation_index[i-1] + activation_indices[i] + 1;
          end
          
          //Calculate the output row and column coordinates
          for (i = 0; i<4; i = i +1) begin
            for (j = 0; j<4; j = j + 1) begin
              weight_index_row = weight_index[i] / weight_dim;
              weight_index_column = weight_index[i] % weight_dim;
              activation_index_row = activation_index[j] / activation_dim;
              activation_index_column = activation_index[j] % activation_dim;
              row_coordinate[i*4 + j] <= (weight_dim >> 1) - weight_index_row + activation_index_row + 1;
              column_coordinate[i*4 + j] <= (weight_dim >> 1) - weight_index_column + activation_index_column + 1;
            end
          end
        end      
      default: row_coordinate[0] <= 0;
    endcase 
  end
end
endmodule
