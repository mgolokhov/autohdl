`default_nettype none
module ctrlv3500_test_firmware(
	// System signals
	input clk_in,
	input rst_in,
	
	// LITTLE-USB inouts
	input usb_rx_in,
	output usb_tx_out,
	
	// SWITCH BOX INTERFACE
	input [1:0] box_in,
	output [1:0] box_out,
	
	// MEZONIN UARTS
	inout uart1_tx_out,
	inout uart1_rx_in,
	inout uart2_tx_out,
	inout uart2_rx_in,
	
	
	///----- CONTROL ONE INTERFACE
	
	// DAC SPI Interface
	output dac1_load_out,
	output dac1_clk_out,
	output dac1_sdi_out,
	
	// Control interface output 
	output [4:0] ctrl1_out,
	
	// RS485 Half duplex interface
	output	rs485_tx1_out,
	output	rs485_de1_out,
	input 	rs485_rx1_in,
	
	///----- CONTROL TWO INTERFACE
	
	// DAC SPI Interface
	output dac2_load_out,
	output dac2_clk_out,
	output dac2_sdi_out,
	
	// Control interface output
	output [4:0] ctrl2_out,
	
	// RS485 Half duplex interface
	output	rs485_tx2_out,
	output	rs485_de2_out,
	input 	rs485_rx2_in,
	
	///--- RS422 interface
	input rs422_rx1_in,
	input rs422_rx2_in,
	input rs422_rx3_in,
	output rs422_tx3_out,
	output rs422_de3_out,
	input rs422_rx4_in,
	output rs422_tx4_out,
	output rs422_de4_out,
	input rs422_rx5_in,
	input rs422_rx6_in,
	input rs422_rx7_in,
	output rs422_tx7_out,
	output rs422_de7_out,
	input rs422_rx8_in,
	output rs422_tx8_out,
	output rs422_de8_out,
	
	input rs422_ext_rx1_in,
	output rs422_ext_tx1_out,
	output rs422_ext_de1_out,
	input rs422_ext_rx2_in,
	output rs422_ext_tx2_out,
	output rs422_ext_de2_out,
	input rs422_ext_rx3_in,
	input rs422_ext_rx4_in,
	
	input [19:0] dig_in,
	
	output [20:0] dig_out,
	
	output [5:0] ssr_out,
	
	// ADC 8 chanel
	
	output adc_dout,
	output adc_sclk_out,
	input  adc_din,
	output adc_con_out,
	
	input [5:0] expm_in,
	inout [15:0] expm_io
	
	);

	assign usb_tx_out = usb_rx_in;
	
	
	reg f10_mhz;	// Strob 10 Mhz
	reg [7:0] f_counter; // Counter for Strob generator
	
	wire clk;
	assign clk = clk_in;
	
	wire rst;
	assign rst = ~rst_in;
	
	always @(posedge clk, posedge rst)
		if(rst)
			begin
				f10_mhz <= 0;
				f_counter <= 0;
			end
		else
			begin
				if(f_counter == 0)
					begin
						f10_mhz <= 1;
						f_counter <= 40;
					end
				else
					begin
						f10_mhz <= 0;
						f_counter <= f_counter - 1;
					end
				
			end
			
wire [7:0] box_data;			
			
switchbox_reader sw_reader (.clk(clk),
	.rst(rst),
	.data_in(box_in),
	.addr_out(box_out),
	.data_out(box_data)
);	
	
	
	wire [3:0] cmd_K;	// ����� �������:
	//0 - �������� �� ������ ������������ ��� �������� �������� ��� ������� SSR
	//1 - �������� �� ������ ������������ ��� �������� �������� ��� ������� DOUT1-DOUT21
	//2 - �������� �� ������ ������������ ��� �������� �������� ��� ������� DOUT1-DOUT5 (CTRL1)
	//3 - �������� �� ������ ������������ ��� �������� �������� ��� ������� DOUT1-DOUT5 (CTRL2) 
	//4 - �������� "����� 1" * � �������� �� ������ ������������ ��� �������� �������� ��� ������������ RS422, EXT1-EXT2, EXTM1-EXTM22
	//5 - �������� "����� 2" * � �������� �� ������ ������������ ��� �������� �������� ��� ������� EXT1-EXT4
	//6 - �������� �� ������ ������������ ��� �������� �������� ��� ��������������� �������� ��� ��� 
	assign cmd_K = 0;
	
	wire [15:0] cmd_d;	// �������� 16��� 
	assign cmd_d = 1;
	
	wire [2:0] cmd_a;	// ����� ��� (0 - 1 �����, 1 - 2 �����, 2 - 3 �����, ...) 
	assign cmd_a = 0;
	
	wire cmd_Z;			// ����������� ��� �������������� ������ ��������� ������� ��� ���:
	// "0" - ������ ��������
	// "1" - ������ �� ��� 
	
	assign cmd_Z = 0;
	
	wire cmd_strob;		// ����� �� �������� ���� ������ ������
	assign cmd_strob = 0;
	
	
	reg RS422_Mode;			   	// ����� RS422
	reg [15:0] SSR_prescaler;	// �������� ��� SSR
	reg [15:0] DOUT_prescaler;	// �������� ��� DOUT
	reg [15:0] CTRL1_prescaler;	// �������� ��� CTRL1
	reg [15:0] CTRL2_prescaler;	// �������� ��� CTRL2
	reg [15:0] EXT_prescaler; 	// �������� ��� EXT
	reg [15:0] DAC_prescaler;	// �������� ��� DAC	 
	
	reg [2:0] ch_adc;  
	reg dac_mode;
	

	reg dout_mode;
	
	always @(posedge clk, posedge rst)
		if(rst)
			begin
				RS422_Mode <= 0;
				ch_adc <= 0;  
				dac_mode <= 1;
				SSR_prescaler <= 0;
				DOUT_prescaler <= 0;
				CTRL1_prescaler <= 0;
				CTRL2_prescaler <= 0;
				EXT_prescaler <= 0;
				DAC_prescaler <= 0;
				
			end
		else
			begin
				DOUT_prescaler <= 10;
				SSR_prescaler <= 10000;
				CTRL1_prescaler <= 10;
				CTRL2_prescaler <= 10;
				dout_mode <= box_data[3];
				RS422_Mode <= box_data[4];
			end
					
	
	// TELEMETRY
	// begin
	// ...
	// end
	
	
	// ADC in	  
	
	wire [11:0] value_out0;
	wire [11:0] value_out1;
	wire [11:0] value_out2;
	wire [11:0] value_out3;
	wire [11:0] value_out4;
	wire [11:0] value_out5;
	wire [11:0] value_out6;
	wire [11:0] value_out7;
	
	
	reg [19:0] strob_counter;
	reg counter_strob;
	
	always @(posedge clk_in or posedge rst)
		if(rst)
			begin
				counter_strob <= 0;
				strob_counter <= 0;	
			end
		else
			begin
				{counter_strob,strob_counter} <= strob_counter + 1;
			end				
	
	adc_spi_conv test_adc (.clk(clk),
		.rst(rst),
//		.chanel_in(0),
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
		.finish()
		);
	
	// ADC Selector
	reg [11:0] ADC_out;
	
	always @(posedge clk, posedge rst)
		if(rst)
			ADC_out <= 0;
		else
			case (box_data[2:0])
				0: ADC_out <= value_out0;
				1: ADC_out <= value_out1;
				2: ADC_out <= value_out2;
				3: ADC_out <= value_out3;
				4: ADC_out <= value_out4;
				5: ADC_out <= value_out5;
				6: ADC_out <= value_out6;
				7: ADC_out <= value_out7;
			endcase
	
	
	// DAC Counter
	reg [10:0] dac_counter;
	reg [15:0] dac_presc_counter;
	
	always @(posedge clk, posedge rst)
		if(rst)
			begin
				dac_counter <= 0;
				dac_presc_counter <= 0;
			end
		else 
			if(f10_mhz)
				begin
					if(dac_presc_counter == 0)
						begin
							dac_presc_counter <= DAC_prescaler;
							dac_counter <= dac_counter + 1;
						end
					else
						begin
							dac_presc_counter <= dac_presc_counter - 1;
						end
				end
	
	// DAC Out former
	reg [9:0] DAC_out;
	
	always @(posedge clk, posedge rst)
		if(rst)
			begin	   
				DAC_out <= 0;
			end
		else
			begin
				if(dac_mode)
					begin // dac_mode == 1
						DAC_out <= ADC_out[11:2];
					end
				else
					begin // dac_mode == 0
						DAC_out <= dac_counter;
					end
				
			end
	
	wire   	dac_sdi_out;
	wire 	dac_clk_out;
	wire 	dac_ld_out;
	
	spi_master #(
		.w_length(10),
		.clk_div(14),
		.inv_clk(1))
		DAC_SPI_MASTER (.clk(clk),
		.rst(rst),
		.value_in(DAC_out),
		.strob_in(counter_strob),
		.sdi_out(dac_sdi_out),
		.sdo_in(1'b0),
		.sclk_out(dac_clk_out),
		.load_out(dac_ld_out)
		);
	
	assign dac1_sdi_out = ~dac_sdi_out;
	assign dac1_clk_out = ~dac_clk_out;
	assign dac1_load_out = dac_ld_out;	
	
	assign dac2_sdi_out = ~dac_sdi_out;
	assign dac2_clk_out = ~dac_clk_out;
	assign dac2_load_out = dac_ld_out;	
	
	
	// SSR Counter
	reg ssr_counter;
	reg [15:0] ssr_presc_counter;
	
	always @(posedge clk, posedge rst)
		if(rst)
			begin
				ssr_counter <= 0;
				ssr_presc_counter <= 0;
			end
		else  
			if(f10_mhz)
				begin
					if(ssr_presc_counter == 0)
						begin
							ssr_presc_counter <= SSR_prescaler;
							ssr_counter <= ssr_counter + 1;
						end
					else
						begin
							ssr_presc_counter <= ssr_presc_counter - 1;
						end
				end
	
	// SSR Former
	
	reg [5:0] SSR_out;
	
	always @(posedge clk, posedge rst)
		if(rst)
			SSR_out <= 0;
		else
			SSR_out <= {ssr_counter,ssr_counter,ssr_counter,ssr_counter,ssr_counter,ssr_counter}; 
	
	assign 	ssr_out =  SSR_out;
	
	
	// DOUT Counter
	reg dout_counter;
	reg [15:0] dout_presc_counter;
	
	always @(posedge clk, posedge rst)
		if(rst)
			begin
				dout_counter <= 0;
				dout_presc_counter <= 0;
			end
		else  
			if(f10_mhz)
				begin
					if(dout_presc_counter == 0)
						begin
							dout_presc_counter <= DOUT_prescaler;
							dout_counter <= dout_counter + 1;
						end
					else
						begin
							dout_presc_counter <= dout_presc_counter - 1;
						end
				end
	
	// DOUT Former
	
	reg [20:0] DOUT_out;
	
	always @(posedge clk, posedge rst)
		if(rst)
			DOUT_out <= 0;
		else
			if(dout_mode)
				DOUT_out <= dig_in;
			else
				DOUT_out <= {dout_counter,dout_counter,dout_counter,dout_counter,dout_counter,dout_counter,
					dout_counter,dout_counter,dout_counter,dout_counter,dout_counter,dout_counter,dout_counter,dout_counter,
					dout_counter,dout_counter,dout_counter,dout_counter,dout_counter,dout_counter,dout_counter}; 
	
	assign 	dig_out =  DOUT_out;	
	
	
	// CTRL1 Counter
	reg ctrl1_counter;
	reg [15:0] ctrl1_presc_counter;
	
	always @(posedge clk, posedge rst)
		if(rst)
			begin
				ctrl1_counter <= 0;
				ctrl1_presc_counter <= 0;
			end
		else  
			if(f10_mhz)
				begin
					if(ctrl1_presc_counter == 0)
						begin
							ctrl1_presc_counter <= CTRL1_prescaler;
							ctrl1_counter <= ctrl1_counter + 1;
						end
					else
						begin
							ctrl1_presc_counter <= ctrl1_presc_counter - 1;
						end
				end
	
	// CTRL1 Former
	
	reg [4:0] CTRL1_out;
	
	always @(posedge clk, posedge rst)
		if(rst)
			CTRL1_out <= 0;
		else
			CTRL1_out <= {ctrl1_counter,ctrl1_counter,ctrl1_counter,ctrl1_counter,ctrl1_counter}; 
	
	assign 	ctrl1_out =  CTRL1_out;	
	
	// CTRL2 Counter
	reg ctrl2_counter;
	reg [15:0] ctrl2_presc_counter;
	
	always @(posedge clk, posedge rst)
		if(rst)
			begin
				ctrl2_counter <= 0;
				ctrl2_presc_counter <= 0;
			end
		else  
			if(f10_mhz)
				begin
					if(ctrl2_presc_counter == 0)
						begin
							ctrl2_presc_counter <= CTRL2_prescaler;
							ctrl2_counter <= ctrl2_counter + 1;
						end
					else
						begin
							ctrl2_presc_counter <= ctrl2_presc_counter - 1;
						end
				end
	
	// CTRL2 Former
	
	reg [4:0] CTRL2_out;
	
	always @(posedge clk, posedge rst)
		if(rst)
			CTRL2_out <= 0;
		else
			CTRL2_out <= {ctrl2_counter,ctrl2_counter,ctrl2_counter,ctrl2_counter,ctrl2_counter}; 
	
	assign 	ctrl2_out =  CTRL2_out;		
	
	
	// EXT Former
	reg ext_counter;
	reg [15:0] ext_presc_counter;
	
	always @(posedge clk, posedge rst)
		if(rst)
			begin
				ext_counter <= 0;
				ext_presc_counter <= 0;
			end
		else  
			if(f10_mhz)
				begin
					if(ext_presc_counter == 0)
						begin
							ext_presc_counter <= EXT_prescaler;
							ext_counter <= ext_counter + 1;
						end
					else
						begin
							ext_presc_counter <= ext_presc_counter - 1;
						end
				end
	
	// EXT Former
	
	assign uart1_tx_out = ext_counter;
	assign  uart1_rx_in = ext_counter;
	assign  uart2_tx_out = ext_counter;
	assign  uart2_rx_in = ext_counter;
	
	// RS Former
	
	wire de;
	assign de = ~	RS422_Mode;
	
	
	// RS485 Half duplex interface
	assign  rs485_tx1_out = ext_counter;
	
	assign  rs485_de1_out = de;
	
	// RS485 Half duplex interface
	assign  rs485_tx2_out = ext_counter;
	assign  rs485_de2_out = de;
	
	///--- RS422 interface
	assign  rs422_tx3_out = ext_counter;
	assign  rs422_de3_out = de;
	assign  rs422_tx4_out = ext_counter;
	assign  rs422_de4_out = de;
	assign  rs422_tx7_out = ext_counter;
	assign  rs422_de7_out = de;
	assign  rs422_tx8_out = ext_counter;
	assign  rs422_de8_out = de;
	
	assign  rs422_ext_tx1_out = ext_counter;
	assign  rs422_ext_de1_out = de;
	assign  rs422_ext_tx2_out = ext_counter;
	assign  rs422_ext_de2_out = de;
	

	assign 	expm_io[0] = RS422_Mode ? rs422_rx1_in :  ext_counter;
	assign 	expm_io[1] = RS422_Mode ? rs422_rx2_in :  ext_counter;
	assign 	expm_io[2] = RS422_Mode ? rs422_rx3_in :  ext_counter;
	assign 	expm_io[3] = RS422_Mode ? rs422_rx4_in :  ext_counter;
	assign 	expm_io[4] = RS422_Mode ? rs422_rx5_in :  ext_counter;
	assign 	expm_io[5] = RS422_Mode ? rs422_rx6_in :  ext_counter;
	assign 	expm_io[6] = RS422_Mode ? rs422_rx7_in :  ext_counter;
	assign 	expm_io[7] = RS422_Mode ? rs422_rx8_in :  ext_counter;
	assign 	expm_io[8] = RS422_Mode ? rs422_ext_rx1_in :  ext_counter;
	assign 	expm_io[9] = RS422_Mode ? rs422_ext_rx2_in :  ext_counter;
	assign 	expm_io[10] = RS422_Mode ? rs422_ext_rx3_in :  ext_counter;
	assign 	expm_io[11] = RS422_Mode ? rs422_ext_rx4_in :  ext_counter;
	assign 	expm_io[12] = RS422_Mode ? rs485_rx2_in :  ext_counter;
	assign 	expm_io[13] = RS422_Mode ? 0 :  ext_counter;
	assign 	expm_io[14] = RS422_Mode ? 0 :  ext_counter;
	assign 	expm_io[15] = RS422_Mode ? 0 :  ext_counter;
	



endmodule
