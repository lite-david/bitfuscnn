module coordinatecomputation
#(parameter MAX_OUTPUTS = 256)
        (
         input wire clk,
         input wire reset_n,
         input wire[1:0] bitwidth,
         input wire[3:0] weight_indices[16],
         input wire[3:0] activation_indices[16],
         input wire[3:0] weight_dim,
         input wire[8:0] activation_dim,
         output logic signed [15:0] row_coordinate[MAX_OUTPUTS],
         output logic signed [15:0] column_coordinate[MAX_OUTPUTS]
       );


logic [31:0] weight_index[16], activation_index[16], weight_index_row, weight_index_column, activation_index_row, activation_index_column;
logic [31:0] next_activation_start, next_weight_start;

logic signed [15:0] next_row_coordinate[MAX_OUTPUTS];
logic signed [15:0] next_column_coordinate[MAX_OUTPUTS];
integer i,j;

always_comb begin
    for (i = 0; i<16; i = i + 1) begin
      weight_index[i] = 0;
      activation_index[i] = 0;
    end
    for (i = 0; i<MAX_OUTPUTS; i++) begin
      next_row_coordinate[i] = 0;
      next_column_coordinate[i] = 0;
    end
    activation_index_row = 0;
    activation_index_column = 0;
    weight_index_row = 0;
    weight_index_column = 0;
    case(bitwidth)
      2'b00:
        begin
          //Calculate weight index and activation index from compressed
          //representation
          weight_index[0] = next_weight_start + weight_indices[0];
          for (i = 1; i<16; i = i + 1) begin
              weight_index[i] = weight_index[i-1] + weight_indices[i] + 1;
          end
          activation_index[0] = next_activation_start + activation_indices[0];
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
              next_row_coordinate[i*16 + j] = (weight_dim >> 1) - weight_index_row + activation_index_row + 1;
              next_column_coordinate[i*16 + j] = (weight_dim >> 1) - weight_index_column + activation_index_column + 1;
            end
          end
        end      
      2'b01: 
        begin
          //Calculate weight index and activation index from compressed
          //representation
          weight_index[0] = next_weight_start + weight_indices[0];
          for (i = 1; i<8; i = i + 1) begin
              weight_index[i] = weight_index[i-1] + weight_indices[i] + 1;
          end
          activation_index[0] = next_activation_start + activation_indices[0];
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
              next_row_coordinate[i*8 + j] = (weight_dim >> 1) - weight_index_row + activation_index_row + 1;
              next_column_coordinate[i*8 + j] = (weight_dim >> 1) - weight_index_column + activation_index_column + 1;
            end
          end
        end      
      2'b10: 
        begin
          //Calculate weight index and activation index from compressed
          //representation
          weight_index[0] = next_weight_start + weight_indices[0];
          for (i = 1; i<4; i = i + 1) begin
              weight_index[i] = weight_index[i-1] + weight_indices[i] + 1;
          end
          activation_index[0] = next_activation_start + activation_indices[0];
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
              next_row_coordinate[i*4 + j] = (weight_dim >> 1) - weight_index_row + activation_index_row + 1;
              next_column_coordinate[i*4 + j] = (weight_dim >> 1) - weight_index_column + activation_index_column + 1;
            end
          end
        end      
    endcase 

end

always @(posedge clk or negedge reset_n) begin
  if (!reset_n) begin
    for (i = 0; i<MAX_OUTPUTS; i = i + 1) begin
      row_coordinate[i] <= 0;
      // next_row_coordinate[i] <= 0;
      // next_column_coordinate[i] <= 0;
      column_coordinate[i] <= 0;
    end
    next_weight_start <= 0;
    next_activation_start <= 0;
  end
  else begin
    case(bitwidth)
      2'b00:
        begin
          next_weight_start <= weight_index[15];
          next_activation_start <= activation_index[15];
          //Calculate the output row and column coordinates
          for (i = 0; i<16; i = i +1) begin
            for (j = 0; j<16; j = j + 1) begin
              row_coordinate[i*16 + j] <= next_row_coordinate[i*16 + j];
              column_coordinate[i*16 + j] <= next_column_coordinate[i*16 + j];
            end
          end
        end      
      2'b01: 
        begin
          next_weight_start <= weight_index[7];
          next_activation_start <= activation_index[7];
          //Calculate the output row and column coordinates
          for (i = 0; i<8; i = i +1) begin
            for (j = 0; j<8; j = j + 1) begin
              row_coordinate[i*8 + j] <= next_row_coordinate[i*8 + j];
              column_coordinate[i*8 + j] <= next_column_coordinate[i*8 + j];
            end
          end
        end      
      2'b10: 
        begin
          next_weight_start <= weight_index[3];
          next_activation_start <= activation_index[3];
          //Calculate the output row and column coordinates
          for (i = 0; i<4; i = i +1) begin
            for (j = 0; j<4; j = j + 1) begin
              row_coordinate[i*4 + j] <= next_row_coordinate[i*4 + j];
              column_coordinate[i*4 + j] <= next_column_coordinate[i*4 + j];
            end
          end
        end      
      default: row_coordinate[0] <= 0;
    endcase 
  end
end
endmodule
