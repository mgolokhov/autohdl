module cmi_packet_manager(
	input rst, 	//Сброс
	input clk,  //Тактовый генератор
	
	input [15:0]cmi_timeslot_len,		//Ширина временного слота
	input cmi_generator_mode,			//Режим работы генератора 0 - внутренний, 1 - внешний
	
	output marker_st_out, 				//Строб прихода маркера
	
	//Контроллер верхнего уровня	
	input  rx_top,						//Ножка RX приемника линии топ
	input  rx_tech,	
	output reg tx_top,			     	//Ножка TX приемника линии топ	  
	//Контроллер по линии 0
	input  rx_0,						//Ножка RX приемника линии топ
	output reg tx_0,			     	//Ножка TX приемника линии топ
	//Контроллер по линии 1
	input  rx_1,						//Ножка RX приемника линии топ
	output reg tx_1,			     	//Ножка TX приемника линии топ
	output cmi_fault,   			// Ошибка при приеме пакета от контроллера верхнего уровня
	
	input [15:0]cmi_data0_self,			//0  канал телеметрии (обновляется по marker_st)
	input [15:0]cmi_data1_self,			//1  канал телеметрии (обновляется по marker_st)
	input [15:0]cmi_data2_self,			//2  канал телеметрии (обновляется по marker_st)
	input [15:0]cmi_data3_self,			//3  канал телеметрии (обновляется по marker_st)

	input  cmi_top_out_enable,		    //Разрешение на отправку пакетов топу
	
	output [7:0] cmi_head_in,			//Заголовок пришедшего пакета
	output [15:0]cmi_data0_in,			//Блок данных 0 прищедшего пакета
	output [15:0]cmi_data1_in,			//Блок данных 1 прищедшего пакета
	output [15:0]cmi_data2_in,	    	//Блок данных 2 прищедшего пакета
	output [15:0]cmi_data3_in,			//Блок данных 3 прищедшего пакета
	output cmi_in_st,					//Строб прихода пакета

	output l0_ok,  					//Целостность линии 0
	output l1_ok					//Целостность линии 1	   	
	
	);
	
parameter link_speed = 54;  //Скорость передачи по линиям: 434 - 115200, 54 - 921600

//*******************Приемники	каналов**********************
//Канал TOP
wire marker_st_0;
wire [1:0]marker_type_0;

wire rx_ena_top;
wire [7:0]rx_data_top;
wire rx_ena_tech;
wire [7:0]rx_data_tech;
wire rx_ena;
wire [7:0]rx_data;	

wire cmi_received;  //Строб прихода телеметрии. Поднимается в тот момент, когда пакет принят. В отличии от строба cmi_in_st, который поднимается, когда телеметрия ретранслируется

assign rx_ena = rx_ena_top | rx_ena_tech;				 	
assign rx_data = (rx_ena_top) ? rx_data_top : rx_data_tech;

cmi_recv_packet Receiver_top (
	.clk(clk),
	.rst(rst),
	.rx_ena(rx_ena),
	.rx_data(rx_data),
	.cmi_head(cmi_head_in),
	.cmi_data0(cmi_data0_in),
	.cmi_data1(cmi_data1_in),
	.cmi_data2(cmi_data2_in),
	.cmi_data3(cmi_data3_in),
	.cmi_rdy(cmi_received),
	.cmi_fault(cmi_fault),
	.marker_st(marker_st_0),
	.marker_type(marker_type_0)
);		

reg rs232_rx_pin;	  
		
rs232_rx #(
	.pWORDw(8),
	.pBitCellCntw(link_speed))
rs232_rx_top (
	.Rst(rst),
	.Clk(clk),
	.iSerial(rs232_rx_pin),
	.oRxD(rx_data_top),
	.oRxDReady(rx_ena_top)
);							  

rs232_rx #(
	.pWORDw(8),
	.pBitCellCntw(link_speed))
rs232_rx_tech (
	.Rst(rst),
	.Clk(clk),
	.iSerial(rx_tech),
	.oRxD(rx_data_tech),
	.oRxDReady(rx_ena_tech)
);
//***********************Комутатор линий приема********************************		
always @(*)
	if(cmi_generator_mode)     			//Если режим работы от внешнего генератора, то принмать и от топа и от 0, иначе только от топа
		rs232_rx_pin <= rx_0;//rx_0;// rx_top&rx_0;
	else
		rs232_rx_pin <= rx_top;	 
		
		

//*******************Передатчик каналов*********************
wire tx_pin;
wire  [7:0]tx_data;
wire  tx_enable;	
wire tx_rdy;
wire tx_busy;

rs232_tx #(
	.pWORDw(8),
	.pBitCellCnt(link_speed))
rs232_tx_core (
	.Rst(rst),
	.Clk(clk),
	.iCode(tx_data),
	.iCodeEn(tx_enable),
	.oTxD(tx_pin),
	.oTxDReady(tx_rdy)
);					  

