module apb_slave(
    input         PCLK,
    input         PRESETn,
    input         PSEL,
    input         PENABLE,
    input         PWRITE,
    input  [31:0] PADDR,
    input  [31:0] PWDATA,
    output reg    PREADY,
    output reg [31:0] PRDATA
);
reg [31:0] apb_memory [0:255];
reg [1:0] state; 
localparam IDLE = 2'b00,
           SETUP = 2'b01,
           ACCESS = 2'b10;
always @(posedge PCLK or negedge PRESETn) begin
    if (!PRESETn) begin
        state <= IDLE;
        PREADY <= 1'b1;
        PRDATA <= 32'b0;
    end else begin
        case (state)
            IDLE: begin
                
                if (PSEL) begin
                    state <= SETUP;
                    PREADY <= 1'b0; 
                end
            end
            
            SETUP: begin
                
                if (PENABLE) begin
                    state <= ACCESS;
                end
            end
          
            ACCESS: begin
                if (PWRITE) begin
                    
                    apb_memory[PADDR[7:0]] <= PWDATA; 
                end else begin
                    
                    PRDATA <= apb_memory[PADDR[7:0]];
                end
                state <= IDLE; 
                PREADY <= 1'b1; 
            end
            
            default: state <= IDLE; 
        endcase
    end
end

endmodule
