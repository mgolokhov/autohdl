//-----------------------------------------------------------------------------
//
// Title       : cordic
// Design      : algorithm
// Author      : Golohov,Romanov
//
//-----------------------------------------------------------------------------
//
// Description : CORDIC sine/cosine generator 
// Argument convertion. 
// z0=-32765 - -pi rad
// z0=32765  - pi rad	
// z0=0      - 0 rad.
// outputs cos and sin - calculated sin(z0) and cos(z0)
// output finish - high level of that signal indicates end of calculations
// input z0 - argument
// inputs clock and reset - clock and reset signals
// input start -  high level of that signal indicates beginning of calculations
//-----------------------------------------------------------------------------

module cordic_core_v2(reset,clock,start,z0,finish,sin,cos);
    
    parameter w = 16;
    parameter st_w = 4;
    parameter vec_len = 19898;
	
    output signed [w-1:0] cos;
    output signed [w-1:0] sin;
    output finish;
    
    input signed [w-1:0] z0;
    
    input start;
    input clock;
    input reset;
    
    reg signed [w-1:0] cos;
    reg signed [w-1:0] sin;
    reg finish;
    
    
    reg [st_w-1:0] i;
    reg state;
    reg signed [w-1:0] y;	
    reg signed [w-1:0] x;	
    reg signed [w-1:0] z;	
    
    wire signed [w-1:0] t [0:w-2];
    
    
    assign t[0]  = 16'd8192;
    assign t[1]  = 16'd4836;
    assign t[2]  = 16'd2555;
    assign t[3]  = 16'd1297;
    assign t[4]  = 16'd651;
    assign t[5]  = 16'd326;
    assign t[6]  = 16'd163;
    assign t[7]  = 16'd81;
    assign t[8]  = 16'd41;
    assign t[9]  = 16'd20;
    assign t[10]  = 16'd10;
    assign t[11]  = 16'd5;
    assign t[12]  = 16'd3;
    assign t[13]  = 16'd1;
    assign t[14]  = 16'd1;
    
    
   
    always @(posedge clock or posedge reset) begin 
            
            if (reset) begin
                    state <= 1'b0;
                    cos <= 0;
                    sin <= 0;
                    finish <= 0;
                    x <= 0;
                    y <= 0;
                    z <= 0;
                    i <= 0;
                end
            else begin
                    if(finish == 1)
                        finish <= 0;
                    case (state)
                        1'b0: begin
                                if (start) begin
                                        x <= vec_len;//6334; //Модуль вектора равен 1/pi
                                        y <= 0;		 
										if (!z0[w-1])
                                        	z <= z0-16'h4000;
										else
											z <= -z0-16'h4000;
                                        i <= 0;
                                        finish <= 0;
                                        state <= 1'b1;
                                    end
                            end
                        1'b1: begin				                                  
                                if (!z[w-1]) begin
                                        if(y[w-1] == 1)
                                            x <= x + ((-y) >> i);
                                        else
                                            x <= x - (y >> i);
                                        if(x[w-1] == 1)
                                            y <= y - ((-x) >> i);
                                        else
                                            y <= y + (x >> i);
                                        
                                        z <= z - t[i];
                                    end
                                else begin
                                        if(y[w-1] == 1)
                                            x <= x - ((-y) >> i);
                                        else
                                            x <= x + (y >> i);
                                        if(x[w-1] == 1)
                                            y <= y + ((-x) >> i);
                                        else
                                            y <= y - (x >> i);
                                        z <= z + t[i];
                                    end
                 
                                if (i == (w-1)) begin
                                                                                
                                        cos<=-y;
										if (!z0[w-1])
											sin<=x;
										else	
											sin<=-x;			
							
                                                                              
                                        
                                        state <= 1'b0;
                                        finish <= 1;
                                    end
                                else begin
                                        i <= i + 1;
                                    end
                            end
                    endcase
                end
        end
    
endmodule