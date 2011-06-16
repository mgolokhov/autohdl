import re
import os
import sys
import time
import subprocess
import hashlib


from lib.pyparsing import *
from hdlLogger import log_call, logging
from lib.yaml.error import YAMLError
log = logging.getLogger(__name__)

import lib.yaml as yaml
import build

import copy

class InstanceException(Exception):
  def __init__(self, iString):
    self.string = iString
  def __str__(self):
    return self.string


def getRegexp():
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

regexp = getRegexp()    
    
    
class ParseFile(object):
  '''
  '''
  def __init__(self, iPath):
    if os.path.splitext(iPath)[1] in ['.v']:
      self.path      = os.path.abspath(iPath)
      self.pathCache = self.getPathCache() 
      self.content   = self.readContent()
      self.parsed    = {}
      self.cacheable = True
      self.includes  = {'paths': [], 'sha': hashlib.sha1()} 
      self.file_sha  = ''
#      log.debug('ParseFile __init__:\n'+str(self))
      
      if not self.getInCache():
        self.parseFile()
        if self.cacheable:
          self.saveInCache()
      else:
        log.info("Got from cache " + str(self.parsed))
        
    else:
      self.parsed = {} # just a stub for getResult()
      log.warning("Supports only verilog files (extensions: .v). Ignoring " + iPath)



  def __str__(self):
    return vars(self)
#    return '\n'.join([str(i) for i in vars(self)])
   

#  @log_call 
  def getResult(self):
    for k in self.parsed:
      self.parsed[k]['path'] = os.path.abspath(self.parsed[k]['path'])
    return self.parsed
  
  
#  @log_call 
  def readContent(self):
    try:
      with open(self.path, 'r') as f:
        return f.read()
    except IOError:
      raise InstanceException('Cannot open file: ' + self.path)

  
#  @log_call 
  def getPathCache(self):
    'Default storage in folder <dsnName>/resource/parsed'
    # transform path to src file in fileName
    relPath = os.path.relpath(self.path, '../script')
    name = relPath.replace('\\', '/').replace('/', '_').replace('.', '_')
    dir = '../resource/parsed/'
    if not os.path.exists(dir):
      os.mkdir(dir)
    return '../resource/parsed/' + name


#  @log_call 
  def getInCache(self):
    '''
    Return true if got match in cache, assign result to self.parsed
    '''
    # calc hash for main src file
    h = hashlib.sha1()
    h.update(self.content)
    self.file_sha = h.hexdigest()
    
    try:
      with open(self.pathCache, 'r') as f:
        y = yaml.load(f)
    except (IOError, YAMLError) as exp:
      log.debug(exp)
      return False


    if self.file_sha != y['file_sha']:
      return False
    
    # calc hash for includes
    if y.get('includes'):
      h = hashlib.sha1()
      for path in y['includes']['paths']:
        try:
          with open(path, 'r') as f:
            h.update(f.read())
        except IOError as exp:
          log.error(exp)
          return False
      includes_sha = h.hexdigest()
      if includes_sha != y['includes']['sha']:
        return False
    self.parsed = y['parsed']
    return True


#  @log_call 
  def removeComments(self):
    self.content = self.content.replace('\t', '    ')
    withoutQuotedStr = self.content
    for tokens in QuotedString(quoteChar='"').searchString(withoutQuotedStr):
      tok = tokens[0]
      log.debug('quoted string= ' + tok)
      withoutQuotedStr = withoutQuotedStr.replace(tok, '', 1)
    for tokens in cppStyleComment.searchString(withoutQuotedStr):
      tok = tokens[0]
      log.debug('comment= ' + tok)
      self.content = self.content.replace(tok, '', 1)


