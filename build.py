import os
import pprint

import structure
import hdlGlobals

import lib.yaml as yaml


from hdlLogger import log_call, logging
log = logging.getLogger(__name__)




class BuildException(Exception):
  def __init__(self, iString):
    self.string = iString
  def __str__(self):
    return self.string
  


@log_call    
def convertToRelpath(iContent):
  os.chdir('../resource')

  pathUCF = iContent.get('UCF') or iContent.get('ucf')
  if pathUCF:
    iContent['ucf'] = os.path.relpath(pathUCF)

  depSrc = iContent.get('dep') or iContent.get('DEP')
  if depSrc:
    iContent['dep'] = [os.path.relpath(i) for i in depSrc]

  include_path = iContent.get('include_path')
  # TODO: bugaga
#  print include_path
  if include_path:
    if type(include_path) != type(list()):
      include_path = [include_path]
    iContent['include_path'] = [os.path.relpath(i) for i in include_path]

  os.chdir('../script')



@log_call    
def convertToAbspath(iContent):
  os.chdir('../resource')

  pathUCF = iContent.get('UCF') or iContent.get('ucf')
  if pathUCF and os.path.exists(pathUCF):
    path = os.path.abspath(pathUCF)
    iContent['ucf'] = path
    
  depSrc = iContent.get('dep')
  if depSrc:
    dep = []
    dep_wrong = []
    for i in depSrc:
      if os.path.exists(i):
        dep.append(os.path.abspath(i))
      else:
        dep_wrong.append(i)
    iContent['dep'] = dep
    if dep_wrong:
      iContent['dep_wrong'] = dep_wrong

  include_path = iContent.get('include_path')
  if include_path:
    if type(include_path) != type(list()):
      include_path = [include_path]
    incl = []
    incl_wrong = []
    for i in include_path:
      if os.path.exists(i):
        incl.append(os.path.abspath(i).replace('\\', '/'))
      else:
        incl_wrong.append(i)
    iContent['include_path'] = incl
    if incl_wrong:
      iContent['include_path_wrong'] = incl_wrong

  os.chdir('../script')


@log_call
def load(iBuildFile = '../resource/build.yaml', _cacheBuild = {}):
  if False:
    pass
#  if _cacheBuild:
#    content = _cacheBuild
  else:
    try:
      with open(iBuildFile) as f:
        with open(os.path.dirname(__file__)+'/data/build.yaml') as f2:
          contentDefault = yaml.load(f2.read())
          content = yaml.load(f.read())
          newFields  = list(contentDefault.viewkeys() - content.viewkeys())
          for i in newFields:
            content[i] = contentDefault[i]
          convertToAbspath(content)
          _cacheBuild.update(content)
          dump(iContent = content, iBuildFile = iBuildFile)
    except IOError:
      logging.warning('Cant open file ' + os.path.abspath(iBuildFile))
      return {}

  return content

def loadDefault():
  with open(os.path.dirname(__file__)+'/data/build.yaml') as f2:
    return yaml.load(f2.read())


def loadUncached(iBuildFile = '../resource/build.yaml'):
  return yaml.load(open(iBuildFile, 'r'))


@log_call    
def dump(iContent = '', iBuildFile = '../resource/build.yaml'):
  content  = iContent or load(iBuildFile = iBuildFile)
  oldContent = loadUncached(iBuildFile = iBuildFile)
  convertToRelpath(content)
  if content != oldContent:
    yaml.dump(content, open(iBuildFile, 'w'), default_flow_style=False)


@log_call
def getParam(iKey, iBuild = '../resource/build.yaml', iDefault = None):
  iDefault = iDefault or []
  content = load(iBuild)
  res = None
  for key in [iKey.upper(), iKey.lower()]:
    try:
      res = content[key]
    except KeyError:
      continue
  res = res or iDefault
  return res


@log_call
def getPathToBuild(file):
  file = os.path.abspath(file)
  pathAsList = file.replace('\\','/').split('/')
  path = ''
  if pathAsList.count('src'):
    index = pathAsList.index('src')
    rootPath = '/'.join(pathAsList[:index])
    path = os.path.join(rootPath, 'resource', 'build.yaml')
    if not os.path.exists(path):
      log.warning("Can't find build file: " + path)
      path = ''
  else:
    log.warning('Wrong location for source file: ' + file)
    log.warning('Expects in <dsn_name>/src/ directory')
  return path


@log_call
def getDepPaths(file):
  """
  Input:  path to file with undefined instance;
  Output: list of path to dependent files
  """
  path = getPathToBuild(file)
  depInBuild = getParam(iKey='dep', iBuild=path, iDefault=[])
  if type(depInBuild) is not list:
    depInBuild = [depInBuild]
  paths = []
  for i in depInBuild:
    if os.path.isfile(i):
      paths.append(os.path.abspath(i))
    elif os.path.isdir(i):
      for root, dirs, files in os.walk(i):
        for f in files:
          paths.append(os.path.abspath(os.path.join(root, f)))
    else:
      log.warning('Path does not exists: '+ os.path.abspath(i) + '; in file: ' + file)
  return paths
