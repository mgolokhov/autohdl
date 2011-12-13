import os
import cache
import vpreprocessor
import vparser
from datetime import datetime

def get_instances(file):
  """
  Input: file
  Output: dictionary
  moduleName: path      : full_path
              inctances : set()
  """
  if cache.refreshCache():
    cache.clean()
  cached = cache.load(file)
  if cached:
    return cached['parsed']
  preprDict = vpreprocessor.Preprocessor(file).result
  res = vparser.Parser(preprDict).result
  cache.dump(res)
  return res['parsed']


if __name__ == '__main__':
  start = datetime.now()
  cache.CACHE_PATH = '.'
  cache.CACHE = False
  try:
    for root, dirs, files in os.walk(r'D:\repo\github\autohdl\test\verilog\in\func'):
      for f in files:
        path = root+'/'+f
        print get_instances(path)
  except Exception as e:
    print e
    print path
    raise
  print datetime.now() - start