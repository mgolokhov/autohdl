module dcs_packet_v2_tb;
    parameter pDataWidth = 20;
    parameter pBaud = 115200;

    reg iClk;
    reg iRst;
    reg [pDataWidth-1:0]iData;
    reg iEnStr;
    wire oDoneStr;
    wire oTxD;
    
    dcs_packet_tx_v2 #(
        .pDataWidth(pDataWidth),
        .pBaud(pBaud),
        .pStopBits(2))
        tx (.iClk(iClk),
        .iRst(iRst),
        .iData(iData),
        .iEnStr(iEnStr),
        .oDoneStr(oDoneStr),
        .oTxD(oTxD)
        );  
    
    
    wire [pDataWidth-1:0] res;
    wire doneRes;
    dcs_packet_rx_v2 #(
        .pDataWidth(pDataWidth),
        .pBaud(pBaud),
        .pStopBits(1)
        ) rx (
        .iClk(iClk),
        .iRst(iRst),
        .iRxD(oTxD),
        .oData(res),
        .oDoneStr(doneRes),
        .oMaskErrStr(),
        .oCrcErrStr()
        );
    
    initial begin
            iClk <= 0;
            forever #10ns iClk <= ~iClk;
        end
    
    initial begin
            iRst <= 1;
            #100ns iRst <= 0;
            iData <= 20'haaaaa;
            @(posedge iClk) iEnStr <= 1;
            @(posedge iClk) iEnStr <= 0;
        end
    
endmodule
