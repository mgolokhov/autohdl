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

from hdlLogger import *


class SynthesisException(Exception):
  def __init__(self, iString):
    self.string = iString
  def __str__(self):
    return self.string
  


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
                          netlist=iPrj['pathSynthesis']+'/'+iPrj['topModule'],
                          src_files=iPrj['srcFiles'])
  f = open(iPrj['pathScript'], 'w')
  f.write(iPrj['scriptContent'])
  f.close()
  
  
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


def parseLog(iPrj, iSilent = False):
  log.debug('def parseLog IN')
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


def run_synplify_batch(iPrj):
  run = '"%s" %s %s %s %s' % (iPrj['pathTool'],
                '-product synplify_premier',
                '-licensetype synplifypremier',
                '-batch', iPrj['pathScript'])
  subprocess.Popen(run)

  while True:
    time.sleep(3)
    try:
      loge = open(iPrj['pathLog'], 'r')
    except IOError as e:
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


def run_synplify_gui(iPrj):
  subprocess.call([iPrj['pathTool'], iPrj['pathSctipt']])


def runTool(iPrj, iSilent):
  '''
  Runs external tool for synthesis
  '''
  log.debug('def runTool IN')
  os.chdir(iPrj['pathSynthesis'])
  
  if iPrj['mode'] == 'synplify_batch':
    run_synplify_batch(iPrj = iPrj)
    parseLog(iPrj = iPrj, iSilent = iSilent)
  elif iPrj['mode'] == 'synplify_gui':
    run_synplify_gui(iPrj=iPrj)
  
  os.chdir(iPrj['pathWas'])


def run(iTopModule, iMode = 'synplify_batch', iSilent = True):
  log.debug('def run IN iMode='+iMode+' iTopModule='+iTopModule)
  # changing current location to synthesis directory
  prj = getStructure(iTopModule = iTopModule, iMode = iMode)
  runTool(iPrj = prj, iSilent = iSilent)
  log.info('Synthesis done!')  


