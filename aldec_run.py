import subprocess
import toolchain
import time
import threading
import sys
import os
import shutil

import structure
import os



def action(iMode = 'copy'):
    # cwd = <dsnName>/script
    rootPathAldec = '../aldec/src'
    rootPathDsn = '..'
    for root, dirs, files in os.walk('../aldec/src'):
      virtDir = root.split(rootPathAldec)[1][1:] # exclude slash
      if not virtDir:
        continue
      for afile in files:
        src = os.path.join(root, afile)
        dst = os.path.join(rootPathDsn, virtDir, afile)
      
        try:
          if iMode == 'copy':
            print 'copying...' 
            print 'src=', os.path.abspath(src)
            print 'dst=', os.path.abspath(dst)
            shutil.copyfile(src, dst)  
          elif iMode == 'move':
            print 'moving...' 
            print 'src=', os.path.abspath(src)
            print 'dst=', os.path.abspath(dst)
            shutil.move(src, dst)  
        except IOError, e:
          print os.getcwd()
          print e
        
def copyInRepo():
  while(1):
    action(iMode = 'copy')
    time.sleep(1)

def moveInRepo():
  action(iMode = 'move')
  
aldec = toolchain.getPath(iTag = 'avhdl_gui')

b = threading.Thread(target=copyInRepo)
b.setDaemon(1)
b.start()

subprocess.call(aldec + ' ../aldec/wsp.aws')
moveInRepo()

sys.exit()


