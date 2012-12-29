import re

__major__ = 2
__minor__ = 7
__build__ = 586

def getVersion():
  return '{}.{}.{}'.format(__major__, __minor__, __build__)

def getIncVersion():
  with open(__file__) as f:
    content = f.read()
    content = re.sub('__build__\s+=\s+(\d+)',
                     '__build__ = {}'.format(__build__+1),
                     content)
    with open(__file__, 'w') as fw:
      fw.write(content)
      return '{}.{}.{}'.format(__major__, __minor__, __build__+1)