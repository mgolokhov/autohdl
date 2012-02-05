import hashlib
import os

import autohdl.lib.yaml as yaml


from hdlLogger import log_call, logging
log = logging.getLogger(__name__)


@log_call    
def _toRelative(content, file):
  """
  Convert all paths in content to relative;
  Input:
    content - dictionary with config parameters;
    file - path to configure file;
  """
  path = os.path.dirname(file)
  pathUCF = content.get('ucf')
  if pathUCF:
    content['ucf'] = os.path.relpath(pathUCF, path)

  depSrc = content.get('dep')
  if depSrc:
    content['dep'] = [os.path.relpath(i, path) for i in depSrc]

  includePath = content.get('include_path')
  if includePath:
    if type(includePath) is not list:
      includePath = [includePath]
    content['include_path'] = [os.path.relpath(i, path) for i in includePath]


@log_call    
def _toAbsolute(content, file):
  """
  Convert all paths in content to absolute;
  Input:
    content - dictionary with config parameters;
    file - path to configure file
  """
  rootPath = os.path.dirname(file)
  pathUCF = content.get('ucf')
  if pathUCF:
    if os.path.exists(pathUCF):
      if not os.path.isabs(pathUCF):
        content['ucf'] = os.path.normpath(rootPath+'/'+pathUCF)
    else:
      log.warning('Wrong path: '+pathUCF)

  depSrc = content.get('dep')
  if depSrc:
    dep = []
    for i in depSrc:
      if not os.path.isabs(i):
        i = os.path.normpath(rootPath+'/'+i)
      if os.path.exists(i):
        dep.append(i)
      else:
        log.warning('Wrong path: '+i)
    content['dep'] = dep

  include_path = content.get('include_path')
  if include_path:
    if type(include_path) is not list:
      include_path = [include_path]
    incl = []
    for i in include_path:
      if not os.path.isabs(i):
        i = os.path.normpath(rootPath+'/'+i)
      if os.path.exists(i):
        incl.append(i)
      else:
        log.warning('Wrong path: '+i)
    content['include_path'] = incl


@log_call
def load(file = '../resource/build.yaml', _cache = {}, cacheEnable = True):
  path = os.path.abspath(file)
  if cacheEnable and _cache.get(path):
    return _cache.get(path)
  else:
    try:
      with open(file) as f:
        content = yaml.load(f.read())
        _toAbsolute(content, path)
        return content
    except IOError as e:
      log.warning(e)
      logging.warning('Cant open file ' + path)
      return {}


def default():
  with open(os.path.dirname(__file__)+'/data/build.yaml') as f:
    content = yaml.load(f.read())
    return content


def isModified(content, file):
  h = hashlib.sha1()
  h.update(yaml.dump(content, default_flow_style=False))
  shaNew = h.hexdigest()
  h = hashlib.sha1()
  h.update(open(file).read())
  shaOld = h.hexdigest()
  if shaNew != shaOld:
    return True

@log_call
def dump(content, file = '../resource/build.yaml'):
  #todo: compare old & new shas in parsed/build_sha
  path = os.path.abspath(file)
  _toRelative(content, path)
  if isModified(content, path):
    yaml.dump(content, open(path, 'w'), default_flow_style=False)


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
  depInBuild = load(path, cacheEnable=False).get('dep')
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
  build = load(cacheEnable=False)
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