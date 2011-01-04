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


def parseFiles(iFiles):
  log.debug('def parseFiles<= iFiles='+str(iFiles))
  parsed = {}
  for oneFile in iFiles:
    f = open(oneFile, 'r')
    content = f.read()
    f.close()
    pureContent = removeComments(content)
    pureContent = removeFunc(pureContent)
    try:
      parsedNew = getInstances(pureContent)
    except InstanceException:
      log.warning("Can't find module body in " + oneFile)
      continue
    for i in parsedNew:
       parsedNew[i].insert(0, oneFile)
    parsed.update(parsedNew)
  log.debug('def parseFiles=> parsed='+str(parsed))
  return parsed


def getInstances(iString):
  log.debug('def getInstances<= iString=\n'+iString)
  instances = {}

  identifier = Word(alphas+"_", alphanums+"_$")
  moduleInstance = identifier
  instanceName = identifier
  params = Literal('#') + nestedExpr("(", ")")
  ports = nestedExpr("(", ")")
  res = WordStart() + moduleInstance.setResultsName('moduleInst') +\
        Optional(params.setResultsName('params')) +\
        instanceName.setResultsName('instName') +\
        Optional(params.setResultsName('params')) +\
        ports.setResultsName('ports') + Literal(';')
        
  for tokens in res.searchString(iString):
    log.debug('moduleInst={0}\nparams={1}\ninstName={2}\nports={3}\n'.format(tokens.get('moduleInst'),
                                                                         tokens.get('params'),
                                                                         tokens.get('instName'),
                                                                         tokens.get('ports')))
    moduleInst = tokens.get('moduleInst')
    if moduleInst == 'module':
      moduleName = tokens.get('instName') 
      instances[moduleName] = []
    else:  
      try:
        instances[moduleName].append(moduleInst)
      except NameError:
        InstanceException('Can\'t find module body')

  log.debug('def getInstances=> instances='+str(instances))
  return instances

    
def undefFirstCall(iFiles):
  '''
  Input: list of full paths;
  Output: (parsed, undefInstances);
    parsed - dictionary key=module name, value=[path, instance1, instance2....];
    undefInstances - set of tuples (path, undefined instance);
  '''
  log.debug('def undefFirstCall<= iFiles='+str(iFiles))
  parsed = parseFiles(iFiles)
  undefInstances = set()
  for module in parsed:
    # exclude path to file
    for instance in parsed[module][1:]:
      if not parsed.get(instance):
        undefInstances.add((parsed[module][0], instance))
  return parsed, undefInstances


def getUndef(iFiles, iParsed = {}, iUndefInstances = set()):
  """
  iFiles as a list even there is one file;
  """
  log.debug('def getUndef<= iFiles='+str(iFiles)+' iParsed='+str(iParsed)+' iUndefInstances='+str(iUndefInstances))
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
  log.debug('def getUndef=> parsed='+str(iParsed)+' undefFinally='+str(undefFinally))    
  return iParsed, undefFinally




