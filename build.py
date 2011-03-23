from xml.dom import minidom
from collections import OrderedDict
import os

import autohdl.lib.yaml as yaml


from hdlLogger import *

class BuildException(Exception):
  def __init__(self, iString):
    self.string = iString
  def __str__(self):
    return self.string
  



def genPredef(iPath, iDsnName):
  pass


def load(iBuildFile = '../resource/build.yaml'):
#  content = yaml.load(open(iBuildFile, 'r'), OrderedDictYAMLLoader)
  content = yaml.load(open(iBuildFile, 'r'))
  return content


def dump(iStructure = '', iContent = '', iBuildFile = '../resource/build.yaml'):
  content  = iContent or load(iBuildFile = iBuildFile)
  if iStructure:
    content['main'] = iStructure['main']
    content['dep']  = [str(i) for i in iStructure['dep']]
    content['TestBench']   = iStructure['TestBench']
    
  yaml.dump(content, open(iBuildFile, 'w'), default_flow_style=False)
    


def getBuilds(iFiles):
  '''
  Input:  list/set of path to files with undefined instances
  Output: one or set of path to build.yaml's
  '''
  pathBuilds = set()
  for f in iFiles:
    pathAsList = f.replace('\\','/').split('/')
    if pathAsList.count('src'):
      index = pathAsList.index('src')
    else:
      log.warning('Wrong location for source file: ' + iPathFile)
      log.warning('Expecting in <dsn_name>/src/ directory')
      continue
    rootPath = '/'.join(pathAsList[:index])
    pathBuild = os.path.join(rootPath, 'resource', 'build.yaml')
    if not os.path.exists(pathBuild):
      log.warning("Can't find build file: " + pathBuild)
      continue
    pathBuilds.add(pathBuild)
  return pathBuilds
    

  
def getParam(iKey, iBuild = '../resource/build.yaml', iDefault = None):
  iDefault = iDefault or []
  content = load(iBuild)
  try:
    for k in iKey.split('.'):
      content = content[k]
  except KeyError:
    log.info('No such key: ' + k + '; in file: ' + iBuild)
    return iDefault
  return content
    
    
def getDeps(iBuilds):
  '''
  Input:  set of path to build.yaml's
  Output: set of new paths/files to parse
  '''
  for pathBuild in iBuilds:
    deps = getParam(iKey='src_dep', iBuild=pathBuild)
    path = set()
    for d in deps:
      if not os.path.exists(d):
        log.warning('Path does not exists: '+ d + '; in file: ' + pathBuild)
      else:
        path.add(d)
  return path



def getDepTree(iFile):
  if type(iFile) == type(""):
    iFile = [iFile]
  pathBuilds = getBuilds(iFile)
  paths = getDeps(pathBuilds)
  depTree = []
  for path in paths:
    if os.path.isfile(path):
      depTree.append(path)
    else:
      for root, dirs, files in os.walk(path):
        for f in files:
          depTree.append(os.path.join(root, f))
  return depTree


def getSrcExtensions(iTag, iBuildFile='../resource/build.yaml'):
  
  if os.path.splitext(iBuildFile)[1] != '.yaml':
    iBuildFile = os.path.join(iBuildFile, 'resource', 'build.yaml')
  if not os.path.exists(iBuildFile):
    log.warning("No such path or file: " + iBuildFile)
    return []
  
  content = load(iBuildFile)
  ext = content.get(iTag)
  if not ext:
    log.warning("Can't get file extensions in file: " + iBuildFile)
    return []
  extensions = ['\.'+i.strip() for i in ext.split(';')]
  return extensions

