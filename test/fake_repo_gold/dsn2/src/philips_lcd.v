module philips_lcd(
    input iRst,
    input iClk,
    input iEnStrobe,
    output oDone,
    input [7:0] pixel1,
    input [7:0] pixel2,
    //    input [11:0] pixel1,
    //    input [11:0] pixel2,
    output reg [13:0] oAddr, //11_616
    output reg oFrame_done,
    // LCD IF
    output reg LCD_RST,  //LCD Reset (set to low to reset) 
    output LCD_CS ,      //LCD chip select (set to low to select the LCD chip)   
    output LCD_SCK,      //Serial Clock (to LCD slave) 
    output LCD_MOSI,     //Master Out - Slave In pin (Serial Data to LCD slave) 
    output LCD_BL        //backlight control (normally PWM control, 1 = full on)  
    
    );      
    
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
    
    
    always@(posedge iClk, posedge iRst)
        if (iRst) begin
                state <= 0;
                cnt <= 0;
                strobeSpi <= 0;
                cs <= 1;
                LCD_RST <= 0;
                column <= 0;
                row <= 0;
                oAddr <= 0;
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
                                    //                                    dataSpiIn <= {1'b1, 8'hC8};
                                    //                                    strobeSpi <= 1;
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
                            if (finish) begin
                                    dataSpiIn <= {1'b1, pixel1};//RGB 8'b000_000_11
                                    strobeSpi <= 1;
                                    state <= state + 1;
                                end
                        end
                    20: if (finish) begin
                                dataSpiIn <= {1'b1, pixel2};//RGB 8'b000_000_11
                                strobeSpi <= 1;
                                oAddr <= oAddr + 1;
                                state <= state + 1;
                            end
                    21: if (finish) begin
                                state <= 19;   
                                
                                if (column == 132/2-1)
                                    column <= 0;
                                else
                                    column <= column + 1;        
                                
                                if (row == 132) begin
                                        oAddr <= 0;
                                        row <= 0;
                                    end
                                else if (column == 132/2-2) begin
                                        row <= row + 1;
                                    end                                    
                                
                            end
                endcase
            end    
    
endmodule
