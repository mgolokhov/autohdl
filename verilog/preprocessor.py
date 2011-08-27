import hashlib
import os
import re
import build
from collections import OrderedDict


from lib.pyparsing import quotedString, cppStyleComment
from hdlLogger import log_call, logging
log = logging.getLogger(__name__)

class PreprocessorException(Exception):
  def __init__(self, iString):
      Exception.__init__(self, iString)


class Preprocessor(object):
  """
  Form dictionary
  file_path    : path,
  file_sha     : num,
  preprocessed : content,
  includes     : paths  : []
                 sha    : num
  """
  def __init__(self, iFile):
    self.path = os.path.abspath(iFile)
    self.content = self.readContent(self.path)
    self.file_sha = hashlib.sha1()
    self.file_sha.update(self.content)
    self.file_sha.hexdigest()
    self.defines = {}
    self.includes  = {'paths': [], 'sha': hashlib.sha1()}

    self.content = self.removeComments(self.content)
    self.result = self.doit(self.content.splitlines())

  def doit(self, iContentIter):
    contentIter = iter(iContentIter)
    result = []
    line = None
    for line in contentIter:
      if '`' not in line:
        result.append(line)
      elif '`include' in line:
        incl = self.doit(self.prepInclude(line))
#        incl - string
        result.append(incl)
      elif '`define' in line:
        self.prepDefine(line)
      elif '`ifdef' in line:
        res = self.prepBranch(line, contentIter)
        branch = self.doit(res)
        result.append(branch)
      else:
        result.append(self.resolveDefines(line))

    return '\n'.join(result)

  def resolveDefines(self, line):
    words = line.split()
    res = []
    for w in words:
      if '`' in w:
        toResolve = self.defines.get(w[1:])
        if toResolve:
          res.append(toResolve)
        else:
          # fuck!
          log.error('cant resolve ' + w + ' in file ' + self.path)
      else:
        res.append(w)
    return ' '.join(res)







  def prepBranch(self, iLine, iContentIter):
    blocks = OrderedDict()
    branch = iLine
    blocks[branch] = []
    nested = 0
    while True:
      line = iContentIter.next()
      if '`ifdef' in line:
        nested += 1
      elif nested and '`endif' in line:
        nested -= 1
        blocks[branch].append(line)
        continue
      if not nested:
        if '`endif' in line:
          break # formed branches
        elif {'`elsif', '`else'} & set(line.split()):
          branch = line
          blocks[branch] = []
        else:
          blocks[branch].append(line)
      else:
        blocks[branch].append(line)



    for k, v in blocks.iteritems():
      if '`else' in k:
        return v
      words = k.split()
      if len(words)==2 and self.defines.get(words[1]):
        return v



        

        

  def prepDefine(self, iLine):
    words = iLine.split()
    qty = len(words)
    if qty >= 3:
      self.defines[words[1]] = ' '.join(words[2:])
    elif  qty == 2:
      self.defines[words[1]] = ' '
    else:
      log.warning('Error in preprocess parsing. Line: ' + iLine)

  def iterFlatten(iIterable):
    it = iter(iIterable)
    for e in it:
      if isinstance(e, (list, tuple)):
        for f in self.iter_flatten(e):
          yield f
      else:
        yield e

  def prepInclude(self, iLine):
    res = re.search(r'`include\s+"(.+?)"', iLine)
    if res:
      inclFile = res.group(1)
      searchPaths = build.getParam(iKey = 'include_path')
      searchPaths += [os.path.dirname(self.path)]
      for path in searchPaths:
        fullPath = os.path.join(path, inclFile)
        if os.path.exists(fullPath):
          inclContent = self.readContent(fullPath)
          self.includes['sha'].update(inclContent)
          self.includes['paths'].append(fullPath)
          return iter(inclContent.splitlines())
#    raise PreprocessorException('Cannot resolve ' + inclLine + ' in file: ' + self.path)


  def readContent(self, iFile):
    try:
      with open(iFile) as f:
        return f.read()
    except IOError:
      raise PreprocessorException('Cannot open file: ' + self.path)

  def removeComments(self, iContent):
    pattern = quotedString.suppress() | cppStyleComment
    for i in pattern.searchString(iContent):
      if i:
        comment = str(i.pop())
        print 'comment= ' + comment
        iContent = iContent.replace(comment, '', 1)
    return  iContent

  def calcSHA(self):
    h = hashlib.sha1()
    h.update(self.content)
    self.file_sha = h.hexdigest()



if __name__ == '__main__':
  print Preprocessor(iFile='nested_ifdef').result