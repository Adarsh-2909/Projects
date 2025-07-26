module async_fifo #(
  parameter DATA_WIDTH = 8,
  parameter ADDR_WIDTH = 4 
)(
  input wr_clk,
  input rd_clk,
  input rst,
  input wr_en,
  input rd_en,
  input [DATA_WIDTH-1:0] din,
  output reg [DATA_WIDTH-1:0] dout,
  output full,
  output empty
);

  localparam DEPTH = (1 << ADDR_WIDTH);

  
  reg [DATA_WIDTH-1:0] mem[0:DEPTH-1];

  
  reg [ADDR_WIDTH:0] wr_ptr_bin = 0;
  reg [ADDR_WIDTH:0] wr_ptr_gray = 0;
  reg [ADDR_WIDTH:0] wr_ptr_gray_rd_clk = 0;

  
  reg [ADDR_WIDTH:0] rd_ptr_bin = 0;
  reg [ADDR_WIDTH:0] rd_ptr_gray = 0;
  reg [ADDR_WIDTH:0] rd_ptr_gray_wr_clk = 0;

  
  reg [ADDR_WIDTH:0] wr_ptr_gray_rd_clk_ff = 0;
  always @(posedge rd_clk or posedge rst) begin
    if (rst) begin
      wr_ptr_gray_rd_clk <= 0;
      wr_ptr_gray_rd_clk_ff <= 0;
    end else begin
      wr_ptr_gray_rd_clk_ff <= wr_ptr_gray;
      wr_ptr_gray_rd_clk <= wr_ptr_gray_rd_clk_ff;
    end
  end

  
  reg [ADDR_WIDTH:0] rd_ptr_gray_wr_clk_ff = 0;
  always @(posedge wr_clk or posedge rst) begin
    if (rst) begin
      rd_ptr_gray_wr_clk <= 0;
      rd_ptr_gray_wr_clk_ff <= 0;
    end else begin
      rd_ptr_gray_wr_clk_ff <= rd_ptr_gray;
      rd_ptr_gray_wr_clk <= rd_ptr_gray_wr_clk_ff;
    end
  end

  
  function [ADDR_WIDTH:0] bin2gray(input [ADDR_WIDTH:0] bin);
    bin2gray = bin ^ (bin >> 1);
  endfunction

 
  function [ADDR_WIDTH:0] gray2bin(input [ADDR_WIDTH:0] gray);
    integer i;
    begin
      gray2bin = gray;
      for (i = ADDR_WIDTH; i > 0; i = i - 1)
        gray2bin[i-1] = gray2bin[i] ^ gray[i-1];
    end
  endfunction

  
  always @(posedge wr_clk or posedge rst) begin
    if (rst) begin
      wr_ptr_bin <= 0;
      wr_ptr_gray <= 0;
    end else if (wr_en && !full) begin
      mem[wr_ptr_bin[ADDR_WIDTH-1:0]] <= din;
      wr_ptr_bin <= wr_ptr_bin + 1;
      wr_ptr_gray <= bin2gray(wr_ptr_bin + 1);
    end
  end

  
  always @(posedge rd_clk or posedge rst) begin
    if (rst) begin
      rd_ptr_bin <= 0;
      rd_ptr_gray <= 0;
      dout <= 0;
    end else if (rd_en && !empty) begin
      dout <= mem[rd_ptr_bin[ADDR_WIDTH-1:0]];
      rd_ptr_bin <= rd_ptr_bin + 1;
      rd_ptr_gray <= bin2gray(rd_ptr_bin + 1);
    end
  end

  
  assign full = (wr_ptr_gray == {~rd_ptr_gray_wr_clk[ADDR_WIDTH:ADDR_WIDTH-1], rd_ptr_gray_wr_clk[ADDR_WIDTH-2:0]});
  assign empty = (rd_ptr_gray == wr_ptr_gray_rd_clk);

endmodule
