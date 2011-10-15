import subprocess
import sys
import shutil
import os
import threading
import time

from hdlLogger import logging
log = logging.getLogger(__name__)


def syncRepo(move=False):
  # cwd = <dsnName>/script
  rootPathAldec = '../aldec/src/'
  rootPathDsn = '../'
  syncDirs = [d for d in os.listdir(rootPathAldec)
          if d not in ['.svn', '.git'] and d in os.listdir(rootPathDsn)]
  for dir in syncDirs:
    for root, dirs, files in os.walk(rootPathAldec+dir):
      try:
        dirs[:] = [d for d in dirs if d not in ['.svn', '.git']]
        pathDsn = root.replace(rootPathAldec, rootPathDsn)
        if not os.path.exists(pathDsn):
          os.makedirs(pathDsn)
        for f in files:
          src = os.path.abspath(root+'/'+f)
          dst = os.path.abspath(pathDsn+'/'+f)
          log.info('Moving src={0} dst={1}'.format(src, dst))
          if move:
            shutil.move(src, dst)
          else:
            shutil.copyfile(src, dst)
      except IOError as e:
        log.exception(e)

def copyInRepo():
  while True:
    syncRepo()
    time.sleep(1)


def moveInRepo():
  syncRepo(move = True)

log.debug(str(sys.argv))
os.chdir(sys.argv[1])

b = threading.Thread(target=copyInRepo)
b.setDaemon(1)
b.start()

aldec = sys.argv[2] #toolchain.getPath(iTag = 'avhdl_gui')
subprocess.call(aldec + ' ../aldec/wsp.aws')
moveInRepo()

sys.exit()


