from lib.pyparsing import Keyword, Literal, nestedExpr, Optional, Word, alphas, alphanums, SkipTo


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
    self.keywords = ['always', 'and', 'assign', 'automatic', 'begin', 'buf', 'bufif0', 'bufif1', 'case', 'casex', 'casez', 'cell', 'cmos', 'config', 'deassign', 'default', 'defparam', 'design', 'disable', 'edge', 'else', 'end', 'endcase', 'endconfig', 'endfunction', 'endgenerate', 'endmodule', 'endprimitive', 'endspecify', 'endtable', 'endtask', 'event', 'for', 'force', 'forever', 'fork', 'function', 'generate', 'genvar', 'highz0', 'highz1', 'if', 'ifnone', 'incdir', 'include', 'initial', 'inout', 'input', 'instance', 'integer', 'join', 'large', 'liblist', 'library', 'localparam', 'macromodule', 'medium', 'module', 'nand', 'negedge', 'nmos', 'nor', 'noshowcancelled', 'not', 'notif0', 'notif1', 'or', 'output', 'parameter', 'pmos', 'posedge', 'primitive', 'pull0', 'pull1', 'pulldown', 'pullup', 'pulsestyle_onevent', 'pulsestyle_ondetect', 'rcmos', 'real', 'realtime', 'reg', 'release', 'repeat', 'rnmos', 'rpmos', 'rtran', 'rtranif0', 'rtranif1', 'scalared', 'showcancelled', 'signed', 'small', 'specify', 'specparam', 'strong0', 'strong1', 'supply0', 'supply1', 'table', 'task', 'time', 'tran', 'tranif0', 'tranif1', 'tri', 'tri0', 'tri1', 'triand', 'trior', 'trireg', 'unsigned', 'use', 'vectored', 'wait', 'wand', 'weak0', 'weak1', 'while', 'wire', 'wor', 'xnor', 'xor']
    id = Word(alphas+"_", alphanums+"_$")
#    for i in self.keywords:
#      id.ignore(Keyword(i))
    params = '#' + nestedExpr()
    ports = nestedExpr()
    patternModule = Keyword('module') + id('moduleName') + Optional(params) + ports + ';'
    patternInst = id('moduleInstance') + Optional(params) + id + ports + ';'
    self.pattern = patternModule | patternInst
#    self.pattern.setDebug()

  def parse(self):
    statements = [i+';' for i in self.result['preprocessed'].split(';')]
    res = {}
    currentModule = 'bug'
    for statement in statements:
#      print 'statement ', statement
      for tokens in self.pattern.searchString(statement):
#        print tokens
#        print tokens.get('moduleName')
#        print tokens.get('moduleInstance')
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
  module ass();
function reg parity (input integer arg);
    begin
    if (arg = 0)
    ;
        if (arg)
            parity = (^buffer[lpBufferWidth-2:0] == buffer[lpBufferWidth-1]);
        else
            parity = 1;
    end
endfunction
'''
  print Parser({'preprocessed':t, 'file_path': 'aaaa'}).parsed
