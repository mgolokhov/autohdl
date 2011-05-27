'''
Imports all modules in package.
Drops package name and gets alias as module names.
'''
#
#import logging
#log = logging.getLogger('hdlLogger')
#logging.basicConfig(level = logging.INFO)
#fh = logging.FileHandler("hdlLogger.log")
#fh.setLevel(logging.DEBUG)
#log.addHandler(fh)


import synthesis
import implement
import instance
import toolchain
import build
import structure
import aldec
import putfw_dav 


import inspect
import os
# change dir to the root script location
# now scrips can run from aldec
try:
  os.chdir(os.path.dirname(inspect.stack()[-1][1]))
except WindowsError:
  #
  pass
  