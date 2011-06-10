import re
import os
import sys
import time
import subprocess
import hashlib


from lib.pyparsing import *
from hdlLogger import log_call, logging
log = logging.getLogger(__name__)

import lib.yaml as yaml
import build



class InstanceException(Exception):
  def __init__(self, iString):
    self.string = iString
  def __str__(self):
    return self.string

@log_call
def removeComments(ioString):
  ioString = ioString.replace('\t', '    ')
  withoutQuotedStr = ioString
  for tokens in QuotedString(quoteChar='"').searchString(withoutQuotedStr):
    tok = tokens[0]
    log.debug('quoted string= ' + tok)
    withoutQuotedStr = withoutQuotedStr.replace(tok, '', 1)
  for tokens in cppStyleComment.searchString(withoutQuotedStr):
    tok = tokens[0]
    log.debug('comment= ' + tok)
    ioString = ioString.replace(tok, '', 1)
  return ioString
  

def removeFunc(content):
  return re.sub(r'\sfunction\s.*?\sendfunction\s', '', content, flags=re.M|re.S)


def readContent(iPathFile):
  f = open(iPathFile, 'r')
  content = f.read()
  f.close() 
  return content 


def getParsedPaths(iAbsPath):
  dir = '../resource/parsed'
  if not os.path.exists(dir):
    os.mkdir(dir)
  relPath = os.path.relpath(iAbsPath, '../script')
  name = relPath.replace(os.sep, '_')
  name = name.replace('.', '_')
  pathToFile = dir+'/'+name
  return relPath, pathToFile 


def calcHash(iContent):
  h = hashlib.sha1()
  h.update(iContent)
  return h.hexdigest()  

@log_call
def saveParsed(iContent, parsed):
  if not parsed:
    return
  hashres = calcHash(iContent)
  relPath, pathToFile = getParsedPaths(parsed.values()[0][0])
  f = open(pathToFile, 'w')
  d = {'sha1': hashres}
  k = parsed.keys()[0]
  v = parsed.values()[0]
  tmp = {}
  for k, v in parsed.iteritems():
    tmp.update({k: [relPath] + v[1:]})
  d.update({'parsed' : tmp})
  yaml.dump(d, f, default_flow_style=False)
  f.close()


@log_call
def checkIfParsed(iContent, iPath):
  relPath, pathToFile = getParsedPaths(iPath)
  if not os.path.exists(pathToFile):
    return
  f = open(pathToFile, 'r')
  y = yaml.load(f)
  f.close()
  hashres = calcHash(iContent)
  if y['sha1'] == hashres:
    log.info('Got from cache ' + iPath)
    return y['parsed']
  else:
    log.info('Save in cache ' + iPath)
    log.info(y['sha1'])
    log.info(hashres)
  

class ProcDirectives():
  def __init__(self, iContent):
    self.defines = {}
    self.line = ''
    self.iterContent = iter(iContent.splitlines())
    self.result = []
    for self.line in self.iterContent:
      if '`' not in self.line:
        self.result.append(self.line)
      else:
        block = self.prepBranch()
        if block:
          for line in block:
            self.line = line
            self.prepReplace()
            self.prepDefine()
            self.result.append(self.line)
        else:
            self.prepReplace()
            self.prepDefine()
            self.result.append(self.line)
            
  def getResult(self):
    return '\n'.join(self.result)


  
  def prepReplace(self):
    'Return a string with replacement accord to defined macros'
    words = self.line.split()
    for word in words:
      if '`' == word[0]:
        val = self.defines.get(word[1:])
        if val:
          self.line = re.sub(word, val, self.line)
  
  def prepDefine(self):
    if '`define' in self.line:
      words = self.line.split()
      qty = len(words)
      if qty == 3:
        self.defines.update({words[1]:words[2]})
      elif qty == 2:
        self.defines.update({words[1]: ''})
      else:
        log.warning('Error in preprocess parsing')
  
  
  def prepBranch(self):
    if '`ifdef' in self.line:
      origin = []
      origin.append(self.line)
      while True:
        try:
          line = self.iterContent.next()
          origin.append(line)
          if '`endif' in line:
            break
        except StopIteration:
          log.warning('Error in preprocess parsing')
          break
    else: # not a branch
      return
    
    branch = []
    beginWords = set(['`ifdef', '`elif', '`else'])
    endWords = set(['`elif', '`else', '`endif'])
    matched = False
    for line in origin:
      words = set(line.split())
      endBlock = endWords & words
      if matched and endBlock:
#        branch.append(line)
        break
      elif matched:
        branch.append(line)
      else:
        beginBlock = beginWords & words
        if '`else' in words or beginBlock and words & set(self.defines.keys()):
          matched = True
#          branch.append(line)

    if branch:          
      return branch
    else:
      return origin
    
    
 
@log_call
def parseFile(iPathFile):
  '''
    Input: path to file;
    Output: dictionary {key = module name, value = [path to file, instance1, instance2,...]}
  '''
  if os.path.splitext(iPathFile)[1] not in ['.v']:
    return 
  contentFull = readContent(iPathFile)
  res = checkIfParsed(contentFull, iPathFile)
  if res:
    for k, v in res.iteritems():
      v[0] = os.path.abspath(v[0])
    return res
  content = removeComments(contentFull)
  content = ProcDirectives(content).getResult()
  content = removeFunc(content)
  try:
    parsed = getInstances(content)
  except InstanceException:
    log.warning("Can't find module body in " + oneFile)
    #continue
  for i in parsed:
     parsed[i].insert(0, iPathFile)
  saveParsed(contentFull, parsed)
  return parsed


@log_call
def parseFiles(iPathFiles):
  '''
    Input: list of path to files;
    Output: dictionary {key = module name, value = [path to file, instance1, instance2,...]};
  '''
  parsed = {}
  if iPathFiles:
    for oneFile in iPathFiles:
      if os.path.splitext(oneFile)[1] not in ['.v']:
        continue 
      try:
        parsedNew = parseFile(oneFile)
        parsed.update(parsedNew)
      except IOError:
        log.warning("Can't open file: "+oneFile)
  return parsed


@log_call
def formRegexp():
  identifier = Word(alphas+"_", alphanums+"_$")
  moduleInstance = identifier
  instanceName = identifier
  params = Literal('#') + nestedExpr("(", ")")
  ports = nestedExpr("(", ")")
  regexp = WordStart() + moduleInstance.setResultsName('moduleInst') +\
        Optional(params.setResultsName('params')) +\
        instanceName.setResultsName('instName') +\
        Optional(params.setResultsName('params')) +\
        ports.setResultsName('ports') + Literal(';')
  return regexp


@log_call
def getInstances(iString):
  '''
    Input: file content without comment and verilog2001 functions definition;
    Output: instances as a dictionary {key = module name, value = list of instances}; 
  '''
  instances = {}

  statements = iString.split(';')
  for statement in [i+';' for i in statements]:
    log.debug('Parsing statement=\n'+statement)
    regexp = formRegexp()
    for tokens in regexp.searchString(statement):
      log.debug('''\
      moduleInst={0}
      params={1}
      instName={2}
      ports={3}
      '''.format(tokens.get('moduleInst'),
          tokens.get('params'),
          tokens.get('instName'),
          tokens.get('ports')))
      
      moduleInst = tokens.get('moduleInst')
      if moduleInst == 'module':
        moduleName = tokens.get('instName') 
        instances[moduleName] = []
      else:  
        try:
          if moduleInst not in instances[moduleName]:
            instances[moduleName].append(moduleInst)
        except NameError:
          InstanceException('Can\'t find module body')
      
  return instances

    
@log_call
def getUndefInst(iParsed):
  '''
    Input: dictionary {key = module name, value = [path to file, instance1, instance2,...]};
    Output: dictionary {key = instance name, value = path to file}; 
  '''
  undefInstances = {}
  for module in iParsed:
    # [1:] - exclude path to file
    for instance in iParsed[module][1:]:
      if not iParsed.get(instance):
         undefInstances[instance] = iParsed[module][0]
  return undefInstances


