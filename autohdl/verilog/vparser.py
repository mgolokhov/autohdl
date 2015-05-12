import re
regex_module_name_content = re.compile(r'module\s*(?P<module_name>\w+)\s*.*?;(?P<module_contents>.*?)endmodule',
                                       flags=re.MULTILINE | re.S)

class Parser(object):
    """
    input: preprocessed content (without comments)
    output: dict
      {module_name0: set(inst0, inst1, ...),
       module_name1: set(inst0, inst2, ...),
       ...,
      }
    """

    def __init__(self, data):
        self.input = data
        self.output = {}
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
                         'use', 'vectored', 'wait', 'wand', 'weak0', 'weak1', 'while', 'wire', 'wor', 'xnor', 'xor', 'string', 'int']

    def parse(self):
        for res in regex_module_name_content.finditer(self.input):
            self.module_name = res.group('module_name')
            self.output[self.module_name] = set()
            module_content = res.group('module_contents')
            self.get_instance_names(module_content)
        return self.output

    def get_instance_names(self, module_content):
        for i in module_content.split(';'):
            res = self.proc_client(i)
            if res:
                self.output[self.module_name].add(res)

    def proc_client(self, aline):
        aline = aline.strip()
        state = "st_module_name"
        module_name = []
        inst_name = []
        ports = []
        params = []
        in_parentheses = 0
        for sym in aline:
            if state == 'st_module_name':
                if re.match('\w', sym):
                    module_name.append(sym)
                elif re.match('[\s\n]', sym):
                    state = 'st_wait_par_or_inst'
                elif re.match('#', sym):
                    state = 'st_param'
                else:
                    return
            elif state == 'st_wait_par_or_inst':
                if re.match("\w", sym):
                    inst_name.append(sym)
                    state = 'st_inst_name'
                elif re.match('[\s\n]', sym):
                    pass
                elif re.match('#', sym):
                    state = 'st_param'
                else:
                    return
            elif state == 'st_inst_name':
                if re.match('\w', sym):
                    inst_name.append(sym)
                elif re.match('\(', sym):
                    ports.append(sym)
                    state = 'st_ports'
            elif state == 'st_ports':
                ports.append(sym)
            elif state == 'st_param':
                if re.match('[\s\n]', sym):
                    pass
                elif re.match('\(', sym):
                    params.append(sym)
                    in_parentheses += 1
                elif re.match('\)', sym):
                    params.append(sym)
                    in_parentheses -= 1
                elif re.match('\w', sym):
                    if not in_parentheses:
                        inst_name.append(sym)
                        state = 'st_inst_name'
                    else:
                        params.append(sym)

        instantiated_module = "".join(module_name)
        inst_name = "".join(inst_name)

        # if state != 'st_module_name':
        #     if not instantiated_module or instantiated_module in self.keywords:
        #         # print("should be ignored " + module_name)
        #         return
        if instantiated_module in self.keywords:
            return
        return instantiated_module





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

module b; as sdsd(); endmodule

'''
    p = Parser(data=t)
    p.parse()

    print(p.output)
