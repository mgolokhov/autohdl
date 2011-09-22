`default_nettype none
module vakhdsp_hw_ctrl_v2
	(
	// Global Inputs
	
	input	clk_in,	// Clock 50 Mhz
	input	rst_in, // Reset Active High
	
	// LITTLE-USB Serial Interface
	
	input	usb_rx_in,	// LITLE_USB Receiver
	output	usb_tx_out,	// LITTLE_USB Tranceiver
	
	// SWITCH BOX 
	
	input	[1:0]	box_in, // Box input signals
	output	[1:0]	box_out,// Box multiplexers signals
	
	// Lyminaries ARM interface
	
	output	uart1_tx_out,	// UART1 Transmitter
	input	uart1_rx_in,	// UART1 Receiver
	output	uart2_tx_out,	// UART2 Transmitter
	input	uart2_rx_in,	// UART2 Receiver
	
	// ===> Control Interface #1
	
	//  1.1 DAC
	
	output	dac1_load_out,	// LOAD signal
	output	dac1_clk_out,	// CLK signal
	output	dac1_sdi_out,	// SDI signal
	
	// 1.2 DISCRETTE OUTPUTS
	
	output	[4:0] ctrl1_out,
	
	// 1.3 RS485 Interface
	
	output	rs485_tx1_out,	// Transmitter
	output	rs485_de1_out,	// TX_ENABLE
	input	rs485_rx1_in,	// Receiver
	
	// ===> Control Interface #2
	
	//  2.1 DAC
	
	output	dac2_load_out,	// LOAD signal
	output	dac2_clk_out,	// CLK signal
	output	dac2_sdi_out,	// SDI signal
	
	// 2.2 DISCRETTE OUTPUTS
	
	output	[4:0] ctrl2_out,
	
	// 2.3 RS485 Interface
	
	output	rs485_tx2_out,	// Transmitter
	output	rs485_de2_out,	// TX_ENABLE Active High
	input	rs485_rx2_in,	// Receiver
	
	// ===> RS422 Sensor Interfaces
	
	// Channel #1
	
	input rs422_rx1_in,		// Receiver
	
	// Channel #2
	
	input rs422_rx2_in,		// Receiver
	
	// Channel #3
	
	input 	rs422_rx3_in,	// Receiver
	output	rs422_tx3_out,	// Transmitter
	output	rs422_de3_out,	// TX_Enable
	
	// Channel #4
	
	input 	rs422_rx4_in,	// Receiver
	output	rs422_tx4_out,	// Transmitter
	output	rs422_de4_out,	// TX_Enable
	
	// Channel #5
	
	input rs422_rx5_in,		// Receiver
	
	// Channel #6
	
	input rs422_rx6_in,		// Receiver
	
	// Channel #7
	
	input 	rs422_rx7_in,	// Receiver
	output	rs422_tx7_out,	// Transmitter
	output	rs422_de7_out,	// TX_Enable
	
	// Channel #8
	
	input 	rs422_rx8_in,	// Receiver
	output	rs422_tx8_out,	// Transmitter
	output	rs422_de8_out,	// TX_Enable
	
	// ===> RS422 External Interfaces
	
	// Channel #1
	
	input 	rs422_ext_rx1_in,	// Receiver
	output	rs422_ext_tx1_out,	// Transmitter
	output	rs422_ext_de1_out,	// TX_Enable
	
	// Channel #2
	
	input 	rs422_ext_rx2_in,	// Receiver
	output	rs422_ext_tx2_out,	// Transmitter
	output	rs422_ext_de2_out,	// TX_Enable
	
	// Channel #3
	
	input rs422_ext_rx3_in,		// Receiver
	
	// Channel #4
	
	input rs422_ext_rx4_in,		// Receiver
	
	// Digital inputs General Purpose
	
	input	[23:0]	dig_in,		// 
	
	// Digital outputs General Purpose
	
	output	[20:0]	dig_out,	//
	
	// Solid state outputs General Purpose
	
	output	[5:0]	ssr_out,	//
	
	// Analog to Digital Convertor AD7812
	output	adc_dout,			// SPI DO
	output	adc_sclk_out,		// SPI SCK
	input	adc_din,			// SPI DI
	output	adc_con_out,		// ADC CONVERT
	
	// Expantion slot
	input	[3:0]	exp_in,		//  Expantion Inputs
	output	[11:0] 	exp_io		//	Expantion bidirectional
	);
	
	wire clk;
	wire rst;
	
	wire f100;
	
	
f100_generator 
F100 (.clk_in(clk),
	.rst_in(rst),
	.f100_out(f100)
);	
	
	assign clk = clk_in;
	assign rst = ~rst_in;
	
	wire [7:0] sw_box_data;
	wire [9:0] v_in;
	
	
	reg [32:0] counter;
	reg [19:0] strob_counter;
	reg counter_strob;
	
	always @(posedge clk_in or posedge rst)
		if(rst)
			begin
				counter <= 0;
				counter_strob <= 0;
				strob_counter <= 0;
			end
		else
			begin
				counter <= counter + 1;
				{counter_strob,strob_counter} <= strob_counter + 1;
			end
	
	wire test = counter[19];
	
	
	// Assign all outputs to one 
	
	
		
wire [15:0] mpu_status1;
assign mpu_status1 = 2;  	// Distance Control
wire [15:0] pdu_status1;
wire [15:0] ka_status1;	
assign ka_status1 = 0;		// BUGAGA Must be controlled


wire [15:0] mpu_status2;
assign mpu_status2 = 2;  	// Distance Control
wire [15:0] pdu_status2;
wire [15:0] ka_status2;	
assign ka_status1 = 0;		// BUGAGA Must be controlled

wire  rx1_1_active;
wire  rx1_2_active;
wire  rx2_1_active;
wire  rx2_2_active;

wire [31:0] enc_value1;
wire [31:0] enc_value2;

if_enc 
encoder1 (
	.clk_in(clk),
	.rst_in(rst),
	.k1_in(rs422_rx1_in),
	.k2_in(rs422_rx2_in),
	.k3_in(1'b0),
	.clear_value_in(1'b0),
	.value_out(enc_value1)
);


if_enc 
encoder2 (
	.clk_in(clk),
	.rst_in(rst),
	.k1_in(rs422_rx5_in),
	.k2_in(rs422_rx6_in),
	.k3_in(1'b0),
	.clear_value_in(1'b0),
	.value_out(enc_value2)
);


if_pdu2ctrl_rx2 pdu2ctrl_rx1 (
		.clk_in(clk),
		.rst_in(rst),
		.rs_rx_1_in(rs422_ext_rx3_in),
		.rs_rx_2_in(rs422_ext_rx3_in),
		
		.pdu_status_out(pdu_status1),
		.rx_1_active_out (rx1_1_active),
		.rx_2_active_out(rx1_2_active)
		);

if_pdu2ctrl_rx2 pdu2ctrl_rx2 (
		.clk_in(clk),
		.rst_in(rst),
		.rs_rx_1_in(rs422_ext_rx4_in),
		.rs_rx_2_in(rs422_ext_rx4_in),
		
		.pdu_status_out(pdu_status2),
		.rx_1_active_out (rx2_1_active),
		.rx_2_active_out(rx2_2_active)
		);
		
		
		
	if_ctrl2pdu_tx ctrl2pdu_tx1 (
		.clk_in(clk),
		.rst_in(rst),
		.iF100_str(f100),
		.mpu_status_in(mpu_status1[1:0]),
		.enc_in(enc_value1),
		.rx_1_active_in(rx1_1_active),
		.rx_2_active_in(rx1_2_active),
		.stf_in(ctrl1_out[0]),
		.str_in(ctrl1_out[1]),
		.stop_in(ctrl1_out[2]),
		.ka_status_in(ka_status1),
		.rs_tx_out(rs422_ext_tx1_out)
		);
		
	if_ctrl2pdu_tx ctrl2pdu_tx2 (
		.clk_in(clk),
		.rst_in(rst),
		.iF100_str(f100),
		.mpu_status_in(mpu_status2[1:0]),
		.enc_in(enc_value2),
		.rx_1_active_in(rx2_1_active),
		.rx_2_active_in(rx2_2_active),
		.stf_in(ctrl2_out[0]),
		.str_in(ctrl2_out[1]),
		.stop_in(ctrl2_out[2]),
		.ka_status_in(ka_status2),
		.rs_tx_out(rs422_ext_tx2_out)
		);
		
		


	//  DAC Interface
	
	wire dac1_sdi;
	wire dac1_clk;
	wire dac1_load;

		
if_drv DRIVE1 (
    .clk_in(clk),
	.rst_in(rst),
	.f100_in(f100),
	.mpu_status_in(mpu_status1),
	.pdu_status_in(pdu_status1),
	.ka_status_in(ka_status1),
	.stf_out(ctrl1_out[0]),
	.str_out(ctrl1_out[1]),
	.stop_out(ctrl1_out[2]),
	.rl_out(ctrl1_out[3]),
	.dac_ld_out(dac1_load),
	.dac_clk_out(dac1_clk),
	.dac_sdi_out(dac1_sdi)
);	

assign ctrl1_out[4] = 0;	
	
	assign dac1_sdi_out = ~dac1_sdi;
	assign dac1_clk_out = ~dac1_clk;
	assign dac1_load_out = dac1_load;
	
	
	//
	wire dac2_sdi;
	wire dac2_clk;
	wire dac2_load;
	
	
if_drv DRIVE2 (
    .clk_in(clk),
	.rst_in(rst),
	.f100_in(f100),
	.mpu_status_in(mpu_status2),
	.pdu_status_in(pdu_status2),
	.ka_status_in(ka_status2),
	.stf_out(ctrl2_out[0]),
	.str_out(ctrl2_out[1]),
	.stop_out(ctrl2_out[2]),
	.rl_out(ctrl2_out[3]),
	.dac_ld_out(dac2_load),
	.dac_clk_out(dac2_clk),
	.dac_sdi_out(dac2_sdi)
);		
assign ctrl2_out[4] = 0;	
	
	assign dac2_sdi_out = ~dac2_sdi;
	assign dac2_clk_out = ~dac2_clk;
	assign dac2_load_out = dac2_load;
	
	
	//
	
	//
	reg usb_tx;
	
	assign usb_tx_out = usb_tx;	 
	
	
	always @(posedge clk, posedge rst)
		if(rst)
			usb_tx <= 0;
		else
			case (sw_box_data)
				0: usb_tx <= uart1_rx_in;
				1: usb_tx <= uart2_rx_in;
				2: usb_tx <= rs485_rx1_in;
				3: usb_tx <= rs485_rx2_in;
				4: usb_tx <= rs422_rx1_in;
				5: usb_tx <= rs422_rx2_in;
				6: usb_tx <= rs422_rx3_in;
				7: usb_tx <= rs422_rx4_in;
				8: usb_tx <= rs422_rx5_in;
				9: usb_tx <= rs422_rx6_in;
				10: usb_tx <= rs422_rx7_in;
				11: usb_tx <= rs422_rx8_in;
				12: usb_tx <= rs422_ext_rx1_in;
				13: usb_tx <= rs422_ext_rx2_in;
				14: usb_tx <= rs422_ext_rx3_in;
				15: usb_tx <= rs422_ext_rx4_in;
				
				default: usb_tx <= usb_rx_in;
				endcase
	
	wire de_all;
	assign de_all = 1;
	
	
	assign rs485_tx1_out = usb_rx_in;
	assign rs485_de1_out = de_all;

	assign rs485_tx2_out = usb_rx_in;
	assign rs485_de2_out = de_all;


	assign uart1_tx_out = usb_rx_in;
	assign uart2_tx_out = usb_rx_in;
	
	assign	rs422_tx3_out = usb_rx_in;
	assign	rs422_de3_out = de_all;
	assign	rs422_tx4_out = usb_rx_in;
	assign	rs422_de4_out = de_all;
	assign	rs422_tx7_out = usb_rx_in;
	assign	rs422_de7_out = de_all;
	assign	rs422_tx8_out = usb_rx_in;
	assign	rs422_de8_out = de_all;
	
	//
//	assign	rs422_ext_tx1_out = usb_rx_in;
	assign	rs422_ext_de1_out = de_all;
//	assign	rs422_ext_tx2_out = usb_rx_in;
	assign	rs422_ext_de2_out = de_all;
	
	//21
	assign dig_out[6:0] = dig_in[6:0];
	assign dig_out[20:15] = dig_in[20:15];
	
	
	
	//6
	assign ssr_out = {test,test,test,test,test,test};
	
	// 
	
	
	wire [11:0] value_out0;
	wire [11:0] value_out1;
	wire [11:0] value_out2;
	wire [11:0] value_out3;
	wire [11:0] value_out4;
	wire [11:0] value_out5;
	wire [11:0] value_out6;
	wire [11:0] value_out7;
	
	adc_spi_conv test_adc (.clk(clk),
		.rst(rst),
		.chanel_in(sw_box_data[2:0]),
		.strob_in(counter_strob),
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
		.finish(exp_io[11])
		);
	
	assign v_in = value_out0[11:2];
	
	
	
	switchbox_reader sw_box (
		.clk(clk_in),
		.rst(rst),
		.data_in(box_in),
		.addr_out(box_out),
		.data_out(sw_box_data)
		
		);
		
	assign dig_out[14:7] = 0;
	assign exp_io[10:0] = value_out0;
	
endmodule