#  @log_call 
  def addIncludes(self, _unresolved = []):
    'BUGAGA: maximum recursion depth exceeded' 
    'cache calculates *per each* include'
    includeFiles = re.findall(r'`include\s+".*?"', self.content)
    contineProc = set(includeFiles)-set(_unresolved)
    if not contineProc:
      self.includes['sha'] = self.includes['sha'].hexdigest()
      return
    searchPaths = build.getParam(iKey = 'include_path', iDefault = '.')
    searchPaths = searchPaths.split(';')
    searchPaths = [os.path.abspath(os.path.join('../resource', i)) for i in searchPaths]
    searchPaths += ['../src']
    incl = {}
    for include in includeFiles:
      if include in _unresolved:
        continue
      file = re.search(r'"(.*?)"', include).group(1)
      for path in searchPaths:
        fullPath = os.path.join(path, file)
        if os.path.exists(fullPath):
          incl.update({include:fullPath})
          break
      if not incl.get(include):
        log.warning('Cannot resolve ' + include)
        _unresolved.append(include)
        self.cacheable = False

    self.includes['paths'] += incl.values() 
    for inclLine, inclFile in incl.iteritems():
      try:
        with open(inclFile, 'r') as f:
          inclContent =  f.read()
          self.includes['sha'].update(inclContent)
          self.content = self.content.replace(inclLine, inclContent)
      except:
        # damaged should not be saved in cache
        log.warning('Cannot resolve ' + inclLine)
        _unresolved.append(inclLine)
        self.cacheable = False
    self.removeComments()
    return self.addIncludes()


#  @log_call 
  def removeFunc(self):
    self.content = re.sub(r'\sfunction\s.*?\sendfunction\s', '', self.content, flags=re.M|re.S)


#  @log_call 
  def parseFile(self):
    '''

    '''
    self.removeComments()
    self.addIncludes()
    self.content = ProcDirectives(self.content).getResult()
    self.removeFunc()
    try:
      self.getInstances()
    except InstanceException as exp:
      log.error(exp)


#  @log_call 
  def getInstances(self):
    '''
      Input: file content without comment and verilog2001 functions definition;
      Output: instances as a dictionary {key = module name, value = list of instances}; 
      {key = moduleName, value = {'path'      : 'fullPath',
                                  'instances' : (set of instances)}
    '''
    statements = self.content.split(';')
    # bugaga could be generator _splitBySemicolon()
    for statement in [i+';' for i in statements]:
      log.debug('Parsing statement=\n'+statement)
      for tokens in regexp.searchString(statement):
        log.debug('''\
        moduleInst={0}
        params={1}
        instName={2}
        ports={3}
        '''.format(
            tokens.get('moduleInst'),
            tokens.get('params'),
            tokens.get('instName'),
            tokens.get('ports')))
        
        moduleInst = tokens.get('moduleInst')
        if moduleInst == 'module':
          moduleName = tokens.get('instName') 
          self.parsed[moduleName] = {'path': os.path.relpath(self.path), 'instances': set()}
        else:  
          try:
            self.parsed[moduleName]['instances'].add(moduleInst)
          except NameError:
            self.cacheable = False
            InstanceException('Cannot find module body in file ' + self.path)


#  @log_call 
  def saveInCache(self):
    with open(self.pathCache, 'w') as f:
      cache = {
               'parsed'   : self.parsed,
               'file_sha' : self.file_sha,
               'includes' : self.includes
               }
      yaml.dump(cache, f, default_flow_style = False)


###############################################################################
###############################################################################



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
    

##################################################################################
##################################################################################
##################################################################################

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
        parsedNew = ParseFile(oneFile).getResult()
        parsed.update(parsedNew)
      except IOError:
        log.warning("Can't open file: "+oneFile)
  return parsed

    
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
    parsedFile = ParseFile(afile).getResult()
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
def analyze(iParsed, _undef = set()):
  log.info('Analyzing...')
  for module in iParsed:
    val = iParsed[module]
    inFile = val['path']
    for instance in val['instances']:
      if instance in _undef:
        continue
      if not iParsed.get(instance):
        parsed = resolveUndef(iInstance = instance, iInFile = inFile)
        if not parsed:
          log.warning("Undefined instance="+instance+' in file='+inFile)
          _undef.add(instance)
        else:
          return parsed





    




