import os
import shutil
import sys
#from distutils.core import setup, Command
from setuptools import setup, Command, find_packages
from autohdl import pkg_info, progressBar

from autohdl.log_server import shutdownLogServer


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
    progressBar.run()
    shutdownLogServer()
    progressBar.stop()

def getDataTree(iPath):
  res = []
  for root, dirs, files in os.walk(iPath):
    for f in files:
      res.append(os.path.join(root,f).replace('autohdl/', ''))
  return res

sys.argv.append('sdist')

setup(name         = 'AutoHDL',
      version      = pkg_info.getVersion(),
      description  = 'Automatization Utilities',
      author       = 'Max Golohov',
      author_email = 'hex_wer@mail.ru',
      platforms    = ['win32'],

      packages     = find_packages(),
      package_data = {'autohdl': ['data/*']+getDataTree('autohdl/doc')+['lib/djtgcfg.exe']},
      # + getDataTree('autohdl/test/fake_repo_gold') + getDataTree('autohdl/test/fake_repo')},
      data_files   = [('', ['autohdl/hdl.py'])],
#      cmdclass     = {'uninstall': Uninstall, 'shutdownlog': ShutdownLogServer},
     )
