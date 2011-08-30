from lib.pyparsing import Keyword, Literal, nestedExpr, Optional, Word, alphas, alphanums, SkipTo


class Parser(object):
  def __init__(self):
    pass

  def parse(self, iStr):
    statements = [i+';' for i in iStr.split(';')]
    id = Word(alphas+"_", alphanums+"_$")
    params = '#' + '(' + SkipTo(')') + ')'
    ports = nestedExpr()
    pattern = Keyword('module') + id('moduleName') + Optional(params) + ports + ';'
    for statement in statements:
      for tokens in pattern.searchString(statement):
        print tokens
        print tokens.get('moduleName')



if __name__ == '__main__':
  t = '''
  module name1#(params)(ports);
  module name2#(
  params
  )(
  ports
  );
  '''
  Parser().parse(t)
