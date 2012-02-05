import os
import re
from collections import OrderedDict

try:
  from lib.pyparsing import quotedString, cppStyleComment
  import build
  from hdlLogger import log_call, logging
except ImportError:
  from ..lib.pyparsing import quotedString, cppStyleComment
  from autohdl import build
  from ..hdlLogger import log_call, logging


log = logging.getLogger(__name__)


#    `define                  no macro func
#    `else                    +
#    `elsif                   +
#    `endif                   +
#    `ifdef                   +
#    `ifndef                  +
#    `include                 +
#    `undef                   +
# ignored:
#    `celldefine              -
#    `default_nettype         -
#    `endcelldefine           -
#    `line                    -
#    `nounconnected_drive     -
#    `resetall                -
#    `timescale               -
#    `unconnected_drive       -



class PreprocessorException(Exception):
  def __init__(self, iString):
      Exception.__init__(self, iString)


class Preprocessor(object):
  """
  Form dictionary
  file_path    : path,
  preprocessed : content,
  includes     : paths  : []
  """
  def __init__(self, iFile):
    self.ignore = {
    '`celldefine',
    '`default_nettype',
    '`endcelldefine',
    '`line',
    '`nounconnected_drive',
    '`resetall',
    '`timescale',
    '`unconnected_drive'
    }

    self.path = iFile
    self.content = self.readContent(self.path)
    self.defines = {}
    self.includes  = {'paths': []}

    self.content = re.sub(r'\\\n', '', self.content)
    self.content = self.removeComments(self.content)
    if '`' in self.content:
      self.preprocessed = self.doit(self.content.splitlines())
    else:
      self.preprocessed = self.content

    self.result = {
      'file_path'    : os.path.relpath(self.path),
      'preprocessed' : self.preprocessed,
      'includes'     : self.includes,
      'cachable'     : True
    }

  def doit(self, iContentIter):
    contentIter = iter(iContentIter)
    result = []
    for line in contentIter:
      if line and '`' not in line:
        result.append(line)
      elif any((i for i in self.ignore if i in line)):
        continue
      elif '`include' in line:
        incl = self.doit(self.prepInclude(line))
        result.append(incl)
      elif '`undef' in line:
        self.prepUndef(line)
      elif '`define' in line:
        self.prepDefine(line)
      elif '`ifdef' in line or '`ifndef' in line:
        res = self.prepBranch(line, contentIter)
        branch = self.doit(res)
        result.append(branch)
      elif line:
        res = self.doit([self.resolveDefines(line)])
#        res = self.doit([res])
        result.append(res)
    return '\n'.join(result)

  def _resolveDefines(self, line):
    words = line.split()
    res = []
    for w in words:
      if '`' in w:
        macro = re.search(r'`(\w+)', w).group()
        toResolve = self.defines.get(macro[1:])
        if toResolve:
          w = w.replace(macro, toResolve)
          res.append(w)
        else:
          log.warning('cant resolve ' + w + ' in file ' + self.path)
      else:
        res.append(w)
    return ' '.join(res)

  def resolveDefines(self, line):
    match = re.search(r'`\w+', line)
    macro = match.group()
    resolve = self.defines.get(macro[1:])
    if not resolve:
      resolve = '' # just delete TODO: store in _undef
      log.warning('cant resolve '+line+' in file '+self.path)
    return line.replace(macro, resolve)

  def prepBranch(self, iLine, iContentIter):
    blocks = OrderedDict()
    branch = iLine
    blocks[branch] = []
    nested = 0
    while True:
      line = iContentIter.next()
      if '`ifdef' in line or '`ifndef' in line:
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
      words = k.split()
      if len(words) >= 2:
        if '`ifndef' in k:
          if words[1] not in  self.defines:
            return v
        elif words[1] in self.defines:
          return v
      elif '`else' in k:
        return v
      else:
        logging.warning('Error in macro ' + k)

    return []

  def prepUndef(self, iLine):
    words = iLine.split()
    if len(words) >= 3 and self.defines.get(words[1]):
      del self.defines[words[1]]

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
      searchPaths = build.load().get('include_path', '.')
      if type(searchPaths) is not list:
        searchPaths = [searchPaths]
      searchPaths += [os.path.dirname(self.path)]
      for path in searchPaths:
        fullPath = os.path.join(path, inclFile)
        if os.path.exists(fullPath):
          self.includes['paths'].append(os.path.relpath(fullPath))
          inclContent = self.readContent(fullPath)
          return inclContent.splitlines()
    logging.warning('Cannot resolve {} in file: {}'.format(iLine,
                                                           os.path.abspath(self.path)))
    return []

  def readContent(self, iFile):
    try:
      with open(iFile) as f:
        return f.read()
    except IOError:
      raise PreprocessorException('Cannot open file: ' + os.path.abspath(self.path))

  def removeComments(self, iContent):
    iContent = iContent.replace('\t', '    ')
    pattern = quotedString.suppress() | cppStyleComment #
    for i in pattern.searchString(iContent):
      if i:
        comment = str(i.pop())
        iContent = iContent.replace(comment, '', 1)
    return  iContent


if __name__ == '__main__':
  print \
  Preprocessor(r'D:\repo\github\autohdl\test\fake_repo_gold\dsn2\src/dspuva16.v').result