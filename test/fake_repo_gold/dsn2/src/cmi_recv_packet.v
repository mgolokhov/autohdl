`default_nettype none
module cmi_recv_packet(
	input clk,			// Тактовый генератор
	input rst,			// Ресет
	input rx_ena,		// Флаг того, что приемник RS232/RS485 получил байт
	input [7:0] rx_data,		// Блок данных полученных с приемника RS232/RS485
	output reg [7:0]  cmi_head,	//Заголовок пакета
	output reg [15:0] cmi_data0,//Блок данных 0	
	output reg [15:0] cmi_data1,//Блок данных 1	
	output reg [15:0] cmi_data2,//Блок данных 2	
	output reg [15:0] cmi_data3,//Блок данных 3							 
	output reg cmi_rdy,		// Флаг того, что пакет принят
	output reg cmi_fault,	// Флаг того, что пакет принят с ошибкой	 
	output reg marker_st,	// Строб прихода маркера
	output reg [1:0]marker_type	// Тип последнего пришедшего маркера
	);
	
	//
	//   CMI пакет 
	//   P - Номер порта
	//   00 - АЗ блок
	//   01 - УМ блок 0
	//   10 - УМ блок 1
	//   11 - Контроллер верхнего уровня
	//   
	//	 H - Заголовок пакета
	//	 A,B,C,D - Блоки данных по 16 бит
	//   CR - CRC6 для обычного пакета и порядковый номер для телеметрии
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
	
	reg [3:0] state_m;	   
	
	reg [15:0] tmp_data0;
	reg [15:0] tmp_data1;
	reg [15:0] tmp_data2;
	reg [15:0] tmp_data3;	
	reg [7:0] tmp_head;	 
	
reg  [5:0]crc;	
wire [5:0]new_crc;
	
crc_6 CRC_Core (
	.data(rx_data),
	.crc(crc),
	.new_crc(new_crc)
);

	always @(posedge clk or posedge rst)
		if(rst)
			begin
				state_m <= 0;
				cmi_head  <=0;
				cmi_data0 <=0;
				cmi_data1 <=0;
				cmi_data2 <=0;
				cmi_data3 <=0;
				cmi_rdy   <=0;
				cmi_fault <=0;
				tmp_head <= 0;	 
				tmp_data0 <= 0;
				tmp_data1 <= 0;
				tmp_data2 <= 0;
				tmp_data3 <= 0;
				crc <= 0;		   
				marker_st <= 0;
				marker_type <= 0;
			end
		else
			begin		 
				if(marker_st)
					marker_st <= 0;
				if(cmi_rdy)
				    cmi_rdy <= 0;
				if(cmi_fault)
				    cmi_fault <= 0;
				if(rx_ena)
					if(rx_data[5:0] == 6'b101101)  //Если пришел маркер
					begin 	
						if(state_m)				//Если во время приема пакета мы приняли маркер, то значет пакет заведомо неверный
							begin 
								state_m <= 0;
								cmi_fault <= 1;
								crc <= 0;
							end	   
						marker_st <= 1;					//Выставляем строб прихода маркера
						marker_type  <= rx_data[7:6];	//Тип маркера равер его старшему биту
					end else	
					case(state_m)
						//   BYTE | 0   1   2   3   4   5   6   7   | 
						//   -----|---------------------------------|
						//     0  | 0   0   P0  P1  T0  R0  R1  R2  |
    					0:
						begin	
							if(rx_data[1:0] == 2'b00)
								begin
									tmp_head[5:0] <= rx_data[7:2];
									state_m <= state_m + 1;
									crc <= new_crc;
								end	else 
									crc	<= 0;
						end
						
						//   BYTE | 0   1   2   3   4   5   6   7   | 
						//   -----|---------------------------------|
						//     1  | 0   1   R3  R4  A0  A1  A2  A3  |
    					1:
						begin
							if(rx_data[1:0] == 2'b10)
								begin					   
									tmp_head[7:6] <= rx_data[3:2];
									tmp_data0[3:0] <= rx_data[7:4];
									state_m <= state_m + 1;
									crc <= new_crc;
								end else 
								begin
									state_m <= 0;
									cmi_fault <= 1;
									crc <= 0;
								end	
						end
						//   BYTE | 0   1   2   3   4   5   6   7   | 
						//   -----|---------------------------------|
						//     2  | 0   1   A4  A5  A6  A7  A8  A9  |
    					2:
						begin
							if(rx_data[1:0] == 2'b10)
								begin					   
									tmp_data0[9:4] <= rx_data[7:2];
									state_m <= state_m + 1;
									crc <= new_crc;
								end else 
								begin
									state_m <= 0;
									cmi_fault <= 1;
									crc <= 0;
								end	
						end
						//   BYTE | 0   1   2   3   4   5   6   7   | 
						//   -----|---------------------------------|
						//     3  | 0   1   A10 A11 A12 A13 A14 A15 |
    					3:
						begin
							if(rx_data[1:0] == 2'b10)
								begin					   
									tmp_data0[15:10] <= rx_data[7:2];
									state_m <= state_m + 1;
									crc <= new_crc;
								end else 
								begin
									state_m <= 0;
									cmi_fault <= 1;
									crc <= 0;
								end	
						end
						//   BYTE | 0   1   2   3   4   5   6   7   | 
						//   -----|---------------------------------|
						//     4  | 0   1   B0  B1  B2  B3  B4  B5  |
    					4:
						begin
							if(rx_data[1:0] == 2'b10)
								begin					   
									tmp_data1[5:0] <= rx_data[7:2];
									state_m <= state_m + 1;
									crc <= new_crc;
								end else 
								begin
									state_m <= 0;
									cmi_fault <= 1;
									crc <= 0;
								end	
						end
						//   BYTE | 0   1   2   3   4   5   6   7   | 
						//   -----|---------------------------------|
						//     5  | 0   1   B6  B7  B8  B9  B10 B11 |
    					5:
						begin
							if(rx_data[1:0] == 2'b10)
								begin					   
									tmp_data1[11:6] <= rx_data[7:2];
									state_m <= state_m + 1;
									crc <= new_crc;
								end else 
								begin
									state_m <= 0;
									cmi_fault <= 1;
									crc <= 0;
								end	
						end
						//   BYTE | 0   1   2   3   4   5   6   7   | 
						//   -----|---------------------------------|
						//     6  | 0   1   B12 B13 B14 B15 C0  C1  |
    					6:
						begin
							if(rx_data[1:0] == 2'b10)
								begin					   
									tmp_data1[15:12] <= rx_data[5:2];
									tmp_data2[1:0] <= rx_data[7:6];
									state_m <= state_m + 1;
									crc <= new_crc;
								end else 
								begin
									state_m <= 0;
									cmi_fault <= 1;
									crc <= 0;
								end	
						end
						//   BYTE | 0   1   2   3   4   5   6   7   | 
						//   -----|---------------------------------|
						//     7  | 0   1   C2  C3  C4  C5  C6  C7  |
    					7:
						begin
							if(rx_data[1:0] == 2'b10)
								begin					   
									tmp_data2[7:2] <= rx_data[7:2];
									state_m <= state_m + 1;
									crc <= new_crc;
								end else 
								begin
									state_m <= 0;
									cmi_fault <= 1;
									crc <= 0;
								end	
						end
						//   BYTE | 0   1   2   3   4   5   6   7   | 
						//   -----|---------------------------------|
						//     8  | 0   1   C8  C9  C10 C11 C12 C13 |
    					8:
						begin
							if(rx_data[1:0] == 2'b10)
								begin					   
									tmp_data2[13:8] <= rx_data[7:2];
									state_m <= state_m + 1;
									crc <= new_crc;
								end else 
								begin
									state_m <= 0;
									cmi_fault <= 1;
									crc <= 0;
								end	
						end
						//   BYTE | 0   1   2   3   4   5   6   7   | 
						//   -----|---------------------------------|
						//     9  | 0   1   C14 C15 D0  D1  D2  D3  |
    					9:
						begin
							if(rx_data[1:0] == 2'b10)
								begin					   
									tmp_data2[15:14] <= rx_data[3:2];
									tmp_data3[3:0] <= rx_data[7:4];
									state_m <= state_m + 1;
									crc <= new_crc;
								end else 
								begin
									state_m <= 0;
									cmi_fault <= 1;
									crc <= 0;
								end	
						end
						//   BYTE | 0   1   2   3   4   5   6   7   | 
						//   -----|---------------------------------|
						//     10 | 0   1   D4  D5  D6  D7  D8  D9  |
    					10:
						begin
							if(rx_data[1:0] == 2'b10)
								begin					   
									tmp_data3[9:4] <= rx_data[7:2];
									state_m <= state_m + 1;
									crc <= new_crc;
								end else 
								begin
									state_m <= 0;
									cmi_fault <= 1;
									crc <= 0;
								end	
						end
						//   BYTE | 0   1   2   3   4   5   6   7   | 
						//   -----|---------------------------------|
						//     11 | 0   1   D10 D11 D12 D13 D14 D15 |
    					11:
						begin
							if(rx_data[1:0] == 2'b10)
								begin					   
									tmp_data3[15:10] <= rx_data[7:2];
									state_m <= state_m + 1;
									crc <= new_crc;
								end else 
								begin
									state_m <= 0;
									cmi_fault <= 1;
									crc <= 0;
								end	
						end
						//   BYTE | 0   1   2   3   4   5   6   7   | 
						//   -----|---------------------------------|
						//     12 | 1   1   CR0 CR1 CR2 CR3 CR4 CR5 |
    					12:
						begin
							if(	(rx_data[1:0] == 2'b11)&							 //Пакет правильный если: правильный конец и
								(rx_data[7:2] == crc)	 							 //правильная контрольная сумма
							  )
								begin					   
									cmi_head <=  tmp_head;
									cmi_data0 <= tmp_data0;
									cmi_data1 <= tmp_data1;
									cmi_data2 <= tmp_data2;
									cmi_data3 <= tmp_data3;
									cmi_rdy <= 1;									
									state_m <= 0;
									crc <= 0;
								end	else
								begin
									state_m <= 0;
									cmi_fault <= 1;
									crc <= 0;
								end			
						end
						default: state_m <= 0;
					endcase
		end
endmodule