#!/usr/bin/env python

from distutils.core import setup
import os
import shutil
import sys
import sqlite3

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


def getVersionRaw():
  aconnect = sqlite3.connect('autohdl/data/autohdl.db')
  acursor = aconnect.cursor()
  if sys.argv[1] == 'bdist_wininst':
    acursor.execute('''UPDATE version SET build = build + 1''')
  res = acursor.execute('''SELECT * FROM version''')
  version = res.fetchone()
  aconnect.commit()
  aconnect.close()
  return version

gVersion = getVersionRaw()

def getVersion():
  version = '.'.join([str(i) for i in gVersion])
  return version



# BUGAGA: win specific
if os.name == 'nt':
  if os.path.exists('build'):
    shutil.rmtree('build')

  name = 'autohdl-'+'.'.join([str(i)for i in gVersion[:-1]])
  
  path = sys.prefix+'/Lib/site-packages/autohdl'
  if os.path.exists(path):
    shutil.rmtree(path)
  
#  if os.path.exists('dist'):
#    for root, dirs, files in os.walk('dist'):
#      for f in files:
#        if name in f:
#          os.remove(f)
    
  

setup(name         = 'autohdl',
      version      = getVersion(),
      description  = 'Automatization Utilities',
      author       = 'Max Golohov',
      author_email = 'hex_wer@mail.ru',
      platforms    = ['win32'],
      packages     = ['autohdl', 'autohdl.test', 'autohdl.lib', 'autohdl.lib.yaml'],
      package_data = {'autohdl': data_resource},
      data_files   = [('', ['autohdl/hdl.py'])]
     )
