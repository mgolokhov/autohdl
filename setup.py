import os
import sys
import shutil
from setuptools import setup, find_packages


def clean_tmp_files():
  if os.path.exists('AutoHDL.egg-info'):
    shutil.rmtree('AutoHDL.egg-info')

  files_to_clean = [i for i in os.listdir('autohdl') if os.path.splitext(i)[1] == '.pyc']
  for i in files_to_clean:
    os.remove(os.path.join('autohdl',i))


clean_tmp_files()
from distribute_setup import use_setuptools
use_setuptools()

sys.path.append('autohdl')
import pkg_info
import procHandler

procHandler.killAll()



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

