import os
import shutil
import subprocess
import time

from autohdl import toolchain, xilinx_env
from autohdl.hdlGlobals import synthesisPath

import logging
from autohdl.hdlLogger import log_call
import sys

log = logging.getLogger(__name__)


@log_call
def getIncludePath(iPrj):
  incl = (iPrj.get('include_path', ".") or '.')
  return ';'.join(incl)
  

@log_call
def setParams(iPrj):
  device = iPrj.get('device')
  part = 'xc' + device[:-5]
  package = device[-5:]
  family = iPrj.get('family')
  technology = family.split()[1] # e.g. 'Xilinx11x SPARTAN3E'
  synMacros = iPrj.get('SynMacros')# TODO: if you get None?
  print '-'*10, synMacros
  if synMacros:
    synMacros = ' '.join(synMacros)
  else:
    synMacros = ""

  iPrj['scriptContent'] = iPrj['scriptContent'].format(
                          device=device,
                          part=part,
                          package=package,
                          technology=technology,
                          topModule=iPrj['top'],
                          netlist=iPrj['top']+'.edf',
                          src_files=iPrj['srcFiles'],
                          synMacros=synMacros,
                          includePath=getIncludePath(iPrj))
  f = open(iPrj['pathScript'], 'w')
  f.write(iPrj['scriptContent'])
  f.close()

  
@log_call
def setSrc(iPrj):
  srcMain = iPrj.get('mainSrc')
  srcDep = iPrj.get('depSrc') or []
  ucf = iPrj.get('ucf')
  ucf = [ucf] if ucf else []
  #TODO: got duplicates, guess some bugs in structure
  srcFiles =  set([i.replace('\\', '/') for i in srcMain + srcDep + ucf])
  iPrj['srcFiles'] = '\n'.join(['add_file "{0}"'.format(i) for i in srcFiles])

  
@log_call  
def extend(prj):
  #TODO: convert all to abspath
  prj['pathTool']      = toolchain.Tool().get(prj['mode'])
  prj['pathSynthesis'] = synthesisPath
  prj['pathScript']    = prj['pathSynthesis']+ '/synthesis.prj'
  prj['pathLog']       = prj['top'] + '.srr'
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

  synthesis_template = os.path.join(os.path.dirname(__file__), 'data', 'template_synplify_prj')
  
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

    log.info('See logfile: '+logFile)
    if errors:
      log.error('Synthesis ended with errors! Num: '+str(errors))
      sys.exit(1)
    elif warnings:
      log.warning('Synthesis ended with warnings! Num: '+str(warnings))
    else:
      log.info('Errors: '+str(errors)+'; Warnings: '+ str(warnings))

    if errors or (not iSilent and warnings):
      subprocess.Popen(['notepad', logFile])

  return logFile


@log_call
def run_synplify_batch(iPrj):
  run = '"%s" %s %s %s %s' % (iPrj['pathTool'],
                '-product synplify_premier',
                '-licensetype synplifypremier',
                '-batch','synthesis.prj')
  subprocess.Popen(run, env = xilinx_env.get())
  loge = ''
  for i in range(13):
    time.sleep(3)
    try:
      loge = open(iPrj['pathLog'], 'r')
    except IOError as e:
      log.debug(e)
      continue
    if loge:
      break

  if not loge:
    log.error('Cant start synthesis see '+synthesisPath+'/stdout.log')
    return

  done = False
  while True:
    where = loge.tell()
    res = loge.readline()
    if res.find('Mapper successful!') != -1:
      done = True
    if '@E' in res:
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
  subprocess.check_call([iPrj['pathTool'], 'synthesis.prj'], env = xilinx_env.get())

@log_call
def runTool(iPrj, iSilent):
  """
  Runs external tool for synthesis
  """
  os.chdir(iPrj['pathSynthesis'])
  
  if iPrj['mode'] == 'synplify_batch':
    run_synplify_batch(iPrj = iPrj)
    parseLog(iPrj = iPrj, iSilent = iSilent)
  elif iPrj['mode'] == 'synplify_gui':
    run_synplify_gui(iPrj=iPrj)
  
  os.chdir(iPrj['pathWas'])


@log_call
def run(config):
  logging.info('Synthesis stage...')
  # changing current location to synthesis directory
  runTool(extend(config), iSilent = True)
  log.info('Synthesis done!')

