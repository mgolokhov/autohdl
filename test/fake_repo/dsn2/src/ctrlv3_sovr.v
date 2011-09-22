`default_nettype none
module ctrlv3_sovr(
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
	assign key1_md	  = dig_in[11];		// Переключение местного и дистанционного управления
	assign key1_on	  = dig_in[5];		// Кнопка включения привода
	assign key1_left  = dig_in[15];		// Вращение влево
	assign key1_off   = dig_in[17];		// Кнопка выключения привода
	assign key1_right = dig_in[8];		// Вращение вправо
	assign key1_lock  = dig_in[1];		// Запрещение местного управления
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
	assign key2_md    = dig_in[9];		// Переключение местного и дистанционного управления
	assign key2_on    = dig_in[10];		// Кнопка включения привода
	assign key2_left  = dig_in[12];		// Вращение влево
	assign key2_off   = dig_in[14];		// Кнопка выключения привода
	assign key2_right = dig_in[16];	// Вращение вправо
	assign key2_lock  = dig_in[19];		// Запрещение местного управления
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

	// F100 
	wire clk;		// Internal clock
	wire rst;		// Internal reset
	
	assign clk = clk_in;
	assign rst = ~rst_in;
	
	wire f100;		// F100 Signal
	
	// Module generates strob with 10 ms (f = 100 Hz) period
	// Verified: OK
	f100_generator 
		F100 (.clk_in(clk),
		.rst_in(rst),
		.f100_out(f100)
		);	
	
	  
	reg [15:0] counter;

	always @(posedge clk, posedge rst)
	if(rst)
	  counter <= 0;
	else 
		if(f100)
	  		counter <= counter + 1;
	// ADC Converter

	assign adc_dout     = 0;
	assign adc_sclk_out = 0;
	assign adc_con_out  = 0;

	// Sensor 1  SSI
	assign  rs422_de4_out = 1;
	assign  rs422_tx4_out = 1;
      
	assign  rs422_de3_out = 1;
	assign  rs422_tx3_out = 1;
	// Sensor 2  SSI
	assign  rs422_de8_out = 1;
	assign  rs422_tx8_out = 1;
      
	assign  rs422_de7_out = 1;
	assign  rs422_tx7_out = 1;

	// Sensor NM 1

	// Sensor NM 2
	
	// MPU1
	assign led1_link = counter[15];
	assign led1_rmt = counter[14];
	assign led1_on = counter[13];
	assign led1_local = counter[12];
	assign led1_alarm = counter[11];
	assign led1_24v = counter[10];
	
	// MPU2
	assign led2_link = counter[9];
	assign led2_rmt = counter[8];
	assign led2_on = counter[7];
	assign led2_local = counter[6];
	assign led2_alarm = counter[5];
	assign led2_24v = counter[4];
	
	// Drive 1
	assign pwr1 = 1;
	assign left1 = 1;
	assign right1 = 1;

	assign dac1_load_out  = 1;
	assign dac1_clk_out = 1;
	assign dac1_sdi_out = 1;
	
	// Drive 2
	assign pwr2 = 1;
	assign left2 = 1;
	assign right2 = 1;
	
	assign dac2_load_out  = 1;
	assign dac2_clk_out = 1;
	assign dac2_sdi_out = 1;

	// LYM2CTRL IF
	
	// CTRL2LYM IF
	
	// Unused Pins 
	assign {usb_tx_out, box_out, ctrl1_out, rs485_de1_out,rs422_ext_de1_out,ctrl2_out} = 0;

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

	
endmodule
