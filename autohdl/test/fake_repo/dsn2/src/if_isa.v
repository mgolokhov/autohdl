`default_nettype none
//
//		Module:		if_isa
//		Version:	0.1
//		Project:	cd_isa
//		FPGA:		Xilinx Spartan3S200 tq144
//  	Board:		hw_isa
//		Author:		Serge V. Kior
//		Testbench:	-none-
//		Repositary:	http://dev.sign4tech.com/svn/SCIRCUS/hdl/cd_isa
//		Wiki:		http://dev.sign4tech.com:8080/confluence/display/SCVAM/if_isa
//

module if_isa
	(
	input			clk_in,				//Вход тактовой частоты
	input			rst_in,				//Вход сброса
	inout	[7:0]	isa_data_io,		//двунаправленный интерфейс  данных ISA 
	output			isa_tr_data_out,	//перевод направления внешних буферов
	input			isa_aen_in,			//сигнал готовности адреса ISA 
	input	[9:0]	isa_addr_in, 		//шина адреса ISA 
	input			isa_iow_in,			//Запись в порт по ISA 
	input			isa_ior_in,			//чтение из порта по ISA 
	output	[15:0]	pdu_0_status_out,	//выход для привода ТП-1
	output	[15:0]	pdu_1_status_out,	//выход для привода ТП-2
	output	[15:0]	pdu_2_status_out,	//выход для привода ТП-3
	output	[15:0]	pdu_3_status_out,	//выход для привода ТП-4
	output	[13:0]	leds_out,			//выходы на индикаторы 
	input	[13:0]	keys_in,			//Входы от кнопок пульта управления
	input	[15:0]	ca0_stat_in,		//Статус командоаппарата ТП-1  
	input	[15:0]	ca1_stat_in,		//Статус командоаппарата ТП-2
	input	[15:0]	ca2_stat_in,		//Статус командоаппарата ТП-3  
	input	[15:0]	ca3_stat_in,		//Статус командоаппарата ТП-4  
	input	[31:0]	sensor0_in,			//Текущее положение ТП-1 
	input	[31:0]	sensor1_in,			//Текущее положение ТП-2
	input	[31:0]	sensor2_in,			//Текущее положение ТП-3 
	input	[31:0]	sensor3_in,			//Текущее положение ТП-4 
	input	[11:0]	ai0_in, 			//положение потенциометра ТП-1 	
	input	[11:0]	ai1_in, 			//положение потенциометра ТП-2
	input	[11:0]	ai2_in, 			//положение потенциометра ТП-3 
	input	[11:0]	ai3_in, 			//положение потенциометра ТП-4 
	input	[11:0]	ai4_in 			//положение потенциометра ГП 
	);
	
	`define STEP_IOW 11
	`define STEP_IOR 26
	`define ADDR_RST 10'h100
	`define ADDR_PROC 10'h101
	
	wire iow_str_l2h;
	
	strobing_l2h  isa_iow_str_l2h (.Rst(rst_in),
		.Clk(clk_in),
		.unstrobed(isa_iow_in),
		.strobed(iow_str_l2h)
		);
	
	wire iow_str_h2l;
	
	strobing_l2h  isa_iow_str_h2l (.Rst(rst_in),
		.Clk(clk_in),
		.unstrobed(~isa_iow_in),
		.strobed(iow_str_h2l)
		);
	
	wire ior_str_l2h;
	
	strobing_l2h  isa_ior_str_l2h (.Rst(rst_in),
		.Clk(clk_in),
		.unstrobed(isa_ior_in),
		.strobed(ior_str_l2h)
		);
	
	wire ior_str_h2l;
	
	strobing_l2h  isa_ior_str_h2l (.Rst(rst_in),
		.Clk(clk_in),
		.unstrobed(~isa_ior_in),
		.strobed(ior_str_h2l)
		);
	
	reg isa_tr_data_out_;
	wire [7:0] isa_data_read; 
	//высокий-прием, низкий-передача
	assign isa_data_io = !isa_tr_data_out_ ? isa_data_read : 8'bzzzz_zzzz;
	
	reg [3:0] CntStepIow; //
	
	reg [7:0] wData0;
	reg [7:0] wData1;
	reg [7:0] wData2;
	reg [7:0] wData3;
	reg [7:0] wData4;
	reg [7:0] wData5;
	reg [7:0] wData6;
	reg [7:0] wData7;
	reg [7:0] wData8;
	reg [7:0] wData9;
	
	
	always @(posedge clk_in, posedge rst_in) begin
			if(rst_in) 
				isa_tr_data_out_ <= 0;
			else begin
					//write mode
					if (iow_str_h2l || ior_str_l2h) isa_tr_data_out_ <= 1;
					//read mode
					else if (ior_str_h2l) isa_tr_data_out_ <= 0; 
				end
		end
	assign isa_tr_data_out = isa_tr_data_out_;
	
	reg stop_write;
	always @(posedge clk_in, posedge rst_in) begin
			if (rst_in) begin
					CntStepIow <= 0;
					wData0 <= 0;
					wData1 <= 0;
					wData2 <= 0;
					wData3 <= 0;
					wData4 <= 0;
					wData5 <= 0;
					wData6 <= 0;
					wData7 <= 0;
					wData8 <= 0;
					wData9 <= 0;
					stop_write <= 0;
				end
			else if (iow_str_l2h) begin
					if (isa_addr_in == `ADDR_RST) begin
							CntStepIow <= 0;
