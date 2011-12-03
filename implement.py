import os
import shutil
import subprocess
import sys

from autohdl import hdlGlobals
from autohdl import toolchain
from autohdl import structure


from hdlLogger import log_call, logging
log = logging.getLogger(__name__)


@log_call
def bit2mcs(config):
  try:
    if config['size']:
      proc = '{tool} -u 0 {top} -s {size} -w'.format(tool = toolchain.getPath('ise_promgen'),
                                                     top = '../implement/'+config['top']+'.bit',
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
  implPath = os.path.abspath('../implement')
  synPath = os.path.abspath('../synthesis')
  clean(implPath)
  top = structure.search(synPath, iOnly = [config['top']+'\.edf'])
  if top:
    top = top[0]
  else:
    log.error('Cant find netlist, try sythesis step first.')
    sys.exit()
    
  ucfSymplicity = structure.search(synPath, iOnly=['\.ucf'], iIgnore=hdlGlobals.ignoreRepoFiles)
  ucf = ucfSymplicity[0] or config['ucf']

  shutil.copyfile(ucf, implPath + config['top']+'.ucf')
  shutil.copyfile(top, implPath + config['top']+'.edf')
  for i in config['depNetlist']:
    shutil.copyfile(i, implPath + os.path.split(i)[1])
  
  
  os.chdir(implPath)
  try:
    subprocess.check_call(('{xflow} -implement balanced.opt'
                           ' -config bitgen.opt {netlist}.edf').format(xflow=toolchain.getPath('ise_xflow'),
                                                                       netlist=config['top']))
  except subprocess.CalledProcessError as e:
    log.error(e)
    sys.exit()

  bit2mcs(config['top'])
    
  log.info('Implementation done')

