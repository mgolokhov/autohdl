`default_nettype none 
//`define EPSON_LCD // by default PHILIPS
//`define NEXYS_MODEL

// BUGAGA:
// 1. break delay make bigger;
// 2. no realization wFqInvReset;
// 3. controller addr display on PDU (too big delay at starting);
// 4. LCD rst by server actions;

`include "defines.v"

`ifdef EPSON_LCD
module top_dcs2_epson(
    `else
    module top_dcs2_philips(
    `endif
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
    
    // Universal
    output  MEZ_0,
    input  MEZ_1,// only as input
    input  MEZ_2,// only as input
    output  MEZ_3,
    output  MEZ_4,
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
    input   MEZ_15,
    
    output  MEZ_16,
    output  MEZ_17,
    output  MEZ_19,
    output  MEZ_18,
    output  MEZ_20,
    output  MEZ_21,
    
    // LCD board
    input  MEST,
    input  DIST_1,
    input  DIST_2, //unused
    input  KNOP_0,
    input  KNOP_1,
    input  KNOP_2,
    input  KNOP_3,
    input  KNOP_4,
    input  KNOP_5,
    
    // LCD interface
    input  LCD_MISO,    //unused?
    output LCD_RST,     //LCD Reset (set to low to reset) 
    output LCD_CS,      //LCD chip select (set to low to select the LCD chip)   
    output LCD_SCK,     //Serial Clock (to LCD slave) 
    output LCD_MOSI,    //Master Out - Slave In pin (Serial Data to LCD slave) 
    output LCD_BL ,     //backlight control (normally PWM control, 1 = full on)  
    
    //Regulated driver
    output STFn,
    output STRn,
    //Unregulated driver
    output STF1n,
    output STR1n,
    
    input  SO_FLASH,
    output RES_FLASHn,
    output CS_FLASHn,
    output SI_FLASH,
    output CCLK,
    
    
    output PDU_POWER,
    output MPU_POWER,
    
    
    output PUSK1n, // turn on magnetic starter
    output TORMOZ1n,
    
    output OUT_4_20MAn, // setting speed
    
    input  V_SENSn, // same as V_SENSn, A
    input  U_SENSn, // same as U_SENSn, B
    input  W_SENSn, // same as W_SENSn, C
    
    input  KA_RAB_VERHn,
    input  KA_RAB_NIZn,
    input  KA_SBROS_VERHn,
    input  KA_SBROS_NIZn,
    input  KA_AVAR,
    
    input  D_IN0n, // magnetic starter turned on (achtung otherwise)
    input  D_IN1n,
    input  D_IN2n, // inverter achtung
    
    inout  SDA,
    inout  SCL
    );
    ////////////////////////////////////////////////
    //              STUBS
    ///////////////////////////////////////////////
    
    assign RES_FLASHn = 0;
    assign CS_FLASHn = 0;
    assign SI_FLASH = 0;
    assign CCLK = 0;
    
    
    assign PDU_POWER = 0;
    assign MPU_POWER = 1;
    ///////////////////////////////////////////////////////////////////
    // Synchronization of all external inputs;
    // Debounce buttons (if any);
    // Internally all signals active-hi (except standart interfaces);
    ///////////////////////////////////////////////////////////////////
    wire iClk = CLOCK;
    wire iRst = ~RESET;
    //
    //
    //
    wire Hz100Strobe;
    wire Hz100;
    signalGen Hz100_e (
        .iClk(iClk),
        .iRst(iRst),
        .oSignalStrobe(Hz100Strobe),
        .oSignal(Hz100)
        ); 
    //
    // Global system signals;
    //
    wire turnOnKey;
    wire turnOffKey;
    wire upKey;
    wire downKey;
    wire open;
    wire close;    
    ///////////////////////////////////////////////////////////////////
    // Synchronization of all external inputs\outputs;
    // Debounce buttons (if any);
    // Internally all signals active-hi (except standart interfaces);
    ///////////////////////////////////////////////////////////////////
    wire UpButtonLCD;
    wire DownButtonLCD;
    wire LeftButtonLCD;
    wire RightButtonLCD;
    wire EscButtonLCD;
    wire EnterButtonLCD;
    wire L1_voltage;
    wire L2_voltage;
    wire L3_voltage;
    wire wKA_RAB_VERH;
    wire wKA_RAB_NIZ;
    wire wKA_SBROS_VERH;
    wire wKA_SBROS_NIZ;
    wire wKA_AVAR;
    wire remoteControl;
    wire localControl;
    wire STFn_io_synch;
    wire STRn_io_synch;
    wire inverterErr;
    wire magneticStarterOn;
    io_synch #(
    .pDebounceCntClk(19),
    .pDebounceCntHz100(3))
    io_synch_e (
    .iClk(iClk),
    .iRst(iRst),
    .iHz100Strobe(Hz100Strobe),
    // Inputs;
    .KNOP_0n(KNOP_0), .oUpButton(UpButtonLCD),
    .KNOP_1n(KNOP_1), .oEnterButton(EnterButtonLCD),
    .KNOP_2n(KNOP_2), .oEscButton(EscButtonLCD),
    .KNOP_3n(KNOP_3), .oLeftButton(LeftButtonLCD),
    .KNOP_4n(KNOP_4), .oRightButton(RightButtonLCD),
    .KNOP_5n(KNOP_5), .oDownButton(DownButtonLCD),
    
    `ifdef NEXYS_MODEL
    .iV_SENSn(0), .oL1_voltage(L1_voltage),
    .iU_SENSn(0), .oL2_voltage(L2_voltage),
    .iW_SENSn(0), .oL3_voltage(L3_voltage),
    
    .iKA_RAB_VERHn(1),     .oKA_RAB_VERHn(wKA_RAB_VERH),
    .iKA_RAB_NIZn(1),       .oKA_RAB_NIZn(wKA_RAB_NIZ),
    .iKA_SBROS_VERHn(1), .oKA_SBROS_VERHn(wKA_SBROS_VERH),
    .iKA_SBROS_NIZn(1),   .oKA_SBROS_NIZn(wKA_SBROS_NIZ),
    .iKA_AVAR(1),               .oKA_AVAR(wKA_AVAR), 
    
    .iInverterErr_n(1),        .oInverterErr(inverterErr),
    .iMagneticStarterErr_n(0), .oMagneticStarterErr(magneticStarterOn),       
    `else
    .iV_SENSn(V_SENSn), .oL1_voltage(L1_voltage),
    .iU_SENSn(U_SENSn), .oL2_voltage(L2_voltage),
    .iW_SENSn(W_SENSn), .oL3_voltage(L3_voltage),
    
    .iKA_RAB_VERHn(KA_RAB_VERHn),     .oKA_RAB_VERHn(wKA_RAB_VERH),
    .iKA_RAB_NIZn(KA_RAB_NIZn),       .oKA_RAB_NIZn(wKA_RAB_NIZ),
    .iKA_SBROS_VERHn(KA_SBROS_VERHn), .oKA_SBROS_VERHn(wKA_SBROS_VERH),
    .iKA_SBROS_NIZn(KA_SBROS_NIZn),   .oKA_SBROS_NIZn(wKA_SBROS_NIZ),
    .iKA_AVAR(KA_AVAR),               .oKA_AVAR(wKA_AVAR), 
    
    .iInverterErr_n(D_IN2n),        .oInverterErr(inverterErr),
    .iMagneticStarterErr_n(D_IN0n), .oMagneticStarterErr(magneticStarterOn),       
    `endif
    
    .iMEST(MEST),     .oLocalControl(localControl),
    .iDIST_1(DIST_1), .oRemoteControl(remoteControl),
    
    // Outputs;
    .iSTF(open),  .oSTFn(STFn_io_synch), 
    .iSTR(close), .oSTRn(STRn_io_synch)   
    
    );
    
    wire PDU_PMUn_mode = ~localControl & remoteControl;
    
    assign STFn = STFn_io_synch;
    assign STF1n = STFn_io_synch;
    assign STRn = STRn_io_synch;
    assign STR1n = STRn_io_synch; 
    
    wire [3:0] achtungNum;
    wire anyAchtung = | achtungNum;
    
    wire turnedOn;
    wire powerOn = turnedOn & ~anyAchtung;
    assign PUSK1n = ~powerOn;
    //
    //
    //
    wire [11:0] wUst;
    wire driveOn_dcs;  
    wire [9:0] speedUp;
    wire [9:0] speed_switch;
    wire open_switch;
    wire close_switch;
    ctrl_units_switch ctrl_units_switch_e (
        .iClk(iClk),
        .iRst(iRst),
        
        .iPDU_PMUn_mode(PDU_PMUn_mode),
        
        .iSpeedPU(speedUp),
        .iSpeedDCS(wUst[10:1]),
        .oSpeed(speed_switch),
        
        .iClosePU(downKey),
        .iCloseDCS(wUst[11]), // 1 - close;
        .oClose(close_switch),
        
        .iOpenPU(upKey),
        .iOpenDCS(~wUst[11]), // 0 - open;
        .oOpen(open_switch),
        
        .iTurnOnKey(turnOnKey),
        .iTurnOffKey(turnOffKey),
        .iTurnedOnDCS(driveOn_dcs),
        .oTurnedOn(turnedOn)
        );        
    //
    //
    //
    wire magneticStarterAchtung;
    magnetic_starter_achtung magnetic_starter_achtung_e (
        .iRst(iRst),
        .iClk(iClk),
        .iEn(turnedOn),
        .iHz100Strobe(Hz100Strobe),
        .iSignal(magneticStarterOn),
        .oAchtung(magneticStarterAchtung)
        );        
    //
    // Achtung handler;
    //
    achtung achtung_e (
        .iClk(iClk),
        .iRst(iRst),
        .iKA_AVAR(wKA_AVAR & ~magneticStarterOn),
        .iInverterErr(inverterErr),
        .iMagneticStarterErr(magneticStarterAchtung),
        .iL1_voltage(~L1_voltage),
        .iL2_voltage(~L2_voltage),
        .iL3_voltage(~L3_voltage),
        .oAchtungNum(achtungNum), 
        .oAchtungBlink()
        );    
    //
    //
    //
    wire [9:0] speed_ctrl_units;
    //assign  speedUp = speed_ctrl_units;
    speed_level_up speed_level_up_e(
        .iRst(iRst),
        .iClk(iClk),
        .iSpeed(speed_ctrl_units),
        .oSpeed(speedUp)
        );    
    //
    //
    //
    wire wLinkDetect; 
    if_ctrl_units #(
    .pAddrMPU(4'b0000))
    if_ctrl_units_e (.iClk(iClk),
    .iRst(iRst),
    .iHz100Strobe(Hz100Strobe),
    
    .iL1_voltage(L1_voltage), // same as V_SENSn, A
    .iL2_voltage(L2_voltage), // same as U_SENSn, B
    .iL3_voltage(L3_voltage), // same as W_SENSn, C
    .iTurnedOn(turnedOn),
    .iAchtung(anyAchtung),        // BUGAGA: Achtung signaling
    .i24v(1),                     // BUGAGA: should be numb; only mpu controling that signal;
    .iLink(wLinkDetect),          // BUGAGA: DSC link
    .iRemoteConsole(remoteControl),
    .iLocalConsole(localControl),
    .iOpen(open),  
    .iClose(close), 
    .iKA_RAB_VERH(wKA_RAB_VERH),
    .iKA_RAB_NIZ(wKA_RAB_NIZ),
    .iKA_SBROS_VERH(wKA_SBROS_VERH),
    .iKA_SBROS_NIZ(wKA_SBROS_NIZ),
    .iSpeed(speed_switch),
    
    .oTurnOnKey(turnOnKey),
    .oTurnOffKey(turnOffKey),
    .oUpKey(upKey),
    .oDownKey(downKey),
    .oSpeed(speed_ctrl_units),
    `ifdef NEXYS_MODEL
    .iMPU_rx(MEZ_15),
    .oMPU_tx(MEZ_14),
    `else
    .iMPU_rx(RS485_RX_MPU),
    .oMPU_tx(RS485_TX_MPU),
    `endif
    .oMPU_txe(RS485_TXE_MPU)
    ); 
    
    //
    //
    //
    wire open_drive;
    wire close_drive;
    if_drive #(
    .pLowSpeed(752)
    ) 
    if_drive_e (
        .iClk(iClk),
        .iRst(iRst),
        .iEnable(!anyAchtung), 
        
        .iKA_RAB_VERH(wKA_RAB_VERH),
        .iKA_RAB_NIZ(wKA_RAB_NIZ),
        .iKA_SBROS_VERH(wKA_SBROS_VERH),
        .iKA_SBROS_NIZ(wKA_SBROS_NIZ),
        
        .iCloseKey(close_switch),
        .iOpenKey(open_switch),
        .iSpeed(speed_switch),
        
        .oOpen(open_drive),
        .oClose(close_drive),
        .oOUT_4_20MAn(OUT_4_20MAn)
        );
    
    break_handler break_handler_e (
        .iRst(iRst),
        .iClk(iClk),
        .iHz100Strobe(Hz100Strobe),
        .iEn(turnedOn),
        .iOpen(open_drive),
        .iClose(close_drive),
        .oOpen(open),
        .oClose(close),
        .oBreak(TORMOZ1n)
        );
    
    //
    // Ctrl addr editor
    //
    wire SDAin_if_ctrl_addr;
    wire RWn_if_ctrl_addr;
    wire SDAout_if_ctrl_addr;
    wire SCLout_if_ctrl_addr;
    wire [4:0] Addr_if_ctrl_addr;
    
    if_ctrl_addr if_ctrl_addr_e (
        .iClk(iClk),
        .iRst(iRst),
        
        .iSDA(SDAin_if_ctrl_addr),
        .oRWn(RWn_if_ctrl_addr),
        .oSDA(SDAout_if_ctrl_addr),
        .oSCL(SCLout_if_ctrl_addr),
        .oAddr(Addr_if_ctrl_addr), 
        .iEsc(EscButtonLCD),
        .iEnter(EnterButtonLCD),
        .iUp(UpButtonLCD),
        .iDown(DownButtonLCD),
        .iLeft(LeftButtonLCD),
        .iRight(RightButtonLCD)
        );
    
    wire ioSCL = (SCLout_if_ctrl_addr) ? 1'bz : 1'b0;
    wire ioSDA = (SDAout_if_ctrl_addr | RWn_if_ctrl_addr) ? 1'bz : 1'b0;  
    assign SDAin_if_ctrl_addr = SDA & RWn_if_ctrl_addr;
    
    assign  SDA = ioSDA;
    assign  SCL = ioSCL;
    
    
    
    //
    //
    //
    wire [7:0] ascii;
    wire enStrobe;
    wire [2:0] sizeRow_write_sym;
    wire [2:0] sizeCol_write_sym;
    wire [7:0] colour_write_sym;
    wire [14:0] startAddrLCD;
    wire [14:0] curAddrLCD_write_sym;
    wire [7:0] dataLCD_write_sym;
    wire done_write_sym;
    
    write_symbol write_symbol_e (
        .iRst(iRst),
        .iClk(iClk),
        .iAscii(ascii), 
        .iEnStrobe(enStrobe),
        .iSizeRow(sizeRow_write_sym),
        .iSizeCol(sizeCol_write_sym),
        .iColour(colour_write_sym),
        .iStartAddrLCD(startAddrLCD), 
        .oCurAddrLCD(curAddrLCD_write_sym),
        .oDataLCD(dataLCD_write_sym),
        .oDone(done_write_sym)
        ); 
    
    
    wire [7:0] digit0Ascii;
    wire [7:0] digit1Ascii;
    bin_addr2ascii bin_addr2ascii_e (
        .iClk(iClk),
        .iRst(iRst),
        .iEnStrobe(1),
        .iAddr(Addr_if_ctrl_addr), 
        .oDigit0Ascii(digit0Ascii),
        .oDigit1Ascii(digit1Ascii)
        );        
    
    
    
    painter painter_e (.iClk(iClk),
        .iRst(iRst),
        .iNextSymbol(done_write_sym),
        .iAddrDigit0Ascii(digit0Ascii),
        .iAddrDigit1Ascii(digit1Ascii),
        .iPDU_PMUn_mode(PDU_PMUn_mode),
        
        .iKA_RAB_VERHn(wKA_RAB_VERH),
        .iKA_RAB_NIZn(wKA_RAB_NIZ),
        .iKA_SBROS_VERHn(wKA_SBROS_VERH),
        .iKA_SBROS_NIZn(wKA_SBROS_NIZ),
        // just for test;
        .iEscButtonLCD(EscButtonLCD),
        .iUpButtonLCD(UpButtonLCD),
        .iLeftButtonLCD(LeftButtonLCD),
        .iEnterButtonLCD(EnterButtonLCD),
        .iRightButtonLCD(RightButtonLCD),
        .iDownButtonLCD(DownButtonLCD),
        
        .iOpen(open),
        .iClose(close),
        .iTurnedOn(turnedOn),
        .iAchtungNum(achtungNum),        
        
        .oAscii(ascii),
        .oSymbolSizeRow(sizeRow_write_sym),
        .oSymbolSizeCol(sizeCol_write_sym),
        .oSymbolColour(colour_write_sym),
        .oStartAddrLCD(startAddrLCD),
        .oEnWriteSymbol(enStrobe)
        );
    
    
    
    
    // write
    reg [14:0] addr_write_vram; 
    reg [7:0] data_write_vram;
    //BUGAGA: calibration
    always@(posedge iClk, posedge iRst)
        if (iRst) begin
                addr_write_vram <= 0;
                data_write_vram <= 0;
            end
        else if (turnOnKey) begin
                addr_write_vram <= addr_write_vram + 1;
                data_write_vram <= 0;
            end
        else begin
                addr_write_vram <= curAddrLCD_write_sym;
                data_write_vram <= dataLCD_write_sym;
            end
    
    
    // read
    wire [13:0] addr_read_vram;
    wire [15:0] data_read_vram;
    
    blk_mem_gen_v3_1
        vram_e (
        // write
        .clka(iClk),
        .wea(1),
        .addra(addr_write_vram),
        .dina(data_write_vram),
        // read
        .clkb(iClk),
        .addrb(addr_read_vram),
        .doutb(data_read_vram)
        );
    
    // BUGAGA: unreal colours
    
    
    wire oRstLCD;
    restart_lcd restart_lcd_e (
        .iClk(iClk),
        .iRst(iRst),
        .iMagneticStarterOn(magneticStarterOn),
        .oRstLCD(oRstLCD)
        );     
    
    `ifdef EPSON_LCD
    wire oDone;
    reg iEnStrobe;
    wire [11:0] pixel1 = {
        data_read_vram[7:5], data_read_vram[5],// R
        data_read_vram[4:2], data_read_vram[2],// G
        data_read_vram[1:0], data_read_vram[0] // B
        };
    wire [11:0] pixel2 = {
        data_read_vram[15:13], data_read_vram[13],// R
        data_read_vram[12:10], data_read_vram[10],// G
        data_read_vram[9:8],   data_read_vram[8] // B
        };        
    epson_lcd #(
        .pSpi_clk_div(4))
        epson_lcd_e (
        .iRst(iRst | turnOnKey | oRstLCD),
        .iClk(iClk),
        .iEnStrobe(1),
        .oDone(),
        .pixel1(pixel1),
        .pixel2(pixel2),
        .oAddr(addr_read_vram),
        .oFrame_done(),
        .LCD_RST(LCD_RST),
        .LCD_CS(LCD_CS),
        .LCD_SCK(LCD_SCK),
        .LCD_MOSI(LCD_MOSI),
        .LCD_BL(LCD_BL)
        );   
    
    `else
    
    wire [7:0] pixel1 = data_read_vram[7:0];
    wire [7:0] pixel2 = data_read_vram[15:8];
    
    philips_lcd philips_lcd_e (
        .iRst(iRst | turnOnKey | oRstLCD),
        .iClk(iClk),
        .iEnStrobe(1),
        .oDone(),
        .pixel1(pixel1),
        .pixel2(pixel2),
        .oAddr(addr_read_vram),
        .oFrame_done(),
        .LCD_RST(LCD_RST),
        .LCD_CS(LCD_CS),
        .LCD_SCK(LCD_SCK),
        .LCD_MOSI(LCD_MOSI),
        .LCD_BL(LCD_BL)
        );
    
    `endif
    //////////////////////////////////////////////
    //                DEBUG
    //////////////////////////////////////////////
    assign  MEZ_0 = 0;
    assign  MEZ_3 = 0;
    
    assign  MEZ_4 = 0;
    assign  MEZ_5 = 0;
    
    assign  MEZ_6 = 0;
    assign  MEZ_7 = 0;
    
    assign  MEZ_8 = 0;
    assign  MEZ_9 = 0;
    
    assign  MEZ_10 = 0;
    assign  MEZ_11 = Hz100;
    
    assign  MEZ_12 = OUT_4_20MAn;//RWn_if_ctrl_addr;
    //assign  MEZ_13 = RWn_if_ctrl_addr;//SDAin_if_ctrl_addr;
    
    /*4*///assign  MEZ_14 = SDA;//SDAout_if_ctrl_addr;
    /*3*///assign  MEZ_15 = SCL;//SCLout_if_ctrl_addr;
    
    
    assign  MEZ_16 = 0;
    assign  MEZ_17 = 0;
    assign  MEZ_19 = 0;
    assign  MEZ_18 = 0;
    assign  MEZ_20 = 0;
    assign  MEZ_21 = 0;    
    ///////////////////////////////////////////////////////////////////
    
    reg [3:0] ctrlAddr;
    always @(posedge iRst, posedge iClk)
        if      (iRst)                  ctrlAddr <= 0;
        else if (!Addr_if_ctrl_addr[4]) ctrlAddr <= Addr_if_ctrl_addr;
    
    wire wLatch; // - Strobe for latching output signals (Encoders and KA`s) 
    wire[3:0] ContrAddr;// Address of controller
    assign ContrAddr = ctrlAddr;
    
    
    wire [2:0]wKA_TM; // KA Telemetry
    // see for codes telemetry2dcs, 7 - local controll
    wire [5:0] extTM = |achtungNum ? {2'd0, achtungNum} : (PDU_PMUn_mode ? 6'd0 : 6'd7);

    
    telemetry2dcs telemetry2dcs_e (
        .iClk(iClk),
        .iRst(iRst),
        .iKA_RAB_VERH(wKA_RAB_VERH),
        .iKA_RAB_NIZ(wKA_RAB_NIZ),
        .iKA_SBROS_VERH(wKA_SBROS_VERH),
        .iKA_SBROS_NIZ(wKA_SBROS_NIZ),
        .iAnyAchtung(anyAchtung | ~PDU_PMUn_mode),
        .iLinkWithDCS(wLinkDetect),
        .oTM(wKA_TM)
        );    
    
    //wire [11:0] wUst; // Ustavka
    
    wire wFqInvReset;
    wire wLinkError;
    wire wDriveFU = inverterErr;                     // ошибка частотника
    wire wErrFlgManualControl = ~PDU_PMUn_mode;      // мануал контролл
    wire wErrFlgPowerNotOn = magneticStarterOn;      // магн пускач
    wire wErrFlgCA_Err = wKA_RAB_VERH | wKA_RAB_NIZ; // авар концевик
    
    wire [23:0] sensor = {
    /*23-16*/8'h5,
    /*15-10*/6'h0,
    /*9-0*/speed_switch};
    
    //{
//        /*20*/ PDU_PMUn_mode,
//        /*19-8*/ wUst,
//        /*7-4*/ 4'h0,
//        /*3*/ wLatch,
//        /*2*/ driveOn_dcs,
//        /*1*/ wLinkDetect,
//        /*0*/ wLinkError
//        };
    
    
    
    Imlight_BusController
        DCS_BUS (
        .rst(RESET),
        .clk(iClk),
        .iHz100(Hz100Strobe),
        .iSerialIn(RS485_RX_EXT_2),
        .oSerialOut(RS485_TX_EXT_1),
        .oSerialEnable(RS485_TXE_EXT_1),
        .oLatch(wLatch), 
        .iSwitchBox(ContrAddr),
        .iKA_TM(wKA_TM), 
        .iExtTM(extTM),
        .iSensor(sensor), // Sensor
        .oUst(wUst),
        .oDriveOn(driveOn_dcs),
        .oLinkDetect(wLinkDetect),
        .oLinkError(wLinkError),
        .iDriveFU(wDriveFU),
        .iErrFlgManualControl(wErrFlgManualControl),
        .iErrFlgPowerNotOn(wErrFlgPowerNotOn),
        .iErrFlgCA_Err(wErrFlgCA_Err),
        .oFqInvReset(wFqInvReset),
		.iNullMark(0),
		.iNullMarkCount(0),
		.imbData(0),
		.iModbus(64'd0),
		.imbStatus(0),
        .iKA_RAB_VERH(wKA_RAB_VERH),
        .iKA_RAB_NIZ(wKA_RAB_NIZ),
        .iKA_SBROS_VERH(wKA_SBROS_VERH),
        .iKA_SBROS_NIZ(wKA_SBROS_NIZ)
        );	    
    
endmodule

