from pyparsing import Keyword, nestedExpr, Optional, Word, alphas, alphanums


class Parser(object):
    """
    Add to dict after preprocessor
    parsed:
      moduleName:
        path      : full_path
        inctances : set()
    """

    def __init__(self, data):
        self.formPattern()
        self.result = data
        self.parsed = self.parse()
        self.result['parsed'] = self.parsed

    def formPattern(self):
        self.keywords = ['always', 'and', 'assign', 'automatic', 'begin', 'buf', 'bufif0', 'bufif1', 'case', 'casex',
                         'casez', 'cell', 'cmos', 'config', 'deassign', 'default', 'defparam', 'design', 'disable',
                         'edge', 'else', 'end', 'endcase', 'endconfig', 'endfunction', 'endgenerate', 'endmodule',
                         'endprimitive', 'endspecify', 'endtable', 'endtask', 'event', 'for', 'force', 'forever',
                         'fork', 'function', 'generate', 'genvar', 'highz0', 'highz1', 'if', 'ifnone', 'incdir',
                         'include', 'initial', 'inout', 'input', 'instance', 'integer', 'join', 'large', 'liblist',
                         'library', 'localparam', 'macromodule', 'medium', 'module', 'nand', 'negedge', 'nmos', 'nor',
                         'noshowcancelled', 'not', 'notif0', 'notif1', 'or', 'output', 'parameter', 'pmos', 'posedge',
                         'primitive', 'pull0', 'pull1', 'pulldown', 'pullup', 'pulsestyle_onevent',
                         'pulsestyle_ondetect', 'rcmos', 'real', 'realtime', 'reg', 'release', 'repeat', 'rnmos',
                         'rpmos', 'rtran', 'rtranif0', 'rtranif1', 'scalared', 'showcancelled', 'signed', 'small',
                         'specify', 'specparam', 'strong0', 'strong1', 'supply0', 'supply1', 'table', 'task', 'time',
                         'tran', 'tranif0', 'tranif1', 'tri', 'tri0', 'tri1', 'triand', 'trior', 'trireg', 'unsigned',
                         'use', 'vectored', 'wait', 'wand', 'weak0', 'weak1', 'while', 'wire', 'wor', 'xnor', 'xor']
        id = Word(alphas + "_", alphanums + "_$")
        #    for i in self.keywords:
        #      id.ignore(Keyword(i))
        params = '#' + nestedExpr()
        ports = nestedExpr()
        patternModule = Keyword('module') + id('moduleName') + Optional(params) + Optional(ports) + ';'
        patternInst = id('moduleInstance') + Optional(params) + id + ports + ';'
        self.pattern = patternModule | patternInst

    #    self.pattern.setDebug()

    def parse(self):
        statements = [i + ';' for i in self.result['preprocessed'].split(';')]
        res = {}
        currentModule = 'bug'
        for statement in statements:
        #      print 'statement ', statement
            for tokens in self.pattern.searchString(statement):
                #print tokens
                #print "module name: ", tokens.get('moduleName')
                #print "module inst: ", tokens.get('moduleInstance')
                #print raw_input("next?????")
                moduleName = tokens.get('moduleName')
                moduleInstance = tokens.get('moduleInstance')
                if moduleInstance and moduleInstance not in self.keywords:
                    res[currentModule]['instances'].add(moduleInstance)
                elif moduleName:
                    currentModule = moduleName
                    res[currentModule] = {'path': self.result['file_path'], 'instances': set()}
        return res


if __name__ == '__main__':
    t = '''
`timescale 1ps / 1ps
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

'''
    print(Parser({'preprocessed': t, 'file_path': 'aaaa'}).parsed)
