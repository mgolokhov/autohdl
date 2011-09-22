`default_nettype none
`define GF_IDLE           0
`define GF_BEGIN          1
`define GF_LATCH          2
`define GF_REG_ANS_WAIT   3
`define GF_CALC_TM        4
`define GF_REG_ANS_WAIT2  5
`define GF_REG_ANS_STROBE 6
`define GF_UST_GET        7
`define GF_UST_SEND       8
`define GF_TM_WAIT        9
`define GF_TM_STROBE      10
//после этого состояния переход в GF_IDLE
`define GF_END            11
`define GF_WAIT           14
`define GF_UST_WAIT_SEND  13

`define SRVBUS_GET_CONTROL  0
`define SRVBUS_CHGRP        1
`define SRVBUS_CHUST        2
`define SRVBUS_GF_BEGIN     3
`define SRVBUS_TM           4
`define SRVBUS_CH_GROUP_UST 5
`define SRVBUS_ERROR_FLAGS  6

`define DC_CNTR_PING    1
`define DC_CNTR_ADR_SET 2
`define DC_CNTR_LATCH   3
`define DC_CNTRL_REG_WR 4
`define DC_CNTRL_REG_RD 5
`define DC_CNTRL_UST    6
`define DC_CNTRL_STOP   7

`define DC_CNTRL_TM         1
`define DC_CNTRL_REG_ANS    2
`define DC_CNTRL_REG_NO_ANS 3

`define CNTRSRV_GF_BEGIN               1
`define CNTRSRV_GF_END                 2
`define CNTRSRV_TM                     3
`define CNTRSRV_UPDATE_PRESET          4
`define CNTRSRV_DC_REG_ANS             5
`define CNTRSRV_DC_REG_NO_ANS          6
`define CNTRSRV_INTERNAL_ERROR_REG_IO  7
`define CNTRSRV_TM_LOG                 8
`define CNTRSRV_GROUP_TM               9
`define CNTRSRV_C16_PIPE_IN            10

