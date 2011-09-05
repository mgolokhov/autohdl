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
  cached = cache.load(file)
  if cached:
    return cached['parsed']
  preprDict = vpreprocessor.Preprocessor(file).result
  res = vparser.Parser(preprDict).result
  cache.dump(res)
  return res['parsed']


if __name__ == '__main__':
  start = datetime.now()
#  print getInctances(r'D:\repo\github\autohdl\test\fake_repo_gold\dsn2\src/top_dcs2.v')
  try:
    for root, dirs, files in os.walk(r'D:\repo\github\autohdl\test\fake_repo_gold\dsn2\src'):
      for f in files:
        print get_instances(root+'/'+f)
  except Exception as e:
    print e
    print root+'/'+f
    raise
  print datetime.now() - start