module async_fifo_tb;

  parameter DATA_WIDTH = 8;
  parameter ADDR_WIDTH = 4;

  reg wr_clk = 0;
  reg rd_clk = 0;
  reg rst = 1;
  reg wr_en = 0;
  reg rd_en = 0;
  reg [DATA_WIDTH-1:0] din;
  wire [DATA_WIDTH-1:0] dout;
  wire full, empty;

  async_fifo #(DATA_WIDTH, ADDR_WIDTH) dut (
    .wr_clk(wr_clk),
    .rd_clk(rd_clk),
    .rst(rst),
    .wr_en(wr_en),
    .rd_en(rd_en),
    .din(din),
    .dout(dout),
    .full(full),
    .empty(empty)
  );

  always #5 wr_clk = ~wr_clk; 
  always #12 rd_clk = ~rd_clk; 

  integer i;

  initial begin
    $monitor("Time=%0t wr_en=%b rd_en=%b din=%h dout=%h full=%b empty=%b", 
              $time, wr_en, rd_en, din, dout, full, empty);

    #20 rst = 0;

    
    for (i = 0; i < 10; i = i + 1) begin
      @(posedge wr_clk);
      if (!full) begin
        din <= i + 8'hA0;
        wr_en <= 1;
      end
    end
    @(posedge wr_clk) wr_en <= 0;

    #100;
    for (i = 0; i < 10; i = i + 1) begin
      @(posedge rd_clk);
      if (!empty) begin
        rd_en <= 1;
      end
    end
    @(posedge rd_clk) rd_en <= 0;
  end
  initial
    begin
      $dumpfile;
      $dumpvars;

    #100 $finish;
  end

endmodule

