import subprocess
import toolchain
import time
import threading
import sys
import os
import shutil

import structure

def budger():
  while(1):
    src = structure.search(iPath = '../aldec/src', iIgnore = ['/TestBench/'])
    tb  = structure.search(iPath = '../aldec/src/TestBench')
    print 'src: ', src
    print 'tb: ', tb
    for i in src:
      shutil.copyfile(i, '../src/'+os.path.split(i)[1])
    for i in tb:
      shutil.copyfile(i, '../TestBench/'+os.path.split(i)[1])
    time.sleep(1)

def move_in_repo():
  src = structure.search(iPath = '../aldec/src', iIgnore = ['/TestBench/'])
  tb  = structure.search(iPath = '../aldec/src/TestBench')
  for i in src:
    shutil.move(i, '../src/'+os.path.split(i)[1])
  for i in tb:
    shutil.move(i, '../TestBench/'+os.path.split(i)[1])
    
aldec = toolchain.getPath(iTag = 'avhdl_gui')

b = threading.Thread(target=budger)
b.setDaemon(1)
b.start()

subprocess.call(aldec + ' ../aldec/wsp.aws')
move_in_repo()

sys.exit()


