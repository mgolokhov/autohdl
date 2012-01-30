import os

import autohdl.lib.yaml as yaml


from hdlLogger import log_call, logging
log = logging.getLogger(__name__)




class BuildException(Exception):
  def __init__(self, iString):
    self.string = iString
  def __str__(self):
    return self.string
  


@log_call    
def convertToRelpath(iContent, buildFile):
  buildPath = os.path.dirname(buildFile)
  pathUCF = getParam('ucf')
  if pathUCF:
    iContent['ucf'] = os.path.relpath(pathUCF, buildPath)

  depSrc = getParam('dep')
  if depSrc:
    iContent['dep'] = [os.path.relpath(i, buildPath) for i in depSrc]

  include_path = iContent.get('include_path')
  # TODO: bugaga
#  print include_path
  if include_path:
    if type(include_path) != type(list()):
      include_path = [include_path]
    iContent['include_path'] = [os.path.relpath(i, buildPath) for i in include_path]


@log_call    
def convertToAbspath(iContent, buildPath):
  rootPath = os.path.dirname(buildPath)
  pathUCF = iContent.get('ucf')
  iContent['dump'] = False
  if pathUCF and os.path.exists(pathUCF):
    if ':' not in pathUCF:
      path = os.path.normpath(rootPath+'/'+pathUCF)
    else:
      iContent['dump'] = True
      path = pathUCF
    iContent['ucf'] = path
    
  depSrc = iContent.get('dep')
  if depSrc:
    dep = []
    for i in depSrc:
      if ':' not in i:
        i = os.path.normpath(rootPath+'/'+i)
      else:
        iContent['dump'] = True
      if os.path.exists(i):
        dep.append(i)
      else:
        log.warning('Wrong path: '+i)
    iContent['dep'] = dep

  include_path = iContent.get('include_path')
  if include_path:
    if type(include_path) != type(list()):
      include_path = [include_path]
    incl = []
    incl_wrong = []
    for i in include_path:
      if ':' not in i:
        i = os.path.normpath(rootPath+'/'+i)
      else:
        iContent['dump'] = True
      if os.path.exists(i):
        incl.append(os.path.abspath(i).replace('\\', '/'))
      else:
        incl_wrong.append(i)
    iContent['include_path'] = incl
    if incl_wrong:
      iContent['include_path_wrong'] = incl_wrong


@log_call
def load(iBuildFile = '../resource/build.yaml', _cacheBuild = {}, silent = False):
  path = os.path.abspath(iBuildFile)
  if _cacheBuild.get(path):
    return _cacheBuild.get(path)
  else:
    try:
      with open(iBuildFile) as f:
        with open(os.path.dirname(__file__)+'/data/build.yaml') as f2:
          contentDefault = yaml.load(f2.read())
          content = yaml.load(f.read())
          newFields  = list(contentDefault.viewkeys() - content.viewkeys())
          for i in newFields:
            content[i] = contentDefault[i]
          convertToAbspath(content, iBuildFile)
          _cacheBuild.update({path:content})
          dump(iContent = content, iBuildFile = iBuildFile)
    except IOError as e:
      if not silent:
        log.warning(e)
        logging.warning('Cant open file ' + os.path.abspath(iBuildFile))
      return {}

  return content


def loadDefault():
  with open(os.path.dirname(__file__)+'/data/build.yaml') as f2:
    content = yaml.load(f2.read())
    convertToAbspath(content, '../resource/build.yaml')
    return content


def loadUncached(iBuildFile = '../resource/build.yaml', silent = False):
  try:
    with open(iBuildFile) as f2:
      content = yaml.load(f2.read())
      convertToAbspath(content, iBuildFile)
      return content
  except IOError as e:
    if not silent:
      log.warning(e)
      logging.warning('Cant open file ' + os.path.abspath(iBuildFile))


@log_call    
def dump(iContent, iBuildFile = '../resource/build.yaml'):
  content = iContent
  convertToRelpath(content, iBuildFile)
  oldContent = loadUncached(iBuildFile = iBuildFile)
  if content != oldContent or content.pop('dump', False):
    yaml.dump(content, open(iBuildFile, 'w'), default_flow_style=False)


@log_call
def getParam(iKey, iBuild = '../resource/build.yaml', iDefault = None):
  content = load(iBuild)
  res = None
  for key in [iKey.upper(), iKey.lower()]:
    try:
      res = content[key]
    except KeyError:
      continue
  res = res or iDefault or []
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
  depInBuild = loadUncached(path).get('dep')
  if not depInBuild:
    return []
  if type(depInBuild) is not list:
    depInBuild = [depInBuild]
  paths = []
  for i in [os.path.abspath(os.path.dirname(file))] + depInBuild:
    if os.path.isfile(i):
      paths.append(i)
    elif os.path.isdir(i):
      for root, dirs, files in os.walk(i):
        for f in files:
          if os.path.splitext(f)[1] in ['.v']:
            paths.append((os.path.join(root, f)))
    else:
      log.warning('Path does not exists: '+ os.path.abspath(i) + '; in file: ' + file)
  return paths


@log_call
def updateDeps(files):
  if type(files) is not list:
    files = [files]
  build = load()
  dep = build.get('dep')
  # build.yaml returns None
  if dep:
    dep = [os.path.abspath(d) for d in dep]
  else:
    dep = []
  log.debug('files ' + '\n'.join(files))
  log.debug('dep ' + '\n'.join(dep))
  files = [os.path.relpath(i, '../resource') for i in files
           if os.path.abspath(i) not in dep]
  build['dep'] = files + dep
  dump(build)