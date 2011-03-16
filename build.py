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
  

gSYN_EXT  = 'v; vm; vhd; vhdl'
gIMPL_EXT = 'ucf; edf; ndf; ngc' 


class OrderedDictYAMLLoader(yaml.Loader):
  """
  A YAML loader that loads mappings into ordered dictionaries.
  """

  def __init__(self, *args, **kwargs):
    yaml.Loader.__init__(self, *args, **kwargs)

    self.add_constructor(u'tag:yaml.org,2002:map', type(self).construct_yaml_map)
    self.add_constructor(u'tag:yaml.org,2002:omap', type(self).construct_yaml_map)

  def construct_yaml_map(self, node):
    data = OrderedDict()
    yield data
    value = self.construct_mapping(node)
    data.update(value)

  def construct_mapping(self, node, deep=False):
    if isinstance(node, yaml.MappingNode):
      self.flatten_mapping(node)
    else:
      raise yaml.constructor.ConstructorError(None, None,
            'expected a mapping node, but found %s' % node.id, node.start_mark)

    mapping = OrderedDict()
    for key_node, value_node in node.value:
      key = self.construct_object(key_node, deep=deep)
      try:
        hash(key)
      except TypeError, exc:
        raise yaml.constructor.ConstructorError('while constructing a mapping',
            node.start_mark, 'found unacceptable key (%s)' % exc, key_node.start_mark)
      value = self.construct_object(value_node, deep=deep)
      mapping[key] = value
    return mapping


def genPredef(iPath, iDsnName):
  pass


def load(iBuildFile = '../resource/build.yaml'):
#  content = yaml.load(open(iBuildFile, 'r'), OrderedDictYAMLLoader)
  content = yaml.load(open(iBuildFile, 'r'))
  return content


def dump(iContent, iBuildFile = '../resource/build.yaml'):
#  content = []
#  for i in iContent:
#    if type(iContent[i]) == type(list()):
#      content.append(i + ': ')
#      for a in iContent[i]:
#        if os.path.exists(a):
#          a = os.path.relpath(path=a, start=os.path.dirname(iBuildFile))
#        content.append('- ' + a)
#    else:
#      if os.path.exists(i):
#        i = os.path.relpath(path=iContent[i], start=os.path.dirname(iBuildFile))
#      content.append(i + ': ' + str(iContent[i]))
#
#  f = open(iBuildFile, 'w')
#  f.write('\n'.join(content))
#  f.close()
  yaml.dump(iContent, open(iBuildFile, 'w'), default_flow_style=False)
    


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
    

def getParam(iKey, iBuild = '../resource/build.yaml', iDefault = []):
  content = load(iBuild)
  try:
    param = content[iKey]
  except KeyError:
    log.error('No such key: '+iKey+'; in file: '+iBuild)
    return iDefault
  return param
    
    
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

