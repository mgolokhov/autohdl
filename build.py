from xml.dom import minidom
from collections import OrderedDict
import os

import structure
import hdlGlobals

import autohdl.lib.yaml as yaml


from hdlLogger import *

class BuildException(Exception):
  def __init__(self, iString):
    self.string = iString
  def __str__(self):
    return self.string
  


def convertToRelpath(iContent, iBuildFile):
  os.chdir('../resource')
  pathUCF = iContent['UCF']
#  pathBuild = os.path.abspath(iBuildFile)
  if pathUCF:
    pathUCF = os.path.relpath(pathUCF)
    iContent['UCF'] = pathUCF
  
  depSrc = iContent['dep']
  if depSrc:
    dep = [os.path.relpath(i) for i in depSrc]
    iContent['dep'] = dep
  os.chdir('../script')



def convertToAbspath(iContent, iBuildFile):
  os.chdir('../resource')
  pathUCF = iContent['UCF']
  if pathUCF and os.path.exists(pathUCF):
    path = os.path.abspath(pathUCF)
    iContent['UCF'] = path
    
  depSrc = iContent['dep']

  if depSrc:
    dep = [os.path.abspath(i) for i in depSrc if os.path.exists(i)]
    iContent['dep'] = dep
  os.chdir('../script')


def defUCFandTop(iContent):
  ucf = iContent['UCF']
  top = iContent['TOPLEVEL']
  if ucf and top:
    return
  elif not ucf and top:
    ucfList = structure.search(iPath = '../src', iIgnore = hdlGlobals.ignore, iOnly = ['\.ucf'])
    ucf = ucfList[0] # first occurrence
    for i in ucfList:
     if top+'.ucf' in i:
       ucf = i
       break
  elif ucf and not top:
    topPath = structure.search(iPath = '../src', iIgnore = hdlGlobals.ignore, iOnly = [ucf+'\.v'])
    topFile = os.path.split(topPath)[1]
    top = os.path.splitext(topFile)[0]
  elif not ucf and not top:
    ucfList = structure.search(iPath = '../src', iIgnore = hdlGlobals.ignore, iOnly = ['\.ucf'])
    for i in ucfList:
      ucfName = os.path.split(i)[1]
      ucfName = os.path.splitext(ucfName)[0]
      topPath = structure.search(iPath = '../src', iIgnore = hdlGlobals.ignore, iOnly = [ucfName+'\.v'])
      if topPath:
        topFile = os.path.split(topPath[0])[1]
        top = os.path.splitext(topFile)[0]
        ucf = i
        break
      else:
        ucf = i
  iContent['UCF'] = ucf
  iContent['TOPLEVEL'] = top


def load(iBuildFile = '../resource/build.yaml', cacheBuild = {}):
  if cacheBuild:
    content = cacheBuild     
  else:
    content = yaml.load(open(iBuildFile, 'r'))
    convertToAbspath(content, iBuildFile)
    defUCFandTop(iContent = content)
    cacheBuild.update(content) 

  return content


def dump(iStructure = '', iContent = '', iBuildFile = '../resource/build.yaml'):
  content  = iContent or load(iBuildFile = iBuildFile)
  if iStructure:
    content['main'] = iStructure['main']
    content['dep']  = [str(i) for i in iStructure['dep']]
    content['TestBench']   = iStructure['TestBench']
  
  convertToRelpath(content, iBuildFile)  
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
    deps = getParam(iKey='dep', iBuild=pathBuild)
    path = set()
    if not deps:
      return []
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

