`default_nettype none
module test_philips_lcd(
    input CLOCK,
    input RESET,
    
    input  RS485_RX_PDU,
    output RS485_TX_PDU,
    output RS485_TXE_PDU,
    
    input  RS485_RX_EXT_2,
    output RS485_TX_EXT_2,
    output RS485_TXE_EXT_2,
    
    input  RS485_RX_EXT_1,
    output RS485_TX_EXT_1,
    output RS485_TXE_EXT_1,
    
    input  RS485_RX_MPU,
    output RS485_TX_MPU,
    output RS485_TXE_MPU,
    
    input  RS485_RX_FREQ,
    output RS485_TX_FREQ,
    output RS485_TXE_FREQ,
    
    
    output  MEZ_0,
    input  MEZ_1,// only as input
    input  MEZ_2,// only as input
    output  MEZ_3,
    input   MEZ_4,
    output  MEZ_5,
    output  MEZ_6,
    output  MEZ_7,
    output  MEZ_8,
    output  MEZ_9,
    output  MEZ_10,
    output  MEZ_11,
    output  MEZ_12,
    output  MEZ_13,
    output  MEZ_14,
    output  MEZ_15,
    output  MEZ_16,
    output  MEZ_17,
    output  MEZ_19,
    output  MEZ_18,
    output  MEZ_20,
    output  MEZ_21,
    
    
    input  MEST,
    input  DIST_1,
    input  DIST_2,
    input  KNOP_0,
    input  KNOP_1,
    input  KNOP_2,
    input  KNOP_3,
    input  KNOP_4,
    input  KNOP_5,
    
    input  LCD_MISO,    //unused?
    output reg LCD_RST,     //LCD Reset (set to low to reset) 
    output LCD_CS ,     //LCD chip select (set to low to select the LCD chip)   
    output LCD_SCK,     //Serial Clock (to LCD slave) 
    output LCD_MOSI,    //Master Out - Slave In pin (Serial Data to LCD slave) 
    output LCD_BL ,     //backlight control (normally PWM control, 1 = full on)  
    
    output STFn,
    output STRn,
    output STF1n,
    output STR1n,
    
    input  SO_FLASH,
    output RES_FLASHn,
    output CS_FLASHn,
    output SI_FLASH,
    output CCLK,
    
    
    output PDU_POWER,
    output MPU_POWER,
    
    
    output PUSK1n,
    output TORMOZ1n,
    
    output OUT_4_20MAn,
    
    input  V_SENSn,
    input  U_SENSn,
    input  W_SENSn,
    
    input  KA_RAB_VERHn,
    input  KA_RAB_NIZn,
    input  KA_SBROS_VERHn,
    input  KA_SBROS_NIZn,
    input  KA_AVAR,
    
    input  D_IN0n,
    input  D_IN1n,
    input  D_IN2n,
    
    inout  SDA,
    inout  SCL
    );
    wire iClk = CLOCK;
    wire iRst = ~RESET;
    
    //
    // Flash IF
    //
    assign RES_FLASHn = SO_FLASH;
    assign CS_FLASHn = 0;
    assign SI_FLASH = 0;
    assign CCLK = 0;
    //
    // MEZONIN IF
    //
    
    reg [26:0] clkDiv;
    assign {
        MEZ_0,
        MEZ_3,
        //MEZ_4,
        //MEZ_5,
        MEZ_6,
        MEZ_7,
        MEZ_8,
        //MEZ_9,
        //MEZ_10,
        //MEZ_11,
        //MEZ_12,
        //MEZ_13,
        //MEZ_14,
        //MEZ_15,
        MEZ_16,
        MEZ_17,
        MEZ_18,
        MEZ_19,
        MEZ_20,
        MEZ_21} = clkDiv;
    //---------------------------------------------------------------  
    
    wire rxDone;
    wire [7:0] rxData;
    wire rxWire = MEZ_4;	
    uart_rx_v2 rx (
        .iClk(iClk),
        .iRst(iRst),
        .iRxD(rxWire),
        .oData(rxData),
        .oDone(rxDone)
        );	
    
    
    wire [7:0] txData = rxData;
    wire txEnStrobe = rxDone;
    wire txWire;
    assign MEZ_5 = txWire; 	
    wire oStrobed;
    uart_tx_v2 tx (
        .iRst(iRst),
        .iClk(iClk),
        .iData(8'd88),
        .iEnStrobe(oStrobed),
        .oTxD(txWire),
        .oDone()
        );	
    
    always @(posedge iClk, posedge iRst)
        if (iRst) begin
                clkDiv <= 0;
            end
        else begin
                clkDiv <= clkDiv+1;
            end
    
    strobe strobe_e (
        .iClk(iClk),
        .iRst(iRst),
        .iUnstrobed(clkDiv[26]),
        .oStrobed(oStrobed)
        );     
    
    reg [7:0] command;
    reg [7:0] data;
    
    localparam pSpiWidth = 9;
    reg [pSpiWidth-1:0] dataSpiIn;
    reg strobeSpi;
    wire csSpi;
    wire sckSpi;
    wire doneSpi;
    wire sdiSpi;
    
    spi_master #(
        .w_length(pSpiWidth),
        .clk_div(4),
        .inv_clk(1))
        Spi
        (.clk(iClk),
        .rst(iRst),
        .value_in(dataSpiIn),
        .value_out(),
        .strob_in(strobeSpi),
        .sdi_out(sdiSpi),
        .sdo_in(1'b0),
        .sclk_out(sckSpi),
        .load_out(csSpi),
        .finish(doneSpi)
        );  
    
    
    reg cs;
    assign LCD_SCK  = csSpi ? 0 : sckSpi;    
    assign LCD_CS   = cs;
    assign LCD_MOSI = sdiSpi;
    assign MEZ_15 = LCD_SCK;
    assign MEZ_14 = LCD_CS;
    assign MEZ_13 = LCD_MOSI;
    assign MEZ_12 = clkDiv[26];//CS_FLASHn;
    assign MEZ_11 = 0;
    assign MEZ_10 = 1;
    assign MEZ_9  = 0;//oStrobed;
    assign LCD_BL = 1; 
    
    reg delay;
    wire finish = !delay & doneSpi & !strobeSpi;
    always@(posedge iClk, posedge iRst)
        if (iRst) begin
                delay <= 0;
            end
        else begin
                delay <= strobeSpi;
            end
    
    localparam SLEEPOUT = {1'b0, 8'h11},
    INVON  = {1'b0, 8'h20},  //invert
    COLMOD = {1'b0, 8'h3A}, //12-bit format
    MADCTL = {1'b0, 8'h36}, //Memory access controller
    SETCON = {1'b0, 8'h25}, //contrast
    DISPON = {1'b0, 8'h29}, //display on
    PASET  = {1'b0, 8'h2B}, //row addr
    CASET  = {1'b0, 8'h2A}, //column addr
    RAMWR  = {1'b0, 8'h2C}; //write memory
    
    integer state;
    reg [18:0] cnt;
    reg [9:0] row;
    reg [9:0] column;
    reg [7:0] rgb;
    
    wire rowStr;
    strobe row_str (.iClk(iClk),
        .iRst(iRst),
        .iUnstrobed(row[3]),
        .oStrobed(rowStr)
        );
    
    wire columnStr;
    strobe column_str (.iClk(iClk),
        .iRst(iRst),
        .iUnstrobed(column[3]),
        .oStrobed(columnStr)
        );
    
    always@(posedge iClk, posedge iRst)
        if (iRst) begin
                state <= 0;
                command <= 0;
                data <= 0;
                cnt <= 0;
                strobeSpi <= 0;
                cs <= 1;
                LCD_RST <= 0;
                column <= 0;
                row <= 0;
                rgb <= 0;
            end
        else begin
                strobeSpi <= 0;
                case(state)
                    // RESET
                    0: begin
                            LCD_RST <= 0;
                            state <= state + 1;
                        end
                    1:begin
                            if (cnt[18]) begin
                                    cnt <= 0;
                                    LCD_RST <= 1;
                                    state <= state + 1;
                                end
                            else begin
                                    cnt <= cnt + 1;
                                end
                        end
                    //  Sleep out
                    2: begin
                            if (finish) begin
                                    dataSpiIn <= SLEEPOUT;
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    // Inversion on 
                    3: begin
                            cs <= 0;
                            if (finish) begin
                                    dataSpiIn <= INVON;
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    //  Color Interface Pixel Format
                    4: begin
                            if (finish) begin
                                    dataSpiIn <= COLMOD;
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    // Set pixel format
                    5: begin
                            if (finish) begin
                                    dataSpiIn <= {1'b1, 8'h2}; // 8 bit format
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    // Setting memory access controller
                    6: begin
                            if (finish) begin
                                    dataSpiIn <= MADCTL;
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    // mirror and invert..
                    7: begin
                            if (finish) begin
                                    dataSpiIn <= {1'b1, 8'hC8};
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    // Set contrast 
                    8: begin
                            if (finish) begin
                                    dataSpiIn <= SETCON;
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    9: begin
                            if (finish) begin
                                    dataSpiIn <= {1'b1, 8'h30};
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    // Delay
                    10:begin
                            if (cnt[7]) begin
                                    cnt <= 0;
                                    state <= state + 1;
                                end
                            else begin
                                    cnt <= cnt + 1;
                                end
                        end
                    // Display On
                    11: begin
                            if (finish) begin
                                    dataSpiIn <= DISPON;
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    // Row address set
                    12: begin
                            if (finish) begin
                                    dataSpiIn <= PASET;
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    13: begin
                            if (finish) begin
                                    dataSpiIn <= {1'b1, 8'h00};
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    14: begin
                            if (finish) begin
                                    dataSpiIn <= {1'b1, 8'h83};
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    // Column address set
                    15: begin
                            if (finish) begin
                                    dataSpiIn <= CASET;
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    16: begin
                            if (finish) begin
                                    dataSpiIn <= {1'b1, 8'h00};
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    17: begin
                            if (finish) begin
                                    dataSpiIn <= {1'b1, 8'h83};
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    
                    //RAMWR
                    18: begin
                            if (finish) begin
                                    dataSpiIn <= RAMWR;
                                    strobeSpi <= 1;
                                    row <= 0;
                                    column <= 0;
                                    state <= state + 1;
                                end
                        end
                    19: begin
                            dataSpiIn <= {1'b1, rgb};//RGB 8'b000_000_11
                            if (columnStr || rowStr)
                                rgb <= ~rgb;
                            if (finish) begin
                                    if (row == 132)
                                        row <= 0;
                                    else if (column == 129)
                                        row <= row + 1; 
                                    
                                    if (column == 131)
                                        column <= 0;
                                    else
                                        column <= column + 1;
                                    
                                    strobeSpi <= 1;
                                    //state <= state + 1;
                                end
                        end
                endcase
            end
    
    
    //	reg [25:0] rrr;
    //	always@(posedge iClk, posedge iRst)
    //		if (iRst)
    //			rrr <= 0;
    //		else if (oStrobed)
    //			rrr <= rrr+1;
    
    
    
    assign STFn     = 0;//rrr[4]; //1,5625
    assign STRn     = 0;//rrr[5]; //0,78125
    assign STF1n    = 0;//rrr[6]; //0,390625
    assign STR1n    = 0;//rrr[7]; //0,1953125
    
    assign PDU_POWER   = 0;//rrr[11]; //0,01220703125
    assign MPU_POWER   = 0;//rrr[12]; //0,006103515625
    assign PUSK1n      = 0;//rrr[13]; //0,0030517578125
    assign TORMOZ1n    = 0;//rrr[14]; //0,00152587890625
    assign OUT_4_20MAn = 0;//rrr[15]; //0,000762939453125
    
    assign RS485_TX_PDU  = 0;//rrr[16];   //0,0003814697265625      RS485_RX_PDU;
    assign RS485_TXE_PDU = 0;//rrr[17];   //0,00019073486328125
    
    assign RS485_TX_EXT_2  = 0;//rrr[18]; //0,000095367431640625     RS485_RX_EXT_2;
    assign RS485_TXE_EXT_2 = 0;//rrr[19]; //0,0000476837158203125
    
    assign RS485_TX_EXT_1  = 0;//rrr[20]; //0,00002384185791015625     RS485_RX_EXT_1;
    assign RS485_TXE_EXT_1 = 0;//rrr[21]; //0,000011920928955078125
    
    assign RS485_TX_MPU  = 0;//rrr[22];   //0,0000059604644775390625   RS485_RX_MPU;
    assign RS485_TXE_MPU = 0;//rrr[23];   //0,00000298023223876953125
    
    assign RS485_TX_FREQ  = 0;//rrr[24];  //0,000001490116119384765625  RS485_RX_FREQ;
    assign RS485_TXE_FREQ = RS485_RX_PDU | 
        RS485_RX_EXT_2 |
        RS485_RX_EXT_1 | 
        RS485_RX_MPU |
        RS485_RX_FREQ |
        MEZ_1 |
        MEZ_2 |
        MEZ_4 |
        MEST |
        DIST_1 |
        DIST_2 |
        KNOP_0 |
        KNOP_1 |
        KNOP_2 |
        KNOP_3 |
        KNOP_4 |
        KNOP_5 |
        LCD_MISO |
        V_SENSn |
        U_SENSn |
        W_SENSn |
        KA_RAB_VERHn |
        KA_RAB_NIZn |
        KA_SBROS_VERHn |
        KA_SBROS_NIZn |
        KA_AVAR |
        D_IN0n |
        D_IN1n |
        D_IN2n;	
    //---------------------------------------------------------------
    wire ioSCL = 0;//0,1953125 ? 1'bz : 1'b0;
    wire ioSDA = 0;//0,09765625 ? 1'bz : 1'b0;  
    assign SCL = ioSCL;
    assign SDA = ioSDA;   
endmodule