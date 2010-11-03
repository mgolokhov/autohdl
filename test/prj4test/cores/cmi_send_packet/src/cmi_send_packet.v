`default_nettype none
module cmi_send_packet(
	input	clk,					// Генератор
	input 	rst,					// Сброс
	input	start,					// Строб начала посылки пакета
	input [7:0]  cmi_head,			// Заголовок пакета [6'b TYPE, 2'b PORT]
	input [15:0] cmi_data0,			// Блок данных 0
	input [15:0] cmi_data1,			// Блок данных 1
	input [15:0] cmi_data2,			// Блок данных 2
	input [15:0] cmi_data3,			// Блок данных 3
	input tx_busy,					// Флаг того, что передатчик RS-232/RS-485 занят
	output reg [7:0] tx_data,		// Пакет для передачи по RS-232/RS-485
	output reg tx_enable,			// Строб начала передачи для передатчика RS-232/RS-485 
	output reg rdy						// Индикатор того, что можно посылать пакет	 (1 - готов посылать, 0 не готов)
	);
	
	

	//   CMI пакет 
	//   Н  - Заголовок пакета
	//   Младшие два бита заголовка - адрес назначения
	//   00 - АЗ блок
	//   01 - УМ блок 0
	//   10 - УМ блок 1
	//   11 - Контроллер верхнего уровня
	//   
	//	 A,B,C,D - Блоки данных по 16 бит
	//   CR - CRC6 для обычного пакета
	//   BYTE | 0   1   2   3   4   5   6   7   | 
	//   -----|---------------------------------|
	//     0  | 0   0   H0  H1  H2  H3  H4  H5  |
	//     1  | 0   1   H6  H7  A0  A1  A2  A3  |
	//     2  | 0   1   A4  A5  A6  A7  A8  A9  |
	//     3  | 0   1   A10 A11 A12 A13 A14 A15 |
	//     4  | 0   1   B0  B1  B2  B3  B4  B5  |
	//     5  | 0   1   B6  B7  B8  B9  B10 B11 |
	//     6  | 0   1   B12 B13 B14 B15 C0  C1  |
	//     7  | 0   1   C2  C3  C4  C5  C6  C7  |
	//     8  | 0   1   C8  C9  C10 C11 C12 C13 |
	//     9  | 0   1   C14 C15 D0  D1  D2  D3  |
	//     10 | 0   1   D4  D5  D6  D7  D8  D9  |
	//     11 | 0   1   D10 D11 D12 D13 D14 D15 |
	//     12 | 1   1   CR0 CR1 CR2 CR3 CR4 CR5 |
	
reg  [5:0]crc;	
wire [5:0]new_crc;
												 
crc_6 CRC6 (
	.data(tx_data),
	.crc(crc),
	.new_crc(new_crc)
);
	
	
	reg [3:0] state_m;
																			 
	reg [1:0] cur_head;
	reg [15:0] cur_tx0;
	reg [15:0] cur_tx1;
	reg [15:0] cur_tx2;
	reg [15:0] cur_tx3;	
	
	reg start_ex;

	
	always @(posedge clk or posedge rst)
		if(rst)
			begin
				tx_data <= 0;
				tx_enable <= 0;	 
				state_m <= 0; 
				cur_head <= 0;
				cur_tx0 <= 0;
				cur_tx1 <= 0;
				cur_tx2 <= 0;
				cur_tx3 <= 0;
				crc <= 0;
				start_ex <= 0;
				rdy <= 0;
			end
		else 
			begin		  
				if(rdy)
					rdy <= 0;
				if (tx_enable)
					tx_enable <= 0;
				else begin
					begin
					   if(!tx_busy)
					   begin
						 case (state_m)
							0:				// OK
		//   BYTE | 0   1   2   3   4   5   6   7   | 
		//   -----|---------------------------------|
		//     0  | 0   0   P0  P1  T0  R0  R1  R2  |
							begin 
							 if (start|start_ex)
							 begin			
								cur_head[1:0] <= cmi_head[7:6];
								cur_tx0 <= cmi_data0;
								cur_tx1 <= cmi_data1;
								cur_tx2 <= cmi_data2;
								cur_tx3 <= cmi_data3;
							    tx_enable <= 1;
							    tx_data <= {cmi_head[5:0],2'b00};
							    state_m <= state_m + 1;	
								crc <= 0;	   
								start_ex <= 0;
							 end
							end
							1:
		//   BYTE | 0   1   2   3   4   5   6   7   | 
		//   -----|---------------------------------|
		//     1  | 0   1   R3  R4  A0  A1  A2  A3  |
							begin
								tx_enable <= 1;
								tx_data <= {cur_tx0[3:0],cur_head[1:0],2'b10};
								state_m <= state_m + 1;
								crc <= new_crc;
							end
							2:
		//   BYTE | 0   1   2   3   4   5   6   7   | 
		//   -----|---------------------------------|
		//     2  | 0   1   A4  A5  A6  A7  A8  A9  |
							begin
								tx_enable <= 1;
								tx_data <= {cur_tx0[9:4],2'b10};
								state_m <= state_m + 1;
								crc <= new_crc;
							end
							3:
		//   BYTE | 0   1   2   3   4   5   6   7   | 
		//   -----|---------------------------------|
		//     3  | 0   1   A10 A11 A12 A13 A14 A15 |
							begin
								tx_enable <= 1;
								tx_data <= {cur_tx0[15:10],2'b10};
								state_m <= state_m + 1;
								crc <= new_crc;
							end
		//   BYTE | 0   1   2   3   4   5   6   7   | 
		//   -----|---------------------------------|
		//     4  | 0   1   B0  B1  B2  B3  B4  B5  |
							4:
							begin
								tx_enable <= 1;
								tx_data <= {cur_tx1[5:0],2'b10};
								state_m <= state_m + 1;
								crc <= new_crc;
							end
		//   BYTE | 0   1   2   3   4   5   6   7   | 
		//   -----|---------------------------------|
		//     5  | 0   1   B6  B7  B8  B9  B10 B11 |
							5:
							begin
								tx_enable <= 1;
								tx_data <= {cur_tx1[11:6],2'b10};
								state_m <= state_m + 1;
								crc <= new_crc;
							end
		//   BYTE | 0   1   2   3   4   5   6   7   | 
		//   -----|---------------------------------|
		//     6  | 0   1   B12 B13 B14 B15 C0  C1  |
							6:
							begin
								tx_enable <= 1;
								tx_data <= {cur_tx2[1:0],cur_tx1[15:12],2'b10};
								state_m <= state_m + 1;
								crc <= new_crc;
							end
		//   BYTE | 0   1   2   3   4   5   6   7   | 
		//   -----|---------------------------------|
		//     7  | 0   1   C2  C3  C4  C5  C6  C7  |
							7:
							begin
								tx_enable <= 1;
								tx_data <= {cur_tx2[7:2],2'b10};
								state_m <= state_m + 1;
								crc <= new_crc;
							end
		//   BYTE | 0   1   2   3   4   5   6   7   | 
		//   -----|---------------------------------|
		//     8  | 0   1   C8  C9  C10 C11 C12 C13 |
							8:
							begin
								tx_enable <= 1;
								tx_data <= {cur_tx2[13:8],2'b10};
								state_m <= state_m + 1;
								crc <= new_crc;
							end
		//   BYTE | 0   1   2   3   4   5   6   7   | 
		//   -----|---------------------------------|
		//     9  | 0   1   C14 C15 D0  D1  D2  D3  |
							9:
							begin
								tx_enable <= 1;
								tx_data <= {cur_tx3[3:0],cur_tx2[15:14],2'b10};
								state_m <= state_m + 1;
								crc <= new_crc;
							end
		//   BYTE | 0   1   2   3   4   5   6   7   | 
		//   -----|---------------------------------|
		//     10 | 0   1   D4  D5  D6  D7  D8  D9  |
							10:
							begin
								tx_enable <= 1;
								tx_data <= {cur_tx3[9:4],2'b10};
								state_m <= state_m + 1;
								crc <= new_crc;
							end
		//   BYTE | 0   1   2   3   4   5   6   7   | 
		//   -----|---------------------------------|
		//     11 | 0   1   D10 D11 D12 D13 D14 D15 |
							11:
							begin
								tx_enable <= 1;
								tx_data <= {cur_tx3[15:10],2'b10};
								state_m <= state_m + 1;
								crc <= new_crc;
							end
		//   BYTE | 0   1   2   3   4   5   6   7   | 
		//   -----|---------------------------------|
		//     12 | 1   1   CR0 CR1 CR2 CR3 CR4 CR5 |
							12:
							begin
								tx_enable <= 1;
								tx_data <= {new_crc,2'b11};
								state_m <= 13;	
								crc <= 0;
							end				 
							13:	
							begin 	
								state_m <= 0;	
								rdy <= 1;
							end							
							default: state_m <= 0;
						 endcase
					 end else
					 if(start)
						start_ex <= 1;	//Если данные пришли в момент, когда линия была занята, то строб старта передачи продляется. Но данные будут переданы не те, которые быле на входах в момент строба, а те которые будут в момент, когда линия освободиться
			end
		end
	end
	
endmodule