//							wData0 <= 0;
//							wData1 <= 0;
//							wData2 <= 0;
//							wData3 <= 0;
//							wData4 <= 0;
//							wData5 <= 0;
//							wData6 <= 0;
//							wData7 <= 0;
//							wData8 <= 0;
//							wData9 <= 0;
							stop_write <= 0;
						end
					else if (isa_addr_in == `ADDR_PROC)begin
						if (CntStepIow == `STEP_IOW-1)
							stop_write <= 1;
							//	CntStepIow <= 0;
							else if(!stop_write) begin
									CntStepIow <= CntStepIow + 1;
									{wData9,wData8,wData7,wData6,wData5,wData4,wData3,wData2,wData1,wData0}
									<=
									{isa_data_io,wData9,wData8,wData7,wData6,wData5,wData4,wData3,wData2,wData1};
								end
						end
				end
		end
	
	reg [4:0] CntStepIor;
	reg [7:0] rData0;
	reg [7:0] rData1;
	reg [7:0] rData2;
	reg [7:0] rData3;
	reg [7:0] rData4;
	reg [7:0] rData5;
	reg [7:0] rData6;
	reg [7:0] rData7;
	reg [7:0] rData8;
	reg [7:0] rData9;
	reg [7:0] rData10;
	reg [7:0] rData11;
	reg [7:0] rData12;
	reg [7:0] rData13;
	reg [7:0] rData14;
	reg [7:0] rData15;
	reg [7:0] rData16;
	reg [7:0] rData17;
	reg [7:0] rData18;
	reg [7:0] rData19;
	reg [7:0] rData20;
	reg [7:0] rData21;
	reg [7:0] rData22;
	reg [7:0] rData23;
	reg [7:0] rData24;
	reg [7:0] rData25;
	
	reg ior_str_h2l_delay;
	always @(posedge clk_in, posedge rst_in)begin
			if (rst_in) ior_str_h2l_delay <= 0;
			else ior_str_h2l_delay <= ior_str_h2l;
		end
	
	
	reg on;
	always @(posedge clk_in, posedge rst_in)begin
			if (rst_in) begin
					CntStepIor <= 0; 
					//on <= 0;
					rData0 <= 0;
					rData1 <= 0;
					rData2 <= 0;
					rData3 <= 0;
					rData4 <= 0;
					rData5 <= 0;
					rData6 <= 0;
					rData7 <= 0;
					rData8 <= 0;
					rData9 <= 0;
					rData10 <= 0;
					rData11 <= 0;
					rData12 <= 0;
					rData13 <= 0;
					rData14 <= 0;
					rData15 <= 0;
					rData16 <= 0;
					rData17 <= 0;
					rData18 <= 0;
					rData19 <= 0;
					rData20 <= 0;
					rData21 <= 0;
					rData22 <= 0;
					rData23 <= 0;
					rData24 <= 0;
					rData25 <= 0;
				end
			else if (ior_str_l2h) begin
					if (isa_addr_in == `ADDR_RST) begin
							CntStepIor <= 0;
							//on <= 0;
							rData0 <= keys_in[7:0]; 	 
							rData1 <= {2'b00,keys_in[13:8]}; //остальные 0 
							rData2 <= ca0_stat_in[7:0]; 	 
							rData3 <= ca0_stat_in[15:8]; 	 
							rData4 <= ca1_stat_in[7:0]; 	 
							rData5 <= ca1_stat_in[15:8]; 	 
							rData6 <= ca2_stat_in[7:0]; 	 
							rData7 <= ca2_stat_in[15:8]; 	 
							rData8 <= ca3_stat_in[7:0]; 	 
							rData9 <= ca3_stat_in[15:8]; 	 
							rData10 <= sensor0_in[7:0]; 	 
							rData11 <= sensor0_in[15:8]; 	 
							rData12 <= sensor0_in[23:16]; 	 
							rData13 <= sensor0_in[31:24]; 	 
							rData14 <= sensor1_in[7:0];  	 
							rData15 <= sensor1_in[15:8]; 	 
							rData16 <= sensor1_in[23:16];  	 
							rData17 <= sensor1_in[31:24]; 	 
							rData18 <= sensor2_in[7:0];  	 
							rData19 <= sensor2_in[15:8]; 	 
							rData20 <= sensor2_in[23:16];  	 
							rData21 <= sensor2_in[31:24]; 	 
							rData22 <= sensor3_in[7:0];  	 
							rData23 <= sensor3_in[15:8]; 	 
							rData24 <= sensor3_in[23:16];  	 
							rData25 <= sensor3_in[31:24];
						end
					else if (isa_addr_in == `ADDR_PROC)begin
							//on <= 1;
							if (CntStepIor == `STEP_IOR-1)
								CntStepIor <= 0;
							else
								if (on) begin
									CntStepIor <= CntStepIor + 1;
									{
									rData25,rData24,rData23,rData22,rData21,
									rData20,rData19,rData18,rData17,rData16,
									rData15,rData14,rData13,rData12,rData11,
									rData10, rData9, rData8, rData7, rData6,
									rData5,  rData4, rData3, rData2, rData1,
									rData0
									} <= 
									{
									8'h0   ,rData25,rData24,rData23,rData22,
									rData21,rData20,rData19,rData18,rData17,
									rData16,rData15,rData14,rData13,rData12,
									rData11,rData10, rData9, rData8, rData7,
									rData6,  rData5, rData4, rData3, rData2,
									rData1
									};
								end
						end
				end
		end
	
	always	@(posedge clk_in, posedge rst_in)begin
			if(rst_in) on <= 0;
			//else if(CntStepIor == `STEP_IOR-1) on <= 0;
			else if(isa_addr_in == `ADDR_PROC) on <= 1;
			else on <= 0;
		end
	
	assign	isa_data_read = on ? rData0 : 8'h0;
	
	
	
	assign leds_out[7:0] = wData0;	 
	assign leds_out[13:8] = wData1; //	остальные 0 
	assign pdu_0_status_out[7:0] = wData2; 	 
	assign pdu_0_status_out[15:8] = wData3;	 
	assign pdu_1_status_out[7:0] = wData4;	 
	assign pdu_1_status_out[15:8] = wData5;	 
	assign pdu_2_status_out[7:0] = wData6;	 
	assign pdu_2_status_out[15:8] = wData7;	 
	assign pdu_3_status_out[7:0] = wData8; 
	assign pdu_3_status_out[15:8] = wData9; 
	
endmodule