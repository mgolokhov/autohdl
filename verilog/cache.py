import os
import hashlib
import lib.yaml as yaml
from hdlLogger import logging


CACHE_PATH = '../resource/'


def cache_path(file):
  file = os.path.relpath(file)
  return CACHE_PATH + file.replace('//', '_').replace('\\', '_').replace('.','_')


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


def load(file):
  file = cache_path(file)
  y = None
  try:
    y = yaml.load(open(file))
  except IOError as e:
    logging.debug(e)
  except Exception as e:
    logging.warning(e)
  if shaOK(y):
    return y


def dump(data):
  if data['cachable']:
    h = hashlib.sha1()
    with open(data['file_path']) as f:
      h.update(f.read())
    for i in data['includes']['paths']:
      with open(i) as f:
        h.update(f.read())
    data['sha'] = h.hexdigest()
    # curdir = <dsn>/script
    del data['preprocessed']
    del data['cachable']
    file = cache_path(data['file_path'])
    yaml.dump(data, open(file, 'w'))

