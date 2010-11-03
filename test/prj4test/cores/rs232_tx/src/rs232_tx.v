`default_nettype none
module rs232_tx (
	input Rst, 				//async reset
	input Clk, 				//system clock
	input [7:0] iCode, 		//data to be transmited 
	input iCodeEn,			//transmit command
	output oTxD,			//serialized data
	output reg oTxDReady	//rstatus; active '1'
	);
	
	parameter pWORDw = 8;
	parameter pBitCellCnt = 434;
	
	
	//typedef enum logic[2:0] {
	`define StIdle   3'b001
	//StStart,
	`define StWait   3'b010
	`define StShift  3'b100
	//StStop
	//} States;
	
	reg[2:0] CurSt, NextSt;
	
	always @ (posedge Clk, posedge Rst)begin
			if (Rst)CurSt <= `StIdle;
			else CurSt <= NextSt;
		end
	
	reg BitCntRst;
	reg BitCntEn;
	reg BitCellCntRst;
	reg ShiftBuffer;
	
	//
	// transfer	buffer with 1 start	and 1 stop bits
	//
	reg [8:0] tx_buffer;
	always @ (posedge Clk, posedge Rst) begin
			if (Rst)tx_buffer <= 9'b1_1111_1111;
			else if (iCodeEn) tx_buffer <=  {iCode,1'b0};
			else if (ShiftBuffer) tx_buffer <= {1'b1,tx_buffer[8:1]};
			else tx_buffer <= tx_buffer;
		end
	//
	// BitCellCnt
	//
	reg [9:0] BitCellCnt;
	always	@(posedge Clk, posedge Rst)begin 
			if (Rst) BitCellCnt <= 0;
			else begin
					if (BitCellCntRst) BitCellCnt <= 0;
					else BitCellCnt <= BitCellCnt + 1;
				end
		end
	//
	// BitCnt
	//
	reg [3:0] BitCnt;
	always @(posedge Clk, posedge Rst)begin
			if (Rst) BitCnt <= 0;
			else if (BitCntRst) BitCnt <= 0;
			else if (BitCntEn) BitCnt <= BitCnt + 1;
			else BitCnt <= BitCnt;
		end

	always @* begin
			//default
			BitCntRst = 0;
			BitCntEn = 0;
			BitCellCntRst = 1;
			ShiftBuffer = 0;
			NextSt = CurSt;
			oTxDReady = 0;
			case(CurSt)
				//
				// wait command to start
				//
				`StIdle:begin
						BitCntRst = 1;		 
						oTxDReady = 1;
						if (iCodeEn) NextSt = `StWait;
						else NextSt = `StIdle;
					end
				//
				// send start bit
				//
				//StStart:begin
				//	end
				//
				// wait bit-cell time
				//
				`StWait:begin
						BitCntRst = 0;
						BitCellCntRst = 0;
						if (BitCellCnt == pBitCellCnt) begin
								NextSt = `StShift;
							end
					end	
				//
				// shift next bit
				//
				`StShift:begin
						BitCntRst = 0;
						BitCellCntRst = 1;
						if (BitCnt == 9) begin
								NextSt = `StIdle;
								//BitCntRst = 1;
								//oTxDReady = 1;
								ShiftBuffer = 0;
								BitCntEn = 0;
							end
						else begin
								BitCntEn = 1;
								ShiftBuffer = 1;
								NextSt = `StWait;
							end
					end
				//
				// send stop bit
				//
				//StStop:begin
				//	end
			endcase
		end
	
	assign oTxD = tx_buffer[0];
	
endmodule

