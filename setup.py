import os
import shutil
import sys
from distutils.core import setup, Command

from log_server import shutdownLogServer
import pkg_info




shutdownLogServer()

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



setup(name         = 'autohdl',
      version      = pkg_info.getVersion(),
      description  = 'Automatization Utilities',
      author       = 'Max Golohov',
      author_email = 'hex_wer@mail.ru',
      platforms    = ['win32'],
      packages     = ['autohdl', 'autohdl.test', 'autohdl.lib', 'autohdl.lib.yaml'],
      package_data = {'autohdl': ['data/*']},
      data_files   = [('', ['autohdl/hdl.py'])],
      cmdclass     = {'uninstall': Uninstall},
     )
