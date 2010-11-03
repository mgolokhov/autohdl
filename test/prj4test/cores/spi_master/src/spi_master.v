`default_nettype none
module spi_master
	#(parameter w_length = 10, clk_div = 14, inv_clk = 1)
	(
	input clk,							// Input Clock
	input rst,							// Reset
	input	[w_length-1:0] value_in,	// Input value
	output reg [w_length-1:0] value_out,	// Output value
	input	strob_in,					// start of convertion
	output	sdi_out,					// SDI output
	input	sdo_in,						// SDO input
	output	sclk_out,					// 
	output	load_out,					// 
	output	reg finish						// 
	);
	
	
	// 50 Mhz clock
	// 10 kHz serial clock
	// 20 rHz machine clock
	
	
	
	reg [clk_div-1:0] clk_divider;
	reg strob;
	
	
	always @(posedge clk, posedge rst)
		if(rst)
			begin
				clk_divider <= 0; 
				strob <= 0;
			end
		
		else
			{strob,clk_divider} <= clk_divider + 1;
	
	
	
	reg [w_length-1:0] value;
	

	reg start;
	reg sdi;
	reg [5:0] state_m;
	reg ss;
	reg sclk;
	
	always @(posedge clk or posedge rst)
		if(rst)		   
			begin
				value <= 0;
				start <= 0;
			end
		else
			begin
				if(strob)
					begin
						start <= 0;
						if(finish == 0)
							if(state_m[0])
								value <= value<<1;
					end
				if(strob_in)
					//if(finish == 0)
					begin
						value <= value_in;
						start <= 1;
					end
			end
	
	
	
	
	
	always @(posedge clk, posedge rst)
		if(rst)
			begin
				finish <= 1;
				state_m <= 0;
				ss <= 1;
				sclk <= 1;
				sdi <= 1;
				value_out <= 0;
			end
		
		else
			begin
				if(start == 1)
					finish <= 0;
				if(strob)
					begin
						sdi <= value[w_length-1];
						case (state_m)
							0: if (start)
									begin
										finish <= 0;
										sclk <= 0;
										ss <= 0;
										state_m <= state_m + 1;
									end
								else
									begin
										finish <= 1;
										sclk <= 1;
										ss <= 1;
									end
							
							({w_length,1'b0}): begin
									finish <= 1;
									ss <= 1;	 
									sclk <= 1;
									state_m <= 0;
								end
							default:
								begin
									sclk <= state_m[0];
									state_m <=state_m + 1;
									if(state_m[0] == 0)
										value_out <= (value_out<<1) | sdo_in ;
									
								end
						endcase
					end
			end
	
	
	
	assign sdi_out = sdi;
	assign load_out = ss;
	assign sclk_out = inv_clk ? sclk: ~sclk;
	
endmodule