assign tx_busy = ~tx_rdy; 

//******************Встроенный генератор********************
wire tsg_tx_rdy;
wire [7:0]tsg_tx_data;
wire tsg_tx_enable;
wire tsg_tx_control;

wire tsg_marker_st;
wire [1:0]tsg_marker_type;		 

assign tsg_tx_rdy = tx_rdy;		//Строб маркера выставляется по факту отправки маркера по 0 линии

wire tsg_enable;
assign tsg_enable = cmi_top_out_enable&(~cmi_generator_mode);  //Стробы генерируются только в режиме работы с внутренним генератором и только, когда разрешена передача данных ТОПу

cmi_timeslot_generator #(
	.T_out(0))
TimeSlot_Generator (
	.rst(rst),
	.clk(clk),
	.enable(tsg_enable),
	.width(cmi_timeslot_len),
	.tx_rdy(tsg_tx_rdy),
	.tx_data(tsg_tx_data),
	.tx_enable(tsg_tx_enable),
	.marker_st(tsg_marker_st),
	.marker_type(tsg_marker_type),
	.tx_control(tsg_tx_control),
	.send_enable()
);			

//*****************Формирование маркера********************								
wire [1:0]marker_type;					//Тип маркера	 
wire marker_st;							//Строб маркера

wire send_marker_st;  //Строб по которому осуществляется отправка
wire resend_marker_st;  //Строб по которому осуществляется ретрансляция пакетов

wire zero_marker;
wire resend_marker;

