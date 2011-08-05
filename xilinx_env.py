import ctypes
import logging
from hdlLogger import log_call
log = logging.getLogger(__name__)

import glob
import subprocess
import toolchain
import os
import ctypes

# TODO: duplication in toolchain
def getWin32Drivers():
  drivers = []
  LOCALDISK = 3
  bitmask = ctypes.windll.kernel32.GetLogicalDrives()
  for i in range(26):
    if (bitmask >> i) & 0x01:
      driver = chr(i+65) + ':/'
      if ctypes.windll.kernel32.GetDriveTypeA(driver ) == LOCALDISK:
        drivers.append(driver)
  return drivers
  
def get():
  try:
    for logicDrive in getWin32Drivers():
      res = glob.glob('{0}Xilinx/*/*/*settings32.bat'.format(logicDrive))
#      print res
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
