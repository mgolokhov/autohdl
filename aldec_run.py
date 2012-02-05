import copy
import hashlib
import subprocess
import sys
import shutil
import os
import threading
import time

from autohdl import build
from autohdl.hdlLogger import logging

# get all logging handlers
# get StreamHandler
# reconfigure debug level

lll = logging.getLogger()
#alog = [i for i in lll.handlers if type(i) is logging.StreamHandler][0]

alog = logging.getLogger(__name__)
alog.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
consoleFormatter = logging.Formatter("%(levelname)s:%(message)s")
consoleHandler.setFormatter(consoleFormatter)
alog.addHandler(consoleHandler)
print 'print'
alog.debug('debug')
alog.info('info')
alog.warning('warning')
alog.error('error')


def calcSha(afile):
  with open(afile) as f:
    h = hashlib.sha1()
    h.update(f.read())
    return h.hexdigest()



def isModified(src, dst):
  if not os.path.exists(dst):
    return True
  if os.stat(src).st_mtime == os.stat(dst).st_mtime:
    return
  if calcSha(src) == calcSha(dst):
    return
  return True


def syncRepo(move=False):
  # cwd = <dsnName>/script
#  alog.debug('Wazzzup!')
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
          if move:
            alog.info('Move src={0} dst={1}'.format(src, dst))
            shutil.move(src, dst)
          elif isModified(src, dst):
            alog.info('Copy src={0} dst={1}'.format(src, dst))
            shutil.copyfile(src, dst)
      except Exception as e:
        alog.exception(e)

def copyInRepo():
  while True:
    syncRepo()
    time.sleep(1)


def moveInRepo():
  syncRepo(move = True)


def parse(content):
  d = set()
#  lines = content.splitlines()
  files = [i for i in content.splitlines() if '[file:' in i or 'Enabled' in i]
#  alog.info('\n'.join(files))
#  time.sleep(5)
  for i, l in enumerate(files):
    if l == 'Enabled=1':
      d.add(files[i-1])
    elif l == 'Enabled=0':
      alog.debug(str(files[i-1]))
  return d


def updateDeps(files):
  #[file:.\..\..\circle\src\achtung.v]
  files = [os.path.abspath('../aldec'+f[7:-1]) for f in files]
  build.updateDeps(files)


def synchBuild():
  # relative to dsn/script dsn/aldec/config.cfg
  config = os.path.abspath('../aldec/compile.cfg')
  timestamp = None
  files = set()
  while True:
    try:
      timestampNew = os.stat(config).st_mtime
      if timestamp != timestampNew:
#        alog.debug("new time "+str(timestamp))
        with open(config) as f:
          content = f.read()
        timestamp = timestampNew
        filesNew = parse(content)
        added = filesNew - files
        if files and added:
          alog.debug('Added: '+'\n'.join(added))
          updateDeps(added)
        files = copy.copy(filesNew)
    except (IOError, WindowsError) as e:
      alog.error('Cant open file: '+config)
      alog.exception(e)
    time.sleep(1)



alog.debug(str(sys.argv))
os.chdir(sys.argv[1])

b = threading.Thread(target=copyInRepo)
b.setDaemon(1)
b.start()

c = threading.Thread(target=synchBuild)
c.setDaemon(1)
c.start()


aldec = sys.argv[2] #toolchain.getPath(iTag = 'avhdl_gui')
subprocess.call(aldec + ' ../aldec/wsp.aws')
moveInRepo()

sys.exit()


