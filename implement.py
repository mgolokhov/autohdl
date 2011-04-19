import os
import sys
import shutil
import re
import subprocess
import filecmp

import toolchain
import synthesis
import structure
import build
from hdlLogger import *


def bit2mcs(iTopModule, iSize):
  proc = 'promgen -u 0 '+ iTopModule + ' -s ' + str(iSize) + ' -w'
  subprocess.call(proc)

def run(iTopModule = '', iFlashSize = ''):  
  log.debug('def run IN iTopModule='+iTopModule)  
  try:
    if os.path.exists('../implement'):
      shutil.rmtree('../implement')
  except OSError:
    log.warning('Can\'t delete folder ../implement')
  if not os.path.exists('../implement'):
    os.makedirs('../implement')  
    
  top = structure.search(iPath = '../synthesis', iOnly = [iTopModule+'\.edf'])[0]
  netlists = structure.search(iPath = '../src', iOnly = ['\.edf', '\.ngc'])
  ucf = build.getParam('UCF')
  
  shutil.copyfile(ucf, '../implement/'+iTopModule+'.ucf')
  shutil.copyfile(top, '../implement/'+iTopModule+'.edf')
  for i in netlists:
    shutil.copyfile(i, '../implement/'+os.path.split(i)[1])
  
  
  os.chdir('../implement')
  subprocess.call('xflow -implement balanced.opt -config bitgen.opt '
                  + iTopModule + '.edf')
  
  if iFlashSize:
    bit2mcs(iTopModule, iFlashSize)
    
  log.info('Implementation done')

