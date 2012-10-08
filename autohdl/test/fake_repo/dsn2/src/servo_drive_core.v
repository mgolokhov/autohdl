module servo_drive_core(
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
	output RS_TX_BUSY,	// RS-232 External transmitter
	output RS2_TX,	    // RS-232 External transmitter
	input  RS2_RX,      // RS-232 External receiver	   	   
	
//Slave RS-485 port 
	input  rs_485_rx_0, //Slave 485 input interface	
	input  rs_485_rx_1, //Slave 485 input interface	
//Master RS-485 port	  
	output rs_485_tx0, //Slave 485 outpur interface	 
	output rs_485_tx1, //Slave 485 outpur interface	 
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
	input end1,			// Emergency end1
	output l0_ok,		// Line 0 link
	output l1_ok		// Line 1 link
	);	
	
	parameter rs_speed = 54; // 115200kbps
	
	
//****************Стробирование входных значений с портов RS-422*********************
//Интерфейс к топу
assign RS2_TX = ~RS_TX;

reg RS_RX_s;

reg RS2_RX_s;

always @(posedge rst, posedge clk)
	if(rst)
		RS_RX_s<=1;
	else
		RS_RX_s<=RS_RX;

always @(posedge rst, posedge clk)
	if(rst)
		RS2_RX_s<=1;
	else
		RS2_RX_s<=RS2_RX;

wire rx_top;			 

wire nRS2_RX_s;	
assign nRS2_RX_s = ~RS2_RX_s; //Инверсия, т.к. RS2 - 485 интерфейс

assign rx_top = RS_RX_s;//&nRS2_RX_s; //Линии топа соеденены через И. Нельзя допускать одновременной передачи

//Интерфейс к линии 0
reg n_rs_485_rx_0_s;
wire rs_485_rx_0_s;	  

wire n_rs_485_tx0;
assign rs_485_tx0 = ~n_rs_485_tx0;

assign rs_485_rx_0_s = ~n_rs_485_rx_0_s;

always @(posedge rst, posedge clk)
	if(rst)
		n_rs_485_rx_0_s<=1;
	else
		n_rs_485_rx_0_s<=rs_485_rx_0;
		
//Интерфейс к линии 1
reg n_rs_485_rx_1_s;
wire rs_485_rx_1_s;	 

wire n_rs_485_tx1;
assign rs_485_tx1 = ~n_rs_485_tx1;

assign rs_485_rx_1_s = ~n_rs_485_rx_1_s;
	
always @(posedge rst, posedge clk)
	if(rst)
		n_rs_485_rx_1_s<=1;
	else
		n_rs_485_rx_1_s<=rs_485_rx_1;					   
		
//******************************************************************************

reg [7:0]  cmi_head;
wire [15:0] cmi_data0;		// CMI  Data
wire [15:0] cmi_data1;		// CMI  Data
wire [15:0] cmi_data2;		// CMI  Data
wire [15:0] cmi_data3;		// CMI  Data

wire [7:0]  cmi_head_recv;
wire [15:0] cmi_data0_recv;		// CMI  Data
wire [15:0] cmi_data1_recv;		// CMI  Data
wire [15:0] cmi_data2_recv;		// CMI  Data
wire [15:0] cmi_data3_recv;		// CMI  Data
wire 		cmi_recv;	    // CMI  Strob
wire 		cmi_fault;	    // CMI  Fault

reg c_r;
reg c_f;	 						  

wire ls;
always @(posedge rst, posedge clk)
	if(rst)
		c_r <=0;
	else	
	if(cmi_recv)
		c_r <= ~ c_r;
		
assign l1_ok = c_r;		

always @(posedge rst, posedge clk)
	if(rst)
		c_f <=0;
	else	
	if(cmi_fault)
		c_f <= ~ c_f;
		
wire [15:0]cmi_timeslot_len;
wire marker_st;
wire cmi_top_out_enable;

parameter cmi_g_mode = 0;

cmi_packet_manager #(
	.link_speed(rs_speed))
