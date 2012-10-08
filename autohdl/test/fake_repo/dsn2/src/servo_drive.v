module servo_drive(
	input clk,		// clock 50 Mhz
	input rst,		// reset switch
// To inverter
	output h1,		    // Phase U Hi
	output l1,		    // Phase U Low
	output h2,		    // Phase V Hi
	output l2,		    // Phase V Low
	output h3,		    // Phase W Hi
	output l3,		    // Phase W Low
	output flt_clr,     // Fault Clear
//To sensor	
	input sensA, 	    // Sensor channel A 
	input sensB,	    // Sensor channel B
	input sensR,	    // Sensor channel R
//To Dual SPI ADC board
	input  sdo0_in,  	// ADC 0 SDO
	input  sdo1_in,		// ADC 1 SDO
	output sdi_out,		// ADC 0,1 SDI
	output sclk_out,	// ADC 0,1 SCLK
	output convst,	// ADC 0,1 CONVST	  
//To 8-channel ADC
	input  sdo_in_adc, 			// 8-channel ADC SDO
	output sdi_out_adc,			// 8-channel ADC SDI
	output sclk_out_adc,		// 8-channel ADC SCLK
	output convst_adc,			// 8-channel ADC CONVST	
//RS-232 port	
	output RS_TX,	    // RS-232 External transmitter
	input  RS_RX,  	    // RS-232 External receiver
	
	output RS2_TX,	    // RS-232 External transmitter
	input  RS2_RX,      // RS-232 External receiver	   
//Slave RS-485 port 
	input  slave_485_rx, //Slave 485 input interface	
//Master RS-485 port	  
	output master_485_tx0, //Slave 485 outpur interface	 
	output master_485_tx1, //Slave 485 outpur interface	 
//Leds	
	output [7:0]L,      // 8 LEDS
//Relays and Resistors
	output dc_rly,		// DC_BUS_Relay
	output brk_rly,		// Brake Relay
	output brk_res,		// Brake Resistor	 
//Button
	input cal_btn,		// Calibrate button
	input lft_btn,		// Left button
	input rt_btn,	    // Right button			
//Еmergency sensors
	input end0,			// Emergency end0
	input end1			// Emergency end1
	);	
	
	parameter rs_speed = 434; // 115200kbps
	
	
	wire TX_ENA;			// Transmit enable
	wire [7:0] tx_data;		// Transmit data
	reg TxD_busy;			// Busy of RS232 transmitter
	

	reg [24:0] count;

	always @(posedge clk or posedge rst)
		if(rst)
			count <= 0;
		else
			
			count <= count + 1;
	
wire tx_ready;
	
rs232_tx #(8,rs_speed) rs_tx (.Rst(rst),.Clk(clk),.iCode(tx_data),.iCodeEn(TX_ENA),.oTxD(RS_TX),.oTxDReady(tx_ready));			


assign RS2_TX = RS_TX;

always @(posedge clk, posedge rst)
if(rst)
  TxD_busy <= 0;
else
  if(TX_ENA)
     TxD_busy <= 1;
  else
     if(tx_ready)
        TxD_busy <= 0;
 

	wire [15:0] cmi_data0;		// CMI  Data
	wire [15:0] cmi_data1;		// CMI  Data
	wire [15:0] cmi_data2;		// CMI  Data
	wire [15:0] cmi_data3;		// CMI  Data
	wire 		cmi_strob;	    // CMI  Strob

	
	cmi_coder Coder (.clk(clk),
	.rst(rst),
	.cmi_strob(cmi_strob),
	.cmi_data0(cmi_data0),
	.cmi_data1(cmi_data1),
	.cmi_data2(cmi_data2),
	.cmi_data3(cmi_data3),
	.tx_busy(TxD_busy),
	.tx_data(tx_data),
	.tx_enable(TX_ENA)
	);	
	
	wire RxD_data_ready_;		// READY from RS-232
	wire [7:0] RxD_data ;		// DATA from RS-232
	wire RxD1_data_ready_;		// READY from RS-232
	wire [7:0] RxD1_data ;		// DATA from RS-232
	wire RxD2_data_ready_;		// READY from RS-232
	wire [7:0] RxD2_data ;		// DATA from RS-232
	
	assign RxD_data_ready_ = RxD1_data_ready_ | RxD2_data_ready_;
	
	assign RxD_data = RxD1_data_ready_ ? RxD1_data : RxD2_data;
			
rs232_rx #(8,rs_speed) rs_rx(.Rst(rst),.Clk(clk),.iSerial(RS_RX),.oRxD(RxD1_data),.oRxDReady(RxD1_data_ready_));

