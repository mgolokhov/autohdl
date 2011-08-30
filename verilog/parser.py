from lib.pyparsing import Keyword, Literal, nestedExpr, Optional, Word, alphas, alphanums, SkipTo


class Parser(object):
  def __init__(self):
    self.formPattern()

  def formPattern(self):
    #'module',
    self.keywords = ['always', 'and', 'assign', 'automatic', 'begin', 'buf', 'bufif0', 'bufif1', 'case', 'casex', 'casez', 'cell', 'cmos', 'config', 'deassign', 'default', 'defparam', 'design', 'disable', 'edge', 'else', 'end', 'endcase', 'endconfig', 'endfunction', 'endgenerate', 'endmodule', 'endprimitive', 'endspecify', 'endtable', 'endtask', 'event', 'for', 'force', 'forever', 'fork', 'function', 'generate', 'genvar', 'highz0', 'highz1', 'if', 'ifnone', 'incdir', 'include', 'initial', 'inout', 'input', 'instance', 'integer', 'join', 'large', 'liblist', 'library', 'localparam', 'macromodule', 'medium',  'nand', 'negedge', 'nmos', 'nor', 'noshowcancelled', 'not', 'notif0', 'notif1', 'or', 'output', 'parameter', 'pmos', 'posedge', 'primitive', 'pull0', 'pull1', 'pulldown', 'pullup', 'pulsestyle_onevent', 'pulsestyle_ondetect', 'rcmos', 'real', 'realtime', 'reg', 'release', 'repeat', 'rnmos', 'rpmos', 'rtran', 'rtranif0', 'rtranif1', 'scalared', 'showcancelled', 'signed', 'small', 'specify', 'specparam', 'strong0', 'strong1', 'supply0', 'supply1', 'table', 'task', 'time', 'tran', 'tranif0', 'tranif1', 'tri', 'tri0', 'tri1', 'triand', 'trior', 'trireg', 'unsigned', 'use', 'vectored', 'wait', 'wand', 'weak0', 'weak1', 'while', 'wire', 'wor', 'xnor', 'xor']
    id = Word(alphas+"_", alphanums+"_$")
    for i in self.keywords:
      id.ignore(Keyword(i))
    params = '#' + '(' + SkipTo(')') + ')'
    ports = '(' + SkipTo(')') + ')'
    patternModule = Keyword('module') + id('moduleName') + Optional(params) + ports + ';'
    patternInst = id('moduleInstance') + Optional('#' + nestedExpr()) + id + nestedExpr() + ';'
    self.pattern = patternModule | patternInst


    
  def parse(self, iStr):
    statements = [i+';' for i in iStr.split(';')]
    res = {}
    for statement in statements:
      for tokens in self.pattern.searchString(statement):
        print tokens
        print tokens.get('moduleName')
        print tokens.get('moduleInstance')
        moduleName = tokens.get('moduleName')
        moduleInstance = tokens.get('moduleInstance')
        if moduleInstance:
          res[currentModule].append(moduleInstance)
        elif moduleName:
          currentModule = moduleName
          res[currentModule] = []
    print res



if __name__ == '__main__':
  t = '''
  module name1#(params)(ports);
  as #() as ();
  and if ();
  dfdfd;
  module name2#(
  params
  )(
  ports
  );
  dfdfd
  module name ();
  '''
  Parser().parse(t)
