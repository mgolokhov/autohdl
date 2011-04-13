import os
import sys
import re
import shutil
import subprocess
import time

import structure
import toolchain
import build

from hdlLogger import *


class Project(object):
  def __init__(self, iTopModule, iMode):
    self._pathTool      = toolchain.getPath(iMode)
    self._mode          = iMode
    self._topModule     = iTopModule
    self._pathSynthesis = '../synthesis'
    scriptName          = '/synthesis.prj'
    #self._pathScript    = self._pathSynthesis + scriptName
    self._pathScript    = './' + scriptName
    self._pathLog       = self._pathSynthesis + '/' + iTopModule + '.srr'
    self._pathWas       = os.getcwd().replace('\\','/')
  
    if os.path.exists(self._pathSynthesis):
      shutil.rmtree(self._pathSynthesis)
    os.makedirs(self._pathSynthesis)
#    shutil.copyfile(self._pathWas + scriptName, self._pathScript)
    os.chdir(self._pathSynthesis)
  
  
#  def __str__(self):
#    s = 
#    return
  
  def __enter__(self):
    return self

  def __exit__(self, type, value, traceback):
    os.chdir(self._pathWas)  
  
  @property
  def topModule(self):
    return self._topModule
  @property
  def pathSynthesis(self):
    return self._pathSynthesis
  @property
  def pathScript(self):
    return self._pathScript
  @property
  def pathTool(self):
    return self._pathTool
  @property
  def pathLog(self):
    return self._pathLog
  @property
  def pathWas(self):
    return self._pathWas
  @property
  def mode(self):
    return self._mode


class SynthesisException(Exception):
  def __init__(self, iString):
    self.string = iString
  def __str__(self):
    return self.string


def synchSrcFile(ioSrcFresh, ioScriptContent, iNum, iLine):
  match = re.search(r'add_file\s+?"(.*?)"', iLine)
  if match:
    res = match.group(1)
    if ioSrcFresh.count(res):
      ioSrcFresh.remove(res)
    else:
      if iLine.strip()[0] != '#':
        ioScriptContent[iNum] = '# {0} WAS DELETED'.format(iLine) 
    return True


def synchTopModule(ioScriptContent, iTopModule, iNum, iLine):
  match = re.search(r'set_option\s+?-top_module\s+?"(.*?)"', iLine)
  if match:
    ioScriptContent[iNum] = 'set_option -top_module "{0}"'.format(iTopModule)
    return True


def synchResultFile(ioScriptContent, iTopModule, iNum, iLine):
  match = re.search(r'project\s+?-result_file\s+"(.*?)"', iLine)
  if match:
#    resultFile = '%s/%s/%s%s' % (os.getcwd(), '../synthesis', iTopModule, '.edf')
#    resultFile = os.path.abspath(resultFile).replace('\\','/')
    resultFile = '../synthesis/'+iTopModule+'.edf'
    ioScriptContent[iNum] = 'project -result_file "{0}"'.format(resultFile)
    return True
  
  
def merge(ioSrcFresh, ioScriptContent, iTopModule):
  '''
  Precondition: items trimmed, files in in quotes
  '''
  lastEntry = 1
  for num, line in enumerate(ioScriptContent):
    if synchSrcFile(ioSrcFresh, ioScriptContent, num, line):
      lastEntry = num+1
      continue
    if synchTopModule(ioScriptContent, iTopModule, num, line):
      continue
    if synchResultFile(ioScriptContent, iTopModule, num, line):
      continue

  ioScriptContent[lastEntry:lastEntry] = ['add_file "{0}"'.format(k) for k in ioSrcFresh]


def getSrcFromFileSys(iDsn):
  log.debug('def getSrcFromFileSys IN iDsn=\n'+str(iDsn))
  ext = build.getSrcExtensions(iTag = 'synthesis_ext')
  ignore = ['\.svn/']
  only = ['\.'+i+'$' for i in ext]
  filesMain = structure.search(iPath = iDsn.pathRoot+'/src', iIgnore = ignore, iOnly = only)
  filesDep = structure.getDepSrc(iSrc = filesMain, iIgnore =ignore, iOnly = only)
  files = filesMain + list(filesDep)
  log.debug('getSrcFromFileSys OUT files'+str(files))
  return files  

  
def genScript(iPrj):
  log.debug('def genScript IN iPrj')#BUGAGA: __str__
  dsn = structure.Design(iPath = '..', iGen = True, iInit = False)
  if os.path.exists(iPrj.pathScript):
    log.info('Refreshing existing synthesis script')
    f = open(iPrj.pathScript, 'r')
  else:  
    log.info('Generating from default synthesis script')
    f = open('../resource/synthesis_default', 'r')
  scriptContent = f.read()
  f.close()
  
  contentAsList = scriptContent.split('\n')
  srcFiles = getSrcFromFileSys(dsn)
  merge(srcFiles, contentAsList, iTopModule = iPrj.topModule)
  scriptContent = '\n'.join(contentAsList)

  f = open(iPrj.pathScript, 'w')
  f.write(scriptContent)
  f.close()
  shutil.copy(iPrj.pathScript, '../synthesis/synthesis.prj')


def parseLog(iPrj, iSilent = False):
  log.debug('def parseLog IN')
  logFile = os.path.abspath(iPrj.pathLog)
  if os.path.exists(logFile):
    f = open(logFile, 'r')
    res = f.read()
    errors = res.count('@E:')
    warningsAll = res.count('@W:')
    ignoreWarnings = res.count('Initial value is not supported on state machine state')
    warnings = warningsAll - ignoreWarnings
    time.sleep(1)
    if errors:
      log.error('Synthesis ended with errors! Num: '+str(errors))
    elif warnings:
      log.warning('Synthesis ended with warnings! Num: '+str(warnings))
    else:
      log.info('Errors: '+str(errors)+'; Warnings: '+ str(warnings))
      
    if not iSilent and (errors or warnings):
      subprocess.Popen(['notepad', logFile])
    log.info('See logfile: '+logFile)
    
  return logFile 


def run_synplify_batch(iPathTool, iPathSctipt, iPrj):
  run = '"%s" %s %s %s %s' % (iPathTool,
                '-product synplify_premier',
                '-licensetype synplifypremier',
                '-batch', iPathSctipt)
  subprocess.Popen(run)

  while True:
    time.sleep(3)
    try:
      loge = open('../synthesis/'+iPrj.topModule+'.srr', 'r')
    except IOError, e:
      log.warning(e)
      continue
    if loge:
      break
    
  done = False
  while True:
    where = loge.tell()
    res = loge.readline()
    if res.find('Mapper successful!') != -1:
      done = True
    if res.endswith('\n'):
      print res
    elif done:
      break
    else:  
      loge.seek(where)
      time.sleep(1)
      
  loge.close()


def run_synplify_gui(iPathTool, iPathSctipt):
  subprocess.call([iPathTool, iPathSctipt])


def runTool(iPrj, iSilent):
  '''
  Runs external tool for synthesis
  '''
  log.debug('def runTool IN')
  os.chdir(iPrj.pathSynthesis)
  if iPrj.mode == 'synplify_batch':
    run_synplify_batch(iPathTool = iPrj.pathTool, iPathSctipt = '../synthesis/synthesis.prj', iPrj = iPrj)
    parseLog(iPrj = iPrj, iSilent = iSilent)
  elif iPrj.mode == 'synplify_gui':
    run_synplify_gui(iPathTool = iPrj.pathTool, iPathSctipt = iPrj.pathScript)


def run(iTopModule, iMode = 'synplify_batch', iSilent = False):
  log.debug('def run IN iMode='+iMode+' iTopModule='+iTopModule)
  # changing current location to synthesis directory
  with Project(iTopModule = iTopModule, iMode = iMode) as prj:
    genScript(iPrj = prj)
    runTool(iPrj = prj, iSilent = iSilent)
  log.info('Synthesis done!')  


