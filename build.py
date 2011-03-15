from xml.dom import minidom
import os

import autohdl.lib.yaml as yaml

from hdlLogger import *

class BuildException(Exception):
  def __init__(self, iString):
    self.string = iString
  def __str__(self):
    return self.string
  

gSYN_EXT  = 'v; vm; vhd; vhdl'
gIMPL_EXT = 'ucf; edf; ndf; ngc' 


def genPredef(iPath, iDsnName):
  '''
  Generates predefined build.xml
  '''
  global gSYN_EXT
  global gIMPL_EXT
  log.debug('def genPredef IN iPath='+iPath+' iDsnName='+iDsnName)
  buildContent = '''\
  <!--default build-->
  <wsp>
    <dsn id="{DESIGN_NAME}">
      <dep>{DEP}</dep>
      <synthesis_ext>{SYN_EXT}</synthesis_ext>
      <implement_ext>{IMPL_EXT}</implement_ext>
    </dsn>
  </wsp>
  '''.format(DESIGN_NAME=iDsnName,
             DEP='',
             SYN_EXT = gSYN_EXT,
             IMPL_EXT = gIMPL_EXT
             )
  pathBuild = iPath+'/build.xml'
  if not os.path.exists(pathBuild):
    f = open(pathBuild, 'w')
    f.write(buildContent)
    f.close()
  log.debug('def genParedef OUT')


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
    

def getParam(iKey, iBuild = '../resource/build.yaml'):
  build = yaml.load(open(iBuild, 'r'))
  try:
    param = build[iKey]
  except KeyError:
    log.error('No such key: '+iKey+'; in file: '+iBuild)
    return
  return param
    
    
def getDeps(iBuilds):
  '''
  Input:  set of path to build.yaml's
  Output: set of new paths/files to parse
  '''
  for pathBuild in iBuilds:
    deps = getParam(iKey='dependences', iBuild=pathBuild)
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
  paths = getFiles(pathBuilds)
  depTree = []
  for path in paths:
    if os.path.isfile(path):
      depTree.append(path)
    else:
      for root, dirs, files in os.path.walk(path):
        for f in files:
          depTree.append(os.path.join(root, f))
  return depTree

  
      

def _getDeps(iDsnName = '', iBuildFile = 'build.xml'):
  '''
  Returns: dictionary key=dsnName, value=list of dependences as full path;
  '''
  log.debug('def getDeps IN iDsnName='+iDsnName+' iBuildFile='+iBuildFile)
  if not os.path.exists(iBuildFile):
    log.warning("Can't find file: " + iBuildFile)
    return
  
  pathBuildFile = os.path.abspath(iBuildFile).replace('\\','/')
  pathDsn = '/'.join(pathBuildFile.split('/')[:-3])

  dom = minidom.parse(pathBuildFile)
  dsnNodes = dom.getElementsByTagName('dsn')
  dependences = {}
  for node in  dsnNodes:
    if node.attributes:
      dsnName = node.attributes['id'].value
      dep = node.getElementsByTagName('dep')
      dsnDep = []
      for k in dep:
        tagContent = k.firstChild
        if not tagContent:
          continue
        pathDep = tagContent.toxml().strip()
        pathDepAbs = '%s/%s' % (pathDsn, pathDep)
        pathDepAbs = os.path.abspath(pathDepAbs).replace('\\','/')
        if not os.path.exists(pathDepAbs):
          log.warning('Wrong dep path: '+pathDepAbs+'; in file: '+iBuildFile)
          continue 
        dsnDep.append(pathDepAbs)
      dependences[dsnName] = dsnDep
      if iDsnName == dsnName:
        break
  log.debug('def getDeps OUT dependences='+str(dependences))
  return dependences



def getSrcExtensions(iTag, iBuildFile='../resource/build.yaml'):
  if os.path.splitext(iBuildFile) != '.yaml':
    iBuildFile = os.path.join(iBuildFile, 'resource', 'build.yaml')
  if not os.path.exists(iBuildFile):
    log.warning("No such path or file: " + iBuildFile)
    return
  
  build = yaml.load(open(iBuildFile, 'r'))
  ext = build.get(iTag)
  if not ext:
    log.warning("Can't get file extensions in file: " + iBuildFile)
    return
  extensions = [i.strip() for i in ext.split(';')]
  return extensions



def _getSrcExtensions(iTag, iBuildFile='../resource/build.xml'):
  '''
  Input: tag (e.g. synthesis_ext, implement_ext), path to buildXml;
  Output: list of extensions (e.g. [.v, .vhdl, .vm])
  Tag example: <synthesis_ext>v;vhdl;vm</synthesis_ext>
  '''
  log.debug('def getSrcExtensions IN iTag='+iTag+'; iBuildFile='+iBuildFile)
  iBuildFile = os.path.abspath(iBuildFile)
  try:
    if not os.path.exists(iBuildFile):
      raise BuildException("Can't find file: "+iBuildFile)  
    dom = minidom.parse(iBuildFile)
    extensionsNode = dom.getElementsByTagName(iTag)
    if not extensionsNode:
      raise BuildException("Can't find tag="+iTag+'; in file='+iBuildFile)  
    extensions = extensionsNode[0].childNodes[0].toxml().strip().strip(';')
    if not extensions:
      raise BuildException("Empty value for tag="+iTag+'; in file='+iBuildFile)  
  except BuildException as msg:
    log.warning(msg)
    if iTag == 'synthesis_ext':
      extensions = gSYN_EXT
      log.warning("Can't get extensions from build.xml. Using default="+str(gSYN_EXT))
    elif iTag == 'implement_ext':
      extensions = gIMPL_EXT
      log.warning("Can't get extensions from build.xml. Using default="+str(gIMPL_EXT))
    else:
      log.warning('Invalid tag='+iTag)
      return ''
    
  extensions = [i.strip() for i in extensions.split(';')]
  log.debug('def getSrcExtensions OUT extensions='+str(extensions))
  return extensions

