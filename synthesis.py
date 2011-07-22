import os
import sys
import re
import shutil
import subprocess
import time

import structure
import toolchain
import build
import hdlGlobals

import logging
from hdlLogger import log_call
log = logging.getLogger(__name__)


class SynthesisException(Exception):
  def __init__(self, iString):
    self.string = iString
  def __str__(self):
    return self.string
  

@log_call
def _getIncludePath(iPrj):
    includePath = ['.']
    for i in range(11):
      incl = build.getParam('IncludeDir'+str(i))
      if not incl:
        break
      includePath.append(incl)
    return ';'.join(includePath) 

  
@log_call
def getIncludePath(iPrj):
  return build.getParam('include_path')
  

@log_call
def setParams(iPrj):
  device = build.getParam('DEVICE')
  part = 'xc' + device[:-5]
  package = device[-5:]
  family = build.getParam('FAMILY')
  technology = family.split()[1] # e.g. 'Xilinx11x SPARTAN3E'
  iPrj['scriptContent'] = iPrj['scriptContent'].format(
                          device=device,
                          part=part,
                          package=package,
                          technology=technology,
                          topModule=iPrj['topModule'],
                          netlist=iPrj['pathSynthesis']+'/'+iPrj['topModule']+'.edf',
                          src_files=iPrj['srcFiles'],
                          includePath=getIncludePath(iPrj))
  f = open(iPrj['pathScript'], 'w')
  f.write(iPrj['scriptContent'])
  f.close()

  
@log_call
def setSrc(iPrj):
  ignore = hdlGlobals.ignore
  only = []
  filesMain = structure.search(iPath = '../src', iIgnore = ignore, iOnly = only)
  filesDep = structure.getDepSrc(iSrc = filesMain, iIgnore =ignore, iOnly = only)
  srcFiles = filesMain + list(filesDep)
  iPrj['srcFiles'] = '\n'.join(['add_file "{0}"'.format(i) for i in srcFiles])

  
@log_call  
def getStructure(iTopModule, iMode):
  prj = {}
  prj['pathTool']      = toolchain.getPath(iMode)
  prj['mode']          = iMode
  prj['topModule']     = iTopModule
  prj['pathSynthesis'] = '../synthesis'
  prj['pathScript']    = prj['pathSynthesis']+ '/synthesis.prj'
  prj['pathLog']       = prj['pathSynthesis'] + '/' + iTopModule + '.srr'
  prj['pathWas']       = os.getcwd().replace('\\','/')

  try:
    if os.path.exists(prj['pathSynthesis']):
      shutil.rmtree(prj['pathSynthesis'])
  except OSError as e:
    log.warning(e)
  
  for i in range(5):  
    if os.path.exists(prj['pathSynthesis']):
      break
    else:
      time.sleep(0.5)
      try:
        os.makedirs(prj['pathSynthesis'])
      except OSError as e:
        log.warning(e)

  synthesis_template = os.path.join(os.path.dirname(__file__), 'data', 'synplify')
  
  f = open(synthesis_template, 'r')
  prj['scriptContent'] = f.read()
  f.close()  
  
  setSrc(prj)
  setParams(prj)
  
  return prj


@log_call
def parseLog(iPrj, iSilent = False):
  logFile = os.path.abspath(iPrj['pathLog'])
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
      
    if errors or (not iSilent and warnings):
      subprocess.Popen(['notepad', logFile])
    log.info('See logfile: '+logFile)
    
  return logFile 



import xilinx_env

@log_call
def run_synplify_batch(iPrj):
  run = '"%s" %s %s %s %s' % (iPrj['pathTool'],
                '-product synplify_premier',
                '-licensetype synplifypremier',
                '-batch', iPrj['pathScript'])
  subprocess.Popen(run, env = xilinx_env.get())
  #TODO: stop waiting
  for i in range(13):
    time.sleep(3)
    try:
      loge = open(iPrj['pathLog'], 'r')
    except IOError as e:
      log.debug(e)
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


@log_call
def run_synplify_gui(iPrj):
  subprocess.call([iPrj['pathTool'], iPrj['pathScript']], env = xilinx_env.get())


@log_call
def runTool(iPrj, iSilent):
  '''
  Runs external tool for synthesis
  '''
  os.chdir(iPrj['pathSynthesis'])
  
  if iPrj['mode'] == 'synplify_batch':
    run_synplify_batch(iPrj = iPrj)
    parseLog(iPrj = iPrj, iSilent = iSilent)
  elif iPrj['mode'] == 'synplify_gui':
    run_synplify_gui(iPrj=iPrj)
  
  os.chdir(iPrj['pathWas'])


import glob
import subprocess

@log_call
def run(iTopModule = '', iMode = 'synplify_batch', iSilent = True):
  

#  try:
#    bat = glob.glob('c:\Xilinx\*\*\*settings32.bat')[0]
#    subprocess.call(bat)
#    log.info('Called '+ bat)
#  except Exception as exp:
#    log.error(exp)  
    
  # changing current location to synthesis directory
  iTopModule = iTopModule or build.getParam('TOPLEVEL')
  prj = getStructure(iTopModule = iTopModule, iMode = iMode)
  runTool(iPrj = prj, iSilent = iSilent)
  log.info('Synthesis done!')  