`define CNTRSRV_UST           1
`define CNTRSRV_CH_GROUP      2
`define CNTRSRV_CH_GROUP_UST  3
`define CNTRSRV_CH_PRESET     4
`define CNTRSRV_DC_PING       5
`define CNTRSRV_DC_ADR_SET    6
`define CNTRSRV_DC_REG_WR     7
`define CNTRSRV_DC_REG_RD     8
`define CNTRSRV_C16_PIPE_OUT  9

`define PrePanicUp   0
`define SlowUp       1
`define Work         2
`define SlowDn       3
`define PrePanicDn   4
`define Panic        5
`define DcNotAns     6
`define NoUst        7


module Imlight_BusController #(parameter 
	pModel_MAC=0,		  // MAC адрес контроллера
	pLinkErrorStrobeW=5  // Было 12 поменял на 5. Таймаут на линк 2^(pLinkErrorStrobeW+1) * 10 мс == почти 82 секунды
	) (
	input rst,           //async reset
	input clk,           //system clock
	
	input        iHz100,
	
	input        iSerialIn,
	output       oSerialOut,
	output reg   oSerialEnable,
	output reg   oLatch,
	input  [3:0] iSwitchBox,
	
	input       [2:0]iKA_TM,
    input       [5:0] iExtTM,
	input      [23:0]iSensor,
	output reg [11:0]oUst,
	output reg       oDriveOn,
	
	input [23:0]iNullMark,
	input [7:0] iNullMarkCount,
	
	output reg oLinkDetect,//Определяет наличие связи
	output reg oLinkError, //Определяет наличие ошибок связи если есть Link
	output AntibounceSerialIn,
	input iDriveFU,
	
	input iErrFlgManualControl,
	input iErrFlgPowerNotOn,
	input iErrFlgCA_Err,
	
	output reg [23:0] ombData,
	output reg [7:0] ombIdx,
	input [23:0] imbData,
	output reg ombWr,
	output reg [7:0]  ombCmd,
	input  [7:0] imbStatus,
	input [63:0] iModbus,
	output test_1,
	output reg test_2,
	output reg oFqInvReset,
    input iKA_RAB_VERH,
    input iKA_RAB_NIZ,
    input iKA_SBROS_VERH,
    input iKA_SBROS_NIZ,
	
	);
	
	
	
	//wire [26:0]PultTx_Data;
	//reg  PultTx_Send,PultTx_Send_;
	//wire PultTx_Ready;
	
	reg [40:0]rOutPacketD;
	reg       rOutPacketSend;
	wire      wOutPacketReady;
	
	reg  [2:0]rKA_TM;
	reg  [23:0]rEncoder; // Был регистр
	reg [11:0]rUst;
	reg       rDriveOn;
	
	wire [19:0]PultRx_Data;
	wire PultRx_Ready;
	
	reg rLatch;
	reg rOutPacketReady_Priv;
	reg  [1:0]Answer;
	reg  [7:0]RdRegAdr;
	wire [7:0]RdRegData;
	reg [11:0]MyMac;
	reg  [7:0]BackReg;
	
	DC_config_rom #(.pModel_MAC(pModel_MAC)) DcConfig (
		.clk(clk),
		.iRdAddr(RdRegAdr),
		.oRdData(RdRegData)
		);
	
	reg [5:0] rExtTM;
	reg [7:0]Link_DetectTimeOut;
	reg [pLinkErrorStrobeW:0]Error_Strobe;
	reg PacketRecive;
	reg Priv_iSerialIn_A;
	reg Priv_iSerialIn_B;
	
	reg [7:0] TestCounter;
	
	always @(posedge clk, negedge rst)
		if(rst == 0)
			TestCounter <= 0; 
		else 
			if(ombWr)
				TestCounter<=TestCounter + 1;
	
	// Есть 3!!! сигнала:
	//  - iSerialIn - вход
	//  - Priv_iSerialIn_A  - вход задержанный на 20 мкс
	//  - Priv_iSerialIn_B  - вход задержанный на 40 мкс
	
	// Пробую разобраться в Таймаутах
	
	// Значит если на канале что-то дергается.
	//    то Link_DetectTimeOut присваивается 0, а oLinkDetect присваивается 1
	//  Далее если на канале ничего не дергается, то раз в F100  Link_DetectTimeOut++
	
	// Как только Link_DetectTimeOut доходит до 5-го бита (то есть оголо 640 мс)
	//  то oLinkDetect сбрасывается в 0.
	//  То есть если за 640 мс ничего не произошло на канале, то линк мы гасим. Уффф.
	
	// След. таймаут
	// Error_Strobe - инкрементор по F100
	
	
	// Автомат требует рефакторинга
	
	assign test_1 = rDriveOn; 
	
	
	//assign rEncoder = iSensor;
	
	
	reg true_latch;
	reg [3:0] pkt_counter;
	
	always @(posedge clk, negedge rst)
		if(!rst)
			begin
				oLatch <= 0;
				true_latch <= 0;
				rEncoder <= 0;
				rExtTM <= 0;
			end
		else
			if(oLatch)
				oLatch <= 0;
			else
				if(PultRx_Ready)
					begin
						case(PultRx_Data[19:16])
							`DC_CNTR_LATCH,`DC_CNTR_PING,`DC_CNTR_ADR_SET,`DC_CNTRL_REG_WR,`DC_CNTRL_REG_RD:
								begin
									rKA_TM<=iKA_TM;
                                    rExtTM<=iExtTM;
									rEncoder<=iSensor;
									oUst<=rUst;
									oDriveOn<=rDriveOn;
									oLatch<=1;
									true_latch <= 1;
								end
							`DC_CNTRL_UST,`DC_CNTRL_STOP:begin
									pkt_counter <= PultRx_Data[3:0]; 
									if(PultRx_Data[3:0]==iSwitchBox[3:0])
										begin
											true_latch <= 0;
										end
									else
										if(true_latch == 0)
											if(pkt_counter > PultRx_Data[3:0])
												begin
													rKA_TM<=iKA_TM;
													rEncoder<=iSensor;
													oUst<=rUst;
													oDriveOn<=rDriveOn;
													oLatch<=1;
													true_latch <= 1;
												end
								end
						endcase        
					end
	
	always @(posedge clk, negedge rst)
			if(rst==0)begin
				//      oDriveOn<=0;
				Error_Strobe <= 0;
					ombIdx <= 0;
					ombData <= 0;
					ombIdx <= 0;
					oSerialEnable<=0;
					oLinkError<= 0;	 		
					ombCmd <= 0;
					BackReg <= 0;
					Answer<=0;
					MyMac <= 0;	  
					RdRegAdr <= 0;
					/*if(RdRegAdr==10)begin
							RdRegAdr<=11;
							MyMac[11:8]<=RdRegData[3:0];
					end else begin
							RdRegAdr<=10;
							MyMac[7:0]<=RdRegData;
						end*/
				end else begin
			rLatch=0;
			rOutPacketSend<=0;
			//   oLatch<=0;
			ombWr <= 0;
			test_2 <= 0;
			if(iHz100)begin 
					// Таймаут по детекту линка На рефактор. 
					// Сейчас пролучается что 2^6 * 10 = 64*10 = 640 мс - похоже
					Link_DetectTimeOut<=Link_DetectTimeOut+1;
					if(Link_DetectTimeOut[2])oLinkDetect<=0; // Было 5 поменял на 2
					Error_Strobe<=Error_Strobe+1;
					if(Error_Strobe[pLinkErrorStrobeW]==1)begin
							Error_Strobe<=0;
							PacketRecive<=0;
							oLinkError<=(PacketRecive==0);
						end
				end
			//if(oLinkError)oDriveOn<=0;
			
			Priv_iSerialIn_A<=iSerialIn;
			Priv_iSerialIn_B<=Priv_iSerialIn_A;
			
			if(Priv_iSerialIn_B!=Priv_iSerialIn_A)begin
					Link_DetectTimeOut<=0;
					oLinkDetect<=1;
				end
			
			if(PultRx_Ready)begin
					/*      case(PultRx_Data[19:16])
					`DC_CNTR_PING:$display("DC_CNTR_PING");
					`DC_CNTR_ADR_SET:$display("DC_CNTR_ADR_SET");
					`DC_CNTR_LATCH:$display("DC_CNTR_LATCH");
					`DC_CNTRL_REG_WR:$display("DC_CNTRL_REG_WR");
					`DC_CNTRL_REG_RD:$display("DC_CNTRL_REG_RD");
					`DC_CNTRL_UST:$display("DC_CNTRL_UST");
					`DC_CNTRL_STOP:$display("DC_CNTRL_STOP");
					endcase*/
					
					case(PultRx_Data[19:16])
						`DC_CNTR_LATCH,`DC_CNTR_PING,`DC_CNTR_ADR_SET,`DC_CNTRL_REG_WR,`DC_CNTRL_REG_RD:begin
								
								//         rKA_TM<=iKA_TM;
								//         rEncoder<=iSensor;
								//         oUst<=rUst;
								//         oDriveOn<=rDriveOn;
								//         oLatch<=1;
								
								//$display("Latch DriveOu %d UST (%d) %d MyMac %d",rDriveOn,rUst[11],rUst,MyMac);
								case(PultRx_Data[19:16])
									`DC_CNTR_PING:begin
											if(PultRx_Data[15:4]==MyMac)begin//My MAC
													Answer<=1;
													RdRegAdr<={4'd0,PultRx_Data[3:0]};
												end
										end
									`DC_CNTR_ADR_SET,`DC_CNTRL_REG_WR:begin
											Answer<=1;
											RdRegAdr<=0;
										end
									`DC_CNTRL_REG_RD:begin
											if(PultRx_Data[11:8]==iSwitchBox[3:0])begin//My MAC
													Answer<=1;
													RdRegAdr<=PultRx_Data[7:0];
												end
										end
								endcase
								case(PultRx_Data[19:16])
									`DC_CNTRL_REG_WR:begin	
											if(PultRx_Data[15:12]==iSwitchBox[3:0]) begin
													case(PultRx_Data[11:8])
														0:;
														1:;
														2:;
														3:;
														4:;
														5:;
														6:;
														7:;
														8:;
														9:;
														10:ombIdx <= PultRx_Data[7:0]; // Modbus Idx
														11:ombCmd <= PultRx_Data[7:0]; // Modbus control
														12:ombData[23:16] <= PultRx_Data[7:0]; // Modbus Cmd/Addr 2
														13:ombData[15:8] <= PultRx_Data[7:0]; // Modbus Cmd/Addr 1
														14:begin ombWr <= 1; ombData[7:0] <= PultRx_Data[7:0]; end// Modbus Cmd/Addr 0
														15:BackReg<= PultRx_Data[7:0];
													endcase	 
												end
										end
								endcase
							end
						`DC_CNTRL_UST,`DC_CNTRL_STOP:begin
								if(PultRx_Data[3:0]==iSwitchBox[3:0])begin
										
										PacketRecive<=1;
										test_2 <= 1;
										
										//$display("Send DC_CNTRL_TM rKA_TM %d",rKA_TM);
										oSerialEnable<=1;
										rOutPacketSend<=1; 	  
										
										rOutPacketD[40:34] <= rExtTM;//{iKA_SBROS_NIZ,iKA_SBROS_VERH,iKA_RAB_NIZ,iKA_RAB_VERH,rDriveOn&(~iErrFlgPowerNotOn),iErrFlgCA_Err,iErrFlgManualControl};
										rOutPacketD[33:31]<=`DC_CNTRL_TM;
										rOutPacketD[30:27]<=iSwitchBox[3:0];
										rOutPacketD[26:24]<=rKA_TM;
										rOutPacketD[23:0]<=rEncoder;
										
										case(PultRx_Data[19:16])
											`DC_CNTRL_UST:begin
													rUst<=PultRx_Data[15:4];
													rDriveOn<=1;
													//$display("`DC_CNTRL_UST %d",PultRx_Data[15:4]);
												end
											`DC_CNTRL_STOP:begin
													rUst<=0;
													rDriveOn<=0;
													//$display("`DC_CNTRL_STOP %d",PultRx_Data[15:4]);
												end
										endcase
								end else oSerialEnable<=0;
							end
						default:oSerialEnable<=0;
					endcase
					
					// $display("if(PultRx_Ready)");
				end
			
			
			oFqInvReset <= 0;
			case(Answer)
				0:;
				1:Answer<=2;
				2:begin
						//$display("Answer `DC_CNTRL_REG_ANS");
						oSerialEnable<=1;
						rOutPacketSend<=1;
						rOutPacketD[40:34] <= 'h7f;
						rOutPacketD[33:31]<=`DC_CNTRL_REG_ANS;
						rOutPacketD[28:17]<={4'b0000,4'b0000,iSwitchBox};//MyMac;
						rOutPacketD[16]<=1;//Адресс в этой версии установлен всегда
						rOutPacketD[15:12]<=iSwitchBox[3:0];//Addrr
						rOutPacketD[11:8]<=RdRegAdr[3:0];
						case(RdRegAdr)
							8:rOutPacketD[7:0]<=2;
							9:rOutPacketD[7:0]<=1;
							10:rOutPacketD[7:0]<=iSwitchBox;
							11:rOutPacketD[7:0]<=0;
							16:rOutPacketD[7:0]<={4'd0,iSwitchBox[3:0]};//Addrr
							127: begin
									oFqInvReset <= 1;
									rOutPacketD[7:0]<= 8'h55; 
								end
							128:begin
									//$display("iErrFlgManualControl %d",iErrFlgManualControl);
									if(iErrFlgCA_Err)             rOutPacketD[7:0]<=1;
									else if(iErrFlgPowerNotOn)    rOutPacketD[7:0]<=2;
									else if(iErrFlgManualControl) rOutPacketD[7:0]<=3;
									else if(iDriveFU)             rOutPacketD[7:0]<=4;
									else                          rOutPacketD[7:0]<=0;
								end
							
							//Регистры нольметки
							129:rOutPacketD[7:0]<=iNullMarkCount;
							130:rOutPacketD[7:0]<=iNullMark[7:0];
							131:rOutPacketD[7:0]<=iNullMark[15:8];
							132:rOutPacketD[7:0]<=iNullMark[23:16];
							
							// Регистры модбаса
							//   input [23:0] imbData,
							//   input  [7:0] imbStatus
							133: rOutPacketD[7:0] <= imbStatus;// 7 64
							134: rOutPacketD[7:0] <= imbData[23:16];// 6 56
							135: rOutPacketD[7:0] <= imbData[15:8];// 5 48
							136: rOutPacketD[7:0] <= imbData[7:0];// 4 40
							137: rOutPacketD[7:0] <= 0;// 3 32
							138: rOutPacketD[7:0] <= ombIdx;// 2 24
							139: rOutPacketD[7:0] <= ombCmd; // 1 16
							140: rOutPacketD[7:0] <= ombData[23:16];  // 0 8
							141: rOutPacketD[7:0] <= ombData[15:8];
							142: rOutPacketD[7:0] <= ombData[7:0];
							143: rOutPacketD[7:0] <= TestCounter;
							
							255: rOutPacketD[7:0] <= BackReg;
							default:rOutPacketD[7:0]<=RdRegAdr;//RdRegData;//Значение прочитанное из регистра
						endcase
						Answer<=0;
						//      rOutPacketD[7:0]
					end
				default:Answer<=0;
			endcase
			
			rOutPacketReady_Priv<=wOutPacketReady;
			if((rOutPacketReady_Priv==0)&&(wOutPacketReady==1))begin
					oSerialEnable<=0;
				end
		end
	
	
	MultiLineAntibounce #(.wCnt(5),.NLine(1)) Antibounce(
		.clk(clk),
		.rst(rst),
		.iHz100(1),
		.iUnstable(iSerialIn),
		.oStable(AntibounceSerialIn)
		);
	
	
	// .pBitCellCnt(77) - ��������� ������� ���� TX
	dcs_packet_tx #(
		.pWords(6),
		.pBitCellCnt(180) // 94 на 4-ке 77 на 3-ке // 180 
		) packet_send(
		.clk(clk),
		.rst(rst),
		.iPacketD(rOutPacketD),
		.iPacketSend(rOutPacketSend),
		.oTxDReady(wOutPacketReady),
		.oTxD(oSerialOut) );
	
	
	// .pBitCellCnt(77) - ��������� ������� ���� RX
	dcs_packet_rx #(
		.pWords(3),
		.pBitCellCnt(180), // 180
		.pTrace(0),.pModulID(700)
		) packet_recive(
		.clk(clk),
		.rst(rst),
		.oPacketD(PultRx_Data),
		.oRxDReady(PultRx_Ready),
		.iRxD(iSerialIn)
		//  .oErrorCountRxPacket(oErrorCountRxPacket),
		//.oErrorCountRx232(oErrorCountRx232)
		);
	
endmodule


module DC_config_rom #(parameter pModel_MAC=0) (
	input clk,           //system clock
	input [7:0] iRdAddr,
	output reg [7:0]oRdData
	);
	reg [7:0]RAM[0:255];
	reg [7:0]PrivRdAdr;
	integer i,b;
	
	initial
		begin
			for(i=0;i<256;i=i+1)begin
					b=pModel_MAC*i;
					RAM[i]=b[7:0];
				end
			RAM[10]=pModel_MAC[7:0];
			RAM[11]=pModel_MAC[15:8];
		end
	
	always @(posedge clk)
		begin
			//if((PrivRdAdr!=iRdAddr)||(RAM[iRdAddr]!=oRdData))begin
			//   $display("group_controll_ram_GROUP RD RAM[%d] --->%d",iRdAddr,RAM[iRdAddr]);
			//end
			PrivRdAdr<=iRdAddr;
			oRdData<=RAM[iRdAddr];
		end
endmodule
