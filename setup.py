import logging
import logging.handlers
from distutils.core import setup, Command
import os
import shutil
import sys
from log_server import shutdownLogServer




shutdownLogServer()
# pre-install
# copy preinstall.py (to shutdown log_server in .exe distribution, clean previous version)    
# post-install? 
shutil.copyfile('preinstall.py', '../preinstall.py')
os.chdir('..')


import database
def getVersion():
  if 'bdist_wininst' in sys.argv[1]: 
    return database.incBuildVersion()
  else:
    return database.getBuildVersion()


class Uninstall(Command):
  description = 'uninstall previous version'
  user_options = []
  def initialize_options(self):
    self.cwd = None
  def finalize_options(self):
    self.cwd = os.getcwd()
  def run(self):
    path = sys.prefix + '/Lib/site-packages/autohdl'
    if os.path.exists(path):
      shutil.rmtree(path)



setup(name         = 'autohdl',
      version      = getVersion(),
      description  = 'Automatization Utilities',
      author       = 'Max Golohov',
      author_email = 'hex_wer@mail.ru',
      platforms    = ['win32'],
      packages     = ['autohdl', 'autohdl.test', 'autohdl.lib', 'autohdl.lib.yaml'],
      package_data = {'autohdl': ['data/*']},
      data_files   = [('', ['autohdl/hdl.py'])],
      cmdclass     = {'uninstall': Uninstall},
     )
