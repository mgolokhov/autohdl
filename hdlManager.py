import argparse
import copy
import logging
import os
import pprint
import subprocess
import sys

import instance
import structure
import build
import git
import synthesis
import aldec
import implement
import webdav
import doc


from hdlLogger import log_call

alog = logging.getLogger(__name__)

@log_call
def convert5to6version(config):
  if 'toplevel' in config:
    config['top'] = config.get('toplevel')
  for i in ['iTop', 'iSize', 'iUpload', 'iUcf']:
    res = config.get(i)
    if res:
      config[i[1:].lower()] = res


@log_call
def validateTop(iTop, config):
  parsed = config.get('src_main')
  if not parsed:
    srcFiles = structure.search(iPath='../src', iOnly=['\.v$'], iIgnore=['\.svn', '\.git'])
    config['src_main'] = instance.get_instances(srcFiles)
    config['src_dep'] = structure.getDepSrc(srcFiles)

  if iTop and parsed.get(iTop):
    return True


@log_call
def getFullPathToUcf(iUcf):
  # could be
  # empty
  # valid full path
  # wrong name\path
  # just name without extension
  # name with extension
  if not iUcf:
    return False
  if os.path.exists(iUcf):
    return os.path.abspath(iUcf).replace('\\', '/')
  pattern = iUcf if os.path.splitext(iUcf)[1] == '.ucf' else iUcf+'\.ucf'
  ucfFiles = structure.search(iPath='../src', iOnly = [pattern])
  if ucfFiles:
   return ucfFiles[0].replace('\\', '/')


@log_call
def setValidTop(arguments, config):
  try:
    topAsScriptName = os.path.splitext(os.path.basename(sys.modules['__main__'].__file__))[0]
  except AttributeError as e:
    alog.debug(e)
    topAsScriptName = ''

  if validateTop(arguments.top, config):
    config['top'] = arguments.top
    alog.info('Using top module name from arguments list')
  elif validateTop(config['top'], config):
    alog.info('Using top module name from script')
  elif topAsScriptName and validateTop(topAsScriptName, config):
    config['top'] = topAsScriptName
    alog.info('Using top module name same as script name')
  else:
    top = build.getParam(iKey='top')
    if validateTop(top, config):
      alog.info('Using top module from build.yaml')
      config['top'] = top
    else:
      alog.error('Top module name undefined!')


@log_call
def setValidUcf(config):

  ucfFromScript = getFullPathToUcf(config['ucf'])
  if ucfFromScript:
    alog.info('Using ucf file from script')
    return

  ucfNameAsTop = getFullPathToUcf(config['top'])
  if ucfNameAsTop:
    config['ucf'] = ucfNameAsTop
    alog.info('Using ucf name same as top module')
    return

  ucfFromBuild = getFullPathToUcf(build.getParam('ucf'))
  if ucfFromBuild:
    config['ucf'] = ucfFromBuild
    alog.info('Using ucf file from build.yaml')
    return

  alog.warning('Ucf file undefined')


@log_call
def validateLocation():
  try: # for Active-hdl compatibility
    if not {'script', 'src'}.issubset(os.listdir(os.getcwd()+'/..')):
      mayBe = os.path.dirname(sys.modules['__main__'].__file__)
      if {'script', 'src'}.issubset(os.listdir(mayBe+'/..')):
        os.chdir(mayBe)
      else:
        alog.error('Wrong current working path!\n Tried: \n{}\n{}'.format(
          os.getcwd(),
          mayBe
        ))
        sys.exit()
  except AttributeError as e:
    alog.debug(e)
  except WindowsError as e:
    alog.debug(e)


@log_call
def mergeConfig(configScript):
#  configBuild = build.loadUncached()
  configBuild = build.load()
  config = copy.deepcopy(configBuild)
  convert5to6version(config)
  convert5to6version(configScript)
  # overwrite
  config.update(configScript)

  depInScript = configScript.get('dep', [])
  if depInScript:
    depInBuild = configBuild.get('dep', []) or []
    depExtend = list(set(depInScript)-set(depInBuild))
    configBuild['dep'] = configBuild.get('dep', []) + depExtend
    config['dep'] = configBuild['dep']
    build.dump(configBuild)
  return config


@log_call
def setMode(arguments, config):
  #bugaga in argparse lib: doesnt have default choice
  if arguments.syn == 'nope':
    arguments.syn = None
  elif not arguments.syn:
    arguments.syn = 'batch'
  config['mode'] = 'synplify_gui' if arguments.syn == 'gui' else 'synplify_batch'


@log_call
def setUpload(arguments, config):
  config['upload'] = True if (not arguments.tb and not arguments.syn and not arguments.impl
                              and (arguments.upload or config['upload'])) else False


@log_call
def printInfo(config):
  alog.info(('Main design settings:\n'
                 + '#'*40 +
                '\n'
                'device     : {device}\n'
                'top module : {top}\n'
                'ucf        : {ucf}\n'
                'flash size : {size}\n'
                'upload     : {upload}\n'
                 + '#'*40 +
                '').format(device = config['device'],
                           top = config['top'],
                           ucf = config['ucf'],
                           size = config['size'],
                           upload = config['upload']))


@log_call
def kungfu(**config):
  alog.info('Processing...')
  alog.debug('args: ', sys.argv)
  alog.debug('config: ', config)

  if not config:
    config = {}

  validateLocation()

  parser = argparse.ArgumentParser(description='HDL Manager')
  parser.add_argument('-tb', action = 'store_true', help = 'export project to active-hdl')
  parser.add_argument('-top', help = 'top module name')
  parser.add_argument('-syn', nargs ='?', default = 'nope', choices = ['gui', 'batch'], help = 'synthesis step')
  parser.add_argument('-impl', action = 'store_true', help = 'implementation step')
  parser.add_argument('-upload', action = 'store_true', help = 'upload firmware to WebDav server')
  parser.add_argument('-git', help = 'creation/synchronization with webdav repo')

  parser.add_argument('-d', action = 'store_true', help = 'debug flag')

  arguments = parser.parse_args()

  config = mergeConfig(config)

  setValidTop(arguments, config)
  setValidUcf(config)
  setMode(arguments, config)
  setUpload(arguments, config)

  if arguments.d:
    pprint.pprint(config)
    sys.exit()

  printInfo(config)

  if arguments.git:
    git.handle(arguments.git, config)
    return

  if arguments.tb:
    aldec.export()
  elif arguments.syn:
    synthesis.run(config)
  elif arguments.impl:
    implement.run(config)
  elif arguments.upload:
    pass
  else:
    synthesis.run(config)
    implement.run(config)

  if config['upload']:
    webdav.upload_fw('../implement/{0}.bit'.format(config['top']))
    webdav.upload_fw('../implement/{0}.mcs'.format(config['top']))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='hdl cycles manager')
  parser.add_argument('-tb', help = 'export project to active-hdl')
  print parser.parse_args('-tb bka-dflkdjfd'.split())

  