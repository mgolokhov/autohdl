`default_nettype none
module 
	adc_spi_conv_v2(
	input clk,
	input rst,
	output	sdi_out,
	input	sdo_in,
	output	sclk_out,
	output	reg conv_out,
	output reg[11:0] value_out0,
	output reg[11:0] value_out1,
	output reg[11:0] value_out2,
	output reg[11:0] value_out3,
	output reg[11:0] value_out4,
	output reg[11:0] value_out5,
	output reg[11:0] value_out6,
	output reg[11:0] value_out7,
	output reg finish
	);	 
	
	parameter chn_str = 0;	 //Номер канала, c которого начина
	parameter chn_end = 7;	 //Номер канала, после которого переключаться снова на chn_str-ой
	
	reg [2:0] ch_in;
	
	wire [11:0] value;
	
	
	wire [12:0] control_word;
	assign control_word = 
	{
		1'b0,
		1'b0, 			// 9 - A0   
		1'b1, 			// 8 - PD1
		1'b1, 			// 7 - PD0
		1'b0, 			// 6 - Vin8,~AGND
		1'b0, 			// 5 - DIFF/~SGL
		ch_in[2],	 	// 4 - CH2
		ch_in[1], 		// 3 - CH1
		ch_in[0], 		// 2 - CH0
		1'b0, 			// 1 - ~CONVS
		1'b1, 			// 0 - EXT REF
		3'b0			// for fix
		};
	
	
	
	reg strob;
	wire finish1;
	
	spi_master #(
		.w_length(13),
		.clk_div(2),
		.inv_clk(0))
		ADC (.clk(clk),
		.rst(rst),
		.value_in(control_word),
		.value_out(value),
		.strob_in(strob),
		.sdi_out(sdi_out),
		.sdo_in(sdo_in),
		.sclk_out(sclk_out),
		.load_out(),
		.finish(finish1)
		);

	// 50 Mhz clock
	// 10 kHz serial clock
	// 20 rHz machine clock
	
	// Statem
	// idle - wait for strob conv = 1
	// run  - conv = 0
	//	wait - wait for 1 us
	//  run2 - conv = 1
	//	wait2 - wait for 1 us
	//	wait3 - wait for 1 us
	//	cycle spi
	//	wait4 - wait for 1 us
	//	wait5 - wait for 1 us, go idle
	
	//typedef enum logic [3:0] {
	`define	st_idle		0
	`define	st_wait		1
	`define	st_cycle1	2
	`define	st_wait2	3
	`define	st_wait2_5	4
	`define	st_wait3	5
	`define	st_cycle2	6
	`define	st_wait4	7
	`define	st_wait5	8
//	} t_state_m;
	
//	t_state_m state_m;

	reg [3:0] state_m;
	
	reg [8:0] timer;
	
	always @(posedge clk, posedge rst)
		if(rst)
			begin  
				ch_in <= chn_str;
				timer <= 0;
				state_m <= `st_idle;
				conv_out <= 0;
				strob <= 0;
				value_out0 <= 0;
				value_out1 <= 0;
				value_out2 <= 0;
				value_out3 <= 0;
				value_out4 <= 0;
				value_out5 <= 0;
				value_out6 <= 0;
				value_out7 <= 0;
				finish <= 0;
			end
		else
			begin
				strob <= 0;	
				finish <= 0;
				if(timer)
					timer <= timer - 1;
				else
					case (state_m)
						`st_idle:
							begin
								state_m <= `st_wait;
								timer <= 20;
								conv_out <= 1;
							end
						`st_wait:
							begin
								state_m <= `st_cycle1;
								timer <= 100;
								conv_out <= 0;
							end
						`st_cycle1:
							begin
								conv_out <= 0;
								strob <= 1;
								state_m <=	`st_wait2;
								timer <= 125;
							end	
						`st_wait2:
							begin
								conv_out <= 0;
								if( finish1 == 1 )
									begin 
										conv_out <= 1;
										state_m <= `st_idle;
										timer <= 1;
										case (ch_in)
											0: value_out0 <= value;
											1: value_out1 <= value;
											2: value_out2 <= value;
											3: value_out3 <= value;
											4: value_out4 <= value;
											5: value_out5 <= value;
											6: value_out6 <= value;
											7: value_out7 <= value;
										endcase				  
										if (ch_in==chn_end)
											ch_in <= chn_str; 
										else 
											ch_in <= ch_in + 1;	
										finish <= 1;
									end
								
							end
					endcase
			end
	
				
	
	
endmodule