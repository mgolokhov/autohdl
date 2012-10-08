`default_nettype none
module ctrl_v2_sovr
	(
	// Global Inputs
	// Used.
	input	clk_in,			// Clock 50 Mhz
	input	rst_in, 		// Reset Active High
	
	// LITTLE-USB Serial Interface
	// Not used in this design
	input	usb_rx_in,		// LITLE_USB Receiver
	output	usb_tx_out,		// LITTLE_USB Tranceiver
	
	// SWITCH BOX 
	// Not used in this design
	input	[1:0]	box_in, // Box input signals
	output	[1:0]	box_out,// Box multiplexers signals
	
	// Lyminaries ARM interface
	// Used: uart1_tx_out, 	 uart1_rx_in  
	
	output	uart1_tx_out,	// UART1 Transmitter
	input	uart1_rx_in,	// UART1 Receiver
	output	uart2_tx_out,	// UART2 Transmitter
	input	uart2_rx_in,	// UART2 Receiver
	
	// ===> Control Interface #1
	
	//  1.1 DAC
	//  Used
	output	dac1_load_out,	// LOAD signal
	output	dac1_clk_out,	// CLK signal
	output	dac1_sdi_out,	// SDI signal
	
	// 1.2 DISCRETTE OUTPUTS
	// ctrl1_out[4] not used
	output	[4:0] ctrl1_out,
	
	// 1.3 RS485 Interface
	// Not used in this design
	output	rs485_tx1_out,	// Transmitter
	output	rs485_de1_out,	// TX_ENABLE
	input	rs485_rx1_in,	// Receiver
	
	// ===> Control Interface #2
	
	//  2.1 DAC
	// Not used
	output	dac2_load_out,	// LOAD signal
	output	dac2_clk_out,	// CLK signal
	output	dac2_sdi_out,	// SDI signal
	
	// 2.2 DISCRETTE OUTPUTS
	// Not used
	output	[4:0] ctrl2_out,
	
	// 2.3 RS485 Interface
	// Not used
	output	rs485_tx2_out,	// Transmitter
	output	rs485_de2_out,	// TX_ENABLE Active High
	input	rs485_rx2_in,	// Receiver
	
	// ===> RS422 Sensor Interfaces
	
	// Channel #1
	// Used
	input rs422_rx1_in,		// Receiver
	
	// Channel #2
	// Used
	input rs422_rx2_in,		// Receiver
	
	// Channel #3
	// Not used
	input 	rs422_rx3_in,	// Receiver
	output	rs422_tx3_out,	// Transmitter
	output	rs422_de3_out,	// TX_Enable
	
	// Channel #4
	// 	Not used
	input 	rs422_rx4_in,	// Receiver
	output	rs422_tx4_out,	// Transmitter
	output	rs422_de4_out,	// TX_Enable
	
	// Channel #5
	// Used
	input rs422_rx5_in,		// Receiver
	
	// Channel #6
	// Used
	input rs422_rx6_in,		// Receiver
	
	// Channel #7
	// Not used 
	input 	rs422_rx7_in,	// Receiver
	output	rs422_tx7_out,	// Transmitter
	output	rs422_de7_out,	// TX_Enable
	
	// Channel #8
	// Not used 
	input 	rs422_rx8_in,	// Receiver
	output	rs422_tx8_out,	// Transmitter
	output	rs422_de8_out,	// TX_Enable
	
	// ===> RS422 External Interfaces
	
	// Channel #1
	// Not used 
	input 	rs422_ext_rx1_in,	// Receiver
	output	rs422_ext_tx1_out,	// Transmitter
	output	rs422_ext_de1_out,	// TX_Enable
	
	// Channel #2
	// Not used 
	input 	rs422_ext_rx2_in,	// Receiver
	output	rs422_ext_tx2_out,	// Transmitter
	output	rs422_ext_de2_out,	// TX_Enable
	
	// Channel #3
	// Used 
	input rs422_ext_rx3_in,		// Receiver
	
	// Channel #4
	// Used
	input rs422_ext_rx4_in,		// Receiver
	
	// Digital inputs General Purpose
	// Used : [0],[1],[2],[3],[5],[7],
	input	[23:0]	dig_in,		// 
	
	// Digital outputs General Purpose
	// Not used
	output	[20:0]	dig_out,	//
	
	// Solid state outputs General Purpose
	// Not used 
	output	[5:0]	ssr_out,	//
	
	// Analog to Digital Convertor AD7812
	// Not used 
	output	adc_dout,			// SPI DO
	output	adc_sclk_out,		// SPI SCK
	input	adc_din,			// SPI DI
	output	adc_con_out,		// ADC CONVERT
	
	// Expantion slot
	// Not Used 
	input	[3:0]	exp_in,		//  Expantion Inputs
	output	[11:0] 	exp_io		//	Expantion bidirectional
	);
	
	wire clk;		// Internal clock
	wire rst;		// Internal reset
	
	assign clk = clk_in;
	assign rst = ~rst_in;



	// Определение внутренних цепей

	wire key1_md;		// Переключение местного и дистанционного управления
	wire key1_on;		// Кнопка включения привода
	wire key1_left;		// Вращение влево
	wire key1_off;		// Кнопка выключения привода
	wire key1_right;	// Вращение вправо
	wire key1_lock;		// Запрещение местного управления
	// 
	wire led1_link;		// Связь
	wire led1_rmt;		// Дистанционное управление
	wire led1_on;		// Активное состояние
	wire led1_local;	// Местное управление
	wire led1_alarm;	// Авария
	wire led1_24v;		// +24В
	wire [9:0] speed_1;	// Скорость
	
	//
	wire pwr1;		// Включение частотника
	wire left1;		// STF
	wire right1;		// STR

	//
	wire key2_md;		// Переключение местного и дистанционного управления
	wire key2_on;		// Кнопка включения привода
	wire key2_left;		// Вращение влево
	wire key2_off;		// Кнопка выключения привода
	wire key2_right;	// Вращение вправо
	wire key2_lock;		// Запрещение местного управления
	// 
	wire led2_link;		// Связь
	wire led2_rmt;		// Дистанционное управление
	wire led2_on;		// Активное состояние
	wire led2_local;	// Местное управление
	wire led2_alarm;	// Авария
	wire led2_24v;		// +24В
	wire [9:0] speed_2;	// Скорость
	
	//
	wire pwr2;		// Включение частотника
	wire left2;		// STF
	wire right2;		// STR
		
	// Назначения входов и выходов
	// Первый привод
	assign key1_md	  = ~dig_in[15];	// Переключение местного и дистанционного управления
	assign key1_on	  = ~dig_in[19];	// Кнопка включения привода
	assign key1_left  = ~dig_in[21];	// Вращение влево
	assign key1_off   = ~dig_in[23];	// Кнопка выключения привода
	assign key1_right = ~dig_in[12];	// Вращение вправо
	assign key1_lock  = ~dig_in[1];		// Запрещение местного управления   
	// 
	assign dig_out[4]  = led1_link;		// Связь
	assign dig_out[2]  = led1_rmt;		// Дистанционное управление
	assign dig_out[0]  = led1_on;		// Активное состояние
	assign dig_out[5]  = led1_local;	// Местное управление
	assign dig_out[3]  = led1_alarm;	// Авария
	assign dig_out[1]  = led1_24v;		// +24В

	assign ssr_out[0] = pwr1;		// Включение частотника
	assign ssr_out[2] = left1;		// STF
	assign ssr_out[3] = right1;		// STR

	// Второй привод
	assign key2_md    = ~dig_in[13];	// Переключение местного и дистанционного управления
	assign key2_on    = ~dig_in[14];	// Кнопка включения привода
	assign key2_left  = ~dig_in[18];	// Вращение влево
	assign key2_off   = ~dig_in[20];	// Кнопка выключения привода
	assign key2_right = ~dig_in[22];	// Вращение вправо
	assign key2_lock  = ~dig_in[11];	// Запрещение местного управления
	// 
	assign dig_out[9]  = led2_link;		// Связь
	assign dig_out[11] = led2_rmt;		// Дистанционное управление
	assign dig_out[8]  = led2_on;		// Активное состояние
	assign dig_out[10] = led2_local;	// Местное управление
	assign dig_out[12] = led2_alarm;	// Авария
	assign dig_out[13] = led2_24v;		// +24В
	
	//
	assign ssr_out[1] = pwr2;		// Включение частотника
	assign ssr_out[4] = left2;		// STF
	assign ssr_out[5] = right2;		// STR

	
	
	wire f100;		// F100 Signal
	
	// Module generates strob with 10 ms (f = 100 Hz) period
	// Verified: OK
	f100_generator 
		F100 (.clk_in(clk),
		.rst_in(rst),
		.f100_out(f100)
		);	
			
			
	wire [15:0] mpu_status1;	// MPU - local control panel Status Word 

	wire [15:0] mpu_status2;
	
	wire [15:0] pdu_status1;	// PDU - remote control panel
	wire [15:0] pdu_status2;
	
	wire [15:0] ka_status1;		// KA - command apparate
	wire [15:0] ka_status2;		// KA - command apparate
	
	wire  rx1_1_active;
	wire  rx1_2_active;
	wire  rx2_1_active;
	wire  rx2_2_active;
	
	wire [31:0] pos1;
	wire [31:0] pos2;
	
	wire [15:0] vel1;
	wire [15:0] vel2;
	
	/*
	
	if_enc  position1 (
		.clk_in(clk),
		.rst_in(rst),
		.k1_in(rs422_rx1_in),
		.k2_in(rs422_rx2_in),
		.k3_in(rs422_rx5_in),
		.clear_value_in(1'b0),
		.value_out(pos1),
		.speed_out(vel1),
		.divider(80000000) // waz 20000000
		);
	*/
	
		   
	/*
	if_enc position2(
		.clk_in(clk),
		.rst_in(rst),
		.k1_in(rs422_ext_rx3_in),
		.k2_in(rs422_ext_rx4_in),
		.k3_in(rs422_rx6_in),
		.clear_value_in(1'b0),
		.value_out(pos2),
		.speed_out(vel2),
		.divider(10000000) // waz 10000000 20000000
		);
	*/
	wire [15:0] speed;	
	wire [15:0] speed2;
	wire speed_strob;
	
	
	reg [13:0] speed_cnt;
	reg [13:0] speed_cnt2;
	reg [7:0] ccc1;
 	reg dirr;
 	reg dirr2;
	
	always @(posedge clk, posedge rst)
		if(rst)
			begin
				dirr <= 0;
				speed_cnt <= 0;
			end
		else
			if(speed_strob)
			begin
				if(speed[15])
					begin // otriz
						dirr <= 1;	   
							speed_cnt <= -speed[15:1];
					end
				else
					begin // pol
						dirr <= 0;
							speed_cnt <= speed[15:1];
					end

			end

	always @(posedge clk, posedge rst)
		if(rst)
			begin
				dirr2 <= 0;
				speed_cnt2 <= 0;
			end
		else
			if(speed_strob)
			begin
				if(speed2[15])
					begin // otriz
						dirr2 <= 1;	   
							speed_cnt2 <= -speed2[15:1];
					end
				else
					begin // pol
						dirr2 <= 0;
							speed_cnt2 <= speed2[15:1];
					end
			end
	
	//	assign pdu_status1 = {speed_cnt[12:1],~dirr,dirr,2'b1};
	
	reg [15:0]pdu1;
	reg [15:0]pdu2;
	
	always @(posedge clk, posedge rst)
	if(rst)
		pdu1 <= 0;
	else
		pdu1 <= {speed_cnt[13:2],~dirr,dirr,2'b1};
			

	assign pdu_status1 = pdu1;

	always @(posedge clk, posedge rst)
	if(rst)
		pdu2 <= 0;
	else
		pdu2 <= {speed_cnt2[13:2],~dirr2,dirr2,2'b1};

	assign pdu_status2 = pdu2; 	
	
	
	// ADC Converter

	wire [11:0] value_out0;
	wire [11:0] value_out1;
	wire [11:0] value_out2;
	wire [11:0] value_out3;
	wire [11:0] value_out4;
	wire [11:0] value_out5;
	wire [11:0] value_out6;
	wire [11:0] value_out7;
	
	adc_spi_conv ADC (.clk(clk),
		.rst(rst),
		.strob_in(f100),
		.sdi_out(adc_dout),
		.sdo_in(adc_din),
		.sclk_out(adc_sclk_out),
		.conv_out(adc_con_out),
		.value_out0(value_out0),
		.value_out1(value_out1),
		.value_out2(value_out2),
		.value_out3(value_out3),
		.value_out4(value_out4),
		.value_out5(value_out5),
		.value_out6(value_out6),
		.value_out7(value_out7),
		.finish()
		);


	// Sensor 1  SSI
	assign  rs422_de4_out = 1;
//	assign  rs422_tx4_out = 1;
      
	assign  rs422_de3_out = 1;
	assign  rs422_tx3_out = 1;
	
	wire [31:0] pos_gray1;
	wire g_ready1;
	
	ssi SSI1(
	.clk(clk),				// Клок 50 Mhz
		 .rst(rst),				// Ресет активный высокий
		 .ssi_clk_out(rs422_tx4_out),			// Выход на SSI клок
		 .ssi_data_in(rs422_rx1_in),			// Вход данных от SSI
		 .read_in(f100),			// Строб запроса датчика
		 .data_out(pos_gray1),		// Выход данных
		 .data_ready(g_ready1)			// Готовность данных
		 ) ;
		 
	gray2bin g2b1(
		 .clk(clk),				// Клок 50 Mhz
		.rst(rst),				// Ресет активный высокий
		.read_in(g_ready1),			// Строб запроса датчика
		.gray_in(pos_gray1),
		.data_out(pos1),		// Выход данных
		.data_ready()			// Готовность данных
				 ) ;		 
	
//	assign pos1 = pos_gray1;
/*	reg [31:0] p1;
	
	always @(posedge clk, posedge rst)
	if(rst)
	  p1 <= 0;
	else
	  if(f100)
	    p1 <= p1 + 1;
		 
	assign pos1 = p1;*/
	// Sensor 2  SSI
	assign  rs422_de8_out = 1;
//	assign  rs422_tx8_out = 1;
      
	assign  rs422_de7_out = 1;
	assign  rs422_tx7_out = 1;


	wire [31:0] pos_gray2;
	wire g_ready2;
	
	ssi SSI2(
	.clk(clk),				// Клок 50 Mhz
		 .rst(rst),				// Ресет активный высокий
		 .ssi_clk_out(rs422_tx8_out),			// Выход на SSI клок
		 .ssi_data_in(rs422_rx5_in),			// Вход данных от SSI
		 .read_in(f100),			// Строб запроса датчика
		 .data_out(pos_gray2),		// Выход данных
		 .data_ready(g_ready2)			// Готовность данных
		 ) ;

		 gray2bin g2b2(
		 .clk(clk),				// Клок 50 Mhz
		.rst(rst),				// Ресет активный высокий
		.read_in(g_ready2),			// Строб запроса датчика
		.gray_in(pos_gray2),
		.data_out(pos2),		// Выход данных
		.data_ready()			// Готовность данных
		);
		
		//assign pos2 = pos_gray2;
		 
		 /*
		 reg [31:0] p2;
	
	always @(posedge clk, posedge rst)
	if(rst)
	  p2 <= 0;
	else
	  if(f100)
	    p2 <= p2 - 1;
	  
	  assign pos2 = p2;*/
	// Sensor NM 1

	// Sensor NM 2
	
	// MPU1

 if_mpu MPU1(
	.clk_in(clk),
	.rst_in(rst),
	.mpu_btn_on_in(key1_on),	// Кнопка выключения
	.mpu_btn_off_in(key1_off),	// Кнопка выключения
	.mpu_btn_mudu_in(key1_md),	// Кнопка переключения с местного на дистанционный
	.mpu_btn_up_in(key1_left),	// Кнопка вверх
	.mpu_btn_down_in(key1_right),	// Кнопка вниз
	.mpu_led_on_out(led1_on),
	.mpu_led_mu_out(led1_local),	// LED Местное
	.mpu_led_du_out(led1_rmt),	// LED Дистанционное
	.mpu_led_link_out(led1_link),// LED Связь
	.mpu_led_kva_out(led1_alarm), // LED Авария
	.speed_in(value_out7),		
	.ka_status_in(ka_status1),	
	.mpu_status_out(mpu_status1),
	.f100_in(f100)
	);

pwm V24PWM (
  .clk(clk),
  .rst(rst),
  .val_in(value_out7),
  .pwm_out(led1_24v)
);

	
//	assign led1_24v = key1_lock;
	
	// MPU2
 if_mpu MPU2(
	.clk_in(clk),
	.rst_in(rst),
	.mpu_btn_on_in(key2_on),	// Кнопка выключения
	.mpu_btn_off_in(key2_off),	// Кнопка выключения
	.mpu_btn_mudu_in(key2_md),	// Кнопка переключения с местного на дистанционный
	.mpu_btn_up_in(key2_left),	// Кнопка вверх
	.mpu_btn_down_in(key2_right),	// Кнопка вниз
	.mpu_led_on_out(led2_on),
	.mpu_led_mu_out(led2_local),	// LED Местное
	.mpu_led_du_out(led2_rmt),	// LED Дистанционное
	.mpu_led_link_out(led2_link),// LED Связь
	.mpu_led_kva_out(led2_alarm), // LED Авария
	.speed_in(value_out6),		
	.ka_status_in(ka_status1),	
	.mpu_status_out(mpu_status2),
	.f100_in(f100)		
	);

pwm V24PWM2 (
  .clk(clk),
  .rst(rst),
  .val_in(value_out6),
  .pwm_out(led2_24v)
);
	
	// Drive 1

	if_ca ca (
		.clk_in(clk),
		.rst_in(rst),
		.kv_ru_in(1'b0),
		.kv_a_u_in(0),
		.kv_a_d_in(0),
		.kv_w_u_in(0),
		.kv_w_d_in(0),
		.kv_ss_u_in(0),
		.kv_ss_d_in(0),
		.ka_status_out(ka_status1)
		);

	//  DAC Interface
	
	wire dac1_sdi;
	wire dac1_clk;
	wire dac1_load;
	
	wire pwr1t;
	
	if_drv DRIVE1 (
		.clk_in(clk),
		.rst_in(rst),
		.f100_in(f100),
		.mpu_status_in(mpu_status1),
		.pdu_status_in(pdu_status1),
		.ka_status_in(ka_status1),
		.stf_out(left1),
		.str_out(right1),
		.stop_out(pwr1t),
		.rl_out(),
		.dac_ld_out(dac1_load),
		.dac_clk_out(dac1_clk),
		.dac_sdi_out(dac1_sdi)
		);						  
			
	assign pwr1 = ~pwr1t;
	
	assign dac1_sdi_out = ~dac1_sdi;
	assign dac1_clk_out = ~dac1_clk;
	assign dac1_load_out = dac1_load;
	
	// Drive 2
	//  DAC Interface
	
	wire dac2_sdi;
	wire dac2_clk;
	wire dac2_load;
	
	wire pwr2t;
	
	if_drv DRIVE2 (
		.clk_in(clk),
		.rst_in(rst),
		.f100_in(f100),
		.mpu_status_in(mpu_status2),
		.pdu_status_in(pdu_status2),
		.ka_status_in(ka_status1),
		.stf_out(left2),
		.str_out(right2),
		.stop_out(pwr2t),
		.rl_out(),
		.dac_ld_out(dac2_load),
		.dac_clk_out(dac2_clk),
		.dac_sdi_out(dac2_sdi)
		);						  
			
	assign pwr2 = ~pwr2t;
	
	assign dac2_sdi_out = ~dac2_sdi;
	assign dac2_clk_out = ~dac2_clk;
	assign dac2_load_out = dac2_load;

	// LYM2CTRL IF
	wire [7:0] RxD1_rs232;
	wire RxDReady1_rs232;
	
	rs232_rx #(
		.pWORDw(8),
		.pBitCellCntw(31))
		rs232_rx1 (
		.Rst(rst),
		.Clk(clk),
		.iSerial(uart1_rx_in),
		.oRxD(RxD1_rs232),
		.oRxDReady(RxDReady1_rs232)
		); 
	
	karet_usp_decoder decoder(
		.clk(clk),			// CLK 60 Mhz
		.rst(rst),			// Reset
		.rx_ena(RxDReady1_rs232),	// RS232 recevie Enable signal
		.rx_data(RxD1_rs232),		// RS232 received data
		.speed(speed),			// Parameter Address
		.speed2(speed2),
		.speed_strob(speed_strob)	// Parameter Value
		);
	
	
	wire oTxDReady;
	wire tx_enable;
	wire [7:0] tx_data;
	reg tx_busy;
	always @(posedge clk, posedge rst)
		if(rst)
			tx_busy <= 0;
		else
			if(tx_enable)
				tx_busy <= 1;
			else
				if(oTxDReady)
					tx_busy <= 0;
	
	wire cmi_busy;
	wire cmi_strob;
	
	wire [7:0] S;
	wire [15:0] D;
	wire [15:0] Q;
	
	reg [15:0] vell;
	
	always @(posedge clk, posedge rst)
		if(rst)
			vell <= 0;
		else
			if(f100)
				vell <= vell + 99;
	
	karet_cmi_former Former(
		.clk(clk),					// 60 Mhz clock
		.rst(rst),					// Reset
		.f100_strob(f100),				// Strob to send cmi
		
		.speed_z(vel2),		// Z-coord speed
		.speed_y(vel1), 		// Z-coord speed
		
		.pos_z(pos2),		// Z-coord position
		.pos_y(pos1),		// Y-coord position
		.rps({dig_in[7],dig_in[5]}),		// Reper Position Sensors
		.cmi_busy(cmi_busy),		// CMI_sender busy flag
		.S(S),		// Sequence field
		.D(D),		// Data field
		.Q(Q),		// Second Data field
		.cmi_strob(cmi_strob),		// Strob to send next cmi
		.ca_status_in(ka_status1)
		);
	
	
	karet_cmi_coder cmi_coder(
		.clk(clk),					// 60 Mhz clock
		.rst(rst),					// Reset
		.cmi_strob(cmi_strob),				// Strob to send cmi
		.packet_counter(S),
		.cmi_data(D),			// d
		.cmi_data2(Q),         // q
		.tx_busy(tx_busy),					// TX busy flag
		.tx_data(tx_data),		// transmit data
		.tx_enable(tx_enable),			// transmit enable
		.cmi_busy(cmi_busy)
		);
	
	
	
	rs232_tx #(
		.pWORDw(8),
		.pBitCellCnt(31))
		tx (
		.Rst(rst),
		.Clk(clk_in),
		.iCode(tx_data),
		.iCodeEn(tx_enable),
		.oTxD(uart1_tx_out),
		.oTxDReady(oTxDReady)
		);
	

	//assign uart1_tx_out = 1;
	// CTRL2LYM IF
	



	// Assign unASsigned pins 
	
	wire de_all;
	assign de_all = 1;
	assign {usb_tx_out, box_out, ctrl1_out, rs485_de1_out,rs422_ext_de1_out,ctrl2_out} = 0;

	assign exp_io = 0;
	assign rs485_de2_out = 0;
	assign rs485_tx1_out = 0;
	assign rs422_ext_de2_out = 0;
	assign rs422_ext_tx1_out = 0;
	assign dig_out[20] = 0;
	assign dig_out[14] = 0;
	assign dig_out[15] = 0;
	assign rs485_tx2_out = 0;
	assign dig_out[6] = 0;
	assign dig_out[16] = 0;
	assign dig_out[7] = 0;
	assign dig_out[17] = 0;
	assign dig_out[18] = 0;
	assign dig_out[19] = 0;
	assign rs422_ext_tx2_out = 0;
	assign uart2_tx_out = 1;
	
	
endmodule
