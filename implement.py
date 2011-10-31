import os
import shutil
import subprocess
import sys
import hdlGlobals

import toolchain
import structure


from hdlLogger import log_call, logging
log = logging.getLogger(__name__)


@log_call
def bit2mcs(iTopModule, iSize):
  proc = '{tool} -u 0 {top} -s {size} -w'.format(tool = toolchain.getPath('ise_promgen'),
                                                 top = iTopModule,
                                                 size = iSize)
  subprocess.call(proc)


@log_call
def run(config):
  try:
    if os.path.exists('../implement'):
      for root, dirs, files in os.walk('../implement'):
        for f in files:
          if os.path.splitext(f)[1] not in ['.mcs', '.bit']:
            os.remove(os.path.join(root, f))
#      shutil.rmtree('../implement')
  except OSError:
    log.warning("Can\'t clean folder ../implement")
  if not os.path.exists('../implement'):
    os.makedirs('../implement')  
    
  top = structure.search(iPath = '../synthesis', iOnly = [config['top']+'\.edf'])
  if top:
    top = top[0]
  else:
    log.error('Cant find netlist, try sythesis step first.')
    sys.exit()
    
  netlists = structure.search(iPath = '../src', iOnly = ['\.edf', '\.ngc'], iIgnore = hdlGlobals.ignore )
  ucfSymplicity = structure.search(iPath='../synthesis', iOnly=['\.ucf'], iIgnore=hdlGlobals.ignore)
  ucf = ucfSymplicity[0] or config['ucf']

  shutil.copyfile(ucf, '../implement/'+config['top']+'.ucf')
  shutil.copyfile(top, '../implement/'+config['top']+'.edf')
  for i in netlists:
    shutil.copyfile(i, '../implement/'+os.path.split(i)[1])
  
  
  os.chdir('../implement')
  subprocess.call(('{xflow} -implement balanced.opt'
                   ' -config bitgen.opt {netlist}.edf').format(xflow=toolchain.getPath('ise_xflow'),
                                                               netlist=config['top']))
  
  if config['size']:
    bit2mcs(config['top'], config['size'])
    
  log.info('Implementation done')

