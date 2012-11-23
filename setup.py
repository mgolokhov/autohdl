import os
import sys
import shutil
from setuptools import setup, find_packages





if os.path.exists('AutoHDL.egg-info'):
  shutil.rmtree('AutoHDL.egg-info')

sys.path.append('autohdl')
import pkg_info
import progressBar
from log_server import shutdownLogServer
from distribute_setup import use_setuptools
use_setuptools()



progressBar.run()
shutdownLogServer()
progressBar.stop()


setup(name='AutoHDL',
      version=pkg_info.getIncVersion(),
      description='Automatization Utilities for HDL projects',
      author='Maxim Golokhov',
      author_email='hexwer@gmail.com',
      platforms=['win32'],
      packages=find_packages(exclude=('autohdl.test',
                                      'autohdl.drafts')),
      scripts=['autohdl/hdl.py',
               'autohdl/hdl.bat'],
      include_package_data=True,
      install_requires=['tinydav', 'pyyaml', 'decorator', 'pyparsing'],
)

