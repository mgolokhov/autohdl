import os

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
def defUCFandTop(iContent):
  #TODO: it's hdlManager work
  ucf = iContent.get('UCF') or iContent.get('ucf')
  top = iContent.get('TOPLEVEL') or iContent.get('toplevel')
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
#    topPath = structure.search(iPath = '../src', iIgnore = hdlGlobals.ignore, iOnly = [ucf.rstrip('.ucf')+'\.v'])
    pathTop = ucf.rstrip('.ucf')+'.v'
    if os.path.exists(pathTop):
      topFile = os.path.split(pathTop)[1]
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


@log_call    
def load(iBuildFile = '../resource/build.yaml', _cacheBuild = {}):
  if _cacheBuild:
    content = _cacheBuild
  else:
    try:
      with open(iBuildFile) as f:
        content = yaml.load(f.read())
        convertToAbspath(content)
        _cacheBuild.update(content)
        dump(iContent = content, iBuildFile = iBuildFile)
    except IOError:
      logging.warning('Cant open file ' + os.path.abspath(iBuildFile))
      return {}

  return content


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
def getBuild(iFile):
  path = os.path.abspath(iFile)
  pathAsList = path.replace('\\','/').split('/')
  pathBuild = ''
  if pathAsList.count('src'):
    index = pathAsList.index('src')
    rootPath = '/'.join(pathAsList[:index])
    pathBuild = os.path.join(rootPath, 'resource', 'build.yaml')
    if not os.path.exists(pathBuild):
      log.warning("Can't find build file: " + pathBuild)
      pathBuild = ''
  else:
    log.warning('Wrong location for source file: ' + iPathFile)
    log.warning('Expecting in <dsn_name>/src/ directory')
  return pathBuild
  


@log_call
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
      rootPath = '/'.join(pathAsList[:index])
      pathBuild = os.path.join(rootPath, 'resource', 'build.yaml')
      if not os.path.exists(pathBuild):
        log.warning("Can't find build file: " + pathBuild)
        continue
      pathBuilds.add(pathBuild)
    else:
      log.warning('Wrong location for source file: ' + iPathFile)
      log.warning('Expecting in <dsn_name>/src/ directory')
      continue
  return pathBuilds



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
def getDep(iBuild):
  deps = getParam(iKey = 'dep', iBuild = iBuild)
  if not deps:
    return 
  # os.chdir('../resource') for relative path same as '../script'
  deps = [os.path.abspath(d) for d in deps]
  paths = set()
  for d in deps:
    if not os.path.exists(d):
      log.warning('Path does not exists: '+ d + '; in file: ' + pathBuild)
    else:
      paths.add(d)
  return paths 




@log_call    
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
    os.chdir('../resource')
    deps = [os.path.abspath(d) for d in deps]
    os.chdir('../script')
    for d in deps:
      if not os.path.exists(d):
        log.warning('Path does not exists: '+ d + '; in file: ' + pathBuild)
      else:
        path.add(d)
  return path


def getTree(iPaths):
  tree = []
  for path in iPaths:
    if os.path.isfile(path):
      tree.append(path)
    else:
      for root, dirs, files in os.walk(path):
        for f in files:
          tree.append(os.path.join(root, f))
  return tree  


def getFileName(iPath):
  return os.path.splitext(os.path.split(iPath)[1])[0]


def getFile(iInstance = '', iInFile = '', _cache = {}):
  if not iInstance and not iInFile:
    return _cache.values()
  build = getBuild(iInFile)
  key = (iInstance, build)
  res = _cache.get(key)
  if not res:
    paths = getDep(build)
    if not paths:
      return
    tree = getTree(paths)
    new = {(getFileName(i), build):i for i in tree}
    _cache.update(new)
    res = _cache.get(key)
  return res


@log_call
def getDepTree(iFile):
  if type(iFile) == type(""):
    iFile = [iFile]
  iFile = list(set(iFile))
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



