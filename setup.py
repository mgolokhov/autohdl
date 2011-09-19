import os
import shutil
import sys
from distutils.core import setup, Command

from log_server import shutdownLogServer
import pkg_info




os.chdir('..')


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


class ShutdownLogServer(Command):
  description = 'Shutdown log server'
  user_options = []
  def initialize_options(self):
    self.cwd = None
  def finalize_options(self):
    self.cwd = os.getcwd()
  def run(self):
    shutdownLogServer()

def getDataTree(iPath):
  res = []
  for root, dirs, files in os.walk(iPath):
    for f in files:
      res.append(os.path.join(root,f).replace('autohdl/', ''))
  return res


setup(name         = 'autohdl',
      version      = pkg_info.getVersion(),
      description  = 'Automatization Utilities',
      author       = 'Max Golohov',
      author_email = 'hex_wer@mail.ru',
      platforms    = ['win32'],
      packages     = ['autohdl',
                      'autohdl.verilog',
                      'autohdl.lib',
                      'autohdl.lib.yaml',
                      'autohdl.lib.tinydav'],
      package_data = {'autohdl': ['data/*']},# + getDataTree('autohdl/test/fake_repo_gold') + getDataTree('autohdl/test/fake_repo')},
      data_files   = [('', ['autohdl/hdl.py'])],
      cmdclass     = {'uninstall': Uninstall, 'shutdownlog': ShutdownLogServer},
     )
