#!/usr/bin/env python

from distutils.core import setup
import os
import shutil
import sys

os.chdir('..')


def getTree(iPathRoot):
  afiles = []
  adirs = []
  for root, dirs, files in os.walk(iPathRoot):
    r = root.replace('\\', '/')
    r = r.replace('autohdl/', '')
    for d in dirs:
      if not os.listdir(root+'/'+d):
        path = r + '/' + d + '/*'
        adirs.append(path)
    for f in files:
      path = '%s/%s' % (r, f)
      afiles.append(path)
  return afiles, adirs

files, dirs = getTree('autohdl/test')
data_resource = files + dirs
files, dirs = getTree('autohdl/data')
data_resource += files + dirs
#print '\n'.join(data_resource)
#print os.getcwd()
#sys.exit()

# BUGAGA: win specific
if os.name == 'nt':
  if os.path.exists('build'): shutil.rmtree('build')
  path = sys.prefix+'/Lib/site-packages/autohdl'
  if os.path.exists(path): shutil.rmtree(path)

setup(name='autohdl',
      version='2.4_alpha',
      description='Automatization Utilities',
      author='Max Golohov',
      author_email='hex_wer@mail.ru',
      packages=['autohdl', 'autohdl.test', 'autohdl.lib'],
      package_data={'autohdl': data_resource},
      data_files=[('', ['autohdl/hdl.py'])]
     )