assign zero_marker = (marker_type==2'b00); 
assign resend_marker = (marker_type==2'b11); 

assign marker_st   = (cmi_generator_mode) ?  marker_st_0   : tsg_marker_st;
assign marker_type = (cmi_generator_mode) ?  marker_type_0 : tsg_marker_type;
assign marker_st_out = marker_st&zero_marker;    //Выходной строб - строб с типом 0

assign send_marker_st = (tsg_marker_st&zero_marker)|(marker_st_0&(~zero_marker)); //Передача осуществляется для блока с задающим генератором по нулевому маркеру, а для остальных по не нулевому)
assign resend_marker_st = (tsg_marker_st&resend_marker); //Передача осуществляется только блоком с задающим генератором по  маркеру 2'b11


//*******************Передатчики каналов********************
reg tx_start;
reg [7:0]tx_cmi_head;

wire [7:0]tx_send_data;
reg  [15:0]cmi_data0_send;
reg  [15:0]cmi_data1_send;
reg  [15:0]cmi_data2_send;
reg  [15:0]cmi_data3_send;
wire tx_send_enable;		 


assign tx_data   = (tsg_tx_control) ? tsg_tx_data : tx_send_data;			//Перехват управления для отправки маркера
assign tx_enable = (tsg_tx_control) ? tsg_tx_enable : tx_send_enable;		//Перехват управления для отправки маркера

cmi_send_packet tx_top_core (
	.clk(clk),
	.rst(rst),
	.start(tx_start),
	.cmi_head(tx_cmi_head),
	.cmi_data0(cmi_data0_send),
	.cmi_data1(cmi_data1_send),
	.cmi_data2(cmi_data2_send),
	.cmi_data3(cmi_data3_send),
	.tx_busy(tx_busy),
	.tx_data(tx_send_data),
	.tx_enable(tx_send_enable),
	.rdy()
);

		
//**********************Машина отвечающая за отправку телеметрии топу и ретрансляцию пакетов*************************
reg  [5:0]seq;					//Номер пакета

reg  [1:0]tx_state;	 //Режим работы передатчика (ожидание/передача телеметрии/ретрансляция)
reg  cmi2resend;     //Флаг наличия телеметрии для ретрансляции

reg  cmi_resend;     //Строб, возникающий, когда пакет ретранслирован

always @(posedge rst, posedge clk)
	if(rst)	  
		begin 	 
			tx_cmi_head <= 0;
			cmi_data0_send <= 0;
			cmi_data1_send <= 0;
			cmi_data2_send <= 0;
			cmi_data3_send <= 0;
			tx_start <= 0;
			seq <=0;
			tx_state <= 0;	
			cmi2resend <=0;
			cmi_resend <=0;
		end	
	else
		begin 			
			if(cmi_resend)
				cmi_resend <=0;
			if(cmi_generator_mode)
				cmi2resend <=0;
			else	
				if(cmi_received)  //Если нам что-то пришло и мы работаем от внутреннего генератора, это стоит ретранслировать
					cmi2resend <=1;	 
			if(send_marker_st)			//При приходе строба передачи
				tx_state <= 1;			//Пропуск одного такта(сделано для единообразия), чтоб при 0 маркере телеметрия успела зафиксироваться	
			if(cmi2resend)				//Если есть что ретранслировать
				if((~cmi_top_out_enable)|(cmi_top_out_enable&resend_marker_st)) //Если мы в данный момент транслируем телеметрию, то пакет ретранслируется в интервал ретрансляции, иначе - немедленно.
					tx_state <= 2;		
			case(tx_state)  
				0: tx_start<=0;	  		//Режим ожидания
				1: begin				//Режим передачи телеметрии
					if(~resend_marker)	//Нехрен в интервал ретрансляции посылать телеметрию
					if((cmi_generator_mode)|(cmi_top_out_enable)) //Отправка осуществляется, либо если система работает от внешнего генератора, либо когда работает внутренний генератор. Когда последний отключен, при работе от внутреннего генератора отправка не осуществляется, т.к. нельзя гарантировать правильность коммутирования каналов.
						begin
							seq <= seq + 1;		//Увеличение номера пакета
							tx_start <= 1;		//Выставление строба начала передачи
							tx_cmi_head <= {seq,marker_type};
							cmi_data0_send <= cmi_data0_self;
							cmi_data1_send <= cmi_data1_self;
							cmi_data2_send <= cmi_data2_self;
							cmi_data3_send <= cmi_data3_self;				
						end	
						tx_state <= 0;		//Снятия состояния tx_state(которое мы использовали для пропуска одного такта)
				   end			
				2: begin 				//Режим ретрансляции
						tx_start <= 1;		//Выставление строба начала передачи
						tx_cmi_head <= cmi_head_in;
						cmi_data0_send <= cmi_data0_in;
						cmi_data1_send <= cmi_data1_in;
						cmi_data2_send <= cmi_data2_in;
						cmi_data3_send <= cmi_data3_in;						
						tx_state <= 0;	//Снятие состояния tx_state(которое мы использовали для пропуска одного такта)							
						cmi2resend <=0; //После отправки пакета телеметрия считается официально ретранслированной:) 
						cmi_resend <=1; //Выставление строба, по факту ретрансляции
				   end						
			endcase	
		end		
		
//Формирование строба прихода пакета
assign cmi_in_st = (cmi_generator_mode) ? cmi_received : cmi_resend;
		
//***********************Комутатор линий передачи********************************		
always @(posedge clk, posedge rst)
	if(rst)
		begin 
			tx_top<= 1;
			tx_0  <= 1;
			tx_1  <= 1;
		end else		  
		if(cmi_generator_mode)
			begin 
				tx_top<=tx_pin;			//В режиме внешнего генератора ножки TX всегда подключены к передатчику
				tx_0<=tx_pin;
				tx_1<=1;
			end else		
			begin	
				if(cmi_top_out_enable)	 
				begin 	
					case(marker_type)
						2'b00 : begin 		 
									tx_top <= tx_pin;			//Передатчик подключен к топу. Передается маркер и пакет
									if(tsg_tx_control)			//На время передачи маркера передатчик подключен к линиям 0 и 1, в остальное время на них держится 1
										begin 
											tx_0 <= tx_pin;
											tx_1 <= tx_pin;
										end	else
										begin 
											tx_0 <= 1;
											tx_1 <= 1;
										end	
								end		
						2'b01 : begin 
									if(tsg_tx_control)   	//Во время передачи строба
								    	begin
											tx_top <= rx_0;	    //Линия топа скоммутирована на линию 1, а передатчик на отправку строба по линии 1
											tx_0 <= tx_pin;
											tx_1 <= 1;
										end
									else begin
											tx_top <= rx_0;	    //В остальное время линия топа скоммутирована на линию 0, а передатчики линий 0 и 1 скоммутированы	на нейтральное состояние											
											tx_0 <= 1;
											tx_1 <= 1;
										 end														
								end	
						2'b10 : begin 
									if(tsg_tx_control)   	//Во время передачи строба
								    	begin
											tx_top <= rx_1;	    //Линия топа скоммутирована на линию 1, а передатчик на отправку строба по линии 1 											
											tx_1 <= tx_pin;
											tx_0 <= 1;
										end
									else begin
											tx_top <= rx_1;	    //В остальное время линия топа скоммутирована на линию 1, а передатчики линий 1 и 0 скоммутированы	на нейтральное состояние											
											tx_0 <= 1;
											tx_1 <= 1;
										 end														
								end	
						2'b11 : begin 
									tx_top <= 1;		//Интервал в который происходит ретрансляция сигналов топа
									tx_0 <= tx_pin;
									tx_1 <= tx_pin;
								end 	
					endcase
				end	else
				begin 				   
					tx_top <= 1;
					tx_0 <= tx_pin;
					tx_1 <= tx_pin;
				end	
			end	



		
//***********************Состояние лампочек связь********************************
assign l0_ok =rx_0;   //Это 485 интерфейсы, у них (в следствии инверсии), когда кабель отключен висит 0
assign l1_ok =rx_1;	  //Это 485 интерфейсы, у них (в следствии инверсии), когда кабель отключен висит 0

endmodule	