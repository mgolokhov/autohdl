import re
import os
import sys
import subprocess

from autohdl.lib.pyparsing import *
from hdlLogger import *

import build



class InstanceException(Exception):
  def __init__(self, iString):
    self.string = iString
  def __str__(self):
    return self.string


def removeComments(ioString):
  ioString = ioString.replace('\t', '    ')
  log.debug('def removeComments IN ioString=\n'+ioString)
  withoutQuotedStr = ioString
  for tokens in QuotedString(quoteChar='"').searchString(withoutQuotedStr):
    tok = tokens[0]
    log.debug('quoted string= ' + tok)
    withoutQuotedStr = withoutQuotedStr.replace(tok, '', 1)
  for tokens in cppStyleComment.searchString(withoutQuotedStr):
    tok = tokens[0]
    log.debug('comment= ' + tok)
    ioString = ioString.replace(tok, '', 1)
  log.debug('def removeComment OUT ioString=\n'+ioString)
  return ioString
  

def removeFunc(content):
  return re.sub(r'\sfunction\s.*?\sendfunction\s', '', content, flags=re.M|re.S)


def readContent(iPathFile):
  f = open(iPathFile, 'r')
  content = f.read()
  f.close() 
  return content 
  
  
def parseFile(iPathFile):
  '''
    Input: path to file;
    Output: dictionary {key = module name, value = [path to file, instance1, instance2,...]}
  '''
  log.debug('def parseFile IN iPathFile='+str(iPathFile))
  if os.path.splitext(iPathFile)[1] not in ['.v']:
    return 
  content = readContent(iPathFile)
  content = removeComments(content)
  content = removeFunc(content)
  try:
    parsed = getInstances(content)
  except InstanceException:
    log.warning("Can't find module body in " + oneFile)
    #continue
  for i in parsed:
     parsed[i].insert(0, iPathFile)
  log.debug('def parseFile OUT parsed='+str(parsed))
  return parsed


def parseFiles(iPathFiles):
  '''
    Input: list of path to files;
    Output: dictionary {key = module name, value = [path to file, instance1, instance2,...]};
  '''
  log.debug('def parseFiles IN iPathFiles='+str(iPathFiles))
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
  log.debug('def parseFiles OUT parsed='+str(parsed))
  return parsed


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


def getInstances(iString):
  '''
    Input: file content without comment and verilog2001 functions definition;
    Output: instances as a dictionary {key = module name, value = list of instances}; 
  '''
  log.debug('def getInstances IN iString=\n'+iString)
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
      
  log.debug('def getInstances OUT instances='+str(instances))
  return instances

    
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


def instTreeDep(iTop, iSrc):
  '''
    Input: iTop - parsed top module 
      a dictionary {key=module name, value=[path, instance1, instance2....]};
    Output: list of parsed modules
      [iTop_parsed, inst1_parsed, inst2_parsed,...];
  '''
  log.debug('instTreeDep IN iTop='+str(iTop)+'; iSrc='+str(iSrc))
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
  log.debug('def instTreeDep OUT dep: '+str(dep)+' undef: '+str(undef))
  return dep, undef

  

def _runMoreProc(proc, num):
  cnt = 0
  for i in proc:
    if i.poll() == None:
      cnt += 1
  if cnt > num:
    return False
  else:
    return True


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
  log.debug('def analyze IN iPathFiles='+str(iPathFiles)+' ioParsed'+str(ioParsed)+' iUndefInst'+str(iUndefInst))
  log.info('Analyzing dependences...')
  parsed = parseFiles(iPathFiles=iPathFiles)
  log.debug('PARSED: ' + str(parsed))
  undefInst = {}
  # first call
  if not iUndefInst:
    log.debug('first call')
    undefInst = getUndefInst(parsed)
    ioParsed.update(parsed)
    log.debug('def analyze OUT undefInst='+str(undefInst))
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
  log.debug('def analyze OUT undefInst='+str(undefInst))
  return undefInst



    




