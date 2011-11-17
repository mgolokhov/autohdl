import os
import hashlib
import sys

try:
  from lib import yaml
  from hdlLogger import logging
  from pkg_info import getVersion
except ImportError:
  from ..lib import yaml
  from ..hdlLogger import logging
  from ..pkg_info import getVersion


CACHE_PATH = '../resource/parsed'
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