packet_manager (
	.rst(rst),
	.clk(clk),
	.cmi_timeslot_len(cmi_timeslot_len),
	.cmi_generator_mode(cmi_g_mode),
	.marker_st_out(marker_st),
	.rx_top(nRS2_RX_s),
	.rx_tech(rx_top),
	.tx_top(RS_TX),
	.rx_0(rs_485_rx_0_s),
	.tx_0(n_rs_485_tx0),
	.rx_1(rs_485_rx_1_s),
	.tx_1(n_rs_485_tx1),
	
	.cmi_fault(cmi_fault),

	.cmi_data0_self(cmi_data0),
	.cmi_data1_self(cmi_data1),
	.cmi_data2_self(cmi_data2),
	.cmi_data3_self(cmi_data3),
	
	.cmi_head_in(cmi_head_recv),
	.cmi_data0_in(cmi_data0_recv),
	.cmi_data1_in(cmi_data1_recv),
	.cmi_data2_in(cmi_data2_recv),
	.cmi_data3_in(cmi_data3_recv),
	.cmi_in_st(cmi_recv),

	.cmi_top_out_enable(cmi_top_out_enable),

	.l0_ok(l0_ok),
	.l1_ok()
);	   

	parameter initial_Kp_i=0;
	parameter initial_Ki_i=0;

	
	parameter sensor_zero = 0;
	parameter resolver_k1h =16'h02C4;
	parameter resolver_k2h =16'h03DD;
	parameter resolver_kdth =16'h007E;
    parameter regulator_hi_eps_k = 22;                   
	parameter regulator_k0_int = 3;   
	parameter regulator_k1_int = 5;   
	parameter dfoc_sensor_k = 16'h0178;	   
	parameter def_dfoc_bias_p = 0;
	parameter def_dfoc_bias_n = 0;
	parameter MotorType = 1;				
	parameter regulator_low_eps_k = 19; 
	parameter calibration_amp =	16'd32000;					   
	parameter calibration_speed = 16'd8000;					   
	parameter end_safe_interval	= 32'd1966080;
	parameter dfoc_regulator_k = 7;
	parameter [1:0]drive_num = 0;

	parameter Kp_s_initial = 0; //Начальное значение коэффициента Kp_s
	parameter Ki_s_initial = 0; //Начальное значение коэффициента Ki_s
	parameter Kd_s_initial = 0; //Начальное значение коэффициента Kd_s
	
	parameter Kp_p_initial = 0; //Начальное значение коэффициента Kp_p
	parameter Ki_p_initial = 0; //Начальное значение коэффициента Ki_p
	parameter Kd_p_initial = 0; //Начальное значение коэффициента Kd_p
	
	parameter max_pos_initial = 400;						   
	parameter aperiodic_dt_initial=-1; //Начальное значение  постоянной времени апериодики

	
	assign RS_TX_BUSY = 0;// cmi_top_out_enable;  //Т.к. ИПС ничего не читает, мы ей ничего и не напишем
	
	ctrl_drv_servo #(	
		.Kp_s_initial(Kp_s_initial),
		.Ki_s_initial(Ki_s_initial),
		.Kd_s_initial(Kd_s_initial),
		.Kp_p_initial(Kp_p_initial),
		.Ki_p_initial(Ki_p_initial),
		.Kd_p_initial(Kd_p_initial),
		.max_pos_initial(max_pos_initial),
		.aperiodic_dt_initial(aperiodic_dt_initial),
							  
		.def_dfoc_bias_p(def_dfoc_bias_p),
		.def_dfoc_bias_n(def_dfoc_bias_n),
		.sensor_zero(sensor_zero),
		.resolver_k1h(resolver_k1h),
		.resolver_k2h(resolver_k2h),
		.resolver_kdth(resolver_kdth),
		.initial_Kp_i(initial_Kp_i),
		.initial_Ki_i(initial_Ki_i),
//		.regulator_hi_eps_k(regulator_hi_eps_k),
//		.regulator_low_eps_k(regulator_low_eps_k),
//		.regulator_k0_int(regulator_k0_int),
//		.regulator_k1_int(regulator_k1_int),
		.dfoc_sensor_k(dfoc_sensor_k),
		.calibration_amp(calibration_amp),
		.calibration_speed(calibration_speed),					   
		.end_safe_interval(end_safe_interval),
		.MotorType(MotorType),
		.dfoc_regulator_k(dfoc_regulator_k),
		.drive_num(drive_num)
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


		.cmi_head_recv(cmi_head_recv),
		.cmi_data0_recv(cmi_data0_recv),
		.cmi_data1_recv(cmi_data1_recv),
		.cmi_data2_recv(cmi_data2_recv),
		.cmi_data3_recv(cmi_data3_recv),
		.cmi_recv(cmi_recv),
		.cmi_fault(cmi_fault),	 
		
		.marker_st(marker_st),
		.cmi_timeslot_len(cmi_timeslot_len),
		.cmi_direction(cmi_top_out_enable),
		
//		.param_addr(param_addr),
//		.param_data(param_data),
//		.param_strob(param_strob),
		.led_out(L),

		.cal_btn(cal_btn),
		.lft_btn(lft_btn),
		.rt_btn(rt_btn),
		
//		.task_in(task_in),
//	    .task_strob(task_strob),			   
		
		.task_out0(),
		.task_out1(),
		.task_out_strob_0(),
		.task_out_strob_1(),
		
		.end0(end0),
		.end1(end1)
	
		);		   	  
		


endmodule