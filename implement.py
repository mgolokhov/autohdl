import glob
import os
import shutil
import subprocess
import sys

from autohdl import hdlGlobals
from autohdl import toolchain
from autohdl import structure
from autohdl.hdlGlobals import synthesisPath, implementPath
import time

from hdlLogger import log_call, logging
from autohdl import progressBar

log = logging.getLogger(__name__)


@log_call
def bit2mcs(config):
  try:
    if config['size']:
      proc = '{tool} -u 0 {top} -s {size} -w'.format(tool = toolchain.Tool().get('ise_promgen'),
                                                     top = config['top']+'.bit',
                                                     size = config['size'])
      subprocess.check_call(proc)
    else:
      log.warning('PROM size was not set')
  except subprocess.CalledProcessError as e:
    log.error(e)
    sys.exit()

@log_call
def clean(path):
  try:
    if os.path.exists(path):
      for root, dirs, files in os.walk(path):
        for f in files:
          if os.path.splitext(f)[1] not in ['.mcs', '.bit']:
            os.remove(os.path.join(root, f))
  except OSError:
    log.warning("Can't clean folder "+path)
  if not os.path.exists(path):
    os.makedirs(path)



@log_call
def run(config):
  log.info("Implementation stage...")
  implPath = os.path.abspath(implementPath)+'/'
  synPath = os.path.abspath(synthesisPath)+'/'
  clean(implPath)
  top = os.path.join(synPath, config['top']+'.edf')
  progressBar.run()
  cnt = 50
  while not os.path.exists(top) or not cnt:
    cnt -= 1
    time.sleep(1)
  progressBar.stop()
  if not cnt:
    log.error('Cant find netlist, try sythesis step first.')
    sys.exit(1)
    
  ucfSymplicity = structure.search(synPath, onlyExt = '.ucf', ignoreDir = hdlGlobals.ignoreRepoDir)
  ucf = ucfSymplicity[0] or config['ucf']

  for i in config.get('depNetlist', []):
    shutil.copyfile(i, implPath + os.path.split(i)[1])
  shutil.copyfile(ucf, implPath + config['top']+'.ucf')
  shutil.copyfile(top, implPath + config['top']+'.edf')

  
  os.chdir(implPath)
  while not os.path.exists(config['top']+'.edf'):
    print 'cant find file: ', config['top']
    time.sleep(0.1)

  try:
    subprocess.check_call(('{xflow} -implement balanced.opt'
                           ' -config bitgen.opt {netlist}.edf').format(xflow=toolchain.Tool().get('ise_xflow'),
                                                                       netlist=config['top']))
  except subprocess.CalledProcessError as e:
    log.error(e)
    sys.exit()

  bit2mcs(config)
    
  log.info('Implementation done')

