import os
import hashlib

import yaml

from autohdl.hdlLogger import logging
from autohdl.pkg_info import getVersion
from autohdl.hdlGlobals import parsedCachePath, buildFilePath


CACHE_PATH = os.path.abspath(parsedCachePath)
CACHE_LOAD = True
CACHE_DUMP = True

def cache_path(file):
  file = os.path.relpath(file)
  name = os.path.basename(file)+'cache'
#  return CACHE_PATH + file.replace('//', '_').replace('\\', '_').replace('.','_')
  return CACHE_PATH + '/' + name


def shaOK(data):
  if data:
    h = hashlib.sha1()
    with open(data['file_path']) as f:
      h.update(f.read())
    for i in data['includes']['paths']:
      with open(i) as f:
        h.update(f.read())
    sha = h.hexdigest()
    if sha == data['sha']:
      return True


def versionOK(data):
  if data.get('version') == getVersion():
    return True


def clean():
  if os.path.exists(CACHE_PATH):
    for i in os.listdir(CACHE_PATH):
      try:
        if os.path.splitext(i)[1] == '.vcache':
          os.remove(CACHE_PATH+'/'+i)
      except Exception as e:
        print e

        
def refreshCache(_once=[]):
  if _once:
    return
  _once.append(True)
  try:
    with open(buildFilePath) as f:
      h = hashlib.sha1()
      h.update(f.read())
      shaNew = h.hexdigest()
    sha_build = CACHE_PATH+'/sha_build'
    try:
      with open(sha_build) as f:
        shaOld = f.read()
        if shaOld != shaNew:
          with open(sha_build, 'w') as f:
            f.write(shaNew)
            return True
    except IOError:
      if not os.path.exists(CACHE_PATH):
        os.makedirs(CACHE_PATH)
      with open(sha_build, 'w') as f:
        f.write(shaNew)
        return True
  except IOError as e:
    logging.error(e)
    return True


def load(file):
  if not CACHE_LOAD:
    return
  file = cache_path(file)
  y = None
  try:
    y = yaml.load(open(file))
  except IOError as e:
    logging.debug(e)
  except Exception as e:
    logging.warning(e)
  try:
    if shaOK(y) and versionOK(y):
      return y
  except IOError as e:
    logging.debug(e)


def dump(data):
  if not CACHE_DUMP:
    return
  if not os.path.exists(CACHE_PATH):
    os.mkdir(CACHE_PATH)
  if data['cachable']:
    h = hashlib.sha1()
    with open(data['file_path']) as f:
      h.update(f.read())
    for i in data['includes']['paths']:
      with open(i) as f:
        h.update(f.read())
    data['sha'] = h.hexdigest()
    data['version'] = getVersion()
    # curdir = <dsn>/script
    del data['preprocessed']
    del data['cachable']
    file = cache_path(data['file_path'])
    yaml.dump(data, open(file, 'w'))