@log_call
def instTreeDep(iTop, iSrc):
  '''
    Input: iTop - parsed top module 
      a dictionary {key=module name, value=[path, instance1, instance2....]};
    Output: list of parsed modules
      [iTop_parsed, inst1_parsed, inst2_parsed,...];
  '''
  dep = [iTop]
  undef = {}
  for module in dep: # iterate over a list of dictionaries
    moduleParsedVal = module.values()[0]
    for instance in moduleParsedVal[1:]: # over a list of instances
      try:
        dep.append({instance:iSrc[instance]})
      except KeyError:
        undef[instance] = moduleParsedVal[0] # key=instance, val=path to parsed file
    if len(dep) > len(iSrc):
      log.warning('Cyclic dependencies!')
      break
  return dep, undef

  

@log_call
def _runMoreProc(proc, num):
  cnt = 0
  for i in proc:
    if i.poll() == None:
      cnt += 1
  if cnt > num:
    return False
  else:
    return True


@log_call
def parseFilesMultiproc(iFiles):
  proc = []
  for i, f in enumerate(iFiles):
    while(True):
      if _runMoreProc(proc, 13):
        break
      else:
        time.sleep(0.2)
    path = os.path.dirname(__file__)+'/instance_proc.py'
    p = subprocess.Popen('python {0} '.format(path) + f, stdout = subprocess.PIPE)
    proc.append(p)
    
  parsed = {}  
  while(True):
    cnt = 0
    for i, e in enumerate(proc):
      if e.poll() != None:
        cnt += 1
      else:
        time.sleep(0.1)
        break

    if cnt == len(proc):
      for i in proc:
        res = eval(i.communicate()[0])
        if res:
          parsed.update(res)    
      break  
  
  return parsed



@log_call
def resolveUndef(iInstance, iInFile, _parsed = {}):
  mayBe = _parsed.get(iInstance)
  if mayBe:
    return {iInstance: mayBe}
  
  afile = build.getFile(iInstance = iInstance, iInFile = iInFile)
  if afile:
    parsedFile = parseFile(afile)
    _parsed.update(parsedFile)
    if parsedFile.get(iInstance):
      return parsedFile
     
  files = build.getFile() #return all cache
  parsedFiles = parseFilesMultiproc(files)
  _parsed.update(parsedFiles)
  val = parsedFiles.get(iInstance)
  if val:
    return {iInstance:val}


  
@log_call
def anal(iParsed, _undef = set()):
  log.info('Analyzing...')
  for module in iParsed:
    val = iParsed[module]
    inFile = val[0]
    for instance in val[1:]:
      if instance in _undef:
        continue
      if not iParsed.get(instance):
        parsed = resolveUndef(iInstance = instance, iInFile = inFile)
        if not parsed:
          log.warning("Undefined instance="+instance+' in file='+inFile)
          _undef.add(instance)
        else:
          return parsed


@log_call
def analyze(iPathFiles, ioParsed = {}, iUndefInst = {}):
  '''
    Input: 
      iPathFiles - list of paths;
      iUndefInst - dictionary 
        {key = instance name, value = path to file};
    Inout: 
      ioParsed - dictionary 
        {key = module name, value = [path to file, instance1, instance2,...]};
    Output:
      undefInst - dictionary
        {key = instance name, value = path to file};
  '''
  log.info('Analyzing dependences...')
  parsed = parseFiles(iPathFiles=iPathFiles)
  log.debug('PARSED: ' + str(parsed))
  undefInst = {}
  # first call
  if not iUndefInst:
    log.debug('first call')
    undefInst = getUndefInst(parsed)
    ioParsed.update(parsed)
    return undefInst
  
  # next calls
  for undef in iUndefInst:
    log.debug('next calls')
    try:
      top = {undef: parsed[undef]}
      parsedAll = {}
      parsedAll.update(parsed)
      parsedAll.update(ioParsed)
      dep, undefNew = instTreeDep(top, parsedAll)
      for d in dep: # update only with necessary instances
        ioParsed.update(d)  
      undefInst.update(undefNew)
    except KeyError:
      undefInst[undef] = iUndefInst[undef]
  return undefInst



    




