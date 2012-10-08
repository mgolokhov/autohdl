module epson_lcd(
    input iRst,
    input iClk,
    input iEnStrobe,
    output oDone,
    input [11:0] pixel1,
    input [11:0] pixel2,
    output reg [13:0] oAddr, //11_616
    output reg oFrame_done,
    // LCD IF
    output reg LCD_RST,  //LCD Reset (set to low to reset) 
    output LCD_CS ,      //LCD chip select (set to low to select the LCD chip)   
    output LCD_SCK,      //Serial Clock (to LCD slave) 
    output LCD_MOSI,     //Master Out - Slave In pin (Serial Data to LCD slave) 
    output LCD_BL        //backlight control (normally PWM control, 1 = full on)  
    
    );
    
    ///////////////////////////////////////////
    //                  SPI
    ///////////////////////////////////////////
    localparam pSpiWidth = 9;
    reg [pSpiWidth-1:0] dataSpiIn;
    reg strobeSpi;
    wire csSpi;
    wire sckSpi;
    wire doneSpi;
    wire sdiSpi;
    
    
    parameter pSpi_clk_div = 4;
    spi_master #(
        .w_length(pSpiWidth),
        .clk_div(pSpi_clk_div),
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
    assign LCD_BL = 1; 
    
    localparam DISON = {1'b0, 8'hAF},      // Display on 
    DISOFF   = {1'b0, 8'hAE},      // Display off 
    DISNOR   = {1'b0, 8'hA6},      // Normal display 
    DISINV   = {1'b0, 8'hA7},      // Inverse display 
    COMSCN   = {1'b0, 8'hBB},      // Common scan direction 
    DISCTL   = {1'b0, 8'hCA},      // Display control 
    SLPIN    = {1'b0, 8'h95},      // Sleep in 
    SLPOUT   = {1'b0, 8'h94},      // Sleep out 
    PASET    = {1'b0, 8'h75},      // Page address set 
    CASET    = {1'b0, 8'h15},      // Column address set 
    DATCTL   = {1'b0, 8'hBC},      // Data scan direction, etc. 
    RGBSET8  = {1'b0, 8'hCE},      // 256-color position set 
    RAMWR    = {1'b0, 8'h5C},      // Writing to memory 
    RAMRD    = {1'b0, 8'h5D},      // Reading from memory 
    PTLIN    = {1'b0, 8'hA8},      // Partial display in 
    PTLOUT   = {1'b0, 8'hA9},      // Partial display out 
    RMWIN    = {1'b0, 8'hE0},      // Read and modify write 
    RMWOUT   = {1'b0, 8'hEE},      // End 
    ASCSET   = {1'b0, 8'hAA},      // Area scroll set 
    SCSTART  = {1'b0, 8'hAB},      // Scroll start set 
    OSCON    = {1'b0, 8'hD1},      // Internal oscillation on 
    OSCOFF   = {1'b0, 8'hD2},      // Internal oscillation off 
    PWRCTR   = {1'b0, 8'h20},      // Power control 
    VOLCTR   = {1'b0, 8'h81},      // Electronic volume control 
    VOLUP    = {1'b0, 8'hD6},      // Increment electronic control by 1 
    VOLDOWN  = {1'b0, 8'hD7},      // Decrement electronic control by 1 
    TMPGRD   = {1'b0, 8'h82},      // Temperature gradient set 
    EPCTIN   = {1'b0, 8'hCD},      // Control EEPROM 
    EPCOUT   = {1'b0, 8'hCC},      // Cancel EEPROM control 
    EPMWR    = {1'b0, 8'hFC},      // Write into EEPROM 
    EPMRD    = {1'b0, 8'hFD},      // Read from EEPROM 
    EPSRRD1  = {1'b0, 8'h7C},      // Read register 1 
    EPSRRD2  = {1'b0, 8'h7D},      // Read register 2 
    NOP      = {1'b0, 8'h25};      // NOP instruction     
    
    
    
    
    integer state;
    reg [26:0] cnt;
    reg [9:0] row;
    reg [9:0] column;
   
    reg delay;
    wire finish = !delay & doneSpi & !strobeSpi;
    always@(posedge iClk, posedge iRst)
        if (iRst) begin
                delay <= 0;
            end
        else begin
                delay <= strobeSpi;
            end

    always@(posedge iClk, posedge iRst)
        if (iRst) begin
                state <= 0;
                cnt <= 0;
                strobeSpi <= 0;
                cs <= 1;
                LCD_RST <= 0;
                column <= 0;
                row <= 0;
                oFrame_done <= 0;
                oAddr <= 0;
            end
        else begin
            strobeSpi <= 0;
            oFrame_done <= 0;
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
                    //
                    // Display control
                    //
                    2: begin
                            if (finish) begin
                                    dataSpiIn <= DISCTL;
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    //  
                    3: begin
                            cs <= 0;
                            if (finish) begin
                                    dataSpiIn <= {1'b1,8'h0C};  // P1: 0x00 = 2 divisions, switching period=8 (default)
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    //  
                    4: begin
                            if (finish) begin
                                    dataSpiIn <= {1'b1,8'h20}; // P2: 0x20 = nlines/4 - 1 = 132/4 - 1 = 32) 
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    // 
                    5: begin
                            if (finish) begin
                                    dataSpiIn <= {1'b1, 8'h00}; // P3: 0x00 = no inversely highlighted lines 
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    //
                    // COM scan
                    //
                    6: begin
                            if (finish) begin
                                    dataSpiIn <= COMSCN;
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    //
                    7: begin
                            if (finish) begin
                                    dataSpiIn <= {1'b1, 8'hC3}; // P1: 0x01 = Scan 1->80, 160<-81
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    //  Internal oscilator ON  
                    8: begin
                            if (finish) begin
                                    dataSpiIn <= OSCON;
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    // Sleep out
                    9: begin
                            if (finish) begin
                                    dataSpiIn <= SLPOUT;
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    // Power control 
                    10:begin
                            if (finish) begin
                                    dataSpiIn <= PWRCTR;
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    //
                    11: begin
                            if (finish) begin
                                    dataSpiIn <= {1'b1, 8'h0f}; // reference voltage regulator on, circuit voltage follower on, BOOST ON 
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    //
                    // Data control 
                    //
                    12: begin
                            if (finish) begin
                                    dataSpiIn <= DATCTL;
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    13: begin
                            if (finish) begin
                                    dataSpiIn <= {1'b1, 8'h00};  // P1: 0x01 = page address inverted, col address normal, address scan in col direction 
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    14: begin
                            if (finish) begin
                                    dataSpiIn <= {1'b1, 8'h00};  // P2: 0x00 = RGB sequence (default value) 
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    15: begin
                            if (finish) begin
                                    dataSpiIn <= {1'b1, 8'h02}; // P3: 0x02 = Grayscale -> 16 (selects 12-bit color, type A) 
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    16: begin
                            if (finish) begin
                                    dataSpiIn <= VOLCTR;
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end                    
                    17: begin
                            if (finish) begin
                                    dataSpiIn <= 30;  // P1 = 32  volume value  (adjust this setting for your display  0 .. 63) 
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end                    
                    18: begin
                            if (finish) begin
                                    dataSpiIn <= 3;  // P2 = 3    resistance ratio  (determined by experiment)  
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end 
                    // allow power supply to stabilize 
                    19: begin
                            if (cnt[18]) begin
                                    cnt <= 0;
                                    state <= state + 1;
                                end
                            else begin
                                    cnt <= cnt + 1;
                                end
                        end
                    // turn on the display 
                    20: begin
                            if (finish) begin
                                    dataSpiIn <= DISON;
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end   
                    ////////////////////////////////////////
                    //             INIT DONE
                    ////////////////////////////////////////
                    
                    
                    //
                    // Column address set
                    //
                    21: begin
                            if (finish) begin
                                    dataSpiIn <= CASET;
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    22: begin
                            if (finish) begin
                                    dataSpiIn <= {1'b1, 8'h00};
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    23: begin
                            if (finish) begin
                                    dataSpiIn <= {1'b1, 8'h83};
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    //
                    // Row address set
                    //
                    24: begin
                            if (finish) begin
                                    dataSpiIn <= PASET;
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    25: begin
                            if (finish) begin
                                    dataSpiIn <= {1'b1, 8'h00};
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    26: begin
                            if (finish) begin
                                    dataSpiIn <= {1'b1, 8'h83};
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    
                    //RAMWR
                    27: begin
                            if (finish) begin
                                    dataSpiIn <= RAMWR;
                                    strobeSpi <= 1;
                                    row <= 0;
                                    column <= 0;
                                    state <= state + 1;
                                end
                        end
                    ///////////////////////////////////////////////
                    //                Actual drawing
                    ///////////////////////////////////////////////
                    28:  if (iEnStrobe) begin
                                if (finish) begin
                                        dataSpiIn <= {1'b1, pixel1[11:4]};
                                        strobeSpi <= 1;
                                        state <= state + 1;
                                    end
                            end
                    29: if (finish) begin
                                dataSpiIn <= {1'b1, {pixel1[3:0], pixel2[11:8]}};
                                strobeSpi <= 1;
                                state <= state + 1;
                            end
                    30: if (finish) begin
                                dataSpiIn <= {1'b1, {pixel2[7:0]}};
                                strobeSpi <= 1;
                                oAddr <= oAddr + 1;
                                state <= 28;
                                
                                if (column == 132/2-1)
                                    column <= 0;
                                else
                                    column <= column + 1;        

                                if (row == 130) begin
                                        oAddr <= 0;
                                        oFrame_done <= 1;
                                        row <= 0;
                                    end
                                else if (column == 132/2-2) begin
                                        row <= row + 1;
                                    end
                                
                            end
                    
                endcase
            end
    
    
endmodule