rs232_rx #(8,rs_speed) rs2_rx(.Rst(rst),.Clk(clk),.iSerial(RS2_RX),.oRxD(RxD2_data),.oRxDReady(RxD2_data_ready_));
	

	wire [7:0]	param_addr;		// Addr of parameter
	wire [15:0]     param_data;		// Data of parameter
	wire 		param_strob;	// Parameter strob
	
	
	packet_decoder Decoder (
		.clk(clk),
		.rst(rst),
		.rx_ena(RxD_data_ready_),
		.rx_data(RxD_data),
		.param_addr(param_addr),
		.param_data(param_data),
		.param_strob(param_strob)
		);	
	
	wire [31:0] task_in;  		// Значение задание полученное по RS485
	wire task_strob;			// Строб того, что задание пришло
	
	wire [7:0]task485_rx_data;	
	wire task485_rx_rdy;
	
	
	parameter task485_speed = 54; //1 Mbps
	
	rs232_rx #(8,task485_speed) slave485_rx(
		.Rst(rst),
		.Clk(clk),
		.iSerial(slave_485_rx),
		.oRxD(task485_rx_data),
		.oRxDReady(task485_rx_rdy)
		);	
	
	lutch_ust_decoder task_decoder (
		.clk(clk),
		.rst(rst),
		.rx_ena(task485_rx_rdy),
		.rx_data(task485_rx_data),
		.ust_out(task_in),
		.strob_out(task_strob)
	);			 
	
	wire [31:0] task_out0; // Передача уставки наверх
	wire [31:0] task_out1; // Передача уставки наверх
	wire task_out_strob;  // Строб того, что задание пора отправлять
	
	wire [7:0]task485_tx_data0;	
	wire task485_tx_enable0;
	wire task485_tx_rdy0;
	reg task485_tx_busy0;
	
	always @(posedge clk, posedge rst)
		if(rst)
			task485_tx_busy0 <= 0;
		else
			if(task485_tx_enable0)
				task485_tx_busy0 <= 1;
			else
				if(task485_tx_rdy0)
					task485_tx_busy0 <= 0;
	
	
	rs232_tx #(8,task485_speed) master485_tx0 (
		.Rst(rst),
		.Clk(clk),
		.iCode(task485_tx_data0),
		.iCodeEn(task485_tx_enable0),
		.oTxD(master_485_tx0),
		.oTxDReady(task485_tx_rdy0)
	);						  
	
	lutch_ust_former task_coder0 (
		.clk(clk),
		.rst(rst),
		.strob_in(task_out_strob),
		.ust_in(task_out0),
		.tx_busy(task485_tx_busy0),
		.tx_data(task485_tx_data0),
		.tx_enable(task485_tx_enable0)
	);

	wire [7:0]task485_tx_data1;	
	wire task485_tx_enable1;
	wire task485_tx_rdy1;
	reg task485_tx_busy1;
	
	always @(posedge clk, posedge rst)
		if(rst)
			task485_tx_busy1 <= 0;
		else
			if(task485_tx_enable1)
				task485_tx_busy1 <= 1;
			else
				if(task485_tx_rdy1)
					task485_tx_busy1 <= 0;
	
	
	rs232_tx #(8,task485_speed) master485_tx1 (
		.Rst(rst),
		.Clk(clk),
		.iCode(task485_tx_data1),
		.iCodeEn(task485_tx_enable1),
		.oTxD(master_485_tx1),
		.oTxDReady(task485_tx_rdy1)
	);						  
	
	lutch_ust_former task_coder1 (
		.clk(clk),
		.rst(rst),
		.strob_in(task_out_strob),
		.ust_in(task_out1),
		.tx_busy(task485_tx_busy1),
		.tx_data(task485_tx_data1),
		.tx_enable(task485_tx_enable1)
	);
	
	
	parameter sensor_zero = 0;
	parameter resolver_k1h =16'h02C4;
	parameter resolver_k2h =16'h03DD;
	parameter resolver_kdth =16'h007E;
    parameter regulator_hi_eps_k = 22;                   
	parameter regulator_low_eps_k = 19; 
	parameter regulator_k0_int = 3;   
	parameter regulator_k1_int = 5;   
	parameter dfoc_sensor_k = 16'h0178;
	parameter def_dfoc_bias_p = 0;
	parameter def_dfoc_bias_n = 0;	  
	parameter MotorType = 1;

	
	ctrl_drv_servo #(
		.def_dfoc_bias_p(def_dfoc_bias_p),
		.def_dfoc_bias_n(def_dfoc_bias_n),
		.sensor_zero(sensor_zero),
		.resolver_k1h(resolver_k1h),
		.resolver_k2h(resolver_k2h),
		.resolver_kdth(resolver_kdth),
		.regulator_hi_eps_k(regulator_hi_eps_k),
		.regulator_low_eps_k(regulator_low_eps_k),
		.regulator_k0_int(regulator_k0_int),
		.regulator_k1_int(regulator_k1_int),
		.dfoc_sensor_k(dfoc_sensor_k),
		.MotorType(MotorType)
		)

	Drive (
		.clk(clk),
		.rst(rst),
		.sensA(sensA),
		.sensB(sensB),
		.sensR(sensR),
		.h1(h1),
		.l1(l1),
		.h2(h2),
		.l2(l2),
		.h3(h3),
		.l3(l3),  
		.flt_clr(flt_clr),		
		.dc_rly(dc_rly),
		.brk_rly(brk_rly),
		.brk_res(brk_res),
		
		.sdo0_in(sdo0_in),
		.sdo1_in(sdo1_in),
		.sdi_out(sdi_out),
		.sclk_out(sclk_out),
		.convst(convst),

		.sdo_in_adc(sdo_in_adc),
		.sdi_out_adc(sdi_out_adc),
		.sclk_out_adc(sclk_out_adc),
		.convst_adc(convst_adc),
				
		.cmi_data0(cmi_data0),
		.cmi_data1(cmi_data1),
		.cmi_data2(cmi_data2),
		.cmi_data3(cmi_data3),
		.cmi_strob(cmi_strob), 
		.cmi_direction(),
		.param_addr(param_addr),
		.param_data(param_data),
		.param_strob(param_strob),
		.led_out(L),

		.cal_btn(cal_btn),
		.lft_btn(lft_btn),
		.rt_btn(rt_btn),
		
		.task_in(task_in),
	    .task_strob(task_strob),			   
		
		.task_out0(task_out0),
		.task_out1(task_out1),
		.task_out_strob(task_out_strob),
		
		.end0(end0),
		.end1(end1)
		);		   	  
		


endmodule