import logging
from hdlLogger import log_call
log = logging.getLogger(__name__)

import glob
import subprocess
import toolchain
import os

  
def get():
  try:
    for logicDrive in toolchain.getDrivesList():
      res = glob.glob('{0}Xilinx\*\*\*settings32.bat'.format(logicDrive))
      if res:
        break
    if not res:
      log.warning('Cannot set env for xilinx tools')
      return
    
    fileToSetEnv = os.getcwd()+'/setXilinxEnv.bat'
        
    with open(fileToSetEnv, 'w') as f:
      f.write('''@echo off
    call {0}
    set'''.format(res[0]))
      
    r = subprocess.check_output('cmd /c call "{0}"'.format(fileToSetEnv))
    
    d = {}
    for i in r.split('\r\n'):
      res = i.split('=')
      if len(res) == 2:
        d.update({res[0]: res[1]})
    return d
  except Exception as exp:
    log.error(exp)
