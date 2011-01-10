import re
import os
import sys
from autohdl.lib.pyparsing import *

from hdlLogger import *


class InstanceException(Exception):
  def __init__(self, iString):
    self.string = iString
  def __str__(self):
    return self.string


def removeComments(ioString):
  log.debug('def removeComments<= ioString=\n'+ioString)
  withoutQuotedStr = ioString
  for tokens in QuotedString(quoteChar='"').searchString(withoutQuotedStr):
    log.debug('quoted string= ' + tokens[0])
    withoutQuotedStr = withoutQuotedStr.replace(tokens[0], '', 1)
  for tokens in cppStyleComment.searchString(withoutQuotedStr):
    log.debug('comment= ' + tokens[0])
    ioString = ioString.replace(tokens[0], '', 1)
  log.debug('def removeComments<= ioString=\n'+ioString)
  return ioString
  

def removeFunc(content):
  return re.sub(r'function.*endfunction', '', content, flags=re.M|re.S)


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
  content = readContent(iPathFile)
  content = removeComments(content)
  content = removeFunc(content)
  try:
    parsed = getInstances(content)
  except InstanceException:
    log.warning("Can't find module body in " + oneFile)
    continue
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
  for oneFile in iPathFiles:
    parsedNew = parseFile(oneFile)
    parsed.update(parsedNew)
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


def formInstDic(iTokens, ioInstances):
  '''
    Refreshes a dictionary of ioInsrances {key = module name, value = list of instances};
    Input: tokens after parsing;
    Inout: ioInstances;
  '''
  moduleInst = iTokens.get('moduleInst')
  if moduleInst == 'module':
    moduleName = iTokens.get('instName') 
    ioInstances[moduleName] = []
  else:  
    try:
      ioInstances[moduleName].append(moduleInst)
    except NameError:
      InstanceException('Can\'t find module body')


def getInstances(iString):
  '''
    Input: file content without comment and verilog2001 functions definition;
    Output: instances as a dictionary {key = module name, value = list of instances}; 
  '''
  log.debug('def getInstances IN iString=\n'+iString)
  instances = {}

  regexp = formRegexp()
  for tokens in regexp.searchString(iString):
    log.debug('''\
    moduleInst={0}
    params={1}
    instName={2}
    ports={3}
    '''.format(tokens.get('moduleInst'),
        tokens.get('params'),
        tokens.get('instName'),
        tokens.get('ports')))
    
    formInstDic(iTokens = tokens, ioInstances = instances)

  log.debug('def getInstances OUT instances='+str(instances))
  return instances

    
def undefFirstCall(iFiles):
  '''
  Input: list of full paths;
  Output: (parsed, undefInstances);
    parsed - dictionary key=module name, value=[path, instance1, instance2....];
    undefInstances - set of tuples (path, undefined instance);
  '''
  log.debug('def undefFirstCall IN iFiles='+str(iFiles))
  parsed = parseFiles(iFiles)
  undefInstances = set()
  for module in parsed:
    # exclude path to file
    for instance in parsed[module][1:]:
      if not parsed.get(instance):
        undefInstances.add((parsed[module][0], instance))
  return parsed, undefInstances


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


def analyze(iPathFiles, iParsed = {}, iUndefInstances = {}):
  parsed = parseFiles(iPathFiles)
  parsed.update(iParsed)
  undef = getUndefInst(parsed)

def getUndef(iFiles, iParsed = {}, iUndefInstances = set()):
  """
  iFiles as a list even there is one file;
  """
  log.debug('def getUndef IN iFiles='+str(iFiles)+' iParsed='+str(iParsed)+' iUndefInstances='+str(iUndefInstances))
  parsedNew, undefNew = undefFirstCall(iFiles)

  undefFinally = set()
  for instance in undefNew:
    #if parsed - reduce undef set, else just leave
    if not iParsed.get(instance[1]):
      undefFinally.add(instance)
  
  iParsed.update(parsedNew)

  for instance in iUndefInstances: #tuple (pathFile, instanceName)
    #instance should be parsed
    if not iParsed.get(instance[1]):
      log.warning('Undefined instance "' + instance[1] + '" in file: ' + instance[0])
  log.debug('def getUndef OUT parsed='+str(iParsed)+' undefFinally='+str(undefFinally))    
  return iParsed, undefFinally


