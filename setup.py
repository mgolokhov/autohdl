import os
import sys
import shutil
from setuptools import setup, find_packages
from setuptools.command.install import install as _install


#
# class install(_install):
#     def _post_install(self, dir):
#         import build
#         build.update_global()
#     def run(self):
#         _install.run(self)
#         self.execute(self._post_install, (self.install_lib,),
#                      msg="Running post install task")
#         print('post install done')


def clean_tmp_files():
  if os.path.exists('AutoHDL.egg-info'):
    shutil.rmtree('AutoHDL.egg-info')

  files_to_clean = [i for i in os.listdir('autohdl') if os.path.splitext(i)[1] == '.pyc']
  for i in files_to_clean:
    os.remove(os.path.join('autohdl', i))

clean_tmp_files()

sys.path.insert(0, 'autohdl')
import pkg_info
import log_server


log_server.shutdownLogServer()



import subprocess
if 'install' in sys.argv:
    for i in ['py', 'cpy']:
        command = 'reg add HKEY_CLASSES_ROOT\{py_type}_auto_file\shell\open\command' \
                  ' /ve /d "C:\windows\py.exe %1 %*" /f'.format(py_type=i)
        print('executing: ' + command)
        print(subprocess.check_output(command, shell=True))


if 'upload' in sys.argv:
  pkg_info.inc_version()

setup(name='AutoHDL',
      version=pkg_info.version(),
      # cmdclass={'install': install},
      description='Automatization Utilities for HDL projects',
      author='Maxim Golokhov',
      author_email='hexwer@gmail.com',
      platforms=['win32'],
      classifiers=['Programming Language :: Python :: 3.4'],
      packages=find_packages(exclude=('autohdl.test',
                                      'autohdl.drafts')),
      scripts=['autohdl/hdl.py',
               'autohdl/hdl.bat'],
      include_package_data=True,
      install_requires=['pyyaml', 'decorator', 'requests'],
      )


