import subprocess
import sys
import shutil
import os
import threading
import time
import build

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


def parse(content):
  d = set()
  lines = content.splitlines()
  for i, l in enumerate(lines):
    if l == 'Enabled=0':
      d.add(lines[i-1])
  return d


def updateDeps(files):
  #[file:.\..\..\circle\src\achtung.v]
  files = [os.path.abspath('../aldec'+f[7:-1]) for f in files]
  build.updateDeps(files)


def synchBuild():
  # relative to dsn/script dsn/aldec/config.cfg
  config = os.path.abspath('../aldec/compile.cfg')
  state = None
  for i in range(10):
    time.sleep(1)
    try:
      state = os.stat(config).st_mtime
      with open(config) as f:
        content = f.read()
      break
    except IOError as e:
      log.error('Cant open file: '+config)
    except WindowsError as e:
      log.error('No such file: '+config)
  if not state:
    return # no config

  files = parse(content)
#  log.info('files: '+str(files))
  while True:
    time.sleep(1)
    try:
      if state != os.stat(config).st_mtime:
        with open(config) as f:
          content = f.read()
    except IOError as e:
      log.error('Cant open file: '+config)
    except WindowsError as e:
      log.error('No such file: '+config)
    filesNew = parse(content)
    added = files - filesNew
    if added:
      log.info('Added: '+str(added))
      updateDeps(added)
      files = filesNew



log.debug(str(sys.argv))
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


