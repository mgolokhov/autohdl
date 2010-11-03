`default_nettype none

module rs232_rx (
	input Rst, 				//async reset
	input Clk, 				//system clock
	input iSerial, 			//goes in uart
	output [7:0] oRxD,		//paralell received data
	output reg oRxDReady	//received data ready; active '1'
	);
	
	parameter pWORDw = 8;
	parameter pBitCellCntw = 434;
	//  
	// Bit-cell counter
	//
	reg [9:0] BitCellCnt;
	reg BitCellCntRst;
	always @(posedge Clk, posedge Rst)
		if (Rst) BitCellCnt <= 0;
		else if (BitCellCntRst) BitCellCnt <= 0;
		else BitCellCnt <= BitCellCnt + 1;
	//
	// Deserializer, LSB is shifted in fiRst
	//
	reg [7:0] Deserializer;
	reg DeserializerShift;
	always @(posedge Clk, posedge Rst)
		if (Rst) Deserializer <= 0;
		else if(DeserializerShift) Deserializer <= {iSerial,Deserializer[7:1]};
		else Deserializer <= Deserializer;
	//
	// Received bit counter
	//
	reg [3:0] BitCnt;
	reg BitCntEn;
	reg BitCntRst;
	always @(posedge Clk, posedge Rst)
		if (Rst) BitCnt <= 0;
		else if (BitCntEn) BitCnt <= BitCnt + 1;
		else if (BitCntRst) BitCnt <= 0;
		else BitCnt <= BitCnt;
	//
	// CurSt Machine
	//
//	`ifdef DEBUG  		 //for simulation
//	typedef enum logic [2:0] {
//	ST_START = 3'b001,
//	ST_CENTER	= 3'b010,
//	ST_WAIT  	= 3'b011,
//	ST_SAMPLE	= 3'b100,
//	ST_STOP  	= 3'b101 	 
//	} CurSts;
//	CurSts NextSt, CurSt;
//	`else		  		 //for synthesis
	reg[2:0] NextSt, CurSt;

	`define	ST_START 	3'b001
	`define ST_CENTER	3'b010
	`define ST_WAIT  	3'b011
	`define ST_SAMPLE	3'b100
	`define	ST_STOP  	3'b101
	
	always @(posedge Clk, posedge Rst)
		if (Rst) CurSt <= `ST_START;
		else CurSt <= NextSt;
	
	// Next CurSt and Output Decode
	always @* 
		begin
			// default
			NextSt  = CurSt;
			BitCellCntRst = 1;
			DeserializerShift = 0;
			BitCntEn = 0;
			BitCntRst = 1;
			oRxDReady = 0;
			
			case (CurSt)
				//
				// Wait for the start bit
				// 
				`ST_START: begin
						if (~iSerial) NextSt = `ST_CENTER;
						else begin 
								NextSt = `ST_START;
							end
					end
				//
				// Find the center of the bit-cell; 
				// if it is still 0, then go on, otherwise, it was noise
				//
				`ST_CENTER: begin
						if (BitCellCnt == pBitCellCntw/2) begin
								if (~iSerial) NextSt = `ST_WAIT;
								else NextSt = `ST_START;
						end else begin
								NextSt  = `ST_CENTER;
								BitCellCntRst = 0;	// allow counter to tick          
							end
					end
				//
				// Pick up some info near the bit-cell center
				// Wait a bit-cell time before sampling the	next bit
				//
				`ST_WAIT: begin
						BitCellCntRst = 0;  // allow counter to tick 
						BitCntRst = 0;
						if (BitCellCnt == pBitCellCntw)begin
								if (BitCnt == pWORDw)	NextSt = `ST_STOP; // we've sampled all bits	 
								else NextSt = `ST_SAMPLE;
							end
						else NextSt  = `ST_WAIT;
					end
				// 
				// Load	bit in Deserializer, after voting
				//
				`ST_SAMPLE: begin
						DeserializerShift = 1; 	// shift in the serial data
						BitCntEn = 1; 			// one more bit received
						BitCntRst = 0;
						NextSt = `ST_WAIT;
					end	
				// 
				// make sure that we've seen the stop bit?
				//
				`ST_STOP: begin
						if(iSerial == 1)begin
								NextSt = `ST_START;
								BitCntRst = 1;
								oRxDReady = 1;	 
							end
						else NextSt = `ST_START;
					end
				
			endcase
		end	 
	
	assign oRxD = Deserializer;
endmodule

