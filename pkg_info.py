import os

import lib.yaml as yaml


def load():
  path = os.path.join(os.path.dirname(__file__), 'data', 'pkg_info.yaml')
  with open(path, 'r') as f:
    content = yaml.load(f)
    return content


def dump(iContent):
  path = os.path.join(os.path.dirname(__file__), 'data', 'pkg_info.yaml')
  with open(path, 'w') as f:
    yaml.dump(iContent, f)


def incBuild():
  y = load()
  y['version']['build'] += 1
  dump(y)
  return getVersion(y)

def getVersion(iContent = ''):
  ver = iContent['version'] if iContent else load()['version']
  verStr = '{major}.{minor}.{build}'.format(major = ver['major'],
                                            minor = ver['minor'],
                                            build = ver['build'])
  return verStr


