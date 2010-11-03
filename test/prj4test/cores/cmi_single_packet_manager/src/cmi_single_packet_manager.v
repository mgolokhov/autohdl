module cmi_single_packet_manager(
	input rst, 					//Асинхронный сброс
	input clk,					//Тактовый генератор
	input rx,					//Ножка входа   USART
	output tx,					//Ножка выхода	USART
	input [15:0]width,			//Ширина временного слота в тактах генератора
	input reload,				//Строб обозночающий перезагрузку счетчика отправленной телеметрии
	input [23:0]cmi_count,		//Значение, которое нужно загрузчить в счетчик телметрии при поднятии строба reload
	output marker_st_out,		//Строб по которому надо обновить данный телеметрии
	input  [15:0]cmi_data0_self,//Данные 0 блока телеметрии
	input  [15:0]cmi_data1_self,//Данные 1 блока телеметрии
	input  [15:0]cmi_data2_self,//Данные 2 блока телеметрии
	input  [15:0]cmi_data3_self,//Данные 3 блока телеметрии

	output [7:0] cmi_head_in,	//Заголовок пришедшего пакета
	output [15:0]cmi_data0_in,	//Данные 0 блока пришедщего пакет
	output [15:0]cmi_data1_in,	//Данные 1 блока пришедщего пакет
	output [15:0]cmi_data2_in,	//Данные 2 блока пришедщего пакет
	output [15:0]cmi_data3_in,	//Данные 3 блока пришедщего пакет	  
	output cmi_in_st,			//Строб прихода пакета		
	output cmi_fault			//Флаг того, что пришел битый пакет
	);
	
parameter link_speed = 54;  //Скорость передачи по линиям: 434 - 115200, 54 - 921600
	
//Приемник USART	 
wire [7:0]rx_data;
wire rx_ena;
/*
uart_rx_v2 #(
    .pClkHz(50_000_000),
    .pBaud(921_600),
    .pStopBits(1),
    .pParity(0),
    .pDataWidth(8)
    )
usart_rx (.iClk(clk),
    .iRst(rst),
    .iRxD(rx),
    .oData(rx_data),
    .oDone(rx_ena)
);

*/
rs232_rx #(
	.pWORDw(8),
	.pBitCellCntw(link_speed))
usart_rx (
	.Rst(rst),
	.Clk(clk),
	.iSerial(rx),
	.oRxD(rx_data),
	.oRxDReady(rx_ena)
);		


//Декодер пакетов
cmi_recv_packet recv_packet (
	.clk(clk),
	.rst(rst),
	.rx_ena(rx_ena),
	.rx_data(rx_data),
	.cmi_head(cmi_head_in),
	.cmi_data0(cmi_data0_in),
	.cmi_data1(cmi_data1_in),
	.cmi_data2(cmi_data2_in),
	.cmi_data3(cmi_data3_in),
	.cmi_rdy(cmi_in_st),
	.cmi_fault(cmi_fault),
	.marker_st(),
	.marker_type()
);	

//Генератор временных слотов для отправки пакетов
cmi_single_timeslot_generator single_tsg (
	.rst(rst),
	.clk(clk),
	.width(width),
	.reload(reload),
	.cmi_count(cmi_count),
	.marker_st(marker_st_out)
);

//Формирователь пакетов
reg cmi_send_start;  //Флаг отправки телеметрии. Поднимается через 2 такта после marker_st_out, т.е. после изменения cmi_data0

always @(posedge rst or posedge clk)
	if(rst)
		cmi_send_start <=0;
	else	
		if(marker_st_out)
			cmi_send_start <=1;
		else	
        	cmi_send_start <=0;
			
reg [5:0]seq;		//Номер пакета

always @(posedge rst or posedge clk)
	if(rst)
		seq <= 0;
	else
		if(marker_st_out)
			seq <= seq + 1;
			
wire [7:0]cmi_head_self;  //Заголовк исходящего пакета(содержит секвенцию)			
assign cmi_head_self = {seq,2'b00};

wire [7:0]tx_data;
wire tx_enable;	
wire tx_rdy;
wire tx_busy;

assign tx_busy = ~tx_rdy;

cmi_send_packet send_packet (
	.clk(clk),
	.rst(rst),
	.start(cmi_send_start),
	.cmi_head(cmi_head_self),
	.cmi_data0(cmi_data0_self),
	.cmi_data1(cmi_data1_self),
	.cmi_data2(cmi_data2_self),
	.cmi_data3(cmi_data3_self),
	.tx_busy(tx_busy),
	.tx_data(tx_data),
	.tx_enable(tx_enable),
	.rdy()
);

//Передатчик USART
/*
uart_tx_v2 #(
    .pClkHz(50_000_000),
    .pBaud(921_600),
    .pStopBits(1),
    .pParity(0),
    .pDataWidth(8))
usart_tx (.iRst(rst),
    .iClk(clk),
    .iData(tx_data),
    .iEnStrobe(tx_enable),
    .oTxD(tx),
    .oDone(tx_rdy)
);
*/
rs232_tx #(
	.pWORDw(8),
	.pBitCellCnt(link_speed))
usart_tx (
	.Rst(rst),
	.Clk(clk),
	.iCode(tx_data),
	.iCodeEn(tx_enable),
	.oTxD(tx),
	.oTxDReady(tx_rdy)
);		 

endmodule
