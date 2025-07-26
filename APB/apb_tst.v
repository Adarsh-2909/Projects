module tb_apb_slave;
reg PCLK;
reg PRESETn;
reg PSEL;
reg PENABLE;
reg PWRITE;
reg [31:0] PADDR;
reg [31:0] PWDATA;
wire [31:0] PRDATA;
wire PREADY;


apb_slave dut (
    .PCLK(PCLK),
    .PRESETn(PRESETn),
    .PSEL(PSEL),
    .PENABLE(PENABLE),
    .PWRITE(PWRITE),
    .PADDR(PADDR),
    .PWDATA(PWDATA),
    .PRDATA(PRDATA),
    .PREADY(PREADY)
);


initial begin
    PCLK = 0;
    forever #5 PCLK = ~PCLK; 
end


initial begin
    PRESETn = 0;
    PSEL = 0;
    PENABLE = 0;
    PWRITE = 0;
    PADDR = 32'b0;
    PWDATA = 32'b0;

    
    #10;
    PRESETn = 1;

    
    PSEL = 1; PADDR = 32'h00; PWDATA = 32'hDEADBEFF; PWRITE = 1; PENABLE = 1;
    #10; 
    PSEL = 0; PWRITE = 0; PENABLE = 0;

    
    #10;
    PSEL = 1; PADDR = 32'h00; PWRITE = 0; PENABLE = 1;
    #10; 
    PSEL = 0; PENABLE = 0;
end
  initial
    begin
      $dumpfile;
      $dumpvars;

   
    #20;
    $finish;
end

endmodule